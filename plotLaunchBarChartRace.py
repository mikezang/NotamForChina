import logging
import time
import bar_chart_race as bcr
from datetime import date, datetime, timedelta
from timeit import timeit

from myModules import myFile
from myModules import myConfig
from myModules import myPlotInit
from myModules import myPlot
from myModules import myExcel
from myModules import myDate

DATA_FILE_PATH = './data/'
TEMP_FILE_PATH = './temp/'

################################################################################################
def rocketSumLabel(rocket, All, Ok, startYear=''):
    sumAll, sumOk = int(All), int(Ok)
    percent = 0 if sumOk == 0 or sumAll == 0 else sumOk / sumAll * 100
    rocket1 = '全部' if rocket == '系列' else rocket
    s = f'{rocket1}:'
    s += f'{int(sumOk):02}/{int(sumAll):02}＝' if startYear else f'{int(sumOk):03}/{int(sumAll):03}＝'
    s += f'{percent:05.1f}%成功率' if int(percent) == 100 or int(percent) == 0 else f'{percent:02.2f}%成功率'
    return s

################################################################################################
def getFilenameAndTitle(isAfterRetired, rocket, no='', startYear='', endYear='', plotStartYear='', count=0):
    if isAfterRetired == None:
        retired = '-noRetired'
        retiredTitle = '(发射数优先)'
    else:
        retired = '' if isAfterRetired else '-beforeRetired'
        retiredTitle = '(现役期间优先)' if isAfterRetired else '(现役优先)'
    if startYear:
        years = f'{startYear}年' if int(startYear) == int(endYear) - 1 else f'{startYear}～{int(endYear) - 1}年'
    else:
        years = ''
    plotYear = f'至{plotStartYear}年'  if plotStartYear else ''
    title = f'中国{rocket}运载火箭发展史{retiredTitle}'
    title = f'{years}' + title if startYear else title
    title = f'{plotYear}' + title if plotStartYear else title
    title = title[:-1] + '前30)' if count > 30 else title
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
            ret = f'{int(valOk)}/{int(valAll):.0f}＝'
            ret += f'{percent:.0f}%成功率' if int(percent) == percent else f'{percent:.2f}%成功率'
            retiredRocketsDict = myConfig.readConfigRetiredDict() #constants.RETIRED_ROCKETS

            if label in retiredRocketsDict:
                retiredDate = retiredRocketsDict[label]
                if isAfterRetired:
                    import pandas as pd
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
        s = rocketSumLabel(rocket, realSumAll, realSumOk, startYear) + '\n'
        s1, s2 = '', ''
        if rocket in ['系列', '全部']:
            czSumAll = czRowAll[czRowAll.index.str.startswith('长征')].sum()
            czSumOk = czRowOk[czRowOk.index.str.startswith('长征')].sum()
            s1 = rocketSumLabel('长征', czSumAll, czSumOk, startYear) + '\n'
            nczSumAll = realSumAll - czSumAll
            nczSumOk = realSumOk - czSumOk
            s2 = rocketSumLabel('其他', nczSumAll, nczSumOk, startYear)
        s = f'{s}{s1}{s2}'
        return {'x': .975, 'y': .03, 's': s, 'ha': 'right', 'size': 10}

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
    dfList = myPlot.parseToDataFrame(df, isAfterRetired=isAfterRetired, isRocket=True, startYear=startYear, endYear=endYear, rocket=rocket, columnDate='日期', columnNotNull='结果')
    dfFormat = dfList[0]
    dfOk = dfList[1] # ok values
    dfAll = dfList[2] # all values
    if plotStartYear:
        plotYear = myDate.convertToDate(plotStartYear)
        dfFormat = dfFormat[dfFormat.index>=plotYear]
        dfOk = dfOk[dfOk.index>=plotYear] # ok values
        dfAll = dfAll[dfAll.index>=plotYear] # all values
    myLogger.info(f'End parsing data to DataFrame')

    filename, title = getFilenameAndTitle(isAfterRetired, rocket, no, startYear, endYear, plotStartYear, len(dfFormat.columns))
    myLogger.info(f'Start ploting bar char race: {filename}')
    myFile.createFolder(filename)
    periodTemplate = '%Y年%m月%d日'
    rocketsCount = min(30, len(dfFormat.columns))
    labelFontSize = 5 if rocketsCount >= 30 else 6 if rocketsCount >= 20 else 7
    fig_kwargs = {'figsize': (6, 3.375), 'dpi': 320}
    print(f'运载火箭数: {len(dfFormat.columns)}')

    bcr.bar_chart_race(dfAll, dfFormat, 
        save_last_frame_image=True, plot_last_frames=False, last_frames_count=100,
        save_frames_csv=False, incremental_plot=False, fig_kwargs=fig_kwargs,
        title=title, filename=filename,interpolate_period=True, #steps_per_period=stepsPerPeriod,  
        tick_template=tickFunc, period_summary_func=sumFunc, bar_texttemplate=barFunc, 
        period_template=periodTemplate, filter_column_colors=True, 
        tick_label_font=labelFontSize, bar_label_font=labelFontSize, n_bars=rocketsCount)
    myLogger.info(f'End ploting bar char race: ---------------------------')

################################################################################################
def plot1(df, startYears):
    rocket = '全部'
    for i, startYear in enumerate(startYears):
        endYear = int(startYears[i + 1]) if i < len(startYears) - 1 else 1 + int(startYears[-1])
        plotRocketChartRaceAnimation(df, rocket, startYear=startYear, endYear=str(endYear))

################################################################################################
def plot2(df, rocket, plotStartYear=None):
    if rocket:
        plotRocketChartRaceAnimation(df, rocket, plotStartYear=plotStartYear)

################################################################################################
def plot3(excelFile, sheetName, plotStartYear=None, days=30, plotLastFrames=True, use_pinyin=False):
    import pandas as pd
    condition = '在轨 >= -1 and 航天员 not in ["-","无人"]'
    df = pd.read_excel(excelFile, sheetName, usecols='A:N', ).query(condition)
    dfExit = pd.read_excel(excelFile, '出舱', usecols='A:G', )
    plotShenzhouChartRaceAnimation(df, dfExit, plotStartYear, days=days, plotLastFrames=plotLastFrames, use_pinyin=use_pinyin)

################################################################################################
def getAge(born, ageYear=None):
    if isinstance(born, datetime) == True:
        today = date.today() if ageYear == None else ageYear
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    else:
        return '?'

################################################################################################
def getBarLabel(taikonaut, iDate, use_pinyin=False):
    startList = [start for start in taikonaut['发射日期']]
    endList = [end for end in taikonaut['着陆日期']]
    bornList = [born for born in taikonaut['出生日期']]
    noList = [no for no in taikonaut['批次']]
    roleList = [role for role in taikonaut['类型']]

    if use_pinyin:
        shipList = [ship for ship in taikonaut['缩写']]
    else:
        # shipList = [ship[:-1].replace('舟', '') if len(ship) > 3 else ship for ship in taikonaut['飞船']]
        shipList = [ship for ship in taikonaut['缩写']]

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

    role = roleList[0]
    no = int(noList[0])
    age = getAge(bornList[0], iDate)
    realDays = int(sum(daysList))
    ships = '+'.join(reversed(shipDaysList))
    batchAge = f'B{no}-A{age}:' if use_pinyin else f'第{no}批{age}岁{role}:'
    dyas = f'D{realDays}' if use_pinyin else f'{realDays}日'
    barLabel = f'{batchAge}{dyas}={ships}' if ships else f'{batchAge}{dyas}'
    return barLabel

################################################################################################
def getSumLabel(df, dfExit, iDate, cond, condExit):
    import numpy as np
    dfNew = df.copy()
    dfNewExit = dfExit.copy()
    dfNew['days'] = np.nan
    cond1 = (iDate >= dfNew['发射日期']) & (iDate <= dfNew['着陆日期'])
    if cond1.any():
        dfNew.loc[cond1, 'days'] = (iDate - dfNew.loc[cond1, '发射日期']).dt.days
    cond2 = iDate > dfNew['着陆日期']
    if cond2.any():
        dfNew.loc[cond2, 'days'] = (dfNew.loc[cond2, '着陆日期'] - dfNew.loc[cond2, '发射日期']).dt.days

    taikoColumn = '航天员'
    dfSumExit = dfNewExit[condExit].groupby(taikoColumn)['出舱'].agg(['sum']).reset_index()
    if dfSumExit.empty:
        sumExitMax = 0
        sumExitMaxLabel = ''
    else:
        # 累计最大出舱次数
        sumExitMax = int(dfSumExit['sum'].max()) 
        sumExitMaxLabel = '／'.join(dfSumExit[dfSumExit['sum'] == sumExitMax][taikoColumn].tolist()[::-1])

    dfSumCount = dfNew[cond].groupby(taikoColumn).agg(
            sum=('days', 'sum'),
            count=('days', lambda x: ((x > 0) & (dfNew.loc[x.index, '缩写'] != 'CSS')).sum())
        ).reset_index()
    # 累计最大在轨日数
    sumDaysMax = int(dfSumCount['sum'].max()) 
    sumDaysMaxLabel = '／'.join(dfSumCount[dfSumCount['sum'] == sumDaysMax][taikoColumn].tolist()[::-1])
    # 累计最大在轨次数
    sumCountMax = dfSumCount['count'].max() 
    sumCountMaxLabel = '／'.join(dfSumCount[dfSumCount['count'] == sumCountMax][taikoColumn].tolist()[::-1])

    l1 = len(sumDaysMaxLabel)
    l2 = len(sumExitMaxLabel)
    l3 = len(sumCountMaxLabel)
    lMax = max(l1, l2, l3)
    sumDaysMaxLabel = sumDaysMaxLabel.ljust(lMax + ('(' in sumDaysMaxLabel), '　')
    sumExitMaxLabel = sumExitMaxLabel.ljust(lMax + ('(' in sumExitMaxLabel), '　') if sumExitMaxLabel else ''
    sumCountMaxLabel = sumCountMaxLabel.ljust(lMax + ('(' in sumCountMaxLabel), '　')
    persons = (str(len(set(dfSumCount['航天员'])))).ljust(2 * lMax)
    
    sumLabel = f'累计最多在轨{str(sumDaysMax).rjust(4)}日：{sumDaysMaxLabel}\n'
    sumLabel+= f'累计最多在轨{str(sumCountMax).rjust(4)}次：{sumCountMaxLabel}\n'
    sumLabel+= f'累计最多出舱{str(sumExitMax).rjust(4)}次：{sumExitMaxLabel}\n' if sumExitMaxLabel else ''
    sumLabel+= f'累计在轨航天员人数：{persons}'
    return sumLabel

################################################################################################
def plotShenzhouChartRaceAnimation(df, dfExit, plotStartYear='', days=30, plotLastFrames=True, use_pinyin=False):
    def barFunc(days, taiko, iDate):
        taikonaut = myPlot.get_nearest_taikonaut(df, iDate, taiko, use_pinyin)
        if int(days) == 0:
            barLabel =  getBarLabel(taikonaut, iDate, use_pinyin)
        else:
            # taikonaut = myPlot.get_nearest_taikonaut(df, iDate, taiko, use_pinyin)
            if len(taikonaut) == 0:
                barLabel = ''
            else:
                barLabel = getBarLabel(taikonaut, iDate, use_pinyin)        
        return barLabel

    def sumFunc(vals, ranks):
        iDate = vals.name
        cond = ((iDate >= df['发射日期']) & (iDate <= df['着陆日期'])) | (iDate >= df['着陆日期'])
        condExit = (iDate >= dfExit['出舱日期'])
        if cond.any():
            sumLabel = getSumLabel(df, dfExit, iDate, cond, condExit)
        else:
            sumLabel = ''
        return {'x': .975, 'y': .03, 's': sumLabel, 'ha': 'right', 'size': 10}

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
        plotYear = myDate.convertToDate(plotStartYear)
        dfWide = dfWide[dfWide.index>=plotYear]
        dfRank = dfRank[dfRank.index>=plotYear]
    myLogger.info(f'End parsing data to DataFrame')

    if use_pinyin:
        filename, title = 'videos\\ChinaTaikonautsOrbitBarChartRace.mp4', 'China Taikonauts Orbit Bar Chart Race (On-orbit Priority)'
    else:
        year = myDate.getThisYear()
        plotYear = f'至{year}年' if year else ''
        filename = f'videos\\{plotYear}中国航天员在轨动态条形图.mp4' if plotLastFrames else f'videos\\中国航天员在轨历史动态条形图.mp4'
        title = f'{plotYear}中国航天员在轨动态条形图(在轨优先)' if plotLastFrames else f'中国航天员在轨历史动态条形图(在轨优先)'
    
    count = len(dfWide.columns)
    title = title[:-1] + '前30)' if count > 30 else title
    myLogger.info(f'Start ploting bar char race: {filename}')
    myFile.createFolder(filename)
    periodTemplate = '%B %d, %Y' if use_pinyin else '%Y年%m月%d日'
    period_label={'x': .98, 'y': .25, 'ha': 'right', 'va': 'center'}
    fig_kwargs = {'figsize': (6, 3.375), 'dpi': 320}
    steps_per_period = 10
    frames = days * steps_per_period
    peopleCount = min(30, len(dfWide.columns))
    labelFontSize = 5 if peopleCount >= 30 else 6 if peopleCount >= 20 else 7
    print(f'航天员数: {len(dfWide.columns)}')

    bcr.bar_chart_race(dfWide, dfRank, 
        save_last_frame_image=True, plot_last_frames=plotLastFrames, last_frames_count=frames,
        save_frames_csv=False, incremental_plot=False, fig_kwargs=fig_kwargs, 
        title=title, filename=filename,interpolate_period=True, steps_per_period=steps_per_period,  
        tick_template=tickFunc, period_summary_func=sumFunc, bar_texttemplate=barFunc, 
        period_label=period_label, period_template=periodTemplate, filter_column_colors=True,
        tick_label_font=labelFontSize, bar_label_font=labelFontSize, n_bars=peopleCount)

    myLogger.info(f'End ploting bar char race: ---------------------------')

################################################################################################
def main():
    logFilename = f"{TEMP_FILE_PATH}{time.strftime('%Y%m%d-%H%M%S')}.log"
    myDate.setLogging(logFilename)
    myLogger = logging.getLogger('main')

    myLogger.info(f'Start: *****************************')
    myPlotInit.init(True)

    myLogger.info(f'Start reading data:')
    excelFile = f"{DATA_FILE_PATH}ChinaRocketLaunch.xlsx"
    sheetName = "乘组"
    plot3(excelFile, sheetName, '2024')

    sheetName = "发射纪录"
    df = myExcel.parseExcelSheetLaunch(excelFile, sheetName)
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