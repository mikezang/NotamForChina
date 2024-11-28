from sys import argv
from os import path
from timeit import timeit
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import PySimpleGUI as sg
import matplotlib.pyplot as plt
from simplekml import Kml
from re import finditer, findall

from myModules import myShape
from myModules import myKml
from myModules import myFile
from myModules import myDate
from myModules import myDict
from myModules import myGUI
from myModules import myNOTAM

################################################################################################
def plotLaunchCenter(axs):
    cities = ('酒泉', '太原', '西昌', '文昌')
    names = ('酒泉卫星发射中心', '太原卫星发射中心', '西昌卫星发射中心', '文昌航天发射场')
    for i, lc in enumerate(cities):
        _, lonlat, color = myFile.readConfig(lc)
        # _, lonlat, color = myShape.CITIES[lc].split('|')
        lon, lat = lonlat.split(',')

################################################################################################
def main():
    import locale
    import sys
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    sys.stdout.reconfigure(encoding='UTF-8')
    
    myGUI.setScreenDpiAware()

    if len(argv) == 1:
        window = sg.Window('Select file to process...',
                        [[sg.Text('file to open')],
                        [sg.In(), sg.FileBrowse()],
                        [sg.Open(), sg.Exit()],
                        ])
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Exit':
                break

            newFile = values[0]
            if newFile != '':
                window.minimize()
                proceeFile(newFile)
                window.Normal()
                newFile = ''
    else:
        newFile = argv[1]
        proceeFile(newFile)

    window.close()

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

################################################################################################
def removeChars(d):
    return d.replace('-', '').replace(' ', '').replace(':', '')

#####################################################################################
def createShipTrackLinesKmlFile(newFile):
    df = readShipMoveData(newFile, '船舶轨迹', skipRows=1)
    mmsiKey = str(df['mmsi'].iloc[0])
    startDate = removeChars(df['时间'].iloc[0])[:12]
    endDate = removeChars(df['时间'].iloc[-1])[:12]
    mmsi = myFile.readConfig(['LaunchShipMMSI'])
    shipName = myFile.readConfig(['LaunchShipName'])
    shipNameDict = dict(zip(mmsi, shipName))
    shipName = shipNameDict[mmsiKey] if mmsiKey in shipNameDict else f'MMSI{mmsiKey}'
    # title = f'{startDate}-{endDate}-{shipName}-航迹'
    title = f'{endDate[:4]}年{endDate[4:6]}月{endDate[6:8]}日{endDate[8:10]}时{endDate[10:12]}分{shipName}航迹'
    coords = df[['经度', '纬度']].values.tolist()
    kml = Kml()
    myShape.drawLine(kml, coords, shipName)
    myShape.updateKmlFile(kml, title, myShape.KML_PATH)

################################################################################################
def proceeFile(newFile):
    if not newFile:
        print("No filename supplied")
    elif '.xls' in newFile:
        print('Filename: ', newFile)
        createShipTrackLinesKmlFile(newFile)
        myFile.playSound()
    elif '.kml' in newFile:
        print('The filename you chose was: ', newFile)
        print('Comapre to other KML files...')
        myShape.compareKmls(newFile)
    elif '.txt' in newFile and 'MSA' in newFile:
        print('The filename you chose was: ', newFile)
        createMsaDropZonesKmlFile(newFile)
    elif '.txt' in newFile:
        notamDict = parseNotamFromTextFile(newFile)
        if notamDict:
            notamDict =  myDict.sortDictByValue(notamDict)
            myDict.printNotam(notamDict)
            myShape.createKmlFile(notamDict)
    else:
        print("Unknown type filename supplied")

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
        if myNOTAM.isChinaNotam(text):
            notam = myNOTAM.parseNotamText(notam, text)
    return notam

################################################################################################
def getUTCTime(fmt='') -> str:
    if fmt == '':
        fmt = "%Y/%m/%d %H:%M:%S"
    return datetime.now(ZoneInfo('UTC')).strftime(fmt)

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

        location, number, startDates, endDates, areas = parseMsa(content)
        lastStart = ''
        lastEnd = ''
        kml = Kml()
        notams = {}

        for i, area in enumerate(areas):
            startDate = startDates[i] if i < len(startDates) else lastStart
            endDate = endDates[i] if i < len(endDates) else lastEnd
            startDate = startDate if startDate else getUTCTime()[:-3]
            endDate = endDate if endDates else getUTCTime()[:-3]
            title = f"{oldFile.replace('.txt', '').split('/')[-1]}"
            title = myFile.convertTitle(startDate, endDate, title, isLocalTime=True)

            if area:
                area = formatMSALatitudeLongitude([area])[0]
                coords = area.split('|')
                coordsList = [myFile.convertDMS2DD(c) for c in coords]
                color = myFile.readConfig('海上')[1]
                if len(coordsList) == 1:
                    radius = parseRadius(content)
                    if radius > 0:
                        # coordsList[0] += f'+{radius:.0f}' 
                        # color = myFile.readConfig('海上')[1]
                        myShape.drawCircle(kml, coordsList, f'{location}/{number}', color=color, radius=radius)
                else:
                    myShape.drawPolygon(kml, coordsList, f'{location}/{number}', )
                notams = myNOTAM.getNoatmDict(notams, number, startDate, endDate, location, area)
                lastStart = startDate
                lastEnd = endDate
        myShape.updateKmlFile(kml, title, myShape.KML_PATH, notams)

################################################################################################
MSA_RADIUS_PATTERN = r'为中心[、，](?:(\d{1,4})(海里|公里|米)为半径|半径(\d{1,4})(海里|公里|米))'
def parseRadius(content):
    radiusMatch = findall(MSA_RADIUS_PATTERN, content)
    for m in radiusMatch:
        radius = getRadius(m)
        if radius > 0:
            break
    return radius

###############################################################################
def getRadius(m):
    myDict = {'海里':1.852, '公里':1, '米':1000}
    if m[0] and m[1]:
        radius = int(m[0]) / myDict[m[1]]
    elif m[2] and m[3]:
        radius = int(m[2]) / myDict[m[3]]
    else:
        radius = 0
    return radius

################################################################################################
def parseMsa(text):
    location = 'MSA'
    number = getMsaLocation(text)
    text = text.replace('\n', '').replace(' ', '').replace('/', '').replace('、', ',')
    startDates, endDates = getMsaDates(text)
    areas = getMsaArea(text)
    return location, number, startDates, endDates, areas

################################################################################################
MSA_PATTERN_LATITUDE_LONGITUDE =  r'(\d{2}[°-]\d{2}[\′.-]?\d{0,3}″?[NS][ \/]?\d{2,3}[°-]\d{1,2}[′.-]?\d{0,3}"?[EW])'
def getMsaArea(contentSection) -> str:
    area = ''
    lastEnd = 0
    areas = []
    contentSection = contentSection.replace('N，', 'N')
    latlons = finditer(MSA_PATTERN_LATITUDE_LONGITUDE, contentSection)
    for m in latlons:
        if lastEnd > 0 and m.start() > lastEnd + 4:
            areas.append(area)
            area = m.group()
        else:
            if area != '':
                area += '|'
            area += m.group()
        lastEnd = m.end()
    if area and area not in areas:
        areas.append(area)
    return areas

################################################################################################
# MSA_PATTERN_DATE_CHINA1 = r'(\d{1,2})月(\d{1,4})日(\d{1,4})时至(\d{1,4})时'
MSA_PATTERN_DATE_CHINA = r'(?:(\d{1,2})月)?(\d{1,2})日(?:(\d{1,4})时)?至(?:(\d{1,2})月)?(?:(\d{1,2})日)?(?:(\d{1,4})时)?'
MSA_PATTERN_DATE = r'FROM(\d{0,2})(\d{0,4})[UTC]{0,3}([A-Z]{0,4})\.?(\d{0,2})TO(\d{0,2})(\d{0,4})[UTC]{0,3}([A-Z]{0,4})\.?(\d{0,2})'
def getMsaDates(content: str) -> tuple:
    startDates, endDates = [], []
    startEndDates1 = [m for m in finditer(MSA_PATTERN_DATE_CHINA, content)]
    startEndDates2 = [m for m in finditer(MSA_PATTERN_DATE, content)]
    if startEndDates1:
        for m in startEndDates1:
            startYear = myDate.getJapanDate()[:4]
            startMonth = int(m.group(1)) if m.group(1) else ''
            startDay = int(m.group(2)) if m.group(2) else ''
            startTime = myDate.convertTime(m.group(3))
            endYear = startYear
            endMonth = int(m.group(4)) if m.group(4) else startMonth
            endDay = int(m.group(5)) if m.group(5) else startDay
            endTime = myDate.convertTime(m.group(6) if len(m.groups()) == 6 else '', False)
            endTime = endTime if endTime != '24:00' else '23:59'
            if startYear and startMonth and startDay and startTime:
                startDate = f'{startYear}/{startMonth:02}/{int(startDay):02} {startTime}'
            if endYear and endMonth and endDay and endTime:
                endDate = f'{endYear}/{endMonth:02}/{endDay:02} {endTime}'
            startDates.append(startDate)
            endDates.append(endDate)
    elif startEndDates2:
        for m in startEndDates2:
            startDay = m.group(1) #convert to UTC+()
            startTime = myDate.convertTime(m.group(2)) #convert to UTC+()
            startMonth = m.group(3)
            startYear = m.group(4) if m.group(4) else myDate.getThisYear()
            endDay = m.group(5) #convert to UTC+()
            endTime = myDate.convertTime(m.group(6)) #convert to UTC+()
            endTime = endTime if endTime != '24:00' else '23:59'
            endMonth = m.group(7)
            endYear = m.group(4) if m.group(4) else myDate.getThisYear()
            startDate = f'{startYear}/{startMonth:02}/{startDay:02} {startTime}'
            endDate = f'{endYear}/{endMonth:02}/{endDay:02} {endTime}'
            startDates.append(startDate)
            endDates.append(endDate)
    return startDates, endDates

################################################################################################
MSA_LOCATIONS = {'鲁航警': 'SD', '粤航警': 'GD', '琼航警': 'HN'}
MSA_PATTERN_NUMBER = r'([A-Z][A-Z]|鲁航警|粤航警|琼航警)(\d{1,3}\/\d{2})'
def getMsaLocation(content) -> str:
    locations = finditer(MSA_PATTERN_NUMBER, content)
    for m in locations:
        if m.group(1) in MSA_LOCATIONS:
            return f'{MSA_LOCATIONS[m.group(1)]}{m.group(2)}'
        else:
            return m.groups()
    else:
        return ''

################################################################################################
def formatMSALatitudeLongitude(oldData) -> str:
    newData = []
    for data in oldData:
        oldllList = data.split('|')

        newllList = ''
        for oldll in oldllList:
            newll = myNOTAM.findConvertLatitudeLongitude(oldll)
            newllList += newll + '|'
        newData.append(newllList[:-1])
    return newData

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')

################################################################################################
if __name__ == "__main__":
    showRunTime("main()")