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

# Adapt to each blockchain, see test_populate_menu_selection
histoire = [
    ["2017", [
        # [857592, 1483228800, "January"],
    ]],
    ["2016", []],
    ["2015", []],
    ["2014", []],
]

genesisblockhash = ""

genesistxhash = ""

novastats = []

novaheights = []

novadata = []
