import sys
import json

appname = str(sys.argv[1])
appposr = int(sys.argv[2])
appposc = int(sys.argv[3])
try:
    appurl = str(sys.argv[4])
except IndexError:
    appurl = None

ifile = open("appdata.json", "r")
data = json.load(ifile)
ifile.close()

data["pngkey"][appname] = [appposr, appposc]
if appurl:
    data["urlkey"][appname] = appurl
    
ofile = open("appdata.json", "w")
json.dump(data, ofile, indent=4)
ofile.close()