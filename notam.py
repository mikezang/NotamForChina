"""
    Thie is NOTAM module to parse luanch data from NOTAM site
    https://notams.aim.faa.gov/notamSearch/
"""
from time import sleep
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from timeit import timeit

from myModules import myUtils
from myModules import myExcept
from myModules import myShape
from myModules import myNet
import nsf

NEW_NOTAM_URL = "https://www.notams.faa.gov/dinsQueryWeb/"
XPATH_SPAN_DETAIL = "//span[@ng-bind-html='globalScope.selectedNOTAM.icaoMessage']"
NEW_CSS_SELECTOR_BUTTON_DISCLAIMER = ".ui-state-default.ui-corner-all"
NEW_XPATH_RADIO_TYPE = "//input[@name='reportType' and @value='Raw']"
NEW_XPATH_TEXTAREA = "//textarea[@name='retrieveLocId']"
NEW_XPATH_SEARCH_BUTTON = "//input[@name='submit' and @value='View NOTAMs']"

################################################################################################
# def getConditionDetail(driver, tdCondition) -> str:
#     tdCondition.click()
#     sleep(1)
#     condition = myNet.elementXPath(driver, 30, XPATH_SPAN_DETAIL).text
#     index = condition.index("E)")
#     if index:
#         condition = condition[(index + 3):] # exclude 'E) '
#     driver.back()
#     return condition

###############################################################################################
def printNotam(dictData, start):
    print(f"\nNOTAM发射预测{start}")
    print("================================")
    print(myUtils.getNotamDictString(dictData))
    print("================================")
    print(f"NOTAM发射预测{start}\n")

################################################################################################
def parseMsa(text):
    location = 'MSA'
    number = myUtils.getMsaLocation(text)
    text = text.replace('\n', '').replace(' ', '').replace('/', '').replace('、', ',')
    startDates, endDates = myUtils.getMsaDates(text)
    areas = myUtils.getMsaArea(text)
    return location, number, startDates, endDates, areas

################################################################################################
def parseNotam(text):
    location = myUtils.getNotamLocation(text)
    numbers = myUtils.getNotamNumbers(text)
    text = text.replace('\n', '').replace(' ', '')
    startDates, endDates = myUtils.getNotamDates(text)
    area = myUtils.getNotamArea(text)
    return location, numbers, startDates, endDates, area

################################################################################################
def getNotamDetail(driver, command, searchLocaltions):
    start = myUtils.getJapanTime()
    print(f"{start}")
    print(f"Searching {command}: {searchLocaltions}")
    notam = {}
    
    try:
        driver.get(NEW_NOTAM_URL)
        # myNet.checkVPN(driver)
        radio = ''

        sleep(1)
        button = myNet.findElementByCssSelector(driver, NEW_CSS_SELECTOR_BUTTON_DISCLAIMER)
        # button = driver.find_element(By.CSS_SELECTOR, NEW_CSS_SELECTOR_BUTTON_DISCLAIMER)
        if button:
            button.click()
            radio = myNet.elementXPath(driver, 30, NEW_XPATH_RADIO_TYPE)

            if radio:
                radio.click()
                myNet.elementInput(driver, 30, NEW_XPATH_TEXTAREA, searchLocaltions)
                myNet.elementClick(driver, 30, NEW_XPATH_SEARCH_BUTTON)
                sleep(5)

                window_after = driver.window_handles[-1]
                driver.switch_to.window(window_after)
                myNet.elementXPath(driver, 30, "//form[@name='NotamRetrievalForm']")
                form = driver.find_element(By.XPATH, "//form[@name='NotamRetrievalForm']")

                if form:
                    try:
                        myNet.waitForPageLoaded(driver, 60)
                    except:
                        pass

                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                    table1 = myNet.findElementByTag(form, "table")
                
                    if table1:
                        td1 = myNet.findElementByTag(table1, "td")

                        if td1:
                            tables = myNet.findElementsByTag(td1, "table")

                            for table2 in tables:
                                if myUtils.isChinaNotam(table2.text):
                                    tds = myNet.findElementsByTag(table2, "td")

                                    for td2 in tds:
                                        if myUtils.isChinaNotam(td2.text):
                                            location, number, startDate, endDate, area = parseNotam(td2.text)
                                            if location == 'RJJJ' and number.startswith('Q'):
                                                continue
                                            if area != '':
                                                startDate = nsf.convertDate(startDate)
                                                endDate = nsf.convertDate(endDate)
                                                area = nsf.formatLatitudeLongitude(area)
                                                notam = getNoatmDict(notam, number, startDate, endDate, location, area)
    except :
        myExcept.printExceptionTrace()
        pass
    return notam, start

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
def convertDate(oldDate):
    if oldDate == 'PERM':
        return oldDate
    elif 'EST' in oldDate:
        return datetime.strptime(oldDate, '%m/%d/%Y %H%MEST').strftime("%Y/%m/%d %H:%M")
    elif '年' in oldDate:
        if '-' in oldDate:
            dates = oldDate.split("-")
            date1 = datetime.strptime(dates[0], '%Y年%m月%d日')
            date2 = datetime.strptime(dates[1], '%Y年%m月%d日')
            diff = date2 - date1
            date3 = date1 + timedelta(diff.days / 2)
            return date3.strftime("%Y/%m/%d")
        else:
            return datetime.strptime(oldDate, '%Y年%m月%d日')
    else:
        return datetime.strptime(oldDate, '%m/%d/%Y %H%M').strftime("%Y/%m/%d %H:%M")
    
def main():
    driver = myNet.getFirefoxDriver()
    command = 'Location'
    try:
        firLocations = myUtils.readConfigFirNames()
        notam_data, start = getNotamDetail(driver, command, firLocations)

        if notam_data:
            notam_data =  myUtils.sortDictByValue(notam_data)
            printNotam(notam_data, start)
            myShape.createKmlFile(notam_data)
    except:
        myExcept.printExceptionTrace()

    if driver:
        driver.quit()

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'Finished in {timedelta(seconds=result)}\n')

################################################################################################
if __name__ == "__main__":
    showRunTime("main()")