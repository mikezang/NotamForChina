from timeit import timeit
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import sqrt
from datetime import timedelta
from matplotlib.lines import Line2D

from myModules import myPlot
from myModules import myShape
from myModules import myUtils

################################################################################################
def countDataFrameByRocket(df, retired_rockets):
    dfCopy = df[0].copy()

    # group by 火箭 and count the total occurrences of each 火箭
    dfTotal = dfCopy.groupby('火箭').size().reset_index(name='发射数') 

    # Get last value in the 日期 column to dfLastDates
    dfLastDates = dfCopy.groupby('火箭')['日期'].agg('last').reset_index()
                            
    # group by 火箭 and 结果, then count the occurrences where 结果 is '成功'
    dfOk = dfCopy[dfCopy['结果'] == '成功'].groupby('火箭').size().reset_index(name='成功数')

    # merge on 火箭 to get 成功数 and Total columns together
    dfResult = pd.merge(dfTotal, dfOk, on='火箭', how='left')

    # merge on 火箭 to get 日期 together
    dfResult = pd.merge(dfResult, dfLastDates, on='火箭', how='left')

    # fill NaN values in 成功数 column with 0 (occurs when 火箭 has no '成功' Result)
    dfResult['成功数'] = dfResult['成功数'].fillna(0)

    # add a new column 成功率 that is calculated by dividing 成功数 by 发射数
    dfResult['成功率'] = dfResult['成功数'] / dfResult['发射数']

    # convert 成功数 columns to integer
    dfResult['成功数'] = dfResult['成功数'].astype(int)

    # Get 失败数
    dfResult['失败数'] = dfResult['发射数'] - dfResult['成功数']

    # Create total sum row
    totalSum = dfResult['发射数'].sum()
    okSum = dfResult['成功数'].sum()
    ngSum = dfResult['失败数'].sum()
    rowTotal = {'火箭': '总计', '发射数': totalSum, '成功数': okSum, '成功率': okSum / totalSum, '失败数': ngSum}

    dfTotal = pd.DataFrame(rowTotal, index=[0])
    # print(dfTotal)

    dfResult = pd.concat([dfTotal, dfResult], ignore_index=True)
    # print(dfResult)

    # Sum CZ and non-CZ total
    dfCz = dfResult[dfResult['火箭'].astype(str).str.startswith('长征')]
    czTotalSum = dfCz['发射数'].sum()
    czOkSum = dfCz['成功数'].sum()
    czNgSum = dfCz['失败数'].sum()

    nczTotalSum = totalSum - czTotalSum
    nczOkSum = okSum - czOkSum
    nczNgSum = nczTotalSum - nczOkSum
    
    # Create rows
    rowCzTotal = {'火箭': '长征合计', '发射数': czTotalSum, '成功数': czOkSum, '成功率': czOkSum / czTotalSum, '失败数': czNgSum}
    rowNczTotal = {'火箭': '其他合计', '发射数': nczTotalSum, '成功数': nczOkSum, '成功率': nczOkSum / nczTotalSum if nczTotalSum > 0 else 0, '失败数': nczNgSum}

    # Create DataFrame
    dfCzTotal = pd.DataFrame(rowCzTotal, index=[0])
    dfNczTotal = pd.DataFrame(rowNczTotal, index=[0])

    # Concat two dfs to result df
    dfCzResult = pd.concat([dfCzTotal, dfResult], ignore_index=True)
    cz = dfCzResult['火箭'].str.startswith('长征')
    dfCzResult = dfCzResult[cz]
    dfNczResult = pd.concat([dfNczTotal, dfResult], ignore_index=True)
    ncz = ~dfNczResult['火箭'].str.startswith('长征')
    ncz &= ~dfNczResult['火箭'].str.startswith('总计')
    dfNczResult = dfNczResult[ncz]
    dfResult = pd.concat([dfCzTotal, dfResult], ignore_index=True)
    dfResult = pd.concat([dfNczTotal, dfResult], ignore_index=True)

    # Copy before sort
    dfSort = dfResult.copy()
    dfCzSort = dfCzResult.copy()
    dfNczSort = dfNczResult.copy()

    # create a new column that maps each row to either 长征组 or 其他组
    dfSort['长征分组'] = np.where(dfSort['火箭'].str.startswith(('总计', '长征')), '长征组', '其他组')
    dfCzSort['长征分组'] = np.where(dfCzSort['火箭'].str.startswith(('总计', '长征')), '长征组', '其他组')
    dfNczSort['长征分组'] = np.where(dfNczSort['火箭'].str.startswith(('总计', '长征')), '长征组', '其他组')

    # create a new column that maps each row to either 现役组 or 退役组
    dfSort['现役分组'] = np.where(dfSort['火箭'].isin(retired_rockets), '现役组', '退役组')
    dfCzSort['现役分组'] = np.where(dfCzSort['火箭'].isin(retired_rockets), '现役组', '退役组')
    dfNczSort['现役分组'] = np.where(dfNczSort['火箭'].isin(retired_rockets), '现役组', '退役组')

    # Sort 
    # dfSortResult = dfSort.sort_values(by=['分组', '发射数', '成功率', '火箭'], ascending=[True, True, True, True])
    # dfSortResult = dfSort.sort_values(by=['长征分组', '现役分组', '发射数', '成功率', '火箭'], ascending=[True, True,  True, True, True])
    dfSortResult1 = dfSort.sort_values(by=['长征分组', '现役分组', '发射数', '成功率', '日期'], ascending=[True, True,  True, True, False])
    dfCzSortResult1 = dfCzSort.sort_values(by=['长征分组', '现役分组', '发射数', '成功率', '日期'], ascending=[True, True,  True, True, False])
    dfNczSortResult1 = dfNczSort.sort_values(by=['长征分组', '现役分组', '发射数', '成功率', '日期'], ascending=[True, True,  True, True, False])

    # Sort by successful rate
    dfSortResult2 = dfSort.sort_values(by=['长征分组', '现役分组', '成功率', '发射数', '日期'], ascending=[True, True,  True, True, False])
    dfCzSortResult2 = dfCzSort.sort_values(by=['长征分组', '现役分组', '成功率', '发射数', '日期'], ascending=[True, True,  True, True, False])
    dfNczSortResult2 = dfNczSort.sort_values(by=['长征分组', '现役分组', '成功率', '发射数', '日期'], ascending=[True, True,  True, True, False])
    noSum = ~dfSortResult2['火箭'].str.contains('合计') & ~dfSortResult2['火箭'].str.contains('总计')
    noCzSum = ~dfCzSortResult2['火箭'].str.contains('合计') & ~dfCzSortResult2['火箭'].str.contains('总计')
    noNczSum = ~dfNczSortResult2['火箭'].str.contains('合计') & ~dfNczSortResult2['火箭'].str.contains('总计')
    dfSortResult2 = dfSortResult2[noSum]
    dfCzSortResult2 = dfCzSortResult2[noCzSum]
    dfNczSortResult2 = dfNczSortResult2[noNczSum]
    return [dfSortResult1, dfSortResult2, dfCzSortResult1, dfCzSortResult2, dfNczSortResult1, dfNczSortResult2]

################################################################################################
def plotLineGraphByRocket(cn_font, ax, df, retired_rockets, startYear):
    nameList, okRateList = list(df['火箭']), list(df['成功率'])
    xTickList = list(range(1, len(nameList) + 1))
    xLabel = '火箭系列'
    leftYLabel = '成功率'
    yMax = 1.05 if startYear == None else 1.10
    ax.plot(xTickList, okRateList, 'bo-', zorder=3)

    # Set y axis
    myPlot.plotLeftYAxis(cn_font, ax, leftYLabel, -0.05, yMax, True)
    hasGreyLabel = myPlot.plotXAxis(cn_font, ax, xLabel, xTickList, nameList, 0, len(xTickList) + 1, retired_rockets=retired_rockets)

    ax.set_zorder(4) # Set left axis to top
    ax.patch.set_visible(False) # set the patch of the left axes to be invisible

    return hasGreyLabel

################################################################################################
def plotBarGraphByRocket(cn_font, ax, df, startYear=None):
    nameList, okList, ngList, totalList = list(df['火箭']), list(df['成功数']), list(df['失败数']) , list(df['发射数'])
    xTickList = list(range(1, len(nameList) + 1))
    rightYLabel = '发射数'

    ax.bar(xTickList, okList, color='green', label=okList, zorder=1)
    ax.bar(xTickList, ngList, color='red', bottom=okList, label=ngList[0], zorder=1)
    ax.bar_label(ax.containers[1], fontsize=12, label_type='edge') 

    # Plot the y-axis values on middle of bar
    for rect, ok, ng in zip(ax.patches, okList, ngList):
        if ok > 0 and ok != ok + ng:
            x, y = rect.get_xy()
            w, h = rect.get_width(), rect.get_height()
            x += w / 2
            y += sqrt(h / 2) #+ log(0.5, 10)
            # y += max(sqrt(0.5), sqrt(h) + log(0.5, 10))
            fontsize = 10 if len(str(ok)) > 2 else 12
            ax.text(x, y, ok, color='w', fontsize=fontsize, horizontalalignment='center', verticalalignment='center')

    # Set y axis
    yTicks = myPlot.getLogList(max(totalList))
    myPlot.plotRightYAxis(cn_font, ax, rightYLabel, yTicks, fontsize=14, log=True)

################################################################################################
def plotTitleLegendByRocket(cn_font, title, hasGreyLabel=False):
    handles = [
        Line2D([0], [0], linestyle='solid', color='blue', label='成功率'),
        Line2D([0], [0], linestyle='none', mfc='green', mec='green', marker='s', label='成功数'),
        Line2D([0], [0], linestyle='none', mfc='red', mec='red', marker='s', label='失败数'),
    ]
    if hasGreyLabel:
        handles.append(Line2D([0], [0], linestyle='none', mfc='grey', mec='grey', marker='s', label='退役'))

    plt.legend(handles=handles, loc='upper center', ncol=4, prop=cn_font)
    plt.title(title, fontproperties=cn_font, fontsize=18)

def plotByRocket(cn_font, df, title, path, startYear):
    # fig, axLeft = plt.subplots(nrows=1, ncols=1, figsize=(20, 10)) 
    fig, axLeft =  myShape.getFigure()
    retiredRocketsDict = myUtils.readConfigRetiredDict() #constants.RETIRED_ROCKETS
    hasGreyLabel = plotLineGraphByRocket(cn_font, axLeft, df, retiredRocketsDict, startYear=startYear)
    axRight = axLeft.twinx()

    plotBarGraphByRocket(cn_font, axRight, df, startYear)
    plotTitleLegendByRocket(cn_font, title, hasGreyLabel)

    myPlot.showBackend()
    myPlot.saveFig(fig, f'./images/{path}{title}.png') # Save the plot to a file

################################################################################################
def plotGraphByRocket(cn_font, df, title, startYear=None, endYear=None, seriesList=None):
    retiredRocketsDict = myUtils.readConfigRetiredDict() #constants.RETIRED_ROCKETS
    df = myPlot.parseToDataFrame(df, columnYear='日期', columnNotNull='结果', startYear=startYear, endYear=endYear)
    df1, df2, dfCz1, dfCz2, dfNcz1, dfNcz2 = countDataFrameByRocket(df, retiredRocketsDict)
    title1 = myPlot.getPlotTitle(title.replace('发射统计', '发射数统计'), startYear, endYear)
    title2 = myPlot.getPlotTitle(title.replace('发射统计', '发射率统计'), startYear, endYear)
    path1 = '' if startYear == None else '火箭年发射数统计/'
    path2 = '' if startYear == None else '火箭年发射率统计/'

    if path1 == '':
        for series in seriesList:
            if series not in '全部,长征,其他':
                continue
            title1New = title1.replace('中国', f'中国{series}')
            title2New = title2.replace('中国', f'中国{series}')
            if series == '长征':
                df1New = dfCz1
                df2New = dfCz2
            elif series == '其他':
                df1New = dfNcz1
                df2New = dfNcz2
            else:
                df1New = df1
                df2New = df2
            plotByRocket(cn_font, df1New, title1New, path1, startYear)
            plotByRocket(cn_font, df2New, title2New, path1, startYear)
            # plotByRocket(cn_font, dfCz1, title1.replace('中国', '中国长征'), path1, startYear)
            # plotByRocket(cn_font, dfCz2, title2.replace('中国', '中国长征'), path1, startYear)
            # plotByRocket(cn_font, dfNcz1, title1.replace('中国', '中国其他'), path1, startYear)
            # plotByRocket(cn_font, dfNcz2, title2.replace('中国', '中国其他'), path1, startYear)
    else:
        plotByRocket(cn_font, df1, title1, path1, startYear)
        plotByRocket(cn_font, df2, title2, path2, startYear)

################################################################################################
def plot1(cn_font, df, startYear=None, seriesList=None):
    plotGraphByRocket(cn_font, df, '中国运载火箭发射统计', startYear, seriesList=seriesList)

################################################################################################
def main():
    cn_font = myPlot.init()
    excelFile = "./data/ChinaRocketLaunch.xlsx"
    sheetName = "发射纪录"
    df = myPlot.readDataFromSheetNew(excelFile, sheetName)
    startYear = '2024'
    if startYear:
        plot1(cn_font, df, startYear)
    else:
        plot1(cn_font, df)

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')
    
if __name__ == "__main__":
    showRunTime("main()")
