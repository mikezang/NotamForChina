"""
    Thie is NOTAM module to parse luanch data from NOTAM site
    https://notams.aim.faa.gov/notamSearch/
"""
# pylint: disable=E1101,W0703,C0103,C0116,C0301

import os
from time import sleep
import inspect
from datetime import datetime, timedelta
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from timeit import timeit

import myUtils
import constants
import nsf


###############################################################################################
def printNotam(launch_date):
    print(f"\nNOTAM发射预测{myUtils.getJapanTime()}")
    print("================================")
    myUtils.printNotamDict(launch_date)
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
    notam = {}
    
    try:
        driver.get(constants.NEW_NOTAM_URL)
        myUtils.checkVPN(driver)
        radio = ''

        sleep(1)
        button = driver.find_element(By.CSS_SELECTOR, constants.NEW_CSS_SELECTOR_BUTTON_DISCLAIMER)
        if button:
            button.click()
            radio = myUtils.elementXPath(driver, 30, constants.NEW_XPATH_RADIO_TYPE)

            if radio:
                radio.click()
                print(f"Searching {command}: {searchLocaltions}\n")

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
                                            # print(number, startDate, endDate, loc, nsf.formatLatitudeLongitude(area))

                                            if area != '':
                                                startDate = nsf.convertDate(startDate)
                                                endDate = nsf.convertDate(endDate)
                                                area = nsf.formatLatitudeLongitude(area)
                                                notam = getNoatmDict(notam, number, startDate, endDate, location, area)
                myUtils.isTempFileSaved = False
    except :
        print(f'{__file__}: {os.linesep} + {traceback.format_exc()}')
        pass
    return notam

################################################################################################
# def getNotam(driver, command, searchTexts):
#     notam = {}
#     isFirstNotam = True
    
#     try:
#         for searchText in searchTexts:
#             driver.get(constants.NOTAM_URL)
#             myUtils.checkVPN(driver)
#             select = ''

#             if isFirstNotam:
#                 sleep(1)
#                 myUtils.elementClick(driver, 10, constants.XPATH_BUTTON_DISCLAIMER)

#             WebDriverWait(driver, 60).until_not(EC.presence_of_element_located((By.XPATH, constants.XPATH_DIV_HIDE1)))
#             WebDriverWait(driver, 60).until_not(EC.presence_of_element_located((By.XPATH, constants.XPATH_DIV_HIDE2)))
#             WebDriverWait(driver, 60).until_not(EC.presence_of_element_located((By.XPATH, constants.XPATH_DIV_HIDE3)))

#             select = WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH, constants.XPATH_SELECT_TYPE)))
#             select = myUtils.elementXPath(driver, 30, constants.XPATH_SELECT_TYPE)

#             if select:
#                 driver.execute_script("arguments[0].scrollIntoView();", select)

#                 if isFirstNotam:
#                     sleep(2)
#                     myUtils.elementInput(driver, 30, constants.COMMANDS['Location'], searchText)
#                     print()
#                 else:
#                     select.click()
#                     myUtils.elementXPath(driver, 10, constants.XPATH_SELECT_OPTION.format(command))

#                     if 'RJJJ' not in searchText:
#                         print(f"Searching {command}: {searchText}")

#                     Select(select).select_by_visible_text(command)
#                     myUtils.elementInput(driver, 30, constants.COMMANDS[command], searchText)
#                 myUtils.elementClick(driver, 30, constants.XPATH_BUTTON_SEARCH)

#                 if isFirstNotam:
#                     isFirstNotam = False
#                     sleep(2)
#                 else:
#                     notam.update(getNotamDetail(driver, searchText))
#         myUtils.isTempFileSaved = False

    # except ElementClickInterceptedException as e:
    #     print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
    #     pass
    # except ElementNotInteractableException as e:
    #     print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
    #     pass
    # except NoSuchElementException as e:
    #     print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
    #     pass
    # except Exception as e:
    #     # print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
    #     pass
    # return notam

################################################################################################
# def getNotamDetail(driver, searchText):
#     notam = {}

#     try:
#         WebDriverWait(driver, 130).until_not(EC.presence_of_element_located((By.XPATH, constants.XPATH_DIV_HIDE1)))
#         WebDriverWait(driver, 130).until_not(EC.presence_of_element_located((By.XPATH, constants.XPATH_DIV_HIDE2)))

#         try:
#             element = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, constants.XPATH_TRS_NOTAM)))
#             driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
#             # driver.execute_script("arguments[0].scrollIntoView(true);", element)
#         except:
#             pass
        
#         if searchText == 'TEMPORARY RESTRICTED AREA ESTABLISHED BOUNDED':
#             driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
#             sleep(10)
#         trs = driver.find_elements(By.XPATH, constants.XPATH_TRS_NOTAM)

#         for iTr in range(len(trs)):
#             WebDriverWait(driver, 130).until_not(EC.presence_of_element_located((By.XPATH, constants.XPATH_DIV_HIDE2)))
#             WebDriverWait(driver, 130).until_not(EC.presence_of_element_located((By.XPATH, constants.XPATH_DIV_HIDE3)))

#             tr = driver.find_elements(By.XPATH, constants.XPATH_TRS_NOTAM)[iTr]
#             tds = tr.find_elements(By.XPATH,".//child::td")
#             tdArray = []

#             for td in tds:
#                 tdArray.append(td.text)

#             location = 'KZAK' if tdArray[constants.COL_LOCATION] == 'ZAK' else tdArray[constants.COL_LOCATION]

#             if location in constants.LOCATIONS_PATTERN:
#                 if tdArray[constants.COL_END_DATE_UTC] == 'PERM':
#                     continue

#                 endDateUtc = convertDate(tdArray[constants.COL_END_DATE_UTC])
#                 if myUtils.isPastTime(endDateUtc):
#                     continue
#                 startDateUtc = convertDate(tdArray[constants.COL_START_DATE_UTC])

#                 condition = myUtils.removeAllSpaces(tdArray[constants.COL_CONDITION])
#                 if myUtils.isNotChinaNotam(location, condition):
#                     continue

#                 patterns = constants.LOCATIONS_PATTERN[location].split('|')[0].split(";")
#                 # items = findall(patterns[0], condition)

#                 # if len(items) == 0 or condition[-3:] == '...':
#                 if condition[-3:] == '...':
#                     condition = myUtils.removeAllSpaces(myUtils.getConditionDetail(driver, tds[constants.COL_CONDITION]))
                    
#                 area = findLatitudeLongitude(patterns[0], condition)

#                 if len(patterns) > 1 and (area == '' or area[0] not in 'NS'):
#                     area = findLatitudeLongitude(patterns[1], condition)

#                 if searchText == 'FLW SEGMENT OF ATS RTE CLSD' and len(area.split('|')) == 1:
#                     continue

#                 if area != '':
#                     number = tdArray[constants.COL_NUMBER]
#                     notam = getNoatmDict(notam, number, startDateUtc, endDateUtc, location, area)
                    # if number in notam:
                    #     location = notam[number].split(";")[2] + "/" + location
                    # notam[number] = startDateUtc + ";"
                    # notam[number] = notam[number] + endDateUtc + ";"
                    # notam[number] = notam[number] + location + ";"
                    # notam[number] = notam[number] + area #+ ";" + str([(p.dm()) for p in coords])

    # except ElementClickInterceptedException as e:
    #     print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
    #     pass
    # except ElementNotInteractableException as e:
    #     print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
    #     pass
    # except TimeoutException as e:
    #     print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
    #     pass
    # except NoSuchElementException as e:
    #     print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
    #     pass
    # except Exception as e:
    #     print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
    #     pass
    # return notam

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
        # notam_data = notam.getNotamDetailNew(driver, command, constants.FIR_LOCATIONS)

        if notam_data:
            # notamDict = myUtils.readNotamDictDetailFromTextFile('./data/notams.txt')
            # if notamDict:
            #     notam_data.update(notamDict)
            notam_data =  myUtils.sortDictByValue(notam_data)
            printNotam(notam_data)
            myUtils.createKmlFile(notam_data)
    except:
        print(f'{__file__}: {os.linesep} + {traceback.format_exc()}')

    if driver:
        driver.quit()

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')

################################################################################################
if __name__ == "__main__":
    showRunTime("main()")