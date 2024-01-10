"""
    This is a utilities module.
"""
# pylint: disable=W0603,W0622,W0703,C0103,C0116,C0301,E1101

import logging
import socket
import pytz
import inspect
import zipfile
import calendar
import ctypes
import configparser
import geopandas as gpd
import matplotlib.pyplot as plt
from time import sleep
from re import compile, findall, finditer, match, search#, sub, IGNORECASE
from pathlib import Path
from numpy import zeros
from simplekml import Kml
from json import dump, load
from sys import argv, platform, exc_info
from datetime import datetime, timedelta
from os import path, remove, system, walk, mkdir
from glob import glob
from math import radians, cos, sin, asin, sqrt, atan2, degrees, pow
from fiona.drvsupport import supported_drivers
from shapely.ops import transform
from shapely.geometry import Point, Polygon
from pyproj import Transformer, CRS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox import service as fs
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions

import constants
import myPlot
import notam
import nsf

isFirstTime = True
NSF_PATH = './notams/maps/nsf/'
KML_PATH = './temp/'

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
        mkdir(folder)

################################################################################################
def getLastdayOfMonth(year, month):
    return calendar.monthrange(int(year), int(month))[1]

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
                if k in d1 and k in d2 and d1[k] != d2[k]
                else d1[k] if k in d1 else d2[k])
            for k in set(d1).union(d2)}

################################################################################################
def getJapanTimeFilename(fmt='') -> str:
    if fmt == '':
        fmt = "%Y%m%d-%H%M%S"
    return datetime.now(pytz.timezone(constants.TIMEZONE_TOKYO)).strftime(fmt)

def getJapanTime(fmt='') -> str:
    if fmt == '':
        fmt = "%Y/%m/%d %H:%M:%S"
    return datetime.now(pytz.timezone(constants.TIMEZONE_TOKYO)).strftime(fmt)

def getUTCTime(fmt='') -> str:
    if fmt == '':
        fmt = "%Y/%m/%d %H:%M:%S"
    return datetime.now(pytz.timezone('UTC')).strftime(fmt)

################################################################################################
def getThisYear():
    return getJapanDate()[:4]

################################################################################################
def getJapanDate(fmt='') -> str:
    if fmt == '':
        fmt = "%Y%m%d"
    return datetime.now(pytz.timezone(constants.TIMEZONE_TOKYO)).strftime(fmt)

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
def convertTitle(utcStartDate, utcEndDate, loc, loc1=None) -> str:
    loc = loc1 if loc == '' else loc
    if utcStartDate != '' and utcEndDate != '':
        startTime = convertToLocalDate(utcStartDate, constants.TIMEZONE_BEIJING)
        lastEndTime = convertToLocalDate(utcEndDate, constants.TIMEZONE_BEIJING)
        endTime = datetime(startTime.year, startTime.month, startTime.day, lastEndTime.hour, lastEndTime.minute)
        endTime = endTime + timedelta(days=1) if str(endTime) < str(startTime) else endTime 
        endTime = pytz.timezone(constants.TIMEZONE_BEIJING).localize(endTime)
        launchTime = startTime + (endTime - startTime) / 3
        return f'{launchTime.strftime("%Y年%m月%d日%H時%M分")}{loc}'
    else:
        return loc
    # return f'{convertToLocalDate(utcStartDate, constants.TIMEZONE_BEIJING).strftime("%Y年%m月%d日%H時%M分")}{loc}'

################################################################################################
def getAreaCenter(coordsList) -> list:
    lat, lon = zip(*[(l[0], l[1]) for l in coordsList if l])
    lats, lons = sum(lat)/len(lat), sum(lon)/len(lon)
    return [lats + 180 if lats < 0 and lats > -10 else lats, lons]

################################################################################################
def getCityCoordinate(city) -> list:
    p1s = constants.CITIES[city].split('|')[1].split(',')
    return [p1s[0], p1s[1]]

################################################################################################
def getConditionDetail(driver, tdCondition) -> str:
    tdCondition.click()
    sleep(1)
    condition = elementXPath(driver, 30, constants.XPATH_SPAN_DETAIL).text
    index = condition.index("E)")
    if index:
        condition = condition[(index + 3):] # exclude 'E) '
    driver.back()
    return condition

#N16°33',E093°17'
#N16°33'44",E093°17'66"
#Decimal degrees	            +-50.91721,      +-5.91775
#Decimal degrees	            NS50.91721°,    EW5.91775°
#Degrees and decimal minutes	NS50°55.032',   EW5°55.065'
#Degrees, minutes and seconds	NS50°55'1.956'',EW5°55'3.9''
#Degrees, minutes and seconds	NS505501,        EW0055503
################################################################################################
def convertDMS2DD(old) -> list:
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

################################################################################################
def getMsaLocation(content) -> str:
    location = finditer(constants.MSA_PATTERN_NUMBER, content)
    for m in location:
        return m.group()
    else:
        return ''

################################################################################################
def getNsfLocation(content) -> str:
    firNames = readConfigFirNames()
    pattern = getFirRegExPattern(firNames)
    # pattern = getFirRegExPattern(constants.FIR_LOCATIONS)
    locations = finditer(pattern, content)
    # locations = finditer(constants.PATTERN_LOCATION_ONLY, content)
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
    firNames = readConfigFirNames()
    pattern = getFirRegExPattern(firNames)
    # pattern = getFirRegExPattern(constants.FIR_LOCATIONS)
    locations = finditer(pattern, content)
    # locations = finditer(constants.PATTERN_LOCATION_ONLY, content)
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
    return area

################################################################################################
def getMsaArea(contentSection) -> str:
    area = ''
    lastEnd = 0
    areas = []
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
def createKmlFileNew(notams: dict, title1='', city1='') -> None:
    notamFiles = devideToFiles(notams)

    kml = Kml()
    lastStartDate = ''
    lastEndDate = ''
    lastCity = ''
    highestPoint = []
    lowestPoint = []
    coordsList = []
    coordsDict = {}

    for number, item in notams.items():
        itemArray = item.split(';')
        startDate = itemArray[0]
        endDate = itemArray[1]
        loc = itemArray[2]
        city = convertLocation(itemArray[2]) if city1 == '' else city1
        coordsArray = itemArray[3].split('-')

        # plot range with all coords for special case
        if len(coordsArray) > 1:
            coordsAll = itemArray[3].replace('-', '|')
            coordsArray.append(coordsAll)

        for arr in coordsArray:
            coords = arr.split('|')
            # if len(coords) == 5: coords.pop(0)
            coordsList = [convertDMS2DD(c) for c in coords]

            if lastStartDate == '' or isNearTime(lastStartDate, startDate, 59):
                # if len(coordsList) > 2:
                coords = drawStages(kml, coordsList, city, f'{loc}/{number}')
                coordsDict[f'{loc}/{number}'] = coordsList
                if loc == 'MSAC' or len(coordsList) > 3:
                    lastCity, highestPoint, lowestPoint = getFirstLastPoint(lowestPoint, highestPoint, coords, lastCity, city)
            else:
                drawRoutes(kml, lastCity, highestPoint, lowestPoint)
                title = convertTitle(lastStartDate, lastEndDate, lastCity, city) if title1 == '' else title1
                updateKmlFile(kml, title, KML_PATH)
                highestPoint = []

                kml = Kml()
                # if len(coordsList) > 2:
                coords = drawStages(kml, coordsList, city, f'{loc}/{number}')
                if loc == 'MSAC' or len(coordsList) > 3:
                    lastCity, highestPoint, lowestPoint = getFirstLastPoint(lowestPoint, highestPoint, coords, lastCity, city)
            lastStartDate = startDate
            lastEndDate = endDate

    drawRoutes(kml, lastCity, highestPoint, lowestPoint)
    title = convertTitle(lastStartDate, lastEndDate, lastCity, city) if title1 == '' else title1
    updateKmlFile(kml, title, KML_PATH)

################################################################################################
def removeChars(d):
    return d.replace('-', '').replace(' ', '').replace(':', '')

################################################################################################
def getLocation(newFile):
    locations = readConfig(['Locations'], False)
    pattern = r'(' + locations.replace(',', '|') + ')'
    locs = findall(pattern, newFile)
    if locs:
        return locs[0], locations
    return None, locations

################################################################################################
def createShipTrackLinesKmlFile(newFile):
    df = myPlot.readShipMoveData(newFile, '船舶轨迹', headersRow=1)
    mmsiKey = df['mmsi'].iloc[0]
    startDate = removeChars(df['时间'].iloc[0])[:12]
    endDate = removeChars(df['时间'].iloc[-1])[:12]
    mmsi, shipName = readConfig(['LaunchShipMMSI', 'LaunchShipName'])
    shipNameDict = dict(zip(mmsi.split(','), shipName.split(',')))
    shipName = shipNameDict[mmsiKey] if mmsiKey in shipNameDict else f'MMSI{mmsiKey}'
    # title = f'{startDate}-{endDate}-{shipName}-航迹'
    title = f'{endDate[:4]}年{endDate[4:6]}月{endDate[6:8]}日{endDate[8:10]}时{endDate[10:12]}分{shipName}航迹'
    coords = df[['经度', '纬度']].values.tolist()
    kml = Kml()
    drawLine(kml, coords, shipName)
    updateKmlFile(kml, title, KML_PATH)

################################################################################################
def createMsaDropZonesKmlFile(oldFile):
    with open(oldFile, encoding='utf-8') as f:
        content = f.read()

    if content:
        lines = content.split('\n')
        content = ''
        for line in lines:
            if line != '' and line[0:1] != '#':
                content += line
        location, number, startDates, endDates, areas = notam.parseMsa(content)

        for startDate, endDate, area in zip(startDates, endDates, areas):
            kml = Kml()
            notams = {}
            startDate = startDate if startDate else getUTCTime()[:-3]
            endDate = endDate if endDate else getUTCTime()[:-3]
            title = f"{oldFile.replace('.txt', '').split('/')[-1]}"
            title = convertTitle(startDate, endDate, title)
            if area:
                area = nsf.formatMSALatitudeLongitude([area])[0]
            # for area in areas:
                coords = area.split('|')
                coordsList = [convertDMS2DD(c) for c in coords]
                if len(coordsList) == 1:
                    drawCircle(kml, coordsList, f'{location}/{number}')
                else:
                    drawPolygon(kml, coordsList, f'{location}/{number}')
                notams = notam.getNoatmDict(notams, number, startDate, endDate, location, area)
            updateKmlFile(kml, title, KML_PATH, notams)

################################################################################################
def getNotamNumbers(content) -> list:
    numbers = finditer(constants.PATTERN_NOTAM_NUMBER_NEW, content)
    return [m.group(1) for m in numbers][0]

################################################################################################
def createKmlFile(notams, title1='', city1='') -> None:
    kml = Kml()
    lastStartDate = ''
    lastEndDate = ''
    lastCity = ''
    highestPoint = []
    lowestPoint = []
    coordsList = []
    seaCoord = {}

    for number, item in notams.items():
        itemArray = item.split(';')
        startDate = itemArray[0]
        endDate = itemArray[1]
        loc = itemArray[2]
        city = convertLocation(itemArray[2]) if city1 == '' else city1
        coordsArray = itemArray[3].split('-')

        # plot range with all coords for special case
        if len(coordsArray) > 1:
            coordsAll = itemArray[3].replace('-', '|')
            coordsArray.append(coordsAll)

        for arr in coordsArray:
            coords = arr.split('|')
            # if len(coords) == 5: coords.pop(0)
            coordsList = [convertDMS2DD(c) for c in coords]

            if lastStartDate == '' or isNearTime(lastStartDate, startDate, 59):
                # if len(coordsList) > 2:
                coords = drawStages(kml, coordsList, city, f'{loc}/{number}')
                if loc == 'MSAC' or len(coordsList) > 3:
                    lastCity, highestPoint, lowestPoint = getFirstLastPoint(lowestPoint, highestPoint, coords, lastCity, city)
                if len(coordsList) == 1:
                    seaCoord['海上']= coordsList[0]
            else:
                drawRoutes(kml, lastCity, highestPoint, lowestPoint, seaCoord)
                title = convertTitle(lastStartDate, lastEndDate, lastCity, city) if title1 == '' else title1
                updateKmlFile(kml, title, KML_PATH, notams)
                highestPoint = []
                seaCoord = {}

                kml = Kml()
                # if len(coordsList) > 2:
                coords = drawStages(kml, coordsList, city, f'{loc}/{number}')
                if loc == 'MSAC' or len(coordsList) > 3:
                    lastCity, highestPoint, lowestPoint = getFirstLastPoint(lowestPoint, highestPoint, coords, lastCity, city)
                if len(coordsList) == 1:
                    seaCoord['海上']= coordsList[0]
            lastStartDate = startDate
            lastEndDate = endDate

    drawRoutes(kml, lastCity, highestPoint, lowestPoint, seaCoord)
    title = convertTitle(lastStartDate, lastEndDate, lastCity, city) if title1 == '' else title1
    updateKmlFile(kml, title, KML_PATH, notams)

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
    monthDict = {month: f'{index:02d}' for index, month in enumerate(calendar.month_abbr) if month}
    return monthDict[month.capitalize()]

################################################################################################
def convertTime(time):
    return '00:00' if time == '' else f'{time[:2]}:{time[2:]}'

def getYYYYMMDD(year):
    if len(year) == 2:
        return '20' + year
    else:
        return year

################################################################################################
def getMsaDates(content) -> tuple:
    startDates, endDates = [], []
    startEndDates = finditer(constants.MSA_PATTERN_DATE, content)
    for m in startEndDates:
        startDay = m.group(1)
        startTime = convertTime(m.group(2))
        startMonth = m.group(3)
        startYear = getJapanDate()[:4] if m.group(4) == '' else getYYYYMMDD(m.group(4))
        endDay = m.group(5)
        endTime = convertTime(m.group(6))
        endMonth = convertMonthToNumber(m.group(7))
        endYear = getJapanDate()[:4] if m.group(8) == '' else getYYYYMMDD(m.group(8))
        startMonth = endMonth if startMonth == '' else convertMonthToNumber(startMonth)
        endTime = endTime if endTime != '00:00' else '23:59'
        startDate = f'{startYear}/{startMonth}/{startDay.zfill(2)} {startTime}'
        endDate = f'{endYear}/{endMonth}/{endDay.zfill(2)} {endTime}'
        startDates.append(startDate)
        endDates.append(endDate)
    return startDates, endDates

################################################################################################
def createNsfKmlFile(title, notams) -> None:
    kml = Kml()
    lastCity = ''
    highestPoint = ()
    lowestPoint = ()

    #2022年10月09日07時43分酒泉長征二号丁
    #01234 567 890 123 456 7 8 9 0 1 2 3
    launchTime, city, _ = title[:17], title[17:19], title[19:]
    _, notamList = notams[0], notams[1]
    usedCoordinates = set()

    for _, item in notamList.items():
        itemArray = item.split(';')
        startDate = itemArray[0]
        endDate = itemArray[1]
        coordinates = itemArray[3]
        if startDate != '' and coordinates not in usedCoordinates and isNsfNearTime(launchTime, startDate, endDate, 600):
            loc = itemArray[2]
            coordsGroups = coordinates.split('-')
            for coordGroup in coordsGroups:
                usedCoordinates.add(coordGroup)
                coords = coordGroup.split('|')
                coordsList = [convertDMS2DD(c) for c in coords]
                coords = drawStages(kml, coordsList, city, loc)
                if loc == 'MSAC' or len(coordsList) > 3:
                    lastCity, highestPoint, lowestPoint = getFirstLastPoint(lowestPoint, highestPoint, coords, lastCity, city)

    drawRoutes(kml, lastCity, highestPoint, lowestPoint)
    updateKmlFile(kml, f'{title}', NSF_PATH)

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
def createFirBoundaryKmlFile(title, boundary):
    kml = Kml()
    for city, coordinates in boundary.items():
        if coordinates:
            pol = kml.newpolygon(name=city)
            res = [(sub[1], sub[0]) for sub in coordinates]
            pol.outerboundaryis = res
            pol.style.polystyle.outline = 1
    updateKmlFile(kml, title, NSF_PATH)

################################################################################################
def hasCoordinates(city) -> bool:
    if city != '':
        lat, lon = getCityCoordinate(city)
        if isinstance(lat, float) and isinstance(lon, float):
            return True
    return False

################################################################################################
#coords(lon経度, lat緯度)
def getFirstLastPoint(lowestPoint, highestPoint, coords, lastCity, city) -> tuple:
    p2 = getAreaCenter(coords)
    if not highestPoint:
        return city, p2, p2
    else:
        p0, p1 = lowestPoint, highestPoint

        if p2[1] > p1[1]:
            highestPoint, lastCity = p2, city
        if p2[1] < p0[1]:
            lowestPoint = p2
        return lastCity, highestPoint, lowestPoint

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
def drawStages(kml, coords, city, location) -> None:
    if coords:
        cities = [city[i:i + 2] for i in range(0, len(city), 2)]
        count = len(coords)
        for c in cities:
            color = constants.CITIES[c].split('|')[2]
            if count == 1:
                drawCircle(kml, coords, location, color, 10.0)
            elif count == 2:
                drawLine(kml, coords, location, color)
            else: #if  location == 'MSAC':
                lon1, lat1, lon2, lat2 = coords[0][0], coords[0][1], coords[-1][0], coords[-1][1]
                distance = haversine(lon1, lat1, lon2, lat2)
                if distance < 150 or location != 'MSAC': # distance less than 150km between first and last point
                    drawPolygon(kml, coords, location, color)
                else:
                    drawLine(kml, coords, location, color)
            break
    return coords

################################################################################################
# distance in kilo metres
def drawCircle(kml, coords, location, color=constants.COLOR_SEA, radius=5):
    circle = circleByPoint(coords[0][1], coords[0][0], radius)
    # circle = [(lon, lat) for lat, lon in buffer]
    drawPolygon(kml, circle, location, color)

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
def drawDottedLine(kml, coords, location, color) -> None:
    for i in range(len(coords) - 1):
        for j in range(1, len(coords)):
            coordsDiff = [(coords[j][0] - coords[i][0]) / 50, (coords[j][1] - coords[i][1]) / 50]
            for k in range(0, 50, 2):
                lat1, lon1 = coords[i][0] + coordsDiff[0] * k, coords[i][1] + coordsDiff[1] * k
                lat2, lon2 = lat1 + coordsDiff[0], lon1 + coordsDiff[1]
                dotted = ((lat1, lon1), (lat2, lon2))
                drawLine(kml, dotted, location, color)

################################################################################################
def openConfig(section=None) -> list:
    config_ini = configparser.ConfigParser()
    config_ini.read('config.ini', encoding='utf-8')
    if section is None:
        section = 'DEFAULT'
    readSection = config_ini[section]
    return readSection

################################################################################################
def readConfigLaunchCenters():
    section = openConfig()
    count = int(section.get('FirCount'))
    launchCenters = {}
    for i in range(count):
        firNames = section.get(f'FirName{i + 1}').replace('~KOREA', '').split(',')
        firLaunchCenters = section.get(f'FirLaunchCenter{i + 1}').split(',')
        launchCenters.update(dict(zip(firNames, firLaunchCenters)))
    return launchCenters

################################################################################################
def readConfigFirNames():
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
def readConfig(keys:list=None, returnList=True) -> list:
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
def drawLine(kml, coords, location=None, color=None) -> None:
    line = kml.newlinestring(name=location)
    line.coords = coords
    line.style.linestyle.color = color if color is not None else constants.COLOR_SEA
    line.style.linestyle.width = 1

################################################################################################
def drawPolygon(kml, coords, location, color=None) -> None:
    pol = kml.newpolygon(name=location)
    pol.outerboundaryis = coords
    pol.style.polystyle.color = color if color is not None else constants.COLOR_SEA
    pol.style.polystyle.outline = 0

################################################################################################
def drawRoutes(kml, city, highestPoint, lowestPoint=None, seaCoord=None) -> None:
    cities = [city[i:i + 2] for i in range(0, len(city), 2)]
    if seaCoord:
        cities.append('海上')

    for c in cities:
        if c == '海上':
            cityCoord = seaCoord[c]
        else:
            cityCoord = getCityCoordinate(c)

        if len(highestPoint) == 0:
            highestPoint = lowestPoint

        if cityCoord[0] == '' or cityCoord[1] == '':
            cityCoord = highestPoint
        
        lon0, lat0 = map(float, cityCoord)
        lon1, lat1 = map(float, highestPoint)
        lon2, lat2 = map(float, lowestPoint)

        if highestPoint == lowestPoint:
            lon1, lat1 = lon0, lat0

        # bearingRoute = great_circle_bearing(lat0, lon0, lat2, lon2)
        # bearingRange = great_circle_bearing(lat1, lon1, lat2, lon2)
        # if abs(bearingRoute - bearingRange) < 5.0:
        angle = great_circle_angle(lat0, lon0, lat2, lon2)
        if (lon0, lat0) == (lon1, lat1):
            lastPoint = great_circle_point(lat0, lon0, lat2, lon2, fromSea=True)
        elif angle > 90:
            lastPoint = great_circle_point(lat0, lon0, lat2, lon2, distance=None)
        else:
            lastPoint = great_circle_point(lat0, lon0, lat2, lon2)
        
        # angle = 90 - angle if angle < 90 else angle 
        ls = kml.newlinestring(name=f'{c}{angle:.1f}°轨道')
        ls.style.linestyle.color = 'ff000000'
        ls.style.linestyle.width = 1
        ls.coords = [cityCoord, lastPoint]

        # change all polygon or linestyle color
        color = constants.CITIES[c].split('|')[2]
        for feature in kml.features:
            feature.style.polystyle.color = color
            # feature.style.linestyle.color = color

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
def isVPN(show=False) -> bool:
#    ip = socket.gethostbyname(socket.gethostname())
    ip = getLocalIp()

    if '192.168.' in ip or '100.' in ip or '172.16' in ip:
        if show:
            print(f"VPN Off (ip: {ip})\n")
        return False
    else:
        if show:
            print(f"VPN On (ip: {ip})\n")
        return True

################################################################################################
def passProxy(driver) -> None:
    try:
        elementInput(driver, 20, constants.XPATH_INPUT_USERNAME, constants.PROXY_ID)
        elementClick(driver, 5, constants.XPATH_INPUT_SUBMIT)
        elementInput(driver, 20, constants.XPATH_INPUT_PASSWORD, constants.PROXY_PW)
        elementClick(driver, 5, constants.XPATH_INPUT_SUBMIT)
        sleep(5)
    except Exception as e:
        print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
        pass

################################################################################################
def getLocalIp() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

################################################################################################
def checkVPN(driver) -> None:
    global isFirstTime

    if isFirstTime:
        isFirstTime = False
        if isVPN(False):
            passProxy(driver)

################################################################################################
def getFirefoxDriver(log=False) -> webdriver:
    options = FirefoxOptions()
    if constants.HEADLESS == 1:
        options.headless = True
        options.add_argument('--headless')
        # options.log.level = "trace"
    if log is False:
        service = fs.Service(log_path=path.devnull)
        driver = webdriver.Firefox(options=options, service=service)
        # driver = webdriver.Firefox(options=options)
    else:
        driver = webdriver.Firefox(options=options)
    return driver

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
def printDict(d):
    for i, (key, value) in enumerate(d.items()):
        print(f'{i + 1:02} {key}:{value}')

################################################################################################
def printList(l):
    for i, value in enumerate(l):
        print(f'{i + 1:02} {value}')

################################################################################################
def removeAllSpaces(s):
    return ''.join(s.split())

################################################################################################
def isLinux():
    if platform == "linux" or platform == "linux2":# linux
        return True
    elif platform == "darwin":# Mac OS X
        return False
    elif platform == "win32":# Windows
        return False

################################################################################################
def isWindows():
    if platform == "linux" or platform == "linux2":# linux
        return False
    elif platform == "darwin":# Mac OS X
        return False
    elif platform == "win32":# Windows
        return True

################################################################################################
def isMacOS():
    if platform == "linux" or platform == "linux2":# linux
        return False
    elif platform == "darwin":# macOS
        return True
    elif platform == "win32":# Windows
        return False

################################################################################################
# def runCommand(command):
#     if isWindows():
#         ret4 = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
#     else:
#         ret4 = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

#     if ret4.stdout:
#         retOutput = ret4.stdout
#     else:
#         retOutput = ret4.stderr

#     if ret4.returncode == 0:
#         return True
#     else:
#         return False

################################################################################################
# def getRectFromPolar(lat, lon):
#     y = sin(lat)
#     x = cos(lat) * cos(lon)
#     z = cos(lat) * sin(lon)
#     return x, y, z

################################################################################################
# def polarFromRect(x, y, z):
#     lat = asin(y)
#     lon = 0 if (y == 1) or (y == -1) else atan2(z, x)
#     return lat, lon

def maxOfLists(lists):
    return max([max(sublist, default=float('-inf')) for sublist in lists])

################################################################################################
def printNotamDict(d):
    for i, (key, value) in enumerate(d.items()):
        # if len(value) > PRINT_NOTAM_LENGTH:
        #     value = value[:PRINT_NOTAM_LENGTH] + '...'
        print(f'{i + 1:02} {key}:{value}')

################################################################################################
def splitNotam(item):
    items = item[1].split(';') 
    return items[0] + items[1] + items[2] + item[0]

################################################################################################
# key: [P1865/23]
# value: [2023/05/17 01:00;2023/05/20 06:00;RJJJ;N22°25',E127°18'|N22°43',E126°23'|N22°27',E126°18'|N22°09',E127°12']
def sortDictByValue(d):
#    sorted_tuples = sorted(d.items(), key=lambda item: item[1])
#    sorted_dict = {k: v for k, v in sorted_tuples}
    return {k : v for k, v in sorted(d.items(), key=lambda x: splitNotam(x))}

################################################################################################
def sortDictByEndDate(d):
    sorted_tuples = sorted(d.items(), key=lambda item: item[1].split(";")[0][:10] + item[1].split(";")[1])
    sorted_dict = {k: v for k, v in sorted_tuples}
    return sorted_dict

################################################################################################
#A1043/22:2022/10/07 10:00;2022/10/13 16:00;NFFF;S22°53',E163°20'|S22°28',E163°59'|S24°42',E165°41'|S25°06',E165°02
#P3921/22:2022/10/07 10:00;2022/10/13 16:00;RJJJ;N21°00',E134°30'|N21°15',E134°20'|N21°40',E135°00'|N21°00',E135°27
#Q2479/22:2022/10/07 10:00;2022/10/13 16:00;RJJJ;N21°00',E136°30'
#A2767/22:2022/10/07 13:10;2022/10/07 13:39;ZSHA;N33°56',E123°55'|N34°18',E123°33'|N34°28',E123°48'|N34°07',E124°10
def sortDictByLatitude(d):
#    sorted_tuples = sorted(d.items(), key=lambda item: item[1])
#    sorted_dict = {k: v for k, v in sorted_tuples}
    return {k : v for k, v in sorted(d.items(), key=lambda x: x[1])}

################################################################################################
def sortDictByKey(d):
#    sorted_tuples = sorted(d.items(), key=lambda item: item[0])
#    sorted_dict = {k: v for k, v in sorted_tuples}
    return  {k : v for k, v in sorted(d.items(), key=lambda x: x[0])}

################################################################################################
def exceptPrint():
    exc_type, _, exc_tb = exc_info()
    fname = path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)

################################################################################################
def elementClass(driver, time, className):
    return WebDriverWait(driver, time).until(EC.presence_of_element_located((By.CLASS_NAME, className)))

################################################################################################
def elementXPath(driver, time, xPath):
    return WebDriverWait(driver, time).until(EC.presence_of_element_located((By.XPATH, xPath)))

################################################################################################
def elementClick(driver, time, xPath):
    elementXPath(driver, time, xPath).click()

################################################################################################
def elementInput(driver, time, xPath, value):
    elementXPath(driver, time, xPath).send_keys(value)

################################################################################################
def listFiles(folder, extension, excludeFile=None):
    for root, dirs, files in walk(folder):
        for file in files:
            if file.endswith(extension):  # Filter files with .kml extension
                if file != excludeFile:
                    filepath = path.join(root, file)
                    yield filepath

################################################################################################
def updateTempFile(notams):
    # filename = f'./data/notam{getJapanTime("%Y%m%d-%H%M%S")}.txt'
    filename = f'./data/notam{getJapanTimeFilename()}.txt'
    # newText = f"NOTAM发射预测{getJapanTime()}\n"
    newText = f"NOTAM发射预测\n"
    newText += "================================\n"
    for i, (key, value) in enumerate(notams.items()):
        items = value.split(';')
        newText += f'{i + 1:02}: {items[2]},{key},{items[0]},{items[1]};{items[3]}\n'

    try:
        isNew = True
        oldFiles = listFiles('./data', '.txt')
        for oldFile in oldFiles:
            with open(oldFile, encoding='utf-8') as f:
                oldText = f.read()

            if oldText == newText:
                isNew = False
        if isNew:
            saveTempFile(filename, newText)
    except FileNotFoundError:
        saveTempFile(filename, newText)

def saveTempFile(filename, newText):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(newText)

    # Opening the text file in its default editor
    if isWindows():
        system(f'start {filename}')
        playSound('Alarm03.wav')
    elif isMacOS():
        playSound('Alarm03.wav')
    elif isLinux():
        playSound('train.wav')

################################################################################################
def playSound(filename=None):
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
def updateKmlFile(kml, title, filePath='', notams=None):
    try:
        with open(f'{filePath}{title}.kml', encoding='utf-8') as f:
            kmlOld = f.read()
            kml.document.name = title
            kmlNew = kml.kml()
            if kmlOld != kmlNew:
                saveKmlFile(kml, title, filePath)
                if notams:
                    updateTempFile(notams)
            else:
                print(f'Not update to file "{filePath}{title}.kml"')
    except FileNotFoundError:
        saveKmlFile(kml, title, filePath)
        if notams:
            updateTempFile(notams)

################################################################################################
def saveKmlFile(kml, title, filePath=''):
    print(f'Saved to file "{filePath}{title}.kml"')
    kml.document.name = title
    kml.save(f'{filePath}{title}.kml') # this is for check content
    kml.save('doc.kml') # this is for zip to kmz file

    with zipfile.ZipFile(f'{filePath}{title}.kmz', mode='w') as zf:
        zf.write('doc.kml')

    remove('doc.kml')

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
def saveDictToJsonFile(nsfDict, filename):
    print(f'Save   to file "{filename}.json"')
    with open(f'{filename}.json', "w", encoding="utf-8") as f:
        dump(nsfDict, f, ensure_ascii=False, indent=2)

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
# TODO add new FIR to here
def isChinaNotam(condition):
    section = openConfig()
    count = int(section.get('FirCount'))
    isChinaNotam = False
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

def isChinaNotamOld(condition):
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
def isNotChinaNotam(location, condition):
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
    timeNow = datetime.now(pytz.timezone("Asia/Tokyo"))
    if timeNow >= localDate:
        return True
    else:
        return False

################################################################################################
def convertToLocalDate(utcDate, tz):
    utcDate = datetime.strptime(utcDate, "%Y/%m/%d %H:%M").replace(tzinfo=pytz.UTC)
    return utcDate.astimezone(pytz.timezone(tz))

################################################################################################
# TODO how to extract lan/lon exactly
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
#0123456789012345678
#37-42.4N120-10.8E
#37-42-46N120-10-98E
def convertPattern7(s):
    if len(s) == 19:
        return f"{s[8:9]}{s[0:2]}°{s[3:5]}'{s[6:8]}\",{s[18:19]}{s[9:12]}°{s[13:15]}'{s[16:18]}\""
    elif len(s) == 21:
        nSecond = str(int(s[6:9]) * 6 / pow(10, len(s[6:9]) - 1))[:2]
        ESecond = str(int(s[17:20]) * 6 / pow(10, len(s[17:20]) - 1))[:2]
        return f"{s[9]}{s[0:2]}°{s[3:5]}'{nSecond}\",{s[20]}{s[10:13]}°{s[14:16]}'{ESecond}\""
    return f"{s[7:8]}{s[0:2]}°{s[3:5]}',{s[16:17]}{s[8:11]}°{s[12:14]}'"

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
# def circleByPointOld(lat, lon, km=5):
#     proj_wgs84 = Proj('+proj=longlat +datum=WGS84')
#     proj_aeqd = Proj('+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0'.format(lat=lat, lon=lon))
#     project = partial(shapely.transform, proj_aeqd, proj_wgs84)
#     buf = Point(0, 0).buffer(km * 1000)  # distance in metres
#     return transform(project, buf).exterior.coords[:]

################################################################################################
def circleByPoint(lat, lon, km=5):
    proj_wgs84 = CRS('EPSG:4326')
    proj_aeqd = CRS(f'+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0')
    transformer = Transformer.from_crs(proj_aeqd, proj_wgs84, always_xy=True)
    buf = Point(0, 0).buffer(km * 1000)  # distance in metres
    return transform(transformer.transform, buf).exterior.coords[:]

# Calculate the great circle distance between two points
# on the earth (specified in decimal degrees)
# calculate distance between points
################################################################################################
def haversine(lon1, lat1, lon2, lat2):
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers is 6371
    km = 6371 * c
    return km

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
# angle is started from equator
def great_circle_angle(lat1, lon1, lat2, lon2):
    return great_circle_bearing(lat1, lon1, lat2, lon2) - 90

################################################################################################
# Formula: θ = atan2( sin Δλ ⋅ cos φ2 , cos φ1 ⋅ sin φ2 − sin φ1 ⋅ cos φ2 ⋅ cos Δλ )
# where	φ1,λ1 is the start point, φ2,λ2 the end point (Δλ is the difference in longitude)
# θ is started from North
def great_circle_bearing(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude to radians
    φ1, λ1, φ2, λ2 = map(radians, [lat1, lon1, lat2, lon2])
    y = sin(λ2 - λ1) * cos(φ2)
    x = cos(φ1) * sin(φ2) - sin(φ1) * cos(φ2) * cos(λ2 - λ1)
    θ = atan2(y, x)
    bearing = degrees(θ) % 360 # in degrees
    return bearing

################################################################################################
# Haversine: a = sin²(Δφ/2) + cos φ1 ⋅ cos φ2 ⋅ sin²(Δλ/2)
#   formula: c = 2 ⋅ atan2( √a, √(1−a) )
#            d = R ⋅ c
# where	φ is latitude, λ is longitude, R is earth’s radius (mean radius = 6,371km);
# note that angles need to be in radians to pass to trig functions!
def great_circle_distance(lat1, lon1, lat2, lon2):
    R = 6371000; # metres

    # convert decimal degrees to radians 
    φ1, λ1, φ2, λ2 = map(radians, [lat1, lon1, lat2, lon2])
    Δφ = φ2 - φ1
    Δλ = λ2 - λ1

    a = sin(Δφ / 2) * sin(Δφ / 2) + cos(φ1) * cos(φ2) * sin(Δλ / 2) * sin(Δλ / 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    d = R * c # in metres
    return d

################################################################################################
def great_circle_point(lat1, lon1, lat2, lon2, distance=5000000, distanceRatio=1.5, fromSea=False):
    bearing = great_circle_bearing(lat1, lon1, lat2, lon2)
    d = great_circle_distance(lat1, lon1, lat2, lon2)
    if fromSea:
        d += 500000
    else:
        d = max(distance, d) if distance != None else d * distanceRatio
    point = great_circle_point_by_distance(lat1, lon1, bearing, d)
    return point

################################################################################################
# Formula:	φ2 = asin( sin φ1 ⋅ cos δ + cos φ1 ⋅ sin δ ⋅ cos θ )
#           λ2 = λ1 + atan2( sin θ ⋅ sin δ ⋅ cos φ1, cos δ − sin φ1 ⋅ sin φ2 )
# where	φ is latitude, λ is longitude, θ is the bearing (clockwise from north), δ is the angular distance d/R; 
# d being the distance travelled, R the earth’s radius
def great_circle_point_by_distance(lat1, lon1, bearing, distance):
    R = 6371000; # metres
    φ1, λ1 = map(radians, [lat1, lon1])
    δ = distance / R
    θ = radians(bearing)
    φ2 = asin(sin(φ1) * cos(δ) + cos(φ1) * sin(δ) * cos(θ))
    λ2 = λ1 + atan2(sin(θ) * sin(δ) * cos(φ1), cos(δ) - sin(φ1) * sin(φ2))
    return [degrees(λ2), degrees(φ2)]

################################################################################################
def compare_kml_files(oldFile, newFile):
    # %% 
    supported_drivers['KML'] = 'rw'
    oldPolys = gpd.read_file(oldFile, driver='KML')
    newPolys = gpd.read_file(newFile, driver='KML')

    # %% 
    plt.imshow(zeros((100, 100)))
    oldPolys.plot(facecolor='orange')
    plt.show()
    return 1

################################################################################################
def kml2Shapely(kml):
    # Load the KML file and get the first polygon feature
    with open('file.kml', 'rt') as f:
        k = kml.KML()
        k.from_string(f.read())
        feature = list(k.features())[0]
        polygon = feature.geometry

    # Extract the coordinates of the polygon
    outer_coords = list(polygon.exterior.coords)
    inner_coords = [list(interior.coords) for interior in polygon.interiors]

    # Create the Shapely polygon object
    shapely_polygon = Polygon(outer_coords, inner_coords)

################################################################################################
# box_1 = [[511, 41], [577, 41], [577, 76], [511, 76]]
# box_2 = [[544, 59], [610, 59], [610, 94], [544, 94]]
# print(calculate_iou(box_1, box_2))
def calculate_iou(box_1, box_2):
    poly_1 = Polygon(box_1)
    poly_2 = Polygon(box_2)
    iou = poly_1.intersection(poly_2).area / poly_1.union(poly_2).area
    return iou

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


