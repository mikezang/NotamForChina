import sys
import geopandas as gpd
import PySimpleGUI as sg
import matplotlib.pyplot as plt
from os import path
from timeit import timeit
from datetime import timedelta

sys.path.append("")

from myModules import constants
from myModules import myUtils
from myModules import myPlot
import notam
import nsf

################################################################################################
def plotLaunchCenter(axs):
    cities = ('酒泉', '太原', '西昌', '文昌')
    names = ('酒泉卫星发射中心', '太原卫星发射中心', '西昌卫星发射中心', '文昌航天发射场')
    for i, lc in enumerate(cities):
        _, lonlat, color = constants.CITIES[lc].split('|')
        lon, lat = lonlat.split(',')

################################################################################################
def compareNotam(newFile, cn_font):
    location, locations = myUtils.getLocation(newFile)
    if location is None:
        print(f'{newFile} not included {locations}')
        return
    
    newGdf = gpd.read_file(newFile, driver='KML')
    if newGdf.empty:
        print(f"No Data in {newFile}!")
        return 

    newGdf = newGdf[(newGdf.geometry.type=='Polygon') | (newGdf.geometry.type=='LineString')]    
    folder = path.abspath(constants.KML_FOLDERS[location])
    filename = path.basename(newFile)

    # delete files
    myUtils.removeFile('./temp/match/*.png')
    myUtils.removeFile('./temp/unmatch/*.png')

    # List all kml files in specific foder except newFile
    oldFiles = myUtils.listFiles(folder, extension=".kml", excludeFile=filename)
    savePath = f'./temp/match/{filename[:-4]}'
    
    for oldFile in oldFiles:
        if '\\old\\' in oldFile:
            continue

        try:
            if plt:
                plt.close()

            # Use geopandas to read old NOTAM kml file to shapely.geometry
            try:
                oldGdf = gpd.read_file(oldFile, driver='KML')
                if oldGdf.empty:
                    continue

                oldGdf = oldGdf[(oldGdf.geometry.type=='Polygon') | (oldGdf.geometry.type=='LineString')]
                fig, ax = myPlot.getFigure(setAspectEqual=True)
            except Exception as e:
                print(f"No Data in {oldFile}!")
                print(f'Exception: {e}\n')

            myPlot.plotTwoNoatms(ax, newGdf, oldGdf)
            newTitle = myUtils.getTitle(newFile)
            newTitle = newTitle if '时' in newTitle else newTitle.replace('日', '日??时??分')
            oldTitle = myUtils.getTitle(oldFile)
            ious = myPlot.plotPolygonsIntersection(fig, ax, cn_font, newGdf, newTitle, oldGdf, oldTitle)
            # myPlot.showBackend()

            # Save the plot to a file
            basename = path.basename(oldFile)
            filename = basename.replace(".kml", ".png")

            if ious:
                print(f'{newTitle} vs {oldTitle}')
                for iou in ious:
                    print(f'    {iou}') 
                myPlot.saveFig(fig, f'{savePath}/{filename}', False, False)
                print('')
            else:
                myPlot.saveFig(fig, f'./temp/unmatch/{filename}', False, False)
        except Exception as e:
            print(f'Exception: {e}\n')
    print('\nFnished comparing!')

################################################################################################
def main():
    myPlot.setScreenDpiAware()
    cn_font = myPlot.init()

    if len(sys.argv) == 1:
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
        newFile = sys.argv[1]
        proceeFile(cn_font, newFile)

    window.close()

################################################################################################
def proceeFile(window, cn_font, newFile):
    if not newFile:
        print("No filename supplied")
    elif '.xls' in newFile:
        print('Filename: ', newFile)
        myUtils.createShipTrackLinesKmlFile(newFile)
        myUtils.playSound()
    elif '.kml' in newFile:
        print('The filename you chose was: ', newFile)
        print('Comapre to other KML files...')
        compareNotam(newFile, cn_font)
    elif '.txt' in newFile and 'MSA' in newFile:
        print('The filename you chose was: ', newFile)
        myUtils.createMsaDropZonesKmlFile(newFile)
    elif '.txt' in newFile:
        notamDict = myUtils.readNotamDictDetailFromTextFile(newFile)
        if notamDict:
            notam.printNotam(notamDict)
            myUtils.createKmlFile(notamDict)
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
        location, number, startDates, endDates, areas = notam.parseMsa(content)
        lastStart = ''
        lastEnd = ''
        kml = kml()
        notams = {}

        for i, area in enumerate(areas):
            startDate = startDates[i] if i < len(startDates) else lastStart
            endDate = endDates[i] if i < len(endDates) else lastEnd
            startDate = startDate if startDate else myUtils.getUTCTime()[:-3]
            endDate = endDate if endDates else myUtils.getUTCTime()[:-3]
            title = f"{oldFile.replace('.txt', '').split('/')[-1]}"
            title = myUtils.convertTitle(startDate, endDate, title, isLocalTime=True)

            if area:
                area = nsf.formatMSALatitudeLongitude([area])[0]
                coords = area.split('|')
                coordsList = [myUtils.convertDMS2DD(c) for c in coords]
                if len(coordsList) == 1:
                    radius = myUtils.parseRadius(content)
                    myUtils.drawCircle(kml, coordsList, f'{location}/{number}', radius=radius)
                else:
                    myUtils.drawPolygon(kml, coordsList, f'{location}/{number}')
                notams = notam.getNoatmDict(notams, number, startDate, endDate, location, area)
                lastStart = startDate
                lastEnd = endDate
        myUtils.updateKmlFile(kml, title, myUtils.KML_PATH, notams)

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')

################################################################################################
if __name__ == "__main__":
    showRunTime("main()")