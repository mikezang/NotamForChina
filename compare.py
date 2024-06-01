from re import finditer
import sys
import geopandas as gpd
import PySimpleGUI as sg
import matplotlib.pyplot as plt
from os import path, remove
from sys import argv
from timeit import timeit
from datetime import timedelta

sys.path.append("")

import constants
import myUtils
import myPlot
import notam

################################################################################################
def plotLaunchCenter(axs):
    cities = ('酒泉', '太原', '西昌', '文昌')
    names = ('酒泉卫星发射中心', '太原卫星发射中心', '西昌卫星发射中心', '文昌航天发射场')
    for i, lc in enumerate(cities):
        _, lonlat, color = constants.CITIES[lc].split('|')
        lon, lat = lonlat.split(',')
        
        # color=myUtils.getColorFromKml(color)
        # from matplotlib.patches import Polygon
        # from matplotlib import patches
        # circle = Polygon(myUtils.circleByPoint(lat, lon, 50), facecolor=myUtils.getColorFromKml(color), closed=True)
        # circle = patches.Circle(xy=(lon, lat), radius=5)
        # axs.add_patch(circle)
        # Convert [(lat1, lon1), (lat2, lon2), ...] to [(lon1, lon2, ...), (lat1, lat2, ...)]
        # lons, lats = zip(*circle)
        # coordinates = list(zip(lons, lats))

        # axs.plot(lon, lat, 'ro')
        # lons, lats = map(lon, lat)
        # axs.plot(lon, lat, marker = 'o', color='r', zorder=5)

################################################################################################
def compareNotam(newFile, cn_font):
    location, locations = myUtils.getLocation(newFile)
    if location is None:
        print(f'{newFile} not included {locations}')
        return
    
    newPolys = gpd.read_file(newFile, driver='KML')
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
            oldPolys = gpd.read_file(oldFile, driver='KML')
            fig, ax = myPlot.getFigure(setAspectEqual=True)

            myPlot.plot2Noatms(fig, ax, newPolys, oldPolys)
            newTitle = myUtils.getTitle(newFile)
            newTitle = newTitle if '时' in newTitle else newTitle.replace('日', '日??时??分')
            oldTitle = myUtils.getTitle(oldFile)
            ious = myPlot.plotPolygonsIntersection(fig, ax, cn_font, newPolys, newTitle, oldPolys, oldTitle)
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
            print(f"{oldFile} No Data!")
            print(f'Exception: {e}\n')
            pass
    print('\nFnished comparing!')

################################################################################################
def main():
    # chineseDate1 = '5月28日至31日'
    # chineseDate2 = '5月28日15时至31日17时'
    # chineseDate3 = '5月28日15时至6月1日17时'
    # patternMyOriginal = r'(\d{1,2})月(\d{1,2})日(\d{0,4})时?至(\d{0,2})月?(\d{1,2})日(\d{0,4})时?'
    # patternByChatGPT = r'(?:(\d{1,2})月)?(\d{1,2})日(?:(\d{1,4})时)?至(?:(\d{1,2})月)?(\d{1,2})日(?:(\d{1,4})时)?'
    # matchesMyOriginal1 = [m.groups() for m in finditer(patternMyOriginal , chineseDate1)]
    # matchesMyOriginal2 = [m.groups() for m in finditer(patternMyOriginal , chineseDate2)]
    # matchesMyOriginal3 = [m.groups() for m in finditer(patternMyOriginal , chineseDate3)]
    # matchesByChatGPT1 = [m.groups() for m in finditer(patternByChatGPT , chineseDate1)]
    # matchesByChatGPT2 = [m.groups() for m in finditer(patternByChatGPT , chineseDate2)]
    # matchesByChatGPT3 = [m.groups() for m in finditer(patternByChatGPT , chineseDate3)]

    # print(f'\n{matchesMyOriginal1 = }')
    # print(f'{matchesMyOriginal2 = }')
    # print(f'{matchesMyOriginal3 = }')
    # print(f'{matchesByChatGPT1 = }')
    # print(f'{matchesByChatGPT2 = }')
    # print(f'{matchesByChatGPT3 = }')

    myPlot.setScreenDpiAware()
    cn_font = myPlot.init()

    if len(sys.argv) == 1:
        window = sg.Window('Select file to process...',
                        [[sg.Text('file to open')],
                        [sg.In(), sg.FileBrowse()],
                        [sg.Open(), sg.Exit()],
                        # [sg.Image(key="-IMAGE-", size=(600, 600))],
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
        print('The filename you chose was: ', newFile)
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
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')

################################################################################################
if __name__ == "__main__":
    showRunTime("main()")