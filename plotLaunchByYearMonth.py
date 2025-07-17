from timeit import timeit
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from cn2an import an2cn
from datetime import datetime, timedelta
from matplotlib.lines import Line2D

from myModules import myPlot
from myModules import myShape
from myModules import myList
from myModules import myDate

DATA_FILE_PATH = './data/'

################################################################################################
def fillZero(dfListMerge, columns):
    for dfMerge in dfListMerge:
        for c in columns:
            dfMerge[c] = dfMerge[c].fillna(0)
            dfMerge[c] = dfMerge[c].astype(int)

################################################################################################
def insertNoDataYear(dfListMerge, years):
    dfListLast = []
    for dfMerge in dfListMerge:
        for y in years:
            dfMerge.loc[len(dfMerge)] = {'日期':y, '发射数':0, '长征发射数':0, '其他发射数':0, '成功数':0, '长征成功数':0, '其他成功数':0}
            dfSorted = dfMerge.sort_values('日期').reset_index()
        dfListLast.append(dfSorted)
    return dfListLast

################################################################################################
def countByYearMonthNew(dfFiltered, byYear):
    dfMerge = None
    if byYear:
        dfYearMonth = dfFiltered['日期'].dt.year
    else:
        dfYearMonth = dfFiltered['日期'].dt.strftime('%Y-%m')

    rockets = ['', '长征:长征', '其他:长征']
    locations = ['', '酒泉', '太原', '西昌', '文昌', '海上']
    isOk = dfFiltered['结果'] == '成功'

    for r in rockets:
        rs = r.split(':')
        if len(r) > 0:
            r0, r1 = rs
            if r0 == r1:
                isRocket = dfFiltered['火箭'].str.startswith(r1)
            else:
                isRocket = ~dfFiltered['火箭'].str.startswith(r1)
        else:
            r0 = r
            isRocket = True

        for l in locations:
            if l == '':
                isLoc = True
            else:
                isLoc = dfFiltered['地点'].str.startswith(l)

            dfTotal = dfFiltered[isRocket & isLoc].groupby(dfYearMonth).size().reset_index(name=f'{r0}{l}发射数')
            dfOk = dfFiltered[isOk & isRocket & isLoc].groupby(dfYearMonth).size().reset_index(name=f'{r0}{l}成功数')
            dfNg = dfTotal - dfOk

            if dfMerge is None:
                dfMerge = dfTotal
            else:
                dfMerge = pd.merge(dfMerge, dfTotal, on='日期', how='left')
    return dfMerge

################################################################################################
def countByMonth(dfListFiltered):
    dfListLast = []
    for dfFiltered in dfListFiltered:
        dfMonth = dfFiltered['日期'].dt.strftime('%m')

        isOk = dfFiltered['结果'] == '成功'
        isCz = dfFiltered['火箭'].str.startswith('长征')
        isNcz = ~dfFiltered['火箭'].str.startswith('长征')

        # Count by month
        dfTotalMonth = dfFiltered.groupby(dfMonth).size().reset_index(name='发射数')
        dfOkMonth = dfFiltered[isOk].groupby(dfMonth).size().reset_index(name='成功数')
        dfCzTotalMonth = dfFiltered[isCz].groupby(dfMonth).size().reset_index(name='长征发射数')
        dfCzOkMonth = dfFiltered[isOk & isCz].groupby(dfMonth).size().reset_index(name='长征成功数')
        dfNczTotalMonth = dfFiltered[isNcz].groupby(dfMonth).size().reset_index(name='其他发射数')
        dfNczOkMonth = dfFiltered[isOk & isNcz].groupby(dfMonth).size().reset_index(name='其他成功数')

        # merge on 日期 to get all columns above together
        dfMergeTotal = pd.merge(dfTotalMonth, dfCzTotalMonth, on='日期', how='left')
        dfMergeTotal = pd.merge(dfMergeTotal, dfNczTotalMonth, on='日期', how='left')
        dfMergeOk = pd.merge(dfOkMonth, dfCzOkMonth, on='日期', how='left')
        dfMergeOk = pd.merge(dfMergeOk, dfNczOkMonth, on='日期', how='left')
        dfMerge = pd.merge(dfMergeTotal, dfMergeOk, on='日期', how='left')
        dfListLast.append(dfMerge)
    return dfListLast

################################################################################################
def countByYearMonth(dfListFiltered, byYear):
    dfListLast = []
    for dfFiltered in dfListFiltered:
        if byYear:
            dfYearMonth = dfFiltered['日期'].dt.year
        else:
            dfYearMonth = dfFiltered['日期'].dt.strftime('%Y-%m')

        isOk = dfFiltered['结果'] == '成功'
        isCz = dfFiltered['火箭'].str.startswith('长征')
        isNcz = ~dfFiltered['火箭'].str.startswith('长征')

        # Count by year
        dfTotalYear = dfFiltered.groupby(dfYearMonth).size().reset_index(name='发射数')
        dfOkYear = dfFiltered[isOk].groupby(dfYearMonth).size().reset_index(name='成功数')
        dfCzTotalYear = dfFiltered[isCz].groupby(dfYearMonth).size().reset_index(name='长征发射数')
        dfCzOkYear = dfFiltered[isOk & isCz].groupby(dfYearMonth).size().reset_index(name='长征成功数')
        dfNczTotalYear = dfFiltered[isNcz].groupby(dfYearMonth).size().reset_index(name='其他发射数')
        dfNczOkYear = dfFiltered[isOk & isNcz].groupby(dfYearMonth).size().reset_index(name='其他成功数')

        # merge on 日期 to get all columns above together
        dfMergeTotal = pd.merge(dfTotalYear, dfCzTotalYear, on='日期', how='left')
        dfMergeTotal = pd.merge(dfMergeTotal, dfNczTotalYear, on='日期', how='left')
        dfMergeOk = pd.merge(dfOkYear, dfCzOkYear, on='日期', how='left')
        dfMergeOk = pd.merge(dfMergeOk, dfNczOkYear, on='日期', how='left')
        dfMerge = pd.merge(dfMergeTotal, dfMergeOk, on='日期', how='left')
        dfListLast.append(dfMerge)
    return dfListLast

################################################################################################
def cumul(dfListResult, columns):
    dfListLast = []
    for dfResult in dfListResult:
        for c in columns:
            dfResult[f'累计{c}'] = dfResult[c].cumsum()
        dfListLast.append(dfResult)
    return dfListLast

################################################################################################
def calcFaliure(dfListResult, columnsSubtrahend1, columnsSubtrahend2):
    # subtrahend, subtrahend, difference
    dfListLast = []
    for dfResult in dfListResult:
        for c1, c2 in zip(columnsSubtrahend1, columnsSubtrahend2):
            c = c2.replace('成功', '失败')
            dfResult[c] = dfResult[c1] - dfResult[c2]
        dfListLast.append(dfResult)
    return dfListLast

################################################################################################
def calcRate(dfListResult, columnsDividend, columnsDivisor):
    # divisor, dividend, quotient, product
    dfListLast = []
    for dfResult in dfListResult:
        for c1, c2 in zip(columnsDividend, columnsDivisor):
            c = c1.replace('数', '率')
            dfResult[c] = dfResult[c1] / dfResult[c2]
        dfListLast.append(dfResult)
    return dfListLast

################################################################################################
def sum(dfListResult, columns):
    dfListLast = []

    for dfResult in dfListResult:
        sum = []
        rowTotal = {'日期': '总计'}

        for i, c in enumerate(columns):
            sum[i] = dfResult[c].sum()
            rowTotal[c] = sum[i]
        # rowTotal = {'日期': '总计', 
        #             '发射数': sum[], '长征发射数': czTotalSum, '其他发射数': nczTotalSum,
        #             '成功数': okSum, '长征成功数': czOkSum, '其他成功数': nczOkSum,
        #             '失败数': ngSum, '长征失败数': czNgSum, '其他失败数': nczNgSum,
        #             '累计发射数': totalSums, '累计长征发射数': czTotalSums, '累计其他发射数': nczTotalSums,
        #             '累计成功数': okSums, '累计长征成功数': czOkSums, '累计其他成功数': nczOkSums,
        #             '累计失败数': ngSums, '累计长征失败数': czNgSums, '累计其他失败数': nczNgSums,
        #             '成功率': okSum / totalSum, '长征成功率': czOkSum / czTotalSum, '其他成功率': nczOkSum / nczTotalSum,
        #             '累计成功率': okSum / totalSum, '累计长征成功率': czOkSum / czTotalSum, '累计其他成功率': nczOkSum / nczTotalSum}

        dfLast = pd.concat([dfResult, pd.DataFrame(rowTotal, index=[0])], ignore_index=True)
        dfListLast.append(dfLast)
    return dfListLast

def calcRockets(dfListMerge):
    # fill NaN values and convert to integer
    columns = ['长征发射数', '其他发射数', '成功数', '长征成功数', '其他成功数']
    fillZero(dfListMerge, columns)
    dfListInserted = dfListMerge.copy()

    # Copy DataFrame
    dfListResult = dfListInserted.copy()

    # Calculate 失败数
    columnsSubtrahend1 = ['发射数', '长征发射数', '其他发射数']
    columnsSubtrahend2 = ['成功数', '长征成功数', '其他成功数']
    dfListResult = calcFaliure(dfListResult, columnsSubtrahend1, columnsSubtrahend2)

    # calculate the cumulative sum of rows
    columns = ['发射数', '长征发射数', '其他发射数', '成功数', '长征成功数', '其他成功数', '失败数', '长征失败数', '其他失败数']
    dfListResult = cumul(dfListResult, columns)

    # Calculate 成功率
    columnsDividend = ['成功数', '长征成功数', '其他成功数', '累计成功数', '累计长征成功数', '累计其他成功数']
    columnsDivisor = ['发射数', '长征发射数', '其他发射数', '累计发射数', '累计长征发射数', '累计其他发射数']
    dfListResult = calcRate(dfListResult, columnsDividend, columnsDivisor)

    # Concate total row as below
    # 总计: 发射数, 成功数, 失败数, 长征发射数, 长征成功数, 长征失败数, 其他发射数, 其他成功数, 其他失败数, 成功率. 长征成功率, 其他成功率
    columns = ['发射数', '长征发射数', '其他发射数', '成功数', '长征成功数', '其他成功数', 
               '失败数', '长征失败数', '其他失败数',
               '累计发射数', '累计长征发射数', '累计其他发射数', '累计成功数', '累计长征成功数', '累计其他成功数', 
               '累计失败数', '累计长征失败数', '累计其他失败数'
    ]

    dfListLast = []
    for df in dfListResult:
        # dfLast = sumDafatFrame(dfResult, columns)
        totalSum = df['发射数'].sum()
        czTotalSum = df['长征发射数'].sum()
        nczTotalSum = df['其他发射数'].sum()
        okSum = df['成功数'].sum()
        czOkSum = df['长征成功数'].sum()
        nczOkSum = df['其他成功数'].sum()
        ngSum = df['失败数'].sum()
        czNgSum = df['长征失败数'].sum()
        nczNgSum = df['其他失败数'].sum()

        # 累计
        totalSums = df['累计发射数'].sum()
        czTotalSums = df['累计长征发射数'].sum()
        nczTotalSums = df['累计其他发射数'].sum()
        okSums = df['累计成功数'].sum()
        czOkSums = df['累计长征成功数'].sum()
        nczOkSums = df['累计其他成功数'].sum()
        ngSums = df['累计失败数'].sum()
        czNgSums = df['累计长征失败数'].sum()
        nczNgSums = df['累计其他失败数'].sum()

        rowTotal = {'日期': '总计', 
                    '发射数': totalSum, '长征发射数': czTotalSum, '其他发射数': nczTotalSum,
                    '成功数': okSum, '长征成功数': czOkSum, '其他成功数': nczOkSum,
                    '失败数': ngSum, '长征失败数': czNgSum, '其他失败数': nczNgSum,
                    '累计发射数': totalSums, '累计长征发射数': czTotalSums, '累计其他发射数': nczTotalSums,
                    '累计成功数': okSums, '累计长征成功数': czOkSums, '累计其他成功数': nczOkSums,
                    '累计失败数': ngSums, '累计长征失败数': czNgSums, '累计其他失败数': nczNgSums,
                    '成功率': okSum / totalSum if totalSum > 0 else 0, 
                    '长征成功率': czOkSum / czTotalSum if czTotalSum > 0 else 0, 
                    '其他成功率': nczOkSum / nczTotalSum if nczTotalSum > 0 else 0,
                    '累计成功率': okSum / totalSums if totalSums > 0 else 0, 
                    '累计长征成功率': czOkSum / czTotalSums if czTotalSums > 0 else 0, 
                    '累计其他成功率': nczOkSum / nczTotalSums if nczTotalSums > 0 else 0}

        dfLast = pd.concat([df, pd.DataFrame(rowTotal, index=[0])], ignore_index=True)
        dfListLast.append(dfLast)
    return dfListLast

################################################################################################
def countDataFrameByMonth(dfList):
    dfListCopy = dfList.copy()
    dfListMerge = countByMonth(dfListCopy)
    dfListLast = calcRockets(dfListMerge)
    return dfListLast

################################################################################################
def countDataFrameByYearMonth(dfList, byYear=True, byLocation=False):
    dfListCopy = dfList.copy()

    dfListMerge = countByYearMonth(dfListCopy, byYear)

    # fill NaN values and convert to integer
    columns = ['长征发射数', '其他发射数', '成功数', '长征成功数', '其他成功数']
    fillZero(dfListMerge, columns)

    if byYear:
        years = [1972, 1977, 1980, 1989]
        dfListInserted = insertNoDataYear(dfListMerge, years)
    else:
        dfListInserted = dfListMerge.copy()

    # Copy DataFrame
    dfListResult = dfListInserted.copy()

    # Calculate 失败数
    columnsSubtrahend1 = ['发射数', '长征发射数', '其他发射数']
    columnsSubtrahend2 = ['成功数', '长征成功数', '其他成功数']
    dfListResult = calcFaliure(dfListResult, columnsSubtrahend1, columnsSubtrahend2)

    # calculate the cumulative sum of rows
    columns = ['发射数', '长征发射数', '其他发射数', '成功数', '长征成功数', '其他成功数', '失败数', '长征失败数', '其他失败数']
    dfListResult = cumul(dfListResult, columns)

    # Calculate 成功率
    columnsDividend = ['成功数', '长征成功数', '其他成功数', '累计成功数', '累计长征成功数', '累计其他成功数']
    columnsDivisor = ['发射数', '长征发射数', '其他发射数', '累计发射数', '累计长征发射数', '累计其他发射数']
    dfListResult = calcRate(dfListResult, columnsDividend, columnsDivisor)

    # Concate total row as below
    # 总计: 发射数, 成功数, 失败数, 长征发射数, 长征成功数, 长征失败数, 其他发射数, 其他成功数, 其他失败数, 成功率. 长征成功率, 其他成功率
    columns = ['发射数', '长征发射数', '其他发射数', '成功数', '长征成功数', '其他成功数', 
               '失败数', '长征失败数', '其他失败数',
               '累计发射数', '累计长征发射数', '累计其他发射数', '累计成功数', '累计长征成功数', '累计其他成功数', 
               '累计失败数', '累计长征失败数', '累计其他失败数'
    ]

    dfListLast = []
    for df in dfListResult:
        # dfLast = sumDafatFrame(dfResult, columns)
        totalSum = df['发射数'].sum()
        czTotalSum = df['长征发射数'].sum()
        nczTotalSum = df['其他发射数'].sum()
        okSum = df['成功数'].sum()
        czOkSum = df['长征成功数'].sum()
        nczOkSum = df['其他成功数'].sum()
        ngSum = df['失败数'].sum()
        czNgSum = df['长征失败数'].sum()
        nczNgSum = df['其他失败数'].sum()

        # 累计
        totalSums = df['累计发射数'].sum()
        czTotalSums = df['累计长征发射数'].sum()
        nczTotalSums = df['累计其他发射数'].sum()
        okSums = df['累计成功数'].sum()
        czOkSums = df['累计长征成功数'].sum()
        nczOkSums = df['累计其他成功数'].sum()
        ngSums = df['累计失败数'].sum()
        czNgSums = df['累计长征失败数'].sum()
        nczNgSums = df['累计其他失败数'].sum()

        rowTotal = {'日期': '总计', 
                    '发射数': totalSum, '长征发射数': czTotalSum, '其他发射数': nczTotalSum,
                    '成功数': okSum, '长征成功数': czOkSum, '其他成功数': nczOkSum,
                    '失败数': ngSum, '长征失败数': czNgSum, '其他失败数': nczNgSum,
                    '累计发射数': totalSums, '累计长征发射数': czTotalSums, '累计其他发射数': nczTotalSums,
                    '累计成功数': okSums, '累计长征成功数': czOkSums, '累计其他成功数': nczOkSums,
                    '累计失败数': ngSums, '累计长征失败数': czNgSums, '累计其他失败数': nczNgSums,
                    '成功率': okSum / totalSum if totalSum > 0 else 0, 
                    '长征成功率': czOkSum / czTotalSum if czTotalSum > 0 else 0, 
                    '其他成功率': nczOkSum / nczTotalSum if nczTotalSum > 0 else 0,
                    '累计成功率': okSum / totalSums if totalSums > 0 else 0, 
                    '累计长征成功率': czOkSum / czTotalSums if czTotalSums > 0 else 0, 
                    '累计其他成功率': nczOkSum / nczTotalSums if nczTotalSums > 0 else 0}

        dfLast = pd.concat([df, pd.DataFrame(rowTotal, index=[0])], ignore_index=True)
        dfListLast.append(dfLast)
    return dfListLast

################################################################################################
def plotLineGraphByMonthOld(cn_font, ax, dfList, rocketType=''):
    yearList, okRateList, okRatesList = [], [], []
    for df in dfList:
        yearList.append(list(df['日期'].astype(str)))
        okRateList.append(list(df[f'{rocketType}成功率']))
        okRatesList.append(list(df[f'累计{rocketType}成功率']))
 
    xTickList = list(range(1, len(yearList[0]) + 1))
    leftYLabel = f'{rocketType}成功率'

    xLabel = '发射月'
    xTickLabels = [f'{an2cn(int(d))}月' if d.isdigit() else d for d in yearList[0]]
    
    colors = [['bo-', 'mx-'], ['go-', 'rx-']]
    for i, (okRate, okRates) in enumerate(zip(okRateList, okRatesList)):
        ax.plot(xTickList, okRate, colors[i][0], zorder=3)
        # ax.plot(xTickList[:-1], okRates[:-1], colors[i][1], zorder=3)

        for j, (xTick, ok, oks) in enumerate(zip(xTickList, okRate, okRates)):
            if ok > 0:
                # if xTick == xTickList[-2]:
                point = (xTick, ok)
                y = 5 if ok > okRate[j - 1] else -15
                color = 'black' if j < len(xTickList)-1 else 'white'
                ax.annotate(f"{ok * 100:.2f}%", xy=point, xytext=(-15, y), color=color, textcoords='offset points')
            # if oks > 0 and oks < 1:
            #     if xTick == xTickList[-2]:
            #         point = (xTick, oks)
            #         y = 5 if oks > okRates[j - 1] else -15
            #         ax.annotate(f"{oks * 100:.2f}%", xy=point, xytext=(-15, y), textcoords='offset points')

    # Set y axis
    myPlot.plotLeftYAxis(cn_font, ax, leftYLabel, -0.05, 1.10, True)

    # Set x Axis
    myPlot.plotXAxis(cn_font, ax, xLabel, xTickList, xTickLabels, 0, len(xTickList) + 1)

    ax.set_zorder(4) # Set left axis to top
    ax.patch.set_visible(False) # set the patch of the left axes to be invisible

################################################################################################
def plotLineGraphByTime(cn_font, ax, dfList, byMonth=True):
    rocketList = ['', '长征', '其他']
    yearList, okRateList, czOkRateList, nczOkRateList = [], [], [], []
    df = dfList[0]
    yearList.append(list(df['日期'].astype(str)))
    okRateList.append(list(df[f'{rocketList[0]}成功率']))
    czOkRateList.append(list(df[f'{rocketList[1]}成功率']))
    nczOkRateList.append(list(df[f'{rocketList[2]}成功率']))
 
    xTickList = list(range(1, len(yearList[0]) + 1))
    leftYLabel = f'成功率'
    xLabel = '发射月'
    if byMonth:
        xTickLabels = [f'{an2cn(int(d))}月' if d.isdigit() else d for d in yearList[0]]
    else:
        xTickLabels = [f'星期{an2cn(int(d))}' if d.isdigit() else d for d in yearList[0]]
        xTickLabels[-2] = '星期日'
    xTicks1 = [i + 0.7 for i in range(0, len(xTickList))]
    xTicks2 = [i + 1.0 for i in range(0, len(xTickList))]
    xTicks3 = [i + 1.3 for i in range(0, len(xTickList))]
    colors = [['bo-', 'mx-'], ['go-', 'rx-']]
    for (nczOkRate, czOkRate, okRate) in zip(nczOkRateList, czOkRateList, okRateList):
        # ax.plot(xTicks1, nczOkRate, 'blue', zorder=3)
        # ax.plot(xTicks2, czOkRate, 'green', zorder=3)
        ax.plot(xTicks3, okRate, 'orange', zorder=3)

        for j, (xTick1, ok1, xTick2, ok2, xTick3, ok3) in enumerate(zip(xTicks1, nczOkRate, xTicks2, czOkRate, xTicks3, okRate)):
            # if ok1 > 0:
            #     point = (xTick1, ok1)
            #     y = 5 if ok1 > nczOkRate[j - 1] else -15
            #     ax.annotate(f"{ok1 * 100:.2f}%", xy=point, xytext=(-15, y), color='black', textcoords='offset points')
            # if ok2 > 0:
            #     point = (xTick2, ok2)
            #     y = 5 if ok2 > czOkRate[j - 1] else -15
            #     ax.annotate(f"{ok2 * 100:.2f}%", xy=point, xytext=(-15, y), color='black', textcoords='offset points')
            if ok3 > 0:
                point = (xTick3, ok3)
                y = 5 if ok3> czOkRate[j - 1] else -15
                ax.annotate(f"{ok3 * 100:.2f}%", xy=point, xytext=(-15, y), color='black', textcoords='offset points')

    myPlot.plotLeftYAxis(cn_font, ax, leftYLabel, -0.05, 1.10, True)
    myPlot.plotXAxis(cn_font, ax, xLabel, xTickList, xTickLabels, 0, len(xTickList) + 1)

    ax.set_zorder(4) # Set left axis to top
    ax.patch.set_visible(False) # set the patch of the left axes to be invisible

################################################################################################
def plotLineGraphByYearMonth(cn_font, ax, dfList, startYear, rocketType='', byYear=True, mom=False):
    yearList, okRateList, okRatesList = [], [], []
    for df in dfList:
        yearList.append(list(df['日期'].astype(str)))
        okRateList.append(list(df[f'{rocketType}成功率']))
        okRatesList.append(list(df[f'累计{rocketType}成功率']))
 
    xTickList = list(range(1, len(yearList[0]) + 1))
    leftYLabel = f'{rocketType}成功率'

    if byYear:
        xLabel = '发射年'
        xTickLabels = yearList[0]
    else:
        xLabel = '发射月'
        xTickLabels = [f'{an2cn(int(d[5:]))}月' if d[5:].isdigit() else d for d in yearList[0]]
    
    if startYear == None:
        colors = [['bo-', 'mx-'], ['go-', 'rx-']]
        width = 0.2
        for i, (okRate, okRates) in enumerate(zip(okRateList, okRatesList)):
            ax.plot(xTickList, okRate, colors[i][0], zorder=3)
            ax.plot(xTickList[:-1], okRates[:-1], colors[i][1], zorder=3)

            for j, (xTick, ok, oks) in enumerate(zip(xTickList, okRate, okRates)):
                if ok > 0 and ok < 1:
                    if (not byYear and xTick != xTickList[-1]) or xTick == xTickList[-2]:
                        point = (xTick, ok)
                        y = 5 if ok > okRate[j - 1] else -15
                        ax.annotate(f"{ok * 100:.2f}%", xy=point, xytext=(-15, y), textcoords='offset points')
                if oks > 0 and oks < 1:
                    if (not byYear and xTick != xTickList[-1]) or xTick == xTickList[-2]:
                        point = (xTick, oks)
                        y = 5 if oks > okRates[j - 1] else -15
                        ax.annotate(f"{oks * 100:.2f}%", xy=point, xytext=(-15, y), textcoords='offset points')

    # Set y axis
    myPlot.plotLeftYAxis(cn_font, ax, leftYLabel, -0.05, 1.10, True)

    # Set x Axis
    myPlot.plotXAxis(cn_font, ax, xLabel, xTickList, xTickLabels, 0, len(xTickList) + 1, inVerticle=not mom)

    ax.set_zorder(4) # Set left axis to top
    ax.patch.set_visible(False) # set the patch of the left axes to be invisible

################################################################################################
def plotBarGraphByMonthOld(cn_font, ax, dfList, rocketType=''):
    nameList, totalList, okList, ngList = [], [], [], []
    for df in dfList:
        nameList.append(list(df['日期']))
        totalList.append(list(df[f'{rocketType}发射数']))
        okList.append(list(df[f'{rocketType}成功数']))
        ngList.append(list(df[f'{rocketType}失败数']))

    xTickList = list(range(1, len(nameList[0]) + 1))
    rightYLabel = f'{rocketType}发射数'

    for i, (xTick, ok, ng) in enumerate(zip(xTickList, okList[0], ngList[0])):
        bar1 = ax.bar(xTick, ok, color='green', label=ok, zorder=1)
        bar2 = ax.bar(xTick, ng, color='red', label=ng, zorder=1, bottom=ok)
        ax.bar_label(bar2, fontsize=12, label_type='edge')
        fontsize = 14
        myPlot.plotTextOnCenterOfBar(ax, bar1.patches[0], okList[0][i], ngList[0][i], fontsize)

        yTicks = myPlot.getLogList(max(totalList[0]))

    # Set y axis
    myPlot.plotRightYAxis(cn_font, ax, rightYLabel, yTicks, fontsize=14, log=True)

################################################################################################
def plotBarGraphByTime(cn_font, axLeft, dfList, byMonth=True):
    rocketList = ['', '长征', '其他']
    nameList, totalList, okList, ngList = [], [], [], []
    czTotalList, czOkList, czNgList = [], [], []
    nczTotalList, nczOkList, nczNgList = [], [], []
    df = dfList[0]
    nameList.append(list(df['日期']))

    totalList.append(list(df[f'{rocketList[0]}发射数']))
    okList.append(list(df[f'{rocketList[0]}成功数']))
    ngList.append(list(df[f'{rocketList[0]}失败数']))
    czTotalList.append(list(df[f'{rocketList[1]}发射数']))
    czOkList.append(list(df[f'{rocketList[1]}成功数']))
    czNgList.append(list(df[f'{rocketList[1]}失败数']))
    nczTotalList.append(list(df[f'{rocketList[2]}发射数']))
    nczOkList.append(list(df[f'{rocketList[2]}成功数']))
    nczNgList.append(list(df[f'{rocketList[2]}失败数']))

     # Set y axis
    # myPlot.plotRightYAxis(cn_font, axRight, rightYLabel, yTicks, fontsize=14, log=True)
    yTicks = myPlot.getLogList(max(totalList[0]) + 1)
    axRight = axLeft.twinx()
    myPlot.setYAxisLog(cn_font, axLeft, yTicks)
    myPlot.setYAxisLog(cn_font, axRight, yTicks)

    # Set x axis
    barWidth = 0.3
    xTickList = list(range(1, len(nameList[0]) + 1))
    xTicks1 = [i + 1 - barWidth for i in range(0, len(xTickList))]
    xTicks2 = [i + 1 for i in range(0, len(xTickList))]
    xTicks3 = [i + 1 + barWidth for i in range(0, len(xTickList))]

    if byMonth:
        xLabel = '发射月'
        xTickLabels = [f'{an2cn(int(d))}月' if d.isdigit() else d for d in nameList[0]]
    else:
        xLabel = '发射周'
        xTickLabels = [f'星期{an2cn(int(d))}' if d.isdigit() else d for d in nameList[0]]
        xTickLabels = ['星期日' if item == '星期七' else item for item in xTickLabels]
    myPlot.plotXAxis(cn_font, axLeft, xLabel, xTickList, xTickLabels, 0, len(xTickList) + 1, inVerticle=False)

    # Plot NCZ
    bar1 = axRight.bar(xTicks1, nczOkList[0], color='blue', edgecolor='k', width=barWidth, zorder=1)
    bar2 = axRight.bar(xTicks1, nczNgList[0], color='red', edgecolor='k', width=barWidth, zorder=1, bottom=nczOkList[0])
    myPlot.plotTextOnCenterOfBars(axRight, bar1, nczOkList[0], fontsize=12)
    axRight.bar_label(bar2, fontsize=12, label_type='edge')

    # Plot CZ
    bar1 = axRight.bar(xTicks2, czOkList[0], color='green', edgecolor='k', width=barWidth, zorder=1)
    bar2 = axRight.bar(xTicks2, czNgList[0], color='red', edgecolor='k', width=barWidth, zorder=1, bottom=czOkList[0])
    myPlot.plotTextOnCenterOfBars(axRight, bar1, czOkList[0], fontsize=12)
    axRight.bar_label(bar2, fontsize=12, label_type='edge')

    # Plot ALL
    bar1 = axRight.bar(xTicks3, okList[0], color='orange', edgecolor='k', width=barWidth, zorder=1)
    bar2 = axRight.bar(xTicks3, ngList[0], color='red', edgecolor='k', width=barWidth, zorder=1, bottom=okList[0])
    myPlot.plotTextOnCenterOfBars(axRight, bar1, okList[0], fontsize=12)
    axRight.bar_label(bar2, fontsize=12, label_type='edge')

    for i in range(-1, len(xTicks3)):
        pos = xTicks3[0] - 2 * barWidth - 0.2 if i == -1 else xTicks3[i] + 0.2
        axRight.axvline(pos, color='black', linestyle='--')

################################################################################################
def plotBarGraphByYearMonth(cn_font, ax, dfList, startYear, rocketType='', byYear=True, mom=False):
    nameList, totalList, okList, ngList = [], [], [], []
    for df in dfList:
        nameList.append(list(df['日期']))
        totalList.append(list(df[f'{rocketType}发射数']))
        okList.append(list(df[f'{rocketType}成功数']))
        ngList.append(list(df[f'{rocketType}失败数']))

    xTickList = list(range(1, len(nameList[0]) + 1))
    rightYLabel = f'{rocketType}发射数'

    if mom and int(startYear) > 1970:
        width = 0.2
        for i, (xTick, ok, ng) in enumerate(zip(xTickList, okList[0], ngList[0])):
            bar1 = ax.bar(xTick - width, ok, width=width * 2, color='blue', label=ok, zorder=1)
            bar2 = ax.bar(xTick - width, ng, width=width * 2, color='red', label=ng, zorder=1, bottom=ok)
            ax.bar_label(bar2, fontsize=12, label_type='edge') 
            myPlot.plotTextOnCenterOfBar(ax, bar1.patches[0], okList[0][i], ngList[0][i])

        for i, (xTick, ok, ng) in enumerate(zip(xTickList, okList[1], ngList[1])):
            bar1 = ax.bar(xTick + width, ok, width=width * 2, color='green', label=ok, zorder=1)
            bar2 = ax.bar(xTick + width, ng, width=width * 2, color='red', label=ng, zorder=1, bottom=ok)
            ax.bar_label(bar2, fontsize=12, label_type='edge') 
            myPlot.plotTextOnCenterOfBar(ax, bar1.patches[0], okList[1][i], ngList[1][i])

        yTicks = myPlot.getLogList(myList.maxOfLists(totalList))
    else:
        for i, (xTick, ok, ng) in enumerate(zip(xTickList, okList[0], ngList[0])):
            bar1 = ax.bar(xTick, ok, color='green', label=ok, zorder=1)
            bar2 = ax.bar(xTick, ng, color='red', label=ng, zorder=1, bottom=ok)
            ax.bar_label(bar2, fontsize=12, label_type='edge')
            fontsize = 8 if len(str(ok)) > 2 else 10
            myPlot.plotTextOnCenterOfBar(ax, bar1.patches[0], okList[0][i], ngList[0][i], fontsize)

        yTicks = myPlot.getLogList(max(totalList[0]))

    # Set y axis
    myPlot.plotRightYAxis(cn_font, ax, rightYLabel, yTicks, fontsize=14, log=True)

    # Plot verticle line
    if not byYear:
        myPlot.plotVLineBetweenYearsMonths(ax, nameList, yMin=-0.05, yMax=1, mustPlot=True)

################################################################################################
def plotTitleLegendByMonthOld(cn_font, title, rocketType=''):
    handles = [
        Line2D([0], [0], linestyle='solid', color='blue', marker='o', label=f'{rocketType}成功率'),
        # Line2D([0], [0], linestyle='solid', color='magenta', marker='x', label=f'{rocketType}累计成功率'),
        Line2D([0], [0], linestyle='none', mfc='green', mec='green', marker='s', label=f'{rocketType}成功数'),
        Line2D([0], [0], linestyle='none', mfc='red', mec='red', marker='s', label=f'{rocketType}失败数'),
    ]

    plt.legend(handles=handles, loc='upper center', ncol=3, prop=cn_font)
    plt.title(title, fontproperties=cn_font, fontsize=18)

################################################################################################
def plotTitleLegendByTime(cn_font, title, onlyTitle=False):
    if not onlyTitle:
        handles = [
            Line2D([0], [0], linestyle='none', mfc='blue', mec='blue', marker='s', label=f'其他'),
            Line2D([0], [0], linestyle='none', mfc='green', mec='green', marker='s', label=f'长征'),
            Line2D([0], [0], linestyle='none', mfc='orange', mec='orange', marker='s', label=f'全部'),
            Line2D([0], [0], linestyle='none', mfc='red', mec='red', marker='s', label=f'失败'),
        ]

        plt.legend(handles=handles, loc='upper center', ncol=4, prop=cn_font)
    plt.title(title, fontproperties=cn_font, fontsize=18)

################################################################################################
def plotTitleLegendByYearMonth(cn_font, title, hasGreyLabel=False, rocketType='', mom=False):
    if mom:
        handles = [
            # Line2D([0], [0], linestyle='solid', color='green', marker='o', label=f'{rocketType}成功率(今年)'),
            # Line2D([0], [0], linestyle='solid', color='red', marker='x', label=f'{rocketType}累计成功率(今年)'),
            # Line2D([0], [0], linestyle='solid', color='blue', marker='o', label=f'{rocketType}成功率(去年)'),
            # Line2D([0], [0], linestyle='solid', color='magenta', marker='x', label=f'{rocketType}累计成功率(去年)'),
            Line2D([0], [0], linestyle='none', mfc='green', mec='green', marker='s', label=f'{rocketType}成功数(今年)'),
            Line2D([0], [0], linestyle='none', mfc='blue', mec='blue', color='blue', marker='s', label=f'{rocketType}成功数(去年)'),
            Line2D([0], [0], linestyle='none', mfc='red', mec='red', color='red',  marker='s', label=f'{rocketType}失败数'),
            # Line2D([0], [0], linestyle='none', mfc='magenta', mec='magenta', marker='s', label=f'{rocketType}失败数(去年)'),
        ]
    else:
        handles = [
            Line2D([0], [0], linestyle='solid', color='blue', marker='o', label=f'{rocketType}成功率'),
            Line2D([0], [0], linestyle='solid', color='magenta', marker='x', label=f'{rocketType}累计成功率'),
            Line2D([0], [0], linestyle='none', mfc='green', mec='green', marker='s', label=f'{rocketType}成功数'),
            Line2D([0], [0], linestyle='none', mfc='red', mec='red', marker='s', label=f'{rocketType}失败数'),
        ]
    if hasGreyLabel:
        handles.append(Line2D([0], [0], linestyle='none', mfc='lightgrey', mec='lightgrey', marker='s', label='退役'))

    plt.legend(handles=handles, loc='upper center', ncol=3, prop=cn_font)
    plt.title(title, fontproperties=cn_font, fontsize=18)

################################################################################################
def plotLineGraphByYearMonthNew(cn_font, ax, dfList, startYear, rocketType=[]):
    yearList, okRateList, okRatesList = [], [], []
    df = dfList[0]
    for rt in rocketType:
        yearList.append(list(df['日期'].astype(str)))
        okRateList.append(list(df[f'{rt}成功率']))
        okRatesList.append(list(df[f'累计{rt}成功率']))
 
    xTickList = list(range(1, len(yearList[0]) + 1))
    leftYLabel = '成功率'

    xLabel = '发射月'
    xTickLabels = [f'{an2cn(int(d[5:]))}月' if d[5:].isdigit() else d for d in yearList[0]]

    # Set y axis
    myPlot.plotLeftYAxis(cn_font, ax, leftYLabel, -0.05, 1.10, True)

    # Set x Axis
    myPlot.plotXAxis(cn_font, ax, xLabel, xTickList, xTickLabels, 0, len(xTickList) + 1)

    ax.set_zorder(4) # Set left axis to top
    ax.patch.set_visible(False) # set the patch of the left axes to be invisible

################################################################################################
def plotBarGraphByYearMonthNew(cn_font, ax, dfList, startYear, rocketType='', byYear=False):
    nameList, totalList, okList, ngList = [], [], [], []
    df = dfList[0]
    for rt in rocketType:
        nameList.append(list(df['日期']))
        totalList.append(list(df[f'{rt}发射数']))
        okList.append(list(df[f'{rt}成功数']))
        ngList.append(list(df[f'{rt}失败数']))

    xTickList = list(range(1, len(nameList[0]) + 1))
    rightYLabel = '发射数'

    width = 0.3
    # allTotal, czTotal, nczTotal = totalList[0], totalList[1], totalList[2]
    allOk, czOk, nczOk = okList[0], okList[1], okList[2]
    allNg, czNg, nczNg = ngList[0], ngList[1], ngList[2]

    for j, xTick in enumerate(xTickList):
        bar1 = ax.bar(xTick - width, nczOk[j], color='green', edgecolor='black', label=nczOk[j], zorder=1, width=width)
        bar2 = ax.bar(xTick - width, nczNg[j], color='red', edgecolor='black', label=nczNg[j], zorder=1, bottom=nczOk[j], width=width)
        ax.bar_label(bar2, fontsize=12, label_type='edge')
        myPlot.plotTextOnCenterOfBar(ax, bar1.patches[0], nczOk[j], nczNg[j], color='black')

        bar1 = ax.bar(xTick, czOk[j], color='blue', edgecolor='black', label=czOk[j], zorder=1, width=width)
        bar2 = ax.bar(xTick, czNg[j], color='red', edgecolor='black', label=czNg[j], zorder=1, bottom=czOk[j], width=width)
        ax.bar_label(bar2, fontsize=12, label_type='edge')
        myPlot.plotTextOnCenterOfBar(ax, bar1.patches[0], czOk[j], czNg[j], color='black')

        bar1 = ax.bar(xTick + width, allOk[j], color='orange', edgecolor='black', label=allOk[j], zorder=1, width=width)
        bar2 = ax.bar(xTick + width, allNg[j], color='red', edgecolor='black', label=allNg[j], zorder=1, bottom=allOk[j], width=width)
        ax.bar_label(bar2, fontsize=12, label_type='edge')
        myPlot.plotTextOnCenterOfBar(ax, bar1.patches[0], allOk[j], allNg[j], color='black')

    yTicks = myPlot.getLogList(max(totalList[0]))

    # Set y axis
    myPlot.plotRightYAxis(cn_font, ax, rightYLabel, yTicks, fontsize=14, log=True)

    # Plot verticle line
    if not byYear:
        myPlot.plotVLineBetweenYearsMonths(ax, nameList, yMin=-0.05, yMax=1, mustPlot=True)

################################################################################################
def plotTitleLegendByYearMonthNew(cn_font, title, hasGreyLabel=False, rocketType=''):
    handles = [
        Line2D([0], [0], linestyle='none', mfc='green', mec='green', marker='s', label=f'其他成功数'),
        Line2D([0], [0], linestyle='none', mfc='blue', mec='blue', marker='s', label=f'长征成功数'),
        Line2D([0], [0], linestyle='none', mfc='orange', mec='orange', marker='s', label=f'成功数'),
        Line2D([0], [0], linestyle='none', mfc='red', mec='red', marker='s', label=f'失败数'),
    ]
    if hasGreyLabel:
        handles.append(Line2D([0], [0], linestyle='none', mfc='lightgrey', mec='lightgrey', marker='s', label='退役'))

    plt.legend(handles=handles, loc='upper center', ncol=4, prop=cn_font)
    plt.title(title, fontproperties=cn_font, fontsize=18)

# Plot data by week
################################################################################################
def countByWeek(dfListFiltered):
    dfListLast = []
    for dfFiltered in dfListFiltered:
        dfWeek = dfFiltered['日期'].dt.strftime('%w')
        dfWeek = dfWeek.replace('0', '7') 
        isOk = dfFiltered['结果'] == '成功'
        isCz = dfFiltered['火箭'].str.startswith('长征')
        isNcz = ~dfFiltered['火箭'].str.startswith('长征')

        # Count by week
        dfTotalWeek = dfFiltered.groupby(dfWeek).size().reset_index(name='发射数')
        dfOkWeek = dfFiltered[isOk].groupby(dfWeek).size().reset_index(name='成功数')
        dfCzTotalWeek = dfFiltered[isCz].groupby(dfWeek).size().reset_index(name='长征发射数')
        dfCzOkWeek = dfFiltered[isOk & isCz].groupby(dfWeek).size().reset_index(name='长征成功数')
        dfNczTotalWeek = dfFiltered[isNcz].groupby(dfWeek).size().reset_index(name='其他发射数')
        dfNczOkWeek = dfFiltered[isOk & isNcz].groupby(dfWeek).size().reset_index(name='其他成功数')

        # merge on 日期 to get all columns above together
        dfMergeTotal = pd.merge(dfTotalWeek, dfCzTotalWeek, on='日期', how='left')
        dfMergeTotal = pd.merge(dfMergeTotal, dfNczTotalWeek, on='日期', how='left')
        dfMergeOk = pd.merge(dfOkWeek, dfCzOkWeek, on='日期', how='left')
        dfMergeOk = pd.merge(dfMergeOk, dfNczOkWeek, on='日期', how='left')
        dfMerge = pd.merge(dfMergeTotal, dfMergeOk, on='日期', how='left')
        dfListLast.append(dfMerge)
    return dfListLast

################################################################################################
def countDataFrameByWeek(dfList):
    dfListCopy = dfList.copy()
    dfListMerge = countByWeek(dfListCopy)
    dfListLast = calcRockets(dfListMerge)
    return dfListLast

################################################################################################
def plotGraphByWeek(cn_font, df, title, startYear=None, rocketList=None):
    dfList = myPlot.parseToDataFrame(df, columnYear='日期', columnNotNull='结果', startYear=startYear)
    dfList = countDataFrameByWeek(dfList)
    if startYear:
        newTitle = myPlot.getPlotTitle(f'中国{title}', startYear)
        savePath = f'./images/年度别发射周统计/{newTitle}.png'
        # fig, axLeft = plt.subplots(nrows=1, ncols=1, figsize=(20, 10))
        fig, axLeft =  myShape.getFigure()
        # plotLineGraphByTime(cn_font, axLeft, dfList, False)
        plotBarGraphByTime(cn_font, axLeft, dfList, False)
        plotTitleLegendByTime(cn_font, newTitle)
        myPlot.showBackend()
        myPlot.saveFig(fig, f'{savePath}') 
    else:
        if '全部' in rocketList:
            newTitle = myPlot.getPlotTitle(f'中国全部{title}')
            savePath = f'./images/{newTitle}.png'
            # fig, axLeft = plt.subplots(nrows=1, ncols=1, figsize=(20, 10))
            fig, axLeft =  myShape.getFigure()
            # plotLineGraphByTime(cn_font, axLeft, dfList, False)
            plotBarGraphByTime(cn_font, axLeft, dfList, False)
            plotTitleLegendByTime(cn_font, newTitle)
            myPlot.showBackend()
            myPlot.saveFig(fig, f'{savePath}') 

################################################################################################
def plotGraphByMonth(cn_font, df, title, startYear=None, rocketList=None):
    dfList = myPlot.parseToDataFrame(df, columnYear='日期', columnNotNull='结果', startYear=startYear)
    dfList = countDataFrameByMonth(dfList)

    if startYear:
        newTitle = myPlot.getPlotTitle(f'中国{title}', startYear)
        savePath = f'./images/年度别发射月统计/{newTitle}.png'
        # fig, axLeft = plt.subplots(nrows=1, ncols=1, figsize=(20, 10))
        fig, axLeft =  myShape.getFigure()
        # newTitle = myPlot.getPlotTitle(f'中国全部{title}')
        # plotLineGraphByTime(cn_font, axLeft, dfList)
        plotBarGraphByTime(cn_font, axLeft, dfList)
        plotTitleLegendByTime(cn_font, newTitle)
        myPlot.showBackend()
        myPlot.saveFig(fig, f'{savePath}') 
    else:
        if '全部' in rocketList:
            newTitle = myPlot.getPlotTitle(f'中国全部{title}')
            savePath = f'./images/{newTitle}.png'
            # fig, axLeft = plt.subplots(nrows=1, ncols=1, figsize=(20, 10))
            fig, axLeft =  myShape.getFigure()
            # newTitle = myPlot.getPlotTitle(f'中国全部{title}')
            # plotLineGraphByTime(cn_font, axLeft, dfList)
            plotBarGraphByTime(cn_font, axLeft, dfList)
            plotTitleLegendByTime(cn_font, newTitle)
            myPlot.showBackend()
            myPlot.saveFig(fig, f'{savePath}') 

################################################################################################
def plotGraphByMonthMax(cn_font, df, title, rocketList):
    dfList = myPlot.parseToDataFrame(df, columnYear='日期', columnNotNull='结果', isMonthMax=True)

    if '全部' in rocketList:
        newTitle = myPlot.getPlotTitle(f'中国全部{title}')
        savePath = f'./images/{newTitle}.png'
        fig, axLeft =  myShape.getFigure()
        plotBarGraphByMonthMax(cn_font, axLeft, dfList)
        plotTitleLegendByTime(cn_font, newTitle, True)
        myPlot.showBackend()
        myPlot.saveFig(fig, f'{savePath}') 

################################################################################################
def plotBarGraphByMonthMax(cn_font, axLeft, dfList):
    df = dfList[0]
    yearList = list(df['year'])
    monthList = list(df['month'])
    totalList = list(df['总发射数'])
    maxList = list(df['最多发射数'])
    avgList = list(df['平均发射数'])
    launchList = list(df['有发射年数'])

     # Set y axis
    axRight = axLeft.twinx()
    axLeft.get_yaxis().set_visible(False)
    yTotalTicks = [1, 1.5, 2.0, 2.5, 3.0, 3.5, 5, 10, 50, 100, totalList[-1] + 30]
    myPlot.setYAxisLog(cn_font, axRight, yTotalTicks, '发射数')
    # yAvgTicks = [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, avgList[-1] + 1.5]
    # yMaxTicks = [1, 5, 10, maxList[-1] + 2]
    # myPlot.setYAxis(cn_font, axLeft, yAvgTicks, '平均发射数')

    # Set x axis
    barWidth = 0.3
    xTickList = list(range(1, len(yearList) + 1))
    xMaxTicks = [i + 1 + barWidth for i in range(0, len(xTickList))]
    xTotalTicks = [i + 1 for i in range(0, len(xTickList))]
    xAvgTicks = [i + 1 - barWidth for i in range(0, len(xTickList))]
    xTicks = [i + 1 for i in range(0, len(xTickList))]
    xLabel = '发射月'

    # xTickLabels = [f'{year}年\n{an2cn(int(month))}月' for year, month in zip(yearList, monthList)]
    xTickLabels = [f'{an2cn(int(month))}月' for month in monthList]
    myPlot.plotXAxis(cn_font, axLeft, xLabel, xTickList, xTickLabels, 0, len(xTickList) + 1, inVerticle=False)

    colors = [myPlot.getUnique20Colors(i) for i in range(0, 12)]
    xAvgLabels = [f'有发射{years}年平均' for years in launchList]
    xTotalLabels = [f'有发射{years}年总数' for years in launchList]
    xYearLabels = [f'{year}年最多' for year in yearList]

    barAvg = axRight.bar(xAvgTicks, avgList, color=colors, edgecolor='k', width=barWidth, zorder=1)
    axRight.bar_label(barAvg, fmt='%.01f', fontsize=10, label_type='edge')
    myPlot.plotTextInsideBars(cn_font, axRight, barAvg, xAvgLabels, fontsize=12, gap=0.06)

    barTotal = axRight.bar(xTotalTicks, totalList, color=colors, edgecolor='k', width=barWidth, zorder=1)
    axRight.bar_label(barTotal, fontsize=12, label_type='edge')
    myPlot.plotTextInsideBars(cn_font, axRight, barTotal, xTotalLabels, fontsize=12)

    barMax = axRight.bar(xMaxTicks, maxList, color=colors, edgecolor='k', width=barWidth, zorder=1)
    axRight.bar_label(barMax, fontsize=12, label_type='edge')
    myPlot.plotTextInsideBars(cn_font, axRight, barMax, xYearLabels, fontsize=12)

    x = np.array(xTicks)
    midpoints = (x[:-1] + x[1:]) / 2
    for pos in midpoints:
        axRight.axvline(pos, color='black', linestyle='--')

################################################################################################
def plotGraphByYearMonth(cn_font, df, title, startYear=None, endYear=None, byYear=True, mom=False, rocketList=[]):
    dfList = myPlot.parseToDataFrame(df, columnYear='日期', columnNotNull='结果', startYear=startYear, endYear=endYear, mom=mom)
    if startYear:
        byYear = False
    else:
        byYear = True

    prefix = '中国'
    dfList = countDataFrameByYearMonth(dfList, byYear)
    date = myDate.getJapanDate()
    thisMonth = f'{date[:4]}-{date[4:6]}'
    if len(dfList) > 1 and dfList[1].日期.iloc[-2] < thisMonth:
        dfTemp = dfList[1]
        rowThisMonth = dfTemp.iloc[-2].copy()
        rowThisMonth.iloc[0] = thisMonth
        rowThisMonth[1:] = 0
        newRow = pd.DataFrame([rowThisMonth])
        row = len(dfTemp) - 1
        dfLast = pd.concat([dfTemp.iloc[:row], newRow, dfTemp.iloc[row:]], ignore_index=True) 
        dfList[1] = dfLast
        
    if rocketList:
        rocketListNew = rocketList.copy()
        if '全部' in rocketListNew:
            rocketListNew[0] = ''
    else:
        rocketListNew = rocketList

    if ((mom and startYear[:4] == myDate.getThisYear()) or startYear == None):
        for rocket in rocketListNew:
            if rocket not in ',长征,其他':
                continue
            fig, axLeft =  myShape.getFigure()
            newTitle = myPlot.getPlotTitle(f'{prefix}{rocket}{title}', startYear, endYear, byYear=byYear, mom=mom)
            if startYear is None and '长征' not in newTitle and '其他' not in newTitle:
                newTitle = newTitle.replace('中国', '中国全部')
            plotLineGraphByYearMonth(cn_font, axLeft, dfList, startYear, rocketType=rocket, byYear=byYear, mom=mom)
            axRight = axLeft.twinx()
            plotBarGraphByYearMonth(cn_font, axRight, dfList, startYear, rocketType=rocket, byYear=byYear, mom=mom)
            plotTitleLegendByYearMonth(cn_font, newTitle, rocketType=rocket, mom=mom)

            myPlot.showBackend()
            path = '' if startYear == None else '年度别发射月统计/'
            myPlot.saveFig(fig, f'./images/{path}{newTitle}.png') 
    else:
        # fig, axLeft = plt.subplots(nrows=1, ncols=1, figsize=(20, 10))
        fig, axLeft =  myShape.getFigure()
        newTitle = myPlot.getPlotTitle(f'{prefix}{title}', startYear, endYear, byYear=byYear)

        plotLineGraphByYearMonthNew(cn_font, axLeft, dfList, startYear, rocketType=rocketListNew)
        axRight = axLeft.twinx()
        plotBarGraphByYearMonthNew(cn_font, axRight, dfList, startYear, rocketType=rocketListNew, byYear=byYear)
        plotTitleLegendByYearMonthNew(cn_font, newTitle, rocketType=rocketListNew)

        myPlot.showBackend()
        path = '' if startYear == None else '年度别发射月统计/'
        myPlot.saveFig(fig, f'./images/{path}{newTitle}.png') 

################################################################################################
def plot1(cn_font, df, years=None, seriesList=None):
    title1 = '运载火箭发射年统计'
    title2 = '运载火箭发射月统计'
    title3 = '运载火箭发射周统计'
    title4 = '运载火箭发射月最多平均统计'

    if years:
        for year in years:
            plotGraphByWeek(cn_font, df, title3, year)
            plotGraphByMonth(cn_font, df, title2, year)

        # for year in years:
            if year == myDate.getThisYear() and seriesList:
                today = datetime.today()
                startYYMMMM = f'{year}01'
                endYYMMMM = f'{year}12' if today.year < int(year) else f'{year}{today.strftime("%m")}'
                plotGraphByYearMonth(cn_font, df, title2, startYYMMMM, endYYMMMM, mom=True, rocketList=seriesList)
    elif seriesList:
        # TODO: split only recent 30 years
        plotGraphByYearMonth(cn_font, df, title1, rocketList=seriesList)
        plotGraphByMonth(cn_font, df, title2, rocketList=seriesList)
        plotGraphByMonthMax(cn_font, df, title4, rocketList=seriesList)
        plotGraphByWeek(cn_font, df, title3, rocketList=seriesList)


################################################################################################
def main():
    cn_font = myPlot.init()
    excelFile = f"{DATA_FILE_PATH}ChinaRocketLaunch.xlsx"
    sheetName = "发射纪录"
    df = myPlot.readDataFromSheetNew(excelFile, sheetName)
    years =  ['2024', '2023', '2022', '2021', '2020']
    years += ['2019', '2018', '2017', '2016', '2015', '2014', '2013', '2012', '2011', '2010']
    years += ['2009', '2008', '2007', '2006', '2005', '2004', '2003', '2002', '2001', '2000']
    years += ['1999', '1998', '1997', '1996', '1995', '1994', '1993', '1992', '1991', '1990']
    years = ['2024']
    plot1(cn_font, df, years)
    # plot1(cn_font, excelSheet, years)
    # title1 = '运载火箭发射月统计'
    # plotGraphByMonth(cn_font, excelSheet, title1)
    # plotGraphByMonth(cn_font, excelSheet, title1, years[0])
    # title2 = '运载火箭发射周统计'
    # plotGraphByWeek(cn_font, excelSheet, title2, years[0])
    # plotGraphByWeek(cn_font, excelSheet, title2)

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')
    
if __name__ == "__main__":
    showRunTime("main()")
