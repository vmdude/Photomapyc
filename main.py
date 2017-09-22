import sys
import os
import re
import datetime
import dateutil.relativedelta
import exifread
import pprint
import operator

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
    ENDC = '\033[0m'
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




    # onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    # print(onlyfiles)
    # print(needFixDirectories)
    if needFixDirectories:
        # print(bcolors.WARNING + "Some directory were malformated, do you want me to try fixing them?")
    # answer = query_yes_no("Some directory were malformated, do you want me to try fixing them?")

        if query_yes_no("Some directory were malformated, do you want me to try fixing them?") == "yes":
        # print("ok")

        for directoryToFix in needFixDirectories:
            newName = generateValidName(directoryToFix)
            if newName != directoryToFix:
                rename(mypath + directoryToFix, mypath + newName)
            else:
                sys.exit("Cannot find better name for '" + mypath + directoryToFix + "', this could be caused by wrong date, please fix it before going further, aborting...")

    step1finish = datetime.datetime.now()
    # step1ttb = step1finish - step1start
    # print(bcolors.OKBLUE + ">> Step 1 completed successfully in" + divmod(step1ttb.days * 86400 + step1ttb.seconds, 60))




    # dt1 = datetime.datetime.fromtimestamp(123456789) # 1973-11-29 22:33:09
    # dt2 = datetime.datetime.fromtimestamp(234567890) # 1977-06-07 23:44:50
    rd = dateutil.relativedelta.relativedelta (step1finish, step1start)
    print(bcolors.OKBLUE + ">> Step 1 completed successfully in " + generateHumanReadableDatetime(rd) + bcolors.ENDC)


# mypath = "/Volumes/share/Download/"
mypath = "Y:\\Download\\TODOPHOTOS\\"
myDeletePath = "Y:\\Download\\TODELETEPHOTOS\\"

if not os.path.exists(myDeletePath):
    os.makedirs(myDeletePath)

print(bcolors.HEADER + "> Starting photomapyc process on " + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + bcolors.ENDC)
print(bcolors.HEADER + "> Selected root folder is '" + mypath + "'" + bcolors.ENDC)

pattern = re.compile("^([A-Z][0-9]+)+$")

# First step is directory naming check
directory_name_check()


# print(generateHumanReadableDatetime(rd))
# 3 years, 6 months, 9 days, 1 hours, 11 minutes and 41 seconds


print(bcolors.OKBLUE + ">> Step 2: Finding orphans RAW files" + bcolors.ENDC)
step2start = datetime.datetime.now()

jpgFiles = []
rawFiles = []

for dirpath, dirs, files in os.walk(mypath):
    files = [f for f in files if f != '.DS_Store']
    for name in files:
        if name.lower().endswith(('.png', '.jpg', '.jpeg')):
            jpgFiles.append(os.path.join(dirpath, name))
        else:
            rawFiles.append(os.path.join(dirpath, name))

orphansRawFiles = []

for rawFile in rawFiles:
    jpgFile = os.path.splitext(rawFile)[0] + '.JPG'
    if not os.path.isfile(jpgFile):
        # photoJpgFilename = os.path.splitext(os.path.join(dirpath, name))[0]+'.JPG'
        rawFileDirectory = os.path.dirname(os.path.abspath(rawFile.replace("TODOPHOTOS", "TODELETEPHOTOS")))
        if not os.path.exists(rawFileDirectory):
            os.makedirs(rawFileDirectory)
        # os.path.dirname(os.path.abspath(rawFile))
        # print(os.path.dirname(os.path.abspath(rawFile)))
        # print(rawFile.replace("TODOPHOTOS", "TODELETEPHOTOS"))
        # os.rename(rawFile, rawFile.replace("TODOPHOTOS", "TODELETEPHOTOS"))
        # tmpFileName = rawFile.split("\\")
        print(bcolors.OKGREEN + "   Orphan file moved: " + rawFile)
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

print(bcolors.OKBLUE + ">> Step 3: Renaming files based on EXIF infos" + bcolors.ENDC)
step3start = datetime.datetime.now()


for folder in os.listdir(mypath):
    if os.path.isdir(os.path.join(mypath, folder)):
        # print(folder)
        dict = {}
        initialCount = 1
        onlyfiles = [f for f in listdir(os.path.join(mypath, folder)) if isfile(join(os.path.join(mypath, folder), f)) and f != '.DS_Store']
        for fileT in onlyfiles:
            if fileT.lower().endswith(('.png', '.jpg', '.jpeg')):
                f = open(join(os.path.join(mypath, folder), fileT), 'rb')
                # tags = exifread.process_file(f)["EXIF DateTimeOriginal"].values
                # for tag in tags.keys():
                #     if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
                #         print("Key: %s, value %s" % (tag, tags[tag]))
                dict[join(os.path.join(mypath, folder), fileT)] = exifread.process_file(f)["EXIF DateTimeOriginal"].values
                # initialCount += 1
        for sorted_dict in sorted(dict.items(), key=operator.itemgetter(1)):
            newName = os.path.join(folder, generateValidNameFromFolder(folder) + "_" + str(initialCount).rjust(3, "0") + ".jpg")
            # os.rename(sorted_dict[0], newName)
            print(bcolors.OKGREEN + "   Renaming file " + sorted_dict[0].replace(mypath, "") + " to " + newName.split("\\")[1] + bcolors.ENDC)
            initialCount += 1
        # pprint.pprint(dict)
        # exit()

# 200803_SalonDuModelismeLeBourget_010.jpg

step3finish = datetime.datetime.now()
rd = dateutil.relativedelta.relativedelta (step3finish, step3start)
print(bcolors.OKBLUE + ">> Step 3 completed successfully in " + generateHumanReadableDatetime(rd) + bcolors.ENDC)

print(bcolors.OKBLUE + ">> Step 4: Separating photos JPG<>RAW")
step4start = datetime.datetime.now()
step4finish = datetime.datetime.now()
rd = dateutil.relativedelta.relativedelta (step4finish, step4start)
print(bcolors.OKBLUE + ">> Step 4 completed successfully in " + generateHumanReadableDatetime(rd) + bcolors.ENDC)
