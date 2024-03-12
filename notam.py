"""
    Thie is NOTAM module to parse luanch data from NOTAM site
    https://notams.aim.faa.gov/notamSearch/
"""
from time import sleep
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from timeit import timeit

import myUtils
import constants
import nsf

###############################################################################################
def printNotam(dictData):
    print(f"\nNOTAM发射预测{myUtils.getJapanTime()}")
    print("================================")
    myUtils.printNotamDict(dictData)
    print("================================")
    print(f"NOTAM发射预测{myUtils.getJapanTime()}\n")

################################################################################################
def parseMsa(text):
    location = 'MSA'
    number = myUtils.getMsaLocation(text)
    text = text.replace('\n', '').replace(' ', '').replace('/', '').replace('、', '')
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
def getNotamDetailNew(driver, command, searchLocaltions):
    print(f"{myUtils.getJapanTime()}")
    print(f"Searching {command}: {searchLocaltions}")
    notam = {}
    
    try:
        driver.get(constants.NEW_NOTAM_URL)
        # myUtils.checkVPN(driver)
        radio = ''

        sleep(1)
        button = driver.find_element(By.CSS_SELECTOR, constants.NEW_CSS_SELECTOR_BUTTON_DISCLAIMER)
        if button:
            button.click()
            radio = myUtils.elementXPath(driver, 30, constants.NEW_XPATH_RADIO_TYPE)

            if radio:
                radio.click()
                myUtils.elementInput(driver, 30, constants.NEW_XPATH_TEXTAREA, searchLocaltions)
                myUtils.elementClick(driver, 30, constants.NEW_XPATH_SEARCH_BUTTON)
                sleep(3)

                window_after = driver.window_handles[-1]
                driver.switch_to.window(window_after)
                sleep(1)

                form = driver.find_element(By.XPATH, "//form[@name='NotamRetrievalForm']")
                if form:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                    table1 = form.find_element(By.TAG_NAME, "table")
                
                    if table1:
                        td1 = table1.find_element(By.TAG_NAME, "td")

                        if td1:
                            tables = td1.find_elements(By.TAG_NAME, "table")

                            for table2 in tables:
                                if myUtils.isChinaNotam(table2.text):
                                    tds = table2.find_elements(By.TAG_NAME, "td")

                                    for td2 in tds:
                                        if myUtils.isChinaNotam(td2.text):
                                            location, number, startDate, endDate, area = parseNotam(td2.text)

                                            if area != '':
                                                startDate = nsf.convertDate(startDate)
                                                endDate = nsf.convertDate(endDate)
                                                area = nsf.formatLatitudeLongitude(area)
                                                notam = getNoatmDict(notam, number, startDate, endDate, location, area)
                myUtils.isTempFileSaved = False
    except :
        myUtils.pritnExceptionTrace()
        pass
    return notam

################################################################################################
def getNoatmDict(notamDict, number, startDate, endDate, location, area):
    if number in notamDict:
        location1 = notamDict[number].split(";")[2]
        location = location1 + "/" + location if location != location1 else location
    notamDict[number] = startDate + ";"
    notamDict[number] = notamDict[number] + endDate + ";"
    notamDict[number] = notamDict[number] + location + ";"
    notamDict[number] = notamDict[number] + area #+ ";" + str([(p.dm()) for p in coords])
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
    driver = myUtils.getFirefoxDriver()
    command = 'Location'
    try:
        firLocations = myUtils.readConfigFirNames()
        notam_data = getNotamDetailNew(driver, command, firLocations)

        if notam_data:
            notam_data =  myUtils.sortDictByValue(notam_data)
            printNotam(notam_data)
            # subject = f"NOTAM发射预测{myUtils.getJapanTime()}"
            # body = [f'{i + 1:02} {k}:{v}\n' for i, (k, v) in enumerate(notam_data.items())]
            # myUtils.sendEmail(subject, body)
            myUtils.createKmlFile(notam_data)
    except:
        myUtils.pritnExceptionTrace()

    if driver:
        driver.quit()

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'Finished in {timedelta(seconds=result)}\n')

################################################################################################
if __name__ == "__main__":
    showRunTime("main()")