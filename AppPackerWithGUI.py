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

#Pull User Inputs
buildclient = None
buildOS = None
packlist = []
pngsheet = None

#Grab Database
database = json.load(open("appdata.json", "r"))
pngkey = database["pngkey"]
urlkey = database["urlkey"]
transformkey = database["transformkey"]
#GUI
class GuiWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        QToolTip.setFont(QFont("SansSerif", 10))
        self.wlayout = QVBoxLayout(self)
        self.setWindowTitle("Apple Icon Maker")
        self.show()
        self.createSettingsButtons()
    
    def createSettingsButtons(self):
        #Build Top Level Buttons
        setbtnbox = QVBoxLayout()
        gbtn = QPushButton("Make Icon Set", self)
        gbtn.setToolTip("Make Icon Set")
        gbtn.resize(30, 600)
        gbtn.clicked.connect(self.start)
        
        osbtnlayout = QHBoxLayout()
        osbtngroup = QButtonGroup(osbtnlayout)
        iosbtn = QRadioButton("iOS")
        iosbtn.toggled.connect(lambda:self.osbtnstate("iOS"))
        osbtngroup.addButton(iosbtn)
        osbtnlayout.addWidget(iosbtn)
        mosbtn = QRadioButton("macOS")
        mosbtn.toggled.connect(lambda:self.osbtnstate("macOS"))
        osbtngroup.addButton(mosbtn)
        osbtnlayout.addWidget(mosbtn)
        
        pngsheetlayout = QHBoxLayout()
        pngsheetgroup = QButtonGroup(pngsheetlayout)
        for file in glob.glob("Inputs/*.png"):
            name = file.split("/")[1]
            pngbtn = QRadioButton(name)
            pngbtn.clicked.connect((lambda name: lambda: self.pngbtnstate(name))(name))
            pngsheetlayout.addWidget(pngbtn)
        
        self.scrollapps = QScrollArea()
        
        setbtnbox.addWidget(gbtn)
        setbtnbox.addLayout(osbtnlayout)
        setbtnbox.addLayout(pngsheetlayout)
        setbtnbox.addWidget(self.scrollapps)
        self.wlayout.addLayout(setbtnbox)

    def createAppSelection(self):
        #Build App List
        global pngsheet #make local later
        pngsheet = img.open("Inputs/"+buildclient)
        scrollbox = QGroupBox()
        applislayout = QFormLayout()
        i = 0
        imglis = []
        btnlis = []
        for entries in pngkey.keys():
            png = fetchicon(entries, "png")
            png = png.resize((100, 100))
            qpng = imgtoQt(png)
            lpng = QLabel(self)
            pixmap = QPixmap.fromImage(qpng)
            lpng.setPixmap(pixmap)
            lpng.resize(100, 100)
            lpng.setToolTip("This is how "+entries+" app will appear")
            imglis.append(lpng)

            btn = QPushButton(entries, self)
            btn.setToolTip("Click here to add "+entries+" to your icon set")
            if entries in packlist:
                btn.setStyleSheet("background-color: green")
            else:
                btn.setStyleSheet("background-color: red")
            btn.clicked.connect(self.selectbuttonPressed)
            btnlis.append(btn)
            
            applislayout.addRow(imglis[i], btnlis[i])
            i = i+1
        
        scrollbox.setLayout(applislayout)
        scroll = self.scrollapps
        scroll.setWidget(scrollbox)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(600)
    
    #Button Actions
    def pngbtnstate(self, name):
        global buildclient #make local later
        buildclient = name
        self.createAppSelection()
    
    def selectbuttonPressed(self):
        #change selection status
        sender = self.sender()
        if sender.styleSheet() == "background-color: green":
            packlist.remove(sender.text())
            sender.setStyleSheet("background-color: red")
        else:
            packlist.append(sender.text())
            sender.setStyleSheet("background-color: green")
    
    def start(self):
        #starts generation
        geniconset()
        
    def osbtnstate(self, btn):
        global buildOS #make local later
        buildOS = btn
    
    def closeEvent(self, event):
        #Quit dialog box
        reply = QMessageBox.question(self, "Message", "Are you sure you want to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
        
            
def fetchicon(name, otype):
    #find and return icon from pngsheet
    pos = pngkey[name]
    croppos = croppos=(pos[1]*1800, pos[0]*1800, (pos[1]*1800)+1500, (pos[0]*1800)+1500)
    icon = pngsheet.crop(croppos)
    if otype == "binary":
        fp = io.BytesIO()
        icon.save(fp, format="png")
        return(fp.getvalue())
    elif otype == "png":
        return(icon)
          
def geniconset():
    print(buildOS)
    #start icon generation for given os
    if buildOS == "iOS":
        iOS(buildclient, packlist)
    elif buildOS == "macOS":
        macOS(buildclient, packlist)
    
def icondict(name, pkname):
    #gen plist dict for app
    answer = dict(
        PayloadType = "com.apple.webClip.managed",
        PayloadVersion = 1,
        PayloadIdentifier = "com.boxofvoxels."+pkname+"-"+name,
        PayloadUUID = str(uuid.uuid4()),
        PayloadDisplayName = name,
        PayloadDescription = name+"Icon",
        PayloadOrganization = "Box Of Voxels iCons",
        URL = urlkey[name],
        Label = name,
        Icon = fetchicon(name, "binary"),
        IsRemovable = True,
        FullScreen = True,
    )
    return(answer)

def packableicon(name):
    #Check if app has url
    try:
        urlkey[name]
        return(True)
    except KeyError:
        return(False)

def iOS(buildclient, packlist):
    #Build iOS icon package
    packedapps = []

    for name in packlist:
        if packableicon(name):
            packedapps.append(icondict(name, buildclient))
        else:
            fetchicon(name, "png").save("Outputs/"+name+".png")
    
    buildfile = dict(
        PayloadType = "Configuration",
        PayloadVersion = 1,
        PayloadOrganization = "Box Of Voxel iCons",
        PayloadIdentifier = "com.boxofvoxels."+buildclient,
        PayloadUUID = str(uuid.uuid4()),
        PayloadDisplayName = buildclient,
        PayloadDescription = "",
        PayloadRemovalDisallow = False,
        PayloadContent = packedapps,
    )
    
    package = open("Outputs/"+buildclient+"iconpackage.mobileconfig", "wb")
    pll.dump(buildfile, package)
    package.close()

def macOS(buildclient, packlist):
    #Generate macOS icns files
    for name in packlist:
        terminal.call(["mkdir", name+".iconset"])
        icon = fetchicon(name, "png")
        for size, savename in transformkey:
            scaledicon = icon.resize((size, size))
            scaledicon.save(name+".iconset/icon_"+savename+".png")
        terminal.call(["iconutil", "-c", "icns", name+".iconset"])
        terminal.call(["rm", "-rf", name+".iconset"])
        terminal.call(["mv", name+".icns", "Outputs/"])
        
def main():
    app = QApplication(sys.argv)
    
    widget = GuiWindow()
    
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()