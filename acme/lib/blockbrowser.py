#!/usr/bin/env python3
"""Blockchain reader."""
import binascii
import datetime
import hashlib


def to_hex(bytestring):
    """Convert given little-endian bytestring to hex."""
    return binascii.hexlify(bytestring[::-1])


def double_hash(bytestring):
    """Double SHA256 hash given bytestring."""
    return hashlib.sha256(hashlib.sha256(bytestring).digest()).digest()


def hash160(bytestring):
    """Perform SHA256 hash of given bytestring followed by RIPEMD-160 hash."""
    return hashlib.new('ripemd160', hashlib.sha256(bytestring).digest()).digest()


def base58(bytestring):
    """Perform base58 encode given bytestring."""
    base58_characters = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    value = int(binascii.hexlify(bytestring), 16)

    result = ""
    while value >= len(base58_characters):
        value, mod = divmod(value, len(base58_characters))
        result += base58_characters[mod]
    result += base58_characters[value]

    # handle leading zeros
    for byte in bytestring:
        if byte == 0:
            result += base58_characters[0]
        else:
            break

    return result[::-1]


def ripemd160_to_address(key_hash):
    """Convert RIPEMD160 to address."""
    version = b"\00"
    checksum = double_hash(version + key_hash)[:4]
    return base58(version + key_hash + checksum)


def public_key_to_address(public_key):
    """Convert public key to address."""
    return ripemd160_to_address(hash160(public_key))


class BlockChain:
    """The Blockchain class."""

    def __init__(self, data):
        """Initialise class."""
        self.data = data
        self.index = 0
        self.block_count = 0

    def blocks(self):
        """Yield blocks one at a time."""
        while self.index < len(self.data):
            yield self.parse_block()
            self.block_count += 1

    def hash_since(self, mark):
        """Double hash data from given mark to current index and return in hex."""
        return to_hex(double_hash(self.data[mark:self.index]))

    # basic reading of little-endian integers of different widths

    def get_uint8(self):
        """Perform basic reading of uint8 little-endian integers of different widths."""
        data = self.data[self.index]
        self.index += 1
        return data

    def get_uint16(self):
        """Perform basic reading of uint16 little-endian integers of different widths."""
        return self.get_uint8() + (self.get_uint8() << 8)

    def get_uint32(self):
        """Perform basic reading of uint32 little-endian integers of different widths."""
        return self.get_uint16() + (self.get_uint16() << 16)

    def get_uint64(self):
        """Perform basic reading of uint64 little-endian integers of different widths."""
        return self.get_uint32() + (self.get_uint32() << 32)

    # more involved data reading

    def get_bytestring(self, length=1):
        """Get bytestring."""
        data = self.data[self.index:self.index + length]
        self.index += length
        return data

    def get_timestamp(self):
        """Get timestamp."""
        return datetime.datetime.utcfromtimestamp(self.get_uint32())

    def get_hash(self):
        """Get hash."""
        return to_hex(self.get_bytestring(32))

    def get_varlen_int(self):
        """Get varlen int."""
        code = self.get_uint8()
        if code < 0xFD:
            return code
        elif code == 0xFD:
            return self.get_uint16()
        elif code == 0xFE:
            return self.get_uint32()
        elif code == 0xFF:
            return self.get_uint64()

    def get_script(self):
        """Get script."""
        script_length = self.get_varlen_int()
        script = self.get_bytestring(script_length)

        tokens = []

        script_index = 0
        while script_index < script_length:
            op_code = script[script_index]
            script_index += 1

            if op_code <= 75:
                tokens.append(script[script_index:script_index + op_code])
                script_index += op_code
            elif op_code == 97:
                tokens.append("OP_NOP")
            elif op_code == 118:
                tokens.append("OP_DUP")
            elif op_code == 136:
                tokens.append("OP_EQUALVERIFY")
            elif op_code == 169:
                tokens.append("OP_HASH160")
            elif op_code == 172:
                tokens.append("OP_CHECKSIG")
            else:
                print("unknown opcode", op_code)
                raise ValueError

        return tokens

    # parsing data structures in block chain

    def parse_block(self):
        """Parse a block."""
        print("Count {}".format(self.block_count))
        assert self.get_uint32() == 0xDADCDDED, self.get_uint32()  # magic network id
        block_length = self.get_uint32()

        # mark current position for block hash calculation
        mark = self.index

        # read rest of block header
        block_data = {
            "size": block_length,
            "ver": self.get_uint32(),
            "prev_block": self.get_hash(),
            "mrkl_root": self.get_hash(),
            "timestamp": self.get_timestamp(),
            "bits": self.get_uint32(),
            "nonce": self.get_uint32()
        }

        # calculate hash
        block_data["hash"] = self.hash_since(mark)

        # read transactions
        transaction_count = self.get_varlen_int()
        block_data["transactions"] = [
            self.parse_transaction() for i in range(transaction_count)
        ]

        return block_data

    def parse_transaction(self):
        """Parse a transaction."""
        # mark current position for transaction hash calculation
        mark = self.index

        # read rest of transaction data
        transaction_data = {
            "ver": self.get_uint32(),
            "inputs": self.parse_inputs(),
            "outputs": self.parse_outputs(),
            "lock_time": self.get_uint32(),
        }

        # calculate hash
        transaction_data["hash"] = self.hash_since(mark)

        return transaction_data

    def parse_inputs(self):
        """Parse the inputs."""
        count = self.get_varlen_int()
        return [{
            "transaction_hash": self.get_hash(),
            "transaction_index": self.get_uint32(),
            "script": self.get_script(),
            "sequence_number": self.get_uint32(),
        } for i in range(count)]

    def parse_outputs(self):
        """Parse the outputs."""
        count = self.get_varlen_int()
        return [{
            "value": self.get_uint64(),
            "script": self.get_script(),
        } for i in range(count)]


if __name__ == "__main__":
    import sys
    sys.argv.append('/home/gjh/.datacoin/blocks/blk00000.dat')
    filename = sys.argv[1]
    with open(filename, "rb") as f:
        data = f.read()
        block_chain = BlockChain(data)
        for block_num, block in enumerate(block_chain.blocks()):
            print()
            print("BLOCK", block_num, block["hash"])
            for transaction_num, transaction in enumerate(block["transactions"]):
                print("  Transaction", transaction_num, transaction["hash"])
                for inp in transaction["inputs"]:
                    if inp["transaction_hash"] == b"0000000000000000000000000000000000000000000000000000000000000000":
                        print("    GENERATED ->")
                    else:
                        print("   ", inp["transaction_hash"], inp["transaction_index"], "->")
                for output_num, output in enumerate(transaction["outputs"]):
                    print("   {} {} ->".format(output_num, output["value"] / 100000000))
                    script = output["script"]
                    if len(script) == 2 and script[1] == "OP_CHECKSIG":
                        print("public-key", public_key_to_address(script[0]))
                    elif len(script) == 5 and (
                        script[0] == "OP_DUP" and
                        script[1] == "OP_HASH160" and
                        script[3] == "OP_EQUALVERIFY" and
                        script[4] == "OP_CHECKSIG"
                    ):
                        print("address-type", ripemd160_to_address(script[2]))
                    else:
                        print("indecipherable script")
