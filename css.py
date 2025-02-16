from os import path, remove
import ssl
from re import search
from sys import argv
from datetime import datetime, timedelta, timezone
from skyfield.api import EarthSatellite, wgs84, load
from timeit import timeit
import zipfile
from pyorbital.orbital import Orbital
from astropy.coordinates import CartesianRepresentation, CartesianDifferential, GCRS, ITRS
from astropy.time import Time
import astropy.units as u
from math import radians, sqrt, sin, cos, asin, degrees
import requests
from selenium.webdriver.common.by import By

from myModules import myNet
from myModules import myFile
from myModules import myDate
from myModules import myDict
from myModules import myHtml

# Constants
EARTH_RADIUS_EQUATORIAL = 6378.137  # in km
ECCENTRICITY_SQUARED = 0.00669437999014
CELESTRAK_URL = 'https://celestrak.org/NORAD/elements/'
CSS_TLE_URL = CELESTRAK_URL + 'gp.php?CATNR=48274&FORMAT=tle'
CSS_MAIN_URL = 'https://www.cmse.gov.cn/'
CSS_DOWNLOAD_URL = CSS_MAIN_URL + 'gfgg/zgkjzgdcs/'
CSS_OEM_ZIP_URL  = CSS_DOWNLOAD_URL + 'YYMM/W020241021391306489470.zip'
CSS_OEM_ZIP_XPATH_DIV = '//div[@class="TRS_Editor"]'
TEMP_FILE_PATH = './temp/'

PLATFORMS = {
    'CSS': "CSS (TIANHE)", 
    'SZ-19': "SHENZHOU-19 (SZ-19)",
    'SZ-17': "SZ-17 MODULE",
    'TZ-7': "TIANZHOU-7"
}

################################################################################################
def downloadTLE():
    print('下载TLE数据...')
    driver = myNet.getFirefoxDriver()

    try:
        driver.set_page_load_timeout(123)
        driver.get(CSS_TLE_URL)

        # XPATH_DIV = '//div[@class="TRS_Editor"]'
        myNet.elementLocatedBy(driver, By.TAG_NAME, 'pre')
        pre = driver.find_element(By.TAG_NAME, 'pre')
        tle = pre.text.split('\n')
        driver.close()
    except Exception as e:
        # print(e)
        print('下载TEL失败！')
        print('使用既存TLE数据...')
        tle = readTLEFromFile()
    return tle

################################################################################################
def downloadOEM(mainUrl):
    print('下载OEM数据...')
    with myNet.getFirefoxDriver() as driver:
        try:
            driver.set_page_load_timeout(180)
            driver.get(mainUrl)
            myNet.elementLocatedBy(driver, By.XPATH, CSS_OEM_ZIP_XPATH_DIV)
            div = driver.find_element(By.XPATH, CSS_OEM_ZIP_XPATH_DIV)
            aTag = div.find_element(By.TAG_NAME, 'a')
            url = aTag.get_attribute('href')
            savePath = ''
            if url:
                filename = div.text
                savePath = f'{TEMP_FILE_PATH}{filename}'
                downloadZipFile(url, savePath)
        except Exception as e:
            print(f'下载OEM失败！\n{e}')
            print('使用既存OEM数据...')
    return savePath

################################################################################################
def downloadZipFile(url, savePath='/temp/'):
    response = requests.get(url)

    if response.status_code == 200:
        with open(savePath, 'wb') as file:
            file.write(response.content)
            print(f'Save to {savePath}!')
    else:
        print(f'Failed to download {response.status_code}')

################################################################################################
def saveTLEToFile(prefix, tle):
    filename = f'{TEMP_FILE_PATH}{prefix}-{tle[1][18:23]}-{tle[1][24:32]}.txt'
    with open(filename, 'w', encoding='utf-8') as f:
        for l in tle:
            f.write(f'{l}\n')

################################################################################################
def readTLEFromFile(tlePath, prefix=''):
    tle = []
    lastModifiedDate = None
    fileList = list(myFile.listFiles(tlePath, '.txt', prefix=prefix))
    try:
        filename = fileList[-1] if fileList else ''
        with open(filename, 'r', encoding='utf-8') as f:
            tle = [line.strip() for line in f]
            lastModifiedDate = myFile.getLastModifiedDate(filename)
    except:
        pass
    return tle, lastModifiedDate

################################################################################################
def convertDMS(decimal_degrees):
    degrees, decimal_minutes = divmod(decimal_degrees, 1)
    minutes, decimal_seconds = divmod(decimal_minutes * 60, 1)
    seconds, _ = divmod(decimal_seconds * 60, 1)
    return degrees, minutes, seconds

################################################################################################
def convertAzimuth(azimuth):
    azimuthChinese = ['正北', '东北偏北', '东北', '东北偏东', 
                      '正东', '东南偏东', '东南', '东南偏南', 
                      '正南', '西南偏南', '西南', '西南偏西', 
                      '正西', '西北偏西', '西北', '西北偏北']
    i = int(((azimuth + 11.25) % 360) / 22.5)
    return azimuthChinese[i]

PAPTTERN_DAYS = r'Current as of \d{4} [a-zA-Z]{3} \d{1,2} \d{2}:\d{2}:\d{2} UTC \(Day (\d{1,3})\)'
################################################################################################
def getDaysOnCelesTrak(url=CELESTRAK_URL):
    with myNet.getFirefoxDriver() as driver:
        driver.get(url)
        myNet.elementLocatedBy(driver, By.XPATH, '//h3[@class="center"]')
        text = search(PAPTTERN_DAYS, driver.page_source)
        try:
            days = int(text.group(1)) - 1 if text else 0
        except:
            days = 0
            pass
        return days

def readLastTLE(platform):
    orbit = None
    prefix = f'tle-{platform.replace(' ', '')}'
    tle, lastTime = readTLEFromFile(TEMP_FILE_PATH, prefix)
    if tle and datetime.now() - timedelta(hours=2.5) < lastTime:
        # days = getDaysOnCelesTrak()
        # if days == int(tle[1][20:23]):
        orbit = Orbital('中国空间站', line1=tle[1], line2=tle[2])
    if not orbit and platform:
        # orbit = Orbital("CSS (TIANHE)")
        orbit = Orbital(platform)
        tle = [orbit.tle.platform, orbit.tle.line1, orbit.tle.line2]
        saveTLEToFile(prefix, tle)
    return tle, orbit

################################################################################################
def calculatePasses(locDict, startDate=None, hours=720, platform=None):
    tle, orbit = readLastTLE(platform)
    # prefix = f'tle-{platform.replace(' ', '')}'
    # tle, lastTime = readTLEFromFile(prefix)
    # if tle and datetime.now() - timedelta(hours=2.5) < lastTime:
    #     # days = getDaysOnCelesTrak()
    #     # if days == int(tle[1][20:23]):
    #     orbit = Orbital('中国空间站', line1=tle[1], line2=tle[2])
    # if not orbit and platform:
    #     # orbit = Orbital("CSS (TIANHE)")
    #     orbit = Orbital(platform)
    #     tle = [orbit.tle.platform, orbit.tle.line1, orbit.tle.line2]
    #     saveTLEToFile(prefix, tle)

    # Get the current time in UTC
    now = datetime.now(timezone.utc) if startDate is None else startDate
    _, _, alt = orbit.get_lonlatalt(now)
    ret = {myDate.getChinaTime(now): alt}

    for loc in locDict:
        ret[loc] = []
        # Calculate the next hours passes of the satellite over the specified location
        passes = orbit.get_next_passes(utc_time=now, length=hours, lat=locDict[loc][0], lon=locDict[loc][1], alt=locDict[loc][2])
        
        # Print the pass information for each pass
        for p in passes:
            rise_time =p[0]
            fall_time = p[1]
            max_elevation_time = p[2]
            azimuth, elevation = orbit.get_observer_look(max_elevation_time, lon=locDict[loc][1], lat=locDict[loc][0], alt=0.01)
            ret[loc].append([myDate.getChinaTime(rise_time), myDate.getChinaTime(fall_time), myDate.getChinaTime(max_elevation_time), azimuth, elevation])
    return ret, tle

################################################################################################
def buildTableBegin(tableId, loc, text):
    html = ''
    if tableId == 0:
        html += '<TABLE class=no-border>'
        html += '<TR><TD rowspan=3>'
    elif tableId == 1:
        html += '<TD>'
    elif tableId in [2, 3]:
        html += '<TR><TD>'
    html += f'<button onclick=saveTableAsImage("{loc}")>Save Table as {loc}.png</button><BR>\n'
    html += f'<TABLE class=borderOnly><TR><TD>\n'
    html += f'<TABLE class=border id={loc}>\n'
    html += f'<TR><TH colspan=3>{text.replace('\n', '<BR>\n')}</TH></TR>\n'
    html += '<TR><TH>北京时间</TH><TH>仰角</TH><TH>方位</TH></TR>\n'
    return html

################################################################################################
def buildTableEnd(tableId):
    html = "</TABLE>\n"
    if tableId == 0:
        html += '</TD>\n'
    elif tableId in [1, 2]:
        html += '</TD></TR>\n'
    else:
        html += '</TD></TR></TABLE></TD></TR></TABLE>\n'
    return html

################################################################################################
def buildHeader(tle, text1, text3):
    html = f'{text1}'
    html += f'<PRE>{tle[1]}</PRE><PRE>{tle[2]}</PRE>'
    html += f'{text3}'
    # html += f'{text4}'
    return html

################################################################################################
def buildTableCell(loc, date, time, degree, minute, second, azimuth, bgColor=None):
    html = '<TR style="background-color:orange;">' if loc in bgColor and date in bgColor[loc] else '<TR>'
    html += f'<TD>{date}{time}</TD>'
    html += f'<TD>{degree:02.0f}°{minute:02.0f}\'{second:02.0f}"</TD>'
    html += f'<TD>{convertAzimuth(azimuth)}</TD></TR>\n'
    return html

################################################################################################
def showTime(platform, passTime, tle, bgColor=None):
    platform = platform.replace(' ', '')
    minAngle = 75
    html = myHtml.buildHtmlBegin(f'{platform}轨道预测')
    tableId = 0
    for i, key in enumerate(passTime):
        if i == 0:
            now, alt = key, passTime[key]
            nowChina = myDate.getChinaTime(now, '%Y-%m-%d %H:%M')
            mean_motion = float(tle[2][52:63])
            period = int(1440 / mean_motion)
            text1 = f"根据最新<A href={CSS_TLE_URL}>{platform}</A>轨道参数TLE数据<BR>"
            # text2 = f"{tle[1]}\n{tle[2]}<BR>\n"
            text3 = f"{platform}轨道周期约<b>{period}分</b>"
            text4 = f"{platform}<b>{nowChina}</b>位于<b>{int(alt)}</b>公里太空<BR>"
            # print(f'{text1}{text2}{text3}{text4}')
            html += buildHeader(tle, text1, text3)
        else:
            loc, values = key, passTime[key]
            # text = f"{nowChina}开始{hours}小时内\n"
            text = f"{text1}{text4}将于下列时间通过{loc}上空(仰角大于{minAngle}°)\n" 
            # print(text)
            html += buildTableBegin(tableId, loc, text)
            for value in values:
                _, _, max_elevation_time, azimuth, elevation = value
                if elevation > minAngle:
                    degree, minute, second = convertDMS(elevation)
                    max_date = max_elevation_time.date()
                    max_time = max_elevation_time.time()
                    date = f'{max_date.year}{max_date.month:02}{max_date.day:02}'
                    time = f'{max_time.hour:02}时{max_time.minute:02}分'
                    text = f"\t{date}{time}，仰角：{degree:02.0f}°{minute:02.0f}'{second:02.0f}\"，"
                    text += f"方位角：{convertAzimuth(azimuth)}"
                    # print(text)
                    html += buildTableCell(loc, date, time, degree, minute, second, azimuth, bgColor)
            print()
            html += buildTableEnd(tableId)
            tableId += 1
    html += myHtml.buildHtmlEnd()
    return html

################################################################################################
def getHours(date1, dateStr2):
    year, month, day = int(dateStr2[:4]), int(dateStr2[4:6]), int(dateStr2[6:8])
    date2 = myDate.getUTCFromLocal(year, month, day)
    return int((date2 - date1).total_seconds() / 3600)

def geodetic_to_ecef(lat, lon, h=0):
    # Convert lat and lon from degrees to radians
    lat_rad = radians(lat)
    lon_rad = radians(lon)
    # Calculate the radius of curvature
    N = EARTH_RADIUS_EQUATORIAL / sqrt(1 - ECCENTRICITY_SQUARED * sin(lat_rad) ** 2)
    # Calculate ECEF coordinates
    x = (N + h) * cos(lat_rad) * cos(lon_rad)
    y = (N + h) * cos(lat_rad) * sin(lon_rad)
    z = (N * (1 - ECCENTRICITY_SQUARED) + h) * sin(lat_rad)
    return x, y, z

def eme2000_to_ecef(time_str, x, y, z, vx, vy, vz):
    # Create a time object from the provided time string (ISO format)
    time = Time(time_str)
    # Create a Cartesian representation of the position and velocity in EME2000
    position = CartesianRepresentation(x * u.km, y * u.km, z * u.km)
    velocity = CartesianDifferential(vx * u.km/u.s, vy * u.km/u.s, vz * u.km/u.s)
    # Combine position and velocity
    gcrs_coord = GCRS(position.with_differentials(velocity), obstime=time)
    # Transform to ECEF (ITRS)
    itrs_coord = gcrs_coord.transform_to(ITRS(obstime=time))
    # Extract the x, y, z positions in ECEF
    x_ecef = itrs_coord.x.to(u.km).value
    y_ecef = itrs_coord.y.to(u.km).value
    z_ecef = itrs_coord.z.to(u.km).value
    return x_ecef, y_ecef, z_ecef

def calculateAltitude(x, y, z, earth_radius=6371):
    # Calculate the distance from the object to the Earth's center
    distance = sqrt(x ** 2 + y ** 2 + z ** 2)
    # Calculate the altitude by subtracting Earth's radius
    altitude = distance - earth_radius
    return altitude

def calculateElevation(x, y, z, lat_o, lon_o, h_o=0):
    # Convert the observer's geodetic coordinates to ECEF coordinates
    x_o, y_o, z_o = geodetic_to_ecef(lat_o, lon_o, h_o)
    # Calculate the relative position between the object and the observer
    delta_x = x - x_o
    delta_y = y - y_o
    delta_z = z - z_o
    # Calculate the range (distance) between the object and the observer
    range_distance = sqrt(delta_x ** 2 + delta_y ** 2 + delta_z ** 2)
    # Calculate the elevation angle in radians and convert to degrees
    elevation_radians = asin(delta_z / range_distance)
    elevation_degrees = degrees(elevation_radians)
    return elevation_degrees

################################################################################################
def unzipFile(zip_path, extract_to=None):
    try:
        if extract_to is None:
            extract_to = path.dirname(zip_path)
        extracted_files = []

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
            extracted_files = zip_ref.namelist()

        remove(zip_path)
        extracted_file_paths = [path.join(extract_to, name) for name in extracted_files]
    except:
        pass
    return extracted_file_paths

################################################################################################
def parseOEMfromFile(oemFile):
    with open(oemFile, 'r') as file:
        lines = file.readlines()
    data = []
    for line in lines:
        line = line.strip()
        if line.startswith('202'):
            data.append(line.split())
    return data

################################################################################################
def getAltitudeDict(oemList, city):
    altitudeDict = {}
    timeList = []
    altitudeList = []
    elevationList = []
    lat, lon, alt = city[0], city[1], city[2]
    for timeStr, x, y, z, vx, vy, vz in oemList:
        x, y, z, vx, vy, vz = float(x), float(y), float(z), float(vx), float(vy), float(vz)
        x_ecef, y_ecef, z_ecef = eme2000_to_ecef(timeStr, x, y, z, vx, vy, vz)
        timeList.append(timeStr)
        altitudeList.append(calculateAltitude(x_ecef, y_ecef, z_ecef))
        elevationList.append(calculateElevation(x_ecef, y_ecef, z_ecef, lat, lon, alt))
        # altitudeDict[timeStr] = (altitude, elevation)
        # print(f'{timeStr}: {altitude:.2f}km. {elevation:.2f}°')
    altitudeDict['Time'] = timeList
    altitudeDict['Altitude'] = altitudeList
    altitudeDict['Elevation'] = elevationList
    return altitudeDict

################################################################################################
def createLineGraphForAltitude(cities):
    fileList = list(myFile.listFiles(TEMP_FILE_PATH, 'dat', includeSubFolder=False))
    lastOemFile = fileList[-1] if fileList else ''
    filenameList = lastOemFile.replace('\\', '/').split('/')
    today = f'CSS_OEM_{myDate.getJapanTime('%Y%m%d')}'

    if lastOemFile == '' or today > filenameList[-1][:16]:
        oemZipFile = downloadOEM(CSS_DOWNLOAD_URL)
        if oemZipFile:
            lastOemFile = unzipFile(oemZipFile)[0]

    oemList = parseOEMfromFile(lastOemFile)
    city = cities['酒泉']
    altitudeDict = getAltitudeDict(oemList, city)
    altitudeFilename = lastOemFile.replace('.dat', 'altitude.txt')
    myDict.saveDictToTextFile(altitudeFilename, altitudeDict)

    # df = pd.DataFrame(altitudeDict)
    # createLineGraph(df)

def calculateLandingTime(cities):
    platform = 'SZ-19'
    tle, _ = readLastTLE(platform)
    satellite = EarthSatellite(tle[1], tle[2], platform)
    lat = cities['酒泉'][0]
    lon = cities['酒泉'][1]
    # altitude = cities['酒泉'][1]
    landing_location = wgs84.latlon(lat, lon)
    ts = load.timescale()
    current_time = datetime.now(timezone.utc)
    
    time_step = timedelta(seconds=1)
    closest_time = None
    min_altitude = float('inf')

    for i in range(24 * 60 * 60):  # 24 hours of seconds
        t = ts.utc(current_time + i * time_step)
        difference = satellite - landing_location
        topocentric = difference.at(t)
        altitude = topocentric.distance().km - 6371

        if altitude < min_altitude:
            min_altitude = altitude
            closest_time = t

        if altitude <= 0:
            print(f"Landing detected at {t.utc_iso()} with altitude {altitude:.2f} km")
            break
    else:
        print(f"No landing detected in the next 24 hours. Closest approach is at {closest_time.utc_iso()} with altitude {min_altitude:.2f} km")

###############################################################################
def checkArgv(cities):
    platform = "CSS (TIANHE)"
    bgColor = {}#'酒泉': ['2024年10月30日'], '文昌': ['2024年11月11日', '2024年11月15日']}
    if len(argv) > 1:
        pf = argv[1].upper()
        platform = PLATFORMS[pf] if pf in PLATFORMS else platform
        bgList = [a.strip() for a in argv]
        for bg in bgList[1:]:
            loc = bg.strip().split(':')
            if loc[0].strip() in cities:
                bgColor[loc[0].strip()] = [l.strip() for l in loc[1].split(',')]
    return platform, bgColor

################################################################################################
def createHtmlForElevation(cities):
    startDate = datetime.now(timezone.utc)
    hours = 2100
    platform, bgColor = checkArgv(cities)#'酒泉': ['2024年10月30日'], '文昌': ['2024年11月11日', '2024年11月15日']}
    passTime, tle = calculatePasses(cities, startDate, hours, platform)
    html = showTime(platform, passTime, tle, bgColor)
    filename = f'{TEMP_FILE_PATH}中国空间站轨道预测.html'
    # filename = f'{TEMP_FILE_PATH}中国空间站轨道预测{myDate.getJapanTimeFilename()}.html'
    myFile.saveTextFile(filename, html)

################################################################################################
def main():
    ssl._create_default_https_context = ssl._create_unverified_context
    cities = {
        '酒泉': (40.9667, 100.3, 1.0),   # altitude=1.0km 
        '文昌': (19.6167, 110.95, 1.5),  # altitude=1.5km 
        '西昌': (28.25, 102.03333, 1.5), # altitude=1.5km 
        '太原': (38.84257, 111.604815, 1.5),  # altitude=1.5km 
    }
    # createLineGraphForAltitude(cities)
    createHtmlForElevation(cities)
    # calculateLandingTime(cities)

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')
    
if __name__ == "__main__":
    showRunTime("main()")

