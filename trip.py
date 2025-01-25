"""
    Thie is TRIP module to parse luanch data from two TRIP site
    https://m.ctrip.com/webapp/vacations/shop/home?productid=31375689&brandId=77691&detailId=31375689&proId=1292581&saleMode=R
    https://mp.sohu.com/profile?xpt=ZW5pdXBsYW5ldEBzaW5hLmNvbQ==
"""
from time import sleep
from re import findall, finditer, match
from datetime import datetime, timedelta
from timeit import timeit
from selenium.webdriver.common.by import By

from myModules import myExcept
from myModules import myNet
from myModules import myDate
from myModules import myDict

BASE_CTRIP_URL = "https://m.ctrip.com/webapp/vacations/tour/detail?productid="
CTRIP_URL = "https://m.ctrip.com/webapp/vacations/shop/home?productid=31375689&brandId=77691&detailId=31375689&proId=1292581&saleMode=R"
ENIUTRIP_URL = "https://mp.sohu.com/profile?xpt=ZW5pdXBsYW5ldEBzaW5hLmNvbQ==&_f=index_pagemp_1&spm=smpc.content-abroad.author.1.1659536786116JJXcGX9"

HUAHUO_TRIP_URL = "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzkxNDc0MzY1MQ==&action=getalbum&album_id=3621026985251602442"
BUTTON_XPATH = "//div[@class='album-sort__wrp js_album_sort']"
LI1_XPATH = "//li[@class='album__list-item js_album_item js_wx_tap_highlight wx_tap_cell']"
SPAN_XPATH = "//span[@class='js_article_create_time album__item-info-item']"

TEMP_FILE_PATH = './temp/'

DAYS_DIFF = {
    "早鸟优惠仅3天": 0,
    "2天" : 1,
    "3天" : 1,
    "3日" : 1,
    "5日" : 2,
    "5天" : 2,
    "4日" : 3,
    "4天" : 1,
}

################################################################################################
def calcYear(this_year, month_int, this_month):
    if month_int < this_month:
        return this_year + 1
    else:
        return this_year

################################################################################################
def getDayDiff(thisText):
    day_diff1 = 0
    for key, value in DAYS_DIFF.items():
        if key in thisText:
            day_diff1 = value
            break
    return day_diff1

################################################################################################
# def getCity(thisText):
#     city = ""
#     for key, value in myExcel.CITIES.items():
#         if key in thisText:
#             city = value.split('|', maxsplit=1)[0]
#             break
#     return city

################################################################################################
def getTitle(titles):
    return titles.text

################################################################################################
def getCTrip(driver):
    launch_date = {}
    cTripDict = getCTripList(driver)

    if cTripDict:
        createHtmlpage('捷程旅行', CTRIP_URL, cTripDict, BASE_CTRIP_URL)
        launch_date = getCTripDetail(driver, cTripDict)
    return launch_date

def order(element, titles):
    _, title, location = element
    maxDate = max([title[:10] for title in titles if location in title])
    return maxDate + location + title

################################################################################################
def getHuahuo(driver):
    launch_date = {}
    huahuoDict = getHuahuoList(driver)
    
    if huahuoDict:
        createHtmlpage('花火亲子旅行', HUAHUO_TRIP_URL, huahuoDict)
        launch_date = getHuahuoDetail(driver, huahuoDict)
    return launch_date

################################################################################################
def selectCity(driver, city):
    myNet.elementClick(driver, "//div[@class='suppliers_search_destination_starting']")
    myNet.elementInput(driver, "//input[@class='search_text']", city)
    myNet.elementClick(driver, "//input[@class='search_text']")
    sleep(2)

    # select input first city
    myNet.elementLocatedBy(driver, By.CLASS_NAME, "search_cn")
    liList = driver.find_elements(By.CLASS_NAME, "search_cn")
    liList[0].click()

################################################################################################
def getCTripList(driver):
    print(f'Searching 捷程旅行...', end='', flush=True)
    CTripDict = {}
    for i in range(5):
        try:
            driver.get(CTRIP_URL)
            myNet.elementLocatedBy(driver, By.ID, "grp-10650014575-list-tab-产品").click()
            noMore = '//div[@class="no_more"]'
            myNet.waitForVisible(driver, noMore)
            myNet.elementLocatedBy(driver, By.CLASS_NAME, "shop_list_item")
            myNet.elementLocatedBy(driver, By.CLASS_NAME, 'shop_tour_content')
            div1 = driver.find_elements(By.CLASS_NAME, "shop_list_item")
            div2 = driver.find_elements(By.CLASS_NAME, "shop_tour_content")
            CTripDict = parseCTripUrls(div1, div2)
            print('\n')
            break
        except:
            if i == 4:
                myExcept.printExceptionTrace()
            else:
                print('...', end='', flush=True)
                sleep(3)
            pass
    return CTripDict

################################################################################################
def getHuahuoList(driver):
    huahuoDict = {}
    print(f'Searching 花火亲子旅行...', end='', flush=True)

    for i in range(2):
        try:
            driver.get(HUAHUO_TRIP_URL)
            myNet.elementLocatedBy(driver, By.XPATH, BUTTON_XPATH).click()
            noMore = '//div[@class="over-line js_no_more_album"]'
            myNet.waitForVisible(driver, noMore)
            li = driver.find_elements(By.XPATH, LI1_XPATH)
            span = driver.find_elements(By.XPATH, SPAN_XPATH)
            huahuoDict = parseHuahuoUrls(li, span)
            print('\n')
            break
        except:
            if i == 1:
                myExcept.printExceptionTrace()
            else:
                print('...', end='', flush=True)
                sleep(3)
            pass
    return huahuoDict

################################################################################################
def getLaunchCity(title):
    if '文昌' in title or '海南' in title:
        return '文昌'
    elif '西昌' in title or '四川' in title:
        return '西昌'
    elif '酒泉' in title or '东方航天城' in title:
        return '酒泉'
    elif '海阳' in title:
        return '海阳'
    elif '太原' in title:
        return '太原'
    return ''

################################################################################################
def parseCTripUrls(div1, div2):
    cTripDict = {}
    for pid, link in zip(div1, div2):
        title = link.find_element(By.TAG_NAME, 'h3').text
        if '观礼' in title:
            url = pid.get_attribute("data-pid")
            city = getLaunchCity(title)
            if city not in cTripDict:
                cTripDict[city] = []
            cTripDict[city].append((title, url))
    return cTripDict

################################################################################################
def convertToDate(dateStr):
    today = datetime.today()
    if dateStr == '昨天':
        today -= timedelta(days=1) 
    elif dateStr == '前天':
        today -= timedelta(days=2) 
    elif dateStr == '1周前':
        today -= timedelta(days=8)
    else:
        m = match(r'(\d+)天前', dateStr)
        if m:
            today -= timedelta(days=int(m.group(1))+1)
        else:
            m = match(r'(\d{4})/(\d{2})/(\d{2})', dateStr)
            if m:
                today = datetime(int(m.group(1)), int(m.group(2)), int(m.group(2)))
    return today.strftime('%Y-%m-%d')

################################################################################################
def parseHuahuoUrls(li, span):
    huahuoDict = {}
    for li, span in zip(li, span):
        title = li.get_attribute('data-title')

        if '观礼' in title or '发射' in title or '航天' in title:
            url = li.get_attribute('data-link')
            dateStr = convertToDate(span.text)
            city = getLaunchCity(title)
            if city not in huahuoDict:
                huahuoDict[city] = []
            huahuoDict[city].append((f'{dateStr}-{title}', url))
    return huahuoDict

################################################################################################
def getDateAfterDays(startDate, days: int):
    if isinstance(startDate, str):
        startDate1 = datetime.strptime(startDate, "%Y/%m/%d")
        endDate = startDate1 + timedelta(days=days)
        endDate = endDate.strftime('%Y/%m/%d')
    else:
        endDate = startDate + timedelta(days=days)
    return endDate

################################################################################################
def parseCTripDate(driver, thisCity, day_diff):
    launchData = {}
    html = driver.page_source
    thisYear = myDate.getThisYear()
    nextYear = int(thisYear) + 1
    pattern = rf'(?<!=)(({thisYear}|{nextYear})\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01]))'
    matches = findall(pattern, html)
    today = myDate.getJapanDate("%Y-%m-%d")
    for m in matches:
        if m[0] > today:
            launchDay = getDateAfterDays(m[0].replace('-', '/'), day_diff)
            launchData[launchDay] = thisCity
    return launchData

################################################################################################
def parseHuahuoDateOld(driver, thisCity, day_diff):
    launchData = {}
    pattern = r'(?<!=)((\d{2,4})?[年\-])?(0[1-9]|1[012])[月\-](0[1-9]|[12][0-9]|3[01])日(?!\s*\d{1,2}:\d{2})'
    pageSource = driver.page_source
    matches = findall(pattern, pageSource)
    today = myDate.getJapanDate("%Y/%m/%d")

    for i, m1 in enumerate(matches):
        year1 = int(m1[1]) if m1[1] != '' else 2025
        month1, day1 = m1[2], m1[3]
        mDate = f'{year1}/{month1}/{day1}'
        date1 = datetime(year1, int(month1), int(day1)) + timedelta(days=1)
        if mDate > today:
            launchDay = getDateAfterDays(mDate, day_diff)
            m2 = launchDay.split('/')
            year2, month2, day2 = int(m2[0]), int(m2[1]), int(m2[2])
            date2 = datetime(year2, month2, day2) + timedelta(days=1)
            launchData[launchDay] = thisCity
            if i < len(matches) - 1:
                m3 = matches[i + 1]
                year3 = int(m3[1]) if m3[1] != '' else 2024
                month3, day3 = int(m3[2]), int(m3[3])
                date3 = datetime(year3, month3, day3)
                if date1 == date3 or date2 == date3:
                    break
    return launchData

################################################################################################
def parseHuahuoDate(driver, thisCity, day_diff):
    launchData = {}
    pattern = r'\b(?:(?P<year1>\d{4})年)?(?P<month1>\d{1,2})月(?P<day1>\d{1,2})日'
    pattern += r'(?:(?:-|--|,|—|、)'
    pattern += r'(?:(?P<year2>\d{4})年)?(?:(?P<month2>\d{1,2})月)?(?:(?P<day2>\d{1,2})日)?\b'
    pattern += r'(?!\s*\d{1,2}:\d{2}))?'
    pageSource = driver.page_source
    matches = finditer(pattern, pageSource)
    today = myDate.getJapanDate("%Y/%m/%d")

    for m in matches:
        groupDict = m.groupdict()
        year1 = groupDict.get('year1')
        year1 = int(year1) if year1 else 2025
        month1, day1 = groupDict.get('month1'), groupDict.get('day1')
        mDate = f'{year1}/{int(month1):02}/{int(day1):02}'
        if mDate > today:
            if day_diff > 0:
                launchDay = getDateAfterDays(mDate, day_diff)
                launchData[launchDay] = thisCity
            else:
                date1 = datetime(year1, int(month1), int(day1))
                month2 = groupDict.get('month2')
                day2 = groupDict.get('day2')
                if month2 and day2:
                    year2 = groupDict.get('year2')
                    year2 = 2025 if month2 < today[5:7] else year2
                    year2 = int(year2) if year2 else 2025
                    date2 = datetime(year2, int(month2), int(day2))
                    day_diff = (date2 - date1).days // 2
                    launchDay = getDateAfterDays(mDate, day_diff)
                    launchData[launchDay] = thisCity
                else:
                    launchDay = getDateAfterDays(mDate, day_diff)
                    launchData[launchDay] = thisCity
    return launchData

################################################################################################
def getCTripDetail(driver, cTripDict):
    launch_date = {}
    no = 1
    for city, cTripList in cTripDict.items():
        for title, url in cTripList:
            real_url = BASE_CTRIP_URL + url
            print(f'Title{no:02}: {title}')
            print(f' Link{no:02}: {real_url}', end='', flush=True)
            no += 1
            myNet.setTimeout(driver, 20)
            try:
                driver.get(real_url)
                print('\n')
                sleep(3)
            except:
                print(' (Timeout)\n')
                pass

            if title != "":
                day_diff = getDayDiff(title)
                launch_temp = parseCTripDate(driver, city, day_diff)
                launch_date = combineValuesForSameDictKey(launch_date, launch_temp)
    launch_date = {k: v + '(捷程)' for k, v in launch_date.items()}
    return launch_date

################################################################################################
def getHuahuoData(driver, launch_date, thisText, url, thisCity, i):
    print(f'Title{i + 1:02}: {thisText}')
    print(f' Link{i + 1:02}: {url}\n')
    day_diff = getDayDiff(thisText)
    launch_temp = parseHuahuoDate(driver, thisCity, day_diff)
    launch_date = combineValuesForSameDictKey(launch_date, launch_temp)
    return launch_date

################################################################################################
def getHuahuoDetail(driver, huahuoDict):
    launch_date = {}
    for i, (city, huahuoList) in enumerate(huahuoDict.items()):
        for title, url in huahuoList:
            myNet.setTimeout(driver, 60)
            driver.get(url)
            sleep(5)
            launch_date = getHuahuoData(driver, launch_date, title, url, city, i)
            break
    launch_date = {k: v + '(花火)' for k, v in launch_date.items()}
    return launch_date

################################################################################################
def convertDate1(oldDate) -> str:
    dList = oldDate.split('-')
    d1 = datetime.strptime(dList[0], '%Y年%m月%d日')
    d2 = datetime.strptime(dList[1], '%Y年%m月%d日')
    days = (d2 - d1) // 2
    d = d1 + timedelta(days=days.days)
    return d.strftime("%Y/%m/%d")

################################################################################################
def printTrip(d, title='各旅行社', reverse=False) -> None:
    title = f"{title}发射预测{myDate.getJapanTime()}"
    print(f'\n{title}')
    print("=" * myDate.lenFullWidth(title), end="\n")
    launch_date = myDict.sortDictByKey(d, reverse=reverse)
    myDict.printDict(launch_date)

################################################################################################
def writeTitle(f, title, location, city):
    if city == '' or city not in title:
        city = location
        f.write(f'<h2>{city}</h2>\n')
    return city

################################################################################################
def createHtmlpage(htmlFile, mainUrl, huahuoDict=None, baseUrl='') -> None:
    filename = f'{TEMP_FILE_PATH}{htmlFile}.html'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f'<a target=_blank href={mainUrl}><h1>{htmlFile}火箭发射观礼</H1></a>\n')
        lastCity = ''
        no = 1
        for city, huahuoList in huahuoDict.items():
            for title, url in huahuoList:
                if lastCity != city:
                    f.write(f'<h2>{city}</h2>\n')
                lastCity = city
                f.write(f'　{no:02}: <a target=_blank href={baseUrl}{url}>{title}</a><br>\n')
                no += 1
        f.write('<BR>')
        print(f'Saved to {filename}!\n')

################################################################################################
def combineValuesForSameDictKey(d1: dict, d2: dict) -> dict:
    return {k: (d1[k] + '/' + d2[k]
                if k in d1 and k in d2 and d1[k] not in d2[k] and d2[k] not in d1[k]
                else d1[k] if k in d1 else d2[k])
            for k in set(d1).union(d2)}

################################################################################################
def main():
    with myNet.getFirefoxDriver(disableImage=True) as driver:
        try:
            date2 = getCTrip(driver)
            date1 = getHuahuo(driver)
            launch_date = combineValuesForSameDictKey(date1, date2)
            printTrip(launch_date)
        except:
            myExcept.printExceptionTrace()

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')

################################################################################################
if __name__ == "__main__":
    showRunTime("main()")
    # myStats.showStats(main)