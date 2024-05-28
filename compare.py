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
    # Use geopandas to read new NOTAM kml file
    location, locations = myUtils.getLocation(newFile)
    # location = newFile.split('/')[-1][11:13]
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
            # fig, axs = plt.subplots(nrows=1, ncols=1)
            fig, axs = myPlot.getFigure()
            axs.set_aspect('equal')

            # Plot NOTAM
            myPlot.plotNotam1(fig, axs, cn_font, newPolys, oldPolys)

            # Plot Launch center 
            # plotLaunchCenter(axs)

            # Get the current latitude and longitude ranges of axs[1]
            lon1, lon2 = axs.get_xlim()
            lat1, lat2 = axs.get_ylim()

            # Plot wordl map
            ious = myPlot.plotNotam2(fig, axs, cn_font, newPolys, myUtils.getTitle(newFile), oldPolys, myUtils.getTitle(oldFile))

            # Plot Launch center 
            # plotLaunchCenter(axs)

            # Set the extent of the axis object to the desired latitude and longitude ranges
            myPlot.adjustLim(axs, lon1, lon2, lat1, lat2)
            
            # Show the plot
            myPlot.showBackend()

            # Save the plot to a file
            basename = path.basename(oldFile)
            filename = basename.replace(".kml", ".png")

            if ious:
                for iou in ious:
                    print(iou) 
                myPlot.saveFig(fig, f'{savePath}/{filename}')
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