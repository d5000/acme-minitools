#!/usr/bin/env python3

"""
Inscriber-qt (GUI with PyQt5).
Testnet invocation: Start it with 'testnet' as an argument.

License: MIT, credits: The Slimcoin Developers

Roadmap:
- 0.2: Save publishing addresses and give them a name. Change to standalone (integrate blocknotifybase objects). 
- 0.3: Add more storage options (server, Siacoin?)
- 0.4: Markdown support, theming support, image converting to base24
- 0.5: first proof-of-concept with Solid integration: "Decentralized Instagram". Trusted URIs?
"""


from blocknotifybase import RPCHost, mainnet, testnet
from hashlib import sha1
from functools import reduce
import inscriber as i
import sys, subprocess
from PyQt5.QtWidgets import QWidget, QAction, QToolTip, QPushButton, QGridLayout, QLineEdit, QTextEdit, QFileDialog, QLabel, QComboBox, QScrollArea, QApplication
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt

GATEWAY_URL = "https://d5000.github.io/web2web/gateway.html"
INFODICT_ORDER = ("length", "name", "piece length", "pieces", "private") # this is the order WebTorrent seems to use
# the following will be replaced by dynamic generation in 0.2+
# order: "d" + ANNOUNCE + ANNOUNCE_LIST + COMMENT + CREATED_BY + CREATION_DATE + INFO_HEADER + info_dict + URL_LIST + "e"
ANNOUNCE = b"8:announce23:udp://explodie.org:6969"
ANNOUNCE_LIST = b"13:announce-listll23:udp://explodie.org:6969el34:udp://tracker.coppersurfer.tk:6969el40:udp://tracker.leechers-paradise.org:6969el35:udp://tracker.openbittorrent.com:80el33:udp://tracker.opentrackr.org:1337el21:udp://zer0day.ch:1337el26:wss://tracker.btorrent.xyzel25:wss://tracker.fastcast.nzel32:wss://tracker.openwebtorrent.comee"
COMMENT = b"7:comment24:Created by Slimcoin Team"
CREATED_BY = b"10:created by15:WebTorrent/0098"
CREATION_DATE = b"13:creation datei1527557849e"
INFO_HEADER = b"4:info"
URL_LIST = b"8:url-listl39:http://185.121.25.146/slimcoinblog.htmle"



class Inscriber(object):
    def __init__(self):

        i.maxcharacters = 72 # smalldata format  
        i.quiet = True
        i.raw = False

        if "testnet" in sys.argv:
            self.network = testnet
        else:
            self.network = mainnet

        self.host = RPCHost('http://{}:{}@localhost:{}/'.format(self.network.get("rpcuser"), self.network.get("rpcpass"), self.network.get("rpcport")))


    def get_addresslist(self):
        
        balances = i.get_balances(self.host)
        addresslist = list(balances.keys())
        return addresslist

    def set_address(self, address):
        self.address = address
        print("Setting address: " + self.address)

    def set_inscription(self, inscription):
        self.inscription = inscription
        print("Setting inscription: " + self.inscription)

    def create_tx(self):
        self.rawtx = i.create_opreturn_tx(self.host, self.address, self.inscription)
        self.rawtx_decoded = self.host.call("decoderawtransaction", self.rawtx)

    def sign_tx(self):
        self.signedtx = self.host.call("signrawtransaction", self.rawtx)

    def send_tx(self):
        self.host.call("sendrawtransaction", self.signedtx["hex"])

class TorrentCreator(object):

    def setTorrentData(self, data, filename):
        self.infodict = self.create_infodict(data, filename)
        self.bencoded_infodict = self.bencode_dict(self.infodict, INFODICT_ORDER)
        self.infohash = sha1(self.bencoded_infodict).hexdigest()
        self.magnetlink = "magnet:?xt=urn:btih:" + self.infohash
        self.metainfo = b"d" + ANNOUNCE + ANNOUNCE_LIST + COMMENT + CREATED_BY + CREATION_DATE + INFO_HEADER + self.bencoded_infodict + URL_LIST + b"e" # this becomes the torrent file
        # self.metainfo = b"d" + ANNOUNCE + INFO_HEADER + self.bencoded_infodict + b"e" # minimal torrent for bugfixing

    def util_collapse(self, data):
        """ Given an homogenous list, returns the items of that list
        concatenated together. """

        return reduce(lambda x, y: x + y, data)

    def util_slice(self, string, n):
        return [string[i:i+n] for i in range(0, len(string), n)]


    def create_infodict(self, contents_raw, fname):

        piece_length = 16384 # originally 524288, but 16384 is used in the example torrent files created by WebTorrent.

        info = {}

        contents = contents_raw.encode("utf-8")
        info["piece length"] = piece_length
        info["length"] = len(contents)
        info["name"] = bytes(fname, "ascii")
        info["private"] = 0
        # info["md5sum"] = md5(contents).hexdigest() # probably not needed

        # Generate the pieces
        pieces = self.util_slice(contents, piece_length)
        pieces = [ sha1(p).digest() for p in pieces ]
        info["pieces"] = self.util_collapse(pieces)
        return info

    def bencode_dict(self, dic, order=None):
        # this could be replaced by a "real" bencode library.
        result = b"d" # start of dict
        item_list = list(dic.keys()) if order is None else order
        for key in item_list:
            len_key = bytes(str(len(key)), "ascii")
            result += len_key + b":" + bytes(key, "ascii")
            if type(dic[key]) == bytes:
                len_value = bytes(str(len(dic[key])), "ascii")
                print(len_value, dic[key])
                result += bytes(len_value) + b":" + dic[key]
                # print(result)
                # time.sleep(20)
            elif type(dic[key]) == int:
                result += b"i" + bytes(str(dic[key]), "ascii") + b"e"
            else:
                pass # lists not implemented, needs recursive parsing, and not needed here.
        result += b"e" # end of dict
        return result
           

class MainWindow(QWidget):
    
    def __init__(self):
        super().__init__()   
        self.insc = Inscriber()
        self.tc = TorrentCreator()
        self.grid = QGridLayout()
        self.initUI()



    def initUI(self):
        
        addr_lbl = QLabel('Address')
        fdl_lbl = QLabel('HTML file (optional)')
        insc_lbl = QLabel('Inscription')


        # address selector
        addr_cb = QComboBox()
        addresslist = self.insc.get_addresslist()
        self.insc.set_address(addresslist[0]) # default: first address
        addr_cb.addItems(addresslist)
        addr_cb.activated[str].connect(self.insc.set_address)

        # file chooser (optional)
        self.fdl_flabel = QLabel('<em>No file selected</em>')
        fdl_btn = QPushButton("Open ...")
        fdl_btn.setToolTip('From an HTML File, a Torrent infohash can be created as an inscription.')
        fdl_btn.clicked.connect(self.openFileDialog)

        # inscription
        self.insc_edit = QLineEdit()
        self.insc_edit.textChanged[str].connect(self.insc.set_inscription)

        cont_btn = QPushButton('Continue', self)
        cont_btn.resize(cont_btn.sizeHint())

        QToolTip.setFont(QFont('SansSerif', 10))
        cont_btn.setToolTip('<strong>Create transaction</strong> (will still not broadcast it)')
        cont_btn.clicked.connect(self.showTX)

        self.grid.setSpacing(10)
        self.grid.addWidget(addr_lbl, 1, 0)
        self.grid.addWidget(addr_cb, 1, 1, 1, 2)
        self.grid.addWidget(fdl_lbl, 2, 0)
        self.grid.addWidget(self.fdl_flabel, 2, 1)
        self.grid.addWidget(fdl_btn, 2, 2)
        self.grid.addWidget(insc_lbl, 3, 0)
        self.grid.addWidget(self.insc_edit, 3, 1, 1, 2)
        self.grid.addWidget(cont_btn, 4, 1)

        self.setLayout(self.grid)
        self.setGeometry(300, 300, 400, 300)
        self.setWindowTitle('The Slimweb Inscriber - Inscribe data on the blockchain')
        self.show()

    def openFileDialog(self):

        fname = QFileDialog.getOpenFileName(self, 'Open file')

        if fname[0]:
            f = open(fname[0], 'r')

            with f:
                data = f.read()
                filename = fname[0].split("/")[-1]
                self.tc.setTorrentData(data, filename)
                self.fdl_flabel.setText(fname[0])
                self.insc_edit.setText(self.tc.magnetlink)
                print("Torrent metainfo", self.tc.metainfo)
  

    def showTX(self):
        self.insc.create_tx()
        rawtx_infolabel = QLabel("Raw Transaction (hex):")
        rawtx_scrollarea = QScrollArea()
        rawtx_showlabel = QLabel(self.insc.rawtx)
        rawtx_showlabel.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        rawtx_scrollarea.setWidget(rawtx_showlabel)

        dectx_infolabel = QLabel("Raw Transaction (JSON):")
        dectx_scrollarea = QScrollArea()
        dectx_showlabel = QLabel(str(self.insc.rawtx_decoded))
        dectx_showlabel.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        dectx_scrollarea.setWidget(dectx_showlabel)

        sign_btn = QPushButton('Inscribe!', self)
        sign_btn.setToolTip("This action inscribes your data in the blockchain. <strong>This cannot be undone!</strong>")
        sign_btn.resize(sign_btn.sizeHint())
        sign_btn.clicked.connect(self.sendTX)

        finish_btn = QPushButton('Quit', self)
        finish_btn.setToolTip("Quit the program.")
        finish_btn.resize(finish_btn.sizeHint())
        finish_btn.clicked.connect(QApplication.instance().quit)


        self.grid.addWidget(rawtx_infolabel, 5, 0)
        self.grid.addWidget(rawtx_scrollarea, 5, 1, 1, 2)
        self.grid.addWidget(dectx_infolabel, 6, 0)
        self.grid.addWidget(dectx_scrollarea, 6, 1, 1, 2)
        self.grid.addWidget(sign_btn, 7, 1)
        self.grid.addWidget(finish_btn, 7, 2)


    def sendTX(self):
        self.insc.sign_tx()
        self.insc.send_tx()
        send_lbl = QLabel("Transaction has been sent! Your text was inscribed in the blockchain.\nPress Quit button to exit.")
        save_btn = QPushButton("Save torrent file ...")
        save_btn.setToolTip("You can save the torrent file and share it later with a WebTorrent-compatible client.")
        self.aftersave_lbl = QLabel()
        save_btn.clicked.connect(self.saveTorrentFileDialog)

        self.grid.addWidget(send_lbl, 8, 0, 1, 3)
        self.grid.addWidget(save_btn, 9, 1)
        self.grid.addWidget(self.aftersave_lbl, 10, 1)

    def saveTorrentFileDialog(self):

        fname = QFileDialog.getSaveFileName(self, 'Save torrent file')

        if fname[0]:
            f = open(fname[0], 'wb')

            with f:
                f.write(self.tc.metainfo)
                print("Torrent metainfo file saved in file:", fname[0])
                self.aftersave_lbl.setText("Torrent saved. Share it with WebTorrent and publish your content!")
                webt_btn = QPushButton("Publish your content with WebTorrent!")
                webt_btn.setToolTip("If you have WebTorrent-Desktop installed, you can <strong>share your content now</strong>.")
                self.grid.addWidget(webt_btn, 11, 1)
                self.webt_lbl = QLabel()
                self.webt_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
                self.tc.torrentfilename = fname[0]
                webt_btn.clicked.connect(self.start_webtorrent)
                self.grid.addWidget(self.webt_lbl, 12, 1)


    def start_webtorrent(self):
        try:
            wtd = subprocess.Popen(["webtorrent-desktop", self.tc.torrentfilename])
        except Exception as e:
            print(e)
            sys.exit()

        self.webt_lbl.setText('You just published your content!<br />Now you can go to <a href="{}">the Slimweb Gateway</a> and test it.<br />Insert your publisher address there: <strong>{}</strong>'.format(GATEWAY_URL, self.insc.address))



if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())
