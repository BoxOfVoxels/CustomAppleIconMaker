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
        
    def bicon(self):
        fp = io.BytesIO()
        self.icon.save(fp, format="png")
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

class Window(QMainWindow):
    def __init__(self, BuildInfo):
        super().__init__()
        self.buildInfo = BuildInfo
        self.setWindowTitle("")
        self.initUI()
        
    def initUI(self):
        cwidget = QWidget()
        clayout = QVBoxLayout()
        self.setCentralWidget(cwidget)
        cwidget.setLayout(clayout)
        
        btnlayout = QHBoxLayout()
        btnlayout.addStretch(1)
        iosbtn = QPushButton("Make iOS Icons", self)
        iosbtn.clicked.connect(self.iOS)
        btnlayout.addWidget(iosbtn)
        macosbtn = QPushButton("Make macOS Icons", self)
        macosbtn.clicked.connect(self.macOS)
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
        self.show()
        
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
    
    def iOS(self):
        iOS(self.buildInfo)
        
    def macOS(self):
        macOS(self.buildInfo)
    
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
            app.icon.save(buildInfo.client+"/"+app.name+".png")
    
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
    app = QApplication(sys.argv)
    
    window = Window(BuildInfo(sys.argv[1]))
    
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()
