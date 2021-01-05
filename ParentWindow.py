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
import getpass
img.MAX_IMAGE_PIXELS = 10000000000

class RawApp():
    def __init__(self):
        self.icon = None
        self.name = ""
        self.urlscheme = ""
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
    
    def iosicon(self):
        icon = self.icon
        cropped = icon.crop(icon.getbbox())
        return(cropped)
    
    def bicon(self):
        fp = io.BytesIO()
        self.iosicon.save(fp, format="png")
        return(fp.getvalue())

class BuildInfo():
    def __init__(self, name):
        self.OS = None
        self.packlist = []
        self.applist = []
        self.client = name
        data = json.load(open(name+"/appdata.json", "r"))
        iconsheet = img.open(name+"/iconsheet.png")
        for keys, entries in data.items():
            newapp = RawApp()
            croppos = (0, entries["pos"]*1024, 1024, (entries["pos"]+1)*1024)
            icon = iconsheet.crop(croppos)
            newapp.setall(keys, entries["url"], entries["pos"], icon)
            self.applist.append(newapp)
        self.applist.sort(key=lambda x: x.name)
        
class ThemeInfo():
    def __init__(self, inputs, package, exs):
        self.apps = []
        self.name = package
        self.exsists = exs
        for icons in inputs:
            newapp = RawApp()
            newapp.icon = icons
            newapp.exsists = False
            self.apps.append(newapp)
        if exs:
            data = json.load(open(package+"/appdata.json", "r"))
            self.iconsheet = img.open(package+"/iconsheet.png")
            for keys, entries in data.items():
                newapp = RawApp()
                croppos = (0, entries["pos"]*1024, 1024, (entries["pos"]+1)*1024)
                icon = self.iconsheet.crop(croppos)
                newapp.setall(keys, entries["url"], entries["pos"], icon)
                newapp.exsists = True
                self.apps.append(newapp)
        
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Apple Icon Maker")
        self.setGeometry(300, 100, 400, 600)
        self.launchWin()
    
    def getthemelist(self):
        files = glob.glob("*")
        themes = []
        for theme in files:
            if os.path.isdir(theme):
                themes.append(theme)
        return(themes)
    
    def inputimages(self, layout):
        self.hiddenelements = []
        
        filelayout = QHBoxLayout()
        filelabel = QLabel("No File Selected")
        filelayout.addWidget(filelabel)
        filelayout.addStretch(1)
        filebtn = QPushButton("Choose File", self)
        filebtn.clicked.connect(self.updateEditSettingsAct)
        filelayout.addWidget(filebtn)
        layout.addLayout(filelayout)
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
        layout.addLayout(imgelayout)
        
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
        layout.addLayout(poselayout)
        
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
        layout.addLayout(countlayout)
        
        for items in self.hiddenelements:
            items.hide()
    
    def launchWin(self):
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
        newbtn.clicked.connect(self.inputsNewWin)
        newlayout.addWidget(newbtn)
        newlayout.addStretch(1)
        clayout.addLayout(newlayout)
        
        editlayout = QHBoxLayout()
        editlayout.addStretch(1)
        editbtn = QPushButton("Edit an exsisting theme", self)
        editbtn.setMinimumSize(300, 32)
        editbtn.clicked.connect(self.inputsEditWin)
        editlayout.addWidget(editbtn)
        editlayout.addStretch(1)
        clayout.addLayout(editlayout)
        
        makelayout = QHBoxLayout()
        makelayout.addStretch(1)
        makebtn = QPushButton("Make theme for your Device", self)
        makebtn.setMinimumSize(300, 32)
        makebtn.clicked.connect(self.inputsThemeWin)
        makelayout.addWidget(makebtn)
        makelayout.addStretch(1)
        clayout.addLayout(makelayout)
        
        manlayout = QHBoxLayout()
        manlayout.addStretch(1)
        manbtn = QPushButton("Manage your Themes", self)
        manbtn.setMinimumSize(300, 32)
        manbtn.clicked.connect(self.manageWin)
        manlayout.addWidget(manbtn)
        manlayout.addStretch(1)
        clayout.addLayout(manlayout)
        
        clayout.addStretch(2)
        
        self.show()
        
    def inputsEditWin(self):
        themes = self.getthemelist()
        
        cwidget = QWidget()
        clayout = QVBoxLayout()
        cwidget.setLayout(clayout)
        self.setCentralWidget(cwidget)
        self.iconsheet = None
        
        clayout.addStretch(1)
        
        self.inputimages(clayout)
        
        for theme in themes:
            layout = QHBoxLayout()
            layout.addStretch(1)
            btn = QPushButton(theme, self)
            btn.clicked.connect(self.launchMakerAct)
            layout.addWidget(btn)
            layout.addStretch(1)
            clayout.addLayout(layout)
        
        clayout.addStretch(2)
        
        homelayout = QHBoxLayout()
        homelayout.addStretch(1)
        homebtn = QPushButton("Home", self)
        homebtn.clicked.connect(self.launchWin)
        homelayout.addWidget(homebtn)
        homelayout.addStretch(1)
        clayout.addLayout(homelayout)

        self.setCentralWidget(cwidget)
        
    def inputsThemeWin(self):
        themes = self.getthemelist()
        
        cwidget = QWidget()
        clayout = QVBoxLayout()
        cwidget.setLayout(clayout)
        self.setCentralWidget(cwidget)
        
        clayout.addStretch(1)
        
        menulayout = QHBoxLayout()
        menulayout.addStretch(1)
        menulabel = QLabel("Please Pick one of your Themes")
        menulayout.addWidget(menulabel)
        menulayout.addStretch(1)
        clayout.addLayout(menulayout)
        
        for theme in themes:
            layout = QHBoxLayout()
            layout.addStretch(1)
            btn = QPushButton(theme, self)
            btn.clicked.connect(self.launchSaverAct)
            layout.addWidget(btn)
            layout.addStretch(1)
            clayout.addLayout(layout)
        
        clayout.addStretch(2)
        
        homelayout = QHBoxLayout()
        homelayout.addStretch(1)
        homebtn = QPushButton("Home", self)
        homebtn.clicked.connect(self.launchWin)
        homelayout.addWidget(homebtn)
        homelayout.addStretch(1)
        clayout.addLayout(homelayout)
        
        self.setCentralWidget(cwidget)
    
    def inputsNewWin(self):
        cwidget = QWidget()
        clayout = QVBoxLayout()
        cwidget.setLayout(clayout)
        self.setCentralWidget(cwidget)
        self.iconsheet = None
        
        clayout.addStretch(1)
        
        self.inputimages(clayout)
        
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
        createbtn.clicked.connect(self.launchMakerAct)
        createlayout.addWidget(createbtn)
        createlayout.addStretch(1)
        clayout.addLayout(createlayout)
        
        clayout.addStretch(2)
        
        homelayout = QHBoxLayout()
        homelayout.addStretch(1)
        homebtn = QPushButton("Home", self)
        homebtn.clicked.connect(self.launchWin)
        homelayout.addWidget(homebtn)
        homelayout.addStretch(1)
        clayout.addLayout(homelayout)

        self.setCentralWidget(cwidget)

    def editWin(self):
        app = self.themeInfo.apps[self.app]
        cwidget = QWidget()
        clayout = QFormLayout()
        cwidget.setLayout(clayout)
        
        namelayout = QHBoxLayout()
        namelayout.addStretch(1)
        namelabel = QLabel("            Name: ")
        namelayout.addWidget(namelabel)
        namebox = QLineEdit()
        namebox.setMinimumSize(200, 30)
        namebox.setPlaceholderText("Snapchat")
        namebox.setText(app.name)
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
        urlbox.setText(app.urlscheme)
        urlbox.textChanged[str].connect(self.updateAct)
        urllayout.addWidget(urlbox)
        urllayout.addStretch(1)
        clayout.addRow(urllayout)
        
        imglayout = QHBoxLayout()
        imgbox = QLabel(self)
        png = app.icon.resize((300, 300))
        pixmap = QPixmap.fromImage(imgtoQt(png))
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
        if len(self.themeInfo.apps) == (self.app + 1):
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
        self.updateAct()
        
        self.setCentralWidget(cwidget)
    
    def themeWin(self):
        cwidget = QWidget()
        clayout = QVBoxLayout()
        cwidget.setLayout(clayout)
        
        btnlayout = QHBoxLayout()
        btnlayout.addStretch(1)
        iosbtn = QPushButton("Make iOS Icons", self)
        iosbtn.clicked.connect(self.iOSAct)
        btnlayout.addWidget(iosbtn)
        macosbtn = QPushButton("Make macOS Icons", self)
        macosbtn.clicked.connect(self.macOSAct)
        btnlayout.addWidget(macosbtn)
        btnlayout.addStretch(1)
        clayout.addLayout(btnlayout)
        
        scroll = QScrollArea()
        scrollbox = QGroupBox()
        applistlayout = QVBoxLayout()
        for entries in self.buildInfo.applist:
            layout = QHBoxLayout()
            
            btn = QPushButton(entries.name, self)
            btn.clicked.connect(self.selectAct)
            layout.addWidget(btn)
            
            verticalSpacer = QSpacerItem(0, 100, QSizePolicy.Minimum, QSizePolicy.Expanding)
            layout.addItem(verticalSpacer)
            png = entries.icon
            png = png.resize((100, 100))
            qpng = imgtoQt(png)
            pnglabel = QLabel(self)
            pixmap = QPixmap.fromImage(qpng)
            pnglabel.setPixmap(pixmap)
            layout.addWidget(pnglabel)
            
            applistlayout.addLayout(layout)
        scrollbox.setLayout(applistlayout)
        scroll.setWidget(scrollbox)
        scroll.setFixedHeight(600)
        clayout.addWidget(scroll)

        self.setCentralWidget(cwidget)
        
    def manageWin(self):
        themes = self.getthemelist()
        cwidget = QWidget()
        clayout = QVBoxLayout()
        cwidget.setLayout(clayout)
        
        clayout.addStretch(1)
        
        for theme in themes:
            layout = QHBoxLayout()
            layout.addStretch(1)
            btn = QPushButton(theme, self)
            btn.clicked.connect(self.launchInfoAct)
            layout.addWidget(btn)
            layout.addStretch(1)
            clayout.addLayout(layout)
        
        clayout.addStretch(2)
        
        homelayout = QHBoxLayout()
        homelayout.addStretch(1)
        homebtn = QPushButton("Home", self)
        homebtn.clicked.connect(self.launchWin)
        homelayout.addWidget(homebtn)
        homelayout.addStretch(1)
        clayout.addLayout(homelayout)
        
        self.setCentralWidget(cwidget)
        
    def infoWin(self, datasheet):
        self.datasheet = datasheet
        cwidget = QWidget()
        clayout = QVBoxLayout()
        cwidget.setLayout(clayout)
        clayout.addStretch(1)
        
        lablayout = QHBoxLayout()
        lablayout.addStretch(1)
        label = QLabel("Would you like to Delete " + datasheet + "?")
        lablayout.addWidget(label)
        lablayout.addStretch(1)
        clayout.addLayout(lablayout)
        
        btnslayout = QHBoxLayout()
        btnslayout.addStretch(2)
        nbtn = QPushButton("No", self)
        nbtn.clicked.connect(self.manageWin)
        btnslayout.addWidget(nbtn)
        btnslayout.addStretch(1)
        ybtn = QPushButton("Yes", self)
        ybtn.clicked.connect(self.deleteThemeAct)
        btnslayout.addWidget(ybtn)
        btnslayout.addStretch(2)
        clayout.addLayout(btnslayout)
        
        clayout.addStretch(2)
        self.setCentralWidget(cwidget)
        
        
    def deleteThemeAct(self):
        terminal.call(["rm", "-rf", self.datasheet])
        self.manageWin()
        
    def selectAct(self):
        sender = self.sender()
        for apps in self.buildInfo.applist:
            if apps.name == sender.text():
                app = apps
        if sender.styleSheet() == "background-color: green":
            self.buildInfo.packlist.remove(app)
            sender.setStyleSheet("background-color: ")
        else:
            self.buildInfo.packlist.append(app)
            sender.setStyleSheet("background-color: green")
    
    def iOSAct(self):
        iOS(self.buildInfo)
        self.launchWin()
        
    def macOSAct(self):
        macOS(self.buildInfo)
        self.launchWin()

    def launchInfoAct(self):
        sender = self.sender()
        self.infoWin(sender.text())
        
    def changeSelectionAct(self):
        sender = self.sender()
        if sender == self.prev:
            self.app = self.app - 1
        elif sender == self.next:
            self.app = self.app + 1
        else:
            print("failed to ident sender")
            return
        self.editWin()
    
    def updateAct(self):
        app = self.themeInfo.apps[self.app]
        sender = self.sender()
        if sender == self.namebox:
            if not app.exsists:
                app.name = sender.text()
                for eapps in self.themeInfo.apps:
                    if eapps.name == app.name and eapps.exsists:
                        self.infolabel.setText("\""+app.name+"\" has been found in this theme.")
                        break
                    else:
                        self.infolabel.setText("\""+app.name+"\" is new to this theme")
            else:
                app.name = sender.text()
        if sender == self.urlbox:
            app.urlscheme = sender.text()
    
    def saveAct(self):
        nextpos = 0
        for apps in self.themeInfo.apps:
            if apps.exsists:
                nextpos = nextpos + 1
        savedata = []
        for napps in self.themeInfo.apps:
            if napps.exsists:
                if napps.name != "":
                    savedata.append(napps)
            else:
                writen = False
                for eapps in self.themeInfo.apps:
                    if napps.name == eapps.name and eapps.exsists:
                        print("write over called")
                        eapps.writeover(napps)
                        writen = True
                if not writen:
                    print("not writen")
                    if napps.name != "":
                        print("appsaved")
                        napps.pos = nextpos
                        savedata.append(napps)
                        nextpos = nextpos + 1
                
        savedict = {}
        saveiconsheet = img.new("RGBA", (1024, len(savedata)*1024))
        for entries in savedata:
            savedict[entries.name] = {"url": entries.urlscheme, "pos": entries.pos}
            saveicon = entries.icon.resize((1024, 1024))
            saveiconsheet.paste(saveicon, (0, entries.pos*1024))
        json.dump(savedict, open(self.themeInfo.name+"/appdata.json", "w"), indent=4)
        saveiconsheet.save(self.themeInfo.name+"/iconsheet.png")
        self.launchWin()
        
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
                self.image2.clear()
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
            fileName, _ = QFileDialog.getOpenFileName(self, "Foo", "", "Images (*.png *.jpg *.jpeg)")
            if fileName:
                iconsheetpath = fileName
                self.iconsheet = img.open(iconsheetpath)
                update()
                for items in self.hiddenelements:
                    items.show()
        else:
            update()
        
    def launchMakerAct(self):
        sender = self.sender()
        if sender.text() == "Create Theme":
            if self.name.text() == "":
                self.name.setFocus()
                error = QMessageBox.question(self, "Message", "No Name Found", QMessageBox.Ok, QMessageBox.Ok)
                return

            if os.path.isdir(self.name.text()):
                error = QMessageBox.question(self, "Message", "A Theme with the name "+self.name.text()+" already exsists", QMessageBox.Ok, QMessageBox.Ok)
                return
            
            terminal.call(["mkdir", self.name.text()])
            exsists = False
            name = self.name.text()
        
        else:
            exsists = True
            name = sender.text()
        
        S = self.spinS.value()
        R = self.spinR.value()
        C = self.spinC.value()
        G = self.spinG.value() + S
        
        if self.iconsheet == None:
            R = 0
            C = 0
        
        icons = []
        
        for rows in range(R):
            for coll in range(C):
                croppos = (G*coll, G*rows, (G*coll)+S, (G*rows)+S)
                ipic = self.iconsheet.crop(croppos)
                icons.append(ipic)

        self.themeInfo = ThemeInfo(icons, name, exsists)
        self.app = 0
        self.editWin()
        
        
    def launchSaverAct(self):
        sender = self.sender()
        self.buildInfo = BuildInfo(sender.text())
        self.themeWin()

def iOS(buildInfo):
    def icondict(app, buildInfo):
        #gen plist dict for app
        answer = dict(
            PayloadType = "com.apple.webClip.managed",
            PayloadVersion = 1,
            PayloadIdentifier = "com.boxofvoxels."+buildInfo.client+"-"+app.name,
            PayloadUUID = str(uuid.uuid4()),
            PayloadDisplayName = app.name,
            PayloadDescription = app.name+"Icon",
            PayloadOrganization = "Box Of Voxels iCons",
            URL = app.urlscheme,
            Label = app.name,
            Icon = app.bicon(),
            IsRemovable = True,
            FullScreen = True,
        )
        return(answer)
    #Build iOS icon package
    packedapps = []
    for app in buildInfo.packlist:
        if app.urlscheme != "":
            packedapps.append(icondict(app, buildInfo))
        else:
            app.iosicon().save(buildInfo.client+"/"+app.name+".png")
    
    buildfile = dict(
        PayloadType = "Configuration",
        PayloadVersion = 1,
        PayloadOrganization = "Box Of Voxel iCons",
        PayloadIdentifier = "com.boxofvoxels."+buildInfo.client,
        PayloadUUID = str(uuid.uuid4()),
        PayloadDisplayName = buildInfo.client,
        PayloadDescription = "",
        PayloadRemovalDisallow = False,
        PayloadContent = packedapps,
    )
    
    package = open(buildInfo.client+"/"+buildInfo.client+"iconpackage.mobileconfig", "wb")
    pll.dump(buildfile, package)
    package.close()

def macOS(buildInfo):
    transformkey = [(1024, "512x512@2x"), (512, "512x512"), (512, "256x256@2x"), (256, "256x256"), (256, "128x128@2x"), (128, "128x128"), (64, "32x32@2x"), (32, "32x32"), (32, "16@2x"), (16, "16x16")]
    for app in buildInfo.packlist:
        terminal.call(["mkdir", app.name+".iconset"])
        for size, savename in transformkey:
            scaledicon = app.icon.resize((size, size))
            scaledicon.save(app.name+".iconset/icon_"+savename+".png")
        terminal.call(["iconutil", "-c", "icns", app.name+".iconset"])
        terminal.call(["rm", "-rf", app.name+".iconset"])
        terminal.call(["mv", app.name+".icns", buildInfo.client+"/"])

    
def main():
    os.chdir("/Users/"+str(getpass.getuser())+"/")
    terminal.call(["mkdir", "iConThemes"])
    os.chdir("iConThemes/")
    
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()