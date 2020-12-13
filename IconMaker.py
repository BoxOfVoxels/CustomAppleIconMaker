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
        print("Write over Called")
        print(over.urlscheme)
        if over.urlscheme != "":
            self.urlscheme = over.urlscheme
        self.icon = over.icon

class SaveInfo():
    def __init__(self, inputs):
        data = json.load(open("appdata2.json", "r"))
        self.iconsheet = img.open("iconsheet.png")
        self.exsistingapps = []
        self.newapps = []
        for keys, entries in data.items():
            print(keys)
            newapp = RawApp()
            croppos = (0, entries["pos"]*1024, 1024, (entries["pos"]+1)*1024)
            icon = self.iconsheet.crop(croppos)
            newapp.setall(keys, entries["url"], entries["pos"], icon)
            self.exsistingapps.append(newapp)
            print(self.exsistingapps[0].name)
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
        prevbtn.setEnabled(False)
        btnslayout.addWidget(prevbtn)
        savebtn = QPushButton("Save", self)
        savebtn.setMinimumSize(200, 30)
        savebtn.clicked.connect(self.saveAct)
        btnslayout.addWidget(savebtn)
        nextbtn = QPushButton(">", self)
        nextbtn.setMinimumSize(50, 30)
        nextbtn.setEnabled(False)
        btnslayout.addWidget(nextbtn)
        btnslayout.addStretch(1)
        clayout.addRow(btnslayout)
        
        self.show()
        self.clayout = clayout
        self.namebox = namebox
        self.urlbox = urlbox
        self.infolabel = infolabel
        self.setFixedSize(self.size())
        
    def updateAct(self):
        print("updateAct Called\n")
        app = self.SaveInfo.newapps[self.app]
        sender = self.sender()
        if sender == self.namebox:
            app.name = sender.text()
            for eapps in self.SaveInfo.exsistingapps:
                print(eapps.name, app.name)
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
        print("saveAct Called")
        nextpos = len(self.SaveInfo.exsistingapps)
        savedata = []
        for napps in self.SaveInfo.newapps:
            print(napps.name, napps.exsists)
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
        json.dump(savedict, open("appdata2.json", "w"), indent=4)
        saveiconsheet = img.new("RGBA", (1024, len(savedata)*1024))
        for entries in savedata:
            saveicon = entries.icon.resize((1024, 1024))
            saveiconsheet.paste(saveicon, (0, entries.pos*1024))
        saveiconsheet.save("iconsheet.png")
        
def main():
    #temp
    name = sys.argv[1]
    number = int(sys.argv[2])
    icons = []
    for i in range(number):
        icon = img.open(name+"/"+str(i)+".png")
        icons.append(icon)
    #temp
    saveInfo = SaveInfo(icons)
    
    app = QApplication(sys.argv)
    
    Window = ApplicationEditorWindow(saveInfo)
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()