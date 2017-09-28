import sys
import os
import re
import datetime
import dateutil.relativedelta
import exifread
import pprint
import operator
import argparse

# import string
from os import listdir, rename
from os.path import isfile, join
from time import gmtime, strftime
from colorama import init
init()

# Custom class for console color support
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[30m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def valid_date(datestring):
    try:
        datetime.datetime.strptime(datestring, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def generateValidName(badName):
    dateBadName = badName.split(" ")[0]
    # re.sub(r'[^0-9]', '', dateBadName)
    # print()
    return re.sub(r'[^0-9-]', '', dateBadName) + " " + badName.split(" ",1)[1].title()

def generateValidNameFromFolder(badName):
    dateName = badName.split(" ", 1)[0].replace("-", "")
    return dateName + "_" + badName.split(" ", 1)[1].title().replace(" ", "").replace(",", "").replace("-", "")

def generateHumanReadableDatetime(deltaDate):
    prettyDatetime = ""
    if deltaDate.years != 0:
        prettyDatetime = str(deltaDate.years) + " years"
    if deltaDate.months != 0:
        if prettyDatetime == "":
            prettyDatetime = str(deltaDate.months) + " months"
        else:
            prettyDatetime = prettyDatetime + ", " + str(deltaDate.months) + " months"
    if deltaDate.days != 0:
        if prettyDatetime == "":
            prettyDatetime = str(deltaDate.days) + " days"
        else:
            prettyDatetime = prettyDatetime + ", " + str(deltaDate.days) + " days"
    if deltaDate.hours != 0:
        if prettyDatetime == "":
            prettyDatetime = str(deltaDate.hours) + " hours"
        else:
            prettyDatetime = prettyDatetime + ", " + str(deltaDate.hours) + " hours"
    if deltaDate.minutes != 0:
        if prettyDatetime == "":
            prettyDatetime = str(deltaDate.minutes) + " minutes"
        else:
            prettyDatetime = prettyDatetime + ", " + str(deltaDate.minutes) + " minutes"
    if deltaDate.seconds != 0:
        if prettyDatetime == "":
            prettyDatetime = str(deltaDate.seconds) + " seconds"
        else:
            prettyDatetime = prettyDatetime + ", " + str(deltaDate.seconds) + " seconds"
    if deltaDate.microseconds != 0:
        if prettyDatetime == "":
            prettyDatetime = str(round(deltaDate.microseconds/1000)) + " ms"
        else:
            prettyDatetime = prettyDatetime + " and " + str(round(deltaDate.microseconds/1000)) + " ms"
    return prettyDatetime


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.
    
    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes":"yes",   "y":"yes",  "ye":"yes",
             "no":"no",     "n":"no"}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while 1:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return default
        elif choice in valid.keys():
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")

def directory_name_check():
    needFixDirectories = []
    cleanDirectories = []

    print(bcolors.OKBLUE + ">> Step 1: Directory naming check" + bcolors.ENDC)
    step1start = datetime.datetime.now()

    for subdirectory in next(os.walk(mypath))[1]:
        if valid_date(subdirectory.split(" ")[0]) and subdirectory.split(" ", 1)[1].istitle():
            print(bcolors.OKGREEN + "   " + subdirectory + bcolors.ENDC)
            cleanDirectories.append(subdirectory)
        else:
            print(bcolors.FAIL + "   " + subdirectory + bcolors.ENDC)
            needFixDirectories.append(subdirectory)

    if needFixDirectories:
        if query_yes_no("Some directory were malformated, do you want me to try fixing them?") == "yes":
            for directoryToFix in needFixDirectories:
                newName = generateValidName(directoryToFix)
                if newName != directoryToFix:
                    rename(mypath + directoryToFix, mypath + newName)
                else:
                    sys.exit("Cannot find better name for '" + mypath + directoryToFix + "', this could be caused by wrong date, please fix it before going further, aborting...")

    step1finish = datetime.datetime.now()
    rd = dateutil.relativedelta.relativedelta (step1finish, step1start)
    print(bcolors.OKBLUE + ">> Step 1 completed successfully in " + generateHumanReadableDatetime(rd) + bcolors.ENDC)

def find_orphan_files():
    print(bcolors.OKBLUE + ">> Step 2: Finding orphans RAW files" + bcolors.ENDC)
    step2start = datetime.datetime.now()

    jpgFiles = []
    rawFiles = []
    orphansRawFiles = []

    for dirpath, dirs, files in os.walk(mypath):
        files = [f for f in files if f != '.DS_Store']
        for name in files:
            if name.lower().endswith(('.png', '.jpg', '.jpeg')):
                jpgFiles.append(os.path.join(dirpath, name))
            else:
                rawFiles.append(os.path.join(dirpath, name))

    for rawFile in rawFiles:
        jpgFile = os.path.splitext(rawFile)[0] + '.JPG'
        if not os.path.isfile(jpgFile):
            orphanRawFileDirectory = os.path.dirname(os.path.abspath(rawFile.replace(mypath, myDeletePath)))
            if not os.path.exists(orphanRawFileDirectory):
                os.makedirs(orphanRawFileDirectory)
            # os.rename(rawFile, rawFile.replace("TODOPHOTOS", "TODELETEPHOTOS"))
            print(bcolors.OKGREEN + "   Orphan file moved: " + rawFile + bcolors.ENDC)
            orphansRawFiles.append(rawFile)

    for orphanRawFile in orphansRawFiles:
        rawFiles.remove(orphanRawFile)

    step2finish = datetime.datetime.now()
    rd = dateutil.relativedelta.relativedelta (step2finish, step2start)
    print(bcolors.OKBLUE + ">> Step 2 completed successfully in " + generateHumanReadableDatetime(rd) + bcolors.ENDC)

    jpgCount = len(jpgFiles)
    rawCount = len(rawFiles)
    if jpgCount != rawCount:
        print(bcolors.FAIL + "Mismatch between JPG count (" + str(jpgCount) + ") and RAW count (" + str(rawCount) + ")! Aborting..." + bcolors.ENDC)
        exit()

def rename_photo_exif():
    print(bcolors.OKBLUE + ">> Step 3: Renaming files based on EXIF infos" + bcolors.ENDC)
    step3start = datetime.datetime.now()

    for folder in os.listdir(mypath):
        if os.path.isdir(os.path.join(mypath, folder)):
            dict = {}
            initialCount = 1
            onlyfiles = [f for f in listdir(os.path.join(mypath, folder)) if isfile(join(os.path.join(mypath, folder), f)) and f != '.DS_Store']
            for fileT in onlyfiles:
                if fileT.lower().endswith(('.png', '.jpg', '.jpeg')):
                    f = open(join(os.path.join(mypath, folder), fileT), 'rb')
                    dict[join(os.path.join(mypath, folder), fileT)] = exifread.process_file(f)["EXIF DateTimeOriginal"].values
            for sorted_dict in sorted(dict.items(), key=operator.itemgetter(1)):
                newName = os.path.join(folder, generateValidNameFromFolder(folder) + "_" + str(initialCount).rjust(3, "0") + ".jpg")
                # os.rename(sorted_dict[0], newName)
                print(bcolors.OKGREEN + "   Renaming file " + sorted_dict[0].replace(mypath, "") + " to " + newName.split("\\")[1] + bcolors.ENDC)
                initialCount += 1

    step3finish = datetime.datetime.now()
    rd = dateutil.relativedelta.relativedelta (step3finish, step3start)
    print(bcolors.OKBLUE + ">> Step 3 completed successfully in " + generateHumanReadableDatetime(rd) + bcolors.ENDC)

def separating_raw_files():
    print(bcolors.OKBLUE + ">> Step 4: Separating photos JPG<>RAW")
    step4start = datetime.datetime.now()

    for dirpath, dirs, files in os.walk(mypath):
        files = [f for f in files if f != '.DS_Store']
        for name in files:
            if name.lower().endswith(('.png', '.jpg', '.jpeg')):
                jpgFiles.append(os.path.join(dirpath, name))
            else:
                rawFiles.append(os.path.join(dirpath, name))

    for rawFile in rawFiles:
        rawFileDirectory = os.path.dirname(os.path.abspath(rawFile.replace(mypath, myRawMovePath)))
        if not os.path.exists(rawFileDirectory):
            os.makedirs(rawFileDirectory)
        # os.rename(rawFile, rawFile.replace("TODOPHOTOS", "TODELETEPHOTOS"))
        print(bcolors.OKGREEN + "   RAW file moved: " + rawFile + bcolors.ENDC)

    for jpgFile in jpgFiles:
        jpgFileDirectory = os.path.dirname(os.path.abspath(jpgFile.replace(mypath, myJpgMovePath)))
        if not os.path.exists(jpgFileDirectory):
            os.makedirs(jpgFileDirectory)
        # os.rename(jpgFile, jpgFile.replace("TODOPHOTOS", jpgFileDirectory))
        print(bcolors.OKGREEN + "   JPG file moved: " + jpgFile + bcolors.ENDC)


    step4finish = datetime.datetime.now()
    rd = dateutil.relativedelta.relativedelta (step4finish, step4start)
    print(bcolors.OKBLUE + ">> Step 4 completed successfully in " + generateHumanReadableDatetime(rd) + bcolors.ENDC)


# Usage
def msg(name=None):                                                            
    return '''main.py
         [--startFolder, Pass argument startFolder]
        '''

# Main routine
parser = argparse.ArgumentParser(description='Process photos: EXIF-based renaming, RAW files split, ...', usage=msg())
parser.add_argument('--startFolder', help='Start folder containing all photos subfolders that will be processed')

if not len(sys.argv) > 1:
    parser.print_help()
    exit()

args = parser.parse_args()

myRootPath = "Y:\\Download\\A_TRIER_PHOTOS\\"
mypath = args.startFolder
# aRgument = PhotoFolder
# create PhotoFolderWorkDir \todelete
#                           \tomovePhotos
#                           \tomovePhotosRAW

if not os.path.exists(args.startFolder):
    print(bcolors.FAIL + "> Directory " + args.startFolder + " does not exist" + bcolors.ENDC)

myDeletePath = myRootPath + "todelete\\"
myRawMovePath = myRootPath + "tomovePhotosRAW\\"
myJpgMovePath = myRootPath + "tomovePhotos\\"

if not os.path.exists(myDeletePath):
    os.makedirs(myDeletePath)

if not os.path.exists(myJpgMovePath):
    os.makedirs(myJpgMovePath)

if not os.path.exists(myRawMovePath):
    os.makedirs(myRawMovePath)

print(bcolors.HEADER + "> Starting photomapyc process on " + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + bcolors.ENDC)
print(bcolors.HEADER + "> Selected root folder is '" + mypath + "'" + bcolors.ENDC)

pattern = re.compile("^([A-Z][0-9]+)+$")

# First step is directory naming check
directory_name_check()

# Second step is finding orphan files and removing them
find_orphan_files()

# Thirs step is renaming photo based on EXIF tags
rename_photo_exif()

# Fourth step is separating JPG files from RAW files
separating_raw_files()

rd = dateutil.relativedelta.relativedelta (step4finish, step1start)
print(bcolors.HEADER + "> Completed in '" + generateHumanReadableDatetime(rd) + bcolors.ENDC)
