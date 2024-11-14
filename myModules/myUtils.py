"""
    This is a utilities module.
"""
# pylint: disable=W0603,W0622,W0703,C0103,C0116,C0301,E1101

import logging
import subprocess
import ctypes
from hashlib import md5
from json import dumps, loads, dump, load
from sys import argv
from glob import glob
from pytz import timezone, UTC
from time import localtime, strftime, time
from datetime import datetime, timedelta, date
from calendar import monthrange
from re import compile, findall, finditer, match, search
from os import path, curdir, makedirs, remove, chdir, listdir

from myModules import myConst
from myModules import myExcept
from myModules import myExcel
from myModules import myFile
from myModules import myDate
from myModules import myDict

startTime = 0

# https://stackoverflow.com/a/25432403
# https://stackoverflow.com/a/43441940

################################################################################################
def getTempPath():
    if myFile.isWindows():
        return 'c:/temp'
    else:
        return '/tmp'
    
################################################################################################
def isSameFile(file1: str, file2: str) -> bool:
    file1Hash = md5(open(file1, "rb").read()).hexdigest()
    file2Hash = md5(open(file2, "rb").read()).hexdigest()
    return file1Hash == file2Hash

################################################################################################
def isSameFileInDict(file: str, dictFiles: dict) -> tuple:
    fileHash = md5(open(file, "rb").read()).hexdigest()
    if fileHash in dictFiles:
        return True, dictFiles
    else:
        dictFiles[fileHash] = file
        return False, dictFiles

################################################################################################
# def removePngHeader(videoFileList):
#     import subprocess
#     newDir = 'new/'
#     makedirs(newDir, exist_ok=True)
#     count =len(videoFileList)
#     for videoFile in videoFileList:
#         ifStr = f'if={videoFile}'
#         ofStr = f'of={newDir}{videoFile}'
#         ibs = 'ibs=8'
#         skip = 'skip=1'
#         o = subprocess.check_output(['dd', ifStr, ofStr, ibs, skip], stderr=subprocess.STDOUT)
#         no = videoFile.replace('.ts', '')
#         percent = int(no) * 100 // count
#         number = f'{no}/{count}{percent:02}%)'
#         print(f'{number}: {o}')
#         remove(videoFile)
#     chdir(newDir)

################################################################################################
##  Styles:
##  0 : OK
##  1 : OK | Cancel
##  2 : Abort | Retry | Ignore
##  3 : Yes | No | Cancel
##  4 : Yes | No
##  5 : Retry | Cancel 
##  6 : Cancel | Try Again | Continue
def msgbox(title, text, style):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)

################################################################################################
def getCityCoordinate(city) -> tuple:
    # p1s = myExcel.CITIES[city].split('|')[1].split(',')
    p1s = myFile.readConfig(city)[2].split('+')
    return (float(p1s[0]), float(p1s[1])) # lon, lat

################################################################################################
def convertLocation(loc) -> str:
    launchCenters = myFile.readConfigLaunchCenters()
    for l in loc.split('/'):
        ret2 = launchCenters[l]
        # ret2 = constants.LOCATIONS_PATTERN[l]
        # ret2 = constants.LOCATIONS_PATTERN[l].split('|')[1]
        if ret2 != '':
            return ret2
    return ''

################################################################################################
#itemArray[0]: startDateUTC
#itemArray[1]: endDateUTC
#itemArray[2]: location
#itemArray[3]: coordinates
def devideToFiles(notams: dict) -> dict:
    notamFiles = {}

    for number, item in notams.items():
        itemArray = item.split(';')
        startDate = itemArray[0]
        endDate = itemArray[1]
        loc = itemArray[2]
        coordsArray = itemArray[3]
        city = convertLocation(itemArray[2])

    return notamFiles

################################################################################################
def findLatitudeLongitude(p, s) -> str:
    ret1 = ''
    itemsiter = finditer(p, s)
    items = findall(p, s)
    count = len(items)
    lastEnd = 0

    for item, itemiter in zip(items, itemsiter):
        tempCoord = convertLatitudeLongitude(p, item)
        if ret1 != '' and lastEnd + 10 < itemiter.start():
           ret1 = ret1[:-1] + '-' + tempCoord + '|' 
        elif tempCoord not in ret1:
            ret1 += tempCoord + '|'
        lastEnd = itemiter.end()
    return ret1.rstrip("|")

################################################################################################
def convertLatitudeLongitude(p, s) -> str:
    if match(p, s):
        return myFile.convertPatterns(s, p)
    else:
        return s

################################################################################################
def getYYYYMMDD(year):
    if len(year) == 2:
        return '20' + year
    else:
        return year

################################################################################################
def convertNotamDate(oldDate):
    if oldDate == 'PERM':
        return oldDate
    elif 'EST' in oldDate:
        return datetime.strptime(oldDate, '%m/%d/%Y %H%MEST').strftime("%Y/%m/%d %H:%M")
    # elif '年' in oldDate:
    #     if '-' in oldDate:
    #         dates = oldDate.split("-")
    #         date1 = datetime.strptime(dates[0], '%Y年%m月%d日')
    #         date2 = datetime.strptime(dates[1], '%Y年%m月%d日')
    #         diff = date2 - date1
    #         date3 = date1 + timedelta(diff.days / 2)
    #         return date3.strftime("%Y/%m/%d")
    #     else:
    #         return datetime.strptime(oldDate, '%Y年%m月%d日')
    else:
        return datetime.strptime(oldDate, '%m/%d/%Y %H%M').strftime("%Y/%m/%d %H:%M")
    
################################################################################################
def hasCoordinates(city) -> bool:
    if city != '':
        lat, lon = getCityCoordinate(city)
        if isinstance(lat, float) and isinstance(lon, float):
            return True
    return False

################################################################################################
# timeDiff = minutes
def isNearTime(date1, date2, timeDiff) -> bool:
    d1 = datetime.strptime(date1, "%Y/%m/%d %H:%M")
    d2 = datetime.strptime(date2, "%Y/%m/%d %H:%M")
    d = d2 - d1
    if d.total_seconds() > timeDiff * 60:
        return False
    return True

################################################################################################
# timeDiff = minutes
def isNsfNearTime(date1, date21, date22, timeDiff) -> bool:
    d1 = datetime.strptime(date1, "%Y年%m月%d日%H时%M分") - timedelta(hours=8)
    d21 = datetime.strptime(date21, "%Y/%m/%d %H:%M")
    d22 = datetime.strptime(date22, "%Y/%m/%d %H:%M")
    diff211 = abs(d21 - d1)
    diff221 = abs(d22 - d1)
    if d21 <= d1 <= d22 or diff211.total_seconds() <= timeDiff * 60 or diff221.total_seconds() <= timeDiff * 60:
        return True
    return False

################################################################################################
def drawPoint(kml, coords, location) -> None:
    p = kml.newpoint(name=location)
    p.coords = coords
    p.style.iconstyle.scale = 0.5
    if location == 'ZSHA':
        p.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pal5/icon18l.png'
    else:
        p.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pal5/icon43l.png'

################################################################################################
def checkArgv() -> tuple:
    if len(argv) <= 1 or not checkCommand(argv[1]):
        print(f'Usage: python {argv[0]}"Location"|"Free Text"')
        return '', '', ''

    if len(argv) == 2:
        p1 = ''
        p2 = ''
    elif len(argv) == 3:
        p1 = argv[2]
        p2 = ''
    elif len(argv) == 4:
        p1 = argv[2]
        p2 = argv[3]

    return argv[1], p1, p2

################################################################################################
def checkCommand(inputCommand) -> bool:
    for command, _ in myConst.COMMANDS.items():
        if command == inputCommand or inputCommand[:3] == command:
            return True
    return False

################################################################################################
# def getChromeDriver():
#     options = ChromeOptions()
#     if HEADLESS == 1:
#         options.add_argument('--headless')
#     options.add_experimental_option('excludeSwitches', ['enable-logging'])
#     return webdriver.Chrome(options=options)

################################################################################################
def printList(l):
    for i, value in enumerate(l):
        print(f'{i + 1:02} {value}')

################################################################################################
def runCommand(command):
    try:
        ret = subprocess.run(command, encoding='utf8', check=True, shell=True, text = True, capture_output=True)
        return ret
    except subprocess.CalledProcessError as cpe:
        myExcept.printExceptionTrace()
        raise cpe

####################################################################
# def sendEmail(subject: str, body: str, toEmail='zhengrong.zang@gmail.com'):
#     if isMacOS() or isLinux():
#         sender = 'mikezang2008@gmail.com'
#         password = 'New@20230831'
#         msg = []#MIMEText(body)
#         msg['Subject'] = subject
#         msg['From'] = sender
#         msg['To'] = toEmail
#     with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
#        smtp_server.login(sender, password)
#        smtp_server.sendmail(sender, toEmail, msg.as_string())
#     print("Message sent!")

################################################################################################
def getImageSize(filename: str) -> tuple:
    from PIL import Image
    im = Image.open(filename)
    return im.width, im.height

################################################################################################
def second2Time(floatTime: float) -> str:
    time = str(timedelta(seconds=floatTime))[:-7]
    time = time if len(time) == 8 else f'0{time}'
    return time

################################################################################################
def swapListItems(swapList: list, swapIndex1: int, swapIndex2: int) -> list:
    swapList[swapIndex1], swapList[swapIndex2] = swapList[swapIndex2], swapList[swapIndex1]
    return swapList

################################################################################################
def isFloat(str):
    return str.replace(".", "").isnumeric()

################################################################################################
def sortTwoLists(list1: list, list2: list, reverse=False):
    sortList2 = sorted(list2)
    sortList1 = [l1 for l1, _ in sorted(zip(list1, list2), reverse=reverse)]
    return sortList1, sortList2

################################################################################################
def isInvalidLocation(location, locations):
    if location in locations:
        return False
    return True

################################################################################################
def isInvalidEndDateUtc(endDateUtc):
    if endDateUtc == 'PERM':
        return True
    endDateUtc = convertNotamDate(endDateUtc)
    if isPastTime(endDateUtc):
        return True
    return False

def isChinaNotamOld(condition: str) -> bool:
    ret1 = 'AGGG' in condition
    ret1 |= 'KZAK' in condition
    ret1 |= 'VCCF' in condition
    ret1 |= 'VVHM' in condition
    ret1 |= 'VVHN' in condition
    ret1 |= 'VYYF' in condition
    ret1 |= 'WIIF' in condition
    ret1 |= 'YBBB' in condition
    ret1 |= 'YMMM' in condition
    ret1 &= 'CHINA' in condition
    if ret1:
        return ret1
    
    ret3 = ('RKRR' in condition) & ('KOREA' not in condition)
    ret3 |= 'RJJJ' in condition
    ret3 |= 'RPHI' in condition
    ret3 |= 'RCAA' in condition
    ret3 |= 'VHHK' in condition
    ret3 |= 'WSJC' in condition
    ret3 &= 'AEROSPACE' in condition
    if ret3:
        return ret3
    
    ret4 = 'ZBPE' in condition
    ret4 |= 'ZGZU' in condition
    ret4 |= 'ZHWH' in condition
    ret4 |= 'ZJSA' in condition
    ret4 |= 'ZLHW' in condition
    ret4 |= 'ZPKM' in condition
    ret4 |= 'ZSHA' in condition
    ret4 |= 'ZWUQ' in condition
    ret4 |= 'ZYSH' in condition
    ret4 &= ('TEMPORARY DANGER AREA ESTABLISHED' in condition) | ('TEMPORARY RESTRICTED AREA ESTABLISHED BOUNDED' in condition)
    if ret4:
        return ret4
    
    ret2 = 'NFFF' in condition
    ret2 &= 'TEMPO DANGER AREA ACTIVATED' in condition
    return ret2

################################################################################################
def isNotChinaNotam(location: str, condition: str) -> bool:
    if (location == 'YBBB' or location == 'YMMM') and 'CHINESE' not in condition:
        return True
    elif (location == 'VYYF' or location == 'KZAK') and 'CHINA' not in condition:
        return True
    elif location == 'RJJJ' and 'KOREA' in condition:
        return True

################################################################################################
def isPastTime(utcDate):
    localDate = myDate.convertToLocalDate(utcDate, "Asia/Tokyo")
    timeNow = datetime.now(timezone("Asia/Tokyo"))
    if timeNow >= localDate:
        return True
    else:
        return False

################################################################################################
def kanji2int(kanjis: str, error="raise", style="auto") -> int:
    """
    :param kanjis - str: Kanji str to convert into Integer
    :param error - str: How to handle Error. "raise": raise error. "ignore": ignore error , "warn": warn but don't raise
    :param style - str: Which style of format will be used. "mixed": Arabic and Kanji Mixed like "4億5230万3千", "all": All letter must be Kanji, "auto": detect automatically by checking any arabic character is in kanjis.
    :return: int
    """
    if error not in ("raise", "warn", "ignore"):
        raise ValueError(f"unexpected value {error} for argument error")
    COL_NUMBER = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
    little_digit = {"十": 1, "百": 2, "千": 3}
    digit = {"万": 4, "億": 8, "兆": 12, "京": 16, "垓": 20, "𥝱": 24, "穣": 28, "溝": 32, "澗": 36, "正": 40, "載": 44, "極": 48, "恒河沙": 52, "阿僧祇": 56, "那由多": 60, "不可思議": 64, "無量大数": 68}

    if style not in ("all", "mixed", "auto"):
        raise ValueError(f"unexpected value {style} for argument style")  # check arguments

    num = 0
    if style == "mixed" or (style == "auto" and any(str(num) in kanjis for num in range(10))):
        for group in compile(f"([0-9]*?千)?([0-9]*?百)?([0-9]*?十)?([0-9]*)({'|'.join(digit.keys())})?").findall(kanjis)[:-1]:
            c_num = 0
            for index, dig in enumerate(group[:4]):
                if dig:
                    c_num += (1000, 100, 10, 1)[index] * int(dig.rstrip('千百十') or 1)
            num += c_num * 10 ** digit.get(group[-1], 0)
        return num
    else:
        current_mini_num = 0
        current_num = 0
        for word in compile('|'.join(list(COL_NUMBER.keys()) + list(little_digit.keys()) + list(digit.keys()))).findall(kanjis):
            if word in COL_NUMBER:
                current_mini_num = COL_NUMBER[word]
            elif word in little_digit:
                current_num += (current_mini_num if current_mini_num else 1) * 10 ** little_digit[word]
                current_mini_num = 0
            elif word in digit:
                num += (current_num + current_mini_num) * 10 ** digit[word]
                current_num = current_mini_num = 0
            else:
                raise ValueError(f"unexpected letter: {word}")
        return num + current_num + current_mini_num

################################################################################################
# def getGreatCircleCoodinates(lon1, lat1, lon2, lat2):
#     g = pyproj.Geod(ellps='WGS84')
#     _, _, dist = g.inv(lon1, lat1, lon2, lat2)

#     # calculate line string along path with segments <= 1 km
#     # lonlats = g.npts(startlong, startlat, endlong, endlat, 1 + int(dist / 1000))
#     lonlats = g.npts(lon1, lat1, lon2, lat2, 1 + int(dist / 100000), initial_idx=0, terminus_idx=0) #<=100 km?

#     # npts doesn't include start/end points, so prepend/append them
#     return lonlats

################################################################################################
def readNotamDictDetailFromTextFile(filename):
    notam = {}
    i = 0
    with open(filename, encoding='UTF-8') as f:
        for line in f:
            i += 1
            if i > 2:
                d = convertToDict(line.replace('\n', ''))
                notam.update(d)
    return notam

################################################################################################
def convertToDict(line):
    data = line[4:].split(';')
    data1 = data[0].split(',')
    fir = data1[0]
    number = data1[1]
    startDate = data1[2]
    endDate = data1[3]
    d = {number : f'{startDate};{endDate};{fir};{data[1]}'}
    # print(d)
    return d

