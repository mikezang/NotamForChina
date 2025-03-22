"""
    Thie is NOTAM module to parse luanch data from NOTAM site
    https://notams.aim.faa.gov/notamSearch/
"""
from datetime import datetime, timedelta
import locale
import sys
from time import sleep
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from timeit import timeit

from myModules import myExcept
from myModules import myShape
from myModules import myNet
from myModules import myFile
from myModules import myDate
from myModules import myDict
from myModules import myNOTAM

NEW_NOTAM_URL = "https://www.notams.faa.gov/dinsQueryWeb/"
XPATH_SPAN_DETAIL = "//span[@ng-bind-html='globalScope.selectedNOTAM.icaoMessage']"
NEW_CSS_SELECTOR_BUTTON_DISCLAIMER = ".ui-state-default.ui-corner-all"
NEW_XPATH_RADIO_TYPE = "//input[@name='reportType' and @value='Raw']"
NEW_XPATH_TEXTAREA = "//textarea[@name='retrieveLocId']"
NEW_XPATH_SEARCH_BUTTON = "//input[@name='submit' and @value='View NOTAMs']"
NEW_FORM_XPATH = "//form[@name='NotamRetrievalForm']"
SCROLL_WINDOW = "window.scrollTo(0, document.body.scrollHeight)"

################################################################################################
def getNotamDetail(driver):
    firLocations = myFile.readConfigFirNames()
    start = myDate.getJapanTime()
    print(f"{start}")
    print(f"Searching Location: {firLocations}")
    print('Searching...', end='')
    notam = {}
    i = 0
    button = None
    while True:
        try:
            driver.get(NEW_NOTAM_URL)
            windowHandles = driver.window_handles
            button = driver.find_element(By.CSS_SELECTOR, NEW_CSS_SELECTOR_BUTTON_DISCLAIMER)
            print()
            break
        except NoSuchElementException:
            i += 1
            print('...', end='')
            sleep(1)
            if i > 3:
                print(f'{NEW_NOTAM_URL} is temporary down, try again later ...')
                button = None
                break
            pass
        except:
            i += 1
            print('...', end='')
            sleep(1)
            if i > 3:
                break
            pass

    try:
        if button:
            button.click()

            if (radio := myNet.elementLocatedBy(driver, By.XPATH, NEW_XPATH_RADIO_TYPE)):
                radio.click()
                myNet.elementInput(driver, NEW_XPATH_TEXTAREA, firLocations)
                myNet.elementClick(driver, NEW_XPATH_SEARCH_BUTTON)
                myNet.windowOpened(driver, windowHandles)
                driver.switch_to.window(driver.window_handles[-1])

                try:
                    myNet.waitForPageLoaded(driver, 160)
                except:
                    pass

                myNet.elementLocatedBy(driver, By.XPATH, NEW_FORM_XPATH)

                if (form := driver.find_element(By.XPATH, NEW_FORM_XPATH)):
                    myNet.scrollBottom(driver)
                    if (table1 := form.find_element(By.TAG_NAME, "table")):
                        if (td1 := table1.find_element(By.TAG_NAME, "td")):
                            for table2 in td1.find_elements(By.TAG_NAME, "table"):
                                if myNOTAM.isChinaNotam(table2.text):
                                    for td2 in table2.find_elements(By.TAG_NAME, "td"):
                                        if myNOTAM.isChinaNotam(td2.text):
                                            notam = myNOTAM.parseNotamText(notam, td2.text)
    except:
        myExcept.printExceptionTrace()
        pass
    return notam, start

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
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    sys.stdout.reconfigure(encoding='UTF-8')

    with myNet.getFirefoxDriver() as driver:
        try:
            notam_data, start = getNotamDetail(driver)

            if notam_data:
                notam_data =  myDict.sortDictByValue(notam_data)
                kmlFiles = myShape.createKmlFile(notam_data)
                myFile.updateTempFile(notam_data)
                myDict.printNotam(notam_data, start)
                # compareKmlList(kmlFiles)
        except:
            myExcept.printExceptionTrace()

###############################################################################
def compareKmlList(kmlFiles):
    for kmlFile in kmlFiles:
        print(f'\ncomparing {kmlFile} with past kml files...')
        myShape.compareKmls(kmlFile)

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'Finished in {timedelta(seconds=result)}\n')

################################################################################################
if __name__ == "__main__":
    showRunTime("main()")
    # myStats.showStats(main)