import configparser
from datetime import datetime, timedelta
from glob import glob
from os import chdir, curdir, listdir, makedirs, path, remove, system, walk
from pathlib import Path
from re import findall, finditer, search, sub
import subprocess
from sys import platform
from typing import NamedTuple
import unicodedata
from pytz import timezone

from myModules import myConst
from myModules import myDate
from myModules import myDict

TEMP_FILE_PATH = './temp/'

class FileInfo(NamedTuple):
    origName: str   # 'videos/01.mp4'
    baseName: str   # basename='01.mp4'
    folderName: str # dirname='videos'
    absFolder: str  # abspath='C://zang/python/RocketLaunch/videos'
    fileName: str   # vfilename='01'
    extension: str  # extension='mp4'

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
def saveTextFile(filename: str, newText: str, openFile=True, noSound=False, showMsg=True):
    """Save string to text file.

    Args
    ___
        filename: String for text filename.
        newText: String to write to text file.
        openFile: Boolean if to open file after saved, default True
        noSound: Boolean if play sound after saved, default false
        showMsg: Boolean to show prompt before saving, default True

    Return
    ------
        None
    """
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
def updateTempFile(notams: dict):
    filename = f'{TEMP_FILE_PATH}notam{myDate.getJapanTimeFilename()}.txt'
    createFolder(filename)
    newText = f"NOTAM发射预测\n"
    newText += "================================\n"
    newText += myDict.getNotamDictString(notams)

    try:
        isNew = True
        oldFiles = glob(f'{TEMP_FILE_PATH}notam*.txt')
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
def listFiles(folder: str='.', extension: str=None, excludeFile=None, onlyFilename=False, includeSubFolder=True, prefix: str=None):
    absPath = path.abspath(folder)
    for root, dirs, files in walk(absPath):
        if not includeSubFolder and root != absPath:
            continue
        for file in files:
            # if prefix != None and not findall(prefix, file):
            if prefix != None and not file.startswith(prefix):
                continue
            if extension == None or file.endswith(extension):
                if file != excludeFile:
                    filepath = file if onlyFilename else path.join(root, file) 
                    yield filepath

################################################################################################
def listFilesByGlob(partOfFilename):
    return glob(partOfFilename)

################################################################################################
def createFolder(filePath):
    folderPath = path.dirname(filePath)
    folder = Path(folderPath)
    if not folder.exists():
        makedirs(folder, exist_ok=True)

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
def readTextFile(filename, tripLinefeed=False):
    with open(filename, encoding='utf-8') as f:
        lines = [line.rstrip('\n') for line in f.readlines()] if tripLinefeed else f.readlines()
        return [convertToDiacritic(line) for line in lines]

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
def saveListToTextFile(filename, dataList):
    lines = ''
    with open(filename, 'w', encoding="utf-8") as f:
        for line in dataList:
            lines += f'{line}\n'
        f.write(lines)
        print(f'Save dict to "{path.abspath(filename)}"')

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
def getFileDuration(filename: str) -> float:
    if not isVideoFile(filename) and not isAudioFile(filename):
        print(f'{filename} is not Audio/Video file!')
        return 0
    cmd = f"ffprobe -v fatal -show_entries format=duration -of default=nw=1:nk=1 {filename}"
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return float(result.stdout)

################################################################################################
def keepOneLineChar():
    if isWindows():
        return '^'
    else:
        return '\\'

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
    firNames = '' #readConfigFirNames().split()
    firLaunchCenters = ''
    section = openConfig()
    count = int(section.get('FirCount'))
    for i in range(count):
        firNames += section.get(f'FirName{i + 1}') + ','
        firLaunchCenters += section.get(f'FirLaunchCenter{i + 1}') + ','
    launchCenters = (dict(zip(firNames.split(','), firLaunchCenters.split(','))))
    return launchCenters

################################################################################################
def readConfigFirNames() -> str:
    section = openConfig()
    count = int(section.get('FirCount'))
    firNames = ''
    for i in range(count):
        firName = section.get(f'FirName{i + 1}')
        firName = ' '.join([x.split('~')[0] for x in firName.split(',')])
        if firNames:
            firNames += ' '
        firNames += firName
    return firNames

################################################################################################
def readConfig(keys=None, returnList=True) -> tuple:
    read_default = openConfig()
    values = []

    if keys is None:
        values.append(read_default.get('ExcelFile'))
        # values.append(read_default.get('SheetLaunch'))
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
        keys = [keys] if isinstance(keys, str) else keys
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
def getLocation(newFile):
    locations = readConfig(['Locations'], False)
    pattern = r'(' + locations.replace(',', '|') + ')'
    try:
        locs = findall(pattern, newFile.split('\\')[-1])
    except:
        pass
    if locs:
        if locs[0] == '文昌':
            locs.append('海南') 
        if locs[0] == '海南':
            locs.append('文昌') 
        return locs, locations
    return None, locations

################################################################################################
def convertTitle(utcStartDate, utcEndDate, loc, loc1=None, isLocalTime=False) -> str:
    loc = loc1 if loc == '' else loc
    if utcStartDate != '' and utcEndDate != '':
        startTime = myDate.convertToLocalDate(utcStartDate, myConst.TIMEZONE_SHANGHAI, isLocalTime=isLocalTime)
        lastEndTime = myDate.convertToLocalDate(utcEndDate, myConst.TIMEZONE_SHANGHAI, isLocalTime=isLocalTime)
        endTime = datetime(startTime.year, startTime.month, startTime.day, lastEndTime.hour, lastEndTime.minute)
        endTime = endTime + timedelta(days=1) if str(endTime) < str(startTime) else endTime 
        endTime = timezone(myConst.TIMEZONE_SHANGHAI).localize(endTime)
        launchTime = startTime + (endTime - startTime) / 3
        return f'{launchTime.strftime("%Y年%m月%d日%H时%M分")}{loc}'
    else:
        return loc

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
def convertPatterns(s, p) -> str:
    if p == myConst.PATTERN1:
        s = convertPattern1(s)
    elif p == myConst.PATTERN3:
        s = convertPattern3(s)
    elif p == myConst.PATTERN5:
        s = convertPattern5(s)
    elif p == myConst.PATTERN6:
        s = convertPattern6(s)
    elif p == myConst.PATTERN7:
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
def removeAllSpaces(s):
    return ''.join(s.split())

################################################################################################
# TODO: remove selected files when re-enter this folder
def listFoldersFiles(curPath: str='.', extension: str='*.*'):
    if not path.isdir(curPath):
        makedirs(curPath)
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
def readConfigRetiredDict():
    retiredRockets = readConfig('Retired')
    retiredDates = readConfig('RetiredDate')
    retiredDict = dict(zip(retiredRockets, retiredDates))
    return retiredDict

################################################################################################
def readConfigSeriesDictList():
    czList = readConfig('SeriesCZ')
    nczList = readConfig('SeriesNCZ')
    czRocketList = readConfig('SeriesCZRockets')
    nczRocketList = readConfig('SeriesNCZRockets')
    seriesList = []
    for cz, czRocket in zip(czList, czRocketList):
        czRockets = czRocket.split('+')
        seriesDict = {}
        for rocket in czRockets:
            seriesDict[rocket] = f'{cz}系列'
        seriesList.append(seriesDict)
    for ncz, nczRocket in zip(nczList, nczRocketList):
        nczRockets = nczRocket.split('+')
        seriesDict = {}
        for rocket in nczRockets:
            seriesDict[rocket] = f'{ncz}系列'
        seriesList.append(seriesDict)
    return seriesList

################################################################################################
def getColorFromKml(color):
    return f'#{color[6:8]}{color[4:6]}{color[2:4]}'

################################################################################################
def getLastModifiedDate(filePath):
    file = Path(filePath)
    return datetime.fromtimestamp(file.stat().st_mtime)