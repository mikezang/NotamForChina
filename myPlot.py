# import cmath
# import textwrap
import random
import numpy as np
import pandas as pd
# import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
# import matplotlib.dates as mdates
# import matplotlib.patches as mpatches
from math import log, sqrt
import matplotlib.font_manager as fm
# from cn2an import an2cn
from os import walk#, path
from datetime import datetime
from openpyxl import load_workbook as loadXLSX
import pyexcel as xls
# from matplotlib.lines import Line2D
# from matplotlib.ticker import ScalarFormatter
from fiona.drvsupport import supported_drivers
from shapely.geometry import Polygon, LineString #, Point
import matplotlib.colors as mcolors

import constants
import myUtils

################################################################################################
def get_nearest_row(df, dateIndex):
    try:
        # Try to retrieve the exact row
        return df.loc[dateIndex]
    except KeyError:
        # If the exact date is not found, find the nearest date
        nearest_index = min(df.index, key=lambda x: abs(x - pd.Timestamp(dateIndex)))
        return df.loc[nearest_index]

################################################################################################
def get_nearest_indices(df, date_index):
    try:
        # Try to retrieve the exact index
        nearest_index = df.index.get_loc(date_index)
    except KeyError:
        # If the exact date is not found, find the nearest indices
        nearest_index = get_nearest_row(df, date_index)

    # Determine the indices before and after the target date
    if nearest_index > 0:
        index_before = df.index[nearest_index - 1]
    else:
        index_before = None  # No index before the target date
    if nearest_index < len(df.index) - 1:
        index_after = df.index[nearest_index + 1]
    else:
        index_after = None  # No index after the target date
    return index_before, index_after

################################################################################################
def parseFloatToTwoInt(f):
    if int(f) > 0:
        vals = str(f).split('.') 
        valAll = int(vals[0])
        n = 10 ** (3 - len(vals[1]))
        valOk = int(vals[1]) if n == 1 else int(vals[1]) * n 
        return valAll, valOk
    else:
        return 0, 0

################################################################################################
def init(setDefaultFont=False):
    # Reset the rcParams to their default values
    mpl.rcParams.update(mpl.rcParamsDefault)

    # Set the Chinese font
    if myUtils.isWindows():
        font_path = 'C:/Windows/Fonts/simhei.ttf'
    elif myUtils.isLinux():
        font_path = '//usr//share//fonts//truetype//wqy//wqy-microhei.ttc'
    elif myUtils.isMacOS():
        font_path = '//usr//local//share//fonts//truetype//SimHei.ttf'
    cn_font = fm.FontProperties(fname=font_path)

    if setDefaultFont:
        # mpl.rcParams['font.family'] = 'FangSong'
        # mpl.rcParams['font.family'] = 'SimHei'
        mpl.rcParams['font.family'] = cn_font.get_name()
    # enable the read and write functionalities for KML-driver
    # by passing 'rw' to whitelist of fiona’s supported drivers:
    supported_drivers['KML'] = 'rw'

    return cn_font

################################################################################################
def show():
    # print(plt.get_backend())
    if plt.get_backend() not in ['agg', 'TkAgg', 'GTK3Agg', 'MacOSX']:
        plt.show()

################################################################################################
def saveFig(fig, filename, isPrint=True):
    myUtils.createFolder(filename)
    if isPrint:
        print(f'Save to file: {filename}')
    fig.savefig(filename, bbox_inches='tight', pad_inches=0, dpi=250)
    plt.close(fig)

################################################################################################
# Insert '\n' after every character
def insertLf(oldList, toChinese=True):
    newList = [
        "".join(
            c if c == "\n" or (i != len(s) - 1 and s[i + 1] == "\n") else c +
            "\n" for i, c in enumerate(s))[:-1] for s in oldList
    ]
    return newList

################################################################################################
def getPlotTitle(titleBase, startYear=None, endYear=None, byYear=True, mom=False, retired=False, nodate=False):
    title = f'{titleBase}'
    year = ''
    plotDate = datetime.today().strftime("%Y年%m月%d日")

    if startYear != None:
        year = f'{startYear[:4]}'
    
    if endYear != None:
        if endYear[:4] != startYear[:4]:
            year += f'～{endYear[:4]}'
    
    #     if len(endYear) == 4:
    #         if f'{endYear}年12月31日' >= plotDate:
    #             title += f'(截止{plotDate})'
    #     elif len(endYear) == 6:
    #         y, m, d = endYear[:4], endYear[4:], myUtils.getLastdayOfMonth(endYear[:4], endYear[4:])
    #         if f'{y}年{m}月{d}日' >= plotDate:
    #             title += f'(截止{plotDate})'
    # else:
    #     if (startYear == None or f'{startYear}年12月31日' >= plotDate) and (retired != True and nodate != True):
    #         title += f'(截止{plotDate})'

    if mom:
        title = f'{title}（去年同期比）'
    if year:
        title = f'{year}{title}'
    
    return title

def logarithmic_middle(lower_bound, upper_bound, base=10):
    log_lower = log(lower_bound, base)
    log_upper = log(upper_bound, base)
    log_middle = (log_lower + log_upper) / 2
    middle_value = base ** log_middle
    return middle_value

def get_rgb(color):
    r,  g, b = mcolors.to_rgb(mcolors.CSS4_COLORS[color])
    return r, g, b

def convert_to_rgb(color):
    if isinstance(color, tuple) and len(color) == 3:
        rgb = [c * 255 if c <= 1 else c for c in color]
        return rgb  # Already in (255, 0, 0) format
    elif isinstance(color, list) and len(color) == 3:
        rgb = [c * 255 if c <= 1 else c for c in color]
        return tuple(rgb)  # Convert list to tuple
    else:
        try:
            rgb = mcolors.to_rgb(color)
            # rgb = int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
            rgb = [c * 255 if c <= 1 else c for c in rgb]
            return rgb
        except ValueError:
            return color

def get_luminance(rgb):
    # r, g, b = color if isinstance(color, list) or isinstance(color, tuple) else get_rgb(color)
    return rgb[0] * 255 * 0.2126 + rgb[1] * 255 * 0.7152 + rgb[2] * 255 * 0.0722
    # return rgb[0] * 0.2126 * 255 + rgb[1] * 0.7152 * 255 + rgb[2] * 0.0722 * 255

def maxContrastColor(color, bw=False):
    r, g, b = convert_to_rgb(color)
    if bw:
        luminance = r * 0.2126 + g * 0.7152 + b * 0.0722
        return '#000000' if luminance > 140 else '#FFFFFF'
    else:
        return f"#{int(255 - r):02X}{int(255 - g):02X}{int(255 - b):02X}"

def invertColor(color, bw=False):
    r, g, b = convert_to_rgb(color)
    if bw: # https://stackoverflow.com/a/3943023/112731
        luminance = r * 0.2990 + g * 0.5870 + b * 0.1140
        return '#000000' if luminance > 186 else '#FFFFFF'
    else:
        return f"#{int(255 - r):02X}{int(255 - g):02X}{int(255 - b):02X}"
    
################################################################################################
def plotTextOnTopOfBars(ax, bar, okList, fontsize=12):
    ax.bar_label(bar, labels=okList, label_type='edge', fontsize=fontsize)

################################################################################################
def plotTextOnCenterOfBars(ax, bar, okList, fontsize=12, color=None):
    barColor = bar[0].get_facecolor()[:3]
    textColor = 'white' if isDarkColor(barColor) else 'black'
    # textColor = maxContrastColor(barColor, True)
    # textColor = invertColor(barColor, True)
    for rect, ok in zip(bar.patches, okList):
        if ok > 0:
            x, y = rect.get_xy()
            w, h = rect.get_width(), rect.get_height()
            x += w / 2
            if ax.get_yscale() == 'log':
                y = sqrt(h / 2) if y == 0 else sqrt(y * (y + h))
            else:
                y = y + h / 2 
            ax.text(x, y, ok, color=textColor, fontsize=fontsize, horizontalalignment='center', verticalalignment='center')

################################################################################################
def plotTextOnCenterOfBar(ax, rect, ok, ng, fontsize=10, color='w'):
    # for rect, ok, ng in zip(bar.patches, okList, ngList):
    if ok > 0 and ok != ok + ng:
        x, y = rect.get_xy()
        w, h = rect.get_width(), rect.get_height()
        x += w / 2
        y += sqrt(h / 2)
        ax.text(x, y, ok, color=color, fontsize=fontsize, horizontalalignment='center', verticalalignment='center')

################################################################################################
def plotXAxis(cn_font, ax, xLabel, xTicks, xTickLabels, minLim, maxLim, fontsize=14, retired_rockets=None):
    ax.set_xlim(minLim, maxLim) # Set the x-limits of the plot to reduce the gap between the left side of the plot and the first x-tick
    ax.set_xticks(xTicks)  # Explicitly set tick positions
    ax.set_xlabel(xLabel, fontproperties=cn_font, fontsize=fontsize)

    ax.set_xticklabels(insertLf(xTickLabels), fontproperties=cn_font, fontsize=fontsize)
    # if xTickLabels[0][:5] != xTickLabels[-2][:5]:
    #     ax.set_xticklabels(insertLf(xTickLabels), fontproperties=cn_font, fontsize=fontsize)
    # else:
    #     xTickLabels = [s[5:] for s in xTickLabels]
    #     ax.set_xticklabels(insertLf(xTickLabels), fontproperties=cn_font, fontsize=fontsize)
    hasGreyLable = False

    if retired_rockets:
        # Set the background color of selected x tick labels
        for tick in ax.get_xticklabels():
            if tick.get_text().replace('\n', '') in retired_rockets:
                tick.set_backgroundcolor('lightgrey')
                hasGreyLable = True
    return hasGreyLable

################################################################################################
def plotYAxis(cn_font, ax, yLabel, yTicks, minLim, maxLim, fontsize=None, copyYAxis=True):
    ax.set_ylabel(yLabel, loc='top', fontproperties=cn_font, fontsize=fontsize)
    # yMax = max(countList) + 0.2 if len(colorDict) < 5 else max(countList) + 0.2 * len(colorDict) / 5
    ax.set_ylim(minLim, maxLim)
    ax.set_yticks(yTicks)

    if copyYAxis:
        axRight = ax.twinx()
        axRight.set_ylabel(yLabel, loc='top', fontproperties=cn_font, fontsize=fontsize)
        # axRight.set_ylabel('发射数', loc='top', fontproperties=cn_font, fontsize=14)
        axRight.set_yticks(ax.get_yticks())
        axRight.set_ylim(ax.get_ylim())

################################################################################################
def isSingleRocket(ax):
    _, labels = ax.get_legend_handles_labels()
    singleRocket = len([*set(labels)]) == 1
    return singleRocket

################################################################################################
def convertStringToArray(str):
    label = []
    for c in str:
        if c.isdigit() and label and label[-1].isdigit():
            label[-1] += c
        else:
            label.append(c)
    return label

################################################################################################
def plotRocketNumber(ax, x, y, gap, label, cn_font, fontsize, color):
    count = len(label) 
    for i in range(count):
        y1 = y + (count / 2 - i) * gap if i < count / 2 else y - (i - count / 2) * gap
        y1 -= gap / 2
        ax.text(x+1, y1, s=label[i], color=color, ha="center", va="center", fontproperties=cn_font, fontsize=fontsize)

def isDarkColor(rgb):
    return get_luminance(rgb) < 128

################################################################################################
# TODO 条形图中显示卫星名，把-ー－转换成｜。
def plotRocketNumberInsideBar(ax, yDataList, xuhaoList, rocketList, colorDict, cn_font, fontsize, upperSrage=None):
    gap = 0.065
    for x, (c, xuhaos, rockets) in enumerate(zip(yDataList, xuhaoList, rocketList)):
        for i, (xuhao, rocket) in enumerate(zip(xuhaos.split('/'), rockets.split('/'))):
            color = 'white' if isDarkColor(colorDict[rocket]) else 'black'
            y = c / 2 if c == 1 else c / 4 + i * c / 2
            y = y * 3.5 if rocket == '春节' else y
            if f'{rocket}{xuhao}' in upperSrage:
                upperStage = upperSrage[f'{rocket}{xuhao}'].split('|')
                if isSingleRocket(ax):
                    withUpperStage = xuhao + '/' + upperStage[0]
                else:
                    withUpperStage = rocket + xuhao + '/' + upperStage[0]
                label = convertStringToArray(withUpperStage)
                # plotRocketNumber(ax, x, y, gap, label, cn_font, fontsize, color)
            else:
                if xuhao.startswith('遥') or xuhao.startswith('天'):
                    if not isSingleRocket(ax):
                        xuhao = rocket + xuhao
                    label = convertStringToArray(xuhao)
                    # plotRocketNumber(ax, x, y, gap, label, cn_font, fontsize, color)
                else:
                    if not isSingleRocket(ax):
                        label = convertStringToArray(rocket)
                        label.append(xuhao)
                    else:
                        label = xuhao
            plotRocketNumber(ax, x, y, gap, label, cn_font, fontsize, color)
                        # plotRocketNumber(ax, x, y, gap, xuhao, cn_font, fontsize, color)

################################################################################################
def plotLeftYAxis(cn_font, ax, yLabel, minLim, maxLim, percent=False, fontsize=14):
    ax.set_ylim(minLim, maxLim)
    ax.set_ylabel(yLabel, fontproperties=cn_font, loc='top', fontsize=fontsize)

    if percent:
        percent_formatter = mtick.PercentFormatter(xmax=1.0) # Create a formatter function to format the tick labels as percentages
        ax.yaxis.set_major_formatter(percent_formatter) # Set the y-axis tick formatter to the percent formatter
        ax.yaxis.set_major_locator(mtick.MultipleLocator(0.05)) # Set the y-axis tick locator to increment in steps of 5%

################################################################################################
def hideYTicks(ax, yTicks):
    # Hide the tick labels for the other y-ticks
    other_yTicks = [tick for tick in ax.get_yticks() if tick not in yTicks]
    ax.set_yticklabels(['' for tick in other_yTicks], minor=True)
    ax.set_yticklabels(['' if tick < 1.0 else tick for tick in yTicks])

################################################################################################
def plotRightYAxis(cn_font, ax, yLabel, yTicks, fontsize=14, log=False):
    if log:
        ax.set(yscale='symlog')
        # ax.set(yscale='log')
    ax.set_yticks(yTicks)
    ax.set_ylabel(yLabel, fontproperties=cn_font, loc='top', fontsize=fontsize)
    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%d'))
    hideYTicks(ax, yTicks)

################################################################################################
def plotYearOnTopOfBar(ax, xDataList, yDataList, fontsize=12):
    # if len(xDataList) == 1 or xDataList[0].year != xDataList[-1].year:
    # if len(xDataList) == 1:
    for i, (y, d) in enumerate(zip(yDataList, xDataList)):
        if i == 0 or d.year != xDataList[i - 1].year:
            ax.text(i+1, y+0.25, str(d.year)[0], ha="center", va="center", fontsize=fontsize)
            ax.text(i+1, y+0.17, str(d.year)[1], ha="center", va="center", fontsize=fontsize)
            ax.text(i+1, y+0.10, str(d.year)[2], ha="center", va="center", fontsize=fontsize)
            ax.text(i+1, y+0.03, str(d.year)[3], ha="center", va="center", fontsize=fontsize)

################################################################################################
def plotVLineBetweenYearsMonths(ax, xDataList, dx=0.5, yMin=-0.24, yMax=0.8, mustPlot=False):
    # fontHeight = plt.rcParams['font.size'] / 72
    # yMax += fontHeight * 5
    if mustPlot:
        for xData in xDataList:
            for i, date in enumerate(xData):
                ax.axvline(i + dx, ymin=yMin, ymax=yMax, linestyle='--', clip_on=False)
            ax.axvline(i + 1 + dx, ymin=yMin, ymax=yMax, linestyle='--', clip_on=False)
    else:
        for i, date in enumerate(xDataList):
            if date.year != xDataList[-1].year:
                if i > 0 and date.year != xDataList[i - 1].year:
                    ax.axvline(i + 1 - dx, ymin=yMin, ymax=yMax, linestyle='--', clip_on=False)
            elif xDataList[0].year == xDataList[-1].year:
                if i > 0 and date.month != xDataList[i - 1].month:
                    ax.axvline(i + 1 - dx, ymin=yMin, ymax=yMax, linestyle='--', clip_on=False)
            else:
                ax.axvline(i + 1 - dx, ymin=yMin, ymax=yMax, linestyle='--', clip_on=False)
                break

################################################################################################
def getLogList(y):
    yList1 = [0.5, 1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 30, 40, 50, 60, 80, 100, 150, 200, 250, 300, 400, 500]
    # yList1 = np.array([0.5, 1, 2, 3, 4, 5, 6, 8, 10, 20, 30, 40, 50, 60, 80, 100, 150, 200, 250, 300, 400, 500])
    yList2 = [600, 700, 800, 900, 1000]
    # yList2 = np.array([600, 700, 800, 900, 1000])
    
    if y >= 500:
        i = int(y / 100 - 5)
        return yList1 + yList2[i:i+1]
    
    for i in range(len(yList1)):
        if y < yList1[i]:
            return yList1[:(i + 1)]
        
    return []

################################################################################################
def kml2ShapelyPolygon(geom):
    x, y = list(geom.exterior.coords.xy[0]), list(geom.exterior.coords.xy[1])
    poly = Polygon(list(zip(x, y)))
    return poly

################################################################################################
def kml2ShapelyLine(geom):
    x, y = list(geom.coords.xy[0]), list(geom.coords.xy[1])
    line = LineString(list(zip(x, y)))
    return line

################################################################################################
def countRace(df, columnRocket, rocket, startYear, endYear, seriesDict):
    if rocket == '全部' or rocket == '系列':
        if rocket == '系列':
            df = ChangeToSeriesName(df, columnRocket, seriesDict)
        cond1 = df[columnRocket].str.startswith('长征')
        cond1 |= ~df[columnRocket].str.startswith('长征')
        # cond1 &= ~df[columnRocket].str.startswith('远征')
    elif rocket == '长征':
        cond1 = df[columnRocket].str.startswith(rocket)
    elif rocket == '其他':
        cond1 = ~df[columnRocket].str.startswith('长征')
        # cond1 &= ~df[columnRocket].str.startswith('远征')
    elif rocket == '民营':
        cond1 = df[columnRocket].str.startswith('OS-M')
        cond1 |= df[columnRocket].str.startswith('朱雀')
        cond1 |= df[columnRocket].str.startswith('双曲线')
        cond1 |= df[columnRocket].str.startswith('谷神星')
        cond1 |= df[columnRocket].str.startswith('力箭')
        cond1 |= df[columnRocket].str.startswith('天龙')
    cond1 &= ~df[columnRocket].str.startswith('远征')

    if startYear:
        columnYear = '日期'
        cond1 &= df[columnYear] >= pd.to_datetime(f'{startYear}0101')

    if endYear:
        columnYear = '日期'
        cond1 &= df[columnYear] < pd.to_datetime(f'{endYear}0101')
    return df[cond1]

################################################################################################
def countDataFrameByDate(dfList):
    # getting sub dataframe where 日期 is year and 结果 is not null
    # df = df[(df['日期'].astype(str).str.startswith(str(year))) & (df['结果'].notnull())]
    dfCountList = []
    # dfCount = dfList[0].copy()
    count = len(dfList)

    for i in range(count):
        dfCount = dfList[i].copy()

        # appending a new column 发射数 to count the same 日期
        dfCount['发射数'] = dfCount.groupby('日期')['日期'].transform('count')

        # Concate other columns with the same 日期
        try:
            dfCount[constants.EXCEL_COLUMN_ROCKET] = dfCount.groupby([constants.EXCEL_COLUMN_DATE])[constants.EXCEL_COLUMN_ROCKET].transform(lambda x: '/'.join(x))
            dfCount[constants.EXCEL_COLUMN_NUMBER] = dfCount.groupby([constants.EXCEL_COLUMN_DATE])[constants.EXCEL_COLUMN_NUMBER].transform(lambda x: '/'.join(x))
            dfCount[constants.EXCEL_COLUMN_LOCATION] = dfCount.groupby([constants.EXCEL_COLUMN_DATE])[constants.EXCEL_COLUMN_LOCATION].transform(lambda x: '/'.join(x))
            dfCount[constants.EXCEL_COLUMN_RESULT] = dfCount.groupby([constants.EXCEL_COLUMN_DATE])[constants.EXCEL_COLUMN_RESULT].transform(lambda x: '/'.join(x))
            # dfCount['火箭'] = dfCount.groupby(['日期'])['火箭'].transform(lambda x: '/'.join(x))
            # dfCount['序号'] = dfCount.groupby(['日期'])['序号'].transform(lambda x: '/'.join(x))
            # dfCount['地点'] = dfCount.groupby(['日期'])['地点'].transform(lambda x: '/'.join(x))
            # dfCount['结果'] = dfCount.groupby(['日期'])['结果'].transform(lambda x: '/'.join(x))
        except:
            pass
        dfCount = dfCount.groupby('日期').first().reset_index()
        dfCountList.append(dfCount)

    # if len(dfList) == 1:
    #     return dfCount
    # else:
    return dfCountList

################################################################################################
def getUpperStageAndLastLuanch(df, columnRocket):
    upperStage = {}
    lastLuanch = []
    df.reset_index(drop=True, inplace=True)
    cond1 = df[columnRocket].str.startswith('远征')
    dfSelected = df[cond1]
    indexSelected = dfSelected.index - 1
    df = df.iloc[indexSelected]
    return upperStage, lastLuanch

################################################################################################
def countRocket(df, columnRocket, rocket, seriesDict=None):
    if columnRocket is not None:
        if isinstance(rocket, list):
            cond1 = df[columnRocket].isin(rocket)
        # elif rocket == '上面级':
        #     # cond1 = df[columnRocket].str.startswith('长征')
        #     # cond1 |= df[columnRocket].str.startswith('远征')
        #     df.reset_index(drop=True, inplace=True)
        #     cond1 = df[columnRocket].str.startswith('远征')
        #     dfSelected = df[cond1]
        #     indexSelected = dfSelected.index - 1
        #     df = df.iloc[indexSelected]
        #     cond1 = None
        elif rocket == '' or rocket == '全部':
            cond1 = df[columnRocket].str.startswith('长征')
            cond1 |= ~df[columnRocket].str.startswith('长征')
            cond1 &= ~df[columnRocket].str.startswith('远征')
        elif rocket == '长征':
            cond1 = df[columnRocket].str.startswith(rocket)
        # TODO use seriesDict to or 
        elif rocket == '长征三号甲系列':
            cond1 = df[columnRocket].str.startswith('长征三号甲')
            cond1 |= df[columnRocket].str.startswith('长征三号乙')
            cond1 |= df[columnRocket].str.startswith('长征三号丙')
        elif rocket == '长征四号系列':
            cond1 = df[columnRocket].str.startswith('长征四号')
        elif rocket == '长征五号系列':
            cond1 = df[columnRocket].str.startswith('长征五号')
        elif rocket == '长征六号系列':
            cond1 = df[columnRocket].str.startswith('长征六号')
        elif rocket == '长征七号系列':
            cond1 = df[columnRocket].str.startswith('长征七号')
        elif rocket == '长征十一号系列':
            cond1 = df[columnRocket].str.startswith('长征十一号')
        elif rocket == '其他':
            cond1 = ~df[columnRocket].str.startswith('长征')
            cond1 &= ~df[columnRocket].str.startswith('远征')
        elif rocket == '快舟系列':
            cond1 = df[columnRocket].str.startswith('快舟')
        elif rocket == '朱雀系列':
            cond1 = df[columnRocket].str.startswith('朱雀')
        elif rocket == '捷龙系列':
            cond1 = df[columnRocket].str.startswith('捷龙')
        elif rocket == '谷神星系列':
            cond1 = df[columnRocket].str.startswith('谷神星')
        elif rocket == '星河系列':
            cond1 = df[columnRocket].str.startswith('谷神星')
            cond1 |= df[columnRocket].str.startswith('智神星')
        elif rocket == '力箭系列':
            cond1 = df[columnRocket].str.startswith('力箭')
        elif rocket == '天龙系列':
            cond1 = df[columnRocket].str.startswith('天龙')
        elif rocket == '民营':
            cond1 = df[columnRocket].str.startswith('OS-M')
            cond1 |= df[columnRocket].str.startswith('朱雀')
            cond1 |= df[columnRocket].str.startswith('双曲线')
            cond1 |= df[columnRocket].str.startswith('谷神星')
            cond1 |= df[columnRocket].str.startswith('力箭')
            cond1 |= df[columnRocket].str.startswith('天龙')
        else:
            cond1 = df[columnRocket] == rocket
    return df[cond1] if cond1 is not None else df

################################################################################################
# headersRow starts from 0
def readShipMoveData(excelFile, sheetName=None, headersRow=None, headers=None):
    if excelFile[-4:] == '.xls':
        oldExcelFile = excelFile
        excelFile = excelFile.replace('.xls', '.xlsx')
        xls.save_book_as(file_name=oldExcelFile, dest_file_name=excelFile)

    excelBook = loadXLSX(excelFile, data_only=True, read_only=True)

    if sheetName is None:
        sheetName = excelBook.get_sheet_names()[0]
    worksheet = excelBook[sheetName]
    
    df = pd.DataFrame(worksheet.values) # Convert the worksheet to a DataFrame

    if headers is not None:
        df.columns = headers # Modify Hedaers
    elif headersRow is not None:
        df.columns = df.iloc[headersRow].replace('\n', '') # Set the column names to the values in the headers row

    for row in range(headersRow + 1):
        df = df.drop(index=row) # Drop the rows above headers, since it's already used as the column names

    df.replace('-', np.nan, inplace=True) # Replace '-' with NaN
    df.replace([None, np.nan], '', inplace=True) # Replace None with empty string
    return df

################################################################################################
def readDataFromSheet(excelSheet, headers, columnNotNull, columnRocket, noAbort, onlyFailed):
    # Convert the worksheet to a DataFrame
    df = pd.DataFrame(excelSheet.values)

    # Set the column names to the values in the first row
    df.columns = df.iloc[0].replace('\n', '')

    # Drop the first row, since it's already used as the column names
    df = df.drop(index=0)

    if headers is not None:
        df.columns = headers # Modify Hedaers

    df.replace('-', np.nan, inplace=True) # Replace '-' with NaN
    df.replace([None, np.nan], '', inplace=True) # Replace None with empty string

    if noAbort:
        cond1 = df[columnNotNull] != '中止' # filter to exclude rows where 结果 is '中止'
        cond1 &= df[columnNotNull].ne('')  # filter to exclude rows where 结果 is ''
        cond1 |= df[columnRocket].str.startswith('远征') # include rows where 火箭 starts with '远征'
        df = df[cond1] 

    if onlyFailed:
        df = df[(df[columnNotNull] != '成功')]
    return df

################################################################################################
def readDataFromBook(excelBook, sheetName, headers, columnNotNull, columnRocket, noAbort, onlyFailed):
    excelSheet = excelBook[sheetName]
    return readDataFromSheet(excelSheet, headers, columnNotNull, columnRocket, noAbort, onlyFailed)
    # # Convert the worksheet to a DataFrame
    # df = pd.DataFrame(worksheet.values)

    # # Set the column names to the values in the first row
    # df.columns = df.iloc[0].replace('\n', '')

    # # Drop the first row, since it's already used as the column names
    # df = df.drop(index=0)

    # if headers is not None:
    #     df.columns = headers # Modify Hedaers

    # df.replace('-', np.nan, inplace=True) # Replace '-' with NaN
    # df.replace([None, np.nan], '', inplace=True) # Replace None with empty string

    # if noAbort:
    #     cond1 = df[columnNotNull] != '中止' # filter to exclude rows where 结果 is '中止'
    #     cond1 &= df[columnNotNull].ne('')  # filter to exclude rows where 结果 is ''
    #     cond1 |= df[columnRocket].str.startswith('远征') # include rows where 火箭 starts with '远征'
    #     df = df[cond1] 

    # if onlyFailed:
    #     df = df[(df[columnNotNull] != '成功')]
    # return df

################################################################################################
def mergeData(dfPivot, dfPivotOk, columnYear):
    def custom_logic(row, index):
        result = {} 
        for column, value in row.items():
            if column in constants.RETIRED_ROCKETS:
                result[column] = f'{value * 1000 + dfPivotOk[column][index]}'    # 退役
            else:
                result[column] = f'{value * 1000000 + dfPivotOk[column][index]}'  # 现役
        return result 

    result_data = []
    for index, row in dfPivot.iterrows():
        resultRow = custom_logic(row, index)
        resultRow[columnYear] = pd.to_datetime(row.name, errors='coerce', format='%Y-%m-%d')
        result_data.append(resultRow)
    
    dfPivot.reset_index(inplace=True)
    dfResult = pd.DataFrame(result_data, columns=dfPivot.columns)
    dfResult.set_index(columnYear, inplace=True)
    return dfResult

################################################################################################
def ChangeToSeriesName(df, columnRocket, seriesDict):
    if seriesDict is None:
        seriesDict = constants.ROCKET_SERIES
    for series in seriesDict:
        df[columnRocket] = df[columnRocket].replace(series)
    return df

################################################################################################
def insertFirstDayOfStartYear(df, startYear):
    startYMD = f'{startYear}-01-01'
    if str(df.iloc[0].name)[:10] > startYMD:
        indexName = df.index.name
        df = df.reset_index()
        first_timestamp = pd.Timestamp(f'{startYMD}').floor('s')
        first_row = df.iloc[0].copy() # first row
        first_row[indexName] = first_timestamp
        df = pd.concat([pd.DataFrame([first_row]), df], ignore_index=True)
        df = df.set_index(indexName)
    return df

def appendLastRow(df, last_timestamp):
    indexName = df.index.name
    df = df.reset_index()
    last_row = df.iloc[-1].copy() # first row
    last_row[indexName] = last_timestamp
    df = pd.concat([df, pd.DataFrame([last_row])], ignore_index=True)
    df = df.set_index(indexName)
    return df

################################################################################################
def appendLastDayOfendYear(df, endYear):
    today = datetime.today()
    if endYear < today.year:
        endYMD = f'{endYear}-12-31 23:59:59'
    else:
        endYMD = f'{today.year}-{today.month}-{today.day} 23:59:59'

    last_timestamp = pd.Timestamp(f'{endYMD}').floor('s')
    df = appendLastRow(df, last_timestamp)
    return df

################################################################################################
def duplicateLastRow(df, today):
    indexName = df.index.name
    df = df.reset_index()
    today_timestamp = pd.Timestamp(today).floor('s')
    last_row = df.iloc[-1].copy() # last row
    last_row[indexName] = today_timestamp
    df = pd.concat([df, pd.DataFrame([last_row])], ignore_index=True)
    df = df.set_index(indexName)
    return df

################################################################################################
def readUpperStageDict():
    excelFile = "./data/ChinaRocketLaunch.xlsx"
    sheetName = "发射纪录"
    excelBook = loadXLSX(excelFile, data_only=True, read_only=True)
    excelSheet = excelBook[sheetName]
    dfList = parseExcelSheetToDataFrame(excelSheet, rocket='上面级+最后发射')
    dfUpperStages = dfList[:-1] # 上面级
    dfLastLaunch = dfList[-1] # 最后的发射
    dictUpperStage = getUpperStageDict(dfUpperStages)
    return dictUpperStage, dfLastLaunch

################################################################################################
def getUpperStageDict(dfList, columnRocket='火箭', columnNumber='序号', columnRemark='备注'):
    # Constructing the dictionary
    result_dict = {}
    for df in dfList:
        for i in range(len(df)):
            key = df.iloc[i][columnRocket] + df.iloc[i][columnNumber]
            value = df.iloc[i][columnRemark]
            result_dict[key] = value
        # for i in range(0, len(df) - 1, 2):  # Iterate until the second last row
        #     key = df.iloc[i][columnRocket] + df.iloc[i][columnNumber]  # Key from col1 and col2 of row N
        #     value = df.iloc[i + 1][columnRocket] + df.iloc[i + 1][columnNumber]  # Value from col1 and col2 of row N+1
        #     result_dict[key] = value
    return result_dict
    
################################################################################################
def getLastLaunch(df, columnResult):
    # Case 1: Get the Last Row
    lastRow = df[df[columnResult] != ''].iloc[-1]

    # # Case 2: Get the Last Two Rows (checking if 序号 is null)
    # if pd.isnull(last_row[columnResult]):
    #     last_rows = df.iloc[-2:]
    #     # print('\nCase 2 - Last Two Rows:')
    #     # print(last_rows)
    # else:
    #     last_rows = last_row.to_frame(0).T
        # print('\nCase 1 - Last Row:')
        # print(last_rows)
    return lastRow

################################################################################################
def parseExcelSheetToDataFrame(excelSheet, 
                               rocket:str=None, location=None, payload=None, startYear=None, endYear=None, 
                               columnRocket='火箭', columnLocation='地点', columnPayload='載荷', 
                               columnYear='日期', columnNotNull='结果', 
                               headers=None, noAbort=True, mom=False,
                               onlyFailed=False, isRace=False, isAfterRetired=None, 
                               seriesDict=None, isMaiden=False, isFirstLast=False, isLunarNewYear=False):
    df = readDataFromSheet(excelSheet, headers, columnNotNull, columnRocket, noAbort, onlyFailed)
    return parseToDataFrame(df, rocket, location, payload, startYear, endYear, columnRocket, columnLocation, columnPayload, 
        columnYear, columnNotNull, headers, noAbort, mom, onlyFailed, isRace, isAfterRetired, seriesDict, isMaiden, isFirstLast, isLunarNewYear)

################################################################################################
def parseExcelBookToDataFrame(excelBook, sheetName, 
                               rocket:str=None, location=None, payload=None, startYear=None, endYear=None, 
                               columnRocket='火箭', columnLocation='地点', columnPayload='載荷', 
                               columnYear='日期', columnNotNull='结果', 
                               headers=None, noAbort=True, mom=False,
                               onlyFailed=False, isRace=False, isAfterRetired=None, 
                               seriesDict=None):
    df = readDataFromBook(excelBook, sheetName, headers, columnNotNull, columnRocket, noAbort, onlyFailed)
    return parseToDataFrame(df, rocket, location, payload, startYear, endYear, columnRocket, columnLocation, columnPayload, 
        columnYear, columnNotNull, headers, noAbort, mom, onlyFailed, isRace, isAfterRetired, seriesDict)

################################################################################################
def getDfFirstlast(df, columnYear):
    dfFirst = df[df[columnYear].apply(lambda x: x.month) == 1].head(1)
    dfLast = df[df[columnYear].apply(lambda x: x.month) == 12].tail(1)
    dfResult = pd.concat([dfFirst, dfLast])
    return dfResult

################################################################################################
def getFirstSameDateRows(df):
    if len(df) > 1 and df.iloc[-1].日期 == df.iloc[-2].日期:
        dfRows = df.tail(2)
    else:
        dfRows = df.tail(1)
    return dfRows

################################################################################################
def getLastSameDateRows(df):
    if len(df) > 1 and df.iloc[0].日期 == df.iloc[1].日期:
        dfRows = df.head(2)
    else:
        dfRows = df.head(1)
    return dfRows

################################################################################################
def parseToDataFrame(df, rocket:str=None, location=None, payload=None, startYear=None, endYear=None, 
                               columnRocket='火箭', columnLocation='地点', columnPayload='載荷', 
                               columnYear='日期', columnNotNull='结果', 
                               headers=None, noAbort=True, mom=False,
                               onlyFailed=False, isRace=False, isAfterRetired=None, 
                               seriesDict=None, isMaiden=False, isFirstLast=False, isLunarNewYear=False):
    dfList = []
    
    # Extract rows by condition
    if isFirstLast:
        dfResult = pd.DataFrame()
        df = df[~df[columnYear].isnull()]
        # df[columnYear] = pd.to_datetime(df[columnYear]).dt.date
        dfResult = df.groupby(df[columnYear].apply(lambda x: x.year)).apply(getDfFirstlast, columnYear).reset_index(drop=True)
        dfResult = dfResult.sort_values(columnYear).reset_index(drop=True)
        dfList.append(dfResult)

    elif isLunarNewYear:
        df = df[~df[columnYear].isnull()]
        lunarNewYearDates = myUtils.readConfig(['LunarNewYear'])
        lunarNewYearDates = [pd.Timestamp(x, unit='D') for x in lunarNewYearDates]
        dfLunarNewYears = pd.DataFrame({
            columnRocket: ['春节'] * len(lunarNewYearDates),
            columnYear: lunarNewYearDates,
            columnLocation: '中国',
            columnNotNull: '成功',
            '序号': '',
        })
        dfCopy = pd.concat([df, dfLunarNewYears]).sort_values(columnYear).reset_index()
        dfLunarNewYearDates = dfCopy[dfCopy[columnRocket] == '春节'][columnYear]
        dfResult = pd.DataFrame()
        for dfLunarNewYearDate in dfLunarNewYearDates:
            year = dfLunarNewYearDate.year
            january01 = pd.Timestamp(f'{year}-01-01', unit='D')
            feburary28 = pd.Timestamp(f'{year}-02-28', unit='D')
            limit = (dfCopy[columnYear] >= january01) & (dfCopy[columnYear] <= feburary28)
            dfBefore = dfCopy[(dfCopy[columnYear] < dfLunarNewYearDate) & limit]
            dfAfter = dfCopy[(dfCopy[columnYear] > dfLunarNewYearDate) & limit]

            if not dfBefore.empty or not dfAfter.empty:
                if not dfBefore.empty:
                    dfResult = pd.concat([dfResult, getFirstSameDateRows(dfBefore)])
                dfThisYear = dfLunarNewYears[dfLunarNewYears[columnYear] == dfLunarNewYearDate]      
                dfResult = pd.concat([dfResult, dfThisYear])
                if not dfAfter.empty:
                    dfResult = pd.concat([dfResult, getLastSameDateRows(dfAfter)])
        dfList.append(dfResult)
    elif isMaiden:
        dfAll = df.groupby(columnRocket).head(1)
        dfCZ = dfAll[dfAll[columnRocket].str.startswith('长征')]
        dfNCZ = dfAll[~dfAll[columnRocket].str.startswith('长征')]
        dfList.append(dfAll)
        dfList.append(dfCZ)
        dfList.append(dfNCZ)
    elif isRace:
        df = countRace(df, columnRocket, rocket, startYear, endYear, seriesDict)
        df = df.copy()
        df.loc[:, 'count'] = 1
        df.loc[:, 'ok'] = 0
        df.loc[df[columnNotNull] == '成功', 'ok'] = 1

        # Pivot the DataFrame from long to wide format
        dfPivot = df.pivot_table(index=columnYear, columns=columnRocket, values='count', aggfunc='sum', fill_value=0)
        dfPivotOk = df.pivot_table(index=columnYear, columns=columnRocket, values='ok', aggfunc='sum', fill_value=0)

        # Reorder columns to match the original order
        column_order = df[columnRocket].unique()
        dfPivot = dfPivot[column_order]
        dfPivotOk = dfPivotOk[column_order]

        # Reset the index to include 'date' as a column
        dfPivot.reset_index(inplace=True)
        dfPivotOk.reset_index(inplace=True)

        # Perform cumulative summation for each category
        dfPivot.set_index(columnYear, inplace=True)
        dfPivot = dfPivot.cumsum()
        dfPivotOk.set_index(columnYear, inplace=True)
        dfPivotOk = dfPivotOk.cumsum()

        if startYear == None:
            today = datetime.today()
            dfPivot = duplicateLastRow(dfPivot, today)
            dfPivotOk = duplicateLastRow(dfPivotOk, today)
        else:
            dfPivot = insertFirstDayOfStartYear(dfPivot, startYear)
            dfPivot = appendLastDayOfendYear(dfPivot, endYear - 1)
            dfPivotOk = insertFirstDayOfStartYear(dfPivotOk, startYear)
            dfPivotOk = appendLastDayOfendYear(dfPivotOk, endYear - 1)

        # copy original df to use when plot
        dfAll = dfPivot.copy()
        dfOk = dfPivotOk.copy()

        if isAfterRetired:
            dfResult = pd.DataFrame(index=dfPivot.index)
            for label, date_value in constants.RETIRED_ROCKETS.items():
                conditionColumn = (dfPivot.columns == label)
                if conditionColumn.any():
                    dfTemp_label = np.where(conditionColumn, dfPivot + dfPivotOk / 1000, dfPivot * 1000 + dfPivotOk / 1000)
                    conditionRow = (dfPivot.index >= date_value)
                    dfTemp_date = np.where(conditionRow[:, np.newaxis], dfTemp_label, dfPivot * 1000 + dfPivotOk / 1000)
                    df_temp_result = pd.DataFrame(dfTemp_date, columns=dfPivot.columns, index=dfPivot.index)
                    if dfResult.empty:
                        dfResult = df_temp_result.copy()
                    else:
                        dfResult[label] = df_temp_result[label]
            if dfResult.empty:
                dfResult = dfPivot * 1000 + dfPivotOk / 1000    # convert to float
        elif isAfterRetired == False:
            condition = dfPivot.columns.isin(constants.RETIRED_ROCKETS)
            dfTemp = np.where(condition, dfPivot + dfPivotOk / 1000, dfPivot * 1000 + dfPivotOk / 1000)
            dfResult = pd.DataFrame(dfTemp, columns=dfPivot.columns, index=dfPivot.index)
        else:
            dfResult = dfPivot * 1000 + dfPivotOk / 1000    # convert to float

        dfList.append(dfResult)
        dfList.append(dfOk)
        dfList.append(dfAll)

    elif startYear is not None:
        if endYear is None:
            endYear = startYear

        if columnYear is None:
            columnYear = '日期' #df.columns[0]

        # df = df[(df[columnYear].astype(str).str.startswith(str(startYear)))]
        # df = df[df[columnYear].between(startYear, endYear)]
        if columnYear is not None:
            # remove rows where 'columnYear' is not of datetime type
            df = df[pd.to_datetime(df[columnYear], errors='coerce', format='%Y-%m-%d').notnull()]

            if len(startYear) == 4:
                startYMD = f'{startYear}0101'
            elif len(startYear) == 6:
                startYMD = f'{startYear}01'
            else:
                startYMD = startYear[:8]

            if len(endYear) == 4:
                endYMD = f'{endYear}1231'
            elif len(endYear) == 6:
                lastDay = myUtils.getLastdayOfMonth(int(endYear[:4]), int(endYear[4:]))
                endYMD = f'{endYear}{lastDay}'
            else:
                endYMD = f'{endYear[:4]}1231'

            if mom:
                year = startYMD[:4]
                lastYear = str(int(year) - 1)
                lastStartYMD = f'{lastYear}{startYMD[4:]}'
                lastEndYMD = f'{lastYear}{endYMD[4:]}'
                d1 = df[columnYear] >= pd.to_datetime(f'{lastStartYMD}')
                d2 = df[columnYear] < pd.to_datetime(f'{lastEndYMD}')
                dfList.append(df[d1 & d2])
                
            cond1 = df[columnYear] >= pd.to_datetime(f'{startYMD}')
            cond2 = df[columnYear] < pd.to_datetime(f'{endYMD}')
            dfList.append(df[cond1 & cond2])

    elif rocket is not None:
        if not isinstance(rocket, list) and rocket.find('上面级') >= 0:
            df.reset_index(drop=True, inplace=True)
            cond1 = df['备注'].str.startswith('远征')
            dfUpperStage = df[cond1]
            dfList = split50perPage(dfUpperStage)
            if rocket == '上面级+最后发射':
                dfLastLaunch = getLastLaunch(df, columnNotNull)
                dfList.append(dfLastLaunch)
        else:
            df = countRocket(df, columnRocket, rocket)
            dfList = split50perPage(df)

    elif location is not None:
        if columnLocation is not None:
            if isinstance(location, list):
                cond1 = df[columnLocation].isin(location)
            else:
                cond1 = df[columnLocation] == location
            df = df[cond1]
            dfList = split50perPage(df)
            # dfList = split50perPage(df, cond1)

    elif payload is not None:
        if columnPayload is not None:
            if isinstance(location, list):
                cond1 = df[columnPayload].isin(payload)
            else:
                startswith = False
                if payload[:1] == '^':
                    startswith = True
                    payload = payload[1:]
                arr = payload.split('~')
                cond1 = df[columnPayload].str.startswith(arr[0]) if startswith else df[columnPayload].str.contains(arr[0])
                if len(arr) > 1:
                     cond1 &= ~df[columnPayload].str.contains(arr[1])

            df = df[cond1]
            dfList = split50perPage(df)
            # dfList = split50perPage(df, cond1)
            # dfResult = df[d1]
            # if len(dfResult) > 50:
            #     dfList = dict(list(dfResult.groupby(np.arange(len(dfResult)) // 50)))
            # else:
            #     dfList.append(dfResult)
    else:
        cond1 = ~df[columnRocket].str.startswith('远征')
        dfSelected = df[cond1]        
        dfList.append(dfSelected)
    return dfList

def calcColsPerLine(newLabels):
    count = len(newLabels)
    ncols1 = 6
    r1 = count % ncols1
    if (count > 20 or r1 == 0):
        return ncols1
    
    ncols2 = 5
    r2 = count % ncols2
    if (r2 == 0):
        return ncols2
    
    if r2 > r1:
        ncols1 = ncols2

    ncols2 = 4
    r2 = count % ncols2
    if (r2 == 0):
        return ncols2
    
    if r2 > r1:
        ncols1 = ncols2

    ncols2 = 3
    r2 = count % ncols2
    if (r2 == 0):
        return ncols2

    if r2 > r1:
        ncols1 = ncols2
    return ncols1

def split50perPage(dfResult):
    dfList = []
    # dfResult = df[d1] if d1 is not None else df
    if len(dfResult) > 50:
        dfList = dict(list(dfResult.groupby(np.arange(len(dfResult)) // 50)))
    else:
        dfList.append(dfResult)

    return dfList

def getUnique20Colors(index: int):
    return plt.cm.tab20(index)

def getUniqueColorList(n: int):
    colorList = list(mpl.colors.CSS4_COLORS.values())
    random.shuffle(colorList)
    return colorList[:n]



