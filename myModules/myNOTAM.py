from re import findall, finditer, search
from myModules import myConst, myFile
from myModules import myDate

################################################################################################
def isChinaNotam(condition):
    if condition.strip() == '':
        return False
    isChinaNotam = False
    section = myFile.openConfig()
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
            isChinaNotam |= hasName
    
        for cond in firConditions:
            withCondition |= cond in condition
        isChinaNotam &= withCondition
        if isChinaNotam:
            return isChinaNotam
    return isChinaNotam

################################################################################################
def getNotamLocation(content) -> str:
    locStr = myFile.readConfigFirNames().replace(' ', '|')
    pattern = rf'A\) ((?:(?:{locStr}) ?){{0,4}})'
    locations = findall(pattern, content)
    loc = ''
    if len(locations) > 0:
        loc = '/'.join(sorted(locations[0].split()))
    return loc 

################################################################################################
def getNotamNumbers(content) -> tuple:
    numbers = finditer(myConst.PATTERN_NOTAM_NUMBER_NEW, content)
    return [m.group(1) for m in numbers][0]

################################################################################################
def getNotamDates(content) -> tuple:
    startDates = findall(myConst.PATTERN_START_DATE, content)
    endDates = findall(myConst.PATTERN_END_DATE, content)
    return startDates[0], endDates[0]

################################################################################################
def parseNotam(text):
    location = getNotamLocation(text)
    numbers = getNotamNumbers(text)
    text = text.replace('\n', '').replace(' ', '')
    startDates, endDates = getNotamDates(text)
    area = getNotamArea(text)
    return location, numbers, startDates, endDates, area

################################################################################################
def getNotamArea(contentSection) -> str:
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
                area += f'+{radiusList[0]}'
        else:
            area = '|'.join([a for a in area.split('-') if len(a.split('|')) > 3])
    return area

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
    return notam

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
            newll = findConvertLatitudeLongitude(radius[0])
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
    notamDict[key] = startDate + ";"
    notamDict[key] = notamDict[key] + endDate + ";"
    notamDict[key] = notamDict[key] + location + ";"
    notamDict[key] = notamDict[key] + area
    return notamDict

################################################################################################
def findConvertLatitudeLongitude(latlon):
    newLatLon2 = latlon
    matched = search(myConst.NEW_PATTERN1, latlon)
    if not matched:
        matched = search(myConst.NEW_PATTERN2, latlon)
    if matched:
        groupDict = matched.groupdict()
        newLatLon2 = f"{groupDict['latDir']}"
        newLatLon2 += f"{groupDict['latDeg']}°"
        newLatLon2 += f"{groupDict['latMin']}'"
        newLatLon2 += f"{groupDict['latSec']}\"" if groupDict['latSec'] != "" else ""
        newLatLon2 += ","
        newLatLon2 += f"{groupDict['lonDir']}"
        newLatLon2 += f"{groupDict['lonDeg']}°"
        newLatLon2 += f"{groupDict['lonMin']}'"
        newLatLon2 += f"{groupDict['lonSec']}\"" if groupDict['lonSec'] != "" else ""
    return newLatLon2

