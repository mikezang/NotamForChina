import io
# import os
# PySimpleGUI Developer Key
# os.environ['PySimpleGUI_license'] = 'eJydJFMkaPWINVlobcn0NylzVgHUlKw8ZUSjIu6eIWkRRXlKdCm3VTsMbM3NBQl3cwiKIGsSIMkHxcpXYQ2OVTulcW27VCJnROCDIH6MMMToc6xpM7z1Qi08MPjxYa2AMYirwJiETUGKlcjKZFWY5tzKZkUiRQl7cuG8xWvBeHWL1hl4bin6RSWaZUXCJjztaKWP9UujInjRogxvLSCVJ6OSYBWJ1KlVRcmVlgy1cO3fQJiiO8i9JUN9aYW0tZlyIEinwdigT2mIFWtWZcUqxEh6cx3PQOiEOci5JOa7YJWg5HnaIZikwyipQD2a9HtfcRGbFyuyeRSNIy6GIPiRItsaIXkANB1CcY3XRPvSbGWTVKyDS7UrQ8iRORi2IcxoNVTbg0xENBSSIFsZIVkxRVhjdMGMVqJOcC3JNX11ZgWvQ2iPOMihIDwWNeCY8hxNOyCf8cy3MjDcI60CIqipwZiiR4GZFf0VZUU7Vz43cmGplHy3ZYX8MOiyO0imIKwoNWCG8VxwOkCz8Xy6MoD6Ia1bIwiNwqi0RYWh1whtaRWixrBrZiGlRPyCZQXPNtz9IwjVotiIenmRhHlNbRmtdpyRb3295pn4LWn9pShXb8mLd7AEZK2b1MhgaNWGwmuzYb2Z9RtkINiZwVibSTVEBbB9ZKGERVyQZVXTNjz5IPjyobi6MVT0MI2ALHjFIay0N8i745yuMWzukGuLNvzkEYiDf3QQ=8=M6cfd0f1ce97942ac714563c6eb9fff4e5e17ea366f2ebecb029772015e49bcd7bc099d9c7eba082b5b88e6510e4a82b0e9042ae87198c187d1ff2e9545990ed71bc7b29cab288cfc566d92ac9f7d406d99607ddff6a531dfffcbbe68283f84843ef67b4f4d78ca7bf44e67fae0980da79a54038e2526ad79c873978c868ed6c079da54d6fad6b10e9d0c71a264410a2217bd9e000bdc8660fb523fc5595864f46fb13598bfb86399871dec8fe916a8145a2f74bfa47731c6315455fae07ab6f2155c6df4d682c4cc522336af8c69e8161e9850af6281bdbffa3724c90a6d8da8c945ead1ca0d8ed3729a991264e4e61bd83f19438fe57effa07f4a1841c37ec4578bad12875c77404947b50ea5790d323dc1e9d88f48b6b38a16fada115a6ea902c6d62a61e81cfe1fe67a93e09f73bc86556d194c9b38727f61906d9da320b5dd7da5e713ab4e139fad910dc876d377ba267a3e1f532c505b3e801bea7c388c5ad9bb5bcc184a5e31be3f717a6890a2f01c75c1d054c0dcbd884787fca43fdc58142a0621f8bb71ff693da112ab38c4815e0e81c4cfaa689129539d1ac5d272689949484b0aeb9f189bd3529383823af517c97273a92066d28af58b5603094b773b42bf17fccb557e691ff5d2fcb31649fb1a3d6e08aa582a335967891bd65e92a757968816e21675566f698838096094352b7187366a6856f9cabcf50b6923'
import random
import subprocess
from math import log, sqrt
from re import findall
from datetime import datetime
import PySimpleGUI as sg
import numpy as np
from PIL import Image
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.font_manager as fm
import matplotlib.colors as mcolors
import matplotlib.image as mpimg

from myModules import myExcel
from myModules import myUtils

################################################################################################
def calcDurationByFrames(frames, framerate):
    return frames / framerate

################################################################################################
def getFileFrameRate(filename: str) -> float:
    if not myUtils.isVideoFile(filename):
        print(f'{filename} not video file!')
        return 0
    cmd = f"ffprobe.exe -v error -show_entries stream=avg_frame_rate -of default=nw=1:nk=1 {filename}"
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return int(result.stdout.split('/')[0])

################################################################################################
def addImages2BarChart():
    labels = ['CW', 'CV', 'GW', 'SX', 'DO']
    colors = ['crimson', 'dodgerblue', 'teal', 'limegreen', 'gold']
    taikos = ['C:\\zang\\python\\RocketLaunch\\images\\flags\\china.png', 
            '..\\images\\flags\\japan.png', 
            '..\\images\\flags\\singapore.png', 
            '..\\images\\flags\\southkorea.png', 
            '..\\images\\flags\\vietnam.png']
    values = 30 + np.random.randint(5, 20, len(labels)).cumsum()
    height = 0.9
    plt.barh(y=labels, width=values, height=height, color=colors, align='center')

    for i, (label, value, taiko) in enumerate(zip(labels, values, taikos)):
        img = mpimg.imread(taiko) 
        rect = [value - 8, value - 2, i - height / 4, i + height / 4]
        plt.imshow(img, extent=rect, aspect='auto', zorder=2)
    plt.xlim(0, max(values) * 1.05)
    plt.ylim(-0.5, len(labels) - 0.5)
    plt.tight_layout()
    plt.show()

################################################################################################
def getFramesCount(filename):
    frames = subprocess.run('ffprobe -show_frames ' + filename)
    return frames

################################################################################################
def make_dpi_aware():
    import ctypes
    import platform
    if myUtils.isWindows() and int(platform.release()) >= 8:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)

def moveWindow(window, x=None, y=None):
    w0, h0 = sg.Window.get_screen_size()
    x0, y0 = window.current_location()
    w, h = window.size
    if x is None:
        x = (w0 - w) // 2 - 10
    if y is None:
        y = y0
    window.move(x, y)

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
def get_nearest_taikonaut(df, date, taikonaut, use_pinyin=False):
    try:
        taikoColumn = 'Pinyin' if use_pinyin else '航天员'
        cond = df[taikoColumn] == taikonaut
        return df[cond]
    except KeyError:
        # If the exact date is not found, find the nearest date
        nearest_index = min(df.index, key=lambda x: abs(x - pd.Timestamp(date)))
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
    # by passing 'rw' to whitelist of fiona's supported drivers:

    return cn_font

################################################################################################
def showBackend():
    # print(plt.get_backend())
    if plt.get_backend().lower() not in ['agg', 'tkagg', 'gtk3agg', 'macosx']:
        plt.show()

################################################################################################
# Function to extract coordinates from LineString geometries
def extractLinestringCoordinates(gdf):
    coords = []
    for line in gdf.geometry:
        if line and line.geom_type == 'LineString':
            x, y = line.xy
            coords.append((list(x), list(y)))
    return coords

################################################################################################
def getImage(filename, resize=True, size=myExcel.IMAGE_SIZE):
    im = Image.open(filename)
    if resize:
        if im.size[0] > im.size[1]:
            resize = [size[0], size[1] * im.size[1] / im.size[0]]
        else:
            resize = [size[0] * im.size[0] / im.size[1], size[1]]
        resize = map(int, resize)
        # ration = max(size[0]/im.size[0], size[1]/im.size[1])
        # resize = (int(size[0] * ration), int(size[1] * ration))
        im = im.resize(resize, Image.LANCZOS)
    with io.BytesIO() as buffer:
        im.save(buffer, format='PNG')
        image = buffer.getvalue()
    return image

################################################################################################
def setScreenDpiAware():
    make_dpi_aware()
    sg.theme('Python')
    sg.set_options(text_justification='right')      

################################################################################################
def saveFig(fig, filename, isPrint=True, resize=True, dpi=300):
    myUtils.createFolder(filename)
    if resize:
        buf = io.BytesIO()
        # fig.savefig(buf, bbox_inches='tight')
        fig.savefig(buf, bbox_inches='tight', dpi=dpi)
        plt.close(fig)
        buf.seek(0)
        img = Image.open(buf)
        figsize = fig.get_size_inches()
        size = figsize * dpi # size in pixels
        img_resize = img.resize(size.astype(int))
        img_resize.save(filename)
    else:
        fig.savefig(filename, bbox_inches='tight')
        plt.close(fig)
    if isPrint:
        print(f'Save to file: {filename}')
    return 

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
def plotXAxis(cn_font, ax, xLabel, xTicks, xTickLabels, minLim, maxLim, fontsize=14, retired_rockets=None, inVerticle=True):
    ax.set_xlim(minLim, maxLim) # Set the x-limits of the plot to reduce the gap between the left side of the plot and the first x-tick
    ax.set_xticks(xTicks)  # Explicitly set tick positions
    ax.set_xlabel(xLabel, fontproperties=cn_font, fontsize=fontsize)

    if inVerticle:
        xTickLabels = insertLf(xTickLabels)
    ax.set_xticklabels(xTickLabels, fontproperties=cn_font, fontsize=fontsize)
    hasGreyLable = False

    if retired_rockets:
        # Set the background color of selected x tick labels
        for tick in ax.get_xticklabels():
            if tick.get_text().replace('\n', '') in retired_rockets:
                tick.set_backgroundcolor('lightgrey')
                hasGreyLable = True
    return hasGreyLable

################################################################################################
def setYAxisLog(cn_font, ax, yTicks):
    ax.set(yscale='log')
    ax.set_yticks(yTicks)
    ax.set_ylabel('发射数', fontproperties=cn_font, loc='top')
    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%d'))
    ax.set_ylim(0.5, yTicks[-1])
    hideYTicks(ax, yTicks)

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
def plotRocketNumber(cn_font, ax, x, y, gap, label, fontsize, color):
    count = len(label) 
    for i in range(count):
        y1 = y + (count / 2 - i) * gap if i < count / 2 else y - (i - count / 2) * gap
        y1 -= gap / 2
        ax.text(x+1, y1, s=label[i], color=color, ha="center", va="center", fontproperties=cn_font, fontsize=fontsize)

def isDarkColor(rgb):
    return get_luminance(rgb) < 128

################################################################################################
def plotPayloadInsideBar(cn_font, ax, yDataList, rocketList, payloadList, colorDict, fontsize, payload=None):
    gap = 0.065
    for x, (c, payloads, rockets) in enumerate(zip(yDataList, payloadList, rocketList)):
        for i, (payload1, rocket) in enumerate(zip(payloads.split('/'), rockets.split('/'))):
            color = 'white' if isDarkColor(colorDict[rocket]) else 'black'
            y = c / 2 if c == 1 else c / 4 + i * c / 2
            y = y * 3.5 if rocket == '春节' else y

            # pattern = r'(天宫.*|梦天.*|问天.*|巡天.*|神舟.*|天舟.*)' if payload == '空间站' else f'{payload}.*'
            pattern = r'(.*)' if payload == '空间站' else f'{payload}.*'
            label = ''
            labels = findall(pattern, payload1)
            if labels:
                for l in labels:
                    label += l + '／'    
            label = label[:-1].split(',')[0].split('(')[0].split('（')[0]
            label = label.replace('-', '|')
            if payload == '吉林一号':
                label = label.replace(payload, '')
            plotRocketNumber(cn_font, ax, x, y, gap, label[:16], fontsize, color)

################################################################################################
def plotRocketNumberInsideBar(cn_font, ax, yDataList, xuhaoList, rocketList, colorDict, fontsize, upperSrage=None, spotList=None, title=''):
    gap = 0.065
    for x, (c, xuhaos, rockets, spots) in enumerate(zip(yDataList, xuhaoList, rocketList, spotList)):
        for i, (xuhao, rocket, spot) in enumerate(zip(xuhaos.split('/'), rockets.split('/'), str(spots).split('/'))):
            color = 'white' if isDarkColor(colorDict[rocket]) else 'black'
            y = c / 2 if c == 1 else c / 4 + i * c / 2
            y = y * 3.5 if rocket == '春节' else y
            if f'{rocket}{xuhao}' in upperSrage:
                upperStage = upperSrage[f'{rocket}{xuhao}'].split('|')
                if isSingleRocket(ax) and '(火箭)' not in title:
                    withUpperStage = xuhao + '/' + upperStage[0]
                else:
                    withUpperStage = rocket + xuhao + '/' + upperStage[0]
                withUpperStage += f'/{spot[2:].split("（")[0]}' if len(spot) > 1 and spot[1] == '海' else ''
                label = convertStringToArray(withUpperStage)
            else:
                if xuhao.startswith('遥') or xuhao.startswith('天'):
                    if not isSingleRocket(ax) or '(火箭)' in title:
                        xuhao = rocket + xuhao
                    xuhao += f'/{spot[2:].split("（")[0]}' if len(spot) > 1 and spot[1] == '海' else ''
                    label = convertStringToArray(xuhao)
                else:
                    if not isSingleRocket(ax) or '(火箭)' in title:
                        rocket += f'/{spot[2:].split("（")[0]}' if len(spot) > 1 and spot[1] == '海' else ''
                        label = convertStringToArray(rocket)
                        label.append(xuhao)
                    else:
                        label = xuhao
                        label += f'/{spot[2:].split("（")[0]}' if len(spot) > 1 and spot[1] == '海' else ''
            plotRocketNumber(cn_font, ax, x, y, gap, label, fontsize, color)

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
    for i, (y, d) in enumerate(zip(yDataList, xDataList)):
        if i == 0 or d.year != xDataList[i - 1].year:
            ax.text(i+1, y+0.25, str(d.year)[0], ha="center", va="center", fontsize=fontsize)
            ax.text(i+1, y+0.17, str(d.year)[1], ha="center", va="center", fontsize=fontsize)
            ax.text(i+1, y+0.10, str(d.year)[2], ha="center", va="center", fontsize=fontsize)
            ax.text(i+1, y+0.03, str(d.year)[3], ha="center", va="center", fontsize=fontsize)

################################################################################################
def plotVLineBetweenYearsMonths(ax, xDataList, dx=0.5, yMin=-0.24, yMax=0.8, mustPlot=False):
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
            # elif xDataList[0].year == xDataList[-1].year:
            #     if i > 0 and date.month != xDataList[i - 1].month:
            #         ax.axvline(i + 1 - dx, ymin=yMin, ymax=yMax, linestyle='--', clip_on=False)
            else:
                ax.axvline(i + 1 - dx, ymin=yMin, ymax=yMax, linestyle='--', clip_on=False)
                break

################################################################################################
def getLogList(y):
    yList1 = [0.5, 1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 30, 40, 50, 60, 90, 120, 150, 200, 250, 300, 400, 500]
    # yList1 = np.array([0.5, 1, 2, 3, 4, 5, 6, 8, 10, 20, 30, 40, 50, 60, 80, 100, 150, 200, 250, 300, 400, 500])
    yList2 = [800, 1000]
    # yList2 = np.array([600, 700, 800, 900, 1000])
    
    if y >= 500:
        i = int(y / 100 - 5)
        return yList1 + yList2[i:i+1]
    
    for i in range(len(yList1)):
        if y < yList1[i]:
            return yList1[:(i + 1)]
        
    return []

################################################################################################
def countRocketWide(df, columnRocket, rocket, startYear, endYear, seriesDict, use_pinyin=False):
    if rocket == '' or rocket == '全部' or rocket == '系列':
        if rocket == '系列':
            df = ChangeToSeriesName(df, columnRocket, seriesDict)
        cond1 = df[columnRocket].str.startswith('长征')
        cond1 |= ~df[columnRocket].str.startswith('长征')
    elif rocket == '长征':
        cond1 = df[columnRocket].str.startswith(rocket)
    elif rocket == '其他':
        cond1 = ~df[columnRocket].str.startswith('长征')
    elif rocket == '民营':
        privates = myUtils.readConfig(['PrivatesPrefix'])
        cond1 = False
        for private in privates:
            cond1 |= df[columnRocket].str.startswith(private)
    cond1 &= ~df[columnRocket].str.startswith('远征')

    if startYear:
        columnYear = '日期'
        cond1 &= df[columnYear] >= pd.to_datetime(f'{startYear}0101')

    if endYear:
        columnYear = '日期'
        cond1 &= df[columnYear] < pd.to_datetime(f'{endYear}0101')
#TODO: modify chinese to pinyin when use_pinyin
    return df[cond1]

################################################################################################
def countDataFrameByDate(dfList):
    dfCountList = []
    # dfCount = dfList[0].copy()
    count = len(dfList)

    for i in range(count):
        dfCount = dfList[i].copy()

        # appending a new column 发射数 to count the same 日期
        dfCount['发射数'] = dfCount.groupby('日期')['日期'].transform('count')

        # Concate other columns with the same 日期
        try:
            dfCount[myExcel.EXCEL_COLUMN_ROCKET] = dfCount.groupby([myExcel.EXCEL_COLUMN_DATE])[myExcel.EXCEL_COLUMN_ROCKET].transform(lambda x: '/'.join(x))
            dfCount[myExcel.EXCEL_COLUMN_NUMBER] = dfCount.groupby([myExcel.EXCEL_COLUMN_DATE])[myExcel.EXCEL_COLUMN_NUMBER].transform(lambda x: '/'.join(x))
            dfCount[myExcel.EXCEL_COLUMN_PAYLOAD] = dfCount.groupby([myExcel.EXCEL_COLUMN_DATE])[myExcel.EXCEL_COLUMN_PAYLOAD].transform(lambda x: '/'.join(x))
            dfCount[myExcel.EXCEL_COLUMN_LOCATION] = dfCount.groupby([myExcel.EXCEL_COLUMN_DATE])[myExcel.EXCEL_COLUMN_LOCATION].transform(lambda x: '/'.join(x))
            dfCount[myExcel.EXCEL_COLUMN_RESULT] = dfCount.groupby([myExcel.EXCEL_COLUMN_DATE])[myExcel.EXCEL_COLUMN_RESULT].transform(lambda x: '/'.join(x))
            dfCount[myExcel.EXCEL_COLUMN_SPOT] = dfCount.groupby([myExcel.EXCEL_COLUMN_DATE])[myExcel.EXCEL_COLUMN_SPOT].transform(lambda x: '/'.join(str(i) for i in x))
        except:
            pass
        dfCount = dfCount.groupby('日期').first().reset_index()
        dfCountList.append(dfCount)
    return dfCountList

################################################################################################
def countRocket(df, columnRocket, rocket, seriesDict=None):
    if columnRocket is not None:
        if isinstance(rocket, list):
            cond1 = df[columnRocket].isin(rocket)
        elif rocket == '' or rocket == '全部':
            cond1 = df[columnRocket].str.startswith('长征')
            cond1 |= ~df[columnRocket].str.startswith('长征')
            cond1 &= ~df[columnRocket].str.startswith('远征')
        elif rocket == '长征':
            cond1 = df[columnRocket].str.startswith(rocket)
        elif rocket == '其他':
            cond1 = ~df[columnRocket].str.startswith('长征')
            cond1 &= ~df[columnRocket].str.startswith('远征')
        elif rocket == '民营':
            privates = myUtils.readConfig(['PrivatesPrefix'])
            cond1 = False
            for private in privates:
                cond1 |= df[columnRocket].str.startswith(private)
# TODO: use config.ini and seriesDict to or 
        elif rocket == '长征三号甲系列':
            cond1 = df[columnRocket].str.startswith('长征三号甲')
            cond1 |= df[columnRocket].str.startswith('长征三号乙')
            cond1 |= df[columnRocket].str.startswith('长征三号丙')
        elif rocket == '星河系列':
            cond1 = df[columnRocket].str.startswith('谷神星')
            cond1 |= df[columnRocket].str.startswith('智神星')
        elif rocket[-2:] == '系列':
            cond1 = df[columnRocket].str.startswith(rocket[:-2])
        # elif rocket == '长征四号系列':
        #     cond1 = df[columnRocket].str.startswith('长征四号')
        # elif rocket == '长征五号系列':
        #     cond1 = df[columnRocket].str.startswith('长征五号')
        # elif rocket == '长征六号系列':
        #     cond1 = df[columnRocket].str.startswith('长征六号')
        # elif rocket == '长征七号系列':
        #     cond1 = df[columnRocket].str.startswith('长征七号')
        # elif rocket == '长征十一号系列':
        #     cond1 = df[columnRocket].str.startswith('长征十一号')
        # elif rocket == '快舟系列':
        #     cond1 = df[columnRocket].str.startswith('快舟')
        # elif rocket == '朱雀系列':
        #     cond1 = df[columnRocket].str.startswith('朱雀')
        # elif rocket == '捷龙系列':
        #     cond1 = df[columnRocket].str.startswith('捷龙')
        # elif rocket == '谷神星系列':
        #     cond1 = df[columnRocket].str.startswith('谷神星')
        # elif rocket == '力箭系列':
        #     cond1 = df[columnRocket].str.startswith('力箭')
        # elif rocket == '天龙系列':
        #     cond1 = df[columnRocket].str.startswith('天龙')
        # elif rocket == '引力系列':
        #     cond1 = df[columnRocket].str.startswith('引力')
        else:
            cond1 = df[columnRocket] == rocket
    return df[cond1] if cond1 is not None else df

################################################################################################
def readDataFromSheetNew(excelFile, sheetName, onlyFailed=False):
    df = pd.read_excel(excelFile, sheetName, header=0, usecols='A:O', dtype={myExcel.EXCEL_COLUMN_SPOT: str})
    cond1 = df[myExcel.EXCEL_COLUMN_RESULT] != '中止'
    cond2 = ~df[myExcel.EXCEL_COLUMN_RESULT].isna()
    # cond3 = df[myExcel.EXCEL_COLUMN_RESULT] != '成功'
    df = df[cond1 & cond2]
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
        cond1 = df[columnNotNull] != '中止' 
        cond1 &= df[columnNotNull].ne('')  # filter to exclude rows where 结果 is ''
        df = df[cond1] 

    if onlyFailed:
        df = df[(df[columnNotNull] != '成功')]
    return df

################################################################################################
def readDataFromBook(excelBook, sheetName, headers, columnNotNull, columnRocket, noAbort, onlyFailed):
    excelSheet = excelBook[sheetName]
    return readDataFromSheet(excelSheet, headers, columnNotNull, columnRocket, noAbort, onlyFailed)

################################################################################################
def mergeData(dfPivot, dfPivotOk, columnYear):
    def custom_logic(row, index):
        result = {} 
        retiredRocketsDict = myUtils.readConfigRetiredDict() #myExcel.RETIRED_ROCKETS
        for column, value in row.items():
            if column in retiredRocketsDict:
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

# if __name__ == "__main__":
#     seriesDict = myUtils.readConfigSeriesDictList()
    
################################################################################################
def ChangeToSeriesName(df, columnRocket, seriesDict):
    if seriesDict is None:
        seriesDict = myUtils.readConfigSeriesDictList()
        # seriesDict = myExcel.ROCKET_SERIES
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
def readUpperStageDictOld(excelSheet, headers=None):
    dfList = parseExcelSheetToDataFrame(excelSheet, headers=headers, rocket='上面级+最后发射')
    dfUpperStages = dfList[:-1] # 上面级
    dfLastLaunch = dfList[-1] # 最后的发射
    dictUpperStage = getUpperStageDict(dfUpperStages)
    return dictUpperStage, dfLastLaunch

################################################################################################
def readUpperStageDict(df):
    dfList = parseToDataFrame(df, rocket='上面级+最后发射')
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
        columnRocket='火箭', columnLocation='地点', columnPayload='载荷', 
        columnYear='日期', columnNotNull='结果', 
        headers=None, noAbort=True, mom=False,
        onlyFailed=False, isRocket=False, isAfterRetired=None, 
        seriesDict=None, isMaiden=False, isFirstLast=False, isLunarNewYear=False, 
        plotMonth=None, plotLocation=False):
    df = readDataFromSheet(excelSheet, headers, columnNotNull, columnRocket, noAbort, onlyFailed)
    return parseToDataFrame(df, rocket, location, payload, startYear, endYear, columnRocket, columnLocation, columnPayload, 
        columnYear, columnNotNull, headers, noAbort, mom, onlyFailed, isRocket, isAfterRetired, seriesDict, 
        isMaiden, isFirstLast, isLunarNewYear, plotMonth, plotLocation)

################################################################################################
def parseExcelBookToDataFrame(excelBook, sheetName, 
        rocket:str=None, location=None, payload=None, startYear=None, endYear=None, 
        columnRocket='火箭', columnLocation='地点', columnPayload='载荷', 
        columnYear='日期', columnNotNull='结果', 
        headers=None, noAbort=True, mom=False,
        onlyFailed=False, isRocket=False, isAfterRetired=None, 
        seriesDict=None):
    df = readDataFromBook(excelBook, sheetName, headers, columnNotNull, columnRocket, noAbort, onlyFailed)
    return parseToDataFrame(df, rocket, location, payload, startYear, endYear, columnRocket, columnLocation, columnPayload, 
        columnYear, columnNotNull, headers, noAbort, mom, onlyFailed, isRocket, isAfterRetired, seriesDict)

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
def parseFirstLast(df, columnYear):
    dfResult = pd.DataFrame()
    df = df[~df[columnYear].isnull()]
    # df[columnYear] = pd.to_datetime(df[columnYear]).dt.date
    dfResult = df.groupby(df[columnYear].apply(lambda x: x.year)).apply(getDfFirstlast, columnYear).reset_index(drop=True)
    dfResult = dfResult.sort_values(columnYear).reset_index(drop=True)
    return dfResult

################################################################################################
def parseLunarNewYear(df, columnYear, columnRocket, columnLocation, columnNotNull):
    df = df[~df[columnYear].isnull()]
    lunarNewYearDates = myUtils.readConfig(['LunarNewYear'])
    lunarNewYearDates = [pd.Timestamp(x, unit='D') for x in lunarNewYearDates]
    dfLunarNewYears = pd.DataFrame({
        columnRocket: ['春节'] * len(lunarNewYearDates),
        columnYear: lunarNewYearDates,
        columnLocation: '中国',
        columnNotNull: '成功',
        '序号': '',
        '载荷': '',
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
    return dfResult

################################################################################################
def convertDataFrame2WideRocket(df, columnYear, columnRocket, columnNotNull, rocket, startYear, endYear, seriesDict, isAfterRetired, use_pinyin=False):
    dfList = []
    df = countRocketWide(df, columnRocket, rocket, startYear, endYear, seriesDict, use_pinyin)
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
    retiredRocketsDict = myUtils.readConfigRetiredDict() #myExcel.RETIRED_ROCKETS

    if isAfterRetired:
        dfRank = pd.DataFrame(index=dfPivot.index)
        for label, date_value in retiredRocketsDict.items():
            conditionColumn = (dfPivot.columns == label)
            if conditionColumn.any():
                dfTemp_label = np.where(conditionColumn, dfPivot + dfPivotOk / 1000, dfPivot * 1000 + dfPivotOk / 1000)
                conditionRow = (dfPivot.index >= date_value)
                dfTemp_date = np.where(conditionRow[:, np.newaxis], dfTemp_label, dfPivot * 1000 + dfPivotOk / 1000)
                df_temp_result = pd.DataFrame(dfTemp_date, columns=dfPivot.columns, index=dfPivot.index)
                if dfRank.empty:
                    dfRank = df_temp_result.copy()
                else:
                    dfRank[label] = df_temp_result[label]
        if dfRank.empty:
            dfRank = dfPivot * 1000 + dfPivotOk / 1000    # convert to float
    elif isAfterRetired == False:
        # retiredRocketsDict = myUtils.readConfigRetiredDict #myExcel.RETIRED_ROCKETS
        condition = dfPivot.columns.isin(retiredRocketsDict)
        dfTemp = np.where(condition, dfPivot + dfPivotOk / 1000, dfPivot * 1000 + dfPivotOk / 1000)
        dfRank = pd.DataFrame(dfTemp, columns=dfPivot.columns, index=dfPivot.index)
    else:
        dfRank = dfPivot * 1000 + dfPivotOk / 1000    # convert to float

    dfList.append(dfRank)
    dfList.append(dfOk)
    dfList.append(dfAll)
    return dfList

def parseMonthData(df, columnYear, plotMonth):
    dfResult = df[df[columnYear].apply(lambda x: x.month) == plotMonth]
    return dfResult

def parseLocationData(df, columnRocket, columnLocation, columnNotNull, columnYear, startYear=None):
    df = df[~df[columnRocket].str.startswith('远征')]
    if startYear:
        df = df[df[columnYear].apply(lambda x: x.year) == int(startYear)]
    dfAll = df.groupby(columnLocation).size().reset_index(name='全部发射数')
    dfAllOk = df[df[columnNotNull].str.startswith('成功')].groupby(columnLocation).size().reset_index(name='全部成功数')
    dfCZ = df[df[columnRocket].str.startswith('长征')].groupby(columnLocation).size().reset_index(name='长征发射数')
    dfCZOk = df[df[columnRocket].str.startswith('长征') & df[columnNotNull].str.startswith('成功')].groupby(columnLocation).size().reset_index(name='长征成功数')
    dfNCZ = df[~df[columnRocket].str.startswith('长征')].groupby(columnLocation).size().reset_index(name='其他发射数')
    dfNCZOk = df[~df[columnRocket].str.startswith('长征') & df[columnNotNull].str.startswith('成功')].groupby(columnLocation).size().reset_index(name='其他成功数')
    dfResult = pd.merge(dfAll, dfAllOk, on=columnLocation, how='left')
    dfResult = pd.merge(dfResult, dfCZ, on=columnLocation, how='left')
    dfResult = pd.merge(dfResult, dfCZOk, on=columnLocation, how='left')
    dfResult = pd.merge(dfResult, dfNCZ, on=columnLocation, how='left')
    dfResult = pd.merge(dfResult, dfNCZOk, on=columnLocation, how='left')
    dfResult.fillna(0, inplace=True)
    dfResult['长征发射数'] = dfResult['长征发射数'].astype(int)
    dfResult['长征成功数'] = dfResult['长征成功数'].astype(int)
    dfResult['其他发射数'] = dfResult['其他发射数'].astype(int)
    dfResult['其他成功数'] = dfResult['其他成功数'].astype(int)
    dfSort = dfResult.sort_values(by='全部发射数', ascending=False)
    dfSum = dfSort.sum().to_frame().T
    dfSum[columnLocation] = '合计'
    dfLast = pd.concat([dfSort, dfSum], ignore_index=True)
    dfLast['全部成功率'] = [ok / all if all != 0 else 0 for ok, all in zip(dfLast['全部成功数'], dfLast['全部发射数'])] 
    dfLast['长征成功率'] = [ok / all if all != 0 else 0 for ok, all in zip(dfLast['长征成功数'], dfLast['长征发射数'])]
    dfLast['其他成功率'] = [ok / all if all != 0 else 0 for ok, all in zip(dfLast['其他成功数'], dfLast['其他发射数'])]
    return dfLast

def getEndRow(row):
    return row.replace(hour=23, minute=59, second=59)

################################################################################################
def convertDataFrame2TimeSeries(df, use_pinyin=False):
    # myUtils.setStartTime()
    removeColumns = ['发射日期', '着陆日期', '在轨日数', '载人飞船', 'Ship', '备注']  
    removeColumns += ['出生日期', '年龄', '入选年', '批次', '日差']
    removeColumns.append('航天员') if use_pinyin else removeColumns.append('Pinyin')

    df['日期'] = df.apply(lambda row: pd.date_range(row['发射日期'], 
                      min(pd.to_datetime(myUtils.getJapanDate()), row['着陆日期'])), axis=1)
    df = (df.drop(columns=removeColumns).explode('日期', ignore_index=True)
          .sort_values(by=['日期', 'Rank']).reset_index(drop=True))
    df.columns = ['航天员', 'Rank', '日期']
    return df

################################################################################################
def convertDataFrame2TWideTaikonaut(dfOld, use_pinyin=False):
    dfTimeSeries = convertDataFrame2TimeSeries(dfOld, use_pinyin)
    dfList = []
    df = dfTimeSeries.copy()

    df['count'] = np.where(df.航天员.duplicated(), 1, 0)
    column_order = df['航天员'].unique() # Reorder columns to match the original order
    dfPivot = df.pivot_table(index='日期', columns='航天员', 
                             values='count', aggfunc='sum', fill_value=0)[column_order]
    dfPivot.reset_index(inplace=True)
    dfPivot['日期'].iloc[-1] = dfPivot['日期'].iloc[-1].replace(hour=23, minute=59, second=59)
    dfPivot = dfPivot.set_index('日期').cumsum()

    dfRank = dfPivot.copy()
    columnTaiko = 'Pinyin' if use_pinyin else '航天员'
    for startDate, endDate, person in zip(dfOld['发射日期'], dfOld['着陆日期'], dfOld[columnTaiko]):
        dfRank.loc[startDate : endDate, person] += 1000 #在轨期间优先排序

    dfList.append(dfPivot)
    dfList.append(dfRank)
    return dfList

################################################################################################
def convertDataFrame2TimeSeriesOld(df):
    myUtils.setStartTime()
    newRows = []

    # Iterate over each row in the original DataFrame
    for _, row in df.iterrows():
        startDate = row['发射日期']
        endDate = min(pd.to_datetime(myUtils.getJapanDate()), row['着陆日期'])
        name = row['航天员']
        rank = row['Rank']
        dateRange = pd.date_range(start=startDate, end=endDate)

        for date in dateRange:
            newRow = {'日期' : pd.to_datetime(date), '航天员': name, 'Rank': rank}
            newRows.append(newRow)

    dfDuplicateDates = pd.DataFrame(newRows)
    dfDuplicateDates.sort_values(by=['日期', 'Rank'], inplace=True)

    # Reset index to ensure a clean DataFrame
    dfDuplicateDates.reset_index(drop=True, inplace=True)
    myUtils.showRunTime()
    return dfDuplicateDates

################################################################################################
def InterpolateGapTime(df):
    dfNew = df.copy()
    threshold_months = 1

    for idx in range(len(df) - 1):
        diff_months = (df.index[idx + 1] - df.index[idx]).days // 30
        if diff_months > threshold_months:
            start_date = df.index[idx]
            end_date = df.index[idx + 1]
            dates = pd.date_range(start=start_date, end=end_date, freq='MS')  # 'MS' = month start
            df_interpolate = pd.DataFrame(index=dates)
            df_interpolated = df_interpolate.interpolate(method='ffill')
            # dfBackward = dfNew.loc[start_date : end_date].bfill()
            # df_interpolated = df_interpolated.combine_first(dfBackward.loc[start_date:end_date])
            df_interpolated = df_interpolated.combine_first(dfNew.loc[start_date:end_date])
            dfNew = pd.concat([dfNew, df_interpolated])

    dfNew.sort_index(inplace=True)
    # dfNew.reset_index(inplace=True)
    dfNew.index.name = df.index.name
    return dfNew

################################################################################################
def parseToDataFrame(dfOld, rocket:str=None, location=None, payload=None, startYear=None, endYear=None, 
                               columnRocket='火箭', columnLocation='地点', columnPayload='载荷', 
                               columnYear='日期', columnNotNull='结果', 
                               headers=None, noAbort=True, mom=False,
                               onlyFailed=False, isRocket=False, isAfterRetired=None, 
                               seriesDict=None, isMaiden=False, isFirstLast=False, isLunarNewYear=False, 
                               plotMonth=None, plotLocation=False, isShenzhou=False, use_pinyin=False):
    dfList = []
    
    if onlyFailed:
        df = dfOld[dfOld[myExcel.EXCEL_COLUMN_RESULT] != '成功']
    else:
        df = dfOld.copy()

    # convert df to wide for plot race bar chart
    if isShenzhou:
        dfList = convertDataFrame2TWideTaikonaut(df, use_pinyin) 
    elif isRocket:
        dfList = convertDataFrame2WideRocket(df, columnYear, columnRocket, columnNotNull, rocket, startYear, endYear, seriesDict, isAfterRetired, use_pinyin)

    # Extract rows by condition
    elif plotLocation:
        dfList = parseLocationData(df, columnRocket, columnLocation, columnNotNull, columnYear, startYear)
    elif plotMonth:
        dfList = split50perPage(parseMonthData(df, columnYear, plotMonth))
    elif isFirstLast:
        dfList = split50perPage(parseFirstLast(df, columnYear))
    elif isLunarNewYear:
        dfList = split50perPage(parseLunarNewYear(df, columnYear, columnRocket, columnLocation, columnNotNull))
    elif isMaiden:
        dfAll = df.groupby(columnRocket).head(1)
        dfCZ = dfAll[dfAll[columnRocket].str.startswith('长征')]
        dfNCZ = dfAll[~dfAll[columnRocket].str.startswith('长征')]
        dfList.append(dfAll)
        dfList.append(dfCZ)
        dfList.append(dfNCZ)

    elif startYear:
        if endYear is None:
            endYear = startYear

        if columnYear is None:
            columnYear = '日期' #df.columns[0]

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
                mmdd = endYMD[4:] if endYMD[4:] != '0229' else '0228'
                lastEndYMD = f'{lastYear}{mmdd}'
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

    elif location:
        if columnLocation is not None:
            if isinstance(location, list):
                cond1 = df[columnLocation].isin(location)
            else:
                cond1 = df[columnLocation] == location
            df = df[cond1]
            dfList = split50perPage(df)

    elif payload:
        if columnPayload is not None:
            if isinstance(payload, list):
                cond1 = df[columnPayload].isin(payload)
            else:
                if payload == '空间站':
                    cond1 = df[columnPayload].str.startswith('天宫')
                    cond1 |= df[columnPayload].str.startswith('梦天')
                    cond1 |= df[columnPayload].str.startswith('问天')
                    cond1 |= df[columnPayload].str.startswith('巡天')
                    cond1 |= df[columnPayload].str.startswith('神舟')
                    cond1 |= df[columnPayload].str.startswith('天舟')
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

    else:
        cond1 = ~df[columnRocket].str.startswith('远征')
        dfSelected = df[cond1]        
        dfList.append(dfSelected)
    return dfList

################################################################################################
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

def split50perPage(df, count=50):
    dfList = []
    if len(df) > count:
        dfList = dict(list(df.groupby(np.arange(len(df)) // count)))
    else:
        dfList.append(df)
    return dfList

def getUnique20Colors(index: int):
    return plt.cm.tab20(index)

def getUniqueColorList(n: int):
    colorList = list(mpl.colors.CSS4_COLORS.values())
    random.shuffle(colorList)
    return colorList[:n]



