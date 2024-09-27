from sys import argv
from os import path
from timeit import timeit
from datetime import timedelta
import PySimpleGUI as sg
import matplotlib.pyplot as plt
from simplekml import Kml
from re import finditer, findall

from myModules import myUtils
from myModules import myPlot
from myModules import myShape
from myModules import myKml

################################################################################################
def plotLaunchCenter(axs):
    cities = ('酒泉', '太原', '西昌', '文昌')
    names = ('酒泉卫星发射中心', '太原卫星发射中心', '西昌卫星发射中心', '文昌航天发射场')
    for i, lc in enumerate(cities):
        _, lonlat, color = myShape.CITIES[lc].split('|')
        lon, lat = lonlat.split(',')

################################################################################################
def compareNotam(newFile, cn_font):
    location, locations = myUtils.getLocation(newFile)
    if location is None:
        print(f'{newFile} not included {locations}')
        return
    
    newGdf = myKml.readKmlFile(newFile)
    if newGdf.empty:
        print(f"No Data in {newFile}!")
        return 

    folder = path.abspath(myShape.KML_FOLDERS[location])
    filename = path.basename(newFile)

    # delete files
    myUtils.removeFile('./temp/match/*.png')
    myUtils.removeFile('./temp/unmatch/*.png')

    # List all kml files in specific foder except newFile
    oldFiles = myUtils.listFiles(folder, extension=".kml", excludeFile=filename)
    savePath1 = f'./temp/match/{filename[:-4]}'
    savePath2 = f'./temp/unmatch/{filename[:-4]}'
    
    for oldFile in oldFiles:
        if '\\old\\' in oldFile:
            continue

        try:
            if plt:
                plt.close()

            # Use geopandas to read old NOTAM kml file to shapely.geometry
            try:
                oldGdf = myKml.readKmlFile(oldFile)
                if oldGdf.empty:
                    continue
                fig, ax = myShape.getFigure(setAspectEqual=True, plotGrid=True)
            except Exception as e:
                print(f"No Data in {oldFile}!")
                print(f'Exception: {e}\n')

            myShape.plotTwoNoatms(ax, newGdf, oldGdf)
            newTitle = myUtils.getTitle(newFile)
            newTitle = newTitle if '时' in newTitle else newTitle.replace('日', '日??时??分')
            oldTitle = myUtils.getTitle(oldFile)
            ious, title = myShape.plotPolygonsIntersection(fig, ax, cn_font, newGdf, newTitle, oldGdf, oldTitle)
            myShape.plotTitleXYLabels(fig, ax, cn_font, title, 'Longitude（经度）', 'Latitude（纬度）')
            # myPlot.showBackend()

            # Save the plot to a file
            basename = path.basename(oldFile)
            filename = basename.replace(".kml", ".png")

            if ious:
                print(f'{newTitle} IoU {oldTitle}')
                for iou in ious:
                    print(f'    {iou}') 
                myPlot.saveFig(fig, f'{savePath1}/{filename}', False, False)
                print('')
            else:
                myPlot.saveFig(fig, f'{savePath2}/{filename}', False, False)
        except Exception as e:
            print(f'Exception: {e}\n')
    print('\nFinished comparing!')

################################################################################################
def main():
    myPlot.setScreenDpiAware()
    cn_font = myPlot.init()

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
                proceeFile(window, cn_font, newFile)
                window.Normal()
                newFile = ''
    else:
        newFile = argv[1]
        proceeFile(cn_font, newFile)

    window.close()

################################################################################################
def proceeFile(window, cn_font, newFile):
    if not newFile:
        print("No filename supplied")
    elif '.xls' in newFile:
        print('Filename: ', newFile)
        myShape.createShipTrackLinesKmlFile(newFile)
        myUtils.playSound()
    elif '.kml' in newFile:
        print('The filename you chose was: ', newFile)
        print('Comapre to other KML files...')
        compareNotam(newFile, cn_font)
    elif '.txt' in newFile and 'MSA' in newFile:
        print('The filename you chose was: ', newFile)
        createMsaDropZonesKmlFile(newFile)
    elif '.txt' in newFile:
        notamDict = myUtils.parseNotamFromTextFile(newFile)
        # notamDict = myUtils.readNotamDictDetailFromTextFile(newFile)
        if notamDict:
            notamDict =  myUtils.sortDictByValue(notamDict)
            myUtils.printNotam(notamDict)
            myShape.createKmlFile(notamDict)
    else:
        print("Unknown type filename supplied")

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
            startDate = startDate if startDate else myUtils.getUTCTime()[:-3]
            endDate = endDate if endDates else myUtils.getUTCTime()[:-3]
            title = f"{oldFile.replace('.txt', '').split('/')[-1]}"
            title = myUtils.convertTitle(startDate, endDate, title, isLocalTime=True)

            if area:
                area = formatMSALatitudeLongitude([area])[0]
                coords = area.split('|')
                coordsList = [myUtils.convertDMS2DD(c) for c in coords]
                if len(coordsList) == 1:
                    radius = parseRadius(content)
                    myShape.drawCircle(kml, coordsList, f'{location}/{number}', radius=radius)
                else:
                    myShape.drawPolygon(kml, coordsList, f'{location}/{number}')
                notams = myUtils.getNoatmDict(notams, number, startDate, endDate, location, area)
                lastStart = startDate
                lastEnd = endDate
        myShape.updateKmlFile(kml, title, myShape.KML_PATH, notams)

################################################################################################
MSA_RADIUS_PATTERN = r'为中心[、，]半径(\d{1,4})([公里米])'
def parseRadius(content):
    radiusMatch = findall(MSA_RADIUS_PATTERN, content)
    for m in radiusMatch:
        return int(m[0]) if m[1] == '公里' else  int(m[0]) // 1000
    
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
    if area:
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
            startYear = myUtils.getJapanDate()[:4]
            startMonth = int(m.group(1)) if m.group(1) else ''
            startDay = int(m.group(2)) if m.group(2) else ''
            startTime = myUtils.convertTime(m.group(3))
            endYear = startYear
            endMonth = int(m.group(4)) if m.group(4) else startMonth
            endDay = int(m.group(5)) if m.group(5) else startDay
            endTime = myUtils.convertTime(m.group(6) if len(m.groups()) == 6 else '', False)
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
            startTime = myUtils.convertTime(m.group(2)) #convert to UTC+()
            startMonth = m.group(3)
            startYear = m.group(4) if m.group(4) else myUtils.getThisYear()
            endDay = m.group(5) #convert to UTC+()
            endTime = myUtils.convertTime(m.group(6)) #convert to UTC+()
            endTime = endTime if endTime != '24:00' else '23:59'
            endMonth = m.group(7)
            endYear = m.group(4) if m.group(4) else myUtils.getThisYear()
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
            newll = myUtils.findConvertLatitudeLongitude(oldll)
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