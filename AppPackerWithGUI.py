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

class BuildInfo():
    def __init__(self):
        self.pngpath = None
        self.client = None
        self.OS = None
        self.packlist = []
        self.iconsheet = None
        dataImport = json.load(open("appdata.json", "r"))
        self.pngkey = dataImport["pngkey"]
        self.urlkey = dataImport["urlkey"]
        self.transformkey = dataImport["transformkey"]
    
    def fetchicon(self, name, otype):
        #find and return icon from pngsheet
        pos = self.pngkey[name]
        croppos = croppos=(pos[1]*1800, pos[0]*1800, (pos[1]*1800)+1500, (pos[0]*1800)+1500)
        icon = self.iconsheet.crop(croppos)
        if otype == "binary":
            fp = io.BytesIO()
            icon.save(fp, format="png")
            return(fp.getvalue())
        elif otype == "png":
            return(icon)
    
    def packableicon(self, name):
        #Check if app has url
        try:
            self.urlkey[name]
            return(True)
        except KeyError:
            return(False)
        

#GUI
class PackerWindow(QMainWindow):
    def __init__(self, buildInfo):
        super().__init__()
        self.buildInfo = buildInfo
        self.setWindowTitle("Apple Icon Maker")
        self.setGeometry(300, 100, 400, 800)
        self.initUI()
        
    def initUI(self):
        QToolTip.setFont(QFont("SansSerif", 10))
        cwidget = QWidget()
        wlayout = QVBoxLayout()
        cwidget.setLayout(wlayout)
        self.setCentralWidget(cwidget)
        self.wlayout = wlayout
        self.createMenuBar()
        self.createSettingsButtons()
        self.show()

    def createMenuBar(self):
        menubar = self.menuBar()
        
        fileMenu = menubar.addMenu("File")
        openAct = QAction("Open", self)
        openAct.triggered.connect(self.openAction)
        fileMenu.addAction(openAct)
        
        editMenu = menubar.addMenu("Edit")
        selectallAct = QAction("Select All", self)
        selectallAct.triggered.connect(self.selectallAction)
        editMenu.addAction(selectallAct)
        deselectallAct = QAction("Deselect All", self)
        deselectallAct.triggered.connect(self.deselectallAction)
        editMenu.addAction(deselectallAct)
    
    def createSettingsButtons(self):
        #Build Top Level Buttons
        setbtnbox = QVBoxLayout()
        gbtn = QPushButton("Make Icon Set", self)
        gbtn.setToolTip("Make Icon Set")
        gbtn.resize(30, 500)
        gbtn.clicked.connect(self.makeiconAction)
        
        osbtnlayout = QHBoxLayout()
        osbtngroup = QButtonGroup(osbtnlayout)
        iosbtn = QRadioButton("iOS")
        iosbtn.clicked.connect(self.toggleOSAction)
        iosbtn.setChecked(True)
        self.buildInfo.OS = "iOS"
        osbtngroup.addButton(iosbtn)
        osbtnlayout.addWidget(iosbtn)
        mosbtn = QRadioButton("macOS")
        mosbtn.clicked.connect(self.toggleOSAction)
        osbtngroup.addButton(mosbtn)
        osbtnlayout.addWidget(mosbtn)
        osbtnlayout.addStretch(1)
        
        pbtn = QPushButton("Select Icon Sheet", self)
        pbtn.setToolTip("This is how you choose your icon set")
        pbtn.resize(30, 500)
        pbtn.clicked.connect(self.openAction)
        
        self.scrollapps = QScrollArea()
        
        setbtnbox.addWidget(gbtn)
        setbtnbox.addLayout(osbtnlayout)
        setbtnbox.addWidget(pbtn)
        setbtnbox.addWidget(self.scrollapps)
        self.wlayout.addLayout(setbtnbox)

    def createAppSelection(self):
        #Build App List
        self.buildInfo.iconsheet = img.open(self.buildInfo.pngpath)
        scrollbox = QGroupBox()
        applislayout = QFormLayout()
        i = 0
        imglis = []
        btnlis = []
        apps = list(self.buildInfo.pngkey.keys())
        apps.sort()
        for entries in apps:
            png = self.buildInfo.fetchicon(entries, "png")
            png = png.resize((100, 100))
            qpng = imgtoQt(png)
            lpng = QLabel(self)
            pixmap = QPixmap.fromImage(qpng)
            lpng.setPixmap(pixmap)
            lpng.resize(100, 100)
            lpng.setToolTip("This is how "+entries+" app will appear")
            imglis.append(lpng)

            btn = QPushButton(entries, self)
            btn.setMinimumSize(200, 30)
            btn.setToolTip("Click here to add "+entries+" to your icon set")
            if entries in self.buildInfo.packlist:
                btn.setStyleSheet("background-color: green")
            else:
                btn.setStyleSheet("background-color: red")
            btn.clicked.connect(self.selectbuttonAction)
            btnlis.append(btn)
            
            applislayout.addRow(imglis[i], btnlis[i])
            i = i+1
        
        self.selectappbtnlis = btnlis
        scrollbox.setLayout(applislayout)
        scroll = self.scrollapps
        scroll.setWidget(scrollbox)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(600)
    
    def selectbuttonAction(self):
        #change selection status
        sender = self.sender()
        if sender.styleSheet() == "background-color: green":
            self.buildInfo.packlist.remove(sender.text())
            sender.setStyleSheet("background-color: red")
        else:
            self.buildInfo.packlist.append(sender.text())
            sender.setStyleSheet("background-color: green")
    
    def makeiconAction(self):
        def starterror(codes):
            errormessage = ""
            for code in codes:
                errormessage = errormessage + "You have not selected a " + code + "\n"

            if errormessage != "":
                errormessage = QMessageBox.question(self, "Message", errormessage, QMessageBox.Ok, QMessageBox.Ok)
        #starts generation
        errorcodes = []
        if self.buildInfo.client == None:
            errorcodes.append("Icon Sheet")
        if self.buildInfo.OS == None:
            errorcodes.append("OS")
        if not errorcodes:
            geniconset(self.buildInfo)
        starterror(errorcodes)
        
        
    def openAction(self):
        #Button Actions
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "All Files (*)")
        if fileName:
            self.buildInfo.pngpath = fileName
            clientName = fileName.split(".")[0]
            clientName = clientName.split("/")[-1]
            self.buildInfo.client = clientName
            self.createAppSelection()
    
    def toggleOSAction(self):
        sender = self.sender()
        if sender.isChecked:
            self.buildInfo.OS = sender.text()
            print(self.buildInfo.OS)
        
    def selectallAction(self):
        self.buildInfo.packlist = []
        for btn in self.selectappbtnlis:
            self.buildInfo.packlist.append(btn.text())
            btn.setStyleSheet("background-color: green")
    
    def deselectallAction(self):
        self.buildInfo.packlist = []
        for btn in self.selectappbtnlis:
            btn.setStyleSheet("background-color: red")
    
    def closeEvent(self, event):
        #Quit dialog box
        reply = QMessageBox.question(self, "Message", "Are you sure you want to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


    
    

def iOS(buildInfo):
    def icondict(name, buildInfo):
        #gen plist dict for app
        answer = dict(
            PayloadType = "com.apple.webClip.managed",
            PayloadVersion = 1,
            PayloadIdentifier = "com.boxofvoxels."+buildInfo.client+"-"+name,
            PayloadUUID = str(uuid.uuid4()),
            PayloadDisplayName = name,
            PayloadDescription = name+"Icon",
            PayloadOrganization = "Box Of Voxels iCons",
            URL = buildInfo.urlkey[name],
            Label = name,
            Icon = buildInfo.fetchicon(name, "binary"),
            IsRemovable = True,
            FullScreen = True,
        )
        return(answer)
    #Build iOS icon package
    packedapps = []

    for name in buildInfo.packlist:
        if buildInfo.packableicon(name):
            packedapps.append(icondict(name, buildInfo))
        else:
            buildInfo.fetchicon(name, "png").save("Outputs/"+name+".png")
    
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
    
    package = open("Outputs/"+buildInfo.client+"iconpackage.mobileconfig", "wb")
    pll.dump(buildfile, package)
    package.close()

def macOS(buildInfo):
    #Generate macOS icns files
    for name in buildInfo.packlist:
        terminal.call(["mkdir", name+".iconset"])
        icon = buildInfo.fetchicon(name, "png")
        for size, savename in buildInfo.transformkey:
            scaledicon = icon.resize((size, size))
            scaledicon.save(name+".iconset/icon_"+savename+".png")
        terminal.call(["iconutil", "-c", "icns", name+".iconset"])
        terminal.call(["rm", "-rf", name+".iconset"])
        terminal.call(["mv", name+".icns", "Outputs/"])
        
def geniconset(buildInfo):
    #start icon generation for given os
    if buildInfo.OS == "iOS":
        iOS(buildInfo)
    elif buildInfo.OS == "macOS":
        macOS(buildInfo)

def main():
    app = QApplication(sys.argv)
    
    buildInfo = BuildInfo()
    widget = PackerWindow(buildInfo)
    
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()