import logging
import time
import bar_chart_race as bcr
import pandas as pd
from datetime import timedelta
from timeit import timeit
from openpyxl import load_workbook as loadXLSX

# import constants
import myUtils
import myPlot

def sumLabel(rocket, All, Ok, startYear=''):
    sumAll, sumOk = int(All), int(Ok)
    percent = 0 if sumOk == 0 or sumAll == 0 else sumOk / sumAll * 100
    rocket1 = '全部' if rocket == '系列' else rocket
    s = f'{rocket1}:'
    s += f'{int(sumOk):02}/{int(sumAll):02}＝成功率' if startYear else f'{int(sumOk):03}/{int(sumAll):03}＝成功率'
    s += f'{percent:05.1f}%' if int(percent) == 100 or int(percent) == 0 else f'{percent:02.2f}%'
    return s

def plotChartRaceAnimation(excelSheet, rocket, startYear=None, endYear=None, no=None):
    def barFunc(val, label, iDate):
        if int(val) == 0:
            return ''
        else:
            realAll = myPlot.get_nearest_row(dfAll, iDate)[label]
            realOk = myPlot.get_nearest_row(dfOk, iDate)[label]
            valAll, valOk = int(realAll), int(realOk)
            percent = 0 if valOk == 0 or valAll == 0 else valOk / valAll * 100
            ret = f'{int(valOk)}/{int(valAll):.0f}＝成功率'
            ret += f'{percent:.0f}%' if int(percent) == percent else f'{percent:.2f}%'
            retiredRocketsDict = myUtils.readConfigRetiredDict() #constants.RETIRED_ROCKETS

            if label in retiredRocketsDict:
                retiredDate = retiredRocketsDict[label]
                if isAfterRetired:
                    ret += f'({retiredDate[:4]}年退役)' if iDate >= pd.Timestamp(retiredDate) else ''
                else:
                    ret += f'({retiredDate[:4]}年退役)'
            return ret

    def sumFunc(vals, ranks):
        iDate = vals.name
        czRowAll = myPlot.get_nearest_row(dfAll, iDate)
        czRowOk = myPlot.get_nearest_row(dfOk, iDate)
        realSumAll = czRowAll.sum()
        realSumOk = czRowOk.sum()
        s = sumLabel(rocket, realSumAll, realSumOk, startYear)
        s1, s2 = '', ''
        if rocket in ['系列', '全部']:
            czSumAll = czRowAll[czRowAll.index.str.startswith('长征')].sum()
            czSumOk = czRowOk[czRowOk.index.str.startswith('长征')].sum()
            s1 = sumLabel('长征', czSumAll, czSumOk, startYear) + '\n'
            nczSumAll = realSumAll - czSumAll
            nczSumOk = realSumOk - czSumOk
            s2 = sumLabel('其他', nczSumAll, nczSumOk, startYear) + '\n'
        s = f'{s1}{s2}{s}'
        return {'x': .95, 'y': .2, 's': s, 'ha': 'right', 'size': 10}

    def tickFunc(val, pos):
        if pos == 0:
            s = '0次'
        else:
            vals = str(val).split('.')
            s = f'{vals[0]}次' if int(vals[1]) == 0 else ''
        return s

    myLogger = logging.getLogger('plot')
    myLogger.info(f'Start parsing data to DataFrame')
    # data encode format: 
    # xxx000.yyy before retired
    #    xxx.yyy since retired 
    # xxx is launch counts, 
    # yyy is luanch counts successfully    
    isAfterRetired = True
    dfList = myPlot.parseExcelSheetToDataFrame(excelSheet, isAfterRetired=isAfterRetired, isRace=True, startYear=startYear, endYear=endYear, rocket=rocket, columnYear='日期', columnNotNull='结果')
    dfFormat = dfList[0] 
    # df2 = dfFormat.iloc[:, ::-1] # Reverse the order of columns to rank based on last occurrence
    dfOk = dfList[1] # ok values
    dfAll = dfList[2] # all values
    myLogger.info(f'End parsing data to DataFrame')

    filename, title = getFilenameAndTitle(isAfterRetired, rocket, no, startYear, endYear)
    myLogger.info(f'Start ploting bar char race: {filename}')
    myUtils.createFolder(filename)
    periodTemplate = '%Y年%m月%d日'

    if startYear != None:
        bcr.bar_chart_race(dfAll, dfFormat, save_last_frame=True, title=title, filename=filename, tick_template=tickFunc, period_summary_func=sumFunc, bar_texttemplate=barFunc, period_template=periodTemplate, filter_column_colors=True, interpolate_period=True, steps_per_period=20)
    elif rocket == '全部':
        bcr.bar_chart_race(dfAll, dfFormat, save_last_frame=True, title=title, filename=filename, tick_template=tickFunc, period_summary_func=sumFunc, bar_texttemplate=barFunc, period_template=periodTemplate, filter_column_colors=True, interpolate_period=True, tick_label_font=5, bar_label_font=5, n_bars=30)
    else:
        bcr.bar_chart_race(dfAll, dfFormat, save_last_frame=True, title=title, filename=filename, tick_template=tickFunc, period_summary_func=sumFunc, bar_texttemplate=barFunc, period_template=periodTemplate, filter_column_colors=True, interpolate_period=True)

    myUtils.playSound()
    myLogger.info(f'End ploting bar char race: ---------------------------')

def getFilenameAndTitle(isAfterRetired, rocket, no='', startYear='', endYear=''):
    if isAfterRetired == None:
        retired = '-noRetired'
        retiredTitle = '(发射数优先)'
    else:
        retired = '' if isAfterRetired else '-beforeRetired'
        retiredTitle = '(现役期间优先)' if isAfterRetired else '(现役优先)'
    if startYear:
        years = f'{startYear}' if startYear == endYear - 1 else f'{startYear}～{endYear - 1}'
    else:
        years = ''
    title = f'中国{rocket}运载火箭发展史{retiredTitle}'
    title = f'{years}' + title if startYear else title
    no = '' if no == None else no
    filename = f'videos/{no}{years}{rocket}{retired}.mp4'
    return filename, title

def plot1(excelSheet, startYears):
    rocket = '全部'
    for i, startYear in enumerate(startYears):
        endYear = int(startYears[i + 1]) if i < len(startYears) - 1 else 1 + int(startYears[-1])
        plotChartRaceAnimation(excelSheet, rocket, startYear=int(startYear), endYear=endYear)

def plot2(excelSheet, rockets):
    for i, rocket in enumerate(rockets):
        if rocket:
            plotChartRaceAnimation(excelSheet, rocket)

def main():
    logFilename = f"temp/{time.strftime('%Y%m%d-%H%M%S')}.log"
    myUtils.setLogging(logFilename)
    myLogger = logging.getLogger('main')

    myLogger.info(f'Start: *****************************')
    myPlot.init(True)

    myLogger.info(f'Start reading data:')
    excelFile = "data/ChinaRocketLaunch.xlsx"
    sheetName = "发射纪录"
    excelBook = loadXLSX(excelFile, data_only=True, read_only=True)
    excelSheet = excelBook[sheetName]
    myLogger.info(f'End reading data:')

    startYears = ['1970', '1980', '1990', '2000']
    startYears += ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019']
    startYears += ['2020', '2021', '2022', '2023']
    startYears = []
    plot1(excelSheet, startYears)

    rockets = ['民营', '其他', '长征', '系列', '全部']
    rockets = ['民营']
    plot2(excelSheet, rockets)

    myLogger.info(f'End: *******************************')

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')
    
if __name__ == "__main__":
    showRunTime("main()")