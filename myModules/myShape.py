from datetime import datetime
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
from math import acos, atan2, cos, radians, sin, sqrt, degrees, pi
from simplekml import Kml
import FreeSimpleGUI as sg
import io

from myModules import myUtils
from myModules import myExcept
from myModules import myMath
from myModules import myExcel
from myModules import myKml
from myModules import myFile
from myModules import myConfig
from myModules import myDate
from myModules import mySys
from myModules import myPlotInit

ANGLE_RANGE = 12.03
TEMP_FILE_PATH = './temp/'
NSF_PATH = './notams/kmls/nsf/'
KML_PATH = './temp/'
# MAP_SHAPES_FOLDER = './natural_earth_vector'
# MAP_SHAPES_PATH_110m = f'{MAP_SHAPES_FOLDER}/110m_cultural'
MAP_SHAPES_FOLDER = './maps'
MAP_SHAPES_PATH_110m = f'{MAP_SHAPES_FOLDER}'
COUNTRIES_SHAPE_110m = f'{MAP_SHAPES_PATH_110m}/ne_110m_admin_0_countries.shp'
MAP_SHAPES_PATH = f'{MAP_SHAPES_FOLDER}/$_cultural'
MAP_SHAPES_LIST_110m = [
	f'{MAP_SHAPES_PATH_110m}/ne_110m_admin_0_countries.shp', 
	f'{MAP_SHAPES_PATH_110m}/ne_110m_admin_0_countries_lakes.shp', 
	f'{MAP_SHAPES_PATH_110m}/ne_110m_admin_0_countries_lakes.shp', 
	f'{MAP_SHAPES_PATH_110m}/ne_110m_admin_0_boundary_lines_land.shp', 
	f'{MAP_SHAPES_PATH_110m}/ne_110m_admin_1_states_provinces_lakes.shp'
]

environ['PYPROJ_GLOBAL_CONTEXT'] = 'ON'

#coords(longitude経度, latitude緯度)

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
    """
    Calculate centered (geometric center) of a polygon given as [(x, y), ...],
    The polygon should be closed (first == last), but it's okay if not.
    """
    if coordsList[0] != coordsList[-1]:
        coordsList = coordsList + [coordsList[0]]
    
    area = 0
    cx, cy = 0, 0
    for i in range(len(coordsList) - 1):
        x0, y0 = coordsList[i]
        x1, y1 = coordsList[i + 1]
        cross = x0 * y1 - x1 * y0
        area += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross

    area *= 0.5
    if area == 0: # fallback: average of points
        lon, lat = zip(*cross)
        cx, cy = sum(lon) / len(lon), sum(lat) / len(lat)
    else:
        cx /= (6 * area)
        cy /= (6 * area)
    return (cx, cy)

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
    angle2 = myMath.launch_azimuth(lat0, lon0, lat1, lon1)
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
    kml.document.name = title.split('-')[0]
    kml.save(f'{filePath}{title}.kml') # this is for check content

#####################################################################################
def updateKmlFile(kml: Kml, title: str, filePath='', suffix=''):
    try:
        filename = f'{filePath}{title}.kml'
        myFile.createFolder(filePath)

        with open(filename, encoding='utf-8') as f:
            kmlOld = f.read()
            kml.document.name = title
            kmlNew = kml.kml()
            if kmlOld != kmlNew:
                title += '-' + suffix if suffix else ''
                saveKmlFile(kml, title, filePath)
            else:
                print(f'Keep to file "{filePath}{title}.kml"\n')
    except FileNotFoundError:
        title += '-' + suffix if suffix else ''
        saveKmlFile(kml, title, filePath)
    return filename

#####################################################################################
def _convertCoordList(coords):
    if len(coords) == 1:
        radius = coords[0].split('+')
        coords = [radius[0]]
        radius.append(10) if len(radius) == 1 else radius
    else:
        radius = [0, 10]

    return [myFile.convertDMS2DD(c) for c in coords], radius

#####################################################################################
def _updateCenterList(centerCoords, coordsList):
    if len(coordsList) == 1:
        center = coordsList[0]
    elif len(coordsList) > 2:
        center = getAreaCenter(coordsList)
    else:
        center = ''

    if center and center not in centerCoords:
        centerCoords.append(center)
    return centerCoords

################################################################################################
def convertLocation(number) -> str:
    numbers = number.split('/')
    loc = numbers[0]
    msa = numbers[1][:2]
    launchCenters = myConfig.readConfigLaunchCenters()
    if loc == 'MSA':
        if msa in 'SD,LYG':
            launchCenters[loc] = '海阳日照'
        elif msa in 'GD':
            launchCenters[loc] = '海南文昌阳江'
        elif msa in 'HN':
            launchCenters[loc] = '海南文昌'
        elif msa in 'LN':
            launchCenters[loc] = '唐山'
    elif loc in 'NAV8,PAC' :
        launchCenters[loc] = '海南文昌酒泉'
    elif loc in 'NAV10,NAV11' :
        launchCenters[loc] = '海南文昌唐山'

    for l in loc.split('/'):
        ret2 = launchCenters.get(l)
        if ret2 != '':
            return ret2
    return ''

#####################################################################################
def _updateCity(l:list, key:str, item:str):
    if key in l:
        l = l.remove(key)
    l.append(item)
    return l

#####################################################################################
def createKmlFile(notamList) -> None:
    filenames = []
    for notams in notamList:
        kml = Kml()
        centerCoords = []
        launchCityList = []
        checkLaunchCity = True

        for notamDict in notams:
            for number, value in notamDict.items():
                itemArray = value.split(';')
                startDate = itemArray[0]
                endDate = itemArray[1]
                loc = itemArray[2]
                cities = convertLocation(number)
                cityList = [cities[i:i+2] for i in range(0, len(cities), 2)]
                coordsArray = itemArray[3].split('-')

                if len(coordsArray) > 1:
                    coordsAll = itemArray[3].replace('-', '|')
                    coordsArray.append(coordsAll)

                for arr in coordsArray:
                    coords = arr.split('|')
                    coordsList, radius =_convertCoordList(coords)
                    centerCoords = _updateCenterList(centerCoords, coordsList)

                    if len(coordsList) == 2:
                        continue
                    elif len(coordsList) == 1 & checkLaunchCity:
                        checkLaunchCity = False
                        if loc in 'ZSHA':
                            if '海阳' in cityList:
                                launchCityList = _updateCity(launchCityList, '海阳', f'海阳|{coordsList[0][0]}|{coordsList[0][1]}')
                            if '日照' in cityList:
                                launchCityList = _updateCity(launchCityList, '日照', f'日照|{coordsList[0][0]}|{coordsList[0][1]}')
                            if not launchCityList:
                                launchCityList = cityList
                        elif loc in 'ZGZU' and '阳江' in cityList:
                            launchCityList = _updateCity(launchCityList, '阳江', f'阳江|{coordsList[0][0]}|{coordsList[0][1]}')
                        elif loc in 'ZYSH' and '唐山' in cityList:
                            launchCityList = _updateCity(launchCityList, '唐山', f'唐山|{coordsList[0][0]}|{coordsList[0][1]}')
                        elif loc == 'MSA':
                            cities = ['海阳', '日照', '阳江', '海南', '文昌', '唐山']
                            for c in cities:
                                if c in cityList:
                                    launchCityList = _updateCity(launchCityList, c, f'{c}|{coordsList[0][0]}|{coordsList[0][1]}')
                            if not launchCityList:
                                launchCityList = cityList
                        else:
                            launchCityList = cityList
                    else: # len(coordsList) >= 3
                        if checkLaunchCity:
                            checkLaunchCity = False
                            launchCityList = parseLaunchCityList(loc, cityList, coordsList)

                    color = myConfig.readConfig(launchCityList[0].split('|')[0])[1] if launchCityList else 'black'
                    drawStages(kml, coordsList, color, number, int(radius[1]), myDate.convertToLocalDate(startDate, fmt="%Y年%m月%d日%H时%M分"))

        launchCity = ''.join([c.split('|')[0] for c in launchCityList])
        title = myFile.convertTitle(startDate, endDate, launchCity)
        drawRoutePolyline(kml, launchCityList, centerCoords)
        filenames.append(updateKmlFile(kml, title, KML_PATH))
    return filenames                

#####################################################################################
def sort_clockwise_from_topleft(points):
    # points = [(lon, lat), ...]
    # 1. find the top-left point (max latitude, then min longitude)
    top_left = max(points, key=lambda p: (p[1], -p[0]))
    # 2. compute centroid
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    # 3. compute angle for clockwise sorting
    def angle(p):
        dx = p[0] - cx
        dy = p[1] - cy
        a = atan2(dy, dx)
        # convert counter-clockwise angle to clockwise
        return -a
    # 4. sort by angle
    sorted_pts = sorted(points, key=angle)
    # 5. rotate list so top_left is first
    i = sorted_pts.index(top_left)
    sorted_pts = sorted_pts[i:] + sorted_pts[:i]
    return sorted_pts

#####################################################################################
def drawStages(kml, coords, color, location, radius, startDate) -> None:
    if coords:
        count = len(coords)
        if count == 1:
            drawCircle(kml, coords, location, color, radius, startDate)
        elif count == 2:
            drawLine(kml, coords, location, color, startDate)
        else: 
            coords = sort_clockwise_from_topleft(coords)
            lon1, lat1, lon2, lat2 = coords[0][0], coords[0][1], coords[-1][0], coords[-1][1]
            distance = myMath.haversine(lon1, lat1, lon2, lat2)
            if distance < 150 or location != 'MSA': # distance less than 150km between first and last point
                drawPolygon(kml, coords, location, color, startDate)
            else:
                drawLine(kml, coords, location, color, startDate)
    return coords

#####################################################################################
def drawPolygon(kml, coords, location, color=None, startDate=None) -> None:
    pol = kml.newpolygon(name=location)
    pol.description = startDate
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
def drawLine(kml, coords, location=None, color=None, startDate=None) -> None:
    line = kml.newlinestring(name=location)
    line.description = startDate
    line.coords = coords
    line.style.linestyle.color = color if color is not None else 'black'
    line.style.linestyle.width = 1

#####################################################################################
# distance in km
def drawCircle(kml, coords, location, color, radius, startDate=None):
    circle = circleByPoint(coords[0][1], coords[0][0], radius)
    # circle = [(lon, lat) for lat, lon in buffer]
    if radius > 20000:
        drawPolygon(kml, circle, location, color, startDate)
    else:
        drawLine(kml, circle, location, color, startDate)


#####################################################################################
def drawRoutePolyline(kml, city, centerCoords, seaCoord=None):
    if len(centerCoords) > 1:
        coordsListSort = sorted(centerCoords, key=lambda x: x[1], reverse=True)
    else:
        coordsListSort = centerCoords

    if isinstance(city, str):
        cities = [city[i:i + 2] for i in range(0, len(city), 2)]
    else:
        cities = city

    for c in cities:
        coordsListCity = coordsListSort.copy()
        if c == '海上':
            coordsListCity.insert(0, seaCoord[c])
        elif '|' in c:
            cList = c.split('|')
            if cList[0] in '唐山,海阳,日照,阳江,海南,文昌':
                coords = (float(cList[1]), float(cList[2]))
                coordsListCity.insert(0, coords)
                c = cList[0]
        else:
            coordsListCity.insert(0, myUtils.getCityCoordinate(c))

        points = coordsListCity
        lon0, lat0 = points[0]
        lon2, lat2 = points[-1]
        angle = myMath.launch_azimuth(lat0, lon0, lat2, lon2)
        # angle = myMath.great_circle_bearing(lat0, lon0, lat2, lon2)

        # Add a polyline string to the KML
        ls = kml.newlinestring(name=f'{c}{angle:.1f}°轨道')
        ls.style.linestyle.color = 'ff000000'
        ls.style.linestyle.width = 1
        ls.coords = points

###############################################################################
def drawRectangle(kml, launchCity, centerCoords):
    cities = [launchCity[i:i + 2] for i in range(0, len(launchCity), 2)]
    for city in cities:
        cityCoord =  myUtils.getCityCoordinate(city)
        lats = [lat for lon, lat in centerCoords + [cityCoord]]
        lons = [lon for lon, lat in centerCoords + [cityCoord]]
        left = min(lons)
        right = max(lons)
        top = max(lats)
        bottom = min(lats)

        rect1 = [(left - 8, top + 5), (right + 8, top + 5), (right + 8, bottom - 2), (left - 8, bottom - 2), (left - 8, top + 5)]
        pol1 = kml.newlinestring(name='Border')
        pol1.coords = rect1
        pol1.style.linestyle.width = 2
        pol1.style.linestyle.color = 'ff000000'

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
        locationList, locations = myConfig.getLocation(newFile)
        if locationList is None:
            print(f'{newFile} not included {locations}')
            return ''
    
    from myModules import myPlot
    cn_font = myPlotInit.init()
    newGdf = myKml.readKmlFile(newFile)
    if newGdf.empty:
        print(f"No Data in {newFile}!")
        return 

    matchDict = {}
    kmlFolder = myConfig.readConfigLocations()
    for location in locationList:
        folder = path.abspath(kmlFolder[location])
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
                iouList, startTimeList, title = plotPolygonsIntersection(ax, newGdf, newTitle, oldGdf, oldTitle)
                plotTitleXYLabels(fig, ax, cn_font, title, 'Longitude（经度）', 'Latitude（纬度）')

                # Save the plot to a file
                basename = path.basename(oldFile)
                filename = basename.replace(".kml", ".png")

                if iouList:
                    oldFilename = oldFile.split('\\')[-1]
                    launchDate = oldFilename[:11]
                    launchDate = datetime.strptime(launchDate, "%Y年%m月%d日")
                    city = oldFilename[17:19]
                    city = city.replace('黄海', '海上').replace('东海', '海上').replace('南海', '海上')
                    matchDict[(launchDate, city)] = [iouList, startTimeList, oldFilename.replace('.kml', '.png')]
                    print(f'{newTitle} IoU {oldTitle}')
                    for iou in iouList:
                        print(f'    {iou}') 
                    myPlot.saveFig(fig, f'{savePath1}/{filename}', False, False)
                    print('')
                else:
                    myPlot.saveFig(fig, f'{savePath2}/{filename}', False, False)
            except Exception as e:
                print(f'Exception: {e}\n')
    return matchDict, savePath1

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
def plotPolygonsIntersection(ax, newPolys, newTitle, oldPolys=None, oldTitle=''):
    # Calculate NOTAM drop zones Jaccard Similarity Index and plot intersection polygons
    iouList, startTimeList = plotIntersection(ax, newPolys, oldPolys)
    # plot title, axis and NOTAM drop zones
    title = f'{oldTitle}\n{newTitle}'
    for ios in iouList:
        title += f'\n{ios}'
    return iouList, startTimeList, title

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

    title = newFile.replace('\\', '/') if mySys.isWindows() else newFile
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

        oldTitle = oldFile.replace('\\', '/') if mySys.isWindows() else oldFile
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
        _, _, newTitle = plotPolygonsIntersection(ax, newGdf, newTitle, oldGdf, oldTitle)

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
    iouList = []
    startTimeList = []

    for i, newGeom in enumerate(newGdf.geometry):
        if isinstance(newGeom, Polygon):
            oldIndex = 0
            newIndex += 1
            newStartTime = newGdf.iloc[i]["Description"]

            for j, oldGeom in enumerate(oldGdf.geometry):
                if isinstance(oldGeom, Polygon):
                    oldIndex += 1
                    iou = 0.0

                    if newGeom.intersects(newGeom):
                        try:
                            intersection = newGeom.intersection(oldGeom)
                            union = newGeom.union(oldGeom)
                            iou = 0.0 if union.area == 0.0 else intersection.area / union.area
                        except Exception as e:
                            pass
                    if iou > 0.01:
                        oldName = oldGdf.iloc[j]["Name"]
                        newName = newGdf.iloc[i]["Name"]
                        if oldName.startswith('MSA'):
                            oldNames = oldName.split('/')
                            oldName = f'{oldNames[0].rjust(4)}/{oldNames[1].rjust(5)}/{oldNames[2]}'
                        if newName.startswith('MSA'):
                            newNames = newName.split('/')
                            newName = f'{newNames[0].rjust(4)}/{newNames[1].rjust(5)}/{newNames[2]}'
                        geomName = f'{newName} IoU {oldName}'
                        text = f'{iou:6.1%} = {geomName}'
                        iouList.append(text)
                        startTimeList.append(newStartTime)
                        plotGeometry(ax, gpd.GeoDataFrame(geometry=[intersection]), color='orange', legend=text, zorder=4)
    return iouList, startTimeList

#####################################################################################
def circleByPoint(lat, lon, m):
    proj_wgs84 = CRS('EPSG:4326')
    proj_aeqd = CRS(f'+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0')
    transformer = Transformer.from_crs(proj_aeqd, proj_wgs84, always_xy=True)
    buf = Point(0, 0).buffer(m)  # distance in metres
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
def calculateAngleOld(point1, point2, point3):
    """
    angle = angle between line from point1 to point2 then to point3
    a = the side length from point1 to point2
      = sqrt((lon1 - lon2) * (lon1 - lon2) + (lat1 - lat2) * (lat1 - lat2))
    A = the angle opposite side a
    b = the side length from point2 to point3
      = sqrt((lon2 - lon3) * (lon2 - lon3) + (lat2 - lat3) * (lat2 - lat3))
    B = the angle opposite side b
    c = the side length from point3 to point1
      = sqrt((lon3 - lon1) * (lon3 - lon1) + (lat3 - lat1) * (lat3 - lat1))
    C = the angle opposite side c
    c * c = a * a + b * b - 2 * a * b * cos(C)
    cos(C) = (a * a + b * b - c * c) / (2 * a * b)
    C = acos((a * a + b * b - c * c) / (2 * a * b))
    """
    lon1, lat1 = point1
    lon2, lat2 = point2
    lon3, lat3 = point3
    # lon2 = (lon2 + lon3) / 2
    # lat2 = (lat2 + lat3) / 2
    a = sqrt((lon2 - lon1) * (lon2 - lon1) + (lat2 - lat1) * (lat2 - lat1))
    b = sqrt((lon3 - lon2) * (lon3 - lon2) + (lat3 - lat2) * (lat3 - lat2))
    if a == 0 or b == 0:
        return 0
    c = sqrt((lon3 - lon1) * (lon3 - lon1) + (lat3 - lat1) * (lat3 - lat1))
    angleC = acos((a * a + b * b - c * c) / (2 * a * b))
    # angleInDegrees = degrees(theta)
    return angleC

###############################################################################
def sliceByLen(text, length):
    return [text[i:i + 2] for i in range(0, len(text), length)]

def angular_distance(lat1, lon1, lat2, lon2):
    """Great-circle angular distance between two lat/lon points (radians)."""
    φ1, λ1 = radians(lat1), radians(lon1)
    φ2, λ2 = radians(lat2), radians(lon2)
    return acos(sin(φ1) * sin(φ2) + cos(φ1) * cos(φ2) * cos(λ2 - λ1))

###############################################################################
def calculateAngle(pointA, pointB, pointC):
    """
    Compute angle B (at vertex pointB), given triangle vertices:
    pointA = (lonA, latA)
    pointB = (lonB, latB)
    pointC = (lonC, latC)
    side a is opposite angle A: between pointB and pointC
    side b is opposite angle B: between pointA and pointC
    side c is opposite angle C: between pointA and pointB
    cos(B) = (cos(b) - cos(a) * cos(c)) / (sin(a) * son(c))
    """
    # Compute spherical triangle sides:
    a = angular_distance(pointB[1], pointB[0], pointC[1], pointC[0])  # side a = BC
    b = angular_distance(pointA[1], pointA[0], pointC[1], pointC[0])  # side b = AC
    c = angular_distance(pointA[1], pointA[0], pointB[1], pointB[0])  # side c = AB
    # Spherical law of cosines for angle B at pointB
    numerator = cos(b) - cos(a) * cos(c)
    denominator = sin(a) * sin(c)
    angle_B_rad = acos(numerator / denominator)
    return angle_B_rad

###############################################################################
def _getLaunchCity(launchCity, launchAngle, loc, city, cityPoint, top1, top2):
    center12 = ((top1[0] + top2[0]) / 2, (top1[1] + top2[1]) / 2)
    angle = calculateAngle(cityPoint, center12, top2)
    if not launchCity or (degrees(abs(pi / 2 - launchAngle)) > 5 and abs(pi / 2 - angle) < abs(pi / 2 - launchAngle)):
        launchCity = city
        launchAngle = angle
    if degrees(abs(pi / 2 - angle)) < 5:
        launchCity += city if city not in launchCity else ''
    print(f'{city} to {loc}: {degrees(angle):6.2f}° = {launchCity}')
    return launchCity, launchAngle, angle

###############################################################################
def parseLaunchCity(launchCityList: list, launchAngle, loc, city, cityPoint, top1, top2):
    city = city.split('|')[0]
    center12 = ((top1[0] + top2[0]) / 2, (top1[1] + top2[1]) / 2)
    angle = calculateAngle(cityPoint, center12, top2)

    if not launchCityList or (degrees(abs(pi / 2 - launchAngle)) > ANGLE_RANGE and abs(pi / 2 - angle) < abs(pi / 2 - launchAngle)):
        launchCityList = [city]
        launchAngle = angle
    
    if degrees(abs(pi / 2 - angle)) < ANGLE_RANGE and city not in launchCityList:
        launchCityList.append(city)
    
    print(f'{city} to {loc}: {degrees(angle):6.2f}° = {''.join(launchCityList)}')
    return launchCityList, launchAngle, angle

###############################################################################
def parseLaunchCityList(loc: str, cityList: list, coordsList: list):
    launchCityList = []
    launchAngle = 0
    # cityList = sliceByLen(cityList, 2)

    for city in cityList:
        if '|' in city:
            cities = city.split('|')
            cityPoint = (float(cities[1]), float(cities[2]))
        else:
            cityPoint = tuple(float(x) for x in myConfig.readConfig(city)[2].split('+'))

        top1, top2 = getTopCorners(coordsList)
        launchCityList, launchAngle, angle = parseLaunchCity(launchCityList, launchAngle, loc, city, cityPoint, top1, top2)

        if angle > pi / 2 or len(coordsList) >= 3:
            top1, top2 = getTopCorners(coordsList, 0, 2)
            launchCityList, launchAngle, angle = parseLaunchCity(launchCityList, launchAngle, loc, city, cityPoint, top1, top2)

        if angle < pi / 4 and len(coordsList) >= 4:
            top1, top2 = getTopCorners(coordsList, 1, 3)
            launchCityList, launchAngle, angle = parseLaunchCity(launchCityList, launchAngle, loc, city, cityPoint, top1, top2)

    if loc == 'ZBPE/ZHWH/ZLHW/ZSHA':
        launchCityList.insert(0, '酒泉')
    return launchCityList

def parseLaunchCities(loc, cities, coordsList):
    launchCity = ''
    launchAngle = 0
    needAgain = False
    cityList = sliceByLen(cities, 2)
    for city in cityList:
        cityPoint = [float(x) for x in myConfig.readConfig(city)[2].split('+')]
        top1, top2 = getTopCorners(coordsList)
        launchCity, launchAngle, angle = _getLaunchCity(launchCity, launchAngle, loc, city, cityPoint, top1, top2)

        if angle > pi / 2 or len(coordsList) > 4:
            top1, top2 = getTopCorners(coordsList, 0, 2)
            launchCity, launchAngle, angle = _getLaunchCity(launchCity, launchAngle, loc, city, cityPoint, top1, top2)

        if angle < pi / 4:
            top1, top2 = getTopCorners(coordsList, 1, 3)
            launchCity, launchAngle, angle = _getLaunchCity(launchCity, launchAngle, loc, city, cityPoint, top1, top2)

    if loc == 'ZBPE/ZHWH/ZLHW/ZSHA':
        launchCity = '酒泉' + launchCity
    return launchCity, launchAngle

def _getCity(cities, coordsList):
    cityList = sliceByLen(cities, 2)
    launchCity = ''
    launchDistance = 0
    for city in cityList:
        cityPoint = [float(x) for x in myConfig.readConfig(city)[2].split('+')]
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
    if len(coordsList) == 1: 
        launchCity = cities
    elif len(coordsList) >= 3: # drop zone
        launchCity, _ = parseLaunchCities(loc, cities, coordsList)
    else:
        launchCity = cities
    isFirst = False if len(coordsList) > 2 else True
    
    if '文昌' in launchCity and '海南' not in launchCity:
        launchCity += '海南'
    elif '海南' in launchCity and '文昌' not in launchCity:
        launchCity += '文昌'

    if loc in 'ZSHA':
        launchCity += '海阳日照'
    elif loc in 'ZGZU':
        launchCity += '阳江'
    elif loc in 'ZYSH':
        launchCity += '唐山'
    
    return launchCity, isFirst

###############################################################################
def getTopCorners(coords: list, top1=0, top2=1):
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
    topPoints = [sortedBylat[top1], sortedBylat[top2]]
    topPointsSortedByLon = sorted(topPoints, key=lambda x: x[0])
    p1 = topPointsSortedByLon[0]
    p2 = topPointsSortedByLon[1]
    return p1, p2

