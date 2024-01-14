"""
    Thie is main module
"""
# pylint: disable=W0622,W0703,C0103,C0116,C0301

from sys import exit, path
import inspect
from timeit import timeit
from datetime import timedelta
from selenium.common.exceptions import NoSuchElementException

path.append("")

import myUtils
import notam
import nsf
import trip
import constants

################################################################################################
def main():
    command, p1, p2 = myUtils.checkArgv()
    driver = None

    if command == 'Location':
        try:
            driver = myUtils.getFirefoxDriver()
            firLocations = myUtils.readConfigFirNames()
            notam_data = notam.getNotamDetailNew(driver, command, firLocations)
            # notam_data = notam.getNotamDetailNew(driver, command, constants.FIR_LOCATIONS)

            if notam_data:
                # notamDict = myUtils.readNotamDictDetailFromTextFile('./data/notams.txt')
                # if notamDict:
                #     notam_data.update(notamDict)
                notam_data =  myUtils.sortDictByValue(notam_data)
                notam.printNotam(notam_data)
                myUtils.createKmlFile(notam_data)
        except Exception as e:
            print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
    # elif command == 'Free Text':
    #     try:
    #         driver = myUtils.getFirefoxDriver()
    #         notam_data =notam.getNotam(driver, command, constants.FREE_TEXTS)
    #         if notam_data:
    #             # notamDict = myUtils.readNotamDictDetailFromTextFile('./data/notams.txt')
    #             # if notamDict:
    #             #     notam_data.update(notamDict)
    #             notam_data =  myUtils.sortDictByValue(notam_data)
    #             notam.printNotam(notam_data)
    #             myUtils.createKmlFile(notam_data)
    #     except NoSuchElementException:
    #         pass
    #     except Exception as e:
    #         print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
    elif command == 'kml':
        try:
            notamDict = myUtils.readNotamDictDetailFromTextFile('./data/notams.txt')
            if notamDict:
                notam.printNotam(notamDict)
                myUtils.createKmlFile(notamDict)
        except Exception as e:
            print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
    # elif command == 'all':
    #     try:
    #         driver = myUtils.getFirefoxDriver()
    #         ctrip_data = trip.getCTrip(driver)
    #         eniutrip_data = trip.getENiuTrip(driver)
    #         trip_data = myUtils.combineValuesForSameDictKey(ctrip_data, eniutrip_data)
    #         notam_data = myUtils.sortDictByValue(notam.getNotam(driver, "Free Text", constants.FREE_TEXTS))
    #         if trip_data:
    #             trip.printTrip(trip_data)
    #         if notam_data:
    #             notam.printNotam(notam_data)
    #             myUtils.createKmlFile(notam_data)
    #     except Exception as e:
    #         # print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
    #         pass
    elif command == 'ctrip':
        try:
            driver = myUtils.getFirefoxDriver()
            trip_data = trip.getCTrip(driver)
            trip.printTrip(trip_data)
            if trip_data:
                print('\n./temp/LaunchTravels.html created!')

        except Exception as e:
            print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
    elif command == 'eniutrip':
        try:
            driver = myUtils.getFirefoxDriver()
            trip_data = trip.getENiuTrip(driver)
            trip.printTrip(trip_data)
        except Exception as e:
            print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
    elif 'fir' == command:
        try:
            print('Create all FIR Boundaries from file.')
            myUtils.createFirBoundaryKmlFile('FIR IN THE ASIA-PACIFIC', constants.FIR_BOUNDARY)
        except Exception as e:
            print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
    elif 'nsf' in command:
        if command == 'nsfurls':
            try:
                driver = myUtils.getFirefoxDriver()
                print('Create all NSF launched urls from site.')
                page = 'url'
                nsfDict = nsf.getNsfUrlList(driver, page)
                myUtils.writeNsfToFile(nsfDict)
            except Exception as e:
                print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
        elif command == 'nsfcontents':
            try:
                driver = myUtils.getFirefoxDriver()
                print('Create all NSF launched contents from file.')
                nsfUrlList = myUtils.loadDictFromJsonFile('nsf-urls')
                titleForCheck = p1
                nsf.parseNsfContents(driver, nsfUrlList, titleForCheck)
            except Exception as e:
                print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
        elif command == 'nsfmaps':
            try:
                print('Create all NSF launched maps from file.')
                nsfLaunchList = myUtils.loadDictFromJsonFile('nsf')
                titleForCheck = p1
                nsf.drawNsfNotam(nsfLaunchList, titleForCheck)
            except Exception as e:
                print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
        else:
            try:
                if command == 'nsfnotams':
                    print('Create all NSF launched NOTAMs from file.')
                    driver = myUtils.getFirefoxDriver()
                    page = 'all'
                    nsf_list = myUtils.loadDictFromJsonFile('nsf-urls')
                    titleForCheck = p1
                    nsf_data = myUtils.sortDictByKey(nsf.getNsfNotamsFromFile(nsf_list, titleForCheck))
                    # nsf_data = myUtils.sortDictByKey(nsf.getNsfList(driver, nsf_list, titleForCheck))
                    nsf.printNsf(nsf_data)
                else:
                    driver = myUtils.getFirefoxDriver()
                    page = command[3:] if len(command) > 3 else '1'
                    nsf_list = nsf.getNsfUrlList(driver, page)
                    myUtils.updateDictToJsonFile(nsf_list, "nsf-urls")
                    titleForCheck = p1
                    nsf_data = myUtils.sortDictByKey(nsf.getNsfList(driver, nsf_list, titleForCheck))
                    nsf.printNsf(nsf_data)

                myUtils.updateNsfNotamJsonFile(nsf_data, 'nsf')
            except Exception as e:
                myUtils.exceptPrint()
                print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
    elif command == 'compare':
        oldFile = p1
        newFile = p2
        print(f'Old file: {oldFile}')
        print(f'New file: {newFile}')
        similarity_index = myUtils.compare_kml_files(oldFile, newFile)
        print(f'Similarity: {similarity_index}')
    elif command == 'test':
        showRunTime('')

#    stats = pstats.Stats(pr)
#    stats.sort_stats(pstats.SortKey.TIME)
#    stats.print_stats(10)

    if driver:
        driver.quit()

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')


################################################################################################
def convert2DDList() -> None:
    dms = ('N09 56 00,E98 33 00','N10 00 00,E96 00 00','N11 00 00,E94 25 00','N13 30 00,E94 25 00','N14 00 00,E92 00 00','N20 00 00,E92 00 00','N21 00 00,E92 00 00','N21 57 00,E92 32 00')
    dd1 = [myUtils.convertDMS2DD(c) for c in dms]
    dd = [(a,b) for (b,a) in dd1]
    for a, b in dd:
        print(f'({a:5f},{b:4f}),')

################################################################################################
if __name__ == "__main__":
    # main()
    # convert2DDlist()
    # drawCircle()
    showRunTime("main()")
    exit