#Imports
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PIL.ImageQt import ImageQt as imgtoQt
from PIL import Image as img
import json
import sys
import subprocess as terminal
import os
import plistlib as pll
import uuid
import io
import glob
img.MAX_IMAGE_PIXELS = 10000000000

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Apple Icon Maker")
        self.setGeometry(300, 100, 400, 600)
        self.launchLaunchWin()
        
    def launchLaunchWin(self):
        cwidget = QWidget()
        clayout = QVBoxLayout()
        cwidget.setLayout(clayout)
        self.setCentralWidget(cwidget)
        
        clayout.addStretch(1)
        
        menulayout = QHBoxLayout()
        menulayout.addStretch(1)
        menulabel = QLabel("What would you like to do?")
        menulayout.addWidget(menulabel)
        menulayout.addStretch(1)
        clayout.addLayout(menulayout)
        
        newlayout = QHBoxLayout()
        newlayout.addStretch(1)
        newbtn = QPushButton("Create a New theme", self)
        newbtn.setMinimumSize(300, 32)
        newbtn.clicked.connect(self.launchNewWin)
        newlayout.addWidget(newbtn)
        newlayout.addStretch(1)
        clayout.addLayout(newlayout)
        
        editlayout = QHBoxLayout()
        editlayout.addStretch(1)
        editbtn = QPushButton("Edit an exsisting theme", self)
        editbtn.setMinimumSize(300, 32)
        editbtn.clicked.connect(self.launchEditWin)
        editlayout.addWidget(editbtn)
        editlayout.addStretch(1)
        clayout.addLayout(editlayout)
        
        makelayout = QHBoxLayout()
        makelayout.addStretch(1)
        makebtn = QPushButton("Make theme for your Device", self)
        makebtn.setMinimumSize(300, 32)
        makebtn.clicked.connect(self.launchMakeWin)
        makelayout.addWidget(makebtn)
        makelayout.addStretch(1)
        clayout.addLayout(makelayout)
        
        clayout.addStretch(2)
        
        self.show()
        
    def launchEditWin(self):
        cwidget = QWidget()
        clayout = QVBoxLayout()
        cwidget.setLayout(clayout)
        self.setCentralWidget(cwidget)
        self.hiddenelements = []
        
        clayout.addStretch(1)
        
        filelayout = QHBoxLayout()
        filelabel = QLabel("No File Selected")
        filelayout.addWidget(filelabel)
        filelayout.addStretch(1)
        filebtn = QPushButton("Choose File", self)
        filebtn.clicked.connect(self.updateEditSettingsAct)
        filelayout.addWidget(filebtn)
        clayout.addLayout(filelayout)
        self.filebtn = filebtn
        
        imgelayout = QHBoxLayout()
        imgelayout.addStretch(1)
        imgelabel1 = QLabel()
        imgelayout.addWidget(imgelabel1)
        self.image1 = imgelabel1
        imgelabel2 = QLabel()
        imgelayout.addWidget(imgelabel2)
        self.image2 = imgelabel2
        imgelayout.addStretch(1)
        clayout.addLayout(imgelayout)
        
        poselayout = QHBoxLayout()
        poselabel1 = QLabel("Icon Size (in px)")
        poselayout.addWidget(poselabel1)
        self.hiddenelements.append(poselabel1)
        posespin1 = QSpinBox()
        posespin1.setRange(128, 4096)
        posespin1.valueChanged.connect(self.updateEditSettingsAct)
        self.hiddenelements.append(posespin1)
        self.spinS = posespin1
        poselayout.addWidget(posespin1)
        poselayout.addStretch(1)
        poselabel2 = QLabel("Gap Size (in px)")
        poselayout.addWidget(poselabel2)
        self.hiddenelements.append(poselabel2)
        posespin2 = QSpinBox()
        posespin2.setRange(0, 820)
        posespin2.valueChanged.connect(self.updateEditSettingsAct)
        self.hiddenelements.append(posespin2)
        self.spinG = posespin2
        poselayout.addWidget(posespin2)
        clayout.addLayout(poselayout)
        
        countlayout = QHBoxLayout()
        countlabel1 = QLabel("Colums")
        self.hiddenelements.append(countlabel1)
        countlayout.addWidget(countlabel1)
        countspin1 = QSpinBox()
        countspin1.setRange(1, 1000)
        countspin1.valueChanged.connect(self.updateEditSettingsAct)
        self.hiddenelements.append(countspin1)
        self.spinC = countspin1
        countlayout.addWidget(countspin1)
        countlayout.addStretch(1)
        countlabel2 = QLabel("Rows")
        self.hiddenelements.append(countlabel2)
        countlayout.addWidget(countlabel2)
        countspin2 = QSpinBox()
        countspin2.setRange(1, 1000)
        countspin2.valueChanged.connect(self.updateEditSettingsAct)
        self.hiddenelements.append(countspin2)
        self.spinR = countspin2
        countlayout.addWidget(countspin2)
        clayout.addLayout(countlayout)
        
        namelayout = QHBoxLayout()
        namelayout.addStretch(1)
        namebox = QLineEdit()
        namebox.setMinimumSize(250, 30)
        namebox.setPlaceholderText("Input Theme Name Here")
        self.name = namebox
        namelayout.addWidget(namebox)
        namelayout.addStretch(1)
        clayout.addLayout(namelayout)
        
        createlayout = QHBoxLayout()
        createlayout.addStretch(1)
        createbtn = QPushButton("Edit Theme", self)
        createbtn.clicked.connect(self.launchEditerAct)
        createlayout.addWidget(createbtn)
        createlayout.addStretch(1)
        clayout.addLayout(createlayout)
        
        clayout.addStretch(2)
        
        homelayout = QHBoxLayout()
        homelayout.addStretch(1)
        homebtn = QPushButton("Home", self)
        homebtn.clicked.connect(self.launchLaunchWin)
        homelayout.addWidget(homebtn)
        homelayout.addStretch(1)
        clayout.addLayout(homelayout)
        
        for items in self.hiddenelements:
            items.hide()

        self.setCentralWidget(cwidget)
        
    def launchMakeWin(self):
        print("add Make Later")
    
    def launchNewWin(self):
        cwidget = QWidget()
        clayout = QVBoxLayout()
        cwidget.setLayout(clayout)
        self.setCentralWidget(cwidget)
        self.hiddenelements = []
        
        clayout.addStretch(1)
        
        filelayout = QHBoxLayout()
        filelabel = QLabel("No File Selected")
        filelayout.addWidget(filelabel)
        filelayout.addStretch(1)
        filebtn = QPushButton("Choose File", self)
        filebtn.clicked.connect(self.updateEditSettingsAct)
        filelayout.addWidget(filebtn)
        clayout.addLayout(filelayout)
        self.filebtn = filebtn
        
        imgelayout = QHBoxLayout()
        imgelayout.addStretch(1)
        imgelabel1 = QLabel()
        imgelayout.addWidget(imgelabel1)
        self.image1 = imgelabel1
        imgelabel2 = QLabel()
        imgelayout.addWidget(imgelabel2)
        self.image2 = imgelabel2
        imgelayout.addStretch(1)
        clayout.addLayout(imgelayout)
        
        poselayout = QHBoxLayout()
        poselabel1 = QLabel("Icon Size (in px)")
        poselayout.addWidget(poselabel1)
        posespin1 = QSpinBox()
        posespin1.setRange(128, 4096)
        posespin1.setEnabled(False)
        posespin1.valueChanged.connect(self.updateEditSettingsAct)
        self.spinS = posespin1
        poselayout.addWidget(posespin1)
        poselayout.addStretch(1)
        poselabel2 = QLabel("Gap Size (in px)")
        poselayout.addWidget(poselabel2)
        posespin2 = QSpinBox()
        posespin2.setRange(0, 820)
        posespin2.setEnabled(False)
        posespin2.valueChanged.connect(self.updateEditSettingsAct)
        self.spinG = posespin2
        poselayout.addWidget(posespin2)
        clayout.addLayout(poselayout)
        
        countlayout = QHBoxLayout()
        countlabel1 = QLabel("Colums")
        countlayout.addWidget(countlabel1)
        countspin1 = QSpinBox()
        countspin1.setRange(1, 1000)
        countspin1.setEnabled(False)
        countspin1.valueChanged.connect(self.updateEditSettingsAct)
        self.spinC = countspin1
        countlayout.addWidget(countspin1)
        countlayout.addStretch(1)
        countlabel2 = QLabel("Rows")
        countlayout.addWidget(countlabel2)
        countspin2 = QSpinBox()
        countspin2.setRange(1, 1000)
        countspin2.setEnabled(False)
        countspin2.valueChanged.connect(self.updateEditSettingsAct)
        self.spinR = countspin2
        countlayout.addWidget(countspin2)
        clayout.addLayout(countlayout)
        
        namelayout = QHBoxLayout()
        namelayout.addStretch(1)
        namebox = QLineEdit()
        namebox.setMinimumSize(250, 30)
        namebox.setPlaceholderText("Input Theme Name Here")
        self.name = namebox
        namelayout.addWidget(namebox)
        namelayout.addStretch(1)
        clayout.addLayout(namelayout)
        
        createlayout = QHBoxLayout()
        createlayout.addStretch(1)
        createbtn = QPushButton("Create Theme", self)
        createbtn.clicked.connect(self.launchEditerAct)
        createlayout.addWidget(createbtn)
        createlayout.addStretch(1)
        clayout.addLayout(createlayout)
        
        clayout.addStretch(2)
        
        homelayout = QHBoxLayout()
        homelayout.addStretch(1)
        homebtn = QPushButton("Home", self)
        homebtn.clicked.connect(self.launchLaunchWin)
        homelayout.addWidget(homebtn)
        homelayout.addStretch(1)
        clayout.addLayout(homelayout)

        self.setCentralWidget(cwidget)
    
    def updateEditSettingsAct(self):
        def update():
            S = self.spinS.value()
            R = self.spinR.value() - 1
            C = self.spinC.value() - 1
            G = self.spinG.value() + S
            if R == 0 and C == 0:
                ipic = self.iconsheet.crop ((0, 0, S, S))
                ipic = ipic.resize((100, 100))
                qpic = imgtoQt(ipic)
                pixmap = QPixmap.fromImage(qpic)
                self.image1.setPixmap(pixmap)
            else:
                ipic1 = self.iconsheet.crop ((0, 0, S, S))
                ipic1 = ipic1.resize((100, 100))
                qpic1 = imgtoQt(ipic1)
                pmap1 = QPixmap.fromImage(qpic1)
                self.image1.setPixmap(pmap1)
                
                ipic2 = self.iconsheet.crop((G*C, G*R, (G*C)+S, (G*R)+S))
                ipic2 = ipic2.resize((100, 100))
                qpic2 = imgtoQt(ipic2)
                pmap2 = QPixmap.fromImage(qpic2)
                self.image2.setPixmap(pmap2)
                
        if self.sender() == self.filebtn:
            self.spinC.setEnabled(False)
            self.spinR.setEnabled(False)
            self.spinS.setEnabled(False)
            self.spinG.setEnabled(False)
            fileName, _ = QFileDialog.getOpenFileName(self, "Foo", "", "Images (*.png *.jpg *.jpeg)")
            if fileName:
                iconsheetpath = fileName
                self.iconsheet = img.open(iconsheetpath)
                update()
                self.spinC.setEnabled(True)
                self.spinR.setEnabled(True)
                self.spinS.setEnabled(True)
                self.spinG.setEnabled(True)
                for items in self.hiddenelements:
                    items.show()
        else:
            update()
        
    def launchEditerAct(self):
        sender = self.sender()
        if sender.text() == "Create Theme":
            mode = False
        else:
            mode = True
        if self.name.text() == "":
            self.name.setFocus()
            error = QMessageBox.question(self, "Message", "No Name Found", QMessageBox.Ok, QMessageBox.Ok)
            return
        
        if os.path.isdir(self.name.text()):
            if mode:
                exsists = True
            else:
                error = QMessageBox.question(self, "Message", "A Theme with the name "+self.name.text()+" already exsists", QMessageBox.Ok, QMessageBox.Ok)
                return
        else:
            if mode:
                error = QMessageBox.question(self, "Message", "No Theme found with the name "+self.name.text()+" found", QMessageBox.Ok, QMessageBox.Ok)
                return
            else:
                exsists = False
                terminal.call(["mkdir", self.name.text()])
        print(mode)
        print(exsists)
        
        S = self.spinS.value()
        R = self.spinR.value()
        C = self.spinC.value()
        G = self.spinG.value() + S
        
        icons = []
        bicons = []
        
        if R == 1 and C == 1:
            ipic = self.iconsheet.crop ((0, 0, S, S))
            icons.append(ipic)
        else:
            for rows in range(R):
                for coll in range(C):
                    ipic = self.iconsheet.crop((G*rows, G*coll, (G*rows)+S, (G*coll)+S))
                    icons.append(ipic)
        i = 0
        for entrie in icons:
            entrie.save(self.name.text()+"/"+str(i)+".png")
            i += 1
        terminal.call(["python3", "IconMaker.py", self.name.text(), str(i), str(exsists)])
    
def main():
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()