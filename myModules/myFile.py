from datetime import datetime, timedelta
from glob import glob
from os import chdir, curdir, listdir, makedirs, path, remove, system, walk
from pathlib import Path
from re import sub
import subprocess
from typing import NamedTuple
import unicodedata
from pytz import timezone

from myModules import myConst
from myModules import myDate
from myModules import mySys

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
    if mySys.isWindows() and openFile:
        system(f'start {filename}')
    if not noSound:
        if mySys.isWindows():
            playSound('Alarm03.wav')
        elif mySys.isMacOS():
            playSound('Alarm03.wav')
        elif mySys.isLinux():
            playSound('train.wav')

################################################################################################
def getNotamListString(notams):
    msg = ''
    for i, notam in enumerate(notams, 1):
        maxLoc = 4
        for j, values in enumerate(notam, 1):
            for key, value in values.items():
                maxLoc = max(maxLoc, len(value.split(';')[2]))

        for j, values in enumerate(notam, 1):
            for key, value in values.items():
                items = value.split(';')
                loc = items[2].rjust(maxLoc)
                number = '/'.join(key.rsplit('/', 2)[1:]).rjust(8)
                startDate = items[0]
                endDate = items[1]
                area = myDate.getDDMM(items[3])
                msg += f'{i:02d}{chr(j + 64)}: {loc},{number},{startDate},{endDate};{area}\n'
        msg += '\n'
    return msg[:-2]

################################################################################################
def updateTempFile(notams: list):
    filename = f'{TEMP_FILE_PATH}notam{myDate.getJapanTimeFilename()}.txt'
    createFolder(filename)
    dataString = getNotamListString(notams)
    newText = f"NOTAM发射预测\n"
    newText += "================================\n"
    newText += dataString
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
    return isNew, dataString

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
def createFolder(filePath):
    folderPath = path.dirname(filePath)
    folder = Path(folderPath)
    if not folder.exists():
        makedirs(folder, exist_ok=True)

################################################################################################
def playSound(filename:str=None):
    if filename is None:
        if mySys.isWindows() or mySys.isMacOS():
            filename = 'Alarm03.wav'
        elif isLinux():
            filename = 'train.wav'
    if mySys.isWindows():
        path = 'C:/Windows/media/'
    elif mySys.isLinux():
        path = '//usr//lib//libreoffice//share//gallery//sounds//'
    elif mySys.isMacOS():
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
def readTextFile(filename, tripLinefeed=False, skipSharp=True):
    with open(filename, encoding='utf-8') as f:
        lines = []
        sharpLines = []
        if skipSharp:
            while line := f.readline():
                if line.startswith('#'):
                    sharpLines.append(line)
                else:
                    lines.append(line)
        else:
            lines = f.readlines()
        lines = [line.rstrip('\n') for line in lines] if tripLinefeed else lines
        sharpLines = [line.rstrip('\n') for line in sharpLines] if tripLinefeed else sharpLines
        return [convertToDiacritic(line) for line in lines], sharpLines

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
    if mySys.isWindows():
        return '^'
    else:
        return '\\'

################################################################################################
def convertTitle(utcStartDate, utcEndDate, city, city1=None, isLocalTime=False) -> str:
    city = city1 if city == '' else city
    if utcStartDate != '' and utcEndDate != '':
        startTime = myDate.convertToLocalDate(utcStartDate, isLocalTime=isLocalTime)
        lastEndTime = myDate.convertToLocalDate(utcEndDate, myConst.TIMEZONE_SHANGHAI, isLocalTime=isLocalTime)
        endTime = datetime(startTime.year, startTime.month, startTime.day, lastEndTime.hour, lastEndTime.minute)
        endTime = endTime + timedelta(days=1) if str(endTime) < str(startTime) else endTime 
        endTime = timezone(myConst.TIMEZONE_SHANGHAI).localize(endTime)
        launchTime = startTime + (endTime - startTime) / 3
        return f'{launchTime.strftime("%Y年%m月%d日%H时%M分")}{city}'
    else:
        return city

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
def getColorFromKml(color):
    return f'#{color[6:8]}{color[4:6]}{color[2:4]}'

################################################################################################
def getLastModifiedDate(filePath):
    file = Path(filePath)
    return datetime.fromtimestamp(file.stat().st_mtime)