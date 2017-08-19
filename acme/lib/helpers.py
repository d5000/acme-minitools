# -*- coding: utf-8 -*-
"""
Helper functions

"""
import logging
from . import iso8601
from datetime import datetime, tzinfo, timedelta
from io import StringIO
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.httpexceptions import status_map
import json
import requests
import time


log = logging.getLogger(__name__)


# http://upcoder.com/7/bitcoin-rpc-from-python


class RPCHost(object):
    def __init__(self, url):
        self._session = requests.Session()
        self._url = url
        self._headers = {'content-type': 'application/json'}

    def call(self, rpcMethod, *params):
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


def abort(code, **kwargs):
    raise status_map[code]('Not found' if code == 404 else '')


def redirect_to(loc):
    return HTTPFound(location=loc)


def redirect(url, code=302):
    """Raises a redirect exception to the specified URL

    Optionally, a code variable may be passed with the status code of
    the redirect, ie::

        redirect(url(controller='home', action='index'), code=303)

    """
    exc = status_map[code]
    raise exc(location=url).exception


def fix_unicode(unicrap):
    """This takes a UNICODE string and replaces Latin-1 characters with
        something equivalent in 7-bit ASCII. It returns a plain ASCII string.
        This function makes a best effort to convert Latin-1 characters into
        ASCII equivalents. It does not just strip out the Latin-1 characters.
        All characters in the standard 7-bit ASCII range are preserved.
        In the 8th bit range all the Latin-1 accented letters are converted
        to unaccented equivalents. Most symbol characters are converted to
        something meaningful. Anything not converted is deleted.
    """
    xlate = {
        0xc0: 'A', 0xc1: 'A', 0xc2: 'A', 0xc3: 'A', 0xc4: 'A', 0xc5: 'A',
        0xc6: 'Ae', 0xc7: 'C',
        0xc8: 'E', 0xc9: 'E', 0xca: 'E', 0xcb: 'E',
        0xcc: 'I', 0xcd: 'I', 0xce: 'I', 0xcf: 'I',
        0xd0: 'Th', 0xd1: 'N',
        0xd2: 'O', 0xd3: 'O', 0xd4: 'O', 0xd5: 'O', 0xd6: 'O', 0xd8: 'O',
        0xd9: 'U', 0xda: 'U', 0xdb: 'U', 0xdc: 'U',
        0xdd: 'Y', 0xde: 'th', 0xdf: 'ss',
        0xe0: 'a', 0xe1: 'a', 0xe2: 'a', 0xe3: 'a', 0xe4: 'a', 0xe5: 'a',
        0xe6: 'ae', 0xe7: 'c',
        0xe8: 'e', 0xe9: 'e', 0xea: 'e', 0xeb: 'e',
        0xec: 'i', 0xed: 'i', 0xee: 'i', 0xef: 'i',
        0xf0: 'th', 0xf1: 'n',
        0xf2: 'o', 0xf3: 'o', 0xf4: 'o', 0xf5: 'o', 0xf6: 'o', 0xf8: 'o',
        0xf9: 'u', 0xfa: 'u', 0xfb: 'u', 0xfc: 'u',
        0xfd: 'y', 0xfe: 'th', 0xff: 'y',
        0xa1: '!', 0xa2: '{cent}', 0xa3: '{pound}', 0xa4: '{currency}',
        0xa5: '{yen}', 0xa6: '|', 0xa7: '{section}', 0xa8: '{umlaut}',
        0xa9: '{C}', 0xaa: '{^a}', 0xab: '<<', 0xac: '{not}',
        0xad: '-', 0xae: '{R}', 0xaf: '_', 0xb0: '{degrees}',
        0xb1: '{+/-}', 0xb2: '{^2}', 0xb3: '{^3}', 0xb4: "'",
        0xb5: '{micro}', 0xb6: '{paragraph}', 0xb7: '*', 0xb8: '{cedilla}',
        0xb9: '{^1}', 0xba: '{^o}', 0xbb: '>>',
        0xbc: '{1/4}', 0xbd: '{1/2}', 0xbe: '{3/4}', 0xbf: '?',
        0xd7: '*', 0xf7: '/'}

    r = ''
    for i in unicrap:
        if ord(i) in xlate:
            r += xlate[ord(i)]
        elif ord(i) >= 0x80:
            pass
        else:
            r += str(i)
    return r


def truncate_content(s, n):
    try:
        words = []
        for word in s.split(' '):
            if len(' '.join(words)) < n:
                words += [word]
            else:
                return ' '.join(words) + ' [...]'
        return ' '.join(words)
    except (UnicodeDecodeError, UnicodeEncodeError):
        return s


def graph_to_dot(graph, dot):
    """
    Turns graph into dot (graphviz graph drawing format) using pydot.
    """
    nodes = {}
    for s, o in graph.subject_objects():
        for i in s, o:
            if i not in nodes.keys():
                # nodes[i] = pydot.Node(str(i.split('/')[1]) \
                #     if i.startswith('http') else str(i), fontcolor="red")
                nodes[i] = i.replace(
                    'http://purl.org/net/bel-epa/ccy#', '')
                # foo = 1 + ''
    for s, p, o in graph.triples((None, None, None)):
        dot.add_edge(pydot.Edge(nodes[s], nodes[o],
                     label=str(p).split('/')[-1], color='blue',
                     fontcolor='green'))


def difflag(data, scheme=["proof-of-work"]):

    import acme.lib.svgdatashapes as s

    dataset = [(b[0], b[2]) for b in data]

    s.svgbegin(width=1000, height=400)

    textstyle = 'font-family: sans-serif;font-size:0.8em;'
    s.settext(color='#bbb', style=textstyle)
    s.setline(color='#888')

    # find the data min and max in X
    for dp in dataset:
        s.findrange(testval=dp[0])    
    xrange = s.findrange(finish=True)
    # xrange.poshi -= 10 

    # find the data min and max in Y
    for dp in dataset:
        s.findrange(testval=dp[1])    
    yrange = s.findrange(finish=True)

    # set up X and Y space...
    s.xspace(svgrange=(100, 950), datarange=xrange)
    s.yspace(svgrange=(100, 350), datarange=yrange)

    # render axes and a shaded plotting area
    s.xaxis(tics=8, loc='min-8', stubrotate=False, stubformat="%d")
    s.yaxis(tics=8, loc='min-8')
    s.plotdeco(shade='transparent', outline=False, rectadj=8)

    # render axis labels with superscript, greek char...
    s.plotdeco(ylabel='difficulty', xlabel='block number')

    # render dataset1 in red data points
    for i, dp in enumerate(dataset):
        dotcolour = {
            'proof-of-work': '#0f0',
            'proof-of-stake stake-modifier': '#00f',
            'proof-of-stake': '#00f',
            'proof-of-burn': '#f00'}.get(
                data[i][3], '#999')
        s.tooltip(str(data[i][0]) + ': ' + str(dp[1]) + ',' + data[i][3])
        s.datapoint(x=dp[0], y=dp[1], color=dotcolour, diameter=12, opacity=0.75)

    # create a legend...
    if 'proof-of-work' in scheme:
        s.legenditem(label='pow', sample='circle', color='#0f0', width=40)
    if 'proof-of-stake' in scheme:
        s.legenditem(label='pos', sample='circle', color='#00f', width=40)
    if 'proof-of-burn' in scheme:
        s.legenditem(label='pob', sample='circle', color='#f00', width=40)
    s.legendrender(location='top', yadjust=30, format='across')

    # return the svg.  The caller could then add it in to the rendered HTML.
    return s.svgresult()

iso22iso3 = {
    "AD": "AND", "AE": "ARE", "AF": "AFG", "AG": "ATG", "AI": "AIA",
    "AL": "ALB", "AM": "ARM", "AO": "AGO", "AQ": "ATA", "AR": "ARG",
    "AS": "ASM", "AT": "AUT", "AU": "AUS", "AW": "ABW", "AX": "ALA",
    "AZ": "AZE", "BA": "BIH", "BB": "BRB", "BD": "BGD", "BE": "BEL",
    "BF": "BFA", "BG": "BGR", "BH": "BHR", "BI": "BDI", "BJ": "BEN",
    "BL": "BLM", "BM": "BMU", "BN": "BRN", "BO": "BOL", "BQ": "BES",
    "BR": "BRA", "BS": "BHS", "BT": "BTN", "BV": "BVT", "BW": "BWA",
    "BY": "BLR", "BZ": "BLZ", "CA": "CAN", "CC": "CCK", "CD": "COD",
    "CF": "CAF", "CG": "COG", "CH": "CHE", "CI": "CIV", "CK": "COK",
    "CL": "CHL", "CM": "CMR", "CN": "CHN", "CO": "COL", "CR": "CRI",
    "CU": "CUB", "CV": "CPV", "CW": "CUW", "CX": "CXR", "CY": "CYP",
    "CZ": "CZE", "DE": "DEU", "DJ": "DJI", "DK": "DNK", "DM": "DMA",
    "DO": "DOM", "DZ": "DZA", "EC": "ECU", "EE": "EST", "EG": "EGY",
    "EH": "ESH", "ER": "ERI", "ES": "ESP", "ET": "ETH", "FI": "FIN",
    "FJ": "FJI", "FK": "FLK", "FM": "FSM", "FO": "FRO", "FR": "FRA",
    "GA": "GAB", "GB": "GBR", "GD": "GRD", "GE": "GEO", "GF": "GUF",
    "GG": "GGY", "GH": "GHA", "GI": "GIB", "GL": "GRL", "GM": "GMB",
    "GN": "GIN", "GP": "GLP", "GQ": "GNQ", "GR": "GRC", "GS": "SGS",
    "GT": "GTM", "GU": "GUM", "GW": "GNB", "GY": "GUY", "HK": "HKG",
    "HM": "HMD", "HN": "HND", "HR": "HRV", "HT": "HTI", "HU": "HUN",
    "ID": "IDN", "IE": "IRL", "IL": "ISR", "IM": "IMN", "IN": "IND",
    "IO": "IOT", "IQ": "IRQ", "IR": "IRN", "IS": "ISL", "IT": "ITA",
    "JE": "JEY", "JM": "JAM", "JO": "JOR", "JP": "JPN", "KE": "KEN",
    "KG": "KGZ", "KH": "KHM", "KI": "KIR", "KM": "COM", "KN": "KNA",
    "KP": "PRK", "KR": "KOR", "XK": "XKX", "KW": "KWT", "KY": "CYM",
    "KZ": "KAZ", "LA": "LAO", "LB": "LBN", "LC": "LCA", "LI": "LIE",
    "LK": "LKA", "LR": "LBR", "LS": "LSO", "LT": "LTU", "LU": "LUX",
    "LV": "LVA", "LY": "LBY", "MA": "MAR", "MC": "MCO", "MD": "MDA",
    "ME": "MNE", "MF": "MAF", "MG": "MDG", "MH": "MHL", "MK": "MKD",
    "ML": "MLI", "MM": "MMR", "MN": "MNG", "MO": "MAC", "MP": "MNP",
    "MQ": "MTQ", "MR": "MRT", "MS": "MSR", "MT": "MLT", "MU": "MUS",
    "MV": "MDV", "MW": "MWI", "MX": "MEX", "MY": "MYS", "MZ": "MOZ",
    "NA": "NAM", "NC": "NCL", "NE": "NER", "NF": "NFK", "NG": "NGA",
    "NI": "NIC", "NL": "NLD", "NO": "NOR", "NP": "NPL", "NR": "NRU",
    "NU": "NIU", "NZ": "NZL", "OM": "OMN", "PA": "PAN", "PE": "PER",
    "PF": "PYF", "PG": "PNG", "PH": "PHL", "PK": "PAK", "PL": "POL",
    "PM": "SPM", "PN": "PCN", "PR": "PRI", "PS": "PSE", "PT": "PRT",
    "PW": "PLW", "PY": "PRY", "QA": "QAT", "RE": "REU", "RO": "ROU",
    "RS": "SRB", "RU": "RUS", "RW": "RWA", "SA": "SAU", "SB": "SLB",
    "SC": "SYC", "SD": "SDN", "SS": "SSD", "SE": "SWE", "SG": "SGP",
    "SH": "SHN", "SI": "SVN", "SJ": "SJM", "SK": "SVK", "SL": "SLE",
    "SM": "SMR", "SN": "SEN", "SO": "SOM", "SR": "SUR", "ST": "STP",
    "SV": "SLV", "SX": "SXM", "SY": "SYR", "SZ": "SWZ", "TC": "TCA",
    "TD": "TCD", "TF": "ATF", "TG": "TGO", "TH": "THA", "TJ": "TJK",
    "TK": "TKL", "TL": "TLS", "TM": "TKM", "TN": "TUN", "TO": "TON",
    "TR": "TUR", "TT": "TTO", "TV": "TUV", "TW": "TWN", "TZ": "TZA",
    "UA": "UKR", "UG": "UGA", "UM": "UMI", "US": "USA", "UY": "URY",
    "UZ": "UZB", "VA": "VAT", "VC": "VCT", "VE": "VEN", "VG": "VGB",
    "VI": "VIR", "VN": "VNM", "VU": "VUT", "WF": "WLF", "WS": "WSM",
    "YE": "YEM", "YT": "MYT", "ZA": "ZAF", "ZM": "ZMB", "ZW": "ZWE",
    "CS": "SCG", "AN": "ANT"
}

histoire = [
    ["2017", [
        [857592, 1483228800, "January"],
        [887318, 1485907200, "February"],
        [914458, 1488326400, "March"],
        [943927, 1491001200, "April"],
        [972533, 1493593200, "May"],
        [1002091, 1496271600, "June"],
        [1030662, 1498863600, "July"]]],
    ["2016", [
        [548109, 1451606400, "January"],
        [574656, 1454284800, "February"],
        [598337, 1456790400, "March"],
        [627886, 1459465200, "April"],
        [656038, 1462057200, "May"],
        [684601, 1464735600, "June"],
        [712756, 1467327600, "July"],
        [738802, 1470006000, "August"],
        [766526, 1472684400, "September"],
        [788058, 1475276400, "October"],
        [805610, 1477958400, "November"],
        [826911, 1480550400, "December"]]],
    ["2015", [
        [199132, 1420070400, "January"],
        [228610, 1422748800, "February"],
        [255283, 1425168000, "March"],
        [285083, 1427842800, "April"],
        [313769, 1430434800, "May"],
        [346655, 1433113200, "June"],
        [374768, 1435705200, "July"],
        [404292, 1438383600, "August"],
        [433630, 1441062000, "September"],
        [462243, 1443654000, "October"],
        [491689, 1446336000, "November"],
        [520318, 1448928000, "December"]]],
    ["2014", [
        [0, 1398898800, "May"],
        [2890, 1401577200, "June"],
        [25812, 1404169200, "July"],
        [55140, 1406847600, "August"],
        [84334, 1409526000, "September"],
        [111240, 1412118000, "October"],
        [140974, 1414800000, "November"],
        [169598, 1417392000, "December"]]],
]

genesisblockhash = "00000766be5a4bb74c040b85a98d2ba2b433c5f4c673912b3331ea6f18d61bea"

genesistxhash = "bae3867d5e5d35c321adaf9610b9e4147a855f9ad319fdcf70913083d783753f"

novastats = [
    {"volume": 0.00256479, "ticker": "2017-02-04T13:28:48Z", "average": 0.00000103, "high": 0.00000105, "low": 0.00000100, "close": 0.00000100, "open": "0.00000105"},
    {"volume": 0.00965537, "ticker": "2017-02-06T05:48:00Z", "average": 0.00000150, "high": 0.00000200, "low": 0.00000100, "close": 0.00000200, "open": "0.00000100"},
    {"volume": 0.00000000, "ticker": "2017-02-07T22:07:12Z", "average": 0.00000200, "high": 0.00000200, "low": 0.00000200, "close": 0.00000200, "open": "0.00000200"},
    {"volume": 0.00000000, "ticker": "2017-02-09T14:26:24Z", "average": 0.00000200, "high": 0.00000200, "low": 0.00000200, "close": 0.00000200, "open": "0.00000200"},
    {"volume": 0.00000000, "ticker": "2017-02-11T06:45:36Z", "average": 0.00000200, "high": 0.00000200, "low": 0.00000200, "close": 0.00000200, "open": "0.00000200"},
    {"volume": 0.00000000, "ticker": "2017-02-12T23:04:48Z", "average": 0.00000200, "high": 0.00000200, "low": 0.00000200, "close": 0.00000200, "open": "0.00000200"},
    {"volume": 0.00000000, "ticker": "2017-02-14T15:24:00Z", "average": 0.00000200, "high": 0.00000200, "low": 0.00000200, "close": 0.00000200, "open": "0.00000200"},
    # {"volume": 0.00000000, "ticker": "2017-02-16T07:43:12Z", "average": 0.00000200, "high": 0.00000200, "low": 0.00000200, "close": 0.00000200, "open": "0.00000200"},
    {"volume": 0.00490000, "ticker": "2017-02-16T07:43:12Z", "average": 0.00001633, "high": 0.00003500, "low": 0.00000400, "close": 0.00000400, "open": "0.00000200"},
    {"volume": 0.00000000, "ticker": "2017-02-18T00:02:24Z", "average": 0.00000400, "high": 0.00000400, "low": 0.00000400, "close": 0.00000400, "open": "0.00000400"},
    {"volume": 0.00000000, "ticker": "2017-02-19T16:21:36Z", "average": 0.00000400, "high": 0.00000400, "low": 0.00000400, "close": 0.00000400, "open": "0.00000400"},
    {"volume": 0.00000000, "ticker": "2017-02-21T08:40:48Z", "average": 0.00000400, "high": 0.00000400, "low": 0.00000400, "close": 0.00000400, "open": "0.00000400"},
    {"volume": 0.00000000, "ticker": "2017-02-23T01:00:00Z", "average": 0.00000400, "high": 0.00000400, "low": 0.00000400, "close": 0.00000400, "open": "0.00000400"},
    # {"volume": 0.00000000, "ticker": "2017-02-24T17:19:12Z", "average": 0.00000400, "high": 0.00000400, "low": 0.00000400, "close": 0.00000400, "open": "0.00000400"},
    {"volume": 0.00040000, "ticker": "2017-02-24T17:19:12Z", "average": 0.00000200, "high": 0.00000200, "low": 0.00000200, "close": 0.00000200, "open": "0.00000400"},
    {"volume": 0.00039920, "ticker": "2017-02-26T09:38:24Z", "average": 0.00000100, "high": 0.00000100, "low": 0.00000100, "close": 0.00000100, "open": "0.00000200"},
    {"volume": 0.00000000, "ticker": "2017-02-28T01:57:36Z", "average": 0.00000100, "high": 0.00000100, "low": 0.00000100, "close": 0.00000100, "open": "0.00000100"},
    {"volume": 0.00000000, "ticker": "2017-03-01T18:16:48Z", "average": 0.00000100, "high": 0.00000100, "low": 0.00000100, "close": 0.00000100, "open": "0.00000100"},
    # {"volume": 0.00000000, "ticker": "2017-03-03T10:36:00Z", "average": 0.00000100, "high": 0.00000100, "low": 0.00000100, "close": 0.00000100, "open": "0.00000100"},
    {"volume": 0.00016485, "ticker": "2017-03-03T10:36:00Z", "average": 0.00000025, "high": 0.00000025, "low": 0.00000025, "close": 0.00000025, "open": "0.00000100"},
    {"volume": 0.00000000, "ticker": "2017-03-05T02:55:12Z", "average": 0.00000025, "high": 0.00000025, "low": 0.00000025, "close": 0.00000025, "open": "0.00000025"},
    {"volume": 0.00000000, "ticker": "2017-03-06T19:14:24Z", "average": 0.00000025, "high": 0.00000025, "low": 0.00000025, "close": 0.00000025, "open": "0.00000025"},
    {"volume": 0.00000000, "ticker": "2017-03-08T11:33:36Z", "average": 0.00000025, "high": 0.00000025, "low": 0.00000025, "close": 0.00000025, "open": "0.00000025"},
    {"volume": 0.00000000, "ticker": "2017-03-10T03:52:48Z", "average": 0.00000025, "high": 0.00000025, "low": 0.00000025, "close": 0.00000025, "open": "0.00000025"},
    {"volume": 0.00000000, "ticker": "2017-03-11T20:12:00Z", "average": 0.00000025, "high": 0.00000025, "low": 0.00000025, "close": 0.00000025, "open": "0.00000025"},
    # {"volume": 0.00000000, "ticker": "2017-03-13T12:31:12Z", "average": 0.00000025, "high": 0.00000025, "low": 0.00000025, "close": 0.00000025, "open": "0.00000025"},
    {"volume": 0.11010000, "ticker": "2017-03-13T12:31:12Z", "average": 0.00000200, "high": 0.00000200, "low": 0.00000200, "close": 0.00000200, "open": "0.00000025"},
    {"volume": 0.01143616, "ticker": "2017-03-15T04:50:24Z", "average": 0.00000034, "high": 0.00000043, "low": 0.00000023, "close": 0.00000043, "open": "0.00000200"},
    {"volume": 0.00019000, "ticker": "2017-03-16T21:09:36Z", "average": 0.00000190, "high": 0.00000190, "low": 0.00000190, "close": 0.00000190, "open": "0.00000043"},
    {"volume": 0.00000000, "ticker": "2017-03-18T13:28:48Z", "average": 0.00000190, "high": 0.00000190, "low": 0.00000190, "close": 0.00000190, "open": "0.00000190"},
    # {"volume": 0.00000000, "ticker": "2017-03-20T05:48:00Z", "average": 0.00000190, "high": 0.00000190, "low": 0.00000190, "close": 0.00000190, "open": "0.00000190"},
    {"volume": 0.00011482, "ticker": "2017-03-20T05:48:00Z", "average": 0.00000026, "high": 0.00000026, "low": 0.00000026, "close": 0.00000026, "open": "0.00000190"},
    {"volume": 0.00000000, "ticker": "2017-03-21T22:07:12Z", "average": 0.00000026, "high": 0.00000026, "low": 0.00000026, "close": 0.00000026, "open": "0.00000026"},
    {"volume": 0.00000000, "ticker": "2017-03-23T14:26:24Z", "average": 0.00000026, "high": 0.00000026, "low": 0.00000026, "close": 0.00000026, "open": "0.00000026"},
    {"volume": 0.00000000, "ticker": "2017-03-25T06:45:36Z", "average": 0.00000026, "high": 0.00000026, "low": 0.00000026, "close": 0.00000026, "open": "0.00000026"},
    # {"volume": 0.00000000, "ticker": "2017-03-27T00:04:48Z", "average": 0.00000026, "high": 0.00000026, "low": 0.00000026, "close": 0.00000026, "open": "0.00000026"},
    {"volume": 0.00046500, "ticker": "2017-03-27T00:04:48Z", "average": 0.00000031, "high": 0.00000031, "low": 0.00000031, "close": 0.00000031, "open": "0.00000026"},
    {"volume": 0.00000000, "ticker": "2017-03-28T16:24:00Z", "average": 0.00000031, "high": 0.00000031, "low": 0.00000031, "close": 0.00000031, "open": "0.00000031"},
    {"volume": 0.00000000, "ticker": "2017-03-30T08:43:12Z", "average": 0.00000031, "high": 0.00000031, "low": 0.00000031, "close": 0.00000031, "open": "0.00000031"},
    # {"volume": 0.00000000, "ticker": "2017-04-01T01:02:24Z", "average": 0.00000031, "high": 0.00000031, "low": 0.00000031, "close": 0.00000031, "open": "0.00000031"},
    {"volume": 0.00920163, "ticker": "2017-04-01T01:02:24Z", "average": 0.00000040, "high": 0.00000040, "low": 0.00000039, "close": 0.00000039, "open": "0.00000031"},
    {"volume": 0.02113994, "ticker": "2017-04-02T17:21:36Z", "average": 0.00000040, "high": 0.00000045, "low": 0.00000032, "close": 0.00000032, "open": "0.00000039"},
    {"volume": 0.00000000, "ticker": "2017-04-04T09:40:48Z", "average": 0.00000032, "high": 0.00000032, "low": 0.00000032, "close": 0.00000032, "open": "0.00000032"},
    # {"volume": 0.00000000, "ticker": "2017-04-06T02:00:00Z", "average": 0.00000032, "high": 0.00000032, "low": 0.00000032, "close": 0.00000032, "open": "0.00000032"},
    {"volume": 0.12590596, "ticker": "2017-04-06T02:00:00Z", "average": 0.00000037, "high": 0.00000043, "low": 0.00000032, "close": 0.00000032, "open": "0.00000032"},
    {"volume": 0.00000000, "ticker": "2017-04-07T18:19:12Z", "average": 0.00000032, "high": 0.00000032, "low": 0.00000032, "close": 0.00000032, "open": "0.00000032"},
    {"volume": 0.00000000, "ticker": "2017-04-09T10:38:24Z", "average": 0.00000032, "high": 0.00000032, "low": 0.00000032, "close": 0.00000032, "open": "0.00000032"},
    {"volume": 0.00000000, "ticker": "2017-04-11T02:57:36Z", "average": 0.00000032, "high": 0.00000032, "low": 0.00000032, "close": 0.00000032, "open": "0.00000032"},
    # {"volume": 0.00000000, "ticker": "2017-04-12T19:16:48Z", "average": 0.00000032, "high": 0.00000032, "low": 0.00000032, "close": 0.00000032, "open": "0.00000032"},
    {"volume": 0.00014700, "ticker": "2017-04-12T19:16:48Z", "average": 0.00000098, "high": 0.00000098, "low": 0.00000098, "close": 0.00000098, "open": "0.00000032"},
    {"volume": 0.05236731, "ticker": "2017-04-14T11:36:00Z", "average": 0.00000118, "high": 0.00000170, "low": 0.00000055, "close": 0.00000169, "open": "0.00000098"},
    {"volume": 0.00000000, "ticker": "2017-04-16T03:55:12Z", "average": 0.00000169, "high": 0.00000169, "low": 0.00000169, "close": 0.00000169, "open": "0.00000169"},
    # {"volume": 0.00000000, "ticker": "2017-04-17T20:14:24Z", "average": 0.00000169, "high": 0.00000169, "low": 0.00000169, "close": 0.00000169, "open": "0.00000169"},
    {"volume": 0.09335010, "ticker": "2017-04-17T20:14:24Z", "average": 0.00000043, "high": 0.00000057, "low": 0.00000031, "close": 0.00000031, "open": "0.00000169"},
    {"volume": 0.07535555, "ticker": "2017-04-19T12:33:36Z", "average": 0.00000073, "high": 0.00000091, "low": 0.00000038, "close": 0.00000038, "open": "0.00000031"},
    {"volume": 0.00000000, "ticker": "2017-04-21T04:52:48Z", "average": 0.00000038, "high": 0.00000038, "low": 0.00000038, "close": 0.00000038, "open": "0.00000038"},
    # {"volume": 0.00000000, "ticker": "2017-04-22T21:12:00Z", "average": 0.00000038, "high": 0.00000038, "low": 0.00000038, "close": 0.00000038, "open": "0.00000038"},
    {"volume": 0.11343003, "ticker": "2017-04-22T21:12:00Z", "average": 0.00000042, "high": 0.00000050, "low": 0.00000028, "close": 0.00000028, "open": "0.00000038"},
    {"volume": 0.00060146, "ticker": "2017-04-24T13:31:12Z", "average": 0.00000026, "high": 0.00000028, "low": 0.00000025, "close": 0.00000028, "open": "0.00000028"},
    {"volume": 0.13472956, "ticker": "2017-04-26T05:50:24Z", "average": 0.00000046, "high": 0.00000060, "low": 0.00000017, "close": 0.00000060, "open": "0.00000028"},
    {"volume": 0.01327236, "ticker": "2017-04-27T22:09:36Z", "average": 0.00000067, "high": 0.00000079, "low": 0.00000036, "close": 0.00000036, "open": "0.00000060"},
    {"volume": 0.00118550, "ticker": "2017-04-29T14:28:48Z", "average": 0.00000036, "high": 0.00000036, "low": 0.00000036, "close": 0.00000036, "open": "0.00000036"},
    {"volume": 0.00555326, "ticker": "2017-05-01T06:48:00Z", "average": 0.00000036, "high": 0.00000040, "low": 0.00000031, "close": 0.00000040, "open": "0.00000036"},
    {"volume": 0.00108564, "ticker": "2017-05-02T23:07:12Z", "average": 0.00000025, "high": 0.00000025, "low": 0.00000025, "close": 0.00000025, "open": "0.00000040"},
    {"volume": 0.00000000, "ticker": "2017-05-04T15:26:24Z", "average": 0.00000025, "high": 0.00000025, "low": 0.00000025, "close": 0.00000025, "open": "0.00000025"},
    # {"volume": 0.00000000, "ticker": "2017-05-06T07:45:36Z", "average": 0.00000025, "high": 0.00000025, "low": 0.00000025, "close": 0.00000025, "open": "0.00000025"},
    {"volume": 0.09441002, "ticker": "2017-05-06T07:45:36Z", "average": 0.00000020, "high": 0.00000025, "low": 0.00000015, "close": 0.00000015, "open": "0.00000025"},
    {"volume": 0.04293573, "ticker": "2017-05-08T00:04:48Z", "average": 0.00000047, "high": 0.00000067, "low": 0.00000015, "close": 0.00000022, "open": "0.00000015"},
    {"volume": 0.01826408, "ticker": "2017-05-09T16:24:00Z", "average": 0.00000040, "high": 0.00000051, "low": 0.00000030, "close": 0.00000037, "open": "0.00000022"},
    {"volume": 0.01446677, "ticker": "2017-05-11T08:43:12Z", "average": 0.00000045, "high": 0.00000053, "low": 0.00000023, "close": 0.00000023, "open": "0.00000037"},
    {"volume": 0.00000000, "ticker": "2017-05-13T01:02:24Z", "average": 0.00000023, "high": 0.00000023, "low": 0.00000023, "close": 0.00000023, "open": "0.00000023"},
    {"volume": 0.00000000, "ticker": "2017-05-14T17:21:36Z", "average": 0.00000023, "high": 0.00000023, "low": 0.00000023, "close": 0.00000023, "open": "0.00000023"},
    {"volume": 0.00000000, "ticker": "2017-05-16T09:40:48Z", "average": 0.00000023, "high": 0.00000023, "low": 0.00000023, "close": 0.00000023, "open": "0.00000023"},
    # {"volume": 0.00000000, "ticker": "2017-05-18T02:00:00Z", "average": 0.00000023, "high": 0.00000023, "low": 0.00000023, "close": 0.00000023, "open": "0.00000023"},
    {"volume": 0.01028960, "ticker": "2017-05-18T02:00:00Z", "average": 0.00000049, "high": 0.00000051, "low": 0.00000048, "close": 0.00000051, "open": "0.00000023"},
    {"volume": 0.03020394, "ticker": "2017-05-19T18:19:12Z", "average": 0.00000064, "high": 0.00000075, "low": 0.00000051, "close": 0.00000075, "open": "0.00000051"},
    {"volume": 0.10672037, "ticker": "2017-05-21T10:38:24Z", "average": 0.00000152, "high": 0.00000320, "low": 0.00000033, "close": 0.00000105, "open": "0.00000075"},
    {"volume": 0.01562038, "ticker": "2017-05-23T02:57:36Z", "average": 0.00000190, "high": 0.00000190, "low": 0.00000190, "close": 0.00000190, "open": "0.00000105"},
    {"volume": 0.00870000, "ticker": "2017-05-24T19:16:48Z", "average": 0.00000190, "high": 0.00000190, "low": 0.00000190, "close": 0.00000190, "open": "0.00000190"},
    {"volume": 0.19582810, "ticker": "2017-05-26T11:36:00Z", "average": 0.00000272, "high": 0.00000325, "low": 0.00000185, "close": 0.00000325, "open": "0.00000190"},
    {"volume": 0.00099262, "ticker": "2017-05-28T03:55:12Z", "average": 0.00000176, "high": 0.00000325, "low": 0.00000101, "close": 0.00000325, "open": "0.00000325"},
    {"volume": 0.00000000, "ticker": "2017-05-29T20:14:24Z", "average": 0.00000325, "high": 0.00000325, "low": 0.00000325, "close": 0.00000325, "open": "0.00000325"},
    # {"volume": 0.00000000, "ticker": "2017-05-31T12:33:36Z", "average": 0.00000325, "high": 0.00000325, "low": 0.00000325, "close": 0.00000325, "open": "0.00000325"},
    {"volume": 0.00534585, "ticker": "2017-05-31T12:33:36Z", "average": 0.00000210, "high": 0.00000270, "low": 0.00000150, "close": 0.00000270, "open": "0.00000325"},
    {"volume": 0.09079665, "ticker": "2017-06-02T04:52:48Z", "average": 0.00000309, "high": 0.00000370, "low": 0.00000203, "close": 0.00000370, "open": "0.00000270"},
    {"volume": 0.05349001, "ticker": "2017-06-03T21:12:00Z", "average": 0.00000221, "high": 0.00000250, "low": 0.00000162, "close": 0.00000250, "open": "0.00000370"},
    {"volume": 0.45023631, "ticker": "2017-06-05T13:31:12Z", "average": 0.00000431, "high": 0.00000590, "low": 0.00000250, "close": 0.00000303, "open": "0.00000250"},
    {"volume": 0.01690141, "ticker": "2017-06-07T05:50:24Z", "average": 0.00000313, "high": 0.00000330, "low": 0.00000304, "close": 0.00000330, "open": "0.00000303"},
    {"volume": 0.06658296, "ticker": "2017-06-08T22:09:36Z", "average": 0.00000378, "high": 0.00000600, "low": 0.00000330, "close": 0.00000335, "open": "0.00000330"},
    {"volume": 0.04174335, "ticker": "2017-06-10T14:28:48Z", "average": 0.00000375, "high": 0.00000560, "low": 0.00000338, "close": 0.00000338, "open": "0.00000335"},
    {"volume": 0.04331340, "ticker": "2017-06-12T06:48:00Z", "average": 0.00000351, "high": 0.00000351, "low": 0.00000351, "close": 0.00000351, "open": "0.00000338"},
    {"volume": 1.94555858, "ticker": "2017-06-13T23:07:12Z", "average": 0.00000289, "high": 0.00000351, "low": 0.00000126, "close": 0.00000126, "open": "0.00000351"},
    {"volume": 0.00049638, "ticker": "2017-06-15T15:26:24Z", "average": 0.00000136, "high": 0.00000136, "low": 0.00000136, "close": 0.00000136, "open": "0.00000126"},
    {"volume": 0.00000000, "ticker": "2017-06-17T07:45:36Z", "average": 0.00000136, "high": 0.00000136, "low": 0.00000136, "close": 0.00000136, "open": "0.00000136"},
    {"volume": 0.00000000, "ticker": "2017-06-19T00:04:48Z", "average": 0.00000136, "high": 0.00000136, "low": 0.00000136, "close": 0.00000136, "open": "0.00000136"},
    # {"volume": 0.00000000, "ticker": "2017-06-20T16:24:00Z", "average": 0.00000136, "high": 0.00000136, "low": 0.00000136, "close": 0.00000136, "open": "0.00000136"},
    {"volume": 0.15330018, "ticker": "2017-06-20T16:24:00Z", "average": 0.00000136, "high": 0.00000139, "low": 0.00000128, "close": 0.00000137, "open": "0.00000136"},
    {"volume": 0.00780000, "ticker": "2017-06-22T08:43:12Z", "average": 0.00000130, "high": 0.00000130, "low": 0.00000130, "close": 0.00000130, "open": "0.00000137"},
    {"volume": 0.04647609, "ticker": "2017-06-24T01:02:24Z", "average": 0.00000203, "high": 0.00000224, "low": 0.00000171, "close": 0.00000224, "open": "0.00000130"},
    {"volume": 0.00000000, "ticker": "2017-06-25T17:21:36Z", "average": 0.00000224, "high": 0.00000224, "low": 0.00000224, "close": 0.00000224, "open": "0.00000224"},
    # {"volume": 0.00000000, "ticker": "2017-06-27T09:40:48Z", "average": 0.00000224, "high": 0.00000224, "low": 0.00000224, "close": 0.00000224, "open": "0.00000224"},
    {"volume": 0.00045082, "ticker": "2017-06-27T09:40:48Z", "average": 0.00000155, "high": 0.00000170, "low": 0.00000135, "close": 0.00000160, "open": "0.00000224"},
    {"volume": 0.00892351, "ticker": "2017-06-29T02:00:00Z", "average": 0.00000156, "high": 0.00000164, "low": 0.00000131, "close": 0.00000164, "open": "0.00000160"},
    {"volume": 0.05146913, "ticker": "2017-06-30T18:19:12Z", "average": 0.00000128, "high": 0.00000131, "low": 0.00000126, "close": 0.00000127, "open": "0.00000164"},
    {"volume": 0.00000000, "ticker": "2017-07-02T10:38:24Z", "average": 0.00000127, "high": 0.00000127, "low": 0.00000127, "close": 0.00000127, "open": "0.00000127"},
    {"volume": 0.00000000, "ticker": "2017-07-04T02:57:36Z", "average": 0.00000127, "high": 0.00000127, "low": 0.00000127, "close": 0.00000127, "open": "0.00000127"},
    # {"volume": 0.00000000, "ticker": "2017-07-05T19:16:48Z", "average": 0.00000127, "high": 0.00000127, "low": 0.00000127, "close": 0.00000127, "open": "0.00000127"},
    {"volume": 0.00026526, "ticker": "2017-07-05T19:16:48Z", "average": 0.00000161, "high": 0.00000161, "low": 0.00000160, "close": 0.00000160, "open": "0.00000127"},
    {"volume": 0.00093828, "ticker": "2017-07-07T11:36:00Z", "average": 0.00000120, "high": 0.00000160, "low": 0.00000080, "close": 0.00000080, "open": "0.00000160"},
    {"volume": 0.33649673, "ticker": "2017-07-09T03:55:12Z", "average": 0.00000265, "high": 0.00000460, "low": 0.00000151, "close": 0.00000349, "open": "0.00000080"},
    {"volume": 0.95661295, "ticker": "2017-07-10T20:14:24Z", "average": 0.00000503, "high": 0.00000650, "low": 0.00000252, "close": 0.00000420, "open": "0.00000349"},
    {"volume": 0.18954295, "ticker": "2017-07-12T12:33:36Z", "average": 0.00000567, "high": 0.00000660, "low": 0.00000423, "close": 0.00000500, "open": "0.00000420"},
    {"volume": 0.35588265, "ticker": "2017-07-14T04:52:48Z", "average": 0.00000463, "high": 0.00000650, "low": 0.00000050, "close": 0.00000440, "open": "0.00000500"},
    {"volume": 1.93548011, "ticker": "2017-07-15T21:12:00Z", "average": 0.00000552, "high": 0.00000800, "low": 0.00000332, "close": 0.00000527, "open": "0.00000440"},
    {"volume": 0.19884672, "ticker": "2017-07-17T13:31:12Z", "average": 0.00000638, "high": 0.00000850, "low": 0.00000555, "close": 0.00000595, "open": "0.00000527"},
    {"volume": 0.05864639, "ticker": "2017-07-19T05:50:24Z", "average": 0.00000507, "high": 0.00000594, "low": 0.00000432, "close": 0.00000432, "open": "0.00000595"},
    {"volume": 1.00110309, "ticker": "2017-07-20T22:09:36Z", "average": 0.00000655, "high": 0.00000799, "low": 0.00000432, "close": 0.00000432, "open": "0.00000432"},
    {"volume": 0.00000000, "ticker": "2017-07-22T14:28:48Z", "average": 0.00000432, "high": 0.00000432, "low": 0.00000432, "close": 0.00000432, "open": "0.00000432"}
]

novaheights = [
    [1486214752, 890793, "2017-02-04T13:28:48Z"],
    [1486360069, 892478, "2017-02-06T05:48:00Z"],
    [1486505201, 894240, "2017-02-07T22:07:12Z"],
    [1486650265, 895836, "2017-02-09T14:26:24Z"],
    [1486795389, 897573, "2017-02-11T06:45:36Z"],
    [1486940583, 899229, "2017-02-12T23:04:48Z"],
    [1487085701, 900774, "2017-02-14T15:24:00Z"],
    [1487230827, 902392, "2017-02-16T07:43:12Z"],
    [1487376127, 904055, "2017-02-18T00:02:24Z"],
    [1487521050, 905647, "2017-02-19T16:21:36Z"],
    [1487666299, 907174, "2017-02-21T08:40:48Z"],
    [1487811571, 908712, "2017-02-23T01:00:00Z"],
    [1487956743, 910342, "2017-02-24T17:19:12Z"],
    [1488101876, 912092, "2017-02-26T09:38:24Z"],
    [1488246958, 913675, "2017-02-28T01:57:36Z"],
    [1488392026, 915088, "2017-03-01T18:16:48Z"],
    [1488537352, 916678, "2017-03-03T10:36:00Z"],
    [1488682497, 918231, "2017-03-05T02:55:12Z"],
    [1488827591, 919838, "2017-03-06T19:14:24Z"],
    [1488972743, 921361, "2017-03-08T11:33:36Z"],
    [1489117843, 923163, "2017-03-10T03:52:48Z"],
    [1489263009, 924838, "2017-03-11T20:12:00Z"],
    [1489408177, 926253, "2017-03-13T12:31:12Z"],
    [1489553324, 927862, "2017-03-15T04:50:24Z"],
    [1489698461, 929712, "2017-03-16T21:09:36Z"],
    [1489843529, 931168, "2017-03-18T13:28:48Z"],
    [1489988876, 932862, "2017-03-20T05:48:00Z"],
    [1490134018, 934455, "2017-03-21T22:07:12Z"],
    [1490279068, 935875, "2017-03-23T14:26:24Z"],
    [1490424115, 937470, "2017-03-25T06:45:36Z"],
    [1490569140, 939192, "2017-03-27T00:04:48Z"],
    [1490714518, 940929, "2017-03-28T16:24:00Z"],
    [1490859723, 942299, "2017-03-30T08:43:12Z"],
    [1491004870, 943958, "2017-04-01T01:02:24Z"],
    [1491150091, 945542, "2017-04-02T17:21:36Z"],
    [1491295226, 947150, "2017-04-04T09:40:48Z"],
    [1491440263, 948903, "2017-04-06T02:00:00Z"],
    [1491585264, 950563, "2017-04-07T18:19:12Z"],
    [1491730693, 952099, "2017-04-09T10:38:24Z"],
    [1491875844, 953666, "2017-04-11T02:57:36Z"],
    [1492020917, 955342, "2017-04-12T19:16:48Z"],
    [1492166146, 956888, "2017-04-14T11:36:00Z"],
    [1492311020, 958502, "2017-04-16T03:55:12Z"],
    [1492456455, 960065, "2017-04-17T20:14:24Z"],
    [1492601084, 961703, "2017-04-19T12:33:36Z"],
    [1492746711, 963287, "2017-04-21T04:52:48Z"],
    [1492891915, 964868, "2017-04-22T21:12:00Z"],
    [1493036652, 966474, "2017-04-24T13:31:12Z"],
    [1493182222, 968073, "2017-04-26T05:50:24Z"],
    [1493327307, 969657, "2017-04-27T22:09:36Z"],
    [1493472457, 971278, "2017-04-29T14:28:48Z"],
    [1493617670, 972846, "2017-05-01T06:48:00Z"],
    [1493762817, 974417, "2017-05-02T23:07:12Z"],
    [1493907821, 976033, "2017-05-04T15:26:24Z"],
    [1494053121, 977630, "2017-05-06T07:45:36Z"],
    [1494198281, 979243, "2017-05-08T00:04:48Z"],
    [1494343408, 980802, "2017-05-09T16:24:00Z"],
    [1494488512, 982424, "2017-05-11T08:43:12Z"],
    [1494633644, 983948, "2017-05-13T01:02:24Z"],
    [1494778849, 985539, "2017-05-14T17:21:36Z"],
    [1494924044, 987206, "2017-05-16T09:40:48Z"],
    [1495069169, 988685, "2017-05-18T02:00:00Z"],
    [1495214042, 990347, "2017-05-19T18:19:12Z"],
    [1495359479, 991942, "2017-05-21T10:38:24Z"],
    [1495504631, 993715, "2017-05-23T02:57:36Z"],
    [1495649629, 995228, "2017-05-24T19:16:48Z"],
    [1495794917, 996853, "2017-05-26T11:36:00Z"],
    [1495940105, 998453, "2017-05-28T03:55:12Z"],
    [1496085247, 1000088, "2017-05-29T20:14:24Z"],
    [1496230321, 1001686, "2017-05-31T12:33:36Z"],
    [1496375564, 1003311, "2017-06-02T04:52:48Z"],
    [1496520668, 1005009, "2017-06-03T21:12:00Z"],
    [1496665838, 1006628, "2017-06-05T13:31:12Z"],
    [1496810940, 1008208, "2017-06-07T05:50:24Z"],
    [1496956137, 1009827, "2017-06-08T22:09:36Z"],
    [1497101119, 1011392, "2017-06-10T14:28:48Z"],
    [1497246447, 1013025, "2017-06-12T06:48:00Z"],
    [1497391589, 1014585, "2017-06-13T23:07:12Z"],
    [1497536694, 1016239, "2017-06-15T15:26:24Z"],
    [1497681915, 1017702, "2017-06-17T07:45:36Z"],
    [1497827034, 1019329, "2017-06-19T00:04:48Z"],
    [1497972027, 1020916, "2017-06-20T16:24:00Z"],
    [1498117366, 1022504, "2017-06-22T08:43:12Z"],
    [1498262458, 1024039, "2017-06-24T01:02:24Z"],
    [1498407681, 1025651, "2017-06-25T17:21:36Z"],
    [1498552793, 1027236, "2017-06-27T09:40:48Z"],
    [1498697959, 1028867, "2017-06-29T02:00:00Z"],
    [1498843074, 1030438, "2017-06-30T18:19:12Z"],
    [1498988232, 1032081, "2017-07-02T10:38:24Z"],
    [1499133401, 1033682, "2017-07-04T02:57:36Z"],
    [1499278577, 1035271, "2017-07-05T19:16:48Z"],
    [1499423660, 1036895, "2017-07-07T11:36:00Z"],
    [1499568810, 1038411, "2017-07-09T03:55:12Z"],
    [1499713940, 1040061, "2017-07-10T20:14:24Z"],
    [1499858634, 1041657, "2017-07-12T12:33:36Z"],
    [1500004356, 1043294, "2017-07-14T04:52:48Z"],
    [1500149516, 1044909, "2017-07-15T21:12:00Z"],
    [1500234709, 1045858, "2017-07-17T13:31:12Z"],
    [1500439824, 1048123, "2017-07-19T05:50:24Z"],
    [1500584976, 1049764, "2017-07-20T22:09:36Z"],
    [1500730128, 1051346, "2017-07-22T14:28:48Z"],
]

novadata = [
    {'low': 1e-06, 'average': 1.03e-06, 'high': 1.05e-06, 'ticker': '2017-02-04T13:28:48Z', 'volume': 0.00256479, 'open': 0.00000105, 'block': 890793, 'close': 1e-06, 'timestamp': 1486214752},
    {'low': 1e-06, 'average': 1.5e-06, 'high': 2e-06, 'ticker': '2017-02-06T05:48:00Z', 'volume': 0.00965537, 'open': 0.00000100, 'block': 892478, 'close': 2e-06, 'timestamp': 1486360069},
    {'low': 2e-06, 'average': 2e-06, 'high': 2e-06, 'ticker': '2017-02-07T22:07:12Z', 'volume': 0.0, 'open': 0.00000200, 'block': 894240, 'close': 2e-06, 'timestamp': 1486505201},
    {'low': 2e-06, 'average': 2e-06, 'high': 2e-06, 'ticker': '2017-02-09T14:26:24Z', 'volume': 0.0, 'open': 0.00000200, 'block': 895836, 'close': 2e-06, 'timestamp': 1486650265},
    {'low': 2e-06, 'average': 2e-06, 'high': 2e-06, 'ticker': '2017-02-11T06:45:36Z', 'volume': 0.0, 'open': 0.00000200, 'block': 897573, 'close': 2e-06, 'timestamp': 1486795389},
    {'low': 2e-06, 'average': 2e-06, 'high': 2e-06, 'ticker': '2017-02-12T23:04:48Z', 'volume': 0.0, 'open': 0.00000200, 'block': 899229, 'close': 2e-06, 'timestamp': 1486940583},
    {'low': 2e-06, 'average': 2e-06, 'high': 2e-06, 'ticker': '2017-02-14T15:24:00Z', 'volume': 0.0, 'open': 0.00000200, 'block': 900774, 'close': 2e-06, 'timestamp': 1487085701},
    {'low': 4e-06, 'average': 1.633e-05, 'high': 3.5e-05, 'ticker': '2017-02-16T07:43:12Z', 'volume': 0.0049, 'open': 0.00000200, 'block': 902392, 'close': 4e-06, 'timestamp': 1487230827},
    {'low': 4e-06, 'average': 4e-06, 'high': 4e-06, 'ticker': '2017-02-18T00:02:24Z', 'volume': 0.0, 'open': 0.00000400, 'block': 904055, 'close': 4e-06, 'timestamp': 1487376127},
    {'low': 4e-06, 'average': 4e-06, 'high': 4e-06, 'ticker': '2017-02-19T16:21:36Z', 'volume': 0.0, 'open': 0.00000400, 'block': 905647, 'close': 4e-06, 'timestamp': 1487521050},
    {'low': 4e-06, 'average': 4e-06, 'high': 4e-06, 'ticker': '2017-02-21T08:40:48Z', 'volume': 0.0, 'open': 0.00000400, 'block': 907174, 'close': 4e-06, 'timestamp': 1487666299},
    {'low': 4e-06, 'average': 4e-06, 'high': 4e-06, 'ticker': '2017-02-23T01:00:00Z', 'volume': 0.0, 'open': 0.00000400, 'block': 908712, 'close': 4e-06, 'timestamp': 1487811571},
    {'low': 2e-06, 'average': 2e-06, 'high': 2e-06, 'ticker': '2017-02-24T17:19:12Z', 'volume': 0.0004, 'open': 0.00000400, 'block': 910342, 'close': 2e-06, 'timestamp': 1487956743},
    {'low': 1e-06, 'average': 1e-06, 'high': 1e-06, 'ticker': '2017-02-26T09:38:24Z', 'volume': 0.0003992, 'open': 0.00000200, 'block': 912092, 'close': 1e-06, 'timestamp': 1488101876},
    {'low': 1e-06, 'average': 1e-06, 'high': 1e-06, 'ticker': '2017-02-28T01:57:36Z', 'volume': 0.0, 'open': 0.00000100, 'block': 913675, 'close': 1e-06, 'timestamp': 1488246958},
    {'low': 1e-06, 'average': 1e-06, 'high': 1e-06, 'ticker': '2017-03-01T18:16:48Z', 'volume': 0.0, 'open': 0.00000100, 'block': 915088, 'close': 1e-06, 'timestamp': 1488392026},
    {'low': 2.5e-07, 'average': 2.5e-07, 'high': 2.5e-07, 'ticker': '2017-03-03T10:36:00Z', 'volume': 0.00016485, 'open': 0.00000100, 'block': 916678, 'close': 2.5e-07, 'timestamp': 1488537352},
    {'low': 2.5e-07, 'average': 2.5e-07, 'high': 2.5e-07, 'ticker': '2017-03-05T02:55:12Z', 'volume': 0.0, 'open': 0.00000025, 'block': 918231, 'close': 2.5e-07, 'timestamp': 1488682497},
    {'low': 2.5e-07, 'average': 2.5e-07, 'high': 2.5e-07, 'ticker': '2017-03-06T19:14:24Z', 'volume': 0.0, 'open': 0.00000025, 'block': 919838, 'close': 2.5e-07, 'timestamp': 1488827591},
    {'low': 2.5e-07, 'average': 2.5e-07, 'high': 2.5e-07, 'ticker': '2017-03-08T11:33:36Z', 'volume': 0.0, 'open': 0.00000025, 'block': 921361, 'close': 2.5e-07, 'timestamp': 1488972743},
    {'low': 2.5e-07, 'average': 2.5e-07, 'high': 2.5e-07, 'ticker': '2017-03-10T03:52:48Z', 'volume': 0.0, 'open': 0.00000025, 'block': 923163, 'close': 2.5e-07, 'timestamp': 1489117843},
    {'low': 2.5e-07, 'average': 2.5e-07, 'high': 2.5e-07, 'ticker': '2017-03-11T20:12:00Z', 'volume': 0.0, 'open': 0.00000025, 'block': 924838, 'close': 2.5e-07, 'timestamp': 1489263009},
    {'low': 2e-06, 'average': 2e-06, 'high': 2e-06, 'ticker': '2017-03-13T12:31:12Z', 'volume': 0.1101, 'open': 0.00000025, 'block': 926253, 'close': 2e-06, 'timestamp': 1489408177},
    {'low': 2.3e-07, 'average': 3.4e-07, 'high': 4.3e-07, 'ticker': '2017-03-15T04:50:24Z', 'volume': 0.01143616, 'open': 0.00000200, 'block': 927862, 'close': 4.3e-07, 'timestamp': 1489553324},
    {'low': 1.9e-06, 'average': 1.9e-06, 'high': 1.9e-06, 'ticker': '2017-03-16T21:09:36Z', 'volume': 0.00019, 'open': 0.00000043, 'block': 929712, 'close': 1.9e-06, 'timestamp': 1489698461},
    {'low': 1.9e-06, 'average': 1.9e-06, 'high': 1.9e-06, 'ticker': '2017-03-18T13:28:48Z', 'volume': 0.0, 'open': 0.00000190, 'block': 931168, 'close': 1.9e-06, 'timestamp': 1489843529},
    {'low': 2.6e-07, 'average': 2.6e-07, 'high': 2.6e-07, 'ticker': '2017-03-20T05:48:00Z', 'volume': 0.00011482, 'open': 0.00000190, 'block': 932862, 'close': 2.6e-07, 'timestamp': 1489988876},
    {'low': 2.6e-07, 'average': 2.6e-07, 'high': 2.6e-07, 'ticker': '2017-03-21T22:07:12Z', 'volume': 0.0, 'open': 0.00000026, 'block': 934455, 'close': 2.6e-07, 'timestamp': 1490134018},
    {'low': 2.6e-07, 'average': 2.6e-07, 'high': 2.6e-07, 'ticker': '2017-03-23T14:26:24Z', 'volume': 0.0, 'open': 0.00000026, 'block': 935875, 'close': 2.6e-07, 'timestamp': 1490279068},
    {'low': 2.6e-07, 'average': 2.6e-07, 'high': 2.6e-07, 'ticker': '2017-03-25T06:45:36Z', 'volume': 0.0, 'open': 0.00000026, 'block': 937470, 'close': 2.6e-07, 'timestamp': 1490424115},
    {'low': 3.1e-07, 'average': 3.1e-07, 'high': 3.1e-07, 'ticker': '2017-03-27T00:04:48Z', 'volume': 0.000465, 'open': 0.00000026, 'block': 939192, 'close': 3.1e-07, 'timestamp': 1490569140},
    {'low': 3.1e-07, 'average': 3.1e-07, 'high': 3.1e-07, 'ticker': '2017-03-28T16:24:00Z', 'volume': 0.0, 'open': 0.00000031, 'block': 940929, 'close': 3.1e-07, 'timestamp': 1490714518},
    {'low': 3.1e-07, 'average': 3.1e-07, 'high': 3.1e-07, 'ticker': '2017-03-30T08:43:12Z', 'volume': 0.0, 'open': 0.00000031, 'block': 942299, 'close': 3.1e-07, 'timestamp': 1490859723},
    {'low': 3.9e-07, 'average': 4e-07, 'high': 4e-07, 'ticker': '2017-04-01T01:02:24Z', 'volume': 0.00920163, 'open': 0.00000031, 'block': 943958, 'close': 3.9e-07, 'timestamp': 1491004870},
    {'low': 3.2e-07, 'average': 4e-07, 'high': 4.5e-07, 'ticker': '2017-04-02T17:21:36Z', 'volume': 0.02113994, 'open': 0.00000039, 'block': 945542, 'close': 3.2e-07, 'timestamp': 1491150091},
    {'low': 3.2e-07, 'average': 3.2e-07, 'high': 3.2e-07, 'ticker': '2017-04-04T09:40:48Z', 'volume': 0.0, 'open': 0.00000032, 'block': 947150, 'close': 3.2e-07, 'timestamp': 1491295226},
    {'low': 3.2e-07, 'average': 3.7e-07, 'high': 4.3e-07, 'ticker': '2017-04-06T02:00:00Z', 'volume': 0.12590596, 'open': 0.00000032, 'block': 948903, 'close': 3.2e-07, 'timestamp': 1491440263},
    {'low': 3.2e-07, 'average': 3.2e-07, 'high': 3.2e-07, 'ticker': '2017-04-07T18:19:12Z', 'volume': 0.0, 'open': 0.00000032, 'block': 950563, 'close': 3.2e-07, 'timestamp': 1491585264},
    {'low': 3.2e-07, 'average': 3.2e-07, 'high': 3.2e-07, 'ticker': '2017-04-09T10:38:24Z', 'volume': 0.0, 'open': 0.00000032, 'block': 952099, 'close': 3.2e-07, 'timestamp': 1491730693},
    {'low': 3.2e-07, 'average': 3.2e-07, 'high': 3.2e-07, 'ticker': '2017-04-11T02:57:36Z', 'volume': 0.0, 'open': 0.00000032, 'block': 953666, 'close': 3.2e-07, 'timestamp': 1491875844},
    {'low': 9.8e-07, 'average': 9.8e-07, 'high': 9.8e-07, 'ticker': '2017-04-12T19:16:48Z', 'volume': 0.000147, 'open': 0.00000032, 'block': 955342, 'close': 9.8e-07, 'timestamp': 1492020917},
    {'low': 5.5e-07, 'average': 1.18e-06, 'high': 1.7e-06, 'ticker': '2017-04-14T11:36:00Z', 'volume': 0.05236731, 'open': 0.00000098, 'block': 956888, 'close': 1.69e-06, 'timestamp': 1492166146},
    {'low': 1.69e-06, 'average': 1.69e-06, 'high': 1.69e-06, 'ticker': '2017-04-16T03:55:12Z', 'volume': 0.0, 'open': 0.00000169, 'block': 958502, 'close': 1.69e-06, 'timestamp': 1492311020},
    {'low': 3.1e-07, 'average': 4.3e-07, 'high': 5.7e-07, 'ticker': '2017-04-17T20:14:24Z', 'volume': 0.0933501, 'open': 0.00000169, 'block': 960065, 'close': 3.1e-07, 'timestamp': 1492456455},
    {'low': 3.8e-07, 'average': 7.3e-07, 'high': 9.1e-07, 'ticker': '2017-04-19T12:33:36Z', 'volume': 0.07535555, 'open': 0.00000031, 'block': 961703, 'close': 3.8e-07, 'timestamp': 1492601084},
    {'low': 3.8e-07, 'average': 3.8e-07, 'high': 3.8e-07, 'ticker': '2017-04-21T04:52:48Z', 'volume': 0.0, 'open': 0.00000038, 'block': 963287, 'close': 3.8e-07, 'timestamp': 1492746711},
    {'low': 2.8e-07, 'average': 4.2e-07, 'high': 5e-07, 'ticker': '2017-04-22T21:12:00Z', 'volume': 0.11343003, 'open': 0.00000038, 'block': 964868, 'close': 2.8e-07, 'timestamp': 1492891915},
    {'low': 2.5e-07, 'average': 2.6e-07, 'high': 2.8e-07, 'ticker': '2017-04-24T13:31:12Z', 'volume': 0.00060146, 'open': 0.00000028, 'block': 966474, 'close': 2.8e-07, 'timestamp': 1493036652},
    {'low': 1.7e-07, 'average': 4.6e-07, 'high': 6e-07, 'ticker': '2017-04-26T05:50:24Z', 'volume': 0.13472956, 'open': 0.00000028, 'block': 968073, 'close': 6e-07, 'timestamp': 1493182222},
    {'low': 3.6e-07, 'average': 6.7e-07, 'high': 7.9e-07, 'ticker': '2017-04-27T22:09:36Z', 'volume': 0.01327236, 'open': 0.00000060, 'block': 969657, 'close': 3.6e-07, 'timestamp': 1493327307},
    {'low': 3.6e-07, 'average': 3.6e-07, 'high': 3.6e-07, 'ticker': '2017-04-29T14:28:48Z', 'volume': 0.0011855, 'open': 0.00000036, 'block': 971278, 'close': 3.6e-07, 'timestamp': 1493472457},
    {'low': 3.1e-07, 'average': 3.6e-07, 'high': 4e-07, 'ticker': '2017-05-01T06:48:00Z', 'volume': 0.00555326, 'open': 0.00000036, 'block': 972846, 'close': 4e-07, 'timestamp': 1493617670},
    {'low': 2.5e-07, 'average': 2.5e-07, 'high': 2.5e-07, 'ticker': '2017-05-02T23:07:12Z', 'volume': 0.00108564, 'open': 0.00000040, 'block': 974417, 'close': 2.5e-07, 'timestamp': 1493762817},
    {'low': 2.5e-07, 'average': 2.5e-07, 'high': 2.5e-07, 'ticker': '2017-05-04T15:26:24Z', 'volume': 0.0, 'open': 0.00000025, 'block': 976033, 'close': 2.5e-07, 'timestamp': 1493907821},
    {'low': 1.5e-07, 'average': 2e-07, 'high': 2.5e-07, 'ticker': '2017-05-06T07:45:36Z', 'volume': 0.09441002, 'open': 0.00000025, 'block': 977630, 'close': 1.5e-07, 'timestamp': 1494053121},
    {'low': 1.5e-07, 'average': 4.7e-07, 'high': 6.7e-07, 'ticker': '2017-05-08T00:04:48Z', 'volume': 0.04293573, 'open': 0.00000015, 'block': 979243, 'close': 2.2e-07, 'timestamp': 1494198281},
    {'low': 3e-07, 'average': 4e-07, 'high': 5.1e-07, 'ticker': '2017-05-09T16:24:00Z', 'volume': 0.01826408, 'open': 0.00000022, 'block': 980802, 'close': 3.7e-07, 'timestamp': 1494343408},
    {'low': 2.3e-07, 'average': 4.5e-07, 'high': 5.3e-07, 'ticker': '2017-05-11T08:43:12Z', 'volume': 0.01446677, 'open': 0.00000037, 'block': 982424, 'close': 2.3e-07, 'timestamp': 1494488512},
    {'low': 2.3e-07, 'average': 2.3e-07, 'high': 2.3e-07, 'ticker': '2017-05-13T01:02:24Z', 'volume': 0.0, 'open': 0.00000023, 'block': 983948, 'close': 2.3e-07, 'timestamp': 1494633644},
    {'low': 2.3e-07, 'average': 2.3e-07, 'high': 2.3e-07, 'ticker': '2017-05-14T17:21:36Z', 'volume': 0.0, 'open': 0.00000023, 'block': 985539, 'close': 2.3e-07, 'timestamp': 1494778849},
    {'low': 2.3e-07, 'average': 2.3e-07, 'high': 2.3e-07, 'ticker': '2017-05-16T09:40:48Z', 'volume': 0.0, 'open': 0.00000023, 'block': 987206, 'close': 2.3e-07, 'timestamp': 1494924044},
    {'low': 4.8e-07, 'average': 4.9e-07, 'high': 5.1e-07, 'ticker': '2017-05-18T02:00:00Z', 'volume': 0.0102896, 'open': 0.00000023, 'block': 988685, 'close': 5.1e-07, 'timestamp': 1495069169},
    {'low': 5.1e-07, 'average': 6.4e-07, 'high': 7.5e-07, 'ticker': '2017-05-19T18:19:12Z', 'volume': 0.03020394, 'open': 0.00000051, 'block': 990347, 'close': 7.5e-07, 'timestamp': 1495214042},
    {'low': 3.3e-07, 'average': 1.52e-06, 'high': 3.2e-06, 'ticker': '2017-05-21T10:38:24Z', 'volume': 0.10672037, 'open': 0.00000075, 'block': 991942, 'close': 1.05e-06, 'timestamp': 1495359479},
    {'low': 1.9e-06, 'average': 1.9e-06, 'high': 1.9e-06, 'ticker': '2017-05-23T02:57:36Z', 'volume': 0.01562038, 'open': 0.00000105, 'block': 993715, 'close': 1.9e-06, 'timestamp': 1495504631},
    {'low': 1.9e-06, 'average': 1.9e-06, 'high': 1.9e-06, 'ticker': '2017-05-24T19:16:48Z', 'volume': 0.0087, 'open': 0.00000190, 'block': 995228, 'close': 1.9e-06, 'timestamp': 1495649629},
    {'low': 1.85e-06, 'average': 2.72e-06, 'high': 3.25e-06, 'ticker': '2017-05-26T11:36:00Z', 'volume': 0.1958281, 'open': 0.00000190, 'block': 996853, 'close': 3.25e-06, 'timestamp': 1495794917},
    {'low': 1.01e-06, 'average': 1.76e-06, 'high': 3.25e-06, 'ticker': '2017-05-28T03:55:12Z', 'volume': 0.00099262, 'open': 0.00000325, 'block': 998453, 'close': 3.25e-06, 'timestamp': 1495940105},
    {'low': 3.25e-06, 'average': 3.25e-06, 'high': 3.25e-06, 'ticker': '2017-05-29T20:14:24Z', 'volume': 0.0, 'open': 0.00000325, 'block': 1000088, 'close': 3.25e-06, 'timestamp': 1496085247},
    {'low': 1.5e-06, 'average': 2.1e-06, 'high': 2.7e-06, 'ticker': '2017-05-31T12:33:36Z', 'volume': 0.00534585, 'open': 0.00000325, 'block': 1001686, 'close': 2.7e-06, 'timestamp': 1496230321},
    {'low': 2.03e-06, 'average': 3.09e-06, 'high': 3.7e-06, 'ticker': '2017-06-02T04:52:48Z', 'volume': 0.09079665, 'open': 0.00000270, 'block': 1003311, 'close': 3.7e-06, 'timestamp': 1496375564},
    {'low': 1.62e-06, 'average': 2.21e-06, 'high': 2.5e-06, 'ticker': '2017-06-03T21:12:00Z', 'volume': 0.05349001, 'open': 0.00000370, 'block': 1005009, 'close': 2.5e-06, 'timestamp': 1496520668},
    {'low': 2.5e-06, 'average': 4.31e-06, 'high': 5.9e-06, 'ticker': '2017-06-05T13:31:12Z', 'volume': 0.45023631, 'open': 0.00000250, 'block': 1006628, 'close': 3.03e-06, 'timestamp': 1496665838},
    {'low': 3.04e-06, 'average': 3.13e-06, 'high': 3.3e-06, 'ticker': '2017-06-07T05:50:24Z', 'volume': 0.01690141, 'open': 0.00000303, 'block': 1008208, 'close': 3.3e-06, 'timestamp': 1496810940},
    {'low': 3.3e-06, 'average': 3.78e-06, 'high': 6e-06, 'ticker': '2017-06-08T22:09:36Z', 'volume': 0.06658296, 'open': 0.00000330, 'block': 1009827, 'close': 3.35e-06, 'timestamp': 1496956137},
    {'low': 3.38e-06, 'average': 3.75e-06, 'high': 5.6e-06, 'ticker': '2017-06-10T14:28:48Z', 'volume': 0.04174335, 'open': 0.00000335, 'block': 1011392, 'close': 3.38e-06, 'timestamp': 1497101119},
    {'low': 3.51e-06, 'average': 3.51e-06, 'high': 3.51e-06, 'ticker': '2017-06-12T06:48:00Z', 'volume': 0.0433134, 'open': 0.00000338, 'block': 1013025, 'close': 3.51e-06, 'timestamp': 1497246447},
    {'low': 1.26e-06, 'average': 2.89e-06, 'high': 3.51e-06, 'ticker': '2017-06-13T23:07:12Z', 'volume': 1.94555858, 'open': 0.00000351, 'block': 1014585, 'close': 1.26e-06, 'timestamp': 1497391589},
    {'low': 1.36e-06, 'average': 1.36e-06, 'high': 1.36e-06, 'ticker': '2017-06-15T15:26:24Z', 'volume': 0.00049638, 'open': 0.00000126, 'block': 1016239, 'close': 1.36e-06, 'timestamp': 1497536694},
    {'low': 1.36e-06, 'average': 1.36e-06, 'high': 1.36e-06, 'ticker': '2017-06-17T07:45:36Z', 'volume': 0.0, 'open': 0.00000136, 'block': 1017702, 'close': 1.36e-06, 'timestamp': 1497681915},
    {'low': 1.36e-06, 'average': 1.36e-06, 'high': 1.36e-06, 'ticker': '2017-06-19T00:04:48Z', 'volume': 0.0, 'open': 0.00000136, 'block': 1019329, 'close': 1.36e-06, 'timestamp': 1497827034},
    {'low': 1.28e-06, 'average': 1.36e-06, 'high': 1.39e-06, 'ticker': '2017-06-20T16:24:00Z', 'volume': 0.15330018, 'open': 0.00000136, 'block': 1020916, 'close': 1.37e-06, 'timestamp': 1497972027},
    {'low': 1.3e-06, 'average': 1.3e-06, 'high': 1.3e-06, 'ticker': '2017-06-22T08:43:12Z', 'volume': 0.0078, 'open': 0.00000137, 'block': 1022504, 'close': 1.3e-06, 'timestamp': 1498117366},
    {'low': 1.71e-06, 'average': 2.03e-06, 'high': 2.24e-06, 'ticker': '2017-06-24T01:02:24Z', 'volume': 0.04647609, 'open': 0.00000130, 'block': 1024039, 'close': 2.24e-06, 'timestamp': 1498262458},
    {'low': 2.24e-06, 'average': 2.24e-06, 'high': 2.24e-06, 'ticker': '2017-06-25T17:21:36Z', 'volume': 0.0, 'open': 0.00000224, 'block': 1025651, 'close': 2.24e-06, 'timestamp': 1498407681},
    {'low': 1.35e-06, 'average': 1.55e-06, 'high': 1.7e-06, 'ticker': '2017-06-27T09:40:48Z', 'volume': 0.00045082, 'open': 0.00000224, 'block': 1027236, 'close': 1.6e-06, 'timestamp': 1498552793},
    {'low': 1.31e-06, 'average': 1.56e-06, 'high': 1.64e-06, 'ticker': '2017-06-29T02:00:00Z', 'volume': 0.00892351, 'open': 0.00000160, 'block': 1028867, 'close': 1.64e-06, 'timestamp': 1498697959},
    {'low': 1.26e-06, 'average': 1.28e-06, 'high': 1.31e-06, 'ticker': '2017-06-30T18:19:12Z', 'volume': 0.05146913, 'open': 0.00000164, 'block': 1030438, 'close': 1.27e-06, 'timestamp': 1498843074},
    {'low': 1.27e-06, 'average': 1.27e-06, 'high': 1.27e-06, 'ticker': '2017-07-02T10:38:24Z', 'volume': 0.0, 'open': 0.00000127, 'block': 1032081, 'close': 1.27e-06, 'timestamp': 1498988232},
    {'low': 1.27e-06, 'average': 1.27e-06, 'high': 1.27e-06, 'ticker': '2017-07-04T02:57:36Z', 'volume': 0.0, 'open': 0.00000127, 'block': 1033682, 'close': 1.27e-06, 'timestamp': 1499133401},
    {'low': 1.6e-06, 'average': 1.61e-06, 'high': 1.61e-06, 'ticker': '2017-07-05T19:16:48Z', 'volume': 0.00026526, 'open': 0.00000127, 'block': 1035271, 'close': 1.6e-06, 'timestamp': 1499278577},
    {'low': 8e-07, 'average': 1.2e-06, 'high': 1.6e-06, 'ticker': '2017-07-07T11:36:00Z', 'volume': 0.00093828, 'open': 0.00000160, 'block': 1036895, 'close': 8e-07, 'timestamp': 1499423660},
    {'low': 1.51e-06, 'average': 2.65e-06, 'high': 4.6e-06, 'ticker': '2017-07-09T03:55:12Z', 'volume': 0.33649673, 'open': 0.00000080, 'block': 1038411, 'close': 3.49e-06, 'timestamp': 1499568810},
    {'low': 2.52e-06, 'average': 5.03e-06, 'high': 6.5e-06, 'ticker': '2017-07-10T20:14:24Z', 'volume': 0.95661295, 'open': 0.00000349, 'block': 1040061, 'close': 4.2e-06, 'timestamp': 1499713940},
    {'low': 4.23e-06, 'average': 5.67e-06, 'high': 6.6e-06, 'ticker': '2017-07-12T12:33:36Z', 'volume': 0.18954295, 'open': 0.00000420, 'block': 1041657, 'close': 5e-06, 'timestamp': 1499858634},
    {'low': 5e-07, 'average': 4.63e-06, 'high': 6.5e-06, 'ticker': '2017-07-14T04:52:48Z', 'volume': 0.35588265, 'open': 0.00000500, 'block': 1043294, 'close': 4.4e-06, 'timestamp': 1500004356},
    {'low': 3.32e-06, 'average': 5.52e-06, 'high': 8e-06, 'ticker': '2017-07-15T21:12:00Z', 'volume': 1.93548011, 'open': 0.00000440, 'block': 1044909, 'close': 5.27e-06, 'timestamp': 1500149516},
    {'low': 5.55e-06, 'average': 6.38e-06, 'high': 8.5e-06, 'ticker': '2017-07-17T13:31:12Z', 'volume': 0.19884672, 'open': 0.00000527, 'block': 1045858, 'close': 5.95e-06, 'timestamp': 1500234709},
    {'low': 4.32e-06, 'average': 5.07e-06, 'high': 5.94e-06, 'ticker': '2017-07-19T05:50:24Z', 'volume': 0.05864639, 'open': 0.00000595, 'block': 1048123, 'close': 4.32e-06, 'timestamp': 1500439824},
    {'low': 4.32e-06, 'average': 6.55e-06, 'high': 7.99e-06, 'ticker': '2017-07-20T22:09:36Z', 'volume': 1.00110309, 'open': 0.00000432, 'block': 1049764, 'close': 4.32e-06, 'timestamp': 1500584976},
    {'low': 4.32e-06, 'average': 4.32e-06, 'high': 4.32e-06, 'ticker': '2017-07-22T14:28:48Z', 'volume': 0.0, 'open': 0.00000432, 'block': 1051346, 'close': 4.32e-06, 'timestamp': 1500730128}
]
