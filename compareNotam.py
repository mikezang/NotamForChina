import sys
import geodatasets
import geopandas as gpd
import PySimpleGUI as sg
import matplotlib.pyplot as plt
from os import path, remove
from sys import argv
from timeit import timeit
from datetime import timedelta
from shapely.geometry import Polygon
from matplotlib.lines import Line2D

sys.path.append("")

import constants
import myUtils
import myPlot
import notam

def plotNotam(axs, polys, color=None, legend=None, lables=None):
    if isinstance(polys, gpd.GeoDataFrame):
        polys.exterior.plot(ax=axs, facecolor=color, color=color, label=legend, zorder=3)
    elif isinstance(polys, Polygon):
        x, y = polys.exterior.xy
        plt.plot(x, y, color=color, zorder=3)

    if lables != None:
        for i, iloc in enumerate(polys.geometry.iloc):
            if isinstance(iloc, Polygon):
                x, y = iloc.centroid.coords[0]
                label = lables[i]
                axs.annotate(label, xy=(x, y), xytext=(x + 0.5, y + 0.1), fontsize=14, arrowprops=dict(arrowstyle='->'))

def plotIOUs(fig, axs, newPolys, oldPolys):
    newIndex = 0
    # oldNames, newNames = [], []
    ious = []

    for i, newGeom in enumerate(newPolys.geometry):
        if isinstance(newGeom, Polygon):
            oldIndex = 0
            newIndex += 1
            newName = newPolys.iloc[i]["Name"]
            # newNames.append(newName)

            for j, oldGeom in enumerate(oldPolys.geometry):
                if isinstance(oldGeom, Polygon):
                    oldIndex += 1
                    oldName = oldPolys.iloc[j]["Name"]
                    # oldNames.append(oldName)
                    geomName = f'{newName} vs {oldName}'

                    newPoly = myPlot.kml2ShapelyPolygon(newGeom)
                    oldPoly = myPlot.kml2ShapelyPolygon(oldGeom)
                    iou = 0.0

                    if newPoly.intersects(oldPoly):
                        try:
                            intersection = newPoly.intersection(oldPoly)
                            union = newPoly.union(oldPoly)
                            iou = 0.0 if union.area == 0.0 else intersection.area / union.area
                        except Exception as e:
                            pass
                    if iou > 0.01:
                        text = f'{geomName} JSI: {iou:.1%}'
                        ious.append(text)
                        # print(text)
                        plotNotam(axs, gpd.GeoDataFrame(geometry=[intersection]), 'orange', text)
    return ious

def plotNotam1(fig, axs, cn_font, newPolys, oldPolys):
    # plot title, axis and NOTAM drop zones
    # plotTitleXYLabels(fig, axs, cn_font, f'{newTitle}\n{oldTitle}', '纬度Latitude', '经度Longitude')

    # plot NOATM drop zones to set scale
    plotNotam(axs, newPolys, 'blue')
    plotNotam(axs, oldPolys, 'green')

def plotNotam2(fig, axs, cn_font, newPolys, oldPolys, newTitle, oldTitle):
    # Load the world map data
    worldmap = gpd.read_file(geodatasets.get_path("naturalearth.land"))

    # Plot the world map data
    # worldmap.plot(color="lightgrey", ax=axs[1])
    worldmap["geometry"].boundary.plot(facecolor="lightgrey", color="grey", ax=axs, zorder=1)
    # worldmap["geometry"].boundary.plot(color="lightgrey", ax=axs[1])

    # Adjust the spacing between the subplots
    plt.subplots_adjust(left=0, right=1, wspace=0, hspace=0)

    # Calculate NOTAM drop zones Jaccard Similarity Index and plot intersection polygons
    ious = plotIOUs(fig, axs, newPolys, oldPolys)

    # plot title, axis and NOTAM drop zones
    title = f'{newTitle}\n{oldTitle}'
    for ios in ious:
        title += f'\n{ios}'
    plotTitleXYLabels(fig, axs, cn_font, title, '纬度Latitude', '经度Longitude')
    return ious

################################################################################################
def getTitle(filename):
    title = path.basename(filename)  # Get the filename from the path
    title = title.split('.')[0]  # Remove the extension
    title = title.split('\\')[-1]  # Get the last portion of the path
    return title

def plotTitleXYLabels(fig, axs, cn_font, title, xLabel, yLabel):
    axs.set_title(title, fontproperties=cn_font, fontsize=18, loc='left') # plot title
    # axs[0].axis('off') # Hide the border of the subplot
    axs.set_xlabel(xLabel, fontproperties=cn_font)  # Add an x-label to the axes.
    axs.set_ylabel(yLabel, fontproperties=cn_font)  # Add a y-label to the axes.

    handles = [
        Line2D([0], [0], linestyle='none', mfc='blue', mec='blue', marker='s', label='New Drop Zone'),
        Line2D([0], [0], linestyle='none', mfc='green', mec='green', marker='s', label='Old Drop Zone'),
        Line2D([0], [0], linestyle='none', mfc='orange', mec='orange', marker='s', label='Intersection Drop Zone')
    ]
    
    fig.legend(handles=handles, bbox_to_anchor=(0.1, 0), loc='outside upper left', ncol=3) # add legend

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

def adjustLim(axs, lon1, lon2, lat1, lat2):
    lon21 = lon2 - lon1
    lat21 = lat2 - lat1
    ratio1 = lat21 / lon21

    if lon21 < lat21:
        dLon = lon21 * (ratio1 - 1) / 2
        axs.set_xlim(lon1 - dLon, lon2 + dLon)
        axs.set_ylim(lat1, lat2)
    else:
        dLat = lat21 * (1 - ratio1) / ratio1 / 2
        axs.set_xlim(lon1, lon2)
        axs.set_ylim(lat1 - dLat, lat2 + dLat)

    lon1, lon2 = axs.get_xlim()
    lat1, lat2 = axs.get_ylim()
    ratio2 = (lat2 - lat1) / (lon2 - lon1)
    # print(f'Ratio1: {ratio1:0.2f}, Ratio2: {ratio2:0.2f}')

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
    oldFiles = myUtils.listFiles(folder, ".kml", filename)

    for oldFile in oldFiles:
        if '\\old\\' in oldFile:
            continue
        try:
            # Use geopandas to read old NOTAM kml file to shapely.geometry
            oldPolys = gpd.read_file(oldFile, driver='KML')

            # Create a figure with a single row and two columns
            # fig, axs = plt.subplots(nrows=1, ncols=1, figsize=(10, 8), gridspec_kw={'height_ratios': [1, 10]})
            # fig, axs = plt.subplots(nrows=1, ncols=1, figsize=(10, 8))
            if plt:
                plt.close()
            fig, axs = plt.subplots(nrows=1, ncols=1)
            axs.set_aspect('equal')

            # Plot NOTAM
            plotNotam1(fig, axs, cn_font, newPolys, oldPolys)

            # Plot Launch center 
            # plotLaunchCenter(axs)

            # Get the current latitude and longitude ranges of axs[1]
            lon1, lon2 = axs.get_xlim()
            lat1, lat2 = axs.get_ylim()

            # Plot wordl map
            ious = plotNotam2(fig, axs, cn_font, newPolys, oldPolys, getTitle(newFile), getTitle(oldFile))

            # Plot Launch center 
            # plotLaunchCenter(axs)

            # Set the extent of the axis object to the desired latitude and longitude ranges
            adjustLim(axs, lon1, lon2, lat1, lat2)
            
            # Show the plot
            myPlot.show()

            # Save the plot to a file
            filename = path.basename(oldFile).replace(".kml", ".png")
            if ious:
                for iou in ious:
                    print(iou) 
                myPlot.saveFig(fig, f'./temp/match/{filename}')
                print('')
            else:
                myPlot.saveFig(fig, f'./temp/unmatch/{filename}', False)
        except Exception as e:
            print(f"{oldFile} No Data!")
            print(f'Exception: {e}\n')
            pass
    print('\nFnished comparing!')

def main():
    cn_font = myPlot.init()

    if len(sys.argv) == 1:
        window = sg.Window('Select file to process...',
                        [[sg.Text('file to open')],
                        [sg.In(), sg.FileBrowse()],
                        [sg.Open(), sg.Exit()]])
        while True:
            event, values = window.read()

            if event == sg.WIN_CLOSED or event == 'Exit':
                break

            newFile = values[0]
            if newFile != '':
                window.minimize()
                proceeFile(cn_font, newFile)
                window.Normal()
                newFile = ''
    else:
        newFile = sys.argv[1]
        proceeFile(cn_font, newFile)

    window.close()

def proceeFile(cn_font, newFile):
    if not newFile:
        print("No filename supplied")
    elif '.xls' in newFile:
        print('The filename you chose was: ', newFile)
        myUtils.createShipTrackLinesKmlFile(newFile)
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