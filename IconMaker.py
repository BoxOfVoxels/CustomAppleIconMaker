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

testicon = img.open("Inputs/exampleicon.png")

class RawApp():
    def __init__(self):
        self.icon = None
        self.name = None
        self.urlscheme = None
        self.pos = None
        self.exsists = False
    
    def setall(self, name, url, pos, icon):
        self.name = name
        self.urlscheme = url
        self.pos = pos
        self.icon = icon
    
    def writeover(self, over):
        if over.urlscheme != "":
            self.urlscheme = over.urlscheme
        self.icon = over.icon

class SaveInfo():
    def __init__(self, inputs, package, exs):
        self.exsistingapps = []
        self.newapps = []
        self.name = package
        self.exsists = exs
        if exs:
            data = json.load(open(package+"/appdata.json", "r"))
            self.iconsheet = img.open(package+"/iconsheet.png")
            for keys, entries in data.items():
                newapp = RawApp()
                croppos = (0, entries["pos"]*1024, 1024, (entries["pos"]+1)*1024)
                icon = self.iconsheet.crop(croppos)
                newapp.setall(keys, entries["url"], entries["pos"], icon)
                self.exsistingapps.append(newapp)
        for icons in inputs:
            newapp = RawApp()
            newapp.icon = icons
            self.newapps.append(newapp)
            


class ApplicationEditorWindow(QMainWindow):
    def __init__(self, SaveInfo):
        super().__init__()
        self.setWindowTitle("Icon Meta Data")
        self.SaveInfo = SaveInfo
        self.app = 0
        self.initUI()
        
    def initUI(self):
        cwidget = QWidget()
        clayout = QFormLayout()
        cwidget.setLayout(clayout)
        self.setCentralWidget(cwidget)
        
        namelayout = QHBoxLayout()
        namelayout.addStretch(1)
        namelabel = QLabel("            Name: ")
        namelayout.addWidget(namelabel)
        namebox = QLineEdit()
        namebox.setMinimumSize(200, 30)
        namebox.setPlaceholderText("Snapchat")
        namebox.textChanged[str].connect(self.updateAct)
        namelayout.addWidget(namebox)
        namelayout.addStretch(1)
        clayout.addRow(namelayout)
        
        urllayout = QHBoxLayout()
        urllayout.addStretch(1)
        urllabel = QLabel("URL Scheme: ")
        urllayout.addWidget(urllabel)
        urlbox = QLineEdit()
        urlbox.setMinimumSize(200, 30)
        urlbox.setPlaceholderText("snapchat://")
        urlbox.textChanged[str].connect(self.updateAct)
        urllayout.addWidget(urlbox)
        urllayout.addStretch(1)
        clayout.addRow(urllayout)
        
        imglayout = QHBoxLayout()
        imgbox = QLabel(self)
        pixmap = QPixmap.fromImage(imgtoQt(self.SaveInfo.newapps[self.app].icon))
        imgbox.setPixmap(pixmap)
        imglayout.addWidget(imgbox)
        clayout.addRow(imglayout)
        
        dialayout = QHBoxLayout()
        dialayout.addStretch(1)
        infolabel = QLabel("")
        dialayout.addWidget(infolabel)
        dialayout.addStretch(1)
        clayout.addRow(dialayout)
                      
        btnslayout = QHBoxLayout()
        btnslayout.addStretch(1)
        prevbtn = QPushButton("<", self)
        prevbtn.setMinimumSize(50, 30)
        if self.app == 0:
            prevbtn.setEnabled(False)
        prevbtn.clicked.connect(self.changeSelectionAct)
        self.prev = prevbtn
        btnslayout.addWidget(prevbtn)
        savebtn = QPushButton("Save", self)
        savebtn.setMinimumSize(200, 30)
        savebtn.clicked.connect(self.saveAct)
        btnslayout.addWidget(savebtn)
        nextbtn = QPushButton(">", self)
        nextbtn.setMinimumSize(50, 30)
        if len(self.SaveInfo.newapps) == (self.app + 1):
            nextbtn.setEnabled(False)
        nextbtn.clicked.connect(self.changeSelectionAct)
        self.next = nextbtn
        btnslayout.addWidget(nextbtn)
        btnslayout.addStretch(1)
        clayout.addRow(btnslayout)
        
        self.show()
        self.clayout = clayout
        self.namebox = namebox
        self.urlbox = urlbox
        self.infolabel = infolabel
        self.setFixedSize(self.size())
    
    def changeSelectionAct(self):
        sender = self.sender()
        if sender == self.prev:
            self.app = self.app - 1
        elif sender == self.next:
            self.app = self.app + 1
        else:
            print("failed to ident sender")
            return
        self.initUI()
    
    def updateAct(self):
        app = self.SaveInfo.newapps[self.app]
        sender = self.sender()
        if sender == self.namebox:
            app.name = sender.text()
            for eapps in self.SaveInfo.exsistingapps:
                if eapps.name == app.name:
                    app.exsists = True
                    self.infolabel.setText("\""+app.name+"\" has been found in this theme.")
                    break
                else:
                    app.exsists = False
                    self.infolabel.setText("\""+app.name+"\" has not been added to this theme yet")
        if sender == self.urlbox:
            app.urlscheme = sender.text()
    
    def saveAct(self):
        nextpos = len(self.SaveInfo.exsistingapps)
        savedata = []
        for napps in self.SaveInfo.newapps:
            if napps.exsists:
                for eapps in self.SaveInfo.exsistingapps:
                    if napps.name == eapps.name:
                        eapps.writeover(napps)
            else:
                napps.pos = nextpos
                savedata.append(napps)
                nexpos = nextpos + 1
        for eapps in self.SaveInfo.exsistingapps:
            savedata.append(eapps)
        savedict = {}
        for entries in savedata:
            savedict[entries.name] = {"url": entries.urlscheme, "pos": entries.pos}
        json.dump(savedict, open(self.SaveInfo.name+"/appdata.json", "w"), indent=4)
        saveiconsheet = img.new("RGBA", (1024, len(savedata)*1024))
        for entries in savedata:
            saveicon = entries.icon.resize((1024, 1024))
            saveiconsheet.paste(saveicon, (0, entries.pos*1024))
        saveiconsheet.save(self.SaveInfo.name+"/iconsheet.png")
        
def main():
    #import data
    name = sys.argv[1]
    number = int(sys.argv[2])
    if sys.argv[3] == "True":
        exs = True
    elif sys.argv[3] == "False":
        exs = False
    icons = []
    for i in range(number):
        icon = img.open(name+"/"+str(i)+".png")
        icons.append(icon)
        terminal.call(["rm", "-rf", name+"/"+str(i)+".png"])

    saveInfo = SaveInfo(icons, name, exs)
    
    app = QApplication(sys.argv)
    
    Window = ApplicationEditorWindow(saveInfo)
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()