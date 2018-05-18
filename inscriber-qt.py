#!/usr/bin/env python3

"""
Inscriber-qt (GUI with PyQt5).
Testnet invocation: Start it with 'testnet' as an argument.

License: MIT, credits: The Slimcoin Developers
"""

from blocknotifybase import RPCHost, mainnet, testnet
import inscriber as i
import sys
from PyQt5.QtWidgets import QWidget, QToolTip, QPushButton, QGridLayout, QLineEdit, QLabel, QComboBox, QScrollArea, QApplication
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt


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


class MainWindow(QWidget):
    
    def __init__(self):
        super().__init__()   
        self.insc = Inscriber()
        self.grid = QGridLayout()
        self.initUI()



    def initUI(self):
        
        addr_lbl = QLabel('Address')
        insc_lbl = QLabel('Inscription') 

        addr_cb = QComboBox()
        addresslist = self.insc.get_addresslist()
        self.insc.set_address(addresslist[0]) # default: first address
        addr_cb.addItems(addresslist)
        addr_cb.activated[str].connect(self.insc.set_address)
        insc_edit = QLineEdit()
        insc_edit.textChanged[str].connect(self.insc.set_inscription)

        cont_btn = QPushButton('Continue', self)
        cont_btn.resize(cont_btn.sizeHint())

        QToolTip.setFont(QFont('SansSerif', 10))
        cont_btn.setToolTip('<b>Create transaction</b> (will still not broadcast it)')
        cont_btn.clicked.connect(self.showTX)

        self.grid.setSpacing(10)
        self.grid.addWidget(addr_lbl, 1, 0)
        self.grid.addWidget(addr_cb, 1, 1, 1, 2)
        self.grid.addWidget(insc_lbl, 2, 0)
        self.grid.addWidget(insc_edit, 2, 1, 1, 2)
        self.grid.addWidget(cont_btn, 3, 1)

        self.setLayout(self.grid)
        self.setGeometry(300, 300, 400, 300)
        self.setWindowTitle('The Slimweb Inscriber - Inscribe data on the blockchain')   
        self.show()

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
        sign_btn.resize(sign_btn.sizeHint())
        sign_btn.clicked.connect(self.sendTX)

        finish_btn = QPushButton('Quit', self)
        finish_btn.resize(finish_btn.sizeHint())
        finish_btn.clicked.connect(QApplication.instance().quit)


        self.grid.addWidget(rawtx_infolabel, 4, 0)
        self.grid.addWidget(rawtx_scrollarea, 4, 1, 1, 2)
        self.grid.addWidget(dectx_infolabel, 5, 0)
        self.grid.addWidget(dectx_scrollarea, 5, 1, 1, 2)
        self.grid.addWidget(sign_btn, 6, 1)
        self.grid.addWidget(finish_btn, 6, 2)

    def sendTX(self):
        self.insc.sign_tx()
        self.insc.send_tx()
        send_label = QLabel("Transaction has been sent! Your text was inscribed in the blockchain.\nPress Quit button to exit.")
        self.grid.addWidget(send_label, 7, 0, 1, 3)


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())
