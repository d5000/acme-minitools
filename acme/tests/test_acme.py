"""Tests of blockchain serialisation to RDF."""
import unittest
import json
import os
import requests
import time
from io import StringIO
from collections import OrderedDict
import datetime
from pyramid import testing
from pyramid.paster import get_appsettings
from pyramid.settings import asbool
from lxml import etree
from jsonschema import validate, exceptions
from json_schema_generator.recorder import Recorder
from acme.lib.helpers import RPCHost


def json2xml(json_obj, line_padding=""):
    result_list = list()

    json_obj_type = type(json_obj)

    if json_obj_type is list:
        for sub_elem in json_obj:
            result_list.append(json2xml(sub_elem, line_padding))

        return "\n".join(result_list)

    if json_obj_type is dict:
        for tag_name in json_obj:
            sub_obj = json_obj[tag_name]
            result_list.append("{}<{}>".format(line_padding, tag_name.replace(' ', '_')))
            result_list.append(json2xml(sub_obj, "\t" + line_padding))
            result_list.append("{}</{}>".format(line_padding, tag_name.replace(' ', '_')))

        return "\n".join(result_list)

    return "{}{}".format(line_padding, json_obj)


class AcmeTests(unittest.TestCase):
    """Test Acme responses."""

    def setUp(self):
        """Setup."""
        self.config = testing.setUp()
        settings = {}
        settings['coins'] = {}
        for k, val in get_appsettings('../../test.ini', name='main').items():
            if k.startswith('coins.'):
                d, c, v = k.split('.')
                try:
                    settings['coins'][c][v] = asbool(val) if val in ['false', 'true'] else val
                except KeyError:
                    settings['coins'][c] = {}
                    settings['coins'][c][v] = asbool(val) if val in ['false', 'true'] else val
        self.coin = settings['coins']['coin']
        self.rpcconn = RPCHost(
            'http://{rpcuser}:{rpcpass}@localhost:{rpcport}/'.format(
                rpcuser=self.coin.get('rpcuser', ''),
                rpcpass=self.coin.get('rpcpass', ''),
                rpcport=int(self.coin.get('testnetrpcport', '9999'))))

    def tearDown(self):
        """Teardown."""
        testing.tearDown()

    @unittest.skip("Passed, skipping")
    def test_populate_menu_selection(self):
        sparql = """SELECT ?height ?dt WHERE { ?block <http://purl.org/net/bel-epa/ccy#height> ?height . ?block <http://purl.org/net/bel-epa/ccy#time> ?dt. """
        sparqlfltr = """FILTER (?dt < {})"""
        sparqlordr = """} ORDER BY DESC(?dt) LIMIT 1"""
        for ym in [
              ["2017", ["01", "02", "03", "04"]],
              ["2016", ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]],
              ["2015", ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]],
              ["2014", ["05", "06", "07", "08", "09", "10", "11", "12"]]]:
            y = ym[0]
            for m in ym[1]:
                tgt = int(datetime.datetime.strptime('{}-{}-01T00:00:00.000Z'.format(y, m), '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())
                print(sparql + sparqlfltr.format(tgt) + sparqlordr)

    # @unittest.skip("Passed, skipping")
    def test_extract_genesis_tx(self):
        import struct  # convert between Python values and C structsrepresented as Python strings
        try:
            import StringIO  # Reads and writes a string buffer
        except ImportError:
            from io import StringIO 
        import mmap  # mutable string
        from binascii import unhexlify, hexlify

        class BCDataStream(object):
            def __init__(self):
                self.input = None
                self.read_cursor = 0

            def clear(self):
                self.input = None
                self.read_cursor = 0

            def write(self, bytes):  # Initialize with string of bytes
                if self.input is None:
                    self.input = bytes
                else:
                    self.input += bytes

            def map_file(self, file, start):  # Initialize with bytes from file
                self.input = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)
                self.read_cursor = start

            def seek_file(self, position):
                self.read_cursor = position

            def close_file(self):
                self.input.close()

            def read_string(self):
                # Strings are encoded depending on length:
                # 0 to 252 :  1-byte-length followed by bytes (if any)
                # 253 to 65,535 : byte'253' 2-byte-length followed by bytes
                # 65,536 to 4,294,967,295 : byte '254' 4-byte-length followed by bytes
                # ... and the Bitcoin client is coded to understand:
                # greater than 4,294,967,295 : byte '255' 8-byte-length followed by bytes of string
                # ... but I don't think it actually handles any strings that big.
                if self.input is None:
                    raise SerializationError("call write(bytes) before trying to deserialize")

                try:
                    length = self.read_compact_size()
                except IndexError:
                    raise SerializationError("attempt to read past end of buffer")

                return self.read_bytes(length)

            def write_string(self, string):
                # Length-encoded as with read-string
                self.write_compact_size(len(string))
                self.write(string)

            def read_bytes(self, length):
                try:
                    result = self.input[self.read_cursor:self.read_cursor + length]
                    self.read_cursor += length
                    return result
                except IndexError:
                    raise SerializationError("attempt to read past end of buffer")

                return ''

            def read_boolean(self):
                return self.read_bytes(1)[0] != chr(0)

            def read_int16(self):
                return self._read_num('>h')

            def read_uint16(self):
                return self._read_num('>H')

            def read_int32(self):
                return self._read_num('>i')

            def read_uint32(self):
                return self._read_num('>I')

            def read_int64(self):
                return self._read_num('>q')

            def read_uint64(self):
                return self._read_num('>Q')

            def write_boolean(self, val):
                return self.write(chr(1) if val else chr(0))

            def write_int16(self, val):
                return self._write_num('>h', val)

            def write_uint16(self, val):
                return self._write_num('>H', val)

            def write_int32(self, val):
                return self._write_num('>i', val)

            def write_uint32(self, val):
                return self._write_num('>I', val)

            def write_int64(self, val):
                return self._write_num('>q', val)

            def write_uint64(self, val):
                return self._write_num('>Q', val)

            def read_compact_size(self):
                size = ord(self.input[self.read_cursor])
                self.read_cursor += 1
                if size == 253:
                    size = self._read_num('>H')
                elif size == 254:
                    size = self._read_num('>I')
                elif size == 255:
                    size = self._read_num('>Q')
                return size

            def write_compact_size(self, size):
                if size < 0:
                    raise SerializationError("attempt to write size < 0")
                elif size < 253:
                    self.write(chr(size))
                elif size < 2**16:
                    self.write('\xfd')
                    self._write_num('>H', size)
                elif size < 2**32:
                    self.write('\xfe')
                    self._write_num('>I', size)
                elif size < 2**64:
                    self.write('\xff')
                    self._write_num('>Q', size)

            def _read_num(self, format):
                (i,) = struct.unpack_from(format, self.input, self.read_cursor)
                self.read_cursor += struct.calcsize(format)
                return i

            def _write_num(self, format, num):
                s = struct.pack(format, num)
                self.write(s)

        def import_blkdat():
                pass

        ds = BCDataStream()
        with open("/home/user/.coin/blocks/blk00000.dat", "rb") as file:
            ds.map_file(file, 0)

            # Read file
            # https://bitcoin.org/en/developer-reference#block-headers
            # https://en.bitcoin.it/wiki/Protocol_specification#block
            magic = ds.read_bytes(4).hex()
            block_size = int(struct.pack('>l', *struct.unpack('<l', ds.read_bytes(4))).hex(), 16)
            version = struct.pack('>l', *struct.unpack('<l', ds.read_bytes(4))).hex()
            prev_header_hash = ds.read_bytes(32)[::-1].hex()
            merkle_root_hash = ds.read_bytes(32)[::-1].hex()
            timestamp = ds.read_bytes(4)[::-1].hex()
            nBits = ds.read_bytes(4)[::-1].hex()
            nonce = ds.read_bytes(4)[::-1].hex()

            fproofofburn = ds.read_boolean()
            hashburnblock = ds.read_bytes(32)[::-1].hex()
            burnhash = ds.read_bytes(32)[::-1].hex()
            burnblockheight = ds.read_int32()
            burnctx = ds.read_int32()
            burnctxout = ds.read_int32()
            neffectiveburncoins = ds.read_int64()
            nburnbits = ds.read_uint32()

            num_of_transaction = ds.read_bytes(1)[::-1].hex()
            tx_version = ds.read_bytes(4)[::-1].hex()
            tx_ntime = ds.read_bytes(4)[::-1].hex()
            tx_input = ds.read_bytes(1)[::-1].hex()
            tx_prev_output_hash = ds.read_bytes(32)[::-1].hex()
            tx_prev_output_num = ds.read_bytes(4)[::-1].hex()
            script_length = ds.read_bytes(1)[::-1].hex()
            scriptsig = ds.read_bytes(int((script_length), 16)).hex()
            dunno = ds.read_bytes(1)[::-1].hex()
            sequence = ds.read_bytes(4)[::-1].hex()
            tx_output = ds.read_bytes(1)[::-1].hex()
            BTC_num = ds.read_bytes(8)[::-1].hex()
            pk_script_len = ds.read_bytes(1)[::-1].hex()
            pk_script = ds.read_bytes(int(pk_script_len, 16))[::-1].hex()
            lock_time = ds.read_bytes(4)[::-1].hex()

            print('magic: {} (6e, 8b, 92, a5)'.format(magic))
            print('block_size: {}'.format(block_size))
            print('version: {}'.format(version))
            print('prevhash: {}'.format(prev_header_hash))
            print('merkle_root: {}'.format(merkle_root_hash))
            print('timestamp: {} ({})'.format(int(timestamp, 16), datetime.datetime.fromtimestamp(int(timestamp, 16)).isoformat()))
            print('nBits: {}'.format(nBits))
            print('nonce: {}'.format(int(nonce, 16)))

            print('fproofofburn: {}'.format(fproofofburn))
            print('hashburnblock: {}'.format(hashburnblock))
            print('burnhash: {}'.format(burnhash))
            print('burnblockheight: {}'.format(burnblockheight))
            print('burnctx: {}'.format(burnctx))
            print('burnctxout: {}'.format(burnctxout))
            print('neffectiveburncoins: {}'.format(neffectiveburncoins))
            print('nburnbits: {}'.format(nburnbits))

            print('--------------------- Transaction Details: ---------------------')
            print('num_of_transaction: {}'.format(int(num_of_transaction, 16)))
            print('tx_version: {}'.format(tx_version))
            print('tx_ntime: {} ({})'.format(int(tx_ntime, 16), datetime.datetime.fromtimestamp(int(tx_ntime, 16)).isoformat()))
            print('tx_input_num: {}'.format(int(tx_input, 16)))
            print('tx_prev_output_hash: {}'.format(tx_prev_output_hash))
            print('tx_prev_output_num: {}'.format(tx_prev_output_num))
            print('script_length: {}'.format(int(script_length, 16)))
            print('scriptsig: {}'.format(scriptsig))
            print('dunno: {}'.format(dunno))
            print('sequence: {}'.format(sequence))
            print('tx_output_num: {}'.format(tx_output))
            print('BTC_num: {}'.format(BTC_num))
            print('pk_script_len: {}'.format(pk_script_len))
            print('pk_script: {}'.format(pk_script))
            print('lock_time: {}'.format(lock_time))
            print('lock_time: {} ({})'.format(int(timestamp, 16), datetime.datetime.fromtimestamp(int(lock_time, 16)).isoformat()))

        ds.close_file()

    @unittest.skip("Passed, skipping")
    def test_schema(self):
        """Test schemas."""
        forreal = True
        newuns = 0
        schemas = {}
        txschemas = {}
        for i in ['getinfo', 'getblock', 'getrawtransaction']:
            with open(os.getcwd() + '/schemas/{}_schema.json'.format(i)) as fp:
                schemas[i] = json.loads(fp.read())
            fp.close()

        d = [x for x in os.listdir(os.getcwd() + '/schemas/getrawtransaction') if 'schema' in x]
        for j in d:
            with open(os.getcwd() + '/schemas/getrawtransaction/{}'.format(j)) as fp:
                txschemas[j] = json.loads(fp.read())
            fp.close()

        # Test blockinfo schema
        binfo = self.rpcconn.call('getinfo')
        if forreal:
            validate(binfo, schemas['getinfo'])

        for nheight in range(1, binfo.get('blocks') + 1):
            if nheight % 500 == 0:
                print(nheight)
            print(nheight)
            blockhash = self.rpcconn.call('getblockhash', nheight)
            block = self.rpcconn.call('getblock', blockhash)
            if forreal:
                try:
                    validate(block, schemas['getblock'])
                except exceptions.ValidationError as e:
                    raise Exception("{} {}".format(e, block))
            for tx in block['tx']:
                transaction = self.rpcconn.call('getrawtransaction', tx, 1)
                if forreal:
                    validated = False
                    try:
                        xmltr = StringIO(
                            '<?xml version="1.0"?>\n'
                            '<transaction>\n{}\n</transaction>\n'.format(
                                json2xml(transaction)))
                        with open(os.getcwd() + '/schemas/transaction.rng', 'r') as fp:
                            relaxng_doc = etree.parse(fp)
                        relaxng = etree.RelaxNG(relaxng_doc)
                        try:
                            doc = etree.parse(xmltr)
                        except Exception as e:
                            print(xmltr.read())
                            raise Exception(e)
                        try:
                            relaxng.assertValid(doc)
                        except Exception as e:
                            print("{} {}".format(e, xmltr.read()))
                            raise Exception(e)
                        # validate(transaction, schemas['getrawtransaction'])
                    except exceptions.ValidationError as e:
                        print(json2xml(transaction))
                        # for label, schema in txschemas.items():
                        #     try:
                        #         validate(transaction, schema)
                        #         validated = True
                        #         break
                        #     except exceptions.ValidationError as e:
                        #         pass
                        # if not validated:
                        #     with open(os.getcwd() + '/schemas/getrawtransaction/{}.json'.format(newuns), 'wb') as fp:
                        #         fp.write(json.dumps(transaction, sort_keys=True, indent=2, separators=(',', ': ')).encode('utf-8'))
                        #     fp.close()
                        #     res = Recorder.from_string(json.dumps(transaction))
                        #     res.save_json_schema(os.getcwd() + '/schemas/getrawtransaction/{}_schema.json'.format(newuns), indent=4)
                        #     # schemas['getblock']
                        #     newuns += 1

    @unittest.skip("Passed, skipping")
    def test_fixup(self):
        """Test schemas."""
        schemas = {}
        for i in ['getinfo', 'getblock', 'getrawtransaction']:
            with open(os.getcwd() + '/schemas/{}_schema.json'.format(i)) as fp:
                schemas[i] = json.loads(fp.read())
            fp.close()

        txid = "be151c377da175c2a06e8d8e103575e27440c9819258a92dc80753d144d93019"
        tx = self.rpcconn.call('getrawtransaction', txid, 1)
        # validate(block, schemas['getrawtransaction'])
        try:
            validate(tx, schemas['getrawtransaction'])
        except exceptions.ValidationError as e:
            with open(os.getcwd() + '/schemas/getrawtransaction_no_coinbase.json', 'wb') as fp:
                fp.write(json.dumps(tx, sort_keys=True, indent=2, separators=(',', ': ')).encode('utf-8'))
            fp.close()
            res = Recorder.from_string(json.dumps(tx))
            res.save_json_schema(os.getcwd() + '/schemas/getrawtransaction_no_coinbase.json', indent=4)
            # schemas['getblock']

    @unittest.skip("Passed, skipping")
    def test_novastats00(self):
        """Test schemas."""
        import cgi
        from acme.lib.helpers import novastats
        query = """http://tessier.bel-epa.com:3030/slmchain/sparql?query=PREFIX+ccy%3A+%3Chttp%3A%2F%2Fpurl.org%2Fnet%2Fbel-epa%2Fccy%23%3E%0ASELECT+%3Fheight+%3Fdt%0AWHERE+%7B%0A++%3Fblock+ccy%3Aheight+%3Fheight+.%0A++%3Fblock+ccy%3Atime+%3Fdt.+%0A++FILTER(%3Fdt+%3C+{timestamp})%0A%7D%0AORDER+BY+DESC(%3Fdt)+LIMIT+1"""
        for i in novastats:
            d = datetime.datetime.strptime(i['ticker'], "%Y-%m-%dT%H:%M:%SZ")
            ts = int(d.timestamp())
            res = requests.get(query.format(timestamp=ts)).content.decode('utf-8')
            resd = json.loads(res)
            height = resd['results']['bindings'][0]['height']['value']
            bdate = resd['results']['bindings'][0]['dt']['value']
            print("""[{d}, {h}, "{t}"],""".format(t=i['ticker'], h=height, d=bdate))

    @unittest.skip("Passed, skipping")
    def test_novastats01(self):
        """Test schemas."""
        from pprint import pprint 
        from acme.lib.helpers import novastats, novaheights
        for i, _ in enumerate(novastats):
            assert novastats[i]['ticker'] == novaheights[i][2]
            novastats[i]['block'] = novaheights[i][1]          
            novastats[i]['timestamp'] = novaheights[i][0]
        print(repr(novastats))

    @unittest.skip("Passed, skipping")
    def test_novadata(self):
        """Test schemas."""
        from pprint import pprint 
        from acme.lib.helpers import novadata
        for d in novadata:
            # Date,Open,High,Low,Close,Volume 
            # 9-Jun-14,62.40,63.34,61.79,62.88,37617413

            # print('[{ts},{o:03.8f},{h:03.8f},{l:03.8f},{c:03.8f},{v}],'.format(
            #     o=d.get('open'), h=d.get('high'), l=d.get('low'),
            #     c=d.get('close'), v=d.get('volume')))
            print('{ts},{o:03.8f},{h:03.8f},{l:03.8f},{c:03.8f},{v:03.8f}'.format(
                o=d.get('open'), h=d.get('high'), l=d.get('low'),
                c=d.get('close'), ts=d.get('timestamp'), v=d.get('volume')))

    @unittest.skip("Passed, skipping")
    def test_novaupdate(self):
        """Test schemas."""
        from pprint import pprint 
        from acme.lib.helpers import novadata
        acmerpc = RPCHost('http://{}:{}@localhost:{}/'.format(
            self.coin.get('rpcuser'), self.coin.get('rpcpass'),
            self.coin.get('rpcport')))
        for d in novadata:
            # print(novadata[i])
            bh = d.get('block')
            blcn = acmerpc.call(
                'getblock', acmerpc.call(
                    'getblockhash', bh))
            print(blcn.get('mint'))

    @unittest.skip("Passed, skipping")
    def test_sparqlemission(self):
        sym = self.coin.symbol.lower()
        testnet = False
        mainnetquery = """http://localhost.com:3030/{}chain/sparql?query=PREFIX+ccy%3A+%3Chttp%3A%2F%2Fpurl.org%2Fnet%2Fbel-epa%2Fccy%23%3E%0ASELECT+%3Fheight+%3Fdt%0AWHERE+%7B%0A++%3Fblock+ccy%3Aheight+%3Fheight+.%0A++%3Fblock+ccy%3Atime+%3Fdt.+%0A++FILTER(%3Fdt+%3C+{timestamp})%0A%7D%0AORDER+BY+DESC(%3Fdt)+LIMIT+1""".format(sym)
        testnetquery = """http://localhost:3030/{}tchain/sparql?query=PREFIX+ccy%3A+%3Chttp%3A%2F%2Fpurl.org%2Fnet%2Fbel-epa%2Fccy%23%3E%0ASELECT+%3Fheight+%3Fdt%0AWHERE+%7B%0A++%3Fblock+ccy%3Aheight+%3Fheight+.%0A++%3Fblock+ccy%3Atime+%3Fdt.+%0A++FILTER(%3Fdt+%3C+{timestamp})%0A%7D%0AORDER+BY+DESC(%3Fdt)+LIMIT+1""".format(sym)
        if testnet:
            query = testnetquery
            psz = datetime.date(year=2017, month=4, day=15)
        else:
            query = mainnetquery
            psz = datetime.date(year=2014, month=5, day=28)
        ptr = psz
        nextday = datetime.timedelta(days=1)
        for day in range(0, (datetime.date.today() - psz).days):
            # if day > 1:
            #     break
            if day % 100 == 0:
                print(day)
            ptr += nextday
            # print('{}-{}-{}T00:00:00.000Z'.format(ptr.year, ptr.month, ptr.day))
            ts = int(datetime.datetime.strptime('{}-{}-{}T00:00:00.000Z'.format(ptr.year, ptr.month, ptr.day), '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())
            # print(query.format(timestamp=ts))
            res = requests.get(query.format(timestamp=ts)).content.decode('utf-8')
            # print(res)
            resd = json.loads(res)
            height = resd['results']['bindings'][0]['height']['value']
            bdate = resd['results']['bindings'][0]['dt']['value']
            datum = '''"{t}",{h},{d}\n'''.format(t=ptr, h=height, d=bdate)
            with open('emissions.csv', 'a') as fp:
                fp.write(datum)
            fp.close()
            # print(datum)

    @unittest.skip("Passed, skipping")
    def test_get_emissions(self):
        # unittests already imported
        import json
        import requests
        import datetime

        # switch endpoint
        testnet = True

        # template SPARQL query returning the block height of the next minted
        # block after {timestamp}
        querytmpl = \
            '''?query=PREFIX+ccy%3A+%3Chttp%3A%2F%2Fpurl.org%2Fnet%2F''' \
            '''bel-epa%2Fccy%23%3E%0ASELECT+%3Fheight+%3Fdt%0AWHERE+%''' \
            '''7B%0A++%3Fblock+ccy%3Aheight+%3Fheight+.%0A++%3Fblock+''' \
            '''ccy%3Atime+%3Fdt.+%0A++FILTER(%3Fdt+%3C+{timestamp})%0''' \
            '''A%7D%0AORDER+BY+DESC(%3Fdt)+LIMIT+1'''

        url = '''http://localhost:3030/{}/sparql'''.format(
            'slmtchain' if testnet else 'slmchain')

        # Initialise the starting date
        ptr = psz = datetime.date(year=2017, month=4, day=15) if testnet \
            else datetime.date(year=2014, month=5, day=28)

        # Create a day incrementer
        nextday = datetime.timedelta(days=1)

        # Save results in comma-separated format
        with open('/tmp/{}-emissions.csv'.format(
                'testnet' if testnet else 'mainnet'), 'w') as fp:

            # create day range to drive iteration
            for day in range(0, (datetime.date.today() - psz).days):

                # Blurt progress
                if day % 100 == 0:
                    print(day)

                # Increment the date pointer by one day
                ptr += nextday

                # Create timestamp from date pointer
                ts = int(datetime.datetime.strptime(
                    '{}-{}-{}T00:00:00.000Z'.format(
                        ptr.year, ptr.month, ptr.day),
                    '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())

                # Execute the SPARQL query
                res = requests.get(url + querytmpl.format(
                    timestamp=ts)
                ).content.decode('utf-8')

                # Marshal and persist the results for the given day
                resd = json.loads(res)
                height = resd['results']['bindings'][0]['height']['value']
                bdate = resd['results']['bindings'][0]['dt']['value']
                datum = '''"{t}",{h},{d}\n'''.format(t=ptr, h=height, d=bdate)
                fp.write(datum)
        fp.close()

    @unittest.skip("Passed, skipping")
    def test_sparqldaystats(self):
        testnet = True
        sym = self.coin.symbol.lower()
        url = 'http://localhost:3030/slmtchain/sparql' if testnet \
            else 'http://localhost:3030/{}chain/sparql'.format(sym)
        query = \
            '?query=PREFIX+ccy%3A+%3Chttp%3A%2F%2Fpurl.org%2Fnet%2Fbel-epa%2F' \
            'ccy%23%3E%0A%23+SELECT+%3Fblock+%3Fheight+WHERE+%7B+%3Fblock+ccy%3' \
            'Aheight+%3Fheight+%7D+ORDER+BY+DESC(%3Fheight)+LIMIT+1%0ASELECT+%3' \
            'Fheight+%3Fdt+%3Fmint+%3Fdiff+%3Fflags+WHERE+%7B%0A++++%3Fblock+cc' \
            'y%3Aheight+%3Fheight+.%0A++++%3Fblock+ccy%3Atime+%3Fdt+.%0A++++%3F' \
            'block+ccy%3Amint+%3Fmint+.%0A++++%3Fblock+ccy%3Adifficulty+%3Fdiff' \
            '+.%0A++++%3Fblock+ccy%3Aflags+%3Fflags+.%0A++FILTER+((%3Fdt+%3E+{f' \
            'romdate})+%26%26+(%3Fdt+%3C+{todate}))%0A%7D+ORDER+BY+ASC(%3Fdt)%0A'
        ptr = psz = datetime.date(year=2017, month=4, day=15) if testnet \
            else datetime.date(year=2014, month=5, day=28)
        nextday = datetime.timedelta(days=1)
        with open('{}-daystats.csv'.format('testnet' if testnet else 'mainnet'), 'w') as fp:
            for day in range(0, (datetime.date.today() - psz).days):
                # if day > 1:
                #     break
                fromdate = int(datetime.datetime.strptime('{}-{}-{}T00:00:00.000Z'.format(
                    ptr.year, ptr.month, ptr.day), '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())
                # print('{}-{}-{}T00:00:00.000Z'.format(ptr.year, ptr.month, ptr.day))
                ptr += nextday
                todate = int(datetime.datetime.strptime(
                    '{}-{}-{}T00:00:00.000Z'.format(
                        ptr.year, ptr.month, ptr.day),
                    '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())
                # print(query.format(timestamp=ts))
                res = requests.get(url + query.format(
                    fromdate=fromdate, todate=todate)
                ).content.decode('utf-8')
                print(res)
                resd = json.loads(res)
                try:
                    height = resd['results']['bindings'][0]['height']['value']
                    bdate = resd['results']['bindings'][0]['dt']['value']
                    mint = resd['results']['bindings'][0]['mint']['value']
                    diff = resd['results']['bindings'][0]['diff']['value']
                    flags = resd['results']['bindings'][0]['flags']['value']
                    datum = '{b}\t{h}\t{t}\t{m}\t{d}\t{f}\n'.format(
                        b=bdate, h=height, t=ptr, m=mint, d=diff, f=flags)
                    fp.write(datum)
                except Exception as e:
                    print("Day {}-{}, {}".format(datetime.datetime.fromtimestamp(fromdate), datetime.datetime.fromtimestamp(todate), e))
                    raise Exception(e)
            fp.close()
            # print(datum)

    @unittest.skip("Passed, skipping")
    def test_cmcap(self):
        cmcap = {
            "market_cap_by_available_supply": [[1424013265000, 0], [1426030164000, 15174], [1426126166000, 15354], [1426212565000, 15739], [1426300466000, 15129], [1426394667000, 14251], [1426481066000, 17198], [1426600765000, 15847], [1426687168000, 14518], [1426780765000, 15276], [1426867166000, 14755], [1426953566000, 15493], [1427039965000, 15175], [1427160267000, 15886], [1427246668000, 14157], [1427341466000, 13569], [1427525665000, 14325], [1427695166000, 13627], [1427781566000, 13168], [1427867962000, 13476], [1427964566000, 13629], [1428052466000, 14480], [1428138866000, 14939], [1428226166000, 15071], [1428365066000, 15445], [1428460165000, 13164], [1428547166000, 14365], [1428633565000, 14273], [1428719965000, 12397], [1428806366000, 11857], [1428892765000, 9951], [1429295366000, 7156], [1429381765000, 10126], [1429663765000, 6338], [1495707257000, 0], [1495938858000, 0], [1496025256000, 0], [1496360960000, 0], [1496459959000, 0], [1496546358000, 0], [1496654657000, 0], [1496741059000, 0], [1496827460000, 0], [1496916264000, 0], [1497002659000, 0], [1497095959000, 0], [1497182360000, 0], [1497268762000, 0], [1497355162000, 0], [1497441559000, 0], [1497989964000, 0], [1498130363000, 0], [1498295661000, 0], [1498777444000, 0], [1498863844000, 0], [1498950244000, 0], [1499036645000, 0], [1499581146000, 0], [1499716750000, 0], [1499803169000, 0], [1499916846000, 0], [1500004749000, 0], [1500091144000, 0], [1500177544000, 0], [1500263944000, 0], [1500350344000, 0], [1500436744000, 0], [1500523149000, 0], [1500609544000, 0], [1500695944000, 0], [1500782346000, 0], [1500868754000, 0], [1501003159000, 0], [1501105763000, 0], [1501192153000, 0], [1501278556000, 0], [1501364964000, 0], [1501451372000, 0], [1501537761000, 0], [1501624163000, 0], [1501710557000, 0], [1501796962000, 0], [1501883360000, 0], [1501969757000, 0], [1502030048000, 0]],
            "price_btc": [[1424013265000, 2.88531e-05], [1426030164000, 2.19854e-05], [1426126166000, 2.19668e-05], [1426212565000, 2.24432e-05], [1426300466000, 2.24524e-05], [1426394667000, 2.1001e-05], [1426481066000, 2.4494e-05], [1426600765000, 2.24987e-05], [1426687168000, 2.19923e-05], [1426780765000, 2.39927e-05], [1426867166000, 2.29652e-05], [1426953566000, 2.4e-05], [1427039965000, 2.35118e-05], [1427160267000, 2.39886e-05], [1427246668000, 2.3028e-05], [1427341466000, 2.20208e-05], [1427525665000, 2.24874e-05], [1427695166000, 2.1981e-05], [1427781566000, 2.0994e-05], [1427867962000, 2.18e-05], [1427964566000, 2.1792e-05], [1428052466000, 2.21914e-05], [1428138866000, 2.32177e-05], [1428226166000, 2.32101e-05], [1428365066000, 2.338e-05], [1428460165000, 2.00207e-05], [1428547166000, 2.25261e-05], [1428633565000, 2.24945e-05], [1428719965000, 2.00143e-05], [1428806366000, 1.90038e-05], [1428892765000, 1.60008e-05], [1429295366000, 1.20039e-05], [1429381765000, 1.69757e-05], [1429663765000, 9.99702e-06], [1495707257000, 1.9e-06], [1495938858000, 3.25e-06], [1496025256000, 3.25e-06], [1496360960000, 2.7e-06], [1496459959000, 2.05e-06], [1496546358000, 3.7e-06], [1496654657000, 2.5e-06], [1496741059000, 2.69e-06], [1496827460000, 3.03e-06], [1496916264000, 3.3e-06], [1497002659000, 3.3e-06], [1497095959000, 3.35e-06], [1497182360000, 5.6e-06], [1497268762000, 3.38e-06], [1497355162000, 3.51e-06], [1497441559000, 1.26e-06], [1497989964000, 1.37e-06], [1498130363000, 1.3e-06], [1498295661000, 2.24e-06], [1498777444000, 1.62e-06], [1498863844000, 1.64e-06], [1498950244000, 1.31e-06], [1499036645000, 1.27e-06], [1499581146000, 8e-07], [1499716750000, 4.1e-06], [1499803169000, 4.5e-06], [1499916846000, 5.52e-06], [1500004749000, 5e-06], [1500091144000, 4.31e-06], [1500177544000, 5.01e-06], [1500263944000, 8e-06], [1500350344000, 5.55e-06], [1500436744000, 5.95e-06], [1500523149000, 5.2e-06], [1500609544000, 4.32e-06], [1500695944000, 4.32e-06], [1500782346000, 4.44e-06], [1500868754000, 1e-05], [1501003159000, 5.66e-06], [1501105763000, 5.52e-06], [1501192153000, 5.5e-06], [1501278556000, 5.52e-06], [1501364964000, 4.21e-06], [1501451372000, 4.37e-06], [1501537761000, 4.14e-06], [1501624163000, 4.56e-06], [1501710557000, 4.01e-06], [1501796962000, 5.11e-06], [1501883360000, 1.5e-05], [1501969757000, 8.46e-06], [1502030048000, 8.54e-06]],
            "price_usd": [[1424013265000, 0.00708782], [1426030164000, 0.00643139], [1426126166000, 0.00647383], [1426212565000, 0.00660677], [1426300466000, 0.00634653], [1426394667000, 0.00595083], [1426481066000, 0.00714714], [1426600765000, 0.00654336], [1426687168000, 0.00596941], [1426780765000, 0.00624966], [1426867166000, 0.00601087], [1426953566000, 0.00628051], [1427039965000, 0.00613829], [1427160267000, 0.00638779], [1427246668000, 0.0056706], [1427341466000, 0.00541552], [1427525665000, 0.0057013], [1427695166000, 0.00539937], [1427781566000, 0.0052051], [1427867962000, 0.00531351], [1427964566000, 0.00535626], [1428052466000, 0.00567145], [1428138866000, 0.00582997], [1428226166000, 0.00585907], [1428365066000, 0.00597341], [1428460165000, 0.00507221], [1428547166000, 0.00551547], [1428633565000, 0.00546093], [1428719965000, 0.0047287], [1428806366000, 0.00450994], [1428892765000, 0.00377336], [1429295366000, 0.00267971], [1429381765000, 0.00378196], [1429663765000, 0.00234756], [1495707257000, 0.0050813], [1495938858000, 0.00692503], [1496025256000, 0.00704406], [1496360960000, 0.00644534], [1496459959000, 0.00507091], [1496546358000, 0.00923742], [1496654657000, 0.00640862], [1496741059000, 0.00766567], [1496827460000, 0.00852906], [1496916264000, 0.00917575], [1497002659000, 0.00924568], [1497095959000, 0.00965945], [1497182360000, 0.0161133], [1497268762000, 0.00913765], [1497355162000, 0.00942776], [1497441559000, 0.00344693], [1497989964000, 0.00342227], [1498130363000, 0.00324741], [1498295661000, 0.00607929], [1498777444000, 0.00411345], [1498863844000, 0.00402266], [1498950244000, 0.00314863], [1499036645000, 0.00316482], [1499581146000, 0.00202746], [1499716750000, 0.00989145], [1499803169000, 0.0103715], [1499916846000, 0.0133272], [1500004749000, 0.0115789], [1500091144000, 0.00905203], [1500177544000, 0.0101893], [1500263944000, 0.0157237], [1500350344000, 0.0119882], [1500436744000, 0.0139139], [1500523149000, 0.0120863], [1500609544000, 0.0114925], [1500695944000, 0.0116928], [1500782346000, 0.012532], [1500868754000, 0.0274719], [1501003159000, 0.0143148], [1501105763000, 0.0137244], [1501192153000, 0.0144915], [1501278556000, 0.0152151], [1501364964000, 0.0114233], [1501451372000, 0.011951], [1501537761000, 0.011838], [1501624163000, 0.0124384], [1501710557000, 0.0107372], [1501796962000, 0.0142108], [1501883360000, 0.0424609], [1501969757000, 0.0271615], [1502030048000, 0.0274727]],
            "volume_usd": [[1424013265000, 52], [1426030164000, 15], [1426126166000, 4], [1426212565000, 2], [1426300466000, 3], [1426394667000, 1], [1426481066000, 16], [1426600765000, 13], [1426687168000, 7], [1426780765000, 0], [1426867166000, 0], [1426953566000, 8], [1427039965000, 3], [1427160267000, 4], [1427246668000, 1], [1427341466000, 0], [1427525665000, 4], [1427695166000, 2], [1427781566000, 1], [1427867962000, 1], [1427964566000, 2], [1428052466000, 0], [1428138866000, 9], [1428226166000, 3], [1428365066000, 0], [1428460165000, 1], [1428547166000, 0], [1428633565000, 7], [1428719965000, 2], [1428806366000, 4], [1428892765000, 8], [1429295366000, 3], [1429381765000, 1], [1429663765000, 12], [1495707257000, 24], [1495938858000, 417], [1496025256000, 2], [1496360960000, 11], [1496459959000, 128], [1496546358000, 94], [1496654657000, 135], [1496741059000, 1122], [1496827460000, 160], [1496916264000, 47], [1497002659000, 16], [1497095959000, 89], [1497182360000, 43], [1497268762000, 72], [1497355162000, 115], [1497441559000, 5323], [1497989964000, 382], [1498130363000, 19], [1498295661000, 124], [1498777444000, 7], [1498863844000, 14], [1498950244000, 79], [1499036645000, 44], [1499581146000, 2], [1499716750000, 892], [1499803169000, 1993], [1499916846000, 374], [1500004749000, 99], [1500091144000, 201], [1500177544000, 1734], [1500263944000, 2600], [1500350344000, 298], [1500436744000, 184], [1500523149000, 118], [1500609544000, 45], [1500695944000, 2563], [1500782346000, 214], [1500868754000, 2054], [1501003159000, 27], [1501105763000, 12], [1501192153000, 603], [1501278556000, 179], [1501364964000, 2596], [1501451372000, 2048], [1501537761000, 1169], [1501624163000, 545], [1501710557000, 45], [1501796962000, 928], [1501883360000, 611], [1501969757000, 539], [1502030048000, 32]]
        }
        mcap = cmcap["market_cap_by_available_supply"]
        btc = cmcap["price_btc"]
        usd = cmcap["price_usd"]
        vol = cmcap["volume_usd"]
        for m, b, u, v in zip(mcap, btc, usd, vol):
            m0 = m[0]
            m1 = m[1]
            b1 = b[1]
            u1 = u[1]
            v1 = v[1]
            try:
                print('{},{},{:0.8f},{:0.8f},{}'.format(
                    int(m0 / 1000), m1, b1, u1, v1))
            except Exception as e:
                print("{} {}".format([m, b, u, v], e))
                raise Exception(e)

    @unittest.skip("Passed, skipping")
    def test_bterohlc(self):
        with open('slmbter.csv', 'r') as fp:
            csv = [d.split('\t') for d in fp.read().split('\n')]
        print(csv[0])

    @unittest.skip("Passed, skipping")
    def test_cmcapblocks(self):
        testnet = False
        mainnetquery = """http://localhost:3030/slmchain/sparql?query=PREFIX+ccy%3A+%3Chttp%3A%2F%2Fpurl.org%2Fnet%2Fbel-epa%2Fccy%23%3E%0ASELECT+%3Fheight+%3Fdt%0AWHERE+%7B%0A++%3Fblock+ccy%3Aheight+%3Fheight+.%0A++%3Fblock+ccy%3Atime+%3Fdt.+%0A++FILTER(%3Fdt+%3C+{timestamp})%0A%7D%0AORDER+BY+DESC(%3Fdt)+LIMIT+1"""
        testnetquery = """http://localhost:3030/slmtchain/sparql?query=PREFIX+ccy%3A+%3Chttp%3A%2F%2Fpurl.org%2Fnet%2Fbel-epa%2Fccy%23%3E%0ASELECT+%3Fheight+%3Fdt%0AWHERE+%7B%0A++%3Fblock+ccy%3Aheight+%3Fheight+.%0A++%3Fblock+ccy%3Atime+%3Fdt.+%0A++FILTER(%3Fdt+%3C+{timestamp})%0A%7D%0AORDER+BY+DESC(%3Fdt)+LIMIT+1"""
        if testnet:
            query = testnetquery
        else:
            query = mainnetquery
        with open('cmcap.csv', 'r') as fp:
            csv = [d.split(',') for d in fp.read().split('\n')][1:]
        for dt in csv[:1]:
            ts = int(dt[0])
            res = requests.get(query.format(timestamp=ts)).content.decode('utf-8')
            # print(res)
            resd = json.loads(res)
            height = resd['results']['bindings'][0]['height']['value']
            bdate = resd['results']['bindings'][0]['dt']['value']
            datum = '''{h},{d}\n'''.format(h=height, d=bdate)
            # with open('emissions.csv', 'a') as fp:
            #     fp.write(datum)
            # fp.close()
            print(datum)

    @unittest.skip("Passed, skipping")
    def test_activitystreams(self):
        from lxml import etree
        with open('data.html', 'r') as fp:
            html = fp.read()
        fp.close()
        root = etree.HTML(html)
        examples = root.xpath('//div[@class="example"]')
        for example in examples:
            title = ''.join(example.xpath('./div[@class="example-title marker"]/span/text()'))
            content = example.xpath('string()').strip()
            titlend = content.find('\n')
            title = content[:titlend]
            content = content[titlend:].strip()
            print('{} = """{}"""\n'.format(title.lower().replace(' ', ''), content))

    @unittest.skip("Passed, skipping")
    def test_asread(self):
        from examples import examples
        from rdflib import Graph
        g = Graph()
        for label, example in examples.items():
            g1 = Graph()
            try:
                g1.parse(data=example, format="json-ld")
                g += g1
            except Exception as e:
                print(label)
            del g1
        print(g.serialize(format="n3").decode('utf-8'))

if __name__ == "__main__":
    unittest.main()


"""
PREFIX ccy: <http://purl.org/net/bel-epa/ccy#>
SELECT ?tx ?bh ?txo ?dt ?asm
WHERE {
  ?tx ccy:output ?txo .
  ?txo ccy:pkasm ?asm .
    { SELECT ?bh ?dt WHERE {
        ?tx ccy:blockhash ?bh .
        ?tx ccy:time ?dt. }
    LIMIT 1 } . 
    FILTER regex(?asm, "OP_RETURN")
} ORDER BY DESC(?dt)

SELECT ?tx ?bh ?txo ?dt ?asm
WHERE {
  ?tx ccy:output ?txo .
  ?txo ccy:pkasm ?asm .
#  { SELECT DISTINCT ?bh ?dt WHERE {
#        ?tx ccy:blockhash ?bh .
#        ?tx ccy:time ?dt. }
#    LIMIT 1 } . 
  ?tx ccy:blockhash ?bh .
  ?tx ccy:time ?dt .
  FILTER regex(?asm, "OP_RETURN")
} ORDER BY DESC(?dt)
"""
