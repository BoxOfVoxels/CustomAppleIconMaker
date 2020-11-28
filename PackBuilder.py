import json
import sys
from PIL import Image as img
import subprocess as terminal
import os
import plistlib as pll
import uuid
import io


img.MAX_IMAGE_PIXELS = 10000000000


buildclient = sys.argv[1]
buildOS = sys.argv[2]
packlist = ["Amazon", "Snapchat", "Bitmoji"] #to be pulled in from external source later

database = json.load(open("appdata.json", "r"))
pngkey = database["pngkey"]
urlkey = database["urlkey"]
transformkey = database["transformkey"]
try:
    pngsheet = img.open("Inputs/"+buildclient+".png")
except FileNotFoundError:
    print("please try again with a valid image deck")

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
        
            

genpacklist()
            
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
    