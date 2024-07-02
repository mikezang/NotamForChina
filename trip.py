"""
    Thie is TRIP module to parse luanch data from two TRIP site
    https://m.ctrip.com/webapp/vacations/shop/home?productid=31375689&brandId=77691&detailId=31375689&proId=1292581&saleMode=R
    https://mp.sohu.com/profile?xpt=ZW5pdXBsYW5ldEBzaW5hLmNvbQ==
"""
# pylint: disable=W0703,C0103,C0116,C0301

from time import sleep
from re import findall, finditer
from datetime import date, datetime, timedelta
from timeit import timeit

from myModules import myExcel
from myModules import myUtils
from myModules import myExcept
from myModules import myNet

BASE_CTRIP_URL = "https://m.ctrip.com/webapp/vacations/tour/detail?productid="
CTRIP_URL = "https://m.ctrip.com/webapp/vacations/shop/home?productid=31375689&brandId=77691&detailId=31375689&proId=1292581&saleMode=R"
ENIUTRIP_URL = "https://mp.sohu.com/profile?xpt=ZW5pdXBsYW5ldEBzaW5hLmNvbQ==&_f=index_pagemp_1&spm=smpc.content-abroad.author.1.1659536786116JJXcGX9"

DAYS_DIFF = {
    '房车·中国海南文昌3日2晚跟团游' : 2,
    '酒泉4天3晚' : 2,
    # '酒泉3天2晚' : 2,
    "酒泉2日" : 1,
    # "西昌2日" : 0,
    # "文昌3日" : 2,
    # "半日" : 0,
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
def getDayDiff(title_text):
    day_diff1 = 0
    for key, value in DAYS_DIFF.items():
        if key in title_text:
            day_diff1 = value
            break
    return day_diff1

################################################################################################
def getCity(title_text):
    city = ""
    for key, value in myExcel.CITIES.items():
        if key in title_text:
            city = value.split('|', maxsplit=1)[0]
            break
    return city

################################################################################################
def getTitle(titles):
    return titles.text

################################################################################################
def getCTrip(driver):
    launch_date = {}
    urls, titles, locations = getCTripList(driver)

    if urls and titles:
        urls, titles, locations = zip(*sorted(zip(urls, titles, locations), key=lambda x: x[2] + x[1]))
        launch_date = getCTripDetail(driver, urls, titles)
        printTrip(launch_date)
        createHtmlpage(urls, titles, locations)

################################################################################################
def selectCity(driver, city):
    myNet.elementClick(driver, 30, "//div[@class='suppliers_search_destination_starting']")
    myNet.elementInput(driver, 30, "//input[@class='search_text']", city)
    myNet.elementClick(driver, 30, "//input[@class='search_text']")
    sleep(2)

    # select input first city
    myNet.elementClass(driver, 10, "search_cn")
    liList = myNet.findElementsByClass(driver, "search_cn")
    liList[0].click()

################################################################################################
def getCTripList(driver):
    urls, titles, locations = [], [], []
    print(f'Searching...', end='', flush=True)

    for i in range(0, 10):
        try:
            driver.get(CTRIP_URL)
            tripCity = myUtils.readConfig(['TripCity'])

            for city in tripCity:
                # click "change city" button
                # selectCity(driver, city)
                sleep(2)

                # show list page
                myNet.elementId(driver, 30, "grp-10650014575-list-tab-产品").click()
                sleep(2)

                myNet.scrollBottom(driver)
                sleep(2)

                div1 = myNet.findElementsByClass(driver, "shop_list_item")
                div2 = myNet.findElementsByClass(driver, 'shop_tour_content')
                urls, titles, locations = parseUrls(div1, div2)
            print('\n')
            break
        except:
            if i == 9:
                myExcept.printExceptionTrace()
            else:
                print('...', end='', flush=True)
                sleep(3)
            pass
    return urls, titles, locations

def parseUrls(div1, div2):
    urls, titles, locations = [], [], []
    for pid, link in zip(div1, div2):
        title = myNet.findElementByTag(link, 'h3').text

        if '观礼' in title:
            url = pid.get_attribute("data-pid")
            if url not in urls:
                titles.append(title)
                urls.append(url)

                if '文昌' in title:
                    locations.append('文昌')
                elif '西昌' in title:
                    locations.append('西昌')
                elif '酒泉' in title or '东方航天城' in title:
                    locations.append('酒泉')
    return urls, titles, locations

################################################################################################
def parseTripDate(driver, this_city, day_diff):
    launchData = {}
    html = driver.page_source
    thisYear = myUtils.getThisYear()
    nextYear = int(thisYear) + 1
    pattern = rf'(?<!=)(({thisYear}|{nextYear})\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01]))'
    matches = findall(pattern, html)
    # matches = finditer(pattern, html)
    for match in matches:
        launchDay = myUtils.getDateAfterDays(match[0], day_diff)
        launchData[launchDay.replace('-', '/')] = this_city
    return launchData

################################################################################################
def parseTripDateOld(driver, this_city, day_diff):
    today = date.today()
    launch_temp = {}
    last_day = 0
    html = driver.page_source
    pattern = rf'(?<!=){myUtils.getThisYear()}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])'
    matches = findall(pattern, html)
    for match in matches:
        month_int, day_int = int(match[0].replace(',', '')), int(match[1])
        day_int += day_diff

        if last_day + 1 != day_int:
            last_day = day_int
            if day_int > 31:
                day_int -= 31
                month_int += 1

            m1 = (today.month == month_int) & (day_int > today.day)
            m2 = (today.month + 1 == month_int) | (today.month + 2 == month_int) | (today.month + 3 == month_int)
            m3 = today.month == 12 & (month_int == 1 | month_int == 2 | month_int == 3)
            if m1 or m2 or m3:
                month_text = f'{month_int:02}'
                day_text = f'{day_int:02}'
                this_year1 = calcYear(today.year, month_int, today.month)
                this_date = str(this_year1) + "/" + month_text + "/" + day_text
                launch_temp[this_date] = this_city
        else:
            launch_temp = {}
            break
    return launch_temp

################################################################################################
def getCTripDetail(driver, urls, titles):
    launch_date = {}

    for j, (url, title_text) in enumerate(zip(urls, titles)):
        try:
            this_city = ""
            day_diff = 0
            real_url = BASE_CTRIP_URL + url
            print(f'Title{j + 1:02}: {title_text}')
            print(f' Link{j + 1:02}: {real_url}', end='', flush=True)

            myNet.setTimeout(driver, 20)
            try:
                driver.get(real_url)
                print('\n')
                sleep(3)
            except:
                print(' (Timeout)\n')
                pass

            if title_text != "":
                this_city = getCity(title_text)
                if this_city == '':
                    break

                day_diff = getDayDiff(title_text)
                launch_temp = parseTripDate(driver, this_city, day_diff)
                launch_date = myUtils.combineValuesForSameDictKey(launch_date, launch_temp)
        except:
            myExcept.printExceptionTrace()
            pass
    return launch_date

################################################################################################
def getENiuTrip(driver):
    launch_date = {}
    urls = getENiuTripList(driver)
    launch_date = getENiuTripDetail(driver, urls)
    return launch_date

################################################################################################
def getENiuTripList(driver):
    urls = {}

    try:
        driver.get(ENIUTRIP_URL)
        myNet.checkVPN(driver)

        myNet.elementClass(driver, 30, "tpl-text-feed-item-content")
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        links = myNet.findElementsByClass(driver, "tpl-text-feed-item-content")

        for i, link in enumerate(links):
            title = myNet.findElementByClass(link, "item-text-content-title")

            if '火箭观礼' in title.text:
                url = links[i].get_attribute("href")
                url = myUtils.removeAllSpaces(url).split("?", maxsplit=1)[0]

                if not title.text in urls:
                    urls[title.text] = url
    except:
        myExcept.printExceptionTrace()
        pass
    return urls

################################################################################################
def getENiuTripDetail(driver, urls):
    launch_date = {}

    try:
        for j, (title, url) in enumerate(urls.items()):
            print(f' Link{j + 1:02}: {url}')
            print(f'Title{j + 1:02}: {title}\n')

            city = getCity(title)
            driver.get(url)
            items = findall(r'\d{4}年\d{1,2}月\d{1,2}日-\d{4}年\d{1,2}月\d{1,2}日', driver.page_source)

            for item in items:
                launch_date[convertDate1(item)] = city
    except:
        myExcept.printExceptionTrace()
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
def printTrip(d) -> None:
    print(f"\n携程旅行发射预测{myUtils.getJapanTime()}")
    print("===================================")
    launch_date = myUtils.sortDictByKey(d)
    myUtils.printDict(launch_date)

################################################################################################
def writeTitle(f, title, location, city):
    if city == '' or city not in title:
        city = location
        f.write(f'<h2>{city}</h2>\n')
    return city

################################################################################################
def sortListByTitle(urls, titles):
    pairs = list(zip(urls, titles))
    pairs.sort(key=lambda p: (p[1]))
    urls[:], titles[:] = zip(*pairs)
    # urls, titles = for url, title in sorted(zip(urls, titles), key=lambda pair: pair[0])]
    return urls, titles

################################################################################################
def createHtmlpage(urls, titles, locations) -> None:
    mainUrl = "https://m.ctrip.com/webapp/vacations/shop/home?productid=31375689&brandId=77691&detailId=31375689&proId=1292581&saleMode=R"
    baseUrl = "https://m.ctrip.com/webapp/vacations/tour/detail?productid="
    city = ''
    filename = 'data/LaunchTravels.html'

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f'<a target=_blank href={mainUrl}><h1>CTRIP火箭发射观礼旅行</H1></a><br>\n\n')

        for i, (url, title, location) in enumerate(zip(urls, titles, locations)):
            city = writeTitle(f, title, location, city)
            f.write(f'{i + 1:02}: <a target=_blank href={baseUrl}{url}>{title}</a><br>\n')

        print(f'Saved to {filename}!')

def main():
    try:
        driver = myNet.getFirefoxDriver(disableImage=False)
        getCTrip(driver)
    except:
        myExcept.printExceptionTrace()
    if driver:
        driver.quit()

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')

################################################################################################
if __name__ == "__main__":
    showRunTime("main()")
    exit