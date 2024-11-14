
from timeit import timeit
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from matplotlib.lines import Line2D

from myModules import myConst
from myModules import myFile
from myModules import myPlot
from myModules import myShape

DATA_FILE_PATH = './data/'

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

    for i in range(-1, len(xTicks3)):
        pos = xTicks3[0] - 2 * barWidth - 0.2 if i == -1 else xTicks3[i] + 0.2
        axRight.axvline(pos, color='black', linestyle='--')

################################################################################################
def plotTitleLegendByLocations(cn_font, title):
    handles = [
        Line2D([0], [0], linestyle='none', mfc='blue', mec='blue', marker='s', label=f'其他'),
        Line2D([0], [0], linestyle='none', mfc='green', mec='green', marker='s', label=f'长征'),
        Line2D([0], [0], linestyle='none', mfc='orange', mec='orange', marker='s', label=f'全部'),
        Line2D([0], [0], linestyle='none', mfc='red', mec='red', marker='s', label=f'失败'),
    ]
    plt.legend(handles=handles, loc='upper center', ncol=6, prop=cn_font)
    plt.title(title, fontproperties=cn_font, fontsize=18)

################################################################################################
def plotGraphByLocations(cn_font, df, title, startYear=None, rocket=None):
    if startYear:
        path = f'./images/年度别发射地统计/{title}.png'
    else:
        path = f'./images/{title}.png'        
    df = myPlot.parseToDataFrame(df, rocket=rocket, startYear=startYear, plotLocation=True)
    fig, axLeft =  myShape.getFigure()
    plotBarByLocations(cn_font, axLeft, df) # Plot bar graph on right axis
    plotTitleLegendByLocations(cn_font, title) # plot legend
    myPlot.showBackend()
    myPlot.saveFig(fig, path)

# def plot1(cn_font, excelSheet, startYears):
#     for startYear in startYears:
#         title = f'{startYear}中国运载火箭发射地统计'
#         plotGraphByMonthLocations(cn_font, excelSheet, title, int(startYear))

################################################################################################
def plot2(cn_font, df, startYear=None, seriesList=None):
    if startYear:
        title = f'{startYear}中国运载火箭发射地统计'
        plotGraphByLocations(cn_font, df, title, startYear, rocket='')
    else:
        for rocket in seriesList:
            if rocket not in '全部':
                continue
            title = f'中国{rocket}运载火箭发射地统计'
            plotGraphByLocations(cn_font, df, title, rocket=rocket)

################################################################################################
def main():
    cn_font = myPlot.init()
    excelFile = f"{DATA_FILE_PATH}ChinaRocketLaunch.xlsx"
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