#!/usr/bin/env python3

"""
Slimweb Publishing Wizard
(Simple Wizard-like GUI for Inscriber with PyQt5).
Testnet invocation: Start it with 'testnet' as an argument.

License: MIT, credits: The Slimcoin Developers

Roadmap:
- 0.2: Save publishing addresses and give them a name. Change to standalone (integrate blocknotifybase objects). 
- 0.3: Add more storage options (server, Siacoin?)
- 0.4: Markdown support, theming support, image converting to base24
- 0.5: first proof-of-concept with Solid integration: "Decentralized Instagram". Trusted URIs?


TODO 0.2:
- Set a default location for the load HTML file dialog (WebTorrent standard download dir?)
- Let users select if they want to publish a new website with one of the addresses with balance, select saved labels, or continue with the previously saved website.
"""


from blocknotifybase import RPCHost
from inscriber import Inscriber, HOMEDIR
from hashlib import sha1
from functools import reduce
# import inscriber as i
import sys, subprocess
from PyQt5.QtWidgets import QWidget, QAction, QWizard, QWizardPage, QToolTip, QPushButton, QGridLayout, QVBoxLayout, QLineEdit, QTextEdit, QMessageBox, QDialog, QFileDialog, QLabel, QComboBox, QScrollArea, QTableView, QApplication
from PyQt5.QtGui import QIcon, QFont, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt

GATEWAY_URL = "https://d5000.github.io/web2web/gateway.html"
INFODICT_ORDER = ("length", "name", "piece length", "pieces", "private") # this is the order WebTorrent seems to use
# the following will be replaced by dynamic generation in 0.2+
# order: "d" + ANNOUNCE + ANNOUNCE_LIST + COMMENT + CREATED_BY + CREATION_DATE + INFO_HEADER + info_dict + URL_LIST + "e"
ANNOUNCE = b"8:announce23:udp://explodie.org:6969"
ANNOUNCE_LIST = b"13:announce-listll23:udp://explodie.org:6969el34:udp://tracker.coppersurfer.tk:6969el40:udp://tracker.leechers-paradise.org:6969el35:udp://tracker.openbittorrent.com:80el33:udp://tracker.opentrackr.org:1337el21:udp://zer0day.ch:1337el26:wss://tracker.btorrent.xyzel25:wss://tracker.fastcast.nzel32:wss://tracker.openwebtorrent.comee"
INFO_HEADER = b"4:info"

class TorrentCreator(object):

    def setTorrentData(self, data, filename):
        self.infodict = self.create_infodict(data, filename)
        self.bencoded_infodict = self.bencode_dict(self.infodict, INFODICT_ORDER)
        self.infohash = sha1(self.bencoded_infodict).hexdigest()
        self.magnetlink = "magnet:?xt=urn:btih:" + self.infohash
        self.metainfo = b"d" + ANNOUNCE + ANNOUNCE_LIST + INFO_HEADER + self.bencoded_infodict + b"e" # this becomes the torrent file

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
           

class PubWizard(QWizard):
    def __init__(self):
        super().__init__()
        if "testnet" in sys.argv:
            networktype = "testnet"
        else:
            networktype = "mainnet"
        self.insc = Inscriber(network_type=networktype, quiet=True, raw=False)
        self.tc = TorrentCreator()
        # self.grid = QGridLayout()


        #self.setOption(QWizard.HaveCustomButton1)
        #self.setButtonLayout([QWizard.BackButton, QWizard.NextButton, QWizard.CustomButton1, QWizard.FinishButton, QWizard.CancelButton])
        # global labels
        self.rawtxlabel = QLabel()
        self.dectxlabel = QLabel()
        self.rawtxlabel.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        self.dectxlabel.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        self.rawtxarea = QScrollArea()
        self.dectxarea = QScrollArea()
        self.aftersave_lbl = QLabel()
        self.webt_lbl = QLabel()
        self.webt_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

        # next button checks if torrent file is saved and starts webtorrent
        self.tc.torrentfilename = None
        nextbutton = self.button(QWizard.NextButton)
        nextbutton.clicked.connect(self.start_webtorrent)

    def intropage(self):
        wpi = QWizardPage()
        wpi.setTitle("Create a Slimweb webpage!")
        wpi_lbl = QLabel("This wizard will help you to publish or update a website on the decentralized Slimweb.<br/>"
                          "You need a HTML file, a Slimcoin client, WebTorrent and an Slimcoin address with a"
                          "balance of more than 0.02 SLM.")

        wpi_lbl.setWordWrap(True)
        wpi_layout = QVBoxLayout()
        wpi_layout.addWidget(wpi_lbl)
        wpi.setLayout(wpi_layout)
        return wpi

    def selectaddrpage(self):

        wps = QWizardPage()
        wps.setTitle("Select a Slimcoin address")
        wps_lbl = QLabel("A Slimcoin address is the <b>identifier</b> for your website, like the domain in the WWW.<br />"
                         "You publish all updates on a single website from the same address.")
        wps_lbl.setWordWrap(True)
        addr_lbl = QLabel('Select an address from the list below:')

        # addresslist = self.insc.get_addresslist()
        acd = self.insc.create_addr_combodict()
        # address selector
        addr_cb = QComboBox()
        addr_tv = QTableView()
        addr_model = QStandardItemModel(len(acd), 3)
        addr_model.setHorizontalHeaderLabels(["Address", "Balance", "Label"])
        x = 0
        item_addresses = [] # is item_addresses etc. necessary? Probably not, as the items are only for the GUI view and need not to be accessed afterwards.
        item_balances = []
        item_labels = []
        for address in acd.keys():
           item_addresses.append(QStandardItem(address)) 
           item_balances.append(QStandardItem(str(acd[address]["balance"])))
           item_labels.append(QStandardItem(acd[address]["label"]))
           addr_model.setItem(x, 0, item_addresses[x])
           addr_model.setItem(x, 1, item_balances[x])
           addr_model.setItem(x, 2, item_labels[x])
           x += 1

        print(item_addresses)
        print(acd)

        addr_cb.setView(addr_tv)
        addr_cb.setModel(addr_model)



        self.insc.address = list(acd.keys())[0] # default: first address
        # addr_cb.addItems(addresslist)
        addr_cb.activated[str].connect(self.insc.set_address)

        wps_layout = QVBoxLayout()
        wps_layout.addWidget(wps_lbl)
        wps_layout.addWidget(addr_lbl)
        wps_layout.addWidget(addr_cb)

        wps.setLayout(wps_layout)
        return wps

    def openfilepage(self):

        wpo = QWizardPage()
        wpo.isCommitPage()
        wpo.setTitle("Select HTML file")
        wpo_lbl = QLabel("Select an <b>HTML file</b> containing your website.<br />"
                         "Slimweb websites are meant to be one-pagers, for now - but one-pagers are fashionable, actually ;-).")
        wpo_lbl2 = QLabel("<b>Note:</b> If you want to publish the page with WebTorrent with this wizard, "
                          "it must be saved in the WebTorrent Download folder.")
        wpo_lbl.setWordWrap(True)
        wpo_lbl2.setWordWrap(True)

        insc_lbl = QLabel('<b>Inscription:</b> This is the magnet link appearing in your Slimcoin transaction.')
        self.fdl_flabel = QLabel('<em>No file selected</em>')
        self.insc_edit = QLineEdit()
        self.insc_edit.textChanged[str].connect(self.inscribe)

        fdl_btn = QPushButton("Open HTML File ...")
        fdl_btn.setToolTip('From an HTML File, a Torrent infohash can be created as an inscription.')
        fdl_btn.clicked.connect(self.openFileDialog)

        wpo_layout = QVBoxLayout()
        wpo_layout.addWidget(wpo_lbl)
        wpo_layout.addWidget(wpo_lbl2)
        wpo_layout.addWidget(self.fdl_flabel)
        wpo_layout.addWidget(fdl_btn)
        wpo_layout.addWidget(insc_lbl)
        wpo_layout.addWidget(self.insc_edit)

        wpo.setLayout(wpo_layout)

        return wpo


    def sendpage(self):

        wpe = QWizardPage()

        wpe.setTitle("Inscribe your website!")
        wpe_lbl = QLabel("If you continue, you inscribe your page in the Slimcoin blockchain with"                         
                         " a special transaction. This cannot be undone!<br/>"
                         "You can check the transaction data before (recommended).")
        wpe_lbl2 = QLabel("<b>Note:</b> Every inscription transaction has a mandatory fee of 0.02 SLM.")
        wpe_lbl.setWordWrap(True)
        wpe_lbl2.setWordWrap(True)

        check_button = QPushButton("Check transaction data")
        check_button.clicked.connect(self.checkTXDialog)

        wpe_layout = QVBoxLayout()
        wpe_layout.addWidget(wpe_lbl)
        wpe_layout.addWidget(wpe_lbl2)
        wpe_layout.addWidget(check_button)



        wpe.setLayout(wpe_layout)
        return wpe


    def publishpage(self):
        wpp = QWizardPage()
        wpp.setFinalPage(True)
        #wpp.isCommitPage()
        wpp.setTitle("Publish your page!")
        wpp_lbl = QLabel("You can publish your page now with WebTorrent.<br /> \
                          As long as you seed it, or any of your readers is seeding it, it is available on Slimweb.<br/> \
                          If there are no seeders left, you can seed it again at any time. Simply start WebTorrent.")
        wpp_lbl2 = QLabel("First, save your website as a torrent file, so WebTorrent can access it.")
        wpp_lbl.setWordWrap(True)
        wpp_lbl2.setWordWrap(True)
        save_btn = QPushButton("Save torrent file ...")
        save_btn.setToolTip("You can save the torrent file and share it now or later with a WebTorrent-compatible client.")

        save_btn.clicked.connect(self.saveTorrentFileDialog)



        wpp_layout = QVBoxLayout()
        wpp_layout.addWidget(wpp_lbl)
        wpp_layout.addWidget(wpp_lbl2)
        wpp_layout.addWidget(save_btn)
        wpp_layout.addWidget(self.aftersave_lbl)

        wpp.setLayout(wpp_layout)

        return wpp

    def endpage(self):
        wpx = QWizardPage()
        wpx.setTitle("Your website has been published!")

        wpx_layout = QVBoxLayout()
        wpx_layout.addWidget(self.webt_lbl)

        wpx.setLayout(wpx_layout)
        
        return wpx



    # AUXILIARY METHODS #

    def openFileDialog(self):

        try:
            opendir = self.insc.config["general"]["webtorrent_dir"]
        except KeyError:
            opendir = HOMEDIR

        fname = QFileDialog.getOpenFileName(self, 'Open file', opendir)

        if fname[0]:
            f = open(fname[0], 'r')

            with f:
                data = f.read()
                self.htmlfilename = fname[0].split("/")[-1]
                self.tc.setTorrentData(data, self.htmlfilename)
                self.fdl_flabel.setText(fname[0])
                self.insc_edit.setText(self.tc.magnetlink)
                print("Torrent metainfo", self.tc.metainfo)
                self.inscribe(self.tc.magnetlink) # setText isn't recognized as "textChanged", must be called manually


    def inscribe(self, inscription):
        self.insc.set_inscription(inscription)
        self.insc.create_tx()
        self.rawtxlabel.setText(self.insc.rawtx)
        self.dectxlabel.setText(str(self.insc.rawtx_decoded))
        self.rawtxarea.setWidget(self.rawtxlabel)
        self.dectxarea.setWidget(self.dectxlabel)

    def checkTXDialog(self):
        cdialog = QDialog()
        cd_layout = QVBoxLayout()

        rawtx_infolabel = QLabel("Raw Transaction:")
        dectx_infolabel = QLabel("Decoded Raw Transaction (JSON):")
        ok_button = QPushButton("OK", cdialog)
        ok_button.clicked.connect(cdialog.close)

        cd_layout.addWidget(rawtx_infolabel)
        cd_layout.addWidget(self.rawtxarea)
        cd_layout.addWidget(dectx_infolabel)
        cd_layout.addWidget(self.dectxarea)
        cd_layout.addWidget(ok_button)

        cdialog.setLayout(cd_layout)
        cdialog.setWindowTitle("Check inscription transaction")
        cdialog.setWindowModality(Qt.ApplicationModal)

        cdialog.exec_()


    def saveTorrentFileDialog(self):

        suggested_fname = "".join(self.htmlfilename.split('.')[:-1]) + ".torrent"
        if "general" in self.insc.config.sections() and "webtorrent_dir" in self.insc.config["general"]:
            torrentdir = self.insc.config["general"]["webtorrent_dir"]
        else:
            torrentdir = HOMEDIR # standard home directory as fallback

        fname = QFileDialog.getSaveFileName(self, 'Save torrent file', torrentdir + "/" + suggested_fname, "Torrent files (*.torrent)") # slash should work in Windows, too

        if fname[0]:
            f = open(fname[0], 'wb')

            with f:
                f.write(self.tc.metainfo)
                print("Torrent metainfo file saved in file:", fname[0])
                self.aftersave_lbl.setText("Torrent saved.<br /> Click <b>Next</b> to share it with WebTorrent and publish your content!<br/>Click <b>Finish</b> to share it later.")

                self.tc.torrentfilename = fname[0]
                savedir = "/".join(fname[0].split("/")[:-1])
                print(savedir)
                if "general" not in self.insc.config.sections():
                    self.insc.config.update({"general" : {"webtorrent_dir" : savedir }})
                elif "webtorrent_dir" not in self.insc.config["general"]:
                    self.insc.config["general"].update({"webtorrent_dir" : savedir })
                print("Dictionary", dict(self.insc.config))
                self.insc.write_config()



    def start_webtorrent(self):
        # this is called each time the NextButton is clicked (no way to create a custom button per page?)
        if self.tc.torrentfilename is not None:
            try:
                wtd = subprocess.Popen(["webtorrent-desktop", self.tc.torrentfilename])
            except Exception as e:
                print(e)
                sys.exit()

            self.webt_lbl.setText('You just published your content!<br />Now you can go to <a href="{}">the Slimweb Gateway</a> and test it.<br />Insert your publisher address there: <strong>{}</strong>'.format(GATEWAY_URL, self.insc.address))

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    pw = PubWizard()
    pw.addPage(pw.intropage())
    pw.addPage(pw.selectaddrpage())
    pw.addPage(pw.openfilepage())
    pw.addPage(pw.sendpage())
    pw.addPage(pw.publishpage())
    pw.addPage(pw.endpage())
    pw.setWindowTitle("Slimweb Publication Wizard")
    pw.show()
    # mw = MainWindow()
    sys.exit(app.exec_())
