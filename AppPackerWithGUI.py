from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import json
import sys
from PIL import Image as img
from PIL.ImageQt import ImageQt as imgtoQt
import subprocess as terminal
import os
import plistlib as pll
import uuid
import io
img.MAX_IMAGE_PIXELS = 10000000000

buildclient = sys.argv[1]
buildOS = sys.argv[2]
packlist = []

database = json.load(open("appdata.json", "r"))
pngkey = database["pngkey"]
urlkey = database["urlkey"]
transformkey = database["transformkey"]
try:
    pngsheet = img.open("Inputs/"+buildclient+".png")
except FileNotFoundError:
    print("please try again with a valid image deck")
    
class GuiWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        QToolTip.setFont(QFont("SansSerif", 10))
        layout = QFormLayout()
        pagebox = QGroupBox()
        
        i = 0
        imglis = []
        btnlis = []
        for entries in pngkey.keys():
            png = fetchicon(entries, "png")
            png = png.resize((100, 100))
            qpng = imgtoQt(png)
            img = QLabel(self)
            pixmap = QPixmap.fromImage(qpng)
            img.setPixmap(pixmap)
            img.resize(100, 100)
            img.setToolTip("This is how "+entries+" app will appear")
            imglis.append(img)

            btn = QPushButton(entries, self)
            btn.setToolTip("Click here to add "+entries+" to your icon set")
            btn.resize(100, 100)
            btn.setStyleSheet("background-color: red")
            btn.clicked.connect(self.buttonPressed)
            btnlis.append(btn)
            
            layout.addRow(imglis[i], btnlis[i])
            i = i+1
        
        pagebox.setLayout(layout)
        btn = QPushButton("Make Icon Set", self)
        btn.setToolTip("Make Icon Set")
        btn.resize(30, 600)
        btn.clicked.connect(self.start)
        scroll = QScrollArea()
        scroll.setWidget(pagebox)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(600)
        wlayout = QVBoxLayout(self)
        wlayout.addWidget(scroll)
        wlayout.addWidget(btn)
        self.move(300, 300)
        self.setWindowTitle("Icon Maker")
        self.show()
        
    def buttonPressed(self):
        sender = self.sender()
        if sender.styleSheet() == "background-color: green":
            sender.setStyleSheet("background-color: red")
        else:
            packlist.append(sender.text())
            sender.setStyleSheet("background-color: green")
    
    def start(self):
        geniconset()
            

def fetchicon(name, otype):
    pos = pngkey[name]
    croppos = croppos=(pos[1]*1800, pos[0]*1800, (pos[1]*1800)+1500, (pos[0]*1800)+1500)
    icon = pngsheet.crop(croppos)
    if otype == "binary":
        fp = io.BytesIO()
        icon.save(fp, format="png")
        return(fp.getvalue())
    elif otype == "png":
        return(icon)

def pressed():
    print("button pressed")
          
def geniconset():
    if buildOS.lower() in ["ios", "iphone"]:
        print("Now building icon set for "+buildclient+"'s iOS Device")
        iOS(buildclient, packlist)
    elif buildOS.lower() in ["macos", "macbook"]:
        print("Now building icon set for "+buildclient+"'s macOS Device")
        macOS(buildclient, packlist)
    else:
        print("Please try again with a valid format")

    print("The icon set for "+buildclient+" is now complete")
    print("look in the outputs folder")
    
def icondict(name, pkname):
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

def genpacklist():
    for img in pngkey.keys():
        asking = True
        while asking:
            selection = input("Do you want an icon for "+img+"? [y/n]\n")
            if selection == "y":
                packlist.append(img)
                asking = False
            elif selection == "n":
                asking = False
            else:
                print("invalid input")

def packableicon(name):
    try:
        urlkey[name]
        return(True)
    except KeyError:
        return(False)

def iOS(buildclient, packlist):
    packedapps = []

    for name in packlist:
        if packableicon(name):
            packedapps.append(icondict(name, buildclient))
            print(name+" has been added to the automatic icon package")
        else:
            fetchicon(name, "png").save("Outputs/"+name+".png")
            print(name+" could not be added to the automatic icon package the image has been saved alonge side it")
    
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