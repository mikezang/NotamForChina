"""
    Thie is NSF module to parse luanch data from NSF site
    https://forum.nasaspaceflight.com/index.php?board=40.0
"""
# pylint: disable=W0105,W0511,W0703,C0103,C0116,C0301

from json import dump, load
import locale
from re import findall, finditer, search, sub, IGNORECASE
from datetime import date, datetime, timedelta
import sys
from timeit import timeit
from pytz import UTC, timezone
from selenium.webdriver.common.by import By

from myModules import myConst
from myModules import myExcept
from myModules import myConst
from myModules import myNet
from myModules import myFile
from myModules import myDate
from myModules import myDict

TEMP_FILE_PATH = './temp/'

################################################################################################
def splitTitle(item: list) -> str:
    items = item[1].split(' - ')
    count = len(items)
    if count == 4:
        titleDate = getDateFromTitle(item[1])
        localDate = convertNsfDate(titleDate, myConst.TIMEZONE_SHANGHAI)
        localDateStr = localDate.strftime("%Y年%m月%d日%H时%M分") if localDate else items[3]
        key = items[1] + localDateStr + items[2] + items[0]
    elif count == 3:
        key = items[1] + items[2] + items[0]
    elif count == 2:
        key = items[1] + items[0]
    else:
        key = items[0]
    return key

################################################################################################
def sortByTitle(d: dict) -> dict:
    return {k : v for k, v in sorted(d.items(), key=lambda x: splitTitle(x))}

################################################################################################
def writeNsfToFile(nsfDict):
    filename = f'{TEMP_FILE_PATH}nsfLinkList.html'
    newText = f"<H2>Chinese Launchers POST List</H2>"
    nsfDict = sortByTitle(nsfDict)
    for i, (key, value) in enumerate(nsfDict.items()):
        values = value.split(':')
        newText += f'{i + 1:03}-{values[0]}: <a target=_blank href={key}>{':'.join(values[1:])}</a><br>'
    myFile.saveTextFile(filename, newText)

################################################################################################
def isPastDate(oldDate) -> bool:
    baseDate = date.today()
    if baseDate >= oldDate.date():
        return True
    else:
        return False

################################################################################################
def updateNotamDict(notamDict, notam) -> dict:
    for k, v in notam.items():
        if k not in notamDict or v.split(";")[2] == '':
            notamDict[k] = v
    return notamDict

################################################################################################
def printNsf(launch_date) -> None:
    print(f"\nNSF发射数据{myDate.getJapanTime()}")
    print("==============================")
    printNsfDict(launch_date)

################################################################################################
def getNsfUrl(driver, page) -> dict:
    urls = {}
    myNet.elementLocatedBy(driver, By.CLASS_NAME, "table_grid")
    table = driver.find_element(By.CLASS_NAME, "table_grid")
    rows = table.find_elements(By.TAG_NAME, "tr")

    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")

        for col in cols:
            className = col.get_attribute("class")
            if 'stickybg' in className or 'lockedbg' in className:
                continue

            if "subject" in className:
                ahref = row.find_element(By.TAG_NAME, "a")
                href = ahref.get_attribute("href") + ';all'
                href = sub(r'PHPSESSID\=[a-z0-9]+\&', '', href)
                title = ahref.text
                urls[href] = f'Page{page:02}: {title}'
    return urls

################################################################################################
def getDateFromTitle(title) -> str:
    titleDate = myFile.removeAllSpaces(title.split("-")[-1])
    if title.lower() == 'Gaofen-4, long march-3B, XSLC, December 28, 2015 (16:04 UTC)'.lower():
        titleDate = titleDate.split('XSLC,')[1].replace(',', '')
    elif title.lower() == 'Chuang Xin 1-04 and Ling Qiao - cz-2D - JSLC, 00:15, September 4th, 2014'.lower():
        titleDate = titleDate.split('JSLC,')[1].replace('th', '')
    return titleDate

################################################################################################
def getNsfUrlList(driver, p='1') -> dict:
    urls = {}
    invalidUrls = {}
    driver.get(myConst.NSF_URL_CHINA)
    # myNet.checkVPN(driver)

    if p == 'all' or p == 'url':
        lastPage = getNsfPages(driver)
        startPage = 1
    else:
        lastPage = int(p)
        startPage = lastPage

    for page in range(startPage, lastPage + 1):
        href = myConst.NSF_URL_CHINA + str(50 * (page - 1))
        print(f"Page{page:02}: {href}")

        if page > 1:
            driver.get(href)

        nsfUrls = getNsfUrl(driver, page)
        urls.update(nsfUrls)
    return urls

################################################################################################
def parseNsfContents(driver, nsfUrls, titleForCheck):
    for i, (title, pageUrl) in enumerate(nsfUrls.items()):
        if titleForCheck == '' or title == titleForCheck: #'2022年06月05日10時44分酒泉長征二号己':
            page, url = pageUrl.split(",")
            parseNsfContent(driver, i, title, page, url)

################################################################################################
def parseNsfContent(driver, i, title, basePage, baseUrl) -> None:
    url = baseUrl + ';all'
    driver.get(url)

    lastPage = getNsfPages(driver)
    printTitlePages(title, lastPage, i)

    if lastPage < 11:
        startPage = lastPage
    else:
        startPage = 1

    html = driver.page_source
    for page in range(startPage, lastPage + 1):
        if startPage == 1 and page > 1:
            url = baseUrl[:-5] + str(20 * (page - 1))
            driver.get(url)
            html += driver.page_source

    html = myNet.getXmlTextContent(html)
    html = myFile.removeAllSpaces(html)
    html = html.replace(r'\n', '').replace(r'\r', '').replace(r'\t', '')
    html = sub(r'sSessionId.+|Read\d{0,10}times', '', html)
    header = findall(myConst.NSF_PAGE_HEADER, html)
    if header and len(header) == 1:
        html = sub(r'.+' + myConst.NSF_PAGE_HEADER, '', html)

    notam = {}
    coords = [f'{basePage},{baseUrl}']

    coodinatesNotam = findall(myConst.PATTERN_LATITUDE_LONGITUDE, html)
    if coodinatesNotam:
        coords.append(f'{[myFile.findConvertLatitudeLongitude(c) for c in coodinatesNotam]}')
        print(coodinatesNotam)
    else:
        coords.append([])

    coodinatesMsa = findall(myConst.MSA_PATTERN_LATITUDE_LONGITUDE1, html)
    if coodinatesMsa:
        coords.append(f'{[myFile.findConvertLatitudeLongitude(c) for c in coodinatesMsa]}')
        print(coodinatesMsa)
    else:
        coords.append([])

    if coords:
        filename = f'c:/zang/rockets/pages/{title}'
        coords.append([f'{html}'])
        notam[title] = coords
        updateDictToJsonFile(notam, filename)

################################################################################################
def updateDictToJsonFile(nsf_data, filename, isBackup=False):
    nsf_old = loadDictFromJsonFile(filename)

    if nsf_old is not None:
        nsf_new = nsf_old.copy()
        nsf_new.update(nsf_data)
        nsf_new = myDict.sortDictByKey(nsf_new)

        if nsf_old != nsf_new:
            saveDictToJsonFile(nsf_new, f"{filename}")
            if isBackup:
                saveDictToJsonFile(nsf_data, f'{filename}{myDate.getJapanTime("-%Y%m%d-%H%M%S")}')
        # else:
        #     print(f'Not update to file "{filename}.json"')
    else:
        saveDictToJsonFile(nsf_data, f"{filename}")
        if isBackup:
            saveDictToJsonFile(nsf_data, f'{filename}{myDate.getJapanTime("-%Y%m%d-%H%M%S")}')

################################################################################################
def saveDictToJsonFile(nsfDict, filename):
    print(f'Save   to file "{filename}.json"')
    with open(f'{filename}.json', "w", encoding="utf-8") as f:
        dump(nsfDict, f, ensure_ascii=False, indent=2)

################################################################################################
def loadDictFromJsonFile(filename):
    try:
        with open(f'{filename}.json', encoding="utf-8") as f:
            print(f'Load from file "{filename}.json".')
            return load(f)
    except FileNotFoundError:
        return None

################################################################################################
def updateNsfNotamJsonFile(nsf_new, filename):
    nsf_old = loadDictFromJsonFile(filename)

    if nsf_old is not None:
        for k, vNew in nsf_new.items():
            if k not in nsf_old:
                nsf_old[k] = vNew
            elif vNew is str:
                continue
            elif nsf_old[k] is str:
                nsf_old[k] = vNew
            elif nsf_old[k] != nsf_new[k]:
                nsf_old[k] = nsf_new[k]

        nsf_old = myDict.sortDictByKey(nsf_old)

        if nsf_old != nsf_new:
            saveDictToJsonFile(nsf_old, f"{filename}")
            saveDictToJsonFile(nsf_old, f'{filename}{myDate.getJapanTime("-%Y%m%d-%H%M%S")}')
        else:
            print(f'Not update to file "{filename}.json"')
    else:
        saveDictToJsonFile(nsf_new, f"{filename}")
        saveDictToJsonFile(nsf_new, f'{filename}{myDate.getJapanTime("-%Y%m%d-%H%M%S")}')

################################################################################################
def getNsfList(driver, nsfUrls, titleForCheck):
    for i, (title, url) in enumerate(nsfUrls.items()):
        if titleForCheck == '' or title == titleForCheck:
            notam = getNsfDetail(driver, i, title, url.split(",")[1])
            if notam and '?' not in title:
                nsfUrls[title] = [url, myDict.sortDictByValue(notam)]
            else:
                nsfUrls[title] = url
    return nsfUrls

################################################################################################
def getNsfDetail(driver, i, title, baseUrl) -> dict:
    notamDict = {}
    startPage = 1
    year = title[2:4]

    url = baseUrl #+ ';all'
    driver.get(url)
    # myNet.checkVPN(driver)

    lastPage = getNsfPages(driver)
    printTitlePages(title, lastPage, i)

    if lastPage < 11:
        startPage = lastPage

    html = driver.page_source
    for page in range(startPage, lastPage + 1):
        if startPage == 1 and page > 1:
            url = baseUrl[:-5] + str(20 * (page - 1))
            driver.get(url)
            html += driver.page_source

    html = myNet.getXmlTextContent(html)
    html = html.replace('MEPEP', myConst.MEPEP).replace('MUMAN', myConst.MUMAN).replace('LUVAR', myConst.LUVAR)
    html = myFile.removeAllSpaces(html)
    # html = html.replace('\n', '').replace("\r", "")
    notamDict.update(getNsfNotam(html, year, i))
    notamDict = removeDuplicateNotams(notamDict)
    return notamDict

# how to find all latitude and longitude
# current algorithem:
# 1. find numbers r'[^R]([A-Z]\d{4}/\d{2}|1345/16)[^0]'
#  1.1 find dates and latitude and longitude betwenn section by numbers
# 2. find dates r'B\)(\d{10})', r'C\)(\d{10})'
#    find dates r'(\d{1,2}[a-zA-Z]+\d{2}:\d{2}\d{4})UNTIL(\d{1,2}[a-zA-Z]+\d{2}:\d{2}\d{4})'
#    find dates r'FROM(\d{4}UTC\d{2}[a-zA-Z]+\d{4})TO(\d{4}UTC\d{1,2}[a-zA-Z]+\d{4})'
#  2.1 find latitude and longitude betwenn section by dates
# 3. find others latitude and longitude
# 4. find MSA dates, latitude and longitude
#
# 1. find numbers
#  1.1 startDate/endDate/location/coodinates bteween numbers[i] and numbers[i+1]
#  1.2 find location by coordinates
# 2. find startDates/endDates if last number section is not end of content
#  2.1 find location/coodinates bteween startDates[i] and startDates[i+1]
#  2.2 find location by coordinates
# 3. find MSA
#  3.1 find coodinates bteween MSA[i] and MSA[i+1]
# 4. find HYDROPAC
#  4.1 find coodinates bteween HYDROPAC[i] and HYDROPAC[i+1]
# 5. find specialMSA
#  5.1 find coodinates bteween specialMSA[i] and specialMSA[i+1]
################################################################################################
def getNsfNotamsFromFile(nsf_list, titleForCheck) -> dict:
    notam = {}
    for j, (title, _) in enumerate(nsf_list.items()):
        if titleForCheck == '' or title == titleForCheck: #'2022年06月05日10時44分酒泉長征二号己':
            conetnts = loadDictFromJsonFile(f'C:/zang/rockets/pages/{title}')
            pageUrl, _, _, content = conetnts[title]
            year = title[2:4]
            notam[title] = [f'{pageUrl}, {getNsfNotam(content[0], year, j)}']
    return notam

################################################################################################
def getNsfNotam(content, year, j) -> dict:
    notam = {}

    latlons = search(myConst.PATTERN_LATITUDE_LONGITUDE, content)
    if not latlons:
        latlons = search(myConst.MSA_PATTERN_LATITUDE_LONGITUDE, content)
        if not latlons:
            return notam

    numbersList = getNsfNumbers(content)
    countNumbers = len(numbersList)

    if countNumbers > 0:
        numberSet = set()
        for i, (number, startIndex, _) in enumerate(numbersList):
            endIndex = len(content) if i == countNumbers - 1 else numbersList[i + 1][1]
            contentSection = content[startIndex:endIndex]
            startDate, endDate, location, area = getNsfNotamData1(contentSection)

            if area:
                notam = updateNotam(notam, number, startDate, endDate, location, area)
                numberSet.add(number)
        print(f'{sorted(numberSet)}')
    else:
        startDates, endDates = getNsfDatesGroup(content)
        endDatesList = [(m.group(1), m.start(), m.end()) for m in endDates]
        countDates = len(endDatesList)

        if countDates > 0:
            startDatesList = [m.group(1) for m in startDates]
            dateSet = set()
            for i, (endDate, _, endIndex) in enumerate(endDatesList):
                startDate = myDate.convertDate(startDatesList[i])
                endDate = myDate.convertDate(endDate)
                number = f'?{1000 + i + 1:04}/{year}'
                startIndex = 0 if i == 0 else endDatesList[i - 1][2]
                contentSection = content[startIndex:endIndex]
                location, area = getNsfNotamData2(contentSection)
                if area:
                    notam[number] = f'{startDate};{endDate};{location};{area}'
                    dateSet.add(startDate)
            print(f'{sorted(dateSet)}')
        else:
            # only latitude and longitute
            location, area = getNsfNotamData3(content)
            if area:
                print('Has Coordinates')
                number = f'?{j + 2001:04}/{year}'
                startDate = ''
                endDate = ''
                notam[number] = f'{startDate};{endDate};{location};{area}'

    # check MSA information for laucnh from Sea
    startDates, endDates, areas = getNsfNotamDataMsa(content, year)
    for i, (startDate, endDate, area) in enumerate(zip(startDates, endDates, areas)):
        if area:
            print('MSAC Coordinates')
            number = f'?{3000 + i + 1:04}/{year}'
            location = 'MSAC' #getLocationIfInsideBoundary(area)
            notam[number] = f'{startDate};{endDate};{location};{area}'

    # check HYDROPAC information
    header, startDates, endDates, areas = getNsfNotamDataHydropac(content, year)
    if areas:
        for i, (startDate, endDate, area) in enumerate(zip(startDates, endDates, areas)):
            if area:
                print(f'{header} Coordinates')
                number = f'?{4000 + i + 1:04}/{year}'
                location = header[:4]
                notam[number] = f'{startDate};{endDate};{location};{area}'

    # check data as below
    # Round trip towing of the Tairui platform from Haiyang port to the launch site was announced beforehand via navigational warnings
    # Forward
    # Published May 31; validity June 2, 0200UTC to June 4, 16000
    # Tugboats: Beihai Jiu 101 and Beihai Jiu 118
    # From Haiyang port to Lianyungang waters via 3632N12116E，3600N12123.5E，and 3454N12112E
    # Total towing length: 500 meters; speed: 5 knots
    # Return
    # Published June 5; validity June 5, 1000UTC to June 8, 1800 UTC
    # Tugboats: Beihai Jiu 101 and Beihai Jiiu 118
    # From Lianyungang waters to Haiyang port via 3454N12112E，3600N12123.5E and 3632N12116E
    # Total towing length: 500 meters; speed: 5 knots
    startDates, endDates, areas = getNsfNotamDataMsa1(content, year)
    if areas:
        for i, (startDate, endDate, area) in enumerate(zip(startDates, endDates, areas)):
            if area:
                print('MSAC Coordinates')
                number = f'?{5000 + i + 1:04}/{year}'
                location = 'MSAC'
                notam[number] = f'{startDate};{endDate};{location};{area}'
    return notam

################################################################################################
def updateNotam(notam, number, startDate, endDate, location, area):
    if number not in notam:
        notam[number] = f'{startDate};{endDate};{location};{area}'
    else:
        startDateOld, endDateOld, locationOld, areaOld = notam[number].split(';')
        if len(startDate) > len(startDateOld) or len(endDate) > len(endDateOld) or len(location) > len(locationOld) or len(area) > len(areaOld):
            notam[number] = f'{startDate};{endDate};{location};{area}'
    return notam

################################################################################################
def convertMsaCoordinates(oldCoords) -> str:
    #lat=37-42-46N, lon=120-10-98E
    #lat=37-42.6N, lon=120-10.8E
    newCoords = ''
    for lat, lon in oldCoords:
        if newCoords != '':
            newCoords += '|'
        newCoords += f"{lat[-1]}{lat[:2]}°{lat[3:5]}',{lon[-1]}{lon[:3]}°{lon[4:6]}'"
        # newCoords += f"{lat[-1]}{lat[:2]}°{lat[3:5]}'{round(float(lat[5:8]) * 60)},{lon[-1]}{lon[:3]}°{lon[4:6]}'{round(float(lon[6:9]) * 60)}"
    return newCoords

################################################################################################
def convertMsaDate(d) -> str:
    return datetime.strptime(d.replace("SEPT", "SEP"), '%y%b%d%H%M').strftime("%Y/%m/%d %H:%M")

################################################################################################
def convertMsaDate1(d) -> str:
    return datetime.strptime(d, '%y%B%d%H%M').strftime("%Y/%m/%d %H:%M")

################################################################################################
def getNsfMsaDates(content, year) -> list:
    seaDates = finditer(myConst.MSA_PATTERN_DATE, content)
    seaDatesList = [(m.groups(), m.start(), m.end()) for m in seaDates]
    startDates, endDates, starts, ends = [], [], [], []
    for i, d in enumerate(seaDatesList):
        # d = (('25', '0500', 'SEPT', '08', '1000', 'OCT'), 24383, 24410)
        month = d[0][2] if d[0][2] != '' else d[0][5]
        startDates.append(convertMsaDate(f'{year}{month}{d[0][0]}{d[0][1]}'))
        endDates.append(convertMsaDate(f'{year}{d[0][5]}{d[0][3]}{d[0][4]}'))
        starts.append(d[1])
        ends.append(seaDatesList[i + 1][1] if i + 1 < len(seaDatesList) else len(content))
    return startDates, endDates, starts, ends

################################################################################################
def getNsfNotamDataMsa(content, year) -> list:
    startDates, endDates, starts, ends = getNsfMsaDates(content, year)
    areas = [convertMsaCoordinates(findall(myConst.MSA_PATTERN_LATITUDE_LONGITUDE, content[start:end])) for start, end in zip(starts, ends)]
    return startDates, endDates, areas

################################################################################################
def getNsfMsaDates1(content, year) -> list:
    seaDates = finditer(myConst.MSA_PATTERN_DATE2_START, content)
    seaEnds = finditer(myConst.MSA_PATTERN_DATE2_END, content)
    seaDatesList = [(m.groups(), m.start(), m.end()) for m in seaDates]
    seaEndsList = [(m.groups(), m.start(), m.end()) for m in seaEnds]
    startDates, endDates, starts, ends = [], [], [], []
    for d, e in zip(seaDatesList, seaEndsList):
        # d = (('June', '2', '0200', 'June', '4', '1600'), 50203, 50236)
        day1 = d[0][1] if len(d[0][1]) == 2 else '0' + d[0][1]
        day2 = d[0][4] if len(d[0][4]) == 2 else '0' + d[0][4]
        startDates.append(convertMsaDate1(f'{year}{d[0][0]}{day1}{d[0][2]}'))
        endDates.append(convertMsaDate1(f'{year}{d[0][3]}{day2}{d[0][5]}'))
        starts.append(d[2])
        ends.append(e[1])
    return startDates, endDates, starts, ends

################################################################################################
def getNsfNotamDataMsa1(content, year) -> list:
    startDates, endDates, starts, ends = getNsfMsaDates1(content, year)
    areas = [myFile.formatLatitudeLongitude(getNsfAreaGroup(content[start:end])) for start, end in zip(starts, ends)]
    return startDates, endDates, areas

################################################################################################
def getNsfHydropacDates(content, year) -> list:
    hydropac = search(myConst.HYDROPAC_PATTERN, content)
    number, startDates, endDates, starts, ends = '', '', '', '', '',
    if hydropac:
        number = hydropac.group()
        seaDates = finditer(myConst.HYDROPAC_PATTERN_DATES, content)
        seaDatesList = [(m.groups(), m.start(), m.end()) for m in seaDates]
        startDates, endDates, starts, ends = [], [], [], []
        if seaDatesList:
            for i, d in enumerate(seaDatesList):
                # d = (('05', '0400', '', '05', '0800', 'AND'), 19895, 19054)
                m1 = d[0][5]
                if 'AND' in m1:
                    m1 = m1.replace('AND', seaDatesList[i + 1][0][5])
                month = d[0][2] if d[0][2] != '' else m1
                startDates.append(convertMsaDate(f'{year}{month}{d[0][0]}{d[0][1]}'))
                endDates.append(convertMsaDate(f'{year}{m1}{d[0][3]}{d[0][4]}'))
                starts.append(d[1])
                ends.append(seaDatesList[i + 1][1] if i + 1 < len(seaDatesList) else len(content))
        else:
            seaDates = finditer(myConst.HYDROPAC_PATTERN_DATES1, content)
            seaDatesList = [(m.groups(), m.start(), m.end()) for m in seaDates]
            for i, d in enumerate(seaDatesList):
                # d = (('01', 'FEB', '21', '0800', '0930'), 5696, 5723)
                startDates.append(convertMsaDate(f'{d[0][2]}{d[0][1]}{d[0][0]}{d[0][3]}'))
                endDates.append(convertMsaDate(f'{d[0][2]}{d[0][1]}{d[0][0]}{d[0][4]}'))
                starts.append(d[1])
                ends.append(seaDatesList[i + 1][1] if i + 1 < len(seaDatesList) else len(content))
    return number, startDates, endDates, starts, ends

################################################################################################
def getNsfNotamDataHydropac(content, year) -> list:
    number, startDates, endDates, starts, ends = getNsfHydropacDates(content, year)
    areas = []
    if number:
        for start, end in zip(starts, ends):
            areasMatch = findall(myConst.MSA_PATTERN_LATITUDE_LONGITUDE, content[start:end])
            areas.append(convertMsaCoordinates(areasMatch))
    return number, startDates, endDates, areas

################################################################################################
def getNsfNumbers(content) -> list:
    numbers = finditer(myConst.PATTERN_NOTAM_NUMBER, content)
    return [(m.group(1).replace(myConst.NOTAM_NUMBER_ERROR, f'A{myConst.NOTAM_NUMBER_ERROR}'), m.start(), m.end()) for m in numbers if m.group(1) != myConst.NOTAM_NUMBER_INVALID]

################################################################################################
def getNsfNotamData1(content) -> tuple:
    # startDate, endDate = getNsfDate(content)
    startDate, endDate, endIndex = getNsfDateIndex(content)
    area = myFile.formatLatitudeLongitude(getNsfAreaGroup(content[:endIndex]))
    location = getNsfLocation(content[:endIndex])
    if not location and area:
        location = getLocationIfInsideBoundary(area)
    return myDate.convertDate(startDate), myDate.convertDate(endDate), location, area

def getFirRegExPattern(fir:str):
    pattern = '(' + fir.replace(' ', '|') + ')'
    return pattern

################################################################################################
def getNsfLocation(content) -> str:
    firNames = myFile.readConfigFirNames()
    pattern = getFirRegExPattern(firNames)
    locations = finditer(pattern, content)
    if locations:
        loc = ''
        lastEnd = 0
        for m in locations:
            if lastEnd == 0 or m.start() - lastEnd < 10:
                if loc != '':
                    loc += '/'
                loc += m.group()
            lastEnd = m.end()
        return loc
    else:
        return ''

################################################################################################
def getNsfNotamData2(content) -> tuple:
    area = myFile.formatLatitudeLongitude(getNsfAreaGroup(content))
    location = getNsfLocation(content)
    if not location and area:
        location = getLocationIfInsideBoundary(area)
    return location, area

################################################################################################
def getNsfArea(contentSection) -> str:
    area = ''
    questionLatLons = findall(myConst.PATTERM_QUESTION, contentSection)
    latlons = findall(myConst.PATTERN_LATITUDE_LONGITUDE, contentSection)
    for latlon in latlons:
        if latlon in questionLatLons or latlon in area:
            continue
        if area != '':
            area += '|'
        area += latlon
    return area

################################################################################################
def getNsfNotamData3(content) -> tuple:
    area = myFile.formatLatitudeLongitude(getNsfArea(content))
    location = getNsfLocation(content)
    if not location and area:
        location = getLocationIfInsideBoundary(area)
    return location, area

################################################################################################
def getLocationIfInsideBoundary(areas) -> str:
    for area1 in areas.split('-'):
        for area in area1.split('|'):
            p = myFile.convertDMS2DD(area)
            for loc, boundary in myConst.FIR_BOUNDARY.items():
                boundary1 = [(lon, lat) for lat, lon in boundary]#swap longitute(y) and latitute(x)
                if pointIsInsidePolygon(p, boundary1):
                    return loc
    return ''

# Given three collinear points p, q, r,
# the function checks if point q lies on line segment 'pr'
################################################################################################
def pointOnSegment(p:tuple, q:tuple, r:tuple):
    if ((q[0] <= max(p[0], r[0])) & (q[0] >= min(p[0], r[0])) &
        (q[1] <= max(p[1], r[1])) & (q[1] >= min(p[1], r[1]))):
        return True
    return False

# A Python3 program to check if a given point lies inside a given polygon
# Refer
# https://www.geeksforgeeks.org/how-to-check-if-a-given-point-lies-inside-a-polygon/
# https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
# https://www.geeksforgeeks.org/orientation-3-ordered-points/amp/%C2%A0/
# for explanation of functions onSegment(), orientation() and doIntersect()
# Define Infinite (Using INT_MAX caused overflow problems)
# This code is contributed by Vikas Chitturi
INT_MAX = 10000

################################################################################################
# Returns true if the point p lies inside the polygon[] with n vertices
def pointIsInsidePolygon(p: tuple, points: list) -> bool:
    n = len(points)
    if n < 3:
        return False# There must be at least 3 vertices in polygon
    extreme = (INT_MAX, p[1])# Create a point for line segment from p to infinite
    decrease = 0# To count number of points in polygon whose y-coordinate is equal to y-coordinate of the point
    count = i = 0

    while True:
        nextPoint = (i + 1) % n
        if points[i][1] == p[1]:
            decrease += 1

        # Check if the line segment from 'p' to 'extreme' intersects with the line
        # segment from 'polygon[i]' to 'polygon[next]'
        if pointDoIntersect(points[i], points[nextPoint], p, extreme):
            # If the point 'p' is collinear with line segment 'i-next', then check if it lies
            # on segment. If it lies, return true, otherwise false
            if pointOrientation(points[i], p, points[nextPoint]) == 0:
                return pointOnSegment(points[i], p, points[nextPoint])
            count += 1
        i = nextPoint
        if i == 0:
            break

	# Reduce the count by decrease amount as these points would have been added twice
    count -= decrease
    return count % 2 == 1# Return true if count is odd, false otherwise

################################################################################################
# To find orientation of ordered triplet (p, q, r).
# The function returns following values
# 0 --> p, q and r are collinear
# 1 --> Clockwise
# 2 --> Counterclockwise
def pointOrientation(p:tuple, q:tuple, r:tuple):
    val = (((q[1] - p[1]) * (r[0] - q[0])) - ((q[0] - p[0]) * (r[1] - q[1])))
    if val == 0:
        return 0
    if val > 0:
        return 1 # Collinear
    else:
        return 2 # Clock or counterclock

################################################################################################
def pointDoIntersect(p1, q1, p2, q2):
    # Find the four orientations needed for general and special cases
    o1 = pointOrientation(p1, q1, p2)
    o2 = pointOrientation(p1, q1, q2)
    o3 = pointOrientation(p2, q2, p1)
    o4 = pointOrientation(p2, q2, q1)

    # General case
    if (o1 != o2) and (o3 != o4):
        return True

    # Special Cases
    if (o1 == 0) and (pointOnSegment(p1, p2, q1)):
        return True# p1, q1 and p2 are collinear and p2 lies on segment p1q1
    if (o2 == 0) and (pointOnSegment(p1, q2, q1)):
        return True# p1, q1 and p2 are collinear and q2 lies on segment p1q1
    if (o3 == 0) and (pointOnSegment(p2, p1, q2)):
        return True# p2, q2 and p1 are collinear and p1 lies on segment p2q2
    if (o4 == 0) and (pointOnSegment(p2, q1, q2)):
        return True# p2, q2 and q1 are collinear and q1 lies on segment p2q2
    return False

################################################################################################
def getNsfDate(content) -> tuple:
    startDate = search(myConst.PATTERN_START_DATE, content)

    if not startDate:
        startEndDate = search(myConst.PATTERN_START_END_DATE1, content)
        if not startEndDate:
            startEndDate = search(myConst.PATTERN_START_END_DATE2, content)
        startDate = startEndDate[1] if startEndDate else ''
        endDate = startEndDate[2] if startEndDate else ''
    else:
        endDate = search(myConst.PATTERN_END_DATE, content)
        startDate = startDate[1] if startDate else ''
        endDate = endDate[1] if endDate else ''
    return startDate, endDate

################################################################################################
def getNsfDateIndex(content) -> tuple:
    startDate1 = search(myConst.PATTERN_START_DATE, content)
    if not startDate1:
        startEndDate = search(myConst.PATTERN_START_END_DATE1, content)
        if not startEndDate:
            startEndDate = search(myConst.PATTERN_START_END_DATE2, content)
        startDate = startEndDate[1] if startEndDate else ''
        endDate = startEndDate[2] if startEndDate else ''
        endIndex = startEndDate.end() if startEndDate else len(content)
    else:
        endDate = search(myConst.PATTERN_END_DATE, content)
        startDate = startDate1[1] if startDate1 else ''
        endDate = endDate[1] if endDate else ''
        endIndex = len(content)
    return startDate, endDate, endIndex

################################################################################################
def getNsfAreaGroup(contentSection) -> str:
    area = ''
    lastEnd = 0
    questionLatLons = findall(myConst.PATTERM_QUESTION, contentSection)
    latlons = finditer(myConst.PATTERN_LATITUDE_LONGITUDE, contentSection)
    for m in latlons:
        latlon = m.group(1)
        if latlon in questionLatLons:
            continue
        if latlon not in area:
            if lastEnd == 0 or m.start() - lastEnd < 20:
                if area != '':
                    area += '|'
                area += latlon
            else:
                area += '-' + latlon
        lastEnd = m.end()
    return area

################################################################################################
def getNsfLocations(content) -> list:
    return findall(myConst.PATTERN_LOCATION_ONLY, content)

################################################################################################
def getNsfDatesGroup(content) -> tuple:
    startDates = search(myConst.PATTERN_START_DATE, content)
    if not startDates:
        startDates = search(myConst.PATTERN_START_DATE1, content)
        if not startDates:
            startDates = search(myConst.PATTERN_START_DATE2, content)
            if not startDates:
                startDates = []
                endDates = []
            else:
                startDates = finditer(myConst.PATTERN_START_DATE2, content)
                endDates = finditer(myConst.PATTERN_END_DATE2, content)
        else:
            startDates = finditer(myConst.PATTERN_START_DATE1, content)
            endDates = finditer(myConst.PATTERN_END_DATE1, content)
    else:
        startDates = finditer(myConst.PATTERN_START_DATE, content)
        endDates = finditer(myConst.PATTERN_END_DATE, content)

    return startDates, endDates

################################################################################################
def getNsfDates(content) -> tuple:
    startDates = findall(myConst.PATTERN_START_DATE, content)
    if not startDates:
        startDates = findall(myConst.PATTERN_START_DATE1, content)
        if not startDates:
            startDates = findall(myConst.PATTERN_START_DATE2, content)
            if not startDates:
                startDates = []
                endDates = []
            else:
                endDates = findall(myConst.PATTERN_END_DATE2, content)
        else:
            endDates = findall(myConst.PATTERN_END_DATE1, content)
    else:
        endDates = findall(myConst.PATTERN_END_DATE, content)

    return startDates, endDates

################################################################################################
def printNsfDict(d) -> None:
    for i, (title, url) in enumerate(d.items()):
        if isinstance(url, list):
            out = f'{i + 1:03} {title}:　\t{url[0]}'

            for j, (number, notam) in enumerate(url[1].items()):
                out += f'\n　{j + 1:02} {number}:{notam}'
            out += '\n'
        else:
            out = f'{i + 1:03} {title}:　\t{url}'

        print(out)

################################################################################################
def convertNsfDate(utcDateStr, tz) -> datetime:
    utcDateStr = utcDateStr.replace('Sept.', 'Sep')
    for fmt in myConst.NSF_DATE_FORMATS:
        try:
            utcDate = datetime.strptime(utcDateStr, fmt).replace(tzinfo=UTC)
            return utcDate.astimezone(timezone(tz))
        except ValueError:
            pass
    return None

################################################################################################
def showNsfNotam(content) -> None:
    numbers = findall(myConst.PATTERN_NOTAM_NUMBER, content)
    locs = getNsfLocations(content)
    startDates, endDates = getNsfDates(content)
    latlons = finditer(myConst.PATTERN_LATITUDE_LONGITUDE, content)
    out = f'{numbers}, {locs}, {startDates}, {endDates}, \n　'
    for m in latlons:
        out += f'{m.group()}({m.start()},{m.end()}), '
    out = out[:-2]
    print(out)

################################################################################################
def removeDuplicateNotams(notamDict) -> dict:
    temp = []
    res = dict()

    for key, val in notamDict.items():
        if val not in temp:
            temp.append(val)
            res[key] = val
        else:
            oldKey = list(res.keys())[list(res.values()).index(val)]
            if key < oldKey:
                res[key] = res.pop(oldKey)
    return res

################################################################################################
def getNsfPages(driver) -> int:
    myNet.elementLocatedBy(driver, By.CLASS_NAME, "pagesection")
    pagesection = driver.find_element(By.CLASS_NAME, "pagesection")
    pages = pagesection.find_elements(By.CLASS_NAME, "navPages")
    return int(pages[-2].text) if len(pages) > 0 and 'Next' == pages[-1].text else 1

################################################################################################
def getRocketName(title) -> str:
    m = search(myConst.NSF_ROCKET_PATTERN, title, IGNORECASE)
    return myConst.NSF_ROCKETS[m.group().lower()] if m else ''

################################################################################################
def getNsfCity(title) -> str:
    m = search(myConst.NSF_CITY_PATTERN, title, IGNORECASE)
    return myConst.NSF_CITIES[m.group().upper()] if m else '未知'

# ################################################################################################
# def drawNsfNotam(nsf_luanchList, titleForCheck) -> None:
#     for title, notams in nsf_luanchList.items():
#         if isinstance(notams, list) and (titleForCheck == '' or title == titleForCheck):
#             myFile.createNsfKmlFile(title, notams)

################################################################################################
def printTitlePages(title, lastPage, i) -> None:
    out = f'{i + 1:03} {title}　\tPage:'
    out1 = ''
    for p in range(1, lastPage + 1):
        if out1 != '':
            out1 += ','
        out1 += f'{p}'
    print(f'\n{out}{out1}')

# D°M'S": N45°46'52",   W108°30'14"
# D°M.M': N45°46.8666', W108°30.2333'
# D-M.M': N45-46.8666', W108-30.2333'
# D.D°  : N45.7811111°, W108.5038888°
# D°M'S" ⇒ D.D°:    D + (M/60) + (S/3600) = D.D°
# D°M'S" ⇒ D°M.M':  D + M + (S/60) = Decimal Minutes
# D°M.M' ⇒ D°M'S":  D + M + round(.M * 60)
# D.D° ⇒ D°M.M':    int(D) = D°, (D - Int(D)) * 60 = M.M'
# D.D° ⇒ D°M'S":    Int(D) = D°, Int((D - Int(D)) * 60) = M', (((D - Int(D)) * 60) - Int((D - Int(D)) * 60)) * 60 = S"

################################################################################################
def main():
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    sys.stdout.reconfigure(encoding='UTF-8')
    with myNet.getFirefoxDriver() as driver:
        try:
            print('Create all NSF launched urls from Chinese Launchers')
            print('https://forum.nasaspaceflight.com/index.php?board=40.0')
            page = 'url'
            nsfDict = getNsfUrlList(driver, page)
            writeNsfToFile(nsfDict)
        except:
            myExcept.printExceptionTrace()

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')

if __name__ == "__main__":
    showRunTime("main()")

