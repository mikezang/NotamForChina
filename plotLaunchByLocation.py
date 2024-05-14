
from timeit import timeit
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from sys import path
from datetime import datetime, timedelta
from openpyxl import load_workbook as loadXLSX
from matplotlib.lines import Line2D

path.append('./')

import constants
import myUtils
import myPlot

def parseExcelSheetToDataFrame(excelSheet, headers, startYear=None, endYear=None):
    # Convert data to list of lists
    data = []
    for row in excelSheet.iter_rows(values_only=True):
        data.append(list(row))

    df = pd.DataFrame(data[1:], columns=data[0]) # Convert list of lists to pandas dataframe
    df.columns = headers # Modify Hedaers
    df.replace('-', np.nan, inplace=True) # Replace '-' with NaN
    col = headers[0]

    if '年月' in col: 
        # Convert datetime to YYYYMM
        df[headers[0]] = [f'{d.year}{d.month:02d}' if isinstance(d, datetime) else d for d in df[col]] 
    elif '年' in col:
        # Convert datetime to YYYY
        df[headers[0]] = [d.year if isinstance(d, datetime) else d for d in df[col]] 
    return df

################################################################################################
def plotBarByMonthLocations(cn_font, ax, df, startYear, endYear=None):
    JanOfYear = f"{startYear}01"
    DecOfYear = f"{startYear}12"

    isYear = df['发射年月'].astype(str).str.startswith(str(startYear))
    isJan = df['发射年月'] <= JanOfYear
    isDec = df['发射年月'] <= DecOfYear

    df = df[isYear]
    dfYear = df.copy()
    if dfYear['发射年月'].count() == 12:
        dfYear = pd.concat([dfYear, df.tail(1)]) 
    dfYear['发射年月'].iloc[-1] = int(f'{startYear}13')
    dfYear['发射年月'] = dfYear['发射年月'].astype(int)

    # Set y axis
    yTicks = myPlot.getLogList(max(dfYear['合计长征发射数']) + 1)
    ax.set(yscale='log')
    ax.set_yticks(yTicks)
    ax.set_ylabel('发射数', fontproperties=cn_font, loc='top')
    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%d'))
    ax.set_ylim(0.5, yTicks[-1])
    myPlot.hideYTicks(ax, yTicks)

    axRight = ax.twinx()
    axRight.set(yscale='log')
    axRight.set_yticks(yTicks)
    axRight.set_ylabel('发射数', fontproperties=cn_font, loc='top')
    axRight.yaxis.set_major_formatter(mtick.FormatStrFormatter('%d'))
    axRight.set_ylim(ax.get_ylim())
    myPlot.hideYTicks(axRight, yTicks)

    # Plot CZ Bar graph on subplot
    colorJQ = myUtils.getColorFromKml(constants.COLOR_JIUQUAN)
    colorTY = myUtils.getColorFromKml(constants.COLOR_TAIYUAN)
    colorXC = myUtils.getColorFromKml(constants.COLOR_XICHANG)
    colorWC = myUtils.getColorFromKml(constants.COLOR_WENCHANG)
    colorHS = myUtils.getColorFromKml(constants.COLOR_SEA)

    barWidth = 0.4
    gap = 0.2
    dfHaishang = dfYear['海上长征发射数']
    dfWenchang = dfYear['文昌长征发射数']
    dfXichang = dfYear['西昌长征发射数']
    dfTaiyuan = dfYear['太原长征发射数']
    dfJiuquan = dfYear['酒泉长征发射数']
    czSumList = [sum(list(dfJiuquan[:-1])), sum(list(dfTaiyuan[:-1])), sum(list(dfXichang[:-1])), sum(list(dfWenchang[:-1])), sum(list(dfHaishang[:-1]))]

    bar1 = ax.bar(dfYear['发射年月'] + gap, dfHaishang, color=colorHS, edgecolor='k', width=barWidth)
    myPlot.plotTextOnCenterOfBars(ax, bar1, list(dfHaishang))

    bottom1 = dfHaishang
    bar2 = ax.bar(dfYear['发射年月'] + gap, dfWenchang, color=colorWC, edgecolor='k', width=barWidth, bottom=bottom1)
    myPlot.plotTextOnCenterOfBars(ax, bar2, list(dfWenchang))

    bottom1 += dfWenchang
    bar3 = ax.bar(dfYear['发射年月'] + gap, dfXichang, color=colorXC, edgecolor='k', width=barWidth, bottom=bottom1)
    myPlot.plotTextOnCenterOfBars(ax, bar3, list(dfXichang))

    bottom1 += dfXichang
    bar4 = ax.bar(dfYear['发射年月'] + gap, dfTaiyuan, color=colorTY, edgecolor='k', width=barWidth, bottom=bottom1)
    myPlot.plotTextOnCenterOfBars(ax, bar4, list(dfTaiyuan))

    bottom1 += dfTaiyuan
    bar5 = ax.bar(dfYear['发射年月'] + gap, dfJiuquan, color=colorJQ, edgecolor='k', width=barWidth, bottom=bottom1)
    myPlot.plotTextOnCenterOfBars(ax, bar5, list(dfJiuquan))

    bottom1 += dfJiuquan
    valueList1 = list(bottom1)
    myPlot.plotTextOnTopOfBars(ax, bar5, valueList1)

    # Plot non-CZ
    dfHaishang = dfYear['海上其他发射数']
    dfWenchang = dfYear['文昌其他发射数']
    dfXichang = dfYear['西昌其他发射数']
    dfTaiyuan = dfYear['太原其他发射数']
    dfJiuquan = dfYear['酒泉其他发射数']
    nczSumList = [sum(list(dfJiuquan[:-1])), sum(list(dfTaiyuan[:-1])), sum(list(dfXichang[:-1])), sum(list(dfWenchang[:-1])), sum(list(dfHaishang[:-1]))]

    bar1 = ax.bar(dfYear['发射年月'] - gap, dfHaishang, color=colorHS, edgecolor='k', width=barWidth)
    myPlot.plotTextOnCenterOfBars(ax, bar1, list(dfHaishang))

    bottom2 = dfHaishang
    bar2 = ax.bar(dfYear['发射年月'] - gap, dfWenchang, color=colorWC, edgecolor='k', width=barWidth, bottom=bottom2)
    myPlot.plotTextOnCenterOfBars(ax, bar2, list(dfWenchang))

    bottom2 += dfWenchang
    bar3 = ax.bar(dfYear['发射年月'] - gap, dfXichang, color=colorXC, edgecolor='k', width=barWidth, bottom=bottom2)
    myPlot.plotTextOnCenterOfBars(ax, bar3, list(dfXichang))

    bottom2 += dfXichang
    bar4 = ax.bar(dfYear['发射年月'] - gap, dfTaiyuan, color=colorTY, edgecolor='k', width=barWidth, bottom=bottom2)
    myPlot.plotTextOnCenterOfBars(ax, bar4, list(dfTaiyuan))

    bottom2 += dfTaiyuan
    bar5 = ax.bar(dfYear['发射年月'] - gap, dfJiuquan, color=colorJQ, edgecolor='k', width=barWidth, bottom=bottom2)
    myPlot.plotTextOnCenterOfBars(ax, bar5, list(dfJiuquan))

    bottom2 += dfJiuquan
    valueList2 = list(bottom2)
    myPlot.plotTextOnTopOfBars(ax, bar5, valueList2)

    # Set x axis
    ax.set_xlabel('发射月', fontproperties=cn_font)
    xTicks = list(dfYear['发射年月'])
    ax.set_xticks(xTicks)
    xTickLabels = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月', '合计']
    ax.set_xticklabels(xTickLabels, fontproperties=cn_font, fontsize=14)
    ax.set_xlim(float(f'{startYear}00.5'), float(f'{startYear}13.5'))

    for pos in xTicks:
        ax.axvline(pos + 0.5, color='black', linestyle='--')

    return czSumList, nczSumList

################################################################################################
def plotBarByLocations(cn_font, axLeft, df):
    # Set y axis
    yTicks = myPlot.getLogList(max(df['全部发射数']))
    myPlot.setYAxisLog(cn_font, axLeft, yTicks)
    axRight = axLeft.twinx()
    myPlot.setYAxisLog(cn_font, axRight, yTicks)

    # # Set x axis
    xTickLabels = list(df['地点'])
    barWidth = 0.3
    xTicks1 = [i + 1 - barWidth for i in range(0, len(xTickLabels))]
    xTicks2 = [i + 1 for i in range(0, len(xTickLabels))]
    xTicks3 = [i + 1 + barWidth for i in range(0, len(xTickLabels))]
    axLeft.set_xlabel('发射地', fontproperties=cn_font)
    axLeft.set_xticks(xTicks2)
    axLeft.set_xticklabels(xTickLabels, fontproperties=cn_font, fontsize=14)

    dfAll, dfAllOk, dfAllNg = df['全部发射数'], df['全部成功数'], df['全部发射数'] - df['全部成功数']
    dfCZ, dfCZOk, czCZNg = df['长征发射数'], df['长征成功数'], df['长征发射数'] - df['长征成功数']
    dfNCZ, dfNCZOk, czNCZNg = df['其他发射数'], df['其他成功数'], df['其他发射数'] - df['其他成功数']
    dfAllRate, dfCZRate, dfNCZRate = df['全部成功率'], df['长征成功率'], df['其他成功率']

    bar1 = axRight.bar(xTicks1, dfNCZOk, color='blue', edgecolor='k', width=barWidth)
    bar2 = axRight.bar(xTicks1, czNCZNg, color='red', edgecolor='k', width=barWidth, bottom=dfNCZOk)
    myPlot.plotTextOnCenterOfBars(axRight, bar1, list(dfNCZOk))
    myPlot.plotTextOnTopOfBars(axRight, bar2, list(dfNCZ))

    bar1 = axRight.bar(xTicks2, dfCZOk, color='green', edgecolor='k', width=barWidth)
    bar2 = axRight.bar(xTicks2, czCZNg, color='red', edgecolor='k', width=barWidth, bottom=dfCZOk)
    myPlot.plotTextOnCenterOfBars(axRight, bar1, list(dfCZOk))
    myPlot.plotTextOnTopOfBars(axRight, bar2, list(dfCZ))

    bar1 = axRight.bar(xTicks3, dfAllOk, color='orange', edgecolor='k', width=barWidth)
    bar2 = axRight.bar(xTicks3, dfAllNg, color='red', edgecolor='k', width=barWidth, bottom=dfAllOk)
    myPlot.plotTextOnCenterOfBars(axRight, bar1, list(dfAllOk))
    myPlot.plotTextOnTopOfBars(axRight, bar2, list(dfAll))

    for pos in xTicks3[:-1]:
        axRight.axvline(pos + 0.2, color='black', linestyle='--')

def plotTitleLegendByMonthLocations(cn_font, title, czSumList, nczSumList):
    colorJQ = myUtils.getColorFromKml(constants.COLOR_JIUQUAN)
    colorTY = myUtils.getColorFromKml(constants.COLOR_TAIYUAN)
    colorXC = myUtils.getColorFromKml(constants.COLOR_XICHANG)
    colorWC = myUtils.getColorFromKml(constants.COLOR_WENCHANG)
    colorHS = myUtils.getColorFromKml(constants.COLOR_SEA)
    nczTotal = sum(nczSumList)
    czTotal = sum(czSumList)
    handles = [
        Line2D([0], [0], linestyle='none', mfc=colorJQ, mec=colorJQ, marker='s', label=f'酒泉其他(左) x {nczSumList[0]}'),
        Line2D([0], [0], linestyle='none', mfc=colorJQ, mec=colorJQ, marker='s', label=f'酒泉长征(右) x {czSumList[0]}'),
        Line2D([0], [0], linestyle='none', mfc=colorTY, mec=colorTY, marker='s', label=f'太原其他(左) x {nczSumList[1]}'),
        Line2D([0], [0], linestyle='none', mfc=colorTY, mec=colorTY, marker='s', label=f'太原长征(右) x {czSumList[1]}'),
        Line2D([0], [0], linestyle='none', mfc=colorXC, mec=colorXC, marker='s', label=f'西昌其他(左) x {nczSumList[2]}'),
        Line2D([0], [0], linestyle='none', mfc=colorXC, mec=colorXC, marker='s', label=f'西昌长征(右) x {czSumList[2]}'),
        Line2D([0], [0], linestyle='none', mfc=colorWC, mec=colorWC, marker='s', label=f'文昌其他(左) x {nczSumList[3]}'),
        Line2D([0], [0], linestyle='none', mfc=colorWC, mec=colorWC, marker='s', label=f'文昌长征(右) x {czSumList[3]}'),
        Line2D([0], [0], linestyle='none', mfc=colorHS, mec=colorHS, marker='s', label=f'海上其他(左) x {nczSumList[4]}'),
        Line2D([0], [0], linestyle='none', mfc=colorHS, mec=colorHS, marker='s', label=f'海上长征(右) x {czSumList[4]}'),
        Line2D([0], [0], linestyle='none', mfc='w', mec='b', marker='s', label=f'其他合计(左) = {nczTotal}'),
        Line2D([0], [0], linestyle='none', mfc='w', mec='b', marker='s', label=f'长征合计(右) = {czTotal}'),
    ]
    plt.legend(handles=handles, loc='upper center', ncol=6, prop=cn_font)
    plt.title(title, fontproperties=cn_font, fontsize=18)

def plotTitleLegendByLocations(cn_font, title):
    handles = [
        Line2D([0], [0], linestyle='none', mfc='blue', mec='blue', marker='s', label=f'其他'),
        Line2D([0], [0], linestyle='none', mfc='green', mec='green', marker='s', label=f'长征'),
        Line2D([0], [0], linestyle='none', mfc='orange', mec='orange', marker='s', label=f'全部'),
        Line2D([0], [0], linestyle='none', mfc='red', mec='red', marker='s', label=f'失败'),
    ]
    plt.legend(handles=handles, loc='upper center', ncol=6, prop=cn_font)
    plt.title(title, fontproperties=cn_font, fontsize=18)

def plotGraphByMonthLocations(cn_font, excelSheet, title, startYear, endYear=None):
    headers = ['发射年月', 
               '酒泉长征发射数', '太原长征发射数', '海上长征发射数', '西昌长征发射数', '文昌长征发射数', '合计长征发射数',
               '酒泉其他发射数', '太原其他发射数', '海上其他发射数', '西昌其他发射数', '文昌其他发射数', '合计其他发射数',
               '酒泉发射数', '太原发射数', '海上发射数', '西昌发射数', '文昌发射数', '合计发射数', '月合计发射数']
    df = parseExcelSheetToDataFrame(excelSheet, headers)
    # fig, axLeft = plt.subplots(nrows=1, ncols=1, figsize=(20, 10))
    fig, axLeft =  myPlot.getFigure()
    czSumList, nczSumList = plotBarByMonthLocations(cn_font, axLeft, df, startYear) # Plot bar graph on right axis
    plotTitleLegendByMonthLocations(cn_font, title, czSumList, nczSumList) # plot legend
    myPlot.showBackend()
    myPlot.saveFig(fig, f'./images/年度别发射地统计/{title}.png')

def plotGraphByLocations(cn_font, df, title, startYear=None):
    df = myPlot.parseToDataFrame(df, rocket='', startYear=startYear, plotLocation=True)
    # fig, axLeft = plt.subplots(nrows=1, ncols=1, figsize=(20, 10))
    fig, axLeft =  myPlot.getFigure()
    plotBarByLocations(cn_font, axLeft, df) # Plot bar graph on right axis
    plotTitleLegendByLocations(cn_font, title) # plot legend
    myPlot.showBackend()
    path = f'./images/年度别发射地统计/{title}.png' if startYear else f'./images/{title}.png'
    myPlot.saveFig(fig, path)

def plot1(cn_font, excelSheet, startYears):
    for startYear in startYears:
        title = f'{startYear}中国运载火箭发射地统计'
        plotGraphByMonthLocations(cn_font, excelSheet, title, int(startYear))

def plot2(cn_font, df, startYear=None):
    title = f'{startYear}中国运载火箭发射地统计' if startYear else '中国全部运载火箭发射地统计'
    plotGraphByLocations(cn_font, df, title, startYear)

def main():
    cn_font = myPlot.init()
    excelFile = "./data/ChinaRocketLaunch.xlsx"
    sheetName = "发射纪录"
    df = myPlot.readDataFromSheetNew(excelFile, sheetName)
    # startYears = ['1970', '1971', '1972', '1973', '1974', '1975', '1976', '1977', '1978', '1979']
    # startYears += ['1980', '1981', '1982', '1983', '1984', '1985', '1986', '1987', '1988', '1989']
    # startYears += ['1990', '1991', '1992', '1993', '1994', '1995', '1996', '1997', '1998', '1999']
    # startYears += ['2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009']
    # startYears = ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019']
    # startYears += ['2020', '2021', '2022', '2023']
    startYears = ['2024']
    for startYear in startYears:
        plot2(cn_font, df, startYear)
    # sheetName2 = "发射地月間統計"
    # excelSheet2 = excelBook[sheetName2]
    # plot1(cn_font, excelSheet2, startYears)
    # plot2(cn_font, excelSheet1)

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')
    
if __name__ == "__main__":
    showRunTime("main()")