from sys import argv
from os import path
from timeit import timeit
from datetime import timedelta
import PySimpleGUI as sg
import matplotlib.pyplot as plt
from simplekml import Kml

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
        location, number, startDates, endDates, areas = myUtils.parseMsa(content)
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
                area = myUtils.formatMSALatitudeLongitude([area])[0]
                coords = area.split('|')
                coordsList = [myUtils.convertDMS2DD(c) for c in coords]
                if len(coordsList) == 1:
                    radius = myUtils.parseRadius(content)
                    myShape.drawCircle(kml, coordsList, f'{location}/{number}', radius=radius)
                else:
                    myShape.drawPolygon(kml, coordsList, f'{location}/{number}')
                notams = myUtils.getNoatmDict(notams, number, startDate, endDate, location, area)
                lastStart = startDate
                lastEnd = endDate
        myShape.updateKmlFile(kml, title, myShape.KML_PATH, notams)

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')

################################################################################################
if __name__ == "__main__":
    showRunTime("main()")