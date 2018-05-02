#! /usr/bin/env python3
"""Second version without unittest.

This script is able to delete entire blocks.
It does not delete address graphs entirely; only the transactions associated to it. This should only be relevant if there's a double spend; in this case an empty address will stay recorded in the dataset that must be deleted manually.
"""
from datetime import datetime, timedelta, tzinfo
from pathlib import Path
import simplejson as json # needed for Decimal conversions, test if it breaks something
# import json
import sys
import re
import requests
import time
import subprocess
import binascii
import os
from rdflib import (
    Namespace,
    URIRef,
    Graph,
    Literal,
)
from rdflib.namespace import RDF, XSD, SKOS
import configparser

# reads configuration file and creates dictionaries "mainnet" and "testnet"
config = configparser.ConfigParser()
config.read('coin.ini')

mainnet = dict((key, config['mainnet'][key]) for key in config['mainnet'])
testnet = dict((key, config['testnet'][key]) for key in config['testnet'])


fusekidir = config["dirs"]["fuseki"]
datadir = config["dirs"]["data"]

global blockhash
debug = False
test = False


class RPCHost(object):
    """Class defining a 'host' for remote procedure calls."""
    def __init__(self, url):
        self._session = requests.Session()
        self._url = url
        self._headers = {'content-type': 'application/json'}

    def call(self, rpcMethod, *params):
        """RPC call using the Bitcoin JSON RPC API."""
        payload = json.dumps({"method": rpcMethod, "params": list(params), "jsonrpc": "2.0"})
        tries = 10
        hadConnectionFailures = False
        while True:
            # print("{url} {headers} {data}".format(url=self._url, headers=self._headers, data=payload))
            try:
                response = self._session.get(self._url, headers=self._headers, data=payload)
            except requests.exceptions.ConnectionError:
                tries -= 1
                if tries == 0:
                    raise Exception('Failed to connect for remote procedure call.')
                hadConnectionFailures = True
                print("Couldn't connect for remote procedure call, will sleep for ten seconds and then try again ({} more tries)".format(tries))
                time.sleep(10)
            else:
                if hadConnectionFailures:
                    print('Connected for remote procedure call after retry.')
                break
        if response.status_code not in (200, 500):
            raise Exception('RPC connection failure: ' + str(response.status_code) + ' ' + response.reason)
        responseJSON = response.json()
        if 'error' in responseJSON and responseJSON['error'] is not None:
            raise Exception('Error in RPC call: ' + str(responseJSON['error']))
        return responseJSON['result']


class GMT1(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=1) + self.dst(dt)

    def dst(self, dt):
        """Daylight saving time."""
        # DST starts last Sunday in March
        d = datetime(dt.year, 4, 1)   # ends last Sunday in October
        self.dston = d - timedelta(days=d.weekday() + 1)
        d = datetime(dt.year, 11, 1)
        self.dstoff = d - timedelta(days=d.weekday() + 1)
        if self.dston <= dt.replace(tzinfo=None) < self.dstoff:
            return timedelta(hours=1)
        else:
            return timedelta(0)

    def tzname(self, dt):
        return "GMT +1"

## data initialization
# block variables # without hash, nonce, confirmations, bits.

blockfields = [
    'size',
    'height',
    'version',
    'headerhash',
    'merkleroot',
    'time',
    'difficulty',
    'transition',
    'primechain',
    'primeorigin',
    'previousblockhash',
    'nextblockhash',
]

# initial data for Slimcoin

doacc_rubric_n3 = """
@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix doacc: <http://purl.org/net/bel-epa/doacc#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

doacc:D6b7dd05f-19f2-4b36-833d-f4bda4be58f5 a doacc:Cryptocurrency ;
    dc:description "Slimcoin burn mining is truly ASIC-proof."@en ;
    doacc:block-reward "50"^^xsd:string ;
    doacc:block-time 90 ;
    doacc:date-founded "2014-05-28"^^xsd:date ;
    doacc:distribution-scheme doacc:Dc10c93fb-f7ec-40cd-a06e-7890686f6ef8 ;
    doacc:image "datacoin_dat.png"^^xsd:string ;
    doacc:incept "2014-05"^^xsd:string ;
    doacc:pow doacc:D28483031-b854-4853-9a35-e1daf97e4c59 ;
    doacc:protection-scheme doacc:D493eab2e-eeba-496d-afca-c9372c6efe9a ;
    doacc:protocol doacc:Dede0f611-3a23-4794-b768-0740933a5ff6 ;
    doacc:retarget-time "continuous"^^xsd:string ;
    doacc:reward-modifier "var/diff"^^xsd:string ;
    doacc:symbol "SLM"@en ;
    doacc:total-coins "250000000"^^xsd:string ;
    skos:prefLabel "Slimcoin"@en .

doacc:Dc10c93fb-f7ec-40cd-a06e-7890686f6ef8 a doacc:DistributionScheme ;
    dc:description "Dissemination via proof of work"@en ;
    rdfs:isDefinedBy <http://purl.org/net/bel-epa/doacc> ;
    skos:prefLabel "pow"@en .

doacc:D28483031-b854-4853-9a35-e1daf97e4c59 a doacc:PoWscheme ;
    dc:description "SHA256 made difficult to parallelise via using leapfrog hashing"@en ;
    rdfs:isDefinedBy <http://purl.org/net/bel-epa/doacc> ;
    skos:prefLabel "dcrypt"@en .

doacc:D493eab2e-eeba-496d-afca-c9372c6efe9a a doacc:ProtectionScheme ;
    dc:description "Proof-of-Work plus Proof-of-Stake augmented by Proof-of-Burn"@en ;
    rdfs:isDefinedBy <http://purl.org/net/bel-epa/doacc> ;
    skos:prefLabel "pob"@en .

doacc:Dede0f611-3a23-4794-b768-0740933a5ff6 a doacc:Protocol ;
    dc:description "Bitcoin"@en ;
    rdfs:isDefinedBy <http://purl.org/net/bel-epa/doacc> ;
    skos:prefLabel "bitcoin"@en .
"""

# ontology scheme for block variables

blockprops = dict(
    bits="http://purl.org/net/bel-epa/ccy#bits",
    confirmations="http://purl.org/net/bel-epa/ccy#confirmations",
    difficulty="http://purl.org/net/bel-epa/ccy#difficulty",
    hash="http://purl.org/net/bel-epa/ccy#hash",
    headerhash="http://purl.org/net/bel-epa/ccy#headerhash",
    height="http://purl.org/net/bel-epa/ccy#height",
    merkleroot="http://purl.org/net/bel-epa/ccy#merkleroot",
    nextblockhash="http://purl.org/net/bel-epa/ccy#nextblockhash",
    nonce="http://purl.org/net/bel-epa/ccy#nonce",
    previousblockhash="http://purl.org/net/bel-epa/ccy#previousblockhash",
    size="http://purl.org/net/bel-epa/ccy#size",
    time="http://purl.org/net/bel-epa/ccy#time",
    version="http://purl.org/net/bel-epa/ccy#version",
    primechain="http://purl.org/net/bel-epa/ccy#primechain",
    primeorigin="http://purl.org/net/bel-epa/ccy#primeorigin",
    transition="http://purl.org/net/bel-epa/ccy#transition",
)

# datatypes for block variables

blockpropdata = dict(
    bits=XSD.hexBinary,
    confirmations=XSD.integer,
    difficulty=XSD.decimal,
    primechain=XSD.string,
    primeorigin=XSD.integer,
    hash=XSD.hexBinary,
    headerhash=XSD.hexBinary,
    height=XSD.integer,
    merkleroot=XSD.hexBinary,
    transition=XSD.decimal,
    nextblockhash=XSD.hexBinary,
    nonce=XSD.integer,
    previousblockhash=XSD.hexBinary,
    size=XSD.integer,
    time=XSD.integer,
    version=XSD.integer,
)

# URI formats for CCY and DOACC ("Description of a Cryptocurrency") ontologies

ccy_urif = "http://purl.org/net/bel-epa/ccy#C{}"
doacc_urif = "http://purl.org/net/bel-epa/doacc#D{}"
hexaPattern = re.compile(r'^([0-9a-fA-F]+)$')
CCY = Namespace("http://purl.org/net/bel-epa/ccy#")
DOACC = Namespace("http://purl.org/net/bel-epa/doacc#")


class RDFChainProcessor(object):

    def sparql_query(self, sparql_string, dataset, mode="select"):
        """SPARQL SELECT and CONSTRUCT queries."""
        query = "{f}/bin/s-query --service='http://localhost:3030/{s}chain/query' '{q}'".format(f=fusekidir, s=dataset, q=sparql_string)
        output = subprocess.getoutput(query)
        try:
            if mode == "select": 
                result = json.loads(output)
            else:
                result = output
        except Exception as e:
            raise Exception("{}. Fuseki server probably not running.".format(e))
        return result

    def sparql_update(self, sparql_string, dataset, mode="delete"):
        """SPARQL DELETE (and possibly other operations)."""
        try:
            query = "{f}/bin/s-update --service='http://localhost:3030/{s}chain/update' '{q}'".format(f=fusekidir, s=dataset, q=sparql_string)
            output = subprocess.getstatusoutput(query)
        except Exception as e:
            raise Exception("{}. Fuseki server probably not running.".format(e))
        return output


    def change_chaingraph(self, dataset):
        """Adds triples to the RDF blockchain dataset."""
        if test:
            n3graph = self.g.serialize(format="n3").decode('utf-8')
            print(n3graph)
            
        else:
            ntgraph = self.g.serialize(format="nt").decode('utf-8')
            with open('/tmp/{s}.nt'.format(s=dataset), 'w') as fp:
                fp.write(ntgraph)

            subprocess.getstatusoutput(
            fusekidir + "/bin/s-post http://localhost:3030/{s}chain/data default /tmp/{s}.nt".format(s=dataset))
            os.unlink("/tmp/{s}.nt".format(s=dataset))


    def get_chaingraph_block(self, blockhash, dataset):
        """Delivers graph of a complete block from the RDF blockchain."""
        block = 'ccy:C' + blockhash
        bg = Graph()
        query_string = 'PREFIX ccy: <http://purl.org/net/bel-epa/ccy#> CONSTRUCT {{ {b} ?bp ?bo . ?tx ?tp ?to . ?txi ?tip ?tio . ?txo ?top ?too }} WHERE {{ {b} ?bp ?bo . ?tx ccy:blockhash {b} . ?tx ?tp ?to . ?tx ccy:input ?txi . ?tx ccy:output ?txo . ?txi ?tip ?tio . ?txo ?top ?too . }}'.format(b=block)

        blockgraph = self.sparql_query(query_string, dataset, "construct")
        bg.parse(data=blockgraph, format="turtle")

        return bg

    def delete_chaingraph_block(self, blockhash, dataset):
        """Deletes a complete block from the RDF blockchain, including transactions, inputs and outputs. TODO: Address graphs are not deleted, only the related TX entries included in orphans."""
        block = 'ccy:C' + blockhash
        update_string = 'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX ccy: <http://purl.org/net/bel-epa/ccy#> DELETE {{ {b} ?bp ?bo . ?tx ?tp ?to . ?txi ?tip ?tio . ?txo ?top ?too . ?addr ccy:tx ?tx }} WHERE {{ {b} ?bp ?bo . ?tx ccy:blockhash {b} . ?tx ?tp ?to . ?tx ccy:input ?txi . ?tx ccy:output ?txo . ?txi ?tip ?tio . ?txo ?top ?too . OPTIONAL {{ ?addr rdf:type ccy:Address . ?addr ccy:tx ?tx }} }}'.format(b=block)
        status = self.sparql_update(update_string, dataset)
        return status

    def get_chaingraph_height(self, dataset):
        """Gets last block height from the Blockchain graph."""
        sparql_string = 'PREFIX ccy: <http://purl.org/net/bel-epa/ccy#> SELECT ?height ?block WHERE { ?block ccy:height ?height } ORDER BY DESC(?height) LIMIT 1'

        result = self.sparql_query(sparql_string, dataset)
        try:
            height = int(result["results"]["bindings"][0]["height"]["value"])
            blockhash = result["results"]["bindings"][0]["block"]["value"].replace(ccy_urif.format(""),"")
            return {"rdf_height":height, "rdf_blockhash":blockhash}
        except IndexError:
            return None # if genesis block is still not built


class BlockChainProcessor(object):
    def __init__(self, network=None):
        """Setting up coin initialization and connection variables."""
        self.ecoin = mainnet if network is None else network
        self.doacc = URIRef("http://purl.org/net/bel-epa/doacc#Dc74ed816-06ae-4b2a-b51a-3ac190810b1e")
        self.serverurl = 'http://{}:{}@localhost:{}/'.format(
            self.ecoin.get('rpcuser'), self.ecoin.get('rpcpass'), self.ecoin.get('rpcport'))
        self.amerpc = RPCHost(self.serverurl)

        # def setInitialData(self):
        self.blockchain = URIRef(ccy_urif.format(self.ecoin.get('genesis')[2:])) # BlockChain object
        self.binfof, self.binfo = self.dobinfo()

    def setUpGraph(self):
        self.g = Graph()
        self.g.bind("", "http://purl.org/net/bel-epa/ccy#")
        self.g.bind("doacc", "http://purl.org/net/bel-epa/doacc#")
        self.g.bind("skos", "http://www.w3.org/2004/02/skos/core#")

    def start_new_chain(self):
        self.setUpGraph()
        self.g.add((self.blockchain, RDF.type, CCY.BlockChain))
        self.g.add((self.blockchain, CCY.cryptocurrency, self.doacc))


    def dobinfo(self):
        """Gets 'getinfo' data."""
        debug = False
        try:
            binfo = self.amerpc.call('getinfo')
            if debug:
                print(json.dumps(binfo, sort_keys=True, indent=2, separators=(',', ': ')))
        except Exception as e:
            raise Exception("{} getinfo failed for {}".format(e, self.ecoin))
        binfof = [
            "balance",
            "blocks",
            "connections",
            "difficulty",
            "errors",
            "ip",
            "keypoololdest",
            "keypoolsize",
            "moneysupply",
            "newmint",
            "paytxfee",
            "protocolversion",
            "proxy",
            "stake",
            "testnet",
            "version",
            "walletversion"
        ]
        return binfof, binfo

    def dotxvi(self, txid, tx, txvi, txnode, s):
        """Stores transaction inputs in graph.
           txid = transaction id
           tx = transaction dictionary
           txvi = transaction input dictionary
           txnode = transaction as RDF node
           s = txvi["n"] (index of input)
        """
        txinnode = URIRef(ccy_urif.format(txid + '-I-' + str(s))) # RDF node for tx input
        if debug:
            print("....")
            print(json.dumps(txvi, sort_keys=True, indent=2, separators=(',', ': ')))
            print("....")
        self.g.add((txinnode, RDF.type, CCY.TransactionInput))
        self.g.add((txnode, CCY.input, txinnode))
        if txvi.get('sequence') != 4294967295:
            self.g.add((txinnode, CCY.sequence, Literal(txvi.get('sequence'), datatype=XSD.integer)))
        if 'coinbase' in txvi:
            self.g.add((txinnode, CCY.coinbase, Literal(txvi.get('coinbase'), datatype=XSD.hexBinary)))
            # Link to address
            # self.g.add((anode, CCY.tx, tnode))
            # self.g.add((anode, CCY.txinput, txinnode))
        else:
            self.g.add((txinnode, CCY.txid, URIRef(ccy_urif.format(txvi.get('txid'))))) 
            self.g.add((txinnode, CCY.nvout, Literal(txvi.get('vout'), datatype=XSD.integer)))
            self.g.add((txinnode, CCY.ssasm, Literal(txvi.get('scriptSig').get('asm'), datatype=XSD.string)))
            # self.g.add((txinnode, CCY.sshex, Literal(txvi.get('scriptSig').get('hex'), datatype=XSD.hexBinary)))

    def dotxvo(self, txid, tx, txvo, txnode, s):
        """Stores transaction outputs in graph.
           txid = transaction id
           tx = transaction dictionary
           txvi = transaction output dictionary
           txnode = transaction as RDF node
           s = txvo["n"] (index of output)
        """
        txoutnode = URIRef(ccy_urif.format(txid + '-O-' + str(s)))
        self.g.add((txoutnode, RDF.type, CCY.TransactionOutput))
        self.g.add((txnode, CCY.output, txoutnode))
        self.g.add((txoutnode, CCY.n, Literal(txvo.get('n'), datatype=XSD.integer)))
        self.g.add((txoutnode, CCY.value, Literal(txvo.get('value'), datatype=XSD.decimal)))
        self.g.add((txoutnode, CCY.pkasm, Literal(txvo.get('scriptPubKey').get('asm'), datatype=XSD.string)))
        # self.g.add((txoutnode, CCY.pkhex, Literal(txvo.get('scriptPubKey').get('hex'), datatype=XSD.hexBinary)))
        if txvo.get('scriptPubKey').get('reqSigs', 1) != 1:
            self.g.add((txoutnode, CCY.reqSigs, Literal(txvo.get('scriptPubKey').get('reqSigs'), datatype=XSD.integer)))
        txvoseq = txvo.get('n')
        txvotype = txvo.get('scriptPubKey').get('type')
        self.g.add((txoutnode, CCY.type, Literal(txvotype, datatype=XSD.string)))
        if debug:
            print("----")
            print(json.dumps(txvo, sort_keys=True, indent=2, separators=(',', ': ')))
            print("----")
        if txvotype == "nulldata" and txvo.get('scriptPubKey').get('asm')[:9] == "OP_RETURN":
            msg = binascii.unhexlify(txvo.get('scriptPubKey').get('asm')[18:])
            if debug:
                print("----")
                print("Message: {}".format(msg))
                print(json.dumps(txvo, sort_keys=True, indent=2, separators=(',', ': ')))
            self.g.add((txoutnode, CCY.inscription, Literal(msg, datatype=XSD.string)))
        if txvotype not in ['nonstandard', 'nulldata']:
            for addr in txvo.get('scriptPubKey').get('addresses'):
                anode = URIRef(CCY[addr])
                self.g.add((anode, RDF.type, CCY.Address))
                self.g.add((txoutnode, CCY.address, anode))
                self.g.add((anode, CCY.tx, txnode))
                # self.g.add((anode, CCY.txoutput, txoutnode))



    def dogetrawtransaction(self, txid, nheight):
        """Gets raw transaction JSON. Separated as this is relatively expensive and needed to know OP_RETURN/burn blocks."""

        tx = self.amerpc.call('getrawtransaction', txid, 1) # gets raw transaction from node
        if debug:
            print(json.dumps(tx, sort_keys=True, indent=2, separators=(',', ': ')))

        return tx
        

    def storetransaction(self, tx):
        """Stores transaction data in the RDF graph."""

        txkeys = dict(
            hex=XSD.hexBinary,
            version=XSD.integer,
            time=XSD.integer,
            locktime=XSD.integer,
            confirmations=False,
            blocktime=XSD.dateTimeStamp,
            blockhash=XSD.hexBinary)

        txnode = URIRef(ccy_urif.format(txid)) # transaction as an RDF node
        self.g.add((txnode, RDF.type, CCY.Transaction))

        for txk, dt in txkeys.items():
            if txk in ['blockhash']:
                self.g.add((txnode, CCY[txk], URIRef(ccy_urif.format(tx.get(txk)))))
            elif txk in ['confirmations', 'locktime', 'version', 'hex', 'blocktime']:
                pass
            # elif txk == 'IsBurnTx' and not tx.get(txk, False):
            #     pass
            elif txk == 'time':
                datestamp = int(datetime.fromtimestamp(tx.get(txk)).timestamp())
                self.g.add((txnode, CCY[txk], Literal(datestamp, datatype=dt)))
            else:
                self.g.add((txnode, CCY[txk.lower()], Literal(tx.get(txk), datatype=dt)))
        for txvi in tx.pop('vin', []):
            if txvi.get('sequence', 4294967295) == 4294967295:
                self.dotxvi(txid, tx, txvi, txnode, txvi.get('n', '0'))
            else:
                s = str(txvi.get('sequence', '0'))
                self.dotxvi(txid, tx, txvi, txnode, s)
        for s, txvo in enumerate(tx.pop('vout', [])):
            self.dotxvo(txid, tx, txvo, txnode, txvo.get('n'))

    def showrawtransaction(self, txid, nheight): # deprecated
       """Workaround."""
       return str(self.amerpc.call('getrawtransaction', txid, 1))


    def dobtime(self, bk):
        """Formats block timestamp."""
        # Split off into separate method?
        try:
            btime = datetime.strptime(
                bk['time'], '%Y-%m-%d %H:%M:%S %Z')
        except:
            btime = datetime.fromtimestamp(bk['time'])
        return int(btime.timestamp())

    def getblockhash(self, nheight):
        """Gets block hash from RPC API for a certain block height."""
        debug = False
        try:
            bhash = self.amerpc.call('getblockhash', nheight)
            if debug:
                print(json.dumps(bhash, sort_keys=True, indent=2, separators=(',', ': ')))
            return bhash
        except Exception as e:
            raise Exception("{} getblockhash failed for {}".format(e, self.ecoin))

    def getblockdata(self, blockhash):
        bk = self.amerpc.call("getblock", blockhash)
        return bk


    def readblock(self, blockhash, mode="mainnet"):
        """Gets block data and stores it in the graph."""
        block = URIRef(ccy_urif.format(str(blockhash)))

        bk = self.amerpc.call('getblock', blockhash)
        if debug:
            print(json.dumps(bk, sort_keys=True, indent=2, separators=(',', ': ')))

        txs = bk.pop('tx', [])
        nheight = bk.get('height', 0)

        txdata = (self.dogetrawtransaction(txid, nheight) for txcnt, txid in enumerate(txs))


        if nheight == 0:
            txs = txs[:2]



        elif mode in ("pub", "burn"):
            # Special modes: publications or burn address
            # For now, it uses a dirty workaround (full text search in transaction JSON).
            # If nheight = 0, genesis block is processed everytime.
            if mode == "pub":
               searchstring = "OP_RETURN"
            elif mode == "burn":
               searchstring = "SfSLMCoinMainNetworkBurnAddr1DeTK5"
            for tx in txdata:
                txstring = str(tx)
                if searchstring in txstring:
                   break
            else:
                print("{} not found at height {}.".format(searchstring, nheight))
                return

        # Writing graph
        # self.setUpGraph() # new graph for every block
        self.g.add((block, RDF.type, CCY.Block))
        for ks in blockfields:

            k = ks.lower()
            val = bk.get(ks)

            # Genesis block has no prevhash
            if val is None and k == 'previousblockhash':
                continue

            if val is None and k == 'nextblockhash':
                if self.binfo.get('blocks') == nheight:
                    continue
                else:
                    assert val is not None

            dt = blockpropdata.get(k)

            if k == 'height':
                self.g.add(
                    (block, URIRef(blockprops.get(k)),
                        Literal(nheight, datatype=dt)))
            elif k == 'time':
                self.g.add(
                    (block, URIRef(blockprops.get(k)),
                        Literal(self.dobtime(bk), datatype=dt)))
            elif k == 'difficulty':
                self.g.add(
                    (block, URIRef(blockprops.get(k)),
                        Literal(round(val, 8), datatype=dt)))
            elif k == 'previousblockhash':
                self.g.add(
                    (block, URIRef(blockprops.get(k)),
                        URIRef(CCY['C' + val])))
                self.g.add(
                    (URIRef(CCY['C' + val]),
                        URIRef(blockprops.get('nextblockhash')), block))
            elif k == 'nextblockhash' and val is not None:
                self.g.add(
                    (block, URIRef(blockprops.get(k)),
                        URIRef(CCY['C' + val])))
            elif k == 'version' and val == 1:
                pass
            else:
                try:
                    self.g.add(
                        (block, URIRef(blockprops.get(k)),
                            Literal(val, datatype=dt)))
                except Exception as e:
                    print("Ooops {} {}".format(e, k))
                    raise Exception(e)

        if nheight == 0:
            rawtx = "010000009d508653010000000000000000000000000000000000000000000000000000000000000000ffffffff0e049e5086530101062f503253482fffffffff01c07a8102000000002321038a52f85595a8d8e7c1d8c256baeee2c9ea7ad0bf7fe534575be4eb47cdbf18f6ac00000000"
        else:
            #for txcnt, txid in enumerate(txs):
            #    self.dogetrawtransaction(txid, nheight)
            for tx in txdata:
                self.storerawtransaction(tx["hash"], nheight)

