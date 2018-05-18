#!/usr/bin/env python3
"""Inscriber is a very small application that creates inscriptions on the Slimcoin blockchain, allowing to choose one particular address for it.

Inscriptions are priced with 0.02 SLM. This is due to the 0.01 minimum fee and the fact that transactions with outputs of less than 0.01 SLM are rejected by consensus.

This version needs a Slimcoin client running.

License: MIT, creators: The Slimcoin Developers


TODO:
- the three-output format doesn't work (it seems to be not accepted by the network).
"""

from blocknotifybase import RPCHost, mainnet, testnet
import argparse
import sys
import binascii
from decimal import Decimal
import simplejson as json

MIN_FEE = Decimal("0.01") # minimal fee for transactions
SLIMTOSHI = Decimal("0.000001") # only 6 decimals
LOCKTIME = "00000000"


def le_to_be(string):
    """Auxiliary function for byte swapping (little endian to big endian)."""
    n = 2
    blist = [string[i:i+n] for i in range(0, len(string), n)]
    return "".join(blist[::-1])

def get_balances(host, addresslist=None, only_possible=True):
    """Gets the balances of all addresses in the wallet. The only_possible flag checks if the address contains at least one UTXO with sufficient balance for the fees."""
    global utxol # utxo list is needed several times

    balances = {}
    if addresslist is not None:
        utxol = host.call("listunspent", addresslist)
    else:
        utxol = host.call("listunspent")
    for utxo in utxol:
        address = utxo.get("address")
        amount = Decimal(str(utxo.get("amount")))
        #if not quiet:
        #    print(amount)
        if address not in balances.keys():
            if only_possible == True:
                if amount < MIN_FEE*2:
                    continue
            balances.update({address : amount})
        else:
            balances.update({address : balances[address] + amount})

    return balances


def create_opreturn_output(content):
    """See https://bitcoin.stackexchange.com/questions/29554/explanation-of-what-an-op-return-transaction-looks-like."""
    insc_bytes = content.encode()
    hex_insc = binascii.hexlify(insc_bytes)
    bytelength = hex(len(insc_bytes)).encode()[2:]
    hexbytes = b"6a" + bytelength + hex_insc
    asm = "OP_RETURN " + str(hex_insc)
    scriptpubkey = {"type":"nulldata", "asm":asm, "hex":hexbytes.decode("utf-8")}
    return {"value":0, "n":2, "scriptPubKey": scriptpubkey }

def create_opreturn_scriptsig(content):
    """See https://bitcoin.stackexchange.com/questions/29554/explanation-of-what-an-op-return-transaction-looks-like."""
    insc_bytes = content.encode()
    if raw:
        hex_insc = binascii.hexlify(insc_bytes)
        bytelength = hex(len(insc_bytes)).encode()[2:]
    else:
        hex_insc = b"face0100" + binascii.hexlify(insc_bytes) # magic bytes for "small data" plaintext format
        bytelength = hex(len(insc_bytes) + 4).encode()[2:]
    hexbytes = b"6a" + bytelength + hex_insc
    asm = "OP_RETURN " + str(hex_insc)
    return hexbytes.decode("utf-8")


def create_opreturn_hash(content):
    """See https://bitcoin.stackexchange.com/questions/29554/explanation-of-what-an-op-return-transaction-looks-like."""
    insc_bytes = content.encode()
    return binascii.hexlify(insc_bytes).decode("utf-8")

def create_single_opreturn_output(pre_tx, content):
    """The single opreturn output mode is shorter and thus creates less blockchain bloat, but creates a nonstandard transaction, because the OP_RETURN transaction has a value."""
    final_inputnum = "02"
    opreturn_value = "1027000000000000" # 0.01
    opreturn_scriptsig = create_opreturn_scriptsig(content)
    opreturn_scriptsiglen_raw = int(len(opreturn_scriptsig) / 2)
    opreturn_scriptsiglen = hex(opreturn_scriptsiglen_raw)[2:]
    return final_inputnum + pre_tx["value1"] + pre_tx["scriptsig1_len"] + pre_tx["scriptsig1"] + opreturn_value + opreturn_scriptsiglen + opreturn_scriptsig

def create_double_opreturn_output(pre_tx, content, o2_start, tx_raw):
    """The double opreturn output mode is longer but creates a standard transaction with nulldata output."""
    final_inputnum = "03"
    opreturn_value = "1027000000000000" # 0.01
    opreturn_scriptsig = create_opreturn_scriptsig(content)
    opreturn_scriptsiglen_raw = int(len(opreturn_scriptsig) / 2)
    opreturn_scriptsiglen = hex(opreturn_scriptsiglen_raw)[2:]
  
    print(o2_start)

    scriptsig2_length = int(tx_raw[o2_start+16:o2_start+18], 16)
    o2_end = o2_start + 18 + (scriptsig2_length * 2) # end of second ScriptSig
    pre_tx.update({"value2":tx_raw[o2_start:o2_start+16], "scriptsig2_len":tx_raw[o2_start+16:o2_start+18], "scriptsig2":tx_raw[o2_start+18:o2_end]})

    return final_inputnum + pre_tx["value1"] + pre_tx["scriptsig1_len"] + pre_tx["scriptsig1"] + pre_tx["value2"] + pre_tx["scriptsig2_len"] + pre_tx["scriptsig2"] + opreturn_value + opreturn_scriptsiglen + opreturn_scriptsig



def create_opreturn_tx(host, address, content, is_testnet=True, threeoutputs=False, secondaddress=None):
    """Simplest way: create tx with first UTXO of selected address that has enough balance.
       Variant with only 2 outputs"""

    for utxo in utxol:
        if utxo["address"] == address:
            
            if Decimal(str(utxo["amount"])) >= MIN_FEE*2:
                if not quiet:
                    print("Choosing imput", utxo)
                # use raw transactions API to create a transaction, then append OP_RETURN code
                # following partially https://bitcoin.stackexchange.com/questions/25224/what-is-a-step-by-step-way-to-insert-data-in-op-return/36439#36439
                input_amount = Decimal(str(utxo["amount"]))
                change_amount = input_amount - MIN_FEE*2
                pre_tx_inputs = [{"txid":utxo["txid"], "vout":utxo["vout"]}]

                if threeoutputs == False:
                    pre_tx_outputs = {address:change_amount}
                else:
                    if newaddress == True:
                        new_address = host.call("getnewaddress")
                    elif secondaddress is not None:
                        new_address = secondaddress
                    else:
                        new_address = address # "splitting" output on same address does not work.
                    pre_tx_outputs = {new_address:MIN_FEE, address:change_amount}

                tx_raw = host.call("createrawtransaction", pre_tx_inputs, pre_tx_outputs)
                if not quiet:
                    print("Preliminary transaction:", tx_raw, len(tx_raw))

                script_length = int(tx_raw[90:92], 16)
                se = 92 + (script_length * 2) # script end
                scriptsig1_length = int(tx_raw[se+26:se+28], 16)
                s1e = se + 28 + (scriptsig1_length * 2) # end of first ScriptSig

                pre_tx = {
                "tx_version" : tx_raw[:8], "tx_ntime" : tx_raw[8:16], "number_of_inputs" : tx_raw[16:18],
                "input_tx_id" : tx_raw[18:82], "input_tx_num" : tx_raw[82:90], "script_length" : tx_raw[90:92],
                "script" : tx_raw[92:se], "sequence" : tx_raw[se:se+8],
                "number_of_outputs":tx_raw[se+8:se+8+2], 
                "value1":tx_raw[se+10:se+26], "scriptsig1_len":tx_raw[se+26:se+28], "scriptsig1":tx_raw[se+28:s1e]
                }
                if not quiet:
                    print(pre_tx)
                    print("Value Output Change Address (sat.):", int(le_to_be(pre_tx["value1"]), 16))

                first_part_tx = tx_raw[:se + 8]

                if threeoutputs == False:
                    second_part_tx = create_single_opreturn_output(pre_tx, content)
                else:
                    second_part_tx = create_double_opreturn_output(pre_tx, content, s1e, tx_raw)

                final_tx = first_part_tx + second_part_tx + LOCKTIME
                if not quiet:
                    print("Final transaction (hex)", final_tx)

                return final_tx



def create_opreturn_tx2(host, address, content, is_testnet=True): # CURRENTLY NOT USED
    """Simplest way: create tx with first UTXO of selected address that has enough balance.
       This uses the "data" field of the raw transaction API - this still DOESN'T work, perhaps in 0.6"""

    for utxo in utxol:
        if utxo["address"] == address:
            print(utxo)
            if Decimal(str(utxo["amount"])) >= MIN_FEE*2:
                # use raw transactions API to create a transaction, then append OP_RETURN code
                # following https://bitcoin.stackexchange.com/questions/25224/what-is-a-step-by-step-way-to-insert-data-in-op-return/36439#36439
                input_amount = Decimal(str(utxo["amount"]))
                change_amount = input_amount - MIN_FEE*2
                change_address = address # simplest behaviour, should be able to be changed later
                pre_tx_inputs = [{"txid":utxo["txid"], "vout":utxo["vout"]}]
                new_address = host.call("getnewaddress")
                pre_tx_outputs = {change_address:change_amount, "data":create_opreturn_hash(content)}
                print(pre_tx_inputs, pre_tx_outputs)

                tx_raw = host.call("createrawtransaction", pre_tx_inputs, pre_tx_outputs)
                return tx_raw


def save_standard_addresses(address_dict):
    with open("inscriber-address.conf", "w") as fp:
        json.dump(fp, address_dict)

def load_standard_addresses():
    with open("inscriber-address.conf", "r") as fp:
        return json.load(fp)

def addr_selection(host, standard=False):
    if standard:
        addresslist = load_standard_addresses()
        balances = get_balances(host, addresslist)
        print("Using standard addresses saved in inscriber-address.conf.")
    else:
        balances = get_balances(host)
        addresslist = list(balances.keys())
        print("Showing addresses with balances of more than {} SLM.".format(MIN_FEE))
    if len(addresslist) == 0:
        raise Exception("No address with suitable balance in your wallet.")
         
    # menu
    for address in addresslist:
        print("{}) '{}' - Balance: {}".format(addresslist.index(address) + 1, address, balances[address]))
    print("Select one of the available addresses' number [1-{}].".format(len(addresslist)))
    selected = input()
    selected_address = addresslist[int(selected) - 1]
    print("Selected address:", selected_address)
    return selected_address

def test_content(content, raw=False):
        if len(content) < 16:
            if not quiet:
                print("NOTE: Inscription shorter than 16 chars, filling with spaces.")

            return content.ljust(16)
        elif len(content) > 75:
            raise Exception("Content longer than maximum length of 75 chars (smalldata: 71 chars).")
        elif (raw == False) and (len(content) > 71):
            raise Exception("Content longer than maximum length of 71 chars (smalldata format).")
        else:
            return content
        


def cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("content", type=str, help="The inscription content (e.g. torrent hash).")
    parser.add_argument("address", type=str, nargs="?", default=None, help="The address you want to use for your inscription. If you don't provide one, you can choose one in a dialog.")
    parser.add_argument("secondaddress", type=str, nargs="?", default=None, help="The address you want to use for the second output (optional).")
    parser.add_argument("--load", "-l", action="store_true", help="Load a list of addresses saved in a JSON file (inscriber-address.conf).")
    parser.add_argument("--save", "-s", action="store_true", help="Save the list of possible addresses in a JSON file (inscriber-address.conf).")
    parser.add_argument("--testnet", "-t", action="store_true", help="Testnet mode.")
    parser.add_argument("--sign", "-S", action="store_true", help="Sign transaction (dangerous!)")
    parser.add_argument("--send", action="store_true", help="Send transaction (dangerous!)")
    parser.add_argument("--newaddress", "-n", action="store_true", help="Use new address for the auxiliary output (only three-output mode).")
    parser.add_argument("--threeoutputs", "-3", action="store_true", help="Use three output mode.")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode (for scripting).")
    parser.add_argument("--onlybalances", "-b", action="store_true", help="Only display address balances and exit.")
    parser.add_argument("--raw", "-R", action="store_true", help="Creates a standard OP_RETURN message without the magic bytes for messages taken from Fusioncoin. Will not be recognized as a 'message' by the Slimcoin client, but provides 4 bytes more space.")
    return parser.parse_args()

def main(gui=False, gui_args=None):

    global quiet
    global newaddress
    global raw

    args = cli_args()


    quiet = args.quiet
    newaddress = args.newaddress
    raw = args.raw
    if args.testnet == True:
       network = testnet
    else:
       network = mainnet
    
    host = RPCHost('http://{}:{}@localhost:{}/'.format(network.get("rpcuser"), network.get("rpcpass"), network.get("rpcport")))

    if args.onlybalances == True:
       print(get_balances(host))
       sys.exit()

    content = test_content(args.content)

    if args.address is None:
        address = addr_selection(host, args.load)
    else:
        if args.address not in get_balances(host).keys():
            if quiet:
                raise Exception("Address doesn't contain any input with enough balance.")
            else:
                print("Error: Address must contain 0.02 SLM or more. Choose another one.")
                address = addr_selection(host)
        else:
            address = args.address


    final_tx = create_opreturn_tx(host, address, content, args.testnet, args.threeoutputs, args.secondaddress)
    if not quiet:

        print("############# FINAL TRANSACTION ###############")
        final_tx_decoded = host.call("decoderawtransaction", final_tx)
        print(final_tx_decoded)
    

    if args.sign == True:
        if not quiet:
            print("Signing transaction.")
        signed_tx = host.call("signrawtransaction", final_tx)
        print(signed_tx)

        if args.send == True:
            if not quiet:
                print("Sending transaction.")
            host.call("sendrawtransaction", signed_tx["hex"])


if __name__ == "__main__":
    main()
