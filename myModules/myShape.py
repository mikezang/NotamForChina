import numpy as np
from shapely.ops import transform
from shapely.geometry import Polygon, LineString, Point
from pyproj import Transformer, CRS
from cartopy.io.shapereader import Reader
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cartopy.feature as cfeature
import cartopy.crs as ccrs
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import geopandas as gpd
import geoplot
from os import environ, makedirs, walk, path
from PIL import Image
from math import acos, sqrt, degrees, pi, ceil, floor
from simplekml import Kml
import PySimpleGUI as sg
import io

from myModules import myUtils
from myModules import myExcept
from myModules import myMath
from myModules import myExcel
from myModules import myKml
from myModules import myFile

KML_FOLDERS = {
    '酒泉' : r'notams/maps/01.酒泉',
    '西昌' : r'notams/maps/02.西昌',
    '太原' : r'notams/maps/03.太原',
    '文昌' : r'notams/maps/04.文昌',
    '海南' : r'notams/maps/05.海南',
    '海上' : r'notams/maps/10.海上',
    '黄海' : r'notams/maps/10.海上',
    '东海' : r'notams/maps/10.海上',
    '南海' : r'notams/maps/10.海上',
}

TEMP_FILE_PATH = './temp/'
NSF_PATH = './notams/maps/nsf/'
KML_PATH = './temp/'
MAP_SHAPES_FOLDER = './natural_earth_vector'
MAP_SHAPES_PATH_110m = f'{MAP_SHAPES_FOLDER}/110m_cultural'
COUNTRIES_SHAPE_110m = f'{MAP_SHAPES_PATH_110m}/ne_110m_admin_0_countries.shp'
MAP_SHAPES_PATH = f'{MAP_SHAPES_FOLDER}/$_cultural'
MAP_SHAPES_LIST_110m = [
	f'{MAP_SHAPES_PATH_110m}/ne_110m_admin_0_countries.shp', 
	f'{MAP_SHAPES_PATH_110m}/ne_110m_admin_0_countries_lakes.shp', 
	f'{MAP_SHAPES_PATH_110m}/ne_110m_admin_0_boundary_lines_land.shp', 
	f'{MAP_SHAPES_PATH_110m}/ne_110m_admin_0_countries_lakes.shp', 
	f'{MAP_SHAPES_PATH_110m}/ne_110m_admin_1_states_provinces_lakes.shp'
]

environ['PYPROJ_GLOBAL_CONTEXT'] = 'ON'

#coords(longitude経度, latitude緯度)

#####################################################################################
def interpolatePolylines(coordsListCity, num_points_per_segment=20):
    points = []

    # Adjust for smoother curves
    for i in range(len(coordsListCity) - 1): 
        lng1, lat1 = coordsListCity[i] 
        lng2, lat2 = coordsListCity[i + 1] 
    
        # Create a bezier-like curve (for simplicity, we just interpolate)
        for t in np.linspace(0, 1, num_points_per_segment): 
            lat = (1 - t) * lat1 + t * lat2 # Linear interpolation 
            lng = (1 - t) * lng1 + t * lng2 
            points.append((lng, lat)) 
    return points

#####################################################################################
def drawRoutePolyline(kml, city, centerCoords, seaCoord=None):
    cities = [city[i:i + 2] for i in range(0, len(city), 2)]
    coordsListSort = sorted(centerCoords, key=lambda x: x[1], reverse=True)
    for c in cities:
        coordsListCity = coordsListSort.copy()
        if c == '海上':
            coordsListCity.insert(0, seaCoord[c])
        else:
            coordsListCity.insert(0, myUtils.getCityCoordinate(c))

        points = coordsListCity
        lon0, lat0 = points[0]
        lon2, lat2 = points[-1]
        angle = myMath.great_circle_angle(lat0, lon0, lat2, lon2)

        # Add a polyline string to the KML
        ls = kml.newlinestring(name=f'{c}{angle:.1f}°轨道')
        ls.style.linestyle.color = 'ff000000'
        ls.style.linestyle.width = 1
        ls.coords = points

        # change all polygon color
        # color = myExcel.CITIES[c].split('|')[2]
        # color = myFile.readConfig(c, False).split(',')[1]
        # for feature in kml.features:
        #     feature.style.polystyle.color = color

#####################################################################################
def drawRouteLine(kml, city, highestPoint, lowestPoint=None, seaCoord=None) -> None:
    cities = [city[i:i + 2] for i in range(0, len(city), 2)]
    for c in cities:
        if c == '海上':
            cityCoord = seaCoord[c]
        else:
            cityCoord = myUtils.getCityCoordinate(c)

        if len(highestPoint) == 0:
            highestPoint = lowestPoint

        if cityCoord[0] == '' or cityCoord[1] == '':
            cityCoord = highestPoint
        
        lon0, lat0 = cityCoord
        lon2, lat2 = lowestPoint = lowerLatitude(cityCoord, lowestPoint)
        angle = myMath.great_circle_angle(lat0, lon0, lat2, lon2)

        ls = kml.newlinestring(name=f'{c}{angle:.1f}°轨道')
        ls.style.linestyle.color = 'ff000000'
        ls.style.linestyle.width = 1
        ls.coords = [cityCoord, lowestPoint]

        # change all polygon color
        # color = myExcel.CITIES[c].split('|')[2]
        # color = myFile.readConfig(c, False).split(',')[1]
        # for feature in kml.features:
        #     feature.style.polystyle.color = color

#####################################################################################
def higherLatitude(coord1, coord2):
    return coord1 if coord1 and coord2 and coord1[1] > coord2[1] else coord2

#####################################################################################
def lowerLatitude(coord1, coord2):
    if not coord1 and not coord2:
        return None, None
    elif coord1 and coord2:
        return coord1 if coord1[1] < coord2[1] else coord2
    elif coord1:
        return coord1
    else:
        return coord2
    # return coord1 if coord1 and coord2 and coord1[1] < coord2[1] else coord2

#####################################################################################
def getAreaCenter(coordsList) -> tuple:
    lon, lat = zip(*[(l[0], l[1]) for l in coordsList if l])
    lons, lats = sum(lon)/len(lon), sum(lat)/len(lat)
    return [lons + 180, lats] if lons < 0 and lons > -10 else [lons, lats]

#####################################################################################
def getNorthSideCenter(coordsList) -> tuple:
    sortedByLatitudes = sorted(coordsList, key=lambda x: x[0])
    northSide = sortedByLatitudes[:2]
    centerPoint = ((northSide[0][0] + northSide[1][0]) / 2, (northSide[0][1] + northSide[1][1]) / 2)
    return centerPoint

#####################################################################################
def getSouthSideCenter(coordsList) -> tuple:
    sortedByLatitudes = sorted(coordsList, key=lambda x: x[0])
    southSide = sortedByLatitudes[2:]
    centerPoint = ((southSide[0][0] + southSide[1][0]) / 2, (southSide[0][1] + southSide[1][1]) / 2)
    return centerPoint

#####################################################################################
def getSatrtEndCoords(lowestPoint, highestPoint, coordsList, lastCity, city, loc=None, seaCoord=[]) -> tuple:
    if len(coordsList) > 2:
        # p1 = getSouthSideCenter(coordsList)
        # p2 = getNorthSideCenter(coordsList)
        p2 = getAreaCenter(coordsList)
        highestPoint = higherLatitude(highestPoint, p2)
        lowestPoint = lowerLatitude(lowestPoint, p2)
        lastCity = city if lastCity == '' or highestPoint == p2 else lastCity
    elif len(coordsList) == 1:
        lastCity = city if lastCity == '' else lastCity
        seaCoord['海上'] = coordsList[0]
        highestPoint = higherLatitude(highestPoint, coordsList[0])
        if loc in 'ZSHA,ZGZU,RCAA':
            seaCoord['海上'] = higherLatitude(seaCoord['海上'], highestPoint)
            lastCity = lastCity + '海上' if lastCity.find('海上') < 0 else lastCity
            lowestPoint = lowerLatitude(lowestPoint, coordsList[0])
    return lastCity, highestPoint, lowestPoint, seaCoord

#####################################################################################
def showRouteAngle(newFile, newNames):
    gdf = myKml.readKmlFile(newFile)
    if gdf is None:
        return None
    startPoint, endPoint = [], []

    for name, geom in zip(gdf.Name, gdf.geometry):
        point = (geom.centroid.x, geom.centroid.y)
        startPoint = higherLatitude(startPoint, point)
        endPoint = lowerLatitude(endPoint, point)

    lon0, lat0 = startPoint
    lon1, lat1 = endPoint
    angle2 = myMath.great_circle_angle(lat0, lon0, lat1, lon1)
    lon2, lat2 = myMath.great_circle_point(lat0, lon0, lat1, lon1, distance=100)
    lat3, lon3, angle3, angle3Final = myMath.getBearing(lat0, lon0, lat1, lon1)
    sg.popup_ok(f'The route bearing is {angle2:.1f}°', font=('Noto Serif CJK JP', 18))

#####################################################################################
def createFirBoundaryKmlFile(title, boundary):
    kml = Kml()
    for city, coordinates in boundary.items():
        if coordinates:
            pol = kml.newpolygon(name=city)
            res = [(sub[1], sub[0]) for sub in coordinates]
            pol.outerboundaryis = res
            pol.style.polystyle.outline = 1
    updateKmlFile(kml, title, NSF_PATH)

#####################################################################################
def saveKmlFile(kml: Kml, title: str, filePath=''):
    print(f'Save to file "{filePath}{title}.kml"\n')
    kml.document.name = title
    kml.save(f'{filePath}{title}.kml') # this is for check content

#####################################################################################
def updateKmlFile(kml: Kml, title: str, filePath='', notams=None):
    try:
        filename = f'{filePath}{title}.kml'
        myFile.createFolder(filePath)
        with open(filename, encoding='utf-8') as f:
            kmlOld = f.read()
            kml.document.name = title
            kmlNew = kml.kml()
            if kmlOld != kmlNew:
                saveKmlFile(kml, title, filePath)
                # if notams:
                #     myFile.updateTempFile(notams)
            else:
                filename = ''
                print(f'Not update to file "{filePath}{title}.kml"\n')
    except FileNotFoundError:
        saveKmlFile(kml, title, filePath)
        # if notams:
        #     myFile.updateTempFile(notams)
    return filename

#####################################################################################
def createKmlFile(notams, title1='', city1='') -> None:
    kml = Kml()
    lastStartDate = ''
    lastEndDate = ''
    lastCity = ''
    highestPoint = []
    lowestPoint = []
    coordsList = []
    seaCoord = {}
    centerCoords = []
    kmlFiles = []
    isFirst = True
    for number, item in notams.items():
        itemArray = item.split(';')
        startDate = itemArray[0]
        endDate = itemArray[1]
        loc = itemArray[2]
        city = myUtils.convertLocation(itemArray[2]) if city1 == '' else city1
        coordsArray = itemArray[3].split('-')

        # plot range with all coords for special case
        if len(coordsArray) > 1:
            coordsAll = itemArray[3].replace('-', '|')
            coordsArray.append(coordsAll)

        for arr in coordsArray:
            coords = arr.split('|')
            if len(coords) == 1:
                radius = coords[0].split('+')
                coords = [radius[0]]
                radius.append(10) if len(radius) == 1 else radius
            else:
                radius = [0, 10]
            coordsList = [myFile.convertDMS2DD(c) for c in coords]

            if lastStartDate == '' or myUtils.isNearTime(lastStartDate, startDate, 59):
                center = getAreaCenter(coordsList)
                if center not in centerCoords:
                    centerCoords.append(center)
                if isFirst:
                    launchCity, isFirst = getLaunchCity(city, coordsList, loc)
                                    
                drawStages(kml, coordsList, launchCity, number, int(radius[1]))
                lastCity, highestPoint, lowestPoint, seaCoord = getSatrtEndCoords(lowestPoint, highestPoint, coordsList, lastCity, launchCity, loc, seaCoord)
            else:
                # newCity = compareKmls(newKml=kml)
                drawRoutePolyline(kml, launchCity, centerCoords, seaCoord)
                isFirst = True
                title = myFile.convertTitle(lastStartDate, lastEndDate, launchCity, launchCity) if title1 == '' else title1
                newKmlFile = updateKmlFile(kml, title, KML_PATH, notams)
                if newKmlFile:
                    kmlFiles.append(newKmlFile)
                centerCoords = []
                highestPoint = []
                lowestPoint = []
                seaCoord = {}
                lastCity = ''

                kml = Kml()
                center = getAreaCenter(coordsList)
                if center not in centerCoords:
                    centerCoords.append(center)
                if isFirst:
                    launchCity, isFirst = getLaunchCity(city, coordsList, loc)
                drawStages(kml, coordsList, launchCity, number, int(radius[1]))
                lastCity, highestPoint, lowestPoint, seaCoord = getSatrtEndCoords(lowestPoint, highestPoint, coordsList, lastCity, launchCity, loc, seaCoord)
            lastStartDate = startDate
            lastEndDate = endDate

    drawRoutePolyline(kml, launchCity, centerCoords, seaCoord)
    title = myFile.convertTitle(lastStartDate, lastEndDate, launchCity, launchCity) if title1 == '' else title1
    newKmlFile = updateKmlFile(kml, title, KML_PATH, notams)
    if newKmlFile:
        kmlFiles.append(newKmlFile)
    return kmlFiles

###############################################################################
def convertKmlToGdf(kml):
    kmlData = []
    for feature in kml.features():
        if isinstance(feature, Kml.Point):
            geometry = Point(feature.coords[0])
            kmlData.append({"Name" : feature.name, "Description": feature.description, "Geometry":geometry})
        elif isinstance(feature, Kml.LineString):
            geometry = LineString(feature.coords)
            kmlData.append({"Name" : feature.name, "Description": feature.description, "Geometry":geometry})
        elif isinstance(feature, Kml.Polygon):
            geometry = LineString(feature.outerboundaryis)
            kmlData.append({"Name" : feature.name, "Description": feature.description, "Geometry":geometry})
    gdf = gpd.GeoDataFrame(kmlData)
    return gdf

################################################################################################
def compareKmls(newFile=None, newKml=None):
    if newKml:
        newGdf = convertKmlToGdf(newKml)
    else:
        locationList, locations = myFile.getLocation(newFile)
        if locationList is None:
            print(f'{newFile} not included {locations}')
            return ''
    
    from myModules import myPlot
    cn_font = myPlot.init()
    newGdf = myKml.readKmlFile(newFile)
    if newGdf.empty:
        print(f"No Data in {newFile}!")
        return 

    for location in locationList:
        folder = path.abspath(KML_FOLDERS[location])
        if not path.isdir(folder):
            makedirs(folder, True)
        filename = path.basename(newFile)

        # delete files
        myFile.removeFile(f'{TEMP_FILE_PATH}match/*.png')
        myFile.removeFile(f'{TEMP_FILE_PATH}unmatch/*.png')

        # List all kml files in specific foder except newFile
        oldFiles = myFile.listFiles(folder, extension=".kml", excludeFile=filename)
        savePath1 = f'{TEMP_FILE_PATH}match/{filename[:-4]}'
        savePath2 = f'{TEMP_FILE_PATH}unmatch/{filename[:-4]}'
        
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
                    fig, ax = getFigure(setAspectEqual=True, plotGrid=True)
                except Exception as e:
                    print(f"No Data in {oldFile}!")
                    print(f'Exception: {e}\n')

                plotTwoNoatms(ax, newGdf, oldGdf)
                newTitle = myFile.getTitle(newFile)
                newTitle = newTitle if '时' in newTitle else newTitle.replace('日', '日??时??分')
                oldTitle = myFile.getTitle(oldFile)
                ious, title = plotPolygonsIntersection(fig, ax, cn_font, newGdf, newTitle, oldGdf, oldTitle)
                plotTitleXYLabels(fig, ax, cn_font, title, 'Longitude（经度）', 'Latitude（纬度）')
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

#####################################################################################
def drawStages(kml, coords, city, location, radius=10) -> None:
    if coords:
        cities = [city[i:i + 2] for i in range(0, len(city), 2)]
        count = len(coords)
        for c in cities:
            color = myFile.readConfig(c)[1]
            # color = myExcel.CITIES[c].split('|')[2]
            if count == 1:
                drawCircle(kml, coords, location, color, radius)
            elif count == 2:
                drawLine(kml, coords, location, color)
            else: #if  location == 'MSAC':
                lon1, lat1, lon2, lat2 = coords[0][0], coords[0][1], coords[-1][0], coords[-1][1]
                distance = myMath.haversine(lon1, lat1, lon2, lat2)
                if distance < 150 or location != 'MSAC': # distance less than 150km between first and last point
                    drawPolygon(kml, coords, location, color)
                else:
                    drawLine(kml, coords, location, color)
            break
    return coords

#####################################################################################
def drawPolygon(kml, coords, location, color=None) -> None:
    pol = kml.newpolygon(name=location)
    pol.outerboundaryis = coords
    pol.style.polystyle.color = color if color is not None else 'black'
    pol.style.polystyle.outline = 0
    pol.style.linestyle.width = 0

#####################################################################################
def drawDottedLine(kml, coords, location, color) -> None:
    for i in range(len(coords) - 1):
        for j in range(1, len(coords)):
            coordsDiff = [(coords[j][0] - coords[i][0]) / 50, (coords[j][1] - coords[i][1]) / 50]
            for k in range(0, 50, 2):
                lat1, lon1 = coords[i][0] + coordsDiff[0] * k, coords[i][1] + coordsDiff[1] * k
                lat2, lon2 = lat1 + coordsDiff[0], lon1 + coordsDiff[1]
                dotted = ((lat1, lon1), (lat2, lon2))
                drawLine(kml, dotted, location, color)

#####################################################################################
def drawLine(kml, coords, location=None, color=None) -> None:
    line = kml.newlinestring(name=location)
    line.coords = coords
    line.style.linestyle.color = color if color is not None else 'black'
    line.style.linestyle.width = 1

#####################################################################################
# distance in km
def drawCircle(kml, coords, location, color, radius=3):
    circle = circleByPoint(coords[0][1], coords[0][0], radius)
    # circle = [(lon, lat) for lat, lon in buffer]
    drawLine(kml, circle, location, color)
    # drawPolygon(kml, circle, location, color)

#####################################################################################
def find_shapefiles(mapsPath=MAP_SHAPES_PATH, resolution='110m'):
    """Recursively find all .shp files in the given directory and subdirectories."""
    shapefiles = []
    for root, _, files in walk(mapsPath.replace('$', resolution)):
        for file in files:
            if file.endswith('.shp'):
                shapefiles.append(path.join(root, file))
    return shapefiles

#####################################################################################
def add_shapefile_to_cartopy(ax, shapefile_path, **kwargs):
    """Add a shapefile to the Cartopy plot."""
    shape_feature = cfeature.ShapelyFeature(
        Reader(shapefile_path).geometries(),
        ccrs.PlateCarree(),
        **kwargs
    )
    ax.add_feature(shape_feature)

#####################################################################################
# alculate Jaccard index of Two Geometries
def getIntersectionOverUnion(newGdf, oldGdf):
    iouDict = {}

    for newGeo, newName in zip(newGdf.geometry, newGdf.Name):
        if isinstance(newGeo, Polygon):
            for oldGeo, oldName in zip(oldGdf.geometry, oldGdf.Name):
                if isinstance(oldGeo, Polygon):
                    geomName = f'{newName} IoU {oldName}'
                    iou = 0.0
                    intersection = newGeo.intersection(oldGeo)

                    if intersection:
                        try:
                            union = newGeo.union(oldGeo)
                            iou = 0.0 if union.area == 0.0 else intersection.area / union.area
                        except Exception as e:
                            pass
                    if iou > 0.01:
                        text = f'{geomName} = {iou:05.1%}'
                        iouDict[text] = gpd.GeoDataFrame(geometry=[intersection])
    return iouDict

#####################################################################################
def readFile(file):
    return gpd.read_file(path.abspath(file))

#####################################################################################
def getFigure(nrows=1, ncols=1, figsize=(18, 10.5), setAspectEqual=False, plotGrid=False):
    fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)
    if setAspectEqual:
        ax.set_aspect('equal')
    if plotGrid:
        ax.xaxis.set_major_formatter(LONGITUDE_FORMATTER)
        ax.yaxis.set_major_formatter(LATITUDE_FORMATTER)
        plt.grid(True, color='red', linestyle='-.', linewidth=0.5)
    return fig, ax

#####################################################################################
def plotTitleXYLabels(fig, ax, cn_font, title, xLabel, yLabel):
    ax.set_title(title, fontproperties=cn_font, fontsize=14, loc='center') # plot title
    # ax[0].axis('off') # Hide the border of the subplot
    ax.set_xlabel(xLabel, fontproperties=cn_font)  # Add an x-label to the axes.
    ax.set_ylabel(yLabel, fontproperties=cn_font)  # Add a y-label to the axes.

    handles = [
        Line2D([0], [0], linestyle='none', mfc='blue', mec='blue', marker='s', label='新落区'),
        Line2D([0], [0], linestyle='none', mfc='green', mec='green', marker='s', label='旧落区'),
        Line2D([0], [0], linestyle='none', mfc='orange', mec='orange', marker='s', label='重叠落区')
    ]
    
    # fig.legend(handles=handles, bbox_to_anchor=(0.1, 0), ncol=3) # add legend
    fig.legend(handles=handles, loc='lower center', ncol=3, fontsize=12, prop=cn_font)

#####################################################################################
def plotPolygonsIntersection(fig, ax, cn_font, newPolys, newTitle, oldPolys=None, oldTitle=''):
    # Calculate NOTAM drop zones Jaccard Similarity Index and plot intersection polygons
    ious = plotIntersection(ax, newPolys, oldPolys)
    # plot title, axis and NOTAM drop zones
    title = f'{newTitle}\n{oldTitle}'
    for ios in ious:
        title += f'\n{ios}'
    return ious, title

#####################################################################################
def customRound(num):
    return num#ceil(num) if num >=0 else floor(num)

#####################################################################################
def getLimits(gdf, plotLines=False, plotPoints=False):
    if plotLines and plotPoints:
        gdf = gdf
    else:
        isPolygons = gdf.geometry.geom_type == 'Polygon'
        isLines = gdf.geometry.geom_type == 'LineString'
        isPoints = gdf.geometry.geom_type == 'Point'
        if plotLines and not plotPoints:
            gdf = gdf[~isPoints]
        elif not plotLines and plotPoints:
            gdf = gdf[~isLines]
        elif not plotLines and not plotPoints:
            if isPolygons.any():
                gdf = gdf[isPolygons]
            elif isLines.any():
                gdf = gdf[isLines]
            elif isPoints.any():
                gdf = gdf[isPoints]
            else:
                sg.popup_error(f'gdf is empty!', font=('Noto Serif CJK JP', 18))
                return -1, 1, -1, 1
    minLatitude = customRound(gdf.bounds.miny.min()) - 1
    maxLatitude = customRound(gdf.bounds.maxy.max()) + 1
    minLongitude = customRound(gdf.bounds.minx.min()) - 1
    maxLongiitude = customRound(gdf.bounds.maxx.max()) + 1
    return minLongitude, minLatitude, maxLongiitude, maxLatitude

#####################################################################################
def getExtent(newGdf, oldGdf=None, plotLines=False, plotPoints=False):
    if oldGdf is None:
        return getLimits(newGdf, plotLines, plotPoints)
    newMinLongitute, newMinLatitude, newMaxLongitute, newMaxLatitude  = getLimits(newGdf, plotLines, plotPoints)
    oldMinLongitute, oldMinLatitude, oldwMaxLongitute, oldMaxLatitude = getLimits(oldGdf, plotLines, plotPoints)
    minLongitude = min(newMinLongitute, oldMinLongitute)
    minLatitude = min(newMinLatitude, oldMinLatitude)
    maxLongitude = max(newMaxLongitute, oldwMaxLongitute)
    maxLatitude = max(newMaxLatitude, oldMaxLatitude)
    minLongitude = customRound(minLongitude)
    minLatitude = customRound(minLatitude)
    maxLongitude = customRound(maxLongitude)
    maxLatitude = customRound(maxLatitude)
    extent = [minLongitude, minLatitude, maxLongitude, maxLatitude]
    return extent

#####################################################################################
def adjustLimitsExtent(ax, extent):
    return adjustLimits(ax, extent[0], extent[1], extent[2], extent[3])

#####################################################################################
def adjustLimits(ax, minLon, minLat, maxLon, maxLat):
    lon21 = maxLon - minLon
    lat21 = maxLat - minLat
    ratio1 = lat21 / lon21

    if lon21 < lat21:
        dLon = lon21 * (ratio1 - 1) / 2
        ax.set_xlim(customRound(minLon - dLon), customRound(maxLon + dLon))
        ax.set_ylim(minLat, maxLat)
    else:
        dLat = lat21 * (1 - ratio1) / ratio1 / 2
        ax.set_xlim(minLon, maxLon)
        ax.set_ylim(customRound(minLat - dLat), customRound(maxLat + dLat))

    minLon1, maxLon1 = ax.get_xlim()
    minLat1, maxLat1 = ax.get_ylim()
    # ratio2 = (lat2 - lat1) / (lon2 - lon1)
    # print(f'Ratio1: {ratio1:0.2f}, Ratio2: {ratio2:0.2f}')
    return minLon1, minLat1, maxLon1, maxLat1

#####################################################################################
def getGdfPolygons(gdf):
    # return gdf[gdf['geometry'].apply(lambda x: isinstance(x, Polygon))]
    return gdf[gdf.geometry.geom_type == 'Polygon']

#####################################################################################
def getGdfLines(gdf):
    return gdf[gdf.geometry.geom_type == 'LineString']

#####################################################################################
def getGdfPoints(gdf):
    return gdf[gdf.geometry.geom_type == 'Point']

#####################################################################################
def plotTwoNoatms(ax, newGdf, oldGdf=None, plotLines=False, plotPoints=False, plotNames=False, plotWorldMap=True, isAdjustLimit=True, font=None, newNames=None, oldNames=None):
    if isAdjustLimit:
        extent = getExtent(newGdf, oldGdf, plotLines, plotPoints)
        # print(f'{extent[2] - extent[0] = }')
        # print(f'{extent[3] - extent[1] = }')
        extent = adjustLimits(ax, extent[0], extent[1], extent[2], extent[3])
    else:
        extent = None
    plotGeometry(ax, newGdf, extent=extent, color='blue', ha='left', plotLines=plotLines, plotPoints=plotPoints, plotNames=plotNames, font=font, names=newNames)

    if oldGdf is not None:
        plotGeometry(ax, oldGdf, extent=extent, color='green', ha='right', plotLines=plotLines, plotPoints=plotPoints, plotNames=plotNames, font=font, names=oldNames)

    if isAdjustLimit:
        minLon, maxLon = ax.get_xlim()
        minLat, maxLat = ax.get_ylim()
        # extent = getExtent(newGdf, oldGdf)

    if plotWorldMap:
        # worldmap = readFile(geodatasets.get_path("naturalearth.land"))
        worldmap = readFile(COUNTRIES_SHAPE_110m)
        worldmap["geometry"].boundary.plot(facecolor="lightgrey", color="grey", ax=ax, zorder=1)

    if isAdjustLimit:
        # extent = adjustLimits(ax, extent[0], extent[1], extent[2], extent[3])
        adjustLimits(ax, minLon, minLat, maxLon, maxLat)

#####################################################################################
def plotCartopyTwoNoatms(ax, newGdf, oldGdf=None, plotLines=False, plotNames=False, plotWorldMap=True, isAdjustLimit=True, font=None):
    extent = getExtent(newGdf, oldGdf)
    extent = adjustLimitsExtent(ax, extent)

    newGdfPolygons = getGdfPolygons(newGdf)
    newGdfLines = getGdfLines(newGdf)
    plotCartopyPolygons(newGdfPolygons, ax, extent=extent, color='blue', ha='left', font=font, plotNames=plotNames)

    if plotLines:
        plotCartopyLines(newGdfLines, ax, extent=extent, color='blue', ha='left', font=font, plotNames=plotNames)

    if oldGdf is not None:
        extent = getExtent(newGdf, oldGdf)
        extent = adjustLimitsExtent(ax, extent)

        # oldTitle = oldFile.replace('\\', '/') if myUtils.isWindows() else oldFile
        # title += '\n' + oldTitle.split('/')[-1]
        oldGdfPolygons = getGdfPolygons(oldGdf)
        plotCartopyPolygons(oldGdfPolygons, ax, extent=extent, color='green', ha='right', font=font, plotNames=plotNames)

        if plotLines:
            oldGdfLines = getGdfLines(oldGdf)
            plotCartopyLines(oldGdfLines, ax, extent=extent, color='green', ha='right', font=font, plotNames=plotNames)

#####################################################################################
def plotCartopyMaps(cn_font, newFile, oldFile=None, projectionName='PlateCarree', plotLines=False, plotPoints=False, plotNames=False, resolution='110m', newNames=None, oldNames=None):
    # Create a plot with Cartopy
    if not hasattr(ccrs, projectionName):
        try:
            raise ValueError(f'Projection "{projectionName}" not found.')
        except:
            myExcept.printExceptionTrace(True)

    newGdf = myKml.readKmlFile(newFile)
    # newNames = [name for name in newGdf.Name]
    newNames = getGeometryNames(newGdf, plotLines, plotPoints) if not newNames else newNames
    oldGdf = myKml.readKmlFile(oldFile) if oldFile else None
    # oldNames = [name for name in oldGdf.Name] if oldFile else []
    oldNames = getGeometryNames(oldGdf, plotLines, plotPoints) if not oldNames else oldNames

    fig = plt.figure(figsize=(16, 9))
    projectionClass = getattr(ccrs, projectionName)
    ax = plt.axes(projection=projectionClass())
    ax.set_aspect('equal')

    title = newFile.replace('\\', '/') if myFile.isWindows() else newFile
    title = title.split('/')[-1].replace('日', '日??时??分')

    extent = getExtent(newGdf, oldGdf)
    extent = adjustLimitsExtent(ax, extent)

    newGdfPolygons = getGdfPolygons(newGdf)
    newGdfLines = getGdfLines(newGdf)
    plotCartopyPolygons(newGdfPolygons, ax, extent=extent, color='blue', ha='left', font=cn_font, plotNames=plotNames)

    if plotLines:
        plotCartopyLines(newGdfLines, ax, extent=extent, color='blue', ha='left', font=cn_font, plotNames=plotNames)

    if oldFile:
        extent = getExtent(newGdf, oldGdf)
        extent = adjustLimitsExtent(ax, extent)

        oldTitle = oldFile.replace('\\', '/') if myFile.isWindows() else oldFile
        title += '\n' + oldTitle.split('/')[-1]
        oldGdfPolygons = getGdfPolygons(oldGdf)
        plotCartopyPolygons(oldGdfPolygons, ax, extent=extent, color='green', ha='right', font=cn_font, plotNames=plotNames)

        if plotLines:
            oldGdfLines = getGdfLines(oldGdf)
            plotCartopyLines(oldGdfLines, ax, extent=extent, color='green', ha='right', font=cn_font, plotNames=plotNames)
        
        gdfIntersectionOverUnion = getIntersectionOverUnion(newGdf, oldGdf)

        for name, gdf in gdfIntersectionOverUnion.items():
            title += f'\n{name}'
            iouGdfPolygons = getGdfPolygons(gdf)
            plotCartopyPolygons(iouGdfPolygons, ax, extent=extent, color='orange', zorder=5)

    # Add coastlines and other basic features
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0.5, linestyle='--', color='red')
    gl.top_labels = False
    gl.right_labels = False
    ax.coastlines(resolution=resolution, linewidth=0.1)
    # ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS.with_scale(resolution), linewidth=0.5)
    ax.add_feature(cfeature.LAND.with_scale(resolution), linewidth=0.5)
    ax.add_feature(cfeature.OCEAN.with_scale(resolution), linewidth=0.5)
    ax.add_feature(cfeature.LAKES.with_scale(resolution), linewidth=0.5)
    ax.add_feature(cfeature.RIVERS.with_scale(resolution), linewidth=0.5)

    # Add each found shapefile to the plot
    for shp in MAP_SHAPES_LIST_110m:
        add_shapefile_to_cartopy(ax, shp, edgecolor='black', facecolor='none')

    # ax.set_title(f'Map with Projection: {projectionName}')
    plotTitleXYLabels(fig, ax, cn_font, title, 'Longitude（经度）', 'Latitude（纬度）')
    return fig, newNames, oldNames

#####################################################################################
def getGeometryNames(gdf, plotLines, plotPoints):
    if gdf is not None:
        names = {}
        for name, geomType in zip(gdf.Name, gdf.geometry.geom_type):
            isPolygon = geomType == 'Polygon'
            isLineString = geomType == ('LineString' and plotLines)
            isPoint = geomType == ('Point' and plotPoints)
            # names[name] = True if geomType == 'Polygon' or (geomType == 'LineString' and plotLines) or (geomType == 'Point' and plotPoints) else False
            names[name] = True if isPolygon or isLineString or isPoint else False
    else:
        names = None
    return names

#####################################################################################
def plotMaps(cn_font, newKmlFile, oldKmlFile=None, plotLines=False, plotPoints=False, plotNames=False, newNames=None, oldNames=None):
    newGdf = myKml.readKmlFile(path.abspath(newKmlFile), False)
    if newGdf is None:
        return None, None, None
    newNames = getGeometryNames(newGdf, plotLines, plotPoints) if not newNames else newNames

    oldGdf = myKml.readKmlFile(oldKmlFile, False) if oldKmlFile else None
    oldNames = getGeometryNames(oldGdf, plotLines, plotPoints) if not oldNames else oldNames
        
    fig, ax = getFigure(setAspectEqual=True, plotGrid=True)
    plotTwoNoatms(ax, newGdf, oldGdf, plotLines=plotLines, plotPoints=plotPoints, plotNames=plotNames, font=cn_font, newNames=newNames, oldNames=oldNames)

    newTitle = myFile.getTitle(newKmlFile)
    if oldKmlFile:
        newTitle = newTitle if '时' in newTitle else newTitle.replace('日', '日??时??分')
        oldTitle = myFile.getTitle(oldKmlFile)
        _, newTitle = plotPolygonsIntersection(fig, ax, cn_font, newGdf, newTitle, oldGdf, oldTitle)

    plotTitleXYLabels(fig, ax, cn_font, newTitle, 'Longitude（经度）', 'Latitude（纬度）')
    return fig, newNames, oldNames

#####################################################################################
def getImageInMemoryFromFig(fig, dpi=96, resize=False, size=myExcel.IMAGE_SIZE):
    buf = io.BytesIO()
    fig.savefig(buf, bbox_inches='tight', dpi=dpi, format='png')
    if resize:
        buf.seek(0)
        img = Image.open(buf)
        img_resize = img.resize(size, Image.LANCZOS)
        with io.BytesIO() as buf1:
            img_resize.save(buf1, format='PNG')
            imagePng = buf1.getvalue()
    else:
        imagePng = buf.getvalue()
    buf.close()
    # graphic = base64.b64encode(imagePng)
    # graphic = graphic.decode('utf-8')
    return imagePng

#####################################################################################
def getImageFromKml(cn_font, newKmlFile, oldKmlFile=None, size=myExcel.IMAGE_SIZE, projection=False, plotLines=False, plotPoints=False, plotNames=False, newNames=None, oldNames=None):
    if plt:
        plt.close()

    if projection:
        projectionName = 'Mercator'
        # projectionName = 'PlateCarree'
        fig, newNames, oldNames = plotCartopyMaps(cn_font, newKmlFile, oldKmlFile, projectionName, plotLines=plotLines, plotPoints=plotPoints, plotNames=plotNames, newNames=newNames, oldNames=oldNames)
    else:
        fig, newNames, oldNames = plotMaps(cn_font, newKmlFile, oldKmlFile, plotLines=plotLines, plotPoints=plotPoints, plotNames=plotNames, newNames=newNames, oldNames=oldNames)

    if not fig:
        return None, newNames, oldNames
    image = getImageInMemoryFromFig(fig, resize=True, size=size)
    return image, newNames, oldNames

#####################################################################################
def plotCartopyPolygons(gdf, ax, extent=None, color=None, ha=None, zorder=2, font=None, plotNames=None):
    try:
        geoplot.polyplot(gdf, ax=ax, extent=extent, facecolor=color, color=color, zorder=zorder)
        crs = ccrs.PlateCarree()
        transform = crs._as_mpl_transform(ax)
        if plotNames:
            plotAnnotate(ax, gdf, color, ha, 10, font, transform)
    except:
        pass

#####################################################################################
def plotCartopyLines(gdf, ax, extent=None, color=None, ha=None, zorder=1, font=None, plotNames=None):
    # geoplot.polyplot(gdf, ax=ax, extent=extent, facecolor='none', color=color, linewidth=0.5, zorder=zorder)
    lons, lats = gdf.geometry.iloc[0].xy
    ax.plot(lons, lats, transform=ccrs.Geodetic(), color=color, zorder=zorder+1)
    if plotNames:
        plotAnnotate(ax, gdf, color, ha, 10, font, ccrs.PlateCarree()._as_mpl_transform(ax))

#####################################################################################
def plotAnnotate(ax, gdf, color, ha, fontsize, font=None, transform=None):
    if hasattr(gdf, 'Name'):
        for label, bound, geometry in zip(gdf.Name, gdf.bounds.iloc, gdf.geometry.iloc):
            if 'MSA' not in label and ha:
                x, y = geometry.centroid.coords[0]
                if geometry.geom_type == 'LineString':
                    x += 1 if ha == 'left' else -1
                else:
                    x = bound.maxx if ha == 'left' else bound.minx
                if transform:
                    ax.annotate(label, xy=(x, y), xytext=(x, y), xycoords=transform, ha=ha, va='center', color=color, fontsize=fontsize, font=font)
                else:
                    ax.annotate(label, xy=(x, y), xytext=(x, y), ha=ha, va='center', color=color, fontsize=fontsize, font=font)

#####################################################################################
def plotGeometry(ax, gdf, extent=None, color=None, ha=None, legend=None, lables=None, plotLines=False, plotPoints=False, plotNames=False, zorder=2, font=None, names=None):
    if isinstance(gdf, gpd.GeoDataFrame):
        if names:
            # names = dict(names) if isinstance(names, list) else names
            for name, isShow in names.items():
                geomGdf = gdf[gdf.Name == name]
                if not geomGdf.empty:
                    if isShow:
                        if (geomGdf.geometry.geom_type == 'Polygon').all():
                            geomGdf.plot(ax=ax, facecolor=color, color=color, zorder=zorder)
                        else:
                            geomGdf.plot(ax=ax, color=color, zorder=zorder+1)
                        if plotNames:
                            plotAnnotate(ax, geomGdf, color, ha, 14, font)
                    else:
                        plotAnnotate(ax, geomGdf, 'none', ha, 14, font)
        else:
            polyGdf = gdf[gdf.geometry.geom_type=='Polygon']
            # polyGdf = gdf[gdf['geometry'].apply(lambda x: isinstance(x, Polygon))]
            polyGdf.plot(ax=ax, facecolor=color, color=color, zorder=zorder)
            if plotNames:
                plotAnnotate(ax, polyGdf, color, ha, 14, font)

            if plotLines:
                lineGdf = gdf[gdf.geometry.geom_type=='LineString']
                if not lineGdf.empty:
                    lineGdf.plot(ax=ax, color=color, zorder=zorder+1)
                if plotNames:
                    plotAnnotate(ax, lineGdf, color, ha, 14, font)

            if plotPoints:
                pointGdf = gdf[gdf.geometry.geom_type=='Point']
                if not pointGdf.empty:
                    pointGdf.plot(ax=ax, color=color, zorder=zorder+2)
                if plotNames:
                    plotAnnotate(ax, lineGdf, color, ha, 14, font)

#####################################################################################
def plotIntersection(ax, newGdf, oldGdf):
    newIndex = 0
    ious = []

    for i, newGeom in enumerate(newGdf.geometry):
        if isinstance(newGeom, Polygon):
            oldIndex = 0
            newIndex += 1
            newName = newGdf.iloc[i]["Name"]

            for j, oldGeom in enumerate(oldGdf.geometry):
                if isinstance(oldGeom, Polygon):
                    oldIndex += 1
                    oldName = oldGdf.iloc[j]["Name"]
                    geomName = f'{newName} IoU {oldName}'
                    iou = 0.0

                    if newGeom.intersects(newGeom):
                        try:
                            intersection = newGeom.intersection(oldGeom)
                            union = newGeom.union(oldGeom)
                            iou = 0.0 if union.area == 0.0 else intersection.area / union.area
                        except Exception as e:
                            pass
                    if iou > 0.01:
                        text = f'{geomName} = {iou:05.1%}'
                        ious.append(text)
                        plotGeometry(ax, gpd.GeoDataFrame(geometry=[intersection]), color='orange', legend=text, zorder=4)
    return ious

#####################################################################################
def circleByPoint(lat, lon, km=5):
    proj_wgs84 = CRS('EPSG:4326')
    proj_aeqd = CRS(f'+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0')
    transformer = Transformer.from_crs(proj_aeqd, proj_wgs84, always_xy=True)
    buf = Point(0, 0).buffer(km * 1000)  # distance in metres
    return transform(transformer.transform, buf).exterior.coords[:]

#####################################################################################
# Function to convert LineString to Points
def lineStringToPoints(gdf):
    points = []
    for line in gdf.geometry:
        if isinstance(line, LineString):
            for coord in line.coords:
                points.append(Point(coord))
    pointsGdf = gpd.GeoDataFrame(geometry=points, crs=gdf.crs)
    return pointsGdf

#####################################################################################
def lineStringToPoint(line):
    coords = line.coords
    points = [Point(coord) for coord in coords]
    return points

#####################################################################################
def lineStringToPointGdf(lineGdf):
    pointGeometries = []
    names = []
    descriptions = []

    for idx, row in lineGdf.iterrows():
        name = row['Name']
        points = [Point(coord) for coord in row['geometry'].coords]
        pointGeometries.extend(points)
        names.extend([name] * len(points))
        descriptions.extend([1 for i in range(len(points))])

    pointGdf = gpd.GeoDataFrame({
        'Name': names, 
        'description': descriptions,
        'geometry': pointGeometries
    }, crs=lineGdf.crs)
    return pointGdf

###############################################################################
def calculateAngle(point1, point2, point3):
    # angle = angle between line from point1 to point2 then to point3
    # a = length from point1 to point2
    #   = sqrt((lon1 - lon2) * (lon1 - lon2) + (lat1 - lat2) * (lat1 - lat2))
    # b = length from point3 to point2
    #   = sqrt((lon3 - lon2) * (lon3 - lon2) + (lat3 - lat2) * (lat3 - lat2))
    # c = length from point1 to point3
    #   = sqrt((lon1 - lon3) * (lon1 - lon3) + (lat1 - lat3) * (lat1 - lat3))
    # cos(θ) = (a * a + b * b - c * c) / (2 * a * b)
    # θ = acos((a * a + b * b - c * c) / (2 * a * b))
    lon1, lat1 = point1
    lon2, lat2 = point2
    lon3, lat3 = point3
    # lon2 = (lon2 + lon3) / 2
    # lat2 = (lat2 + lat3) / 2
    a = sqrt((lon2 - lon1) * (lon2 - lon1) + (lat2 - lat1) * (lat2 - lat1))
    b = sqrt((lon2 - lon3) * (lon2 - lon3) + (lat2 - lat3) * (lat2 - lat3))
    if a == 0 or b == 0:
        return 0
    c = sqrt((lon1 - lon3) * (lon1 - lon3) + (lat1 - lat3) * (lat1 - lat3))
    theta = acos((a * a + b * b - c * c) / (2 * a * b))
    # angleInDegrees = degrees(theta)
    return theta

###############################################################################
def sliceByLen(text, length):
    return [text[i:i + 2] for i in range(0, len(text), length)]

###############################################################################
def _getLaunchCity(launchCity, launchAngle, loc, city, cityPoint, top1, top2):
    angle = calculateAngle(cityPoint, top1, top2)
    if not launchCity or abs(pi / 2 - angle) < abs(pi / 2 - launchAngle):
        launchCity = city
        launchAngle = angle
    if degrees(abs(pi / 2 - angle)) < 5:
        launchCity += city if city not in launchCity else ''
    print(f'{city} to {loc}: {degrees(angle):6.2f}° = {launchCity}')
    return launchCity, launchAngle, angle

def _getLaunchCities(loc, cities, coordsList):
    launchCity = ''
    launchAngle = 0
    needAgain = False
    cityList = sliceByLen(cities, 2)
    for city in cityList:
        cityPoint = [float(x) for x in myFile.readConfig(city)[2].split('+')]
        top1, top2 = getTopCorners(coordsList)
        launchCity, launchAngle, angle = _getLaunchCity(launchCity, launchAngle, loc, city, cityPoint, top1, top2)
        needAgain = angle > pi / 2

        if needAgain or len(coordsList) > 4:
            top1, top2 = getTopCorners(coordsList, 2)
            launchCity, launchAngle, angle = _getLaunchCity(launchCity, launchAngle, loc, city, cityPoint, top1, top2)
    return launchCity, launchAngle

def _getCity(cities, coordsList):
    cityList = sliceByLen(cities, 2)
    launchCity = ''
    launchDistance = 0
    for city in cityList:
        cityPoint = [float(x) for x in myFile.readConfig(city)[2].split('+')]
        y = abs(cityPoint[0] - coordsList[0][0])
        x = abs(cityPoint[1] - coordsList[0][1])
        d = x * x + y * y
        if launchCity == '':
            launchCity = city
            launchDistance = d
        elif d < launchDistance:
            launchDistance = d
            launchCity = city
    return launchCity

###############################################################################
def getLaunchCity(cities, coordsList, loc):
    if len(cities) > 2:
        if len(coordsList) == 1: # launch spot
            launchCity = _getCity(cities, coordsList)
        elif len(coordsList) > 3: # drop zone
            launchCity, launchAngle = _getLaunchCities(loc, cities, coordsList)
    else:
        launchCity = cities
    isFirst = False if len(coordsList) > 3 else True
    return launchCity, isFirst

###############################################################################
def getTopCorners(coords, top=1):
    """
    Given a list of four coordinates (lon, lat) of a rectagle, return top corner:
    - p1 as the top-left corner (highest latitude, samllest longitude)
    - p2 as the top-right corner (hightest latitude, larest longitude)

    Args:
      coord (list of tuple): List of coordinates [(lon, lat), ...]
    
    Returns:
      tuple: p1 (left-top), p2(right-top)
    """
    sortedBylat = sorted(coords, key=lambda x: x[1], reverse=True)
    if top == 1:
        topPoints = sortedBylat[:2]
    else:
        topPoints = [sortedBylat[0], sortedBylat[2]]
    topPointsSortedByLon = sorted(topPoints, key=lambda x: x[0])
    p1 = topPointsSortedByLon[0]
    p2 = topPointsSortedByLon[1]
    return p1, p2

