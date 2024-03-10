"""
    Thie is TRIP module to parse luanch data from two TRIP site
    https://m.ctrip.com/webapp/vacations/shop/home?productid=31375689&brandId=77691&detailId=31375689&proId=1292581&saleMode=R
    https://mp.sohu.com/profile?xpt=ZW5pdXBsYW5ldEBzaW5hLmNvbQ==
"""
# pylint: disable=W0703,C0103,C0116,C0301

# import os
from time import sleep
from re import findall
from datetime import date, datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

import myUtils
import constants

################################################################################################
def calcYear(this_year, month_int, this_month):
    if month_int < this_month:
        return this_year + 1
    else:
        return this_year

################################################################################################
def getDayDiff(title_text):
    day_diff1 = 0
    for key, value in constants.DAYS_DIFF.items():
        if key in title_text:
            day_diff1 = value
            break
    return day_diff1

################################################################################################
def getCity(title_text):
    city = ""
    for key, value in constants.CITIES.items():
        if key in title_text:
            city = value.split('|', maxsplit=1)[0]
            break
    return city

################################################################################################
def getTitle(titles):
    # title_text = ""
    # for title in titles:
    #     try:
    #         title_text = title.get_attribute('innerHTML')
    #     except Exception as e:
    #         # print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
    #         continue
    return titles.text

################################################################################################
def getCTrip(driver):
    launch_date = {}
    urls, titles, locations = getCTripList(driver)

    if urls and titles:
        urls, titles, locations = zip(*sorted(zip(urls, titles, locations), key=lambda x: x[2] + x[1]))
        createHtmlpage(urls, titles, locations)
        launch_date = getCTripDetail(driver, urls, titles)
    return launch_date

################################################################################################
def getCTripList(driver):
    urls, titles, locations = [], [], []

    try:
        driver.get(constants.CTRIP_URL)
        print(f'Searching', end=' ', flush=True)
        tripCity = myUtils.readConfig(['TripCity'])

        for i, city in enumerate(tripCity):
            if i < len(tripCity) - 1:
                print(f'{city}', end=',', flush=True)
            else:
                print(f'{city}\n')

            # click "change city" button
            myUtils.elementClick(driver, 30, "//div[@class='suppliers_search_destination_starting']")
            myUtils.elementInput(driver, 30, "//input[@class='search_text']", city)
            myUtils.elementClick(driver, 30, "//input[@class='search_text']")
            sleep(2)
        
            # select input first city
            liList = driver.find_elements(By.CLASS_NAME, "search_cn")
            liList[0].click()
            sleep(2)

            # show list page again
            myUtils.elementId(driver, 30, "grp-10650014575-list-tab-产品").click()
            sleep(2)

            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            sleep(2)

            div1 = driver.find_elements(By.CLASS_NAME, "shop_list_item")
            div2 = driver.find_elements(By.CLASS_NAME, 'shop_tour_content')

            for pid, link in zip(div1, div2):
                title = link.find_element(By.TAG_NAME, 'h3').text
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
    except:
        myUtils.pritnExceptionTrace()
        pass

    return urls, titles, locations

################################################################################################
def getCTripDetail(driver, urls, titles):
    today = date.today()
    this_year = today.year
    this_month = today.month
    launch_date = {}

    for j, (url, title_text) in enumerate(zip(urls, titles)):
        try:
            this_city = ""
            day_diff = 0
            real_url = constants.BASE_CTRIP_URL + url
            print(f'Title{j + 1:02}: {title_text}')
            print(f' Link{j + 1:02}: {real_url}', end='', flush=True)

            myUtils.setTimeout(driver, 20)
            try:
                driver.get(real_url)
                print('\n')
                sleep(2)
            except:
                print(' (Timeout)\n')
                pass

            launch_temp = {}
            if title_text != "":
                this_city = getCity(title_text)
                if this_city == '':
                    break

                day_diff = getDayDiff(title_text)
                last_day = 0

                html = driver.page_source
                matches = findall(r'星期.*?(\d{2}-\d{2})', html)
                for match in matches:
                    month_int, day_int = map(int, match.split("-"))
                    day_int += day_diff

                    if last_day + 1 != day_int:
                        last_day = day_int

                        if day_int > 31:
                            day_int -= 31
                            month_int += 1
                        month_text = f'{month_int:02}'
                        day_text = f'{day_int:02}'
                        this_year1 = calcYear(this_year, month_int, this_month)
                        this_date = str(this_year1) + "/" + month_text + "/" + day_text
                        launch_temp[this_date] = this_city
                    else:
                        launch_temp = {}
                        break
                launch_date = myUtils.combineValuesForSameDictKey(launch_date, launch_temp)
        except:
            myUtils.pritnExceptionTrace()
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
        driver.get(constants.ENIUTRIP_URL)
        myUtils.checkVPN(driver)

        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "tpl-text-feed-item-content")))
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        links = driver.find_elements(By.CLASS_NAME, "tpl-text-feed-item-content")

        for i, link in enumerate(links):
            title = link.find_element(By.CLASS_NAME, "item-text-content-title")

            if '火箭观礼' in title.text:
                url = links[i].get_attribute("href")
                url = myUtils.removeAllSpaces(url).split("?", maxsplit=1)[0]

                if not title.text in urls:
                    urls[title.text] = url

    except NoSuchElementException:
        print("No ENiuTrip Data!")
    except:
        myUtils.pritnExceptionTrace()
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
        myUtils.pritnExceptionTrace()
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
    filename = './temp/LaunchTravels.html'

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f'<a target=_blank href={mainUrl}><h1>CTRIP火箭发射观礼旅行</H1></a><br>\n\n')

        for i, (url, title, location) in enumerate(zip(urls, titles, locations)):
            city = writeTitle(f, title, location, city)
            f.write(f'{i + 1:02}: <a target=_blank href={baseUrl}{url}>{title}</a><br>\n')
