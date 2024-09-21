"""
    This is a utilities module.
"""
# pylint: disable=W0603,W0622,W0703,C0103,C0116,C0301,E1101

import logging
import configparser
import subprocess
import unicodedata
import ctypes
from hashlib import md5
from numpy import zeros
from json import dumps, loads, dump, load
from sys import argv, platform
from glob import glob
from pathlib import Path
from pytz import timezone, UTC
from time import localtime, strftime, time
from datetime import datetime, timedelta, date
from calendar import monthrange, month_abbr
from re import compile, findall, finditer, match, sub, search
from os import path, linesep, curdir, makedirs, remove, chdir, listdir, walk, system
from typing import NamedTuple

from myModules import constants
from myModules import myExcept
from myModules import myExcel

class FileInfo(NamedTuple):
    origName: str   # 'videos/01.mp4'
    baseName: str   # basename='01.mp4'
    folderName: str # dirname='videos'
    absFolder: str  # abspath='C://zang/python/RocketLaunch/videos'
    fileName: str   # vfilename='01'
    extension: str  # extension='mp4'

startTime = 0

# https://stackoverflow.com/a/25432403
# https://stackoverflow.com/a/43441940

################################################################################################
def getFileDuration(filename: str) -> float:
    if not isVideoFile(filename) and not isAudioFile(filename):
        print(f'{filename} is not Audio/Video file!')
        return 0
    cmd = f"ffprobe -v fatal -show_entries format=duration -of default=nw=1:nk=1 {filename}"
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return float(result.stdout)

################################################################################################
def getDateAfterDays(startDate, days: int):
    if isinstance(startDate, str):
        startDate1 = datetime.strptime(startDate.replace('-', '/'), "%Y/%m/%d")
    endDate = startDate1 + timedelta(days=days)
    if isinstance(startDate, str):
        endDate = endDate.strftime('%Y/%m/%d')
    return endDate

################################################################################################
def listFilesByGlob(partOfFilename):
    return glob(partOfFilename)

################################################################################################
def convertToDiacritic(text, mode="NFC"):
    """
    基底文字と濁点・半濁点を結合
    """
    bytes_text = text.encode()  # str -> bytes

    # 濁点Unicode結合文字置換
    bytes_text = sub(b"\xe3\x82\x9b", b'\xe3\x82\x99', bytes_text)
    bytes_text = sub(b"\xef\xbe\x9e", b'\xe3\x82\x99', bytes_text)

    # 半濁点Unicode結合文字置換
    bytes_text = sub(b"\xe3\x82\x9c", b'\xe3\x82\x9a', bytes_text)
    bytes_text = sub(b"\xef\xbe\x9f", b'\xe3\x82\x9a', bytes_text)
    text = bytes_text.decode() # bytet -> str
    text = unicodedata.normalize(mode, text) # 正規化
    return text

################################################################################################
def keepOneLineChar():
    if isWindows():
        return '^'
    else:
        return '\\'
    
################################################################################################
def removeItemsFromTwoLists(list1: list, list2: list, list1Remove: list):
    list1New = list1.copy()
    list2New = list2.copy()
    durationRemoved = 0
    for i1Removed in list1Remove:
        list1New, list2New = zip(*((l1, l2) for l1, l2 in zip(list1New, list2New) if l1 != i1Removed))
        if i1Removed in list1:
            removedIndex = list1.index(i1Removed)
            durationRemoved += list2[removedIndex]
    return list1New, list2New, durationRemoved

################################################################################################
def readTextFile(filename, tripLinefeed=False):
    with open(filename, encoding='utf-8') as f:
        lines = [line.rstrip('\n') for line in f.readlines()] if tripLinefeed else f.readlines()
        return [convertToDiacritic(line) for line in lines]
    
################################################################################################
def setStartTime():
    global startTime
    startTime = time()
    
################################################################################################
def showRunTime():
    global startTime
    endTime = time()
    runTime = endTime - startTime
    print(f"\nFinish: {strftime('%Y-%m-%d %H:%M:%S', localtime(endTime))}")
    print(f'Run time: {timedelta(seconds=runTime)}')

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
def readDictFromFile(filename: str):
    with open(filename) as f: 
        data = f.read()
        return loads(data) 
    
################################################################################################
def saveDictToFile(filename: str, dataDict: dict):
    with open(filename, 'w', encoding="utf-8") as f:
        f.write(dumps(dataDict))
        print(f'Save dict to "{path.abspath(filename)}"')

################################################################################################
def saveDictToTextFile(filename, dataDict):
    lines = ''
    with open(filename, 'w', encoding="utf-8") as f:
        for i, (key, value) in enumerate(dataDict.items(), 1):
            lines += f'{i:02} {key}: {value}\n'
        f.write(lines)
        print(f'Save dict to "{path.abspath(filename)}"')

################################################################################################
def saveListToTextFile(filename, dataList):
    lines = ''
    with open(filename, 'w', encoding="utf-8") as f:
        for line in dataList:
            lines += f'{line}\n'
        f.write(lines)
        print(f'Save dict to "{path.abspath(filename)}"')

################################################################################################
def saveDictToJsonFile(nsfDict, filename):
    print(f'Save   to file "{filename}.json"')
    with open(f'{filename}.json', "w", encoding="utf-8") as f:
        dump(nsfDict, f, ensure_ascii=False, indent=2)

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
def removeFile(folderWithWildcard):
    # Get a list of all the file paths that ends with .txt from in specified directory
    fileList = glob(f'{folderWithWildcard}')
    # Iterate over the list of filepaths & remove each file.
    for filePath in fileList:
        try:
            remove(filePath)
        except:
            #print("Error while deleting file : ", filePath)
            pass

################################################################################################
def getTitle(filename):
    title = path.basename(filename)  # Get the filename from the path
    title = title.split('.')[0]  # Remove the extension
    title = title.split('\\')[-1]  # Get the last portion of the path
    return title

################################################################################################
def setLogging(filename):
    level = logging.INFO
    datefmt = "%Y-%m-%d %H:%M:%S"
    format = '%(asctime)s %(levelname)-6s %(processName)s %(name)s %(message)s'
    handlers = [logging.FileHandler(filename, encoding='utf-8'), logging.StreamHandler()]
    logging.basicConfig(level=level, handlers=handlers, encoding='utf-8', format=format, datefmt=datefmt)
    # logging.basicConfig(level=level, filename=filename, encoding='utf-8', format=format, datefmt=datefmt)
    # formatter = logging.Formatter(format)
    # console = logging.StreamHandler()
    # console.setLevel(logging.INFO)
    # console.setFormatter(formatter)
    # logging.getLogger().addHandler(console)

################################################################################################
def createFolder(filePath):
    folderPath = path.dirname(filePath)
    folder = Path(folderPath)
    if not folder.exists():
        makedirs(folder, exist_ok=True)

################################################################################################
def getLastdayOfMonth(year, month):
    return monthrange(int(year), int(month))[1]

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
def combineValuesForSameDictKey(d1: dict, d2: dict) -> dict:
    return {k: (d1[k] + '/' + d2[k]
                if k in d1 and k in d2 and d1[k] not in d2[k] and d2[k] not in d1[k]
                else d1[k] if k in d1 else d2[k])
            for k in set(d1).union(d2)}

################################################################################################
def getJapanTimeFilename(fmt='') -> str:
    if fmt == '':
        fmt = "%Y%m%d-%H%M%S"
    return datetime.now(timezone(constants.TIMEZONE_TOKYO)).strftime(fmt)

def getJapanTime(fmt='') -> str:
    if fmt == '':
        fmt = "%Y/%m/%d %H:%M:%S"
    return datetime.now(timezone(constants.TIMEZONE_TOKYO)).strftime(fmt)

def getUTCTime(fmt='') -> str:
    if fmt == '':
        fmt = "%Y/%m/%d %H:%M:%S"
    return datetime.now(timezone('UTC')).strftime(fmt)

################################################################################################
def getThisYear():
    return getJapanDate()[:4]

################################################################################################
def getJapanDate(fmt='') -> str:
    if fmt == '':
        fmt = "%Y%m%d"
    return datetime.now(timezone(constants.TIMEZONE_TOKYO)).strftime(fmt)

################################################################################################
def getChinaTime(d, fmt=''):
    if fmt == '':
        return constants.TIMEZONE__UTC.localize(d).astimezone(constants.TIMEZONE_SHANGHAI)
    else:
        return constants.TIMEZONE__UTC.localize(d).astimezone(constants.TIMEZONE_SHANGHAI).strftime(fmt)

################################################################################################
# def showNotamDetail(driver, td):
#     elementClick(driver, 30, XPATH_TD_SPAN)
#     ret1 = elementXPath(driver, 30, XPATH_SPAN_DETAIL)
#     return ret1

################################################################################################
def convertTitle(utcStartDate, utcEndDate, loc, loc1=None, isLocalTime=False) -> str:
    loc = loc1 if loc == '' else loc
    if utcStartDate != '' and utcEndDate != '':
        startTime = convertToLocalDate(utcStartDate, constants.TIMEZONE_SHANGHAI, isLocalTime=isLocalTime)
        lastEndTime = convertToLocalDate(utcEndDate, constants.TIMEZONE_SHANGHAI, isLocalTime=isLocalTime)
        endTime = datetime(startTime.year, startTime.month, startTime.day, lastEndTime.hour, lastEndTime.minute)
        endTime = endTime + timedelta(days=1) if str(endTime) < str(startTime) else endTime 
        endTime = timezone(constants.TIMEZONE_SHANGHAI).localize(endTime)
        launchTime = startTime + (endTime - startTime) / 3
        return f'{launchTime.strftime("%Y年%m月%d日%H時%M分")}{loc}'
    else:
        return loc
    # return f'{convertToLocalDate(utcStartDate, constants.TIMEZONE_SHANGHAI).strftime("%Y年%m月%d日%H時%M分")}{loc}'

################################################################################################
def getCityCoordinate(city) -> tuple:
    p1s = myExcel.CITIES[city].split('|')[1].split(',')
    return [float(p1s[0]), float(p1s[1])]

#N16°33',E093°17'
#N16°33'44",E093°17'66"
#Decimal degrees	            +-50.91721,      +-5.91775
#Decimal degrees	            NS50.91721°,    EW5.91775°
#Degrees and decimal minutes	NS50°55.032',   EW5°55.065'
#Degrees, minutes and seconds	NS50°55'1.956'',EW5°55'3.9''
#Degrees, minutes and seconds	NS505501,        EW0055503
################################################################################################
def convertDMS2DD(old) -> tuple:
    direction = {'N':1, 'S':-1, 'E': 1, 'W':-1}
    news = old.split(',')
    new = []
    for coord in news:
        coord_dir = coord[0:1]
        coord1 = coord[1:].replace('°',' ').replace('\'',' ').replace('"',' ').replace('.', '').replace('-', '')
        coord2 = coord1.split()
        if len(coord2) == 2:
            coord2.append("0")
        new.insert(0, direction[coord_dir] * (int(coord2[0]) + int(coord2[1]) / 60.0 + int(coord2[2]) / 3600.0))
        # new.append(direction[coord_dir] * (int(coord2[0]) + int(coord2[1]) / 60.0 + int(coord2[2]) / 3600.0))
    return new

################################################################################################
def convertLocation(loc) -> str:
    launchCenters = readConfigLaunchCenters()
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

def getFirRegExPattern(fir:str):
    pattern = '(' + fir.replace(' ', '|') + ')'
    return pattern

MSA_LOCATIONS = {'鲁航警': 'SD', '粤航警': 'GD', '琼航警': 'HN'}
################################################################################################
def getMsaLocation(content) -> str:
    locations = finditer(constants.MSA_PATTERN_NUMBER, content)
    for m in locations:
        if m.group(1) in MSA_LOCATIONS:
            return f'{MSA_LOCATIONS[m.group(1)]}{m.group(2)}'
        else:
            return m.groups()
    else:
        return ''

################################################################################################
def getNsfLocation(content) -> str:
    firNames = readConfigFirNames()
    pattern = getFirRegExPattern(firNames)
    locations = finditer(pattern, content)
    if locations:
        loc = ''
        lastEnd = 0
        for m in locations:
            if lastEnd == 0 or m.start() - lastEnd < 10:
                if loc != '':
                    loc += '/'
                loc += m.group()
            lastEnd = m.end()
        return loc
    else:
        return ''

################################################################################################
def getNotamLocation(content) -> str:
    # firNames = readConfigFirNames()
    # pattern = getFirRegExPattern(firNames)
    # locations = sorted(set(findall(pattern, content)))
    pattern = r'A\) ((?:[A-Z]{4} ?){0,3})'
    locations = findall(pattern, content)
    loc = ''
    if len(locations) > 0:
        loc = '/'.join(locations[0].split())
    return loc 

################################################################################################
def getNsfArea(contentSection) -> str:
    area = ''
    questionLatLons = findall(constants.PATTERM_QUESTION, contentSection)
    latlons = findall(constants.PATTERN_LATITUDE_LONGITUDE, contentSection)
    for latlon in latlons:
        if latlon in questionLatLons or latlon in area:
            continue
        if area != '':
            area += '|'
        area += latlon
    return area

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
        return convertPatterns(s, p)
    else:
        return s

################################################################################################
def getNotamArea(contentSection) -> str:
    area = ''
    lastEnd = 0
    startIndex = contentSection.find('E)')
    latlons = finditer(constants.PATTERN_LATITUDE_LONGITUDE, contentSection[startIndex:])
    for m in latlons:
        if lastEnd > 0 and m.start() > lastEnd + 10:
            area += '-' + m.group()
        else:
            if m.group() not in area:
                if area != '':
                    area += '|'
                area += m.group() 
        lastEnd = m.end()
    if area:
        count = len(area.split('|')) + len(area.split('-'))
        if count == 2:
            radiusList = findall(constants.PATTERN_RADIUS, contentSection[startIndex:])
            if radiusList:
                area += f'+{radiusList[0]}'
    return area

################################################################################################
def getMsaArea(contentSection) -> str:
    area = ''
    lastEnd = 0
    areas = []
    contentSection = contentSection.replace('N，', 'N')
    latlons = finditer(constants.MSA_PATTERN_LATITUDE_LONGITUDE, contentSection)
    for m in latlons:
        if lastEnd > 0 and m.start() > lastEnd + 4:
            areas.append(area)
            area = m.group()
        else:
            if area != '':
                area += '|'
            area += m.group()
        lastEnd = m.end()
    if area:
        areas.append(area)
    return areas

################################################################################################
def removeChars(d):
    return d.replace('-', '').replace(' ', '').replace(':', '')

################################################################################################
def getLocation(newFile):
    locations = readConfig(['Locations'], False)
    pattern = r'(' + locations.replace(',', '|') + ')'
    try:
        locs = findall(pattern, newFile)
    except:
        pass
    if locs:
        return locs[0], locations
    return None, locations

################################################################################################
# headersRow starts from 0
def readShipMoveData(excelFile, sheetName=None, skipRows=None, headers=None):
    if excelFile[-4:] == '.xls':
        oldExcelFile = excelFile
        excelFile = excelFile.replace('.xls', '.xlsx')
        import pyexcel as xls
        xls.save_book_as(file_name=oldExcelFile, dest_file_name=excelFile)
    import pandas as pd
    import numpy as np
    df = pd.read_excel(excelFile, sheetName, skiprows=skipRows, dtype={'速度': float}) # Convert the worksheet to a DataFrame
    df.replace('-', np.nan, inplace=True) # Replace '-' with NaN
    df.replace([None, np.nan], '', inplace=True) # Replace None with empty string
    df = df[df['速度'] > 1.0]
    return df


MSA_RADIUS_PATTERN = r'为中心、半径(\d{1,2})公里'
################################################################################################
def parseRadius(content):
    radiusMatch = findall(MSA_RADIUS_PATTERN, content)
    for m in radiusMatch:
        return int(m)
    
################################################################################################
def getNotamNumbers(content) -> tuple:
    numbers = finditer(constants.PATTERN_NOTAM_NUMBER_NEW, content)
    return [m.group(1) for m in numbers][0]

################################################################################################
def getNotamDates(content) -> tuple:
    # startDate = findall(constants.PATTERN_START_DATE, content)
    # if not startDate:
    #     startDate = findall(constants.PATTERN_START_DATE1, content)
    #     if not startDate:
    #         startDate = findall(constants.PATTERN_START_DATE2, content)
    #         if not startDate:
    #             startDate = []
    #             endDate = []
    #         else:
    #             endDate = findall(constants.PATTERN_END_DATE2, content)
    #     else:
    #         endDate = findall(constants.PATTERN_END_DATE1, content)
    # else:
    #     endDate = findall(constants.PATTERN_END_DATE, content)
    startDates = findall(constants.PATTERN_START_DATE, content)
    endDates = findall(constants.PATTERN_END_DATE, content)
    return startDates[0], endDates[0]

################################################################################################
def convertMonthToNumber(month:str):
    monthDict = {month: f'{index:02d}' for index, month in enumerate(month_abbr) if month}
    return monthDict[month.capitalize()]

################################################################################################
def convertTime(time, start=True):
    if start:
        t = '00:00' if not time else f'{time[:2]}:{time[2:]}'
    else:
        t = '23:59' if not time else f'{time[:2]}:{time[2:]}'
    return t

################################################################################################
def convertToDate(d: str):
    from dateutil import parser
    try:
        if len(d) == 4:
            d = f'{d}0101'
        elif len(d) == 6:
            d = f'{d}01'
        return parser.parse(d)
    except:
        myExcept.printExceptionTrace() 

################################################################################################
def getYYYYMMDD(year):
    if len(year) == 2:
        return '20' + year
    else:
        return year

################################################################################################
def getMsaDates(content: str) -> tuple:
    startDates, endDates = [], []
    startEndDates1 = [m for m in finditer(constants.MSA_PATTERN_DATE_CHINA, content)]
    startEndDates2 = [m for m in finditer(constants.MSA_PATTERN_DATE, content)]
    if startEndDates1:
        for m in startEndDates1:
            startYear = getJapanDate()[:4]
            startMonth = int(m.group(1)) if m.group(1) else ''
            startDay = int(m.group(2)) if m.group(2) else ''
            startTime = convertTime(m.group(3))
            endYear = startYear
            endMonth = int(m.group(4)) if m.group(4) else startMonth
            endDay = int(m.group(5)) if m.group(5) else startDay
            endTime = convertTime(m.group(6) if len(m.groups()) == 6 else '', False)
            if startYear and startMonth and startDay and startTime:
                startDate = f'{startYear}/{startMonth:02}/{int(startDay):02} {startTime}'
            if endYear and endMonth and endDay and endTime:
                endDate = f'{endYear}/{endMonth:02}/{endDay:02} {endTime}'
            startDates.append(startDate)
            endDates.append(endDate)
    elif startEndDates2:
        for m in startEndDates2:
            startDay = m.group(1) #convert to UTC+()
            startTime = convertTime(m.group(2)) #convert to UTC+()
            startMonth = m.group(3)
            startYear = m.group(4) if m.group(4) else getThisYear()
            endDay = m.group(5) #convert to UTC+()
            endTime = convertTime(m.group(6)) #convert to UTC+()
            endMonth = m.group(7)
            endYear = m.group(4) if m.group(4) else getThisYear()
            startDate = f'{startYear}/{startMonth:02}/{startDay:02} {startTime}'
            endDate = f'{endYear}/{endMonth:02}/{endDay:02} {endTime}'
            startDates.append(startDate)
            endDates.append(endDate)
    return startDates, endDates

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
    d1 = datetime.strptime(date1, "%Y年%m月%d日%H時%M分") - timedelta(hours=8)
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
def openConfig(section=None) -> tuple:
    config_ini = configparser.ConfigParser()
    config_ini.read('config.ini', encoding='utf-8')
    if section is None:
        section = 'DEFAULT'
    readSection = config_ini[section]
    return readSection

################################################################################################
def readConfigLaunchCenters() -> dict:
    section = openConfig()
    count = int(section.get('FirCount'))
    launchCenters = {}
    for i in range(count):
        firNames = section.get(f'FirName{i + 1}').replace('~KOREA', '').split(',')
        firLaunchCenters = section.get(f'FirLaunchCenter{i + 1}').split(',')
        launchCenters.update(dict(zip(firNames, firLaunchCenters)))
    return launchCenters

################################################################################################
def readConfigFirNames() -> str:
    section = openConfig()
    count = int(section.get('FirCount'))
    firNames = ''
    for i in range(count):
        if firNames:
            firNames += ' '
        firNames += section.get(f'FirName{i + 1}')
    firNames = firNames.replace(',', ' ').replace('~KOREA', '')
    return firNames

################################################################################################
def readConfigSeriesDictList():
    data = readConfig()
    seriesAll = data[5]
    seriesCZ = seriesAll[0]
    seriesNCZ = seriesAll[1]
    seriesCZRockets = seriesAll[2]
    seriesNCZRockets = seriesAll[3]
    # series = seriesAll[4]
    seriesList = []
    czList = seriesCZ.split(',')
    nczList = seriesNCZ.split(',')
    czRocketList = seriesCZRockets.split(',')
    nczRocketList = seriesNCZRockets.split(',')
    for cz, czRocket in zip(czList, czRocketList):
        czRockets = czRocket.split('|')
        seriesDict = {}
        for rocket in czRockets:
            seriesDict[rocket] = f'{cz}系列'
        seriesList.append(seriesDict)
    for ncz, nczRocket in zip(nczList, nczRocketList):
        nczRockets = nczRocket.split('|')
        seriesDict = {}
        for rocket in nczRockets:
            seriesDict[rocket] = f'{ncz}系列'
        seriesList.append(seriesDict)
    return seriesList

################################################################################################
def readConfigRetiredDict():
    data = readConfig()
    retiredData = data[4]
    retiredRockets = retiredData[2]
    retiredDates = retiredData[3]
    retiredDict = dict(zip(retiredRockets.split(','), retiredDates.split(',')))
    return retiredDict

################################################################################################
def readConfig(keys:list=None, returnList=True) -> tuple:
    read_default = openConfig()
    values = []

    if keys is None:
        values.append(read_default.get('ExcelFile'))
        values.append(read_default.get('SheetNames').split(','))
        values.append(read_default.get('Years'))
        rockets = []
        rockets.append(read_default.get('RocketsCZ'))
        rockets.append(read_default.get('RocketsNCZ'))
        rockets.append(read_default.get('Rockets'))
        values.append(rockets)
        retired = []
        retired.append(read_default.get('RetiredCZ'))
        retired.append(read_default.get('RetiredNCZ'))
        retired.append(read_default.get('Retired'))
        retired.append(read_default.get('RetiredDate'))
        values.append(retired)
        series = []
        series.append(read_default.get('SeriesCZ'))
        series.append(read_default.get('SeriesNCZ'))
        series.append(read_default.get('SeriesCZRockets'))
        series.append(read_default.get('SeriesNCZRockets'))
        series.append(read_default.get('Series'))
        values.append(series)
        values.append(read_default.get('Privates'))
        values.append(read_default.get('Locations'))
        values.append(read_default.get('Categories'))
        values.append(read_default.get('Payloads'))
        return values
    else:
        if returnList:
            valueList = []
            for key in keys:
                values = read_default.get(key)
                for value in values.split(','):
                    valueList.append(value)
            return valueList
        else:
            values = ''
            for key in keys:
                values += read_default.get(key)
            return values

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
    for command, _ in constants.COMMANDS.items():
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
def getColorFromKml(color):
    return f'#{color[6:8]}{color[4:6]}{color[2:4]}'

################################################################################################
def printDict(d, withQuotation=False, hasNo=True):
    for i, (key, value) in enumerate(d.items()):
        no = f'{i + 1:02} ' if hasNo else ''
        item = f'{no}"{key}": "{value}"' if withQuotation else f'{no}{key}: {value}'
        print(item)

################################################################################################
def printList(l):
    for i, value in enumerate(l):
        print(f'{i + 1:02} {value}')

################################################################################################
def removeAllSpaces(s):
    return ''.join(s.split())

################################################################################################
def isLinux() -> bool:
    if platform == "linux" or platform == "linux2":# linux
        return True
    elif platform == "darwin":# Mac OS X
        return False
    elif platform == "win32":# Windows
        return False

################################################################################################
def isWindows() -> bool:
    if platform == "linux" or platform == "linux2":# linux
        return False
    elif platform == "darwin":# Mac OS X
        return False
    elif platform == "win32":# Windows
        return True

################################################################################################
def isMacOS() -> bool:
    if platform == "linux" or platform == "linux2":# linux
        return False
    elif platform == "darwin":# macOS
        return True
    elif platform == "win32":# Windows
        return False

################################################################################################
def runCommand(command):
    try:
        ret = subprocess.run(command, encoding='utf8', check=True, shell=True, text = True, capture_output=True)
        return ret
    except subprocess.CalledProcessError as cpe:
        myExcept.printExceptionTrace()
        raise cpe

################################################################################################
def maxOfLists(lists):
    return max([max(sublist, default=float('-inf')) for sublist in lists])

################################################################################################
def getDDMM(ddmmss):
    ddmm = ''
    for ddmmssItem in ddmmss.split('-'):
        ddmm += '-' if ddmm != '' else ddmm
        if '|' in ddmmssItem:
            ddmmssList = ddmmssItem.split('|')
            ddmmList = [f'{dms[:7]},{dms[-11:-3]}' if len(dms.split('+')[0]) > 16 else dms for dms in ddmmssList]
            ddmm += '|'.join(ddmmList)
        else:
            plus = ddmmssItem.split('+')
            ddmm += f'{plus[0][:7]},{plus[0][-11:-3]}' if len(plus[0]) > 16 else plus[0]
            ddmm += '+' + plus[1] if len(plus) > 1 else ''
    return ddmm

################################################################################################
def getNotamDictString(d):
    msg = ''
    for i, (key, value) in enumerate(d.items()):
        items = value.split(';')
        msg += f'{i + 1:02}: {items[2]},{key[-8:]},{items[0]},{items[1]};{getDDMM(items[3])}\n'
    return msg[:-1]

################################################################################################
def splitNotam(item):
    items = item[1].split(';')
    return (items[0], items[1], -float(items[3].split('°')[0][1:]), items[2], item[0])

################################################################################################
def sortDictByValue(d: dict) -> dict:
    return {k : v for k, v in sorted(d.items(), key=lambda x: splitNotam(x))}

################################################################################################
def sortDictByEndDate(d: dict):
    sorted_tuples = sorted(d.items(), key=lambda item: item[1].split(";")[0][:10] + item[1].split(";")[1])
    sorted_dict = {k: v for k, v in sorted_tuples}
    return sorted_dict

################################################################################################
def sortDictByLatitude(d: dict):
    return {k : v for k, v in sorted(d.items(), key=lambda x: x[1])}

################################################################################################
def sortDictByKey(d: dict):
    return  {k : v for k, v in sorted(d.items(), key=lambda x: x[0])}

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
def getMimeTyoe(filename):
    import mimetypes
    mime = mimetypes.guess_type(filename)
    return mime

################################################################################################
def isTextFile(filename):
    mime = getMimeTyoe(filename)
    return mime[0] == 'text/plain'

################################################################################################
def isImageFile(filename):
    mime = getMimeTyoe(filename)
    return 'image' in mime[0] 

################################################################################################
def isAudioFile(filename):
    mime = getMimeTyoe(filename)
    return 'audio' in mime[0] 

################################################################################################
def isVideoFile(filename):
    mime = getMimeTyoe(filename)
    return 'video' in mime[0] 

################################################################################################
def isMediaFile(fileName):
    import mimetypes
    mimestart = mimetypes.guess_type(fileName)[0]
    if mimestart != None:
        mimestart = mimestart.split('/')[0]
        if mimestart in ['audio', 'video', 'image']:
            return True
    return False

################################################################################################
def swapListItems(swapList: list, swapIndex1: int, swapIndex2: int) -> list:
    swapList[swapIndex1], swapList[swapIndex2] = swapList[swapIndex2], swapList[swapIndex1]
    return swapList

################################################################################################
# TODO: remove selected files when re-enter this folder
def listFoldersFiles(curPath: str='.', extension: str='*.*'):
    oldPath = path.abspath(curdir)
    folders = listdir(curPath[:-1] if curPath.endswith('/') else curPath)
    chdir(curPath)
    dirList = sorted([f'{x}/' for x in folders if path.isdir(x)])
    fileList = sorted([x for x in folders if path.isfile(x)])
    result = dirList
    result.extend(fileList)

    if extension == '*.*':
        extSet = set(['*' + path.splitext(item)[1] if path.isfile(item) else '*.*' for item in result])
        extSet.add('*.*')
        extList = sorted(list(extSet))
        result.insert(0, '..')
        resultFiles = result
    else:
        if extension == '*':
            ext = ''
        else:
            ext = extension.replace('*', '')
        
        resultFiles = []
        for item in result:
            if path.splitext(item)[1] == ext:
                resultFiles.append(item)

        extSet = set(['*' + path.splitext(item)[1] if path.isfile(item) else '*.*' for item in result])
        extList = sorted(list(extSet))
        resultFiles.insert(0, '..')
    chdir(oldPath)
    return resultFiles, extList

################################################################################################
def parseFileInfo(filenameOrig: str): # filename='video/01.mp4'
    baseName = path.basename(filenameOrig)
    folderName = path.dirname(filenameOrig)
    absFolder = path.abspath(folderName)
    fileName = baseName[:-4]
    extension = baseName[-4:]
    fileInfo = FileInfo(filenameOrig, baseName, folderName, absFolder, fileName, extension)
    return fileInfo

################################################################################################
def isFloat(str):
    return str.replace(".", "").isnumeric()

################################################################################################
def listFiles(folder: str='.', extension: str=None, excludeFile=None, onlyFilename=False, includeSubFolder=True, prefix: str=None):
    absPath = path.abspath(folder)
    for root, dirs, files in walk(absPath):
        if not includeSubFolder and root != absPath:
            continue
        for file in files:
            if prefix != None and not findall(prefix, file):
                continue
            if extension == None or file.endswith(extension):
                if file != excludeFile:
                    filepath = file if onlyFilename else path.join(root, file) 
                    yield filepath
    
################################################################################################
def updateTempFile(notams: dict):
    filename = f'./data/notam{getJapanTimeFilename()}.txt'
    createFolder(filename)
    newText = f"NOTAM发射预测\n"
    newText += "================================\n"
    newText += getNotamDictString(notams)
    # for i, (key, value) in enumerate(notams.items()):
    #     items = value.split(';')
    #     newText += f'{i + 1:02}: {items[2]}/{key},{items[0]},{items[1]};{items[3]}\n'

    try:
        isNew = True
        oldFiles = listFiles('./data', '.txt')
        for oldFile in oldFiles:
            with open(oldFile, encoding='utf-8') as f:
                oldText = f.read()

            if oldText == newText:
                isNew = False
        if isNew:
            saveTextFile(filename, newText)
    except FileNotFoundError:
        saveTextFile(filename, newText)

################################################################################################
def getAge(born, ageYear=None):
    today = date.today() if ageYear == None else ageYear
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

################################################################################################
def saveTextFile(filename: str, newText: str, openFile=True, noSound=False, showMsg=True):
    if showMsg:
        print(f'Save to file "{filename}"')
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(newText)

    # Opening the text file in its default editor
    if isWindows() and openFile:
            system(f'start {filename}')
    if not noSound:
        if isWindows():
            playSound('Alarm03.wav')
        elif isMacOS():
            playSound('Alarm03.wav')
        elif isLinux():
            playSound('train.wav')

################################################################################################
def playSound(filename:str=None):
    if filename is None:
        if isWindows() or isMacOS():
            filename = 'Alarm03.wav'
        elif isLinux():
            filename = 'train.wav'
    if isWindows():
        path = 'C:/Windows/media/'
    elif isLinux():
        path = '//usr//lib//libreoffice//share//gallery//sounds//'
    elif isMacOS():
        path = '//Users//mikezang//music//'

    from playsound import playsound
    playsound(f'{path}{filename}')

################################################################################################
def updateNsfNotamJsonFile(nsf_new, filename):
    nsf_old = loadDictFromJsonFile(filename)

    if nsf_old is not None:
        for k, vNew in nsf_new.items():
            if k not in nsf_old:
                nsf_old[k] = vNew
            elif vNew is str:
                continue
            elif nsf_old[k] is str:
                nsf_old[k] = vNew
            elif nsf_old[k] != nsf_new[k]:
                nsf_old[k] = nsf_new[k]

        nsf_old = sortDictByKey(nsf_old)

        if nsf_old != nsf_new:
            saveDictToJsonFile(nsf_old, f"{filename}")
            saveDictToJsonFile(nsf_old, f'{filename}{getJapanTime("-%Y%m%d-%H%M%S")}')
        else:
            print(f'Not update to file "{filename}.json"')
    else:
        saveDictToJsonFile(nsf_new, f"{filename}")
        saveDictToJsonFile(nsf_new, f'{filename}{getJapanTime("-%Y%m%d-%H%M%S")}')

################################################################################################
def sortTwoLists(list1: list, list2: list, reverse=False):
    sortList2 = sorted(list2)
    sortList1 = [l1 for l1, _ in sorted(zip(list1, list2), reverse=reverse)]
    return sortList1, sortList2

################################################################################################
def updateDictToJsonFile(nsf_data, filename, isBackup=False):
    nsf_old = loadDictFromJsonFile(filename)

    if nsf_old is not None:
        nsf_new = nsf_old.copy()
        nsf_new.update(nsf_data)
        nsf_new = sortDictByKey(nsf_new)

        if nsf_old != nsf_new:
            saveDictToJsonFile(nsf_new, f"{filename}")
            if isBackup:
                saveDictToJsonFile(nsf_data, f'{filename}{getJapanTime("-%Y%m%d-%H%M%S")}')
        # else:
        #     print(f'Not update to file "{filename}.json"')
    else:
        saveDictToJsonFile(nsf_data, f"{filename}")
        if isBackup:
            saveDictToJsonFile(nsf_data, f'{filename}{getJapanTime("-%Y%m%d-%H%M%S")}')

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

################################################################################################
def isChinaNotam(condition):
    if condition.strip() == '':
        return False
    isChinaNotam = False
    section = openConfig()
    count = int(section.get('FirCount'))
    for i in range(count):
        withCondition = False
        firNames = section.get(f'FirName{i + 1}').split(',')
        firConditions = section.get(f'FirCondition{i + 1}').split(',')

        for name in firNames:
            names = name.split('~')
            hasName = names[0] in condition
            if len(names) == 2:
                hasName &= names[1] not in condition
            isChinaNotam |= hasName
    
        for cond in firConditions:
            withCondition |= cond in condition
        isChinaNotam &= withCondition
        if isChinaNotam:
            return isChinaNotam
    return isChinaNotam

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
def loadDictFromJsonFile(filename):
    try:
        with open(f'{filename}.json', encoding="utf-8") as f:
            print(f'Load from file "{filename}.json".')
            return load(f)
    except FileNotFoundError:
        return None

################################################################################################
def isPastTime(utcDate):
    localDate = convertToLocalDate(utcDate, "Asia/Tokyo")
    timeNow = datetime.now(timezone("Asia/Tokyo"))
    if timeNow >= localDate:
        return True
    else:
        return False

################################################################################################
def convertToLocalDate(utcDate, tz, isLocalTime=False):
    if not isLocalTime:
        utcDate1 = datetime.strptime(utcDate, "%Y/%m/%d %H:%M").replace(tzinfo=UTC)
    else:
        utcDate1 = datetime.strptime(utcDate, "%Y/%m/%d %H:%M").replace(tzinfo=timezone(tz))
    return utcDate1.astimezone(timezone(tz))

################################################################################################
def convertPatterns(s, p) -> str:
    if p == constants.PATTERN1:
        s = convertPattern1(s)
    elif p == constants.PATTERN3:
        s = convertPattern3(s)
    elif p == constants.PATTERN5:
        s = convertPattern5(s)
    elif p == constants.PATTERN6:
        s = convertPattern6(s)
    elif p == constants.PATTERN7:
        s = convertPattern7(s)
    return s

################################################################################################
#r'([NS]\d{4,6}E\d{5,7})
#N1234E12345
#012345678901234
#N123456E1234567
def convertPattern1(s):
    if len(s) == 15:
        return f"{s[0:3]}°{s[3:5]}'{s[5:7]}\",{s[7:11]}°{s[11:13]}'{s[13:15]}\""
    return f"{s[0:3]}°{s[3:5]}',{s[5:9]}°{s[9:11]}'"

################################################################################################
#r'(\d{4,6}[NS]\d{5,7}E)'
def convertPattern3(s):
    if len(s) == 21:
        #174800.00N1152300.00E
        return f"{s[9:10]}{s[0:2]}°{s[2:4]}'{s[4:6]}\",{s[20:21]}{s[10:13]}°{s[13:15]}'{s[15:17]}\""
    elif len(s) == 15:
        #174800N1152300E
        return f"{s[6:7]}{s[0:2]}°{s[2:4]}'{s[4:6]}\",{s[14:15]}{s[7:10]}°{s[10:12]}'{s[12:14]}\""
    if len(s) == 14:
        #174800N152300E
        return f"{s[6:7]}{s[0:2]}°{s[2:4]}'{s[4:6]}\",{s[13:14]}{s[7:9]}°{s[9:11]}'{s[11:13]}\""
    #1748N1523E
    return f"{s[4:5]}{s[0:2]}°{s[2:4]}',{s[10:11]}{s[5:8]}°{s[8:10]}'"

################################################################################################
#r'(\d{4,6}\.\d{1,2}[NS]\d{5,7}\.\d{1,2}E)'
def convertPattern5(s):
    if len(s) == 15:
        return f"{s[6:7]}{s[0:2]}°{s[2:4]}'{s[4:6]}\",{s[14:15]}{s[7:10]}°{s[10:12]}'{s[12:14]}\""
    if len(s) == 10:
        return f"{s[4:5]}{s[0:2]}°{s[2:4]}',{s[9:10]}0{s[5:7]}°{s[7:9]}'"
    return f"{s[4:5]}{s[0:2]}°{s[2:4]}',{s[10:11]}{s[5:8]}°{s[8:10]}'"

################################################################################################
#1234[NS]/12345E
#0123456789ABCDEF
#123456N/1234567E
def convertPattern6(s):
    if len(s) == 16:
        return f"{s[6:7]}{s[0:2]}°{s[2:4]}'{s[4:6]}\",{s[15:16]}{s[8:11]}'°{s[11:13]}'{s[13:15]}\""
    return f"{s[4:5]}{s[0:2]}°{s[2:4]}',{s[11:12]}{s[6:9]}°{s[9:11]}'"

################################################################################################
#0123456789012345678901
#37-42.4N120-10.8E
#18-18.60N118-09.46E
#37-42-46N120-10-98E
def convertPattern7(s):
    if len(s) == 19:
        if '.' in s:
            nSecond = str(int(s[6:8]) * 6 / pow(10, len(s[6:8]) - 1))[:2]
            eSecond = str(int(s[16:18]) * 6 / pow(10, len(s[16:18]) - 1))[:2]
            ret = f"{s[8:9]}{s[0:2]}°{s[3:5]}'{nSecond}\",{s[18:19]}{s[9:12]}°{s[13:15]}'{eSecond}\""
        else:
            ret =  f"{s[8:9]}{s[0:2]}°{s[3:5]}'{s[6:8]}\",{s[18:19]}{s[9:12]}°{s[13:15]}'{s[16:18]}\""
    elif len(s) == 21:
        nSecond = str(int(s[6:9]) * 6 / pow(10, len(s[6:9]) - 1))[:2]
        eSecond = str(int(s[17:20]) * 6 / pow(10, len(s[17:20]) - 1))[:2]
        ret =  f"{s[9]}{s[0:2]}°{s[3:5]}'{nSecond}\",{s[20]}{s[10:13]}°{s[14:16]}'{eSecond}\""
    elif len(s) == 13:
        ret =  f"{s[5:6]}{s[0:2]}°{s[3:5]}',{s[12:13]}{s[6:9]}°{s[10:12]}'"
    else:
        ret = f"{s[7:8]}{s[0:2]}°{s[3:5]}',{s[16:17]}{s[8:11]}°{s[12:14]}'"
    return ret

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

# A Python3 program to check if a given point lies inside a given polygon
# Refer
# https://www.geeksforgeeks.org/how-to-check-if-a-given-point-lies-inside-a-polygon/
# https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
# https://www.geeksforgeeks.org/orientation-3-ordered-points/amp/%C2%A0/
# for explanation of functions onSegment(), orientation() and doIntersect()
# Define Infinite (Using INT_MAX caused overflow problems)
# This code is contributed by Vikas Chitturi
INT_MAX = 10000

# Given three collinear points p, q, r,
# the function checks if point q lies on line segment 'pr'
################################################################################################
def pointOnSegment(p:tuple, q:tuple, r:tuple):
    if ((q[0] <= max(p[0], r[0])) & (q[0] >= min(p[0], r[0])) &
        (q[1] <= max(p[1], r[1])) & (q[1] >= min(p[1], r[1]))):
        return True
    return False

################################################################################################
# To find orientation of ordered triplet (p, q, r).
# The function returns following values
# 0 --> p, q and r are collinear
# 1 --> Clockwise
# 2 --> Counterclockwise
def pointOrientation(p:tuple, q:tuple, r:tuple):
    val = (((q[1] - p[1]) * (r[0] - q[0])) - ((q[0] - p[0]) * (r[1] - q[1])))
    if val == 0:
        return 0
    if val > 0:
        return 1 # Collinear
    else:
        return 2 # Clock or counterclock

################################################################################################
def pointDoIntersect(p1, q1, p2, q2):
    # Find the four orientations needed for general and special cases
    o1 = pointOrientation(p1, q1, p2)
    o2 = pointOrientation(p1, q1, q2)
    o3 = pointOrientation(p2, q2, p1)
    o4 = pointOrientation(p2, q2, q1)

    # General case
    if (o1 != o2) and (o3 != o4):
        return True

    # Special Cases
    if (o1 == 0) and (pointOnSegment(p1, p2, q1)):
        return True# p1, q1 and p2 are collinear and p2 lies on segment p1q1
    if (o2 == 0) and (pointOnSegment(p1, q2, q1)):
        return True# p1, q1 and p2 are collinear and q2 lies on segment p1q1
    if (o3 == 0) and (pointOnSegment(p2, p1, q2)):
        return True# p2, q2 and p1 are collinear and p1 lies on segment p2q2
    if (o4 == 0) and (pointOnSegment(p2, q1, q2)):
        return True# p2, q2 and q1 are collinear and q1 lies on segment p2q2
    return False

################################################################################################
# Returns true if the point p lies inside the polygon[] with n vertices
def pointIsInsidePolygon(p: tuple, points: list) -> bool:
    n = len(points)
    if n < 3:
        return False# There must be at least 3 vertices in polygon
    extreme = (INT_MAX, p[1])# Create a point for line segment from p to infinite
    decrease = 0# To count number of points in polygon whose y-coordinate is equal to y-coordinate of the point
    count = i = 0

    while True:
        nextPoint = (i + 1) % n
        if points[i][1] == p[1]:
            decrease += 1

        # Check if the line segment from 'p' to 'extreme' intersects with the line
        # segment from 'polygon[i]' to 'polygon[next]'
        if pointDoIntersect(points[i], points[nextPoint], p, extreme):
            # If the point 'p' is collinear with line segment 'i-next', then check if it lies
            # on segment. If it lies, return true, otherwise false
            if pointOrientation(points[i], p, points[nextPoint]) == 0:
                return pointOnSegment(points[i], p, points[nextPoint])
            count += 1
        i = nextPoint
        if i == 0:
            break

	# Reduce the count by decrease amount as these points would have been added twice
    count -= decrease
    return count % 2 == 1# Return true if count is odd, false otherwise

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
def parseNotamFromTextFile(filename):
    texts = []
    notam = {}
    lines = ''
    with open(filename, encoding='UTF-8') as f:
        for line in f:
            if line == '\n':
                texts.append(lines)
                lines = ''
            else:
                lines += line
        texts.append(lines)
    for text in texts:
        if isChinaNotam(text):
            notam = parseNotamText(notam, text)
    return notam

################################################################################################
def parseNotamText(notam, text):
    location, number, startDate, endDate, area = parseNotam(text)
    if location == 'RJJJ' and number.startswith('Q'):
        return notam
    if area != '':
        startDate = convertDate(startDate)
        endDate = convertDate(endDate)
        area = formatLatitudeLongitude(area)
        notam = getNoatmDict(notam, number, startDate, endDate, location, area)
    return notam

################################################################################################
def convertDate(oldDate) -> str:
    for pattern, fmt in constants.FORMAT_DATE.items():
        if search(pattern, oldDate):
            return datetime.strptime(oldDate, fmt).strftime("%Y/%m/%d %H:%M")
    return oldDate

################################################################################################
def formatLatitudeLongitude(oldData) -> str:
    newData = ''
    llListGroup = oldData.split('-')
    for ll in llListGroup:
        if newData != '':
            newData = newData[:-1] + '-'
        llList = ll.split('|')

        for oldll in llList:
            radius = oldll.split('+')
            newll = findConvertLatitudeLongitude(radius[0])
            if len(radius) == 2:
                newll += f'+{radius[1]}'
            newData += newll + '|'
    return newData[:-1]

################################################################################################
def parseNotam(text):
    location = getNotamLocation(text)
    numbers = getNotamNumbers(text)
    text = text.replace('\n', '').replace(' ', '')
    startDates, endDates = getNotamDates(text)
    area = getNotamArea(text)
    return location, numbers, startDates, endDates, area

################################################################################################
def getNoatmDict(notamDict, number, startDate, endDate, location, area):
    key = location + '/' + number
    if key in notamDict:
        items = notamDict[key].split(";")
        if startDate == items[0] and location != items[2]:
            location = items[2] + "/" + location
        c1 = [m.find(location) for m in notamDict.values()]
        c2 = [m.find(startDate) for m in notamDict.values()]
        c3 = [m.find(endDate) for m in notamDict.values()]
        if max(c1)>= 0 and max(c2) >= 0 and max(c3) >= 0:
            area1 = notamDict[key].split(";")[3]
            area = area1 + "-" + area if area != area1 else area
    notamDict[key] = startDate + ";"
    notamDict[key] = notamDict[key] + endDate + ";"
    notamDict[key] = notamDict[key] + location + ";"
    notamDict[key] = notamDict[key] + area
    return notamDict

################################################################################################
def parseMsa(text):
    location = 'MSA'
    number = getMsaLocation(text)
    text = text.replace('\n', '').replace(' ', '').replace('/', '').replace('、', ',')
    startDates, endDates = getMsaDates(text)
    areas = getMsaArea(text)
    return location, number, startDates, endDates, areas

################################################################################################
def formatMSALatitudeLongitude(oldData) -> str:
    newData = []
    # llListGroup = oldData.split('-')
    for data in oldData:
        oldllList = data.split('|')

        newllList = ''
        for oldll in oldllList:
            newll = findConvertLatitudeLongitude(oldll)
            newllList += newll + '|'
        newData.append(newllList[:-1])
    return newData

################################################################################################
def findConvertLatitudeLongitude(latlon):
    for p in constants.PATTERNS:
        if search(p, latlon):
            return convertPatterns(latlon, p)
    return latlon

###############################################################################################
def printNotam(dictData, start=''):
    print(f"\nNOTAM发射预测{start}")
    print("================================")
    print(getNotamDictString(dictData))
    print("================================")
    print(f"NOTAM发射预测{start}\n")

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

