from dataclasses import dataclass
from datetime import datetime, timedelta
from re import findall, finditer, search
from zoneinfo import ZoneInfo

from myModules import myConst
from myModules import myConfig
from myModules import myDate

@dataclass
class NotamClass:
    location: str
    number: str
    startDate: datetime = None # UTC
    endDate: datetime = None  # UTC
    coordinates: list[(float, float)] = None # coordinate(latitude纬度, longitude经度
    radius: int = 0 # meter

    def __init__(self, localtion: str, number: str, startDate: str, endDate: str, coordinates: list, radius: int = 0):
        self.location = localtion
        self.number = number
        self.startDate = self.parseDate(startDate)
        self.endDate = self.parseDate(endDate)
        self.coordinates = self.parseCoordinate(coordinates)
        self.radius = radius

    def __init__(self, localtion: str, number: str, coordinates: list, radius: int = 0):
        self.location = localtion
        self.number = number
        self.coordinates = [self.parseCoordinate(c) for c in coordinates.split('|')]
        self.radius = radius

    def setDates(self, startDate: datetime, endDate: datetime):
        self.startDate = startDate
        self.endDate = endDate

    def parseDate(self, date: str):
        return datetime.strptime(date, '%Y/%m/%d %H:%M')

    def parseCoordinate(self, coordinate: tuple) -> tuple: # coordinate(latitude纬度, longitude经度)
        lat = self.parseLatLon(coordinate[0])
        lon = self.parseLatLon(coordinate[1])
        return (lat, lon)

    def parseLatLon(self, latlong: str):
        dms = latlong.split('°')
        ms = dms[1].split("'")
        dir = dms[0][0]
        degree = int(dms[0][1:])
        minute = int(ms[0])
        second = int( ms[1][:-1] if len(ms) > 1 else 0)
        degreeMinuteSecond = (1 if dir in 'NE' else -1) * (degree + minute / 60 + second / 3600)
        return degreeMinuteSecond

    def print(self):
        sDate = self.startDate.strftime('%Y/%m/%d %H:%M') 
        eDate = self.endDate.strftime('%Y/%m/%d %H:%M')
        coords = [self.convertCoordinate(c) for c in self.coordinates]
        # ZSHA,A4319/25,2025/11/25 04:01,2025/11/25 04:43;N36°12',E121°12'|N35°05',E124°00'|N32°55',E124°00'|N34°29',E120°12'
        return f'{self.location},{self.number},{sDate},{eDate};{"|".join(coords)}{"+" + self.radius if self.radius > 0 else ""}'

    def convertCoordinate(self, coordinate: tuple) -> tuple: # coordinate(latitude纬度, longitude经度)
        latFloat, lonFloat = coordinate
        lat = self.convertLatLon(latFloat, 'N' if latFloat > 0 else 'S')
        lon = self.convertLatLon(lonFloat, 'E' if lonFloat > 0 else 'W')
        return (lat,lon)

    def convertLatLon(self, latlon: float, dir: str, onlyDegreeMinute=True):
        degree = int(latlon)
        minuteSecond = (latlon - degree) * 60
        minute = int(minuteSecond)
        second = (minuteSecond - minute) * 60
        return f'{dir}{degree}°{minute}\'' if onlyDegreeMinute else f'{dir}{degree}°{minute}\'{second}"'

################################################################################################
def isChinaNotamOld(condition, checkCondition=False):
    if condition.strip() == '':
        return False
    isChinaNotamOld = False
    section = myConfig.openConfig()
    count = int(section.get('FirCount'))
    for i in range(count):
        withCondition = False
        firNames = section.get(f'FirName{i + 1}').split(',')
        firConditions = section.get(f'FirCondition{i + 1}').split(',')

        for name in firNames:
            names = name.split('~')
            hasName = names[0] in condition
            if len(names) == 2:
                hasName &= names[1] not in condition
            isChinaNotamOld |= hasName
    
        if checkCondition:
            for cond in firConditions:
                withCondition |= cond in condition
            isChinaNotamOld &= withCondition
            if isChinaNotamOld:
                return isChinaNotamOld
    return isChinaNotamOld

################################################################################################
def isChinaNotam(condition, location, icaoList):
    # return True
    isChinaNotam = location in icaoList[1]
    for icao in icaoList[0].split(','):
        names = icao.split('~')
        if len(names) == 2 and location == names[0]:
            isChinaNotam &= names[1] not in condition
            break
        names = icao.split('+')
        if len(names) == 2 and location == names[0]:
            isChinaNotam &= names[1] in condition
            break
    return isChinaNotam

################################################################################################
def parseLocation(content) -> str:
    locStr = myConfig.readConfigFirNames().replace(' ', '|')
    pattern = rf'A\) ?((?:(?:{locStr}) ?){{0,4}})'
    locations = findall(pattern, content)
    loc = ''
    if len(locations) > 0:
        loc = '/'.join(sorted(locations[0].split()))
    return loc 

################################################################################################
def parseNumber(content) -> tuple:
    numbers = finditer(myConst.PATTERN_NOTAM_NUMBER_NEW, content)
    return [m.group(1) for m in numbers][0]

################################################################################################
def parseDates(content) -> tuple:
    startDates = findall(myConst.PATTERN_START_DATE, content)
    endDates = findall(myConst.PATTERN_END_DATE, content)
    return startDates[0], endDates[0]

################################################################################################
def parseArea(contentSection) -> str:
    area = ''
    lastEnd = 0
    startIndex = contentSection.find('E)')
    latlons = finditer(myConst.PATTERN_LATITUDE_LONGITUDE, contentSection[startIndex:])
    for m in latlons:
        if lastEnd > 0 and m.start() > lastEnd + 10:
            area += '-' + m.group()
        else:
            if m.group() not in area:
                if area != '':
                    area += '|'
                area += m.group() 
        lastEnd = m.end()
    if area:
        count = len(area.split('|')) + len(area.split('-'))
        if count == 2:
            radiusList = findall(myConst.PATTERN_RADIUS, contentSection[startIndex:])
            if radiusList:
                area += f'+{getRadiusInMeter(radiusList[0])}'
                # area += f'+{int(radiusList[0][0]) * 1000}'
            else:
                area = ''
        else:
            area = '-'.join([a for a in area.split('-') if len(a.split('|')) > 2])
    return area

###############################################################################
def getRadiusInMeter(m):
    myDict = {'海里':1852, '浬':1852, '公里':1000, '千米':1000, 'KM':1000, '米':1}
    if m[0] and m[1]:
        radius = float(m[0]) * myDict[m[1]]
    elif m[2] and m[3]:
        radius = float(m[2]) * myDict[m[3]]
    else:
        radius = 0
    return int(radius)

################################################################################################
def parseNotamText(notam, text):
    location, number, startDate, endDate, area = parseNotam(text)
    if location == 'RJJJ' and number.startswith('Q'):
        return notam
    if area != '':
        startDate = myDate.convertDate(startDate)
        endDate = myDate.convertDate(endDate)
        area = formatLatitudeLongitude(area)
        notam = getNoatmDict(notam, number, startDate, endDate, location, area)
        # notamClass = NotamClass(location, number, startDate, endDate, area)
    return notam

################################################################################################
def parseNotam(text):
    try:
        location = ''
        numbers = ''
        startDates = ''
        endDates = ''
        area = ''
        location = parseLocation(text)
        numbers = parseNumber(text)
        text = text.replace('\n', '').replace(' ', '')
        startDates, endDates = parseDates(text)
        area = parseArea(text)
    except:
        print(f'Parsing text: "{text}"\n')
        pass
    return location, numbers, startDates, endDates, area

################################################################################################
def formatLatitudeLongitude(oldData) -> str:
    newData = ''
    llListGroup = oldData.split('-')
    for ll in llListGroup:
        if newData != '':
            newData = newData[:-1] + '-'
        llList = ll.split('|')

        for oldll in llList:
            radius = oldll.split('+')
            newll = convertLatitudeLongitude(radius[0])
            if len(radius) == 2:
                newll += f'+{radius[1]}'
            newData += newll + '|'
    return newData[:-1]

################################################################################################
def getNoatmDict(notamDict, number, startDate, endDate, location, area):
    key = location + '/' + number
    if key in notamDict:
        items = notamDict[key].split(";")
        if startDate == items[0] and location != items[2]:
            location = items[2] + "/" + location
        c1 = [m.find(location) for m in notamDict.values()]
        c2 = [m.find(startDate) for m in notamDict.values()]
        c3 = [m.find(endDate) for m in notamDict.values()]
        if max(c1)>= 0 and max(c2) >= 0 and max(c3) >= 0:
            area1 = notamDict[key].split(";")[3]
            area = area1 + "-" + area if area != area1 else area
    elif len(area.split('|')) > 1:
        area = '-'.join([a for a in area.split('-') if len(a.split('|')) > 1 ])
    notamDict[key] = startDate + ";"
    notamDict[key] = notamDict[key] + endDate + ";"
    notamDict[key] = notamDict[key] + location + ";"
    notamDict[key] = notamDict[key] + area
    return notamDict

def pattern12(matched):
    groupDict = matched.groupdict()
    newLatlon = f"{groupDict['latDir']}"
    newLatlon += f"{groupDict['latDeg']}°"
    newLatlon += f"{groupDict['latMin']}'"
    newLatlon += f"{groupDict['latSec'].partition('.')[0]}\"" if groupDict['latSec'] != "" else ""
    newLatlon += ","
    newLatlon += f"{groupDict['lonDir']}"
    newLatlon += f"{groupDict['lonDeg']}°"
    newLatlon += f"{groupDict['lonMin']}'"
    newLatlon += f"{groupDict['lonSec'].partition('.')[0]}\"" if groupDict['lonSec'] != "" else ""
    return newLatlon

def pattern3(matched):
    groupDict = matched.groupdict()
    newLatlon  = f"{groupDict['latDir']}"
    newLatlon += f"{groupDict['latDeg']}°"
    latMin = groupDict['latMin'].split('.')
    newLatlon += f"{latMin[0].rjust(2, '0')}'"
    latSec = int((float(groupDict['latMin']) - int(latMin[0])) * 60)
    newLatlon += f'{latSec:02d}"'
    newLatlon += ","
    newLatlon += f"{groupDict['lonDir']}"
    newLatlon += f"{groupDict['lonDeg']}°"
    lonMin = groupDict['lonMin'].split('.')
    newLatlon += f"{lonMin[0].rjust(2, '0')}'"
    lonSec = int((float(groupDict['lonMin']) - int(lonMin[0])) * 60)
    newLatlon += f'{lonSec:02d}"'
    return newLatlon

################################################################################################
def convertLatitudeLongitude(latlon):
    matched = search(myConst.NEW_PATTERN3, latlon)
    if matched:
        return pattern3(matched)
    
    matched = search(myConst.NEW_PATTERN1, latlon)
    if not matched:
        matched = search(myConst.NEW_PATTERN2, latlon)

    if matched:
        return pattern12(matched)
    return latlon

################################################################################################
def parseNotamFromMsaTextFile(oldFile):
    print("\nSearching 9: 'MSA for SD(ShanDong), GD(GuangDong), HN(HaiNan), NAV8/11(NAVAREA VIII/XI) and PAC(HYDROPAC)'...")
    notams = {}
    msaSet = set()

    with open(oldFile, 'r', encoding='utf-8') as f:
        msaList = f.read().split('\n\n')

    for msa in msaList:
        location, number, startDates, endDates, areas = parseMsa(msa)
        lastStart = ''
        lastEnd = ''

        from myModules import myFile
        for i, area in enumerate(areas):
            startDate = startDates[i] if i < len(startDates) else lastStart
            endDate = endDates[i] if i < len(endDates) else lastEnd
            nowUTC = datetime.now(ZoneInfo('UTC')).strftime('%Y/%m/%d %H:%M')

            if endDate <= nowUTC:
                print(f'The date was past:\n{msa}')
                break

            startDate = startDate if startDate else getUTCTime()[:-3]
            endDate = endDate if endDates else getUTCTime()[:-3]
            title = f"{oldFile.replace('.txt', '').split('/')[-1]}"
            title = myFile.convertTitle(startDate, endDate, title, isLocalTime=True)

            if area:
                area = formatMSALatitudeLongitude([area])[0]
                coords = area.split('|')
                coordsList = [myFile.convertDMS2DD(c) for c in coords]
                if len(coordsList) == 1:
                    radius = parseRadius(msa)
                    if radius > 0:
                        area += f'+{radius}'
                notams = getNoatmDict(notams, number, startDate, endDate, location, area)
                msaSet.add(number[:2]) if location == 'MSA' else msaSet.add(location)
                lastStart = startDate
                lastEnd = endDate

    count = len(notams)
    msaSet = ['GD', 'HN', 'SD', 'NAV8', 'NAV11','PAC'] if count == 0 else msaSet
    print(f'{count} MSA(s) for {sorted(msaSet)}\n')
    return notams

################################################################################################
def parseMsa(text):
    number = parseMsaLocation(text)
    location = 'PAC' if 'HYDROPAC' in text else 'NAV8' if 'NAVAREA VIII' in text else 'NAV11' if 'NAVAREA XI' in text else 'MSA'
    text = text.replace('\n', '').replace(' ', '').replace('/', '').replace('、', ',').replace('\xa0', '')
    startDates, endDates = parseMsaDates(text)
    areas = parseMsaArea(text)
    return location, number, startDates, endDates, areas

################################################################################################
MSA_PATTERN_LATITUDE_LONGITUDE =  r'(\d{2}[°-]\d{2}[\′.-]?\d{0,3}″?[NS][ \/]?\d{2,3}[°-]\d{1,2}[′.-]?\d{0,3}"?[EW])'
def parseMsaArea(contentSection) -> str:
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
# 自2025年11月10日至11月11日，每日0925时至1140时
# 自2025年11月9日0300时至0600时
# 自11月9日0400时至0600时
# 012340 TO 020400 UTC JUL 26
MSA_PATTERN_DATE_CHINA = r'(?:(?P<sYear>\d{2,4})年)?(?:(?P<sMonth>\d{1,2})月)?(?P<sDay>\d{1,2})日(?:(?P<sTime1>\d{1,4})时)?至(?:(?P<eYear>\d{2,4})年)?(?:(?P<eMonth>\d{1,2})月)?(?:(?P<eDay>\d{1,2})日)?(?:，每日)?(?:(?P<sTime2>\d{1,4})时)?至?(?:(?P<eTime>\d{1,4})时)'
MSA_PATTERN_DATE = r'FROM(\d{0,2})(\d{0,4})UTC([A-Z]{0,4})\.?(\d{0,2})TO(\d{0,2})(\d{0,4})UTC([A-Z]{0,4})\.?(\d{0,2})'
NAVAREA_PATTERN = r'(?:(?P<sDay>\d{1,2})(?P<sMonth>[A-Z]{3,4})(?P<sYear>\d{2})FROM(?P<sTime1>\d{0,4})TO(?P<eTime>\d{0,4})UTC(?P<eYear>)(?P<eMonth>)(?P<eDay>)(?P<sTime2>))'
NAVAREA_PATTERN+= r'|(?:(?P<sDay_2>\d{2})\s*(?P<sTime1_2>\d{4})(?:Z|\s*UTC)?\s*TO\s*(?P<eDay_2>\d{2})\s*(?P<eTime_2>\d{4})(?:Z|\s*UTC)?\s*(?P<sMonth_2>[A-Z]{3})\.?\s*(?P<sYear_2>\d{2})?(?P<eMonth_2>)(?P<eYear_2>)(?P<sTime2_2>))'
HYDROPAC_PATTERM = r'SPACEDEBRIS(?P<sDay>\d{2})(?P<sTime1>\d{4})Z(?P<sMonth>[A-Z]{0,3})(?P<sYear>\d{0,2})TO(?P<eDay>\d{2})(?P<eTime>\d{4})Z(?P<eMonth>[A-Z]{3})(?P<eYear>\d{0,2})'
def parseMsaDates(content: str) -> tuple:
    startDates, endDates = [], []
    startEndDates1 = [m for m in finditer(MSA_PATTERN_DATE_CHINA, content)]
    startEndDates2 = [m for m in finditer(NAVAREA_PATTERN, content)]
    startEndDates3 = [m for m in finditer(HYDROPAC_PATTERM, content)]
    startEndDates = startEndDates1 if startEndDates1 else startEndDates2 if startEndDates2 else startEndDates3
    if startEndDates:
        for m in startEndDates:
            startYear = m.group('sYear') if m.group('sYear') else myDate.getJapanDate()[:4]
            startYear = '20' + startYear if len(startYear) == 2 else startYear
            startMonth = m.group('sMonth') if m.group('sMonth') else ''
            startMonth = int(startMonth) if startMonth.isdigit() else datetime.strptime(startMonth, '%b').month if startMonth else ''
            startDay = int(m.group('sDay')) if m.group('sDay') else ''
            startTime = m.group('sTime1') if m.group('sTime1') else m.group('sTime2') if m.group('sTime2') else ''
            startTime = myDate.convertTime(startTime)
            endYear = m.group('eYear') if m.group('eYear') else startYear
            endMonth = m.group('eMonth') if m.group('eMonth') else str(startMonth)
            endMonth = int(endMonth) if endMonth.isdigit() else datetime.strptime(endMonth, '%b').month if endMonth else ''
            startMonth = endMonth if not startMonth else startMonth
            endDay = int(m.group('eDay')) if m.group('eDay') else startDay
            endTime = myDate.convertTime(m.group('eTime')) if m.group('eTime') else ''
            if startYear and startMonth and startDay and startTime:
                startDate = f'{startYear}/{startMonth:02}/{int(startDay):02} {startTime}'
            else:
                break
            if endYear and endMonth and endDay and endTime:
                endDate = f'{endYear}/{endMonth:02}/{endDay:02} {endTime}'
            else:
                break
            if startEndDates1:
                startDate = convertChinaTimeToUTC(startDate)
                endDate = convertChinaTimeToUTC(endDate)
            startDates.append(startDate)
            endDates.append(endDate)
    if startEndDates2:
        for m in startEndDates2:
            startYear = m.group('sYear_2') if m.group('sYear_2') else myDate.getJapanDate()[:4]
            startYear = '20' + startYear if len(startYear) == 2 else startYear
            startMonth = m.group('sMonth_2') if m.group('sMonth_2') else ''
            startMonth = int(startMonth) if startMonth.isdigit() else datetime.strptime(startMonth, '%b').month if startMonth else ''
            startDay = int(m.group('sDay_2')) if m.group('sDay_2') else ''
            startTime = m.group('sTime1_2') if m.group('sTime1_2') else m.group('sTime2_2') if m.group('sTime2_2') else ''
            startTime = myDate.convertTime(startTime)
            endYear = m.group('eYear_2') if m.group('eYear_2') else startYear
            endMonth = m.group('eMonth_2') if m.group('eMonth_2') else str(startMonth)
            endMonth = int(endMonth) if endMonth.isdigit() else datetime.strptime(endMonth, '%b').month if endMonth else ''
            startMonth = endMonth if not startMonth else startMonth
            endDay = int(m.group('eDay_2')) if m.group('eDay_2') else startDay
            endTime = myDate.convertTime(m.group('eTime_2')) if m.group('eTime_2') else ''
            if startYear and startMonth and startDay and startTime:
                startDate = f'{startYear}/{startMonth:02}/{int(startDay):02} {startTime}'
            if endYear and endMonth and endDay and endTime:
                endDate = f'{endYear}/{endMonth:02}/{endDay:02} {endTime}'
            if startEndDates1:
                startDate = convertChinaTimeToUTC(startDate)
                endDate = convertChinaTimeToUTC(endDate)
            startDates.append(startDate)
            endDates.append(endDate)
    return startDates, endDates

################################################################################################
def convertChinaTimeToUTC(localDate):
    ChinaTimeZone = ZoneInfo('Asia/Shanghai')
    local = datetime.strptime(localDate, '%Y/%m/%d %H:%M')
    utc = local.replace(tzinfo=ChinaTimeZone).astimezone(ZoneInfo('UTC'))
    utcDate = utc.strftime('%Y/%m/%d %H:%M')
    return utcDate

################################################################################################
MSA_LOCATIONS = {'辽航警': 'LN', '鲁航警': 'SD', '粤航警': 'GD', '琼航警': 'HN', '沪航警': 'SH', '云航警': 'LYG', 'NAVAREA VIII -': '', 'NAVAREA XI NO.': '', 'HYDROPAC ': ''}
MSA_PATTERN_NUMBER = r'([A-Z][A-Z]|辽航警|鲁航警|粤航警|琼航警|沪航警|云航警|NAVAREA VIII \-|NAVAREA XI NO\.|HYDROPAC )(\d{0,2}\-?\d{1,4}\/?\d{0,2})'
def parseMsaLocation(content) -> str:
    locations = finditer(MSA_PATTERN_NUMBER, content)
    for m in locations:
        if m.group(1) in MSA_LOCATIONS:
            if '-' in m.group(2):
                arr = m.group(2).split('-')
                return f'{arr[1]}/{arr[0]}'  
            else:
                return f'{MSA_LOCATIONS[m.group(1)]}{m.group(2)}' 
        else:
            return m.groups()
    else:
        return ''

################################################################################################
def getUTCTime(fmt='') -> str:
    if fmt == '':
        fmt = "%Y/%m/%d %H:%M:%S"
    return datetime.now(ZoneInfo('UTC')).strftime(fmt)

################################################################################################
def formatMSALatitudeLongitude(oldData) -> str:
    newData = []
    for data in oldData:
        oldllList = data.split('|')

        newllList = ''
        for oldll in oldllList:
            newll = convertLatitudeLongitude(oldll)
            newllList += newll + '|'
        newData.append(newllList[:-1])
    return newData

################################################################################################
MSA_RADIUS_PATTERN = r'(?:为中心|圆心)[、，]?(?:(\d{1,4}\.?\d{0,2})(海里|浬|公里|千米|米)为半径|半径(\d{1,4})(海里|浬|公里|千米|米))'
def parseRadius(content):
    radiusMatch = findall(MSA_RADIUS_PATTERN, content)
    for m in radiusMatch:
        radius = getRadiusInMeter(m)
        if radius > 0:
            break
    return radius

################################################################################################
def isSpecialNoatms(lastLoc, lastSartDate, loc, startDate):
    RJJJ_ZKPM_ZGZU = (lastLoc == 'RJJJ' and (loc == 'ZKPM' or loc == 'ZGZU'))
    NVA8_VECF_VOMF = (lastLoc == 'NAV8' and (loc == 'VECF' or loc == 'VOMF'))
    KZAK_RPHI_MSA = lastLoc == 'KZAK' and (loc == 'RPHI' or loc == 'MSA')
    MSA_ZJSA = (lastSartDate == startDate and lastLoc == 'MSA' and loc == 'ZJSA')
    RJJJ_ZSHA = (lastLoc == 'RJJJ' and loc == 'ZSHA')
    RPHI_ZJSA = (lastLoc == 'RPHI' and loc == 'ZJSA')
    VCCF_ZLHW_ZKPM = (lastLoc == 'VCCF' and ('ZLHW' in loc or 'ZPKM' in loc))
    WIIF_VVHM = (lastLoc == 'WIIF' and loc == 'VVHM')
    isSpecial = (MSA_ZJSA or NVA8_VECF_VOMF or KZAK_RPHI_MSA or RJJJ_ZKPM_ZGZU or RJJJ_ZSHA or RPHI_ZJSA or VCCF_ZLHW_ZKPM or WIIF_VVHM) 
    isSpecial = isSpecial and not isNewLaunch(startDate, lastSartDate)
    return isSpecial

################################################################################################
def isNearTime(oldDate, newDate, minutes=5.0):
    dt1 = datetime.strptime(oldDate, '%Y/%m/%d %H:%M')
    dt2 = datetime.strptime(newDate, '%Y/%m/%d %H:%M')
    if abs(dt2 - dt1) < timedelta(minutes=minutes):
        return True
    else:
        return False

################################################################################################
def isNewLaunch(oldDate, newDate, minutes=120.0):
    dt1 = datetime.strptime(oldDate, '%Y/%m/%d %H:%M')
    dt2 = datetime.strptime(newDate, '%Y/%m/%d %H:%M')
    if abs(dt2 - dt1) > timedelta(minutes=minutes) or (oldDate == newDate and oldDate[-5:] == '00:00'):
        return True
    else:
        return False

#####################################################################################
def isLowerLatitude(coordsList1, coordsList2):
    if coordsList1:
        return coordsList1[0][1] >= coordsList2[0][1] or len(coordsList1) == 1
    else:
        return False

#####################################################################################
def isNextDropZone(lastLoc, loc):
    RPHI_YMMM = lastLoc == 'RPHI' and loc == 'YMMM'
    RJJJ_MSA = 'RJJJ' in lastLoc and loc == 'MSA'
    ZWUQ_VCCF = 'ZWUQ' in lastLoc and loc == 'VCCF'
    ZLHW_RPHI = 'ZLHW' in lastLoc and (loc == 'RPHI' or loc == 'MSA')
    ZWUQ_ZLHW = 'ZWUQ' in lastLoc and loc == 'ZLHW'

    if RPHI_YMMM or RJJJ_MSA or ZWUQ_VCCF or ZLHW_RPHI or ZWUQ_ZLHW:
        return False
    else:
        return True

################################################################################################
def parseLaunch(notam) -> list:
    notamList = []
    notamLaunch = []
    lastKey = ''
    lastValue = ''
    lastLoc = ''
    lastSartDate = ''
    lastCoordsList = []
    from myModules import myFile

    for key, value in notam.items():
        loc = key.split('/')[0]
        items = value.split(';')
        startDate = items[0]

        for coords in items[3].split('-'):
            coordsList = [myFile.convertDMS2DD(c)  for c in coords.split('|')]

            if not notamLaunch:
                notamLaunch.append({key: value})
            elif isSpecialNoatms(lastLoc, lastSartDate, loc, startDate):
                lastIndex = notamLaunch.index({lastKey: lastValue})
                notamLaunch.insert(lastIndex, {key: value})
                key = lastKey
                value = lastValue
                startDate = lastSartDate
                coordsList = lastCoordsList
                loc = lastLoc
            elif not isNewLaunch(lastSartDate, startDate) and isNextDropZone(lastLoc, loc):
                if isNearTime(lastSartDate, startDate) or isLowerLatitude(lastCoordsList, coordsList):
                    notamLaunch.append({key: value})
                else: # new launch
                    if notamLaunch:
                        notamList.append(notamLaunch)
                    notamLaunch = [{key: value}]
            else:
                if {lastKey: lastValue} not in notamLaunch:
                    notamLaunch.append({lastKey: lastValue})
                notamList.append(notamLaunch)
                notamLaunch = [{key: value}]

            lastKey = key
            lastValue = value
            lastSartDate = startDate
            lastCoordsList = coordsList
            lastLoc = loc

    notamList.append(notamLaunch)
    return notamList
