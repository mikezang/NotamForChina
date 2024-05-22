import logging
import time

import numpy as np
import bar_chart_race as bcr
import pandas as pd
from datetime import timedelta, datetime
from timeit import timeit
from openpyxl import load_workbook as loadXLSX

# import constants
import myUtils
import myPlot

################################################################################################
def sumLabel(rocket, All, Ok, startYear=''):
    sumAll, sumOk = int(All), int(Ok)
    percent = 0 if sumOk == 0 or sumAll == 0 else sumOk / sumAll * 100
    rocket1 = '全部' if rocket == '系列' else rocket
    s = f'{rocket1}:'
    s += f'{int(sumOk):02}/{int(sumAll):02}＝成功率' if startYear else f'{int(sumOk):03}/{int(sumAll):03}＝成功率'
    s += f'{percent:05.1f}%' if int(percent) == 100 or int(percent) == 0 else f'{percent:02.2f}%'
    return s

################################################################################################
def getFilenameAndTitle(isAfterRetired, rocket, no='', startYear='', endYear='', plotStartYear=''):
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
    plotYear = '至' + plotStartYear if plotStartYear else ''
    title = f'中国{rocket}运载火箭发展史{retiredTitle}'
    title = f'{years}' + title if startYear else title
    title = f'{plotYear}' + title if plotStartYear else title
    no = '' if no == None else no
    filename = f'videos/{plotYear}'
    filename += 'years/' if startYear else ''
    filename += f'{no}{years}{rocket}{retired}.mp4'
    return filename, title

################################################################################################
def plotRocketChartRaceAnimation(df, rocket, startYear=None, endYear=None, no='', plotStartYear=''):
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
            s = ''
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
    dfList = myPlot.parseToDataFrame(df, isAfterRetired=isAfterRetired, isRocket=True, startYear=startYear, endYear=endYear, rocket=rocket, columnYear='日期', columnNotNull='结果')
    dfFormat = dfList[0]
    dfOk = dfList[1] # ok values
    dfAll = dfList[2] # all values
    if plotStartYear:
        plotYear = myUtils.convertToDate('2024')
        dfFormat = dfFormat[dfFormat.index>=plotYear]
        dfOk = dfOk[dfOk.index>=plotYear] # ok values
        dfAll = dfAll[dfAll.index>=plotYear] # all values
    myLogger.info(f'End parsing data to DataFrame')

    filename, title = getFilenameAndTitle(isAfterRetired, rocket, no, startYear, endYear, plotStartYear)
    myLogger.info(f'Start ploting bar char race: {filename}')
    myUtils.createFolder(filename)
    periodTemplate = '%Y年%m月%d日'
    rocketsCount = min(30, len(dfFormat.columns))
    labelFontSize = 5 if rocketsCount >= 30 else 7
    # stepsPerPeriod = 20 if startYear else 10

    bcr.bar_chart_race(dfAll, dfFormat, 
        save_last_frame_image=True, plot_last_frames=False, last_frames_count=100,
        save_frames_csv=True, incremental_plot=False,
        title=title, filename=filename,interpolate_period=True, #steps_per_period=stepsPerPeriod,  
        tick_template=tickFunc, period_summary_func=sumFunc, bar_texttemplate=barFunc, 
        period_template=periodTemplate, filter_column_colors=True, 
        tick_label_font=labelFontSize, bar_label_font=labelFontSize, n_bars=rocketsCount)

    myUtils.playSound()
    myLogger.info(f'End ploting bar char race: ---------------------------')

################################################################################################
def plot1(df, startYears):
    rocket = '全部'
    for i, startYear in enumerate(startYears):
        endYear = int(startYears[i + 1]) if i < len(startYears) - 1 else 1 + int(startYears[-1])
        plotRocketChartRaceAnimation(df, rocket, startYear=int(startYear), endYear=endYear)

################################################################################################
def plot2(df, rocket, plotStartYear=None):
    if rocket:
        plotRocketChartRaceAnimation(df, rocket, plotStartYear=plotStartYear)

################################################################################################
def plot3(excelFile, sheetName, plotStartYear=None, use_pinyin=False):
    df = pd.read_excel(excelFile, sheetName)
    # df['发射日期'] = df['发射日期'].apply(lambda d: d.replace(hour=0, minute=0, second=0))
    # df['着陆日期'] = df['着陆日期'].apply(lambda d: d.replace(hour=23, minute=23, second=59))
    plotShenzhouChartRaceAnimation(df, plotStartYear, use_pinyin)

################################################################################################
def getBarLabel(taikonaut, iDate, use_pinyin=False):
    startList = [start for start in taikonaut['发射日期']]
    endList = [end for end in taikonaut['着陆日期']]
    bornList = [born for born in taikonaut['出生日期']]
    noList = [no for no in taikonaut['批次']]

    if use_pinyin:
        shipList = [ship for ship in taikonaut['Ship']]
    else:
        shipList = [ship[:-1].replace('舟', '') for ship in taikonaut['载人飞船']]

    daysList = []
    shipDaysList = []
    onOrbit = 'Orbit' if use_pinyin else '在轨'

    for start, end, ship in zip(startList, endList, shipList):
        if iDate >= start and iDate <= end:
            realDays = (iDate - start).days
            daysList.append(realDays)
            shipDaysList.append(f'{ship}({onOrbit}{realDays})')
        elif iDate > end:
            realDays = (end - start).days
            daysList.append(realDays)
            shipDaysList.append(f'{ship}({realDays})')

    no = noList[0]
    age = myUtils.getAge(bornList[0], iDate)
    realDays = int(sum(daysList))
    ships = '+'.join(reversed(shipDaysList))
    batchAge = f'B{no}-A{age}:' if use_pinyin else f'第{no}批{age}岁:'
    dyas = f'D{realDays}' if use_pinyin else f'{realDays}日'
    barLabel = f'{batchAge}{dyas}={ships}'
    return barLabel

################################################################################################
def getSumLabel(df, iDate, cond, use_pinyin=False):
    dfNew = df.copy()
    dfNew['days'] = np.nan
    cond1 = (iDate >= dfNew['发射日期']) & (iDate <= dfNew['着陆日期'])
    if cond1.any():
        dfNew.loc[cond1, 'days'] = (iDate - dfNew.loc[cond1, '发射日期']).dt.days
    cond2 = iDate > dfNew['着陆日期']
    if cond2.any():
        dfNew.loc[cond2, 'days'] = (dfNew.loc[cond2, '着陆日期'] - dfNew.loc[cond2, '发射日期']).dt.days

    taikoColumn = 'Pinyin' if use_pinyin else '航天员'
    dfSumCount = dfNew[cond].groupby(taikoColumn)['days'].agg(['sum', 'count']).reset_index()
    countMax = dfSumCount['count'].max()
    daysMax = int(dfSumCount['sum'].max())
    countMaxName = '／'.join(dfSumCount[dfSumCount['count'] == countMax][taikoColumn].tolist())
    daysMaxName = '／'.join(dfSumCount[dfSumCount['sum'] == daysMax][taikoColumn].tolist())

    l1 = len(daysMaxName)# - ('(' in daysMaxName)
    l2 = len(countMaxName)# - ('(' in countMaxName)
    lMax = max(l1, l2)
    if l1 > l2:
        if use_pinyin:
            countMaxName = countMaxName.ljust(lMax, ' ')
        else:
            lMax = lMax - ('(' in daysMaxName)
            countMaxName = countMaxName.ljust(lMax, '　')
    elif l1 < l2:
        if use_pinyin:
            daysMaxName = daysMaxName.ljust(lMax, ' ')
        else:
            lMax = lMax + ('(' in daysMaxName)
            daysMaxName = daysMaxName.ljust(lMax, '　')
    lMax = max(len(str(daysMax)), len(str(countMax)))
    if use_pinyin:
        sumLabel = f'Max Days {daysMax:0{lMax}}：{daysMaxName}\nMax Times {countMax:0{lMax}}：{countMaxName}'
    else:
        sumLabel = f'最多{daysMax:0{lMax}}日：{daysMaxName}\n最多{countMax:0{lMax}}次：{countMaxName}'
    return sumLabel

################################################################################################
def plotShenzhouChartRaceAnimation(df, plotStartYear='', use_pinyin=False):
    def barFunc(days, taiko, iDate):
        if int(days) == 0:
            barLabel = ''
        else:
            taikonaut = myPlot.get_nearest_taikonaut(df, iDate, taiko, use_pinyin)
            if len(taikonaut) == 0:
                barLabel = ''
            else:
                barLabel = getBarLabel(taikonaut, iDate, use_pinyin)        
        return barLabel

    def sumFunc(vals, ranks):
        iDate = vals.name
        cond = ((iDate >= df['发射日期']) & (iDate <= df['着陆日期'])) | (iDate >= df['着陆日期'])
        if cond.any():
            sumLabel = getSumLabel(df, iDate, cond, use_pinyin)
        else:
            sumLabel = ''
        return {'x': .95, 'y': .03, 's': sumLabel, 'ha': 'right', 'size': 10}

    def tickFunc(val, pos):
        vals = str(val).split('.')
        tick = f'{vals[0]}D' if use_pinyin else f'{vals[0]}日' if int(vals[1]) == 0 else ''
        return tick

    myLogger = logging.getLogger('plot')
    myLogger.info(f'Start parsing data to DataFrame')
    dfList = myPlot.parseToDataFrame(df, isShenzhou=True, use_pinyin=use_pinyin)
    dfWide = dfList[0]
    dfRank = dfList[1]
    if plotStartYear:
        plotYear = myUtils.convertToDate('2024')
        dfWide = dfWide[dfWide.index>=plotYear]
        dfRank = dfRank[dfRank.index>=plotYear]
    myLogger.info(f'End parsing data to DataFrame')

    if use_pinyin:
        filename, title = 'videos\\ChinaTaikonautsOrbitBarChartRace.mp4', 'China Taikonauts Orbit Bar Chart Race (On-orbit Priority)'
    else:
        plotYear = '至' + plotStartYear if plotStartYear else ''
        filename, title = f'videos\\{plotYear}中国航天员在轨动态条形图.mp4', f'{plotYear}中国航天员在轨动态条形图(在轨优先)'
    myLogger.info(f'Start ploting bar char race: {filename}')
    myUtils.createFolder(filename)
    periodTemplate = '%B %d, %Y' if use_pinyin else '%Y年%m月%d日'

    bcr.bar_chart_race(dfWide, dfRank, 
                       save_last_frame_image=True, plot_last_frames=False, last_frames_count=100,
                       save_frames_csv=True, incremental_plot=False,
                       title=title, filename=filename,interpolate_period=True, steps_per_period=10,  
                       tick_template=tickFunc, period_summary_func=sumFunc, bar_texttemplate=barFunc, 
                       period_template=periodTemplate, filter_column_colors=True)

    myUtils.playSound()
    myLogger.info(f'End ploting bar char race: ---------------------------')

################################################################################################
def main():
    logFilename = f"temp/{time.strftime('%Y%m%d-%H%M%S')}.log"
    myUtils.setLogging(logFilename)
    myLogger = logging.getLogger('main')

    myLogger.info(f'Start: *****************************')
    myPlot.init(True)

    myLogger.info(f'Start reading data:')
    excelFile = "data/ChinaRocketLaunch.xlsx"
    sheetName = "中国航天员"
    plot3(excelFile, sheetName, '2024')

    sheetName = "发射纪录"
    df = myPlot.readDataFromSheetNew(excelFile, sheetName)
    myLogger.info(f'End reading data:')

    startYears = ['1970', '1980', '1990', '2000']
    startYears += ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019']
    startYears += ['2020', '2021', '2022', '2023']
    startYears = []
    if startYears:
        plot1(df, startYears)

    rockets = ['民营', '其他', '长征', '系列', '全部']
    rockets = []
    for rocket in rockets:
        if rocket in '民营, 其他':
            plot2(df, rocket)
        else:
            plot2(df, rocket, '2024')

    myLogger.info(f'End: *******************************')

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')
    
if __name__ == "__main__":
    showRunTime("main()")