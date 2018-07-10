#!/usr/bin/env python3
"""Inscriber is a very small application that creates inscriptions on the Slimcoin blockchain, allowing to choose one particular address for it.

Inscriptions are priced with 0.02 SLM. This is due to the 0.01 minimum fee and the fact that transactions with outputs of less than 0.01 SLM are rejected by consensus.

This version needs a Slimcoin client running.

License: MIT, creators: The Slimcoin Developers


TODO:
- the three-output format doesn't work (it seems to be not accepted by the network). Thrash it?
"""

from rpchost import RPCHost
import argparse
import configparser
import sys
import binascii
from decimal import Decimal
import simplejson as json
from pathlib import Path

MIN_FEE = Decimal("0.01") # minimal fee for transactions
SLIMTOSHI = Decimal("0.000001") # minimal unit, 6 decimals
LOCKTIME = "00000000"
CONFIGFILE = "inscriber.ini"
DEFAULT_LINUX_MAINNET_CONFFILE = "/.slimcoin/slimcoin.conf"
DEFAULT_WINDOWS_MAINNET_CONFFILE = "\SLIMCoin\slimcoin.conf"
DEFAULT_LINUX_TESTNET_CONFFILE = "/.slimcoin/testnet/slimcoin-testnet.conf"
DEFAULT_WINDOWS_TESTNET_CONFFILE = "\SLIMCoin\testnet\slimcoin-testnet.conf"
HOMEDIR = str(Path.home())

def le_to_be(string):
    """Auxiliary function for byte swapping (little endian to big endian)."""
    n = 2
    blist = [string[i:i+n] for i in range(0, len(string), n)]
    return "".join(blist[::-1])

def simple_configreader(fileobj):
    dictionary = {}
    for line in fileobj.readlines():
        l = line.strip()
        if (len(l) > 0) and (l[0] != '#'):
            try:
                lkey, lvalue = l.split("=")
                dictionary.update({lkey:lvalue})
            except ValueError:
                raise ValueError("Configuration file error.")
    print(dictionary)
    return dictionary


class Inscriber(object):

    def __init__(self, network_type="mainnet", content=None, address=None, secondaddress=None, raw=False, quiet=False, force=False, newaddress=False, loadaddr=None, saveaddr=False, sign=False, send=False, threeoutputs=False):

        self.stored_addresses = {}

        self.address = address
        self.secondaddress = secondaddress
        self.network_type = network_type
        self.quiet = quiet
        self.raw = raw
        self.content = content
        self.newaddress = newaddress
        self.force = force
        self.loadaddr = loadaddr
        self.saveaddr = saveaddr
        self.sign = sign
        self.send = send
        self.threeoutputs = threeoutputs

        self.rawtx = None
        self.rawtx_decoded = None
        self.signedtx = None
        self.inscription = None

        self.config = configparser.ConfigParser()
        self.read_config()

        self.host = RPCHost('http://{}:{}@localhost:{}/'.format(self.network.get("rpcuser"), self.network.get("rpcpass"), self.network.get("rpcport")))

        # Address and UTXO list selection
        if self.loadaddr is not None:
            if self.loadaddr == "<ALL>":
                self.utxol = self.host.call("listunspent", 0, 99999999, list(self.stored_addresses.values()))
            else:
                self.address = self.stored_addresses[self.loadaddr]
        else:
            self.utxol = self.host.call("listunspent")
        if self.address is not None:
            self.utxol = self.host.call("listunspent", 0, 99999999, [self.address])

        self.balances = self.get_balances()
        self.addresslist = list(self.balances.keys()) # addresses to be displayed in the UI, also sets self.balances


    ### CONFIG AND ARGS ###

    def read_config(self, cf=CONFIGFILE):
        
        self.config.read(cf)
        try:
            self.gen_config = dict((key, self.config['general'][key]) for key in self.config['general'])
        except KeyError:
            self.gen_config = {}
        print(self.gen_config)
        try:
            self.network = dict((key, self.config[self.network_type][key]) for key in self.config[self.network_type])
        except KeyError:
            self.read_coinconfig()
        if "addresses" in self.config:
            self.stored_addresses = dict((key, self.config['addresses'][key]) for key in self.config['addresses'])

    def read_coinconfig(self):
        self.network = {}
        ccffile = self.gen_config.get("{}_configfile".format(self.network_type))
        if ccffile is None:
            homedir = str(Path.home())
            if homedir[:5] == '/home': # Linux/Unix
                if self.network_type == "testnet":
                    ccffile = homedir + DEFAULT_LINUX_TESTNET_CONFFILE
                else:
                    ccffile = homedir + DEFAULT_LINUX_MAINNET_CONFFILE
            else:
                if self.network_type == "testnet":
                    ccffile = homedir + DEFAULT_WINDOWS_TESTNET_CONFFILE
                else:
                    ccffile = homedir + DEFAULT_WINDOWS_MAINNET_CONFFILE
 
        try:
            with open(ccffile, "r") as cf:
                coinconfig = simple_configreader(cf)
        except FileNotFoundError:
            print("File {} not found, adjust {} config file.".format(ccffile, CONFIGFILE))
        networkdata = {"rpcport" : coinconfig["rpcport"], "rpcuser" : coinconfig["rpcuser"], "rpcpass" : coinconfig["rpcpassword"] }
        self.network.update(networkdata)
        self.config[self.network_type] = networkdata
        ccffilelabel = self.network_type + "_configfile"
        if "general" in self.config:
            self.config["general"].update({ccffilelabel:ccffile})
        else:
            self.config.update({"general":{ccffilelabel:ccffile}})

    def save_standard_address(self, label="default"):
        if "addresses" in self.config.sections():
            if (self.address in self.config["addresses"]) and (self.force == False):
                print("Address already saved. Change label in configuration file or use '--force' option to overwrite.")
            elif (label in self.config["addresses"].keys()) and (self.force == False):
                print("Label already used. Change address in configuration file or use '--force' option to overwrite.")
            else: 
                self.config["addresses"].update({label : self.address})
        else:
            self.config.update({"addresses" : {label : self.address}})

    def write_config(self):
        # print(dict(self.config))
        with open("inscriber.ini", "w") as cf:
            self.config.write(cf)

    ### MAIN METHODS ###

    def get_balances(self, only_possible=True):
        """Gets the balances of all addresses of the self.utxol UTXO list (all UTXOs of the wallet or a selection). The only_possible flag checks if the address contains at least one UTXO with sufficient balance for the fees."""

        balances = {}
        for utxo in self.utxol:
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


    def create_opreturn_output(self):
        """See https://bitcoin.stackexchange.com/questions/29554/explanation-of-what-an-op-return-transaction-looks-like."""
        insc_bytes = self.inscription.encode()
        hex_insc = binascii.hexlify(insc_bytes)
        bytelength = hex(len(insc_bytes)).encode()[2:]
        hexbytes = b"6a" + bytelength + hex_insc
        asm = "OP_RETURN " + str(hex_insc)
        scriptpubkey = {"type":"nulldata", "asm":asm, "hex":hexbytes.decode("utf-8")}
        return {"value":0, "n":2, "scriptPubKey": scriptpubkey }

    def create_opreturn_scriptsig(self):
        """See https://bitcoin.stackexchange.com/questions/29554/explanation-of-what-an-op-return-transaction-looks-like."""
        insc_bytes = self.inscription.encode()
        if self.raw:
            hex_insc = binascii.hexlify(insc_bytes)
            bytelength = hex(len(insc_bytes)).encode()[2:]
        else:
            hex_insc = b"face0100" + binascii.hexlify(insc_bytes) # magic bytes for "small data" plaintext format
            bytelength = hex(len(insc_bytes) + 4).encode()[2:]
        hexbytes = b"6a" + bytelength + hex_insc
        asm = "OP_RETURN " + str(hex_insc)
        return hexbytes.decode("utf-8")


    def create_opreturn_hash(self):
        """See https://bitcoin.stackexchange.com/questions/29554/explanation-of-what-an-op-return-transaction-looks-like."""
        insc_bytes = self.inscription.encode()
        return binascii.hexlify(insc_bytes).decode("utf-8")

    def create_single_opreturn_output(self, pre_tx):
        """The single opreturn output mode is shorter and thus creates less blockchain bloat, but creates a nonstandard transaction, because the OP_RETURN transaction has a value."""
        final_inputnum = "02"
        opreturn_value = "1027000000000000" # 0.01
        opreturn_scriptsig = self.create_opreturn_scriptsig()
        opreturn_scriptsiglen_raw = int(len(opreturn_scriptsig) / 2)
        opreturn_scriptsiglen = hex(opreturn_scriptsiglen_raw)[2:]
        return final_inputnum + pre_tx["value1"] + pre_tx["scriptsig1_len"] + pre_tx["scriptsig1"] + opreturn_value + opreturn_scriptsiglen + opreturn_scriptsig

    def create_double_opreturn_output(self, pre_tx, o2_start, tx_raw):
        """The double opreturn output mode is longer but creates a standard transaction with nulldata output."""
        final_inputnum = "03"
        opreturn_value = "1027000000000000" # 0.01
        opreturn_scriptsig = self.create_opreturn_scriptsig()
        opreturn_scriptsiglen_raw = int(len(opreturn_scriptsig) / 2)
        opreturn_scriptsiglen = hex(opreturn_scriptsiglen_raw)[2:]
  
        print(o2_start)

        scriptsig2_length = int(tx_raw[o2_start+16:o2_start+18], 16)
        o2_end = o2_start + 18 + (scriptsig2_length * 2) # end of second ScriptSig
        pre_tx.update({"value2":tx_raw[o2_start:o2_start+16], "scriptsig2_len":tx_raw[o2_start+16:o2_start+18], "scriptsig2":tx_raw[o2_start+18:o2_end]})

        return final_inputnum + pre_tx["value1"] + pre_tx["scriptsig1_len"] + pre_tx["scriptsig1"] + pre_tx["value2"] + pre_tx["scriptsig2_len"] + pre_tx["scriptsig2"] + opreturn_value + opreturn_scriptsiglen + opreturn_scriptsig



    def create_opreturn_tx(self):
        """Simplest way: create tx with first UTXO of selected address that has enough balance.
           Variant with only 2 outputs"""

        for utxo in self.utxol:
            if utxo["address"] == self.address:
            
                if Decimal(str(utxo["amount"])) >= MIN_FEE*2:
                    if not self.quiet:
                        print("Choosing imput", utxo)
                    # use raw transactions API to create a transaction, then append OP_RETURN code
                    # following partially https://bitcoin.stackexchange.com/questions/25224/what-is-a-step-by-step-way-to-insert-data-in-op-return/36439#36439
                    input_amount = Decimal(str(utxo["amount"]))
                    change_amount = input_amount - MIN_FEE*2
                    pre_tx_inputs = [{"txid":utxo["txid"], "vout":utxo["vout"]}]

                    if self.threeoutputs == False:
                        pre_tx_outputs = {self.address:change_amount}
                    else:
                        if self.newaddress == True:
                            new_address = self.host.call("getnewaddress")
                        elif self.secondaddress is not None:
                            new_address = self.secondaddress
                        else:
                            new_address = self.address # "splitting" output on same address does not work.
                        pre_tx_outputs = {new_address:MIN_FEE, self.address:change_amount}

                    tx_raw = self.host.call("createrawtransaction", pre_tx_inputs, pre_tx_outputs)
                    if not self.quiet:
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
                    if not self.quiet:
                        print(pre_tx)
                        print("Value Output Change Address (sat.):", int(le_to_be(pre_tx["value1"]), 16))

                    first_part_tx = tx_raw[:se + 8]

                    if self.threeoutputs == False:
                        second_part_tx = self.create_single_opreturn_output(pre_tx)
                    else:
                        second_part_tx = self.create_double_opreturn_output(pre_tx, s1e, tx_raw)

                    final_tx = first_part_tx + second_part_tx + LOCKTIME
                    if not self.quiet:
                        print("Final transaction (hex)", final_tx)

                    return final_tx



    def create_opreturn_tx2(self): # CURRENTLY NOT USED
        """Simplest way: create tx with first UTXO of selected address that has enough balance.
           This uses the "data" field of the raw transaction API - this still DOESN'T work in Slimcoin, perhaps in 0.6"""

        for utxo in self.utxol:
            if utxo["address"] == self.address:
                print(utxo)
                if Decimal(str(utxo["amount"])) >= MIN_FEE*2:
                    # use raw transactions API to create a transaction, then append OP_RETURN code
                    # following https://bitcoin.stackexchange.com/questions/25224/what-is-a-step-by-step-way-to-insert-data-in-op-return/36439#36439
                    input_amount = Decimal(str(utxo["amount"]))
                    change_amount = input_amount - MIN_FEE*2
                    change_address = self.address # simplest behaviour, should be able to be changed later
                    pre_tx_inputs = [{"txid":utxo["txid"], "vout":utxo["vout"]}]
                    new_address = self.host.call("getnewaddress")
                    pre_tx_outputs = {change_address:change_amount, "data":create_opreturn_hash()}
                    print(pre_tx_inputs, pre_tx_outputs)

                    tx_raw = self.host.call("createrawtransaction", pre_tx_inputs, pre_tx_outputs)
                    return tx_raw

    def get_addresslist(self):
        addresslist = list(self.balances.keys())
        if len(addresslist) == 0:
            raise Exception("No address with suitable balance in your wallet.")
        return addresslist

    def addr_selection(self):
        """CLI menu to select address."""
        if not self.quiet:
            if self.loadaddr:
                print("Using standard addresses saved in inscriber.ini.")
            else: # display all addresses with enough balance
                print("Showing addresses with balances of more than {} SLM.".format(MIN_FEE))
        for item in self.create_menulist():
            print(item)

        print("Select one of the available addresses' number [1-{}].".format(len(self.addresslist)))
        selected = input()
        self.address = self.addresslist[int(selected) - 1]
        print("Selected address:", self.address)


    def create_menulist(self):
        menulist = []
        addressnum = 0
        for address in self.addresslist:
            storedlist = list(self.stored_addresses.values())
            if address in storedlist:
                label_shown = list(self.stored_addresses.keys())[storedlist.index(address)]
            else:
                label_shown = "-"
            addressnum += 1
            menulist.append("{}) '{}' (Balance: {}, Label: {})".format(addressnum, address, self.balances[address], label_shown))
        return menulist

    def create_addr_combodict(self):
        addr_combodict = {}
        for address in self.balances.keys():
            storedlist = list(self.stored_addresses.values())
            if address in storedlist:
                label = list(self.stored_addresses.keys())[storedlist.index(address)]
            else:
                label = None
            balance = self.balances[address]
            addr_combodict.update({address:{"balance":balance,"label":label}})
        return addr_combodict
            

    def create_inscription(self):
        if len(self.content) < 16:
            if not quiet:
                print("NOTE: Inscription shorter than 16 chars, filling with spaces.")
    
            self.inscription = self.content.ljust(16)
        elif len(self.content) > 75:
            raise Exception("Content longer than maximum length of 75 chars (smalldata: 71 chars).")
        elif (self.raw == False) and (len(self.content) > 71):
            raise Exception("Content longer than maximum length of 71 chars (smalldata format).")
        else:
            self.inscription = self.content


    def init_address(self):

        if self.address is None:
            self.addr_selection()
        else:
            if self.address not in self.get_balances().keys():
                if self.quiet:
                    raise Exception("Address doesn't contain any input with enough balance.")
                else:
                    print("Error: Address must contain 0.02 SLM or more. Choose another one.")
                    self.address = self.addr_selection()
            else:
                self.address = self.address
        if self.saveaddr is not None:
            self.save_standard_address(self.saveaddr)


    def inscribe(self):

        self.create_inscription()

        final_tx = self.create_opreturn_tx()
        if not self.quiet:

            print("############# FINAL TRANSACTION ###############")
            final_tx_decoded = self.host.call("decoderawtransaction", final_tx)
            print(final_tx_decoded)
    

        if self.sign == True:
            if not self.quiet:
                print("Signing transaction.")
            signed_tx = self.host.call("signrawtransaction", final_tx)
            if not self.quiet:
                print("Signed transaction:", signed_tx)

            if self.send == True:
                if not self.quiet:
                    print("Sending transaction.")
                self.host.call("sendrawtransaction", signed_tx["hex"])


    # simplified methods

    def create_tx(self):
        self.rawtx = self.create_opreturn_tx()
        self.rawtx_decoded = self.host.call("decoderawtransaction", self.rawtx)

    def sign_tx(self):
        self.signedtx = self.host.call("signrawtransaction", self.rawtx)

    def send_tx(self):
        self.host.call("sendrawtransaction", self.signedtx["hex"])

    def set_address(self, address):
        self.address = address
        print("Setting address: " + self.address)

    def set_inscription(self, inscription):
        self.inscription = inscription
        print("Setting inscription: " + self.inscription)
        
def cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("content", type=str, help="The inscription content (e.g. torrent hash).")
    parser.add_argument("address", type=str, nargs="?", default=None, help="The address you want to use for your inscription. If you don't provide one, you can choose one in a dialog.")
    parser.add_argument("secondaddress", type=str, nargs="?", default=None, help="The address you want to use for the second output (optional).")
    parser.add_argument("--load", "-l", type=str, nargs="?", default=None, const="<ALL>", help="Load address(es) saved in the configuration file, select label if you want, otherwise all will be loaded.")
    parser.add_argument("--save", "-s", type=str, nargs="?", default=None, const="default", help="Save the selected address with a custom label. If no label is provided, it will be saved as 'default'.")
    parser.add_argument("--force", action="store_true", help="Overwrite addresses or labels if they are already stored in the configuration file.")
    parser.add_argument("--testnet", "-t", action="store_const", const="testnet", default="mainnet", help="Testnet mode.")
    parser.add_argument("--sign", "-S", action="store_true", help="Sign transaction (dangerous!)")
    parser.add_argument("--send", action="store_true", help="Send transaction (dangerous!)")
    parser.add_argument("--newaddress", "-n", action="store_true", help="Use new address for the auxiliary output (only three-output mode).")
    parser.add_argument("--threeoutputs", "-3", action="store_true", help="Use three output mode.")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode (for scripting).")
    parser.add_argument("--onlybalances", "-b", action="store_true", help="Only display address balances and exit.")
    parser.add_argument("--raw", "-R", action="store_true", help="Creates a standard OP_RETURN message without the magic bytes for messages taken from Fusioncoin. Will not be recognized as a 'message' by the Slimcoin client, but provides 2 bytes more space.")
    return parser.parse_args()



def cli_main():

    args = cli_args()

    i = Inscriber(network_type=args.testnet, content=args.content, address=args.address, secondaddress=args.secondaddress, raw=args.raw, quiet=args.quiet, force=args.force, newaddress=args.newaddress, loadaddr=args.load, saveaddr=args.save, sign=args.sign, send=args.send, threeoutputs=args.threeoutputs)

    if args.onlybalances == True:
       print(i.get_balances())
       sys.exit()
    else:
       i.init_address()
       i.inscribe()
       i.write_config()

if __name__ == "__main__":
    cli_main()
