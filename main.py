rom os import listdir
from os.path import isfile, join
mypath = "/Volumes/share/Download/"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
