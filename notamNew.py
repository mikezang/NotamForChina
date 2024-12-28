"""
    Thie is NOTAM module to parse luanch data from NOTAM site
    https://notams.aim.faa.gov/notamSearch/
"""
from datetime import datetime, timedelta
import locale
import sys
from selenium.common.exceptions import NoSuchElementException
from timeit import timeit
from playwright.sync_api import sync_playwright

from myModules import myExcept
from myModules import myShape
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
def getNotamDetail(browser, searchLocaltions):
    start = myDate.getJapanTime()
    print(f"{start}")
    print(f"Searching Location: {searchLocaltions}")
    notam = {}
    
    try:
        context = browser.new_context()
        page = context.new_page()
        page.goto(NEW_NOTAM_URL, wait_until="domcontentloaded")
        button = page.locator(NEW_CSS_SELECTOR_BUTTON_DISCLAIMER)
    except NoSuchElementException:
        print(f'{NEW_NOTAM_URL} is temporary down, try again later ...')
        button = None
        pass

    try:
        if button.is_visible():
            page.click(NEW_CSS_SELECTOR_BUTTON_DISCLAIMER)
            radio = page.wait_for_selector(NEW_XPATH_RADIO_TYPE)
            
            if radio:
                radio.click()
                
                textarea = page.wait_for_selector(NEW_XPATH_TEXTAREA)
                textarea.fill(searchLocaltions)
                
                with context.expect_page() as new_tab_info:
                    page.click(NEW_XPATH_SEARCH_BUTTON)

                new_tab = new_tab_info.value
                new_tab.wait_for_load_state("load")
                form = new_tab.locator(NEW_FORM_XPATH)

                if form.is_visible():
                    new_tab.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    table1 = form.locator("table").nth(0)
                    td1 = table1.locator("td").nth(0)

                    for table2 in td1.locator("table").all():
                        if myNOTAM.isChinaNotam(table2.text_content()):
                            for td2 in table2.locator("td").all():
                                if myNOTAM.isChinaNotam(td2.text_content()):
                                    notam = myNOTAM.parseNotamText(notam, td2.text_content())
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

    with sync_playwright() as p:
        try:
            firLocations = myFile.readConfigFirNames()
            browser = p.firefox.launch(headless=True, slow_mo=0)
            notam_data, start = getNotamDetail(browser, firLocations)
            browser.close()

            if notam_data:
                notam_data =  myDict.sortDictByValue(notam_data)
                myShape.createKmlFile(notam_data)
                myFile.updateTempFile(notam_data)
                myDict.printNotam(notam_data, start)
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
    print(f'\nFinished in {timedelta(seconds=result)}')

################################################################################################
if __name__ == "__main__":
    showRunTime("main()")
    # myStats.showStats(main)