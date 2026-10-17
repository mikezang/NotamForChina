from timeit import timeit
from datetime import timedelta
from sortedcontainers import SortedDict

from myModules import myExcel
from myModules import myPlotInit
from myModules import myPlot
from myModules import myShape
from myModules import myHtml
from myModules import myFile

TEMP_FILE_PATH = './htmls/'
DATA_FILE_PATH = './data/'

################################################################################################
def reverseLocation(loc, spot):
    if '/' in loc:
        tempLoc = loc.split('/')
        tempLoc.reverse()
        tempSpot = spot.split('/')
        tempSpot.reverse()
        tempLocNew = [l.replace('海上', s[:2]) for l, s in zip(tempLoc, tempSpot)]
        return '/'.join(tempLocNew)
    else:
        loc = loc.replace('海上', spot[:2])
        return loc
    
################################################################################################
def plotBarGraphByDate(cn_font, ax, df, colorDict=None, fontsize=12, upperStages=None, isMaiden=False, plotPayload=False, payload=None, title=''):
    from cn2an import an2cn
    # Extract plot data
    xDataList = list(df[myExcel.EXCEL_COLUMN_DATE])
    yDataList = list(df['发射数'])
    rocketList = list(df[myExcel.EXCEL_COLUMN_ROCKET])
    xuhaoList = list(df[myExcel.EXCEL_COLUMN_NUMBER])
    upperList = list(df[myExcel.EXCEL_COLUMN_REMARKS])
    payloadList = list(df[myExcel.EXCEL_COLUMN_PAYLOAD])
    resultList = list(df[myExcel.EXCEL_COLUMN_RESULT])
    locationList = list(df[myExcel.EXCEL_COLUMN_LOCATION])
    spotList = list(df[myExcel.EXCEL_COLUMN_SPOT])
    xTickList = list(range(1, len(xDataList) + 1))
    xTicksLabelList = [f'{reverseLocation(l, s)}{an2cn(str(d.month))}月{an2cn(str(d.day))}日' for d, l, s in zip(xDataList, locationList, spotList)]
    colorDict = colorDict if colorDict else getColorDict(df)

    # Plot bar with the same color for the same rokect
    for i in range(len(xDataList)):
        bottom = 0
        # edgecolor = None
        edgecolor = 'black'
        for rocket, okNg in zip(rocketList[i].split('/'), (resultList[i].split('/') if resultList[i] else [])):
            color = colorDict[rocket]
            hatch = None if okNg == '成功' else '/'
            y = 2 if rocket == '春节' else 1
            bars = ax.bar(xTickList[i], y, label=rocket, bottom=bottom, color=color, hatch=hatch, edgecolor=edgecolor)
            colorDict[rocket] = bars[0].get_facecolor()
            bottom += y

    if plotPayload:
        # Plot 载荷 text inside bar
        myPlot.plotPayloadInsideBar(cn_font, ax, yDataList, rocketList, payloadList, colorDict, fontsize, payload)
    else:
        # Plot 火箭遥号 text inside bar
        myPlot.plotRocketNumberInsideBar(cn_font, ax, yDataList, xuhaoList, rocketList, upperList, colorDict, fontsize, upperStages, spotList, title=title)

    # Plot year on top of bar when startYear is different from endYear
    myPlot.plotYearOnTopOfBar(ax, xDataList, yDataList)

    # Set x axis
    xMax = xTickList[-1] + 0.5
    myPlot.plotXAxis(cn_font, ax, '发射日期', xTickList, xTicksLabelList, 0.5, xMax, fontsize)

    # Set y axis
    yTicks = list(range(1, int(max(yDataList) + 1)))
    yMax = max(yDataList) + 0.5 if len(colorDict) < 5 else max(yDataList) + 0.5 + 0.1 * len(colorDict) / 5
    myPlot.plotYAxis(cn_font, ax, '发射数', yTicks, 0, yMax, 14)

    # Plot line between months/years
    myPlot.plotVLineBetweenYearsMonths(ax, xDataList)

################################################################################################
def plotTitleLegendByDate(cn_font, ax, title, df, okRate=None, page=0, isSeries=False, isMaiden=False, isLunarNewYear=False, isFirstLast=False, plotPayload=False):
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    # get handles and labels
    handles, labels = ax.get_legend_handles_labels()
    singleRocket = myPlot.isSingleRocket(ax)

    # Found if there is launch failed
    df['结果'] = df['结果'].str.split('/') # Split by '/' and explode
    df = df.explode('结果')
    counts = df['结果'].value_counts() # Count occurrences of each value
    countsLunarNewYear = df[df['火箭'] == '春节']['火箭'].value_counts()
    sumAll = counts.sum() - countsLunarNewYear.sum()
    sumOk = counts.get('成功', 0) - countsLunarNewYear.sum()
    sumNg =  sumAll - sumOk # Subtract sum of 'ok' from total count to get sum of non-'ok' values

    # create dictionary of unique labels and their corresponding handles
    uniqueLabels, labelCounts = {}, {}
    for label, handle in zip(labels, handles):
        if label not in uniqueLabels:
            labelCounts[label] = 1
            uniqueLabels[label] = handle
        else:
            labelCounts[label] += 1

    # create new lists of handles and labels without duplicates
    newHandles = list(uniqueLabels.values())
    newLabels = list(uniqueLabels.keys())
    newCounts = list(labelCounts.values())
    if '首飞日' not in title:
        newLabels = [f'发射成功 x {c - sumNg}' if singleRocket and not plotPayload and not isSeries else f'{l} x {c}' for l, c in zip(newLabels, newCounts)]

    for i, handle in enumerate(newHandles):
        color = handle.patches[0].get_facecolor()
        colorPatch = mpatches.Patch(hatch='', facecolor=color, edgecolor='black')
        newHandles[i] = colorPatch

    # Plot Failed counts
    if sumNg > 0:
        failedPatch = mpatches.Patch(hatch='///', facecolor='none', edgecolor='black') # Create a new Patch object with a hatch pattern
        newHandles.append(failedPatch) # Add the new Patch object to the handles list
        newLabels.append(f'发射失败 x {sumNg}') # Add the 'failed' label to the labels list

    if singleRocket and okRate is not None:
        ratePatch = mpatches.Patch(hatch='+', facecolor='none', edgecolor='black') 
        newHandles.append(ratePatch) 
        newLabels.append(f'全发射成功率 = {okRate:.0%}') 

    if isMaiden:
        ratePatch = mpatches.Patch(hatch='+', facecolor='none', edgecolor='black') 
        newHandles.append(ratePatch) 
        newLabels.append(f'首飞成功率 = {okRate:.0%}') 

    # move '春节' to last
    if isLunarNewYear:
        moveLabel = [item for item in newLabels if '春节' in item][0]
        moveIndex = newLabels.index(moveLabel)
        moveHandle = newHandles[moveIndex]
        newLabels.pop(moveIndex)
        newHandles.pop(moveIndex)
        newLabels.append(moveLabel)
        newHandles.append(moveHandle)

    # Plot all counts
    allPatch = mpatches.Patch(facecolor='none', edgecolor='black') # Create a new Patch object with a hatch pattern
    newHandles.append(allPatch) # Add the new Patch object to the handles list
    newLabels.append(f'合计 = {sumAll}') # Add the 'failed' label to the labels list
    if page > 0:
        sumAll += page * 50
        newHandles.append(allPatch) # Add the new Patch object to the handles list
        newLabels.append(f'总计 = {sumAll}') # Add the 'failed' label to the labels list

    # set new handles and labels back to the bar plot
    ncols = myPlot.calcColsPerLine(newLabels)
    ax.legend(newHandles, newLabels , loc='upper center', prop={'family': cn_font.get_name(), 'size': 12}, ncol=ncols)
    plt.title(title, fontproperties=cn_font, fontsize=18)
    return singleRocket

# 1月年初12月年末发射日统计
################################################################################################
def plotGraphForFirstLast(cn_font, df, upperStages):
    dfList = myPlot.parseToDataFrame(df, columnDate='日期', columnNotNull='结果', isFirstLast=True)
    dfList = myPlot.countDataFrameByDate(dfList)
    # series = ['全部', '长征', '其他']
    series = ['全部']

    for df, s in zip(dfList, series):
        if not df.iloc[0:, :].empty:
            colorDict = getColorDict(df)
            okRate = getOkRate([df])
            title = f'中国{s}运载火箭年初年末发射日统计'
            # fig, axLeft = plt.subplots(nrows=1, ncols=1, figsize=(20, 10)) 
            fig, axLeft =  myShape.getFigure()
            plotBarGraphByDate(cn_font, axLeft, df, upperStages=upperStages, colorDict=colorDict)
            plotTitleLegendByDate(cn_font, axLeft, title, df, okRate=okRate, isFirstLast=True)
            myPlot.showBackend()
            myPlot.saveFig(fig, f'./images/{title}.png') # Save the plot to a file

# 1月2月春节前后发射日统计
################################################################################################
def plotGraphForLunarNewYear(cn_font, df, upperStages, printLast=True):
    dfList = myPlot.parseToDataFrame(df, columnDate='日期', columnNotNull='结果', isLunarNewYear=True)
    dfList = myPlot.countDataFrameByDate(dfList)
    count = len(dfList)
    colorDict = getColorDict(dfList)

    for no, df in enumerate(dfList, 1):
        if not printLast or no == len(dfList):
            if not df.iloc[0:, :].empty:
                okRate = getOkRate([df])
                title = f'中国全部运载火箭春节前后发射日统计'
                title += str(no) if count > 1 else ''
                # fig, axLeft = plt.subplots(nrows=1, ncols=1, figsize=(20, 10)) 
                fig, axLeft =  myShape.getFigure()
                plotBarGraphByDate(cn_font, axLeft, df, upperStages=upperStages, colorDict=colorDict)
                plotTitleLegendByDate(cn_font, axLeft, title, df, okRate=okRate, isLunarNewYear=True)
                myPlot.showBackend()
                myPlot.saveFig(fig, f'./images/{title}.png') # Save the plot to a file

# 首飞发射日统计
################################################################################################
def plotGraphForMaiden(cn_font, df, upperStages, seriesChecked, printLast=True):
    from myModules import myDataFrame
    dfList = myPlot.parseToDataFrame(df, columnDate='日期', columnNotNull='结果', isMaiden=True)
    dfList = myPlot.countDataFrameByDate(dfList)
    series = ['全部', '长征', '其他']

    for df, s in zip(dfList, series):
        if s in seriesChecked:
            dfListPage = myDataFrame.splitToPages(df)
            dfListPage = myPlot.countDataFrameByDate(dfListPage)
            okRate = getOkRate(dfListPage)
            
            for no, dfPage in enumerate(dfListPage, 1):
                if not dfPage.iloc[0:, :].empty and (not printLast or no == len(dfListPage)):
                    colorDict = getColorDict(dfPage)
                    title = f'中国{s}运载火箭首飞日统计'
                    title += f'{no}' if len(dfListPage) > 1 else ''
                    fig, axLeft =  myShape.getFigure()
                    plotBarGraphByDate(cn_font, axLeft, dfPage, upperStages=upperStages, colorDict=colorDict, isMaiden=True)
                    plotTitleLegendByDate(cn_font, axLeft, title, dfPage, okRate=okRate, isMaiden=True)
                    myPlot.showBackend()
                    myPlot.saveFig(fig, f'./images/{title}.png') # Save the plot to a file

LAUNCH_DATES_BY_YEAR = "01.年度别发射日统计"
################################################################################################
def plotGraphByDate(cn_font, df, title, startYear, endYear=None, upperStages=None, seriesDict=None, printLast=True):
    from myModules import myDataFrame
    df = myPlot.parseToDataFrame(df, startYear=startYear, endYear=endYear, columnDate='日期', columnNotNull='结果', seriesDict=seriesDict)
    dfList = myDataFrame.splitToPages(df[0])
    dfList = myPlot.countDataFrameByDate(dfList)

    for i, df in enumerate(dfList, 1):
        if not df.iloc[0:, :].empty:
            if not printLast or (printLast and i == len(dfList)):
                colorDict = getColorDict(df)
                fig, axLeft =  myShape.getFigure()
                newTitle = f'{myPlot.getPlotTitle(title, startYear, endYear)}'
                newTitle += f'{i}' if len(dfList) > 1 else ''
                plotBarGraphByDate(cn_font, axLeft, df, upperStages=upperStages, colorDict=colorDict)
                plotTitleLegendByDate(cn_font, axLeft, newTitle, df, page=i-1)
                myPlot.showBackend()
                myPlot.saveFig(fig, f'./images/{LAUNCH_DATES_BY_YEAR}/{newTitle}.png') # Save the plot to a file

################################################################################################
def getOkRate(dfList):
    ok, ng = 0, 0
    for df in dfList:
        condition = df['结果'] == '成功'
        ok += df['结果'][condition].count()
        ng += df['结果'][~condition].count()
    return ok / (ok + ng) if ok + ng > 0 else 0

# Plot single rocket
LAUNCH_DYAS_BY_ROCKET = "11.火箭别发射日统计"
LAUNCH_DYAS_BY_SERIES = "12.系列别发射日统计"
################################################################################################
def plotGraphByRocketDate(cn_font, df, title, rocket, retired=False, upperStages=None, plotLast=True, seriesDict=None):
    dfList = myPlot.parseToDataFrame(df, rocket=rocket, seriesDict=seriesDict)
    dfList = myPlot.countDataFrameByDate(dfList)
    okRate = getOkRate(dfList)
    colorDict = getColorDict(dfList)

    for i, df in enumerate(dfList):
        if not df.iloc[0:, :].empty and (i == len(dfList) - 1 or not plotLast):
            nodate = True if i < len(dfList) - 1 or retired else False
            no = '' if len(dfList) == 1 else f'{i + 1}'
            newTitle = myPlot.getPlotTitle(f'{title}{no}', retired=retired, nodate=nodate)
            # fig, axLeft = plt.subplots(nrows=1, ncols=1, figsize=(20, 10)) 
            fig, axLeft =  myShape.getFigure()
            plotBarGraphByDate(cn_font, axLeft, df, fontsize=12, upperStages=upperStages, colorDict=colorDict)
            singleRocket = plotTitleLegendByDate(cn_font, axLeft, newTitle, df, okRate, page=i)
            
            myPlot.showBackend()
            
            if retired:
                if singleRocket:
                    path = f'./images/{LAUNCH_DYAS_BY_ROCKET}/退役/{newTitle}.png'
                else:
                    path = f'./images/{LAUNCH_DYAS_BY_SERIES}/退役/{newTitle}.png'
            else:
                path = f'./images/{LAUNCH_DYAS_BY_ROCKET}/{newTitle}.png'

            myPlot.saveFig(fig, path) # Save the plot to a file

################################################################################################
def plotGraphByPayloadDate(cn_font, df, title, payload, upperStages=None, plotLast=True, seriesDict=None):
    dfList = myPlot.parseToDataFrame(df, payload=payload, seriesDict=seriesDict)
    dfList = myPlot.countDataFrameByDate(dfList)

    for i, df in enumerate(dfList):
        if i == len(dfList) - 1 or not plotLast:
            if not df.iloc[0:, :].empty:
                no = '' if len(dfList) == 1 else f'{i + 1}'
                dfCopy =df.copy()

                # Plot rocket
                # fig, axLeft = plt.subplots(nrows=1, ncols=1, figsize=(20, 10)) 
                fig, axLeft =  myShape.getFigure()
                newTitleRocket = myPlot.getPlotTitle(f'{title}{no}') + '(火箭)'
                plotPayload(fig, axLeft, cn_font, newTitleRocket, df, i, upperStages) 

                # Plot payload
                # fig, axLeft = plt.subplots(nrows=1, ncols=1, figsize=(20, 10)) 
                fig, axLeft =  myShape.getFigure()
                newTitlePayload = myPlot.getPlotTitle(f'{title}{no}') + '(载荷)'
                plotPayload(fig, axLeft, cn_font, newTitlePayload, dfCopy, i, upperStages, True, payload=payload) 

LAUNCH_DYAS_BY_SATELLITE = "14.卫星别发射日统计"
################################################################################################
def plotPayload(fig, ax, cn_font, title, df, i, upperStages, plotPayload=False, payload=None):
    colorDict = getColorDict(df)
    plotBarGraphByDate(cn_font, ax, df, fontsize=12, upperStages=upperStages, plotPayload=plotPayload, payload=payload, colorDict=colorDict, title=title)
    plotTitleLegendByDate(cn_font, ax, title, df, page=i, plotPayload=plotPayload)
    myPlot.showBackend()
    path = f'./images/{LAUNCH_DYAS_BY_SATELLITE}/{title}.png'
    myPlot.saveFig(fig, path) # Save the plot to a file

################################################################################################
def getColorDict(dfList):
    rocketList = []
    if isinstance(dfList, list):
        for df in dfList:
            rocketList.extend(list(df['火箭']))
    else:
        rocketList.extend(list(dfList['火箭']))

    rocketList = set(rocketList)
    colorDict = SortedDict({rocket: None for rockets in rocketList for rocket in rockets.split('/') })

    count = len(colorDict)
    print(f'火箭数:{count:02}', end=', ')
    if count == 1:
        for rocket in colorDict:
            colorDict[rocket] = 'orange'
    else:
        colorList = myPlot.getUniqueColorList(count)

        for i, rocket in enumerate(colorDict.keys()):
            colorDict[rocket] = colorList[i] if count > 20 else myPlot.getUnique20Colors(i)
    return colorDict

# Plot multiple rockets
################################################################################################
def plotGraphByRocketsDate(cn_font, df, title, rocket, onlyFailed=False, upperStages=None, plotLast=True, seriesDict=None, plotMonth=None):
    dfListAll = myPlot.parseToDataFrame(df, rocket=rocket, onlyFailed=onlyFailed, seriesDict=seriesDict, plotMonth=plotMonth)
    dfList = myPlot.countDataFrameByDate(dfListAll)
    isSeries = rocket.endswith('系列')

    for i, df in enumerate(dfList):
        if not df.iloc[0:, :].empty and (i == len(dfList) - 1 or not plotLast):
            no = '' if len(dfList) == 1 else f'{i + 1}'
            no = f'{i + 1:02}' if rocket in ['', '长征', '其他'] and not plotMonth else no
            newTitle = myPlot.getPlotTitle(f'{title}{no}')
            fig, axLeft =  myShape.getFigure()
            plotBarGraphByDate(cn_font, axLeft, df, fontsize=12, upperStages=upperStages, title=newTitle)
            plotTitleLegendByDate(cn_font, axLeft, newTitle, df, page=i, isSeries=isSeries)
            
            myPlot.showBackend()
            path = f'./images/{LAUNCH_DYAS_BY_SERIES}/失败/{newTitle}.png' if onlyFailed else f'./images/{LAUNCH_DYAS_BY_SERIES}/{newTitle}.png'
            myPlot.saveFig(fig, path) # Save the plot to a file

################################################################################################
def getMonthRockets(dfList):
    dfMonthList = []
    return dfMonthList

LAUNCH_DYAS_BY_SITE = "10.地点别发射日统计"
################################################################################################
def plotGraphByLocationDate(cn_font, df, title, location, upperStages=None, plotLast=True, seriesDict=None):
    dfList = myPlot.parseToDataFrame(df, location=location, seriesDict=seriesDict)
    dfList = myPlot.countDataFrameByDate(dfList)

    for i, df in enumerate(dfList):
        if not df.iloc[0:, :].empty and (i == len(dfList) - 1 or not plotLast):
            nodate = True if i < len(dfList) - 1 else False
            no = '' if len(dfList) == 1 else f'{i + 1:02}'
            newTitle = myPlot.getPlotTitle(f'{title}{no}', retired=True, nodate=nodate)
            # fig, axLeft = plt.subplots(nrows=1, ncols=1, figsize=(20, 10)) 
            fig, axLeft =  myShape.getFigure()
            plotBarGraphByDate(cn_font, axLeft, df, fontsize=12, upperStages=upperStages)
            plotTitleLegendByDate(cn_font, axLeft, newTitle, df, page=i)

            myPlot.showBackend()
            path = f'./images/{LAUNCH_DYAS_BY_SITE}/{newTitle}.png'
            myPlot.saveFig(fig, path) # Save the plot to a file

# Print Rocket List
################################################################################################
def printRocketPayloadList(df, rocketPayload=None, startYear=None, endYear=None, onlyPrintYaoNumber=False, isLunarNewYear=False, 
                           isFirstLast=False, isMaiden=False, plotMonth=None, onlyFailed=None, printYao=False):
    html = ''
    title = ''

    if printYao:
        dfRocketList = myPlot.parseToDataFrame(df, startYear=startYear, endYear=endYear, rocket=rocketPayload, printYao=printYao, splitCount=100)
        dfPayloadList = [[]]
        dfLocationList = [[]]
    elif onlyFailed:
        dfRocketList = myPlot.parseToDataFrame(df, startYear=startYear, endYear=endYear, rocket=rocketPayload, onlyFailed=onlyFailed, splitCount=100)
        dfPayloadList = [[]]
        dfLocationList = [[]]
    elif isLunarNewYear:
        dfRocketList = myPlot.parseToDataFrame(df, startYear=startYear, endYear=endYear, rocket=rocketPayload, isLunarNewYear=isLunarNewYear, splitCount=100)
        dfPayloadList = [[]]
        dfLocationList = [[]]
    elif isFirstLast:
        dfRocketList = myPlot.parseToDataFrame(df, startYear=startYear, endYear=endYear, rocket=rocketPayload, isFirstLast=isFirstLast, splitCount=100)
        dfPayloadList = [[]]
        dfLocationList = [[]]
    elif isMaiden:
        dfRocketList = myPlot.parseToDataFrame(df, startYear=startYear, endYear=endYear, rocket=rocketPayload, isMaiden=isMaiden, splitCount=100)
        dfPayloadList = [[]]
        dfLocationList = [[]]
    elif plotMonth:
        dfRocketList = myPlot.parseToDataFrame(df, startYear=startYear, endYear=endYear, rocket=rocketPayload, plotMonth=plotMonth, splitCount=100)
        dfPayloadList = [[]]
        dfLocationList = [[]]
    elif rocketPayload:
        dfRocketList = myPlot.parseToDataFrame(df, startYear=startYear, endYear=endYear, rocket=rocketPayload, splitCount=100)
        dfPayloadList = myPlot.parseToDataFrame(df, startYear=startYear, endYear=endYear, payload=rocketPayload, splitCount=100)
        dfLocationList = myPlot.parseToDataFrame(df, startYear=startYear, endYear=endYear, location=rocketPayload, splitCount=100)
    else:
        dfRocketList = myPlot.parseToDataFrame(df, startYear=startYear, endYear=endYear, splitCount=100)
        dfPayloadList = [[]]
        dfLocationList = [[]]

    if len(dfRocketList[0]) == 0 and len(dfPayloadList[0]) == 0 and len(dfLocationList[0]) == 0 and not onlyPrintYaoNumber:
        print(f'{rocketPayload} not found!\n')
    else:
        from myModules import myConfig
        retiredRockets = myConfig.readConfigRetiredDict()
        rocketPayload = rocketPayload.split('.')[0] + '系列' if rocketPayload and '.' in rocketPayload else rocketPayload
        rocketPayload = rocketPayload.replace('^', '') if rocketPayload else rocketPayload

        if len(dfRocketList[0]) > 0:
            isSingleRocket = False if rocketPayload is None or '系列' in rocketPayload or '空间站' in rocketPayload or '上面级' in rocketPayload or isLunarNewYear or isFirstLast or isMaiden or plotMonth else True
            myHtml.printList(dfRocketList, rocketPayload, isSingleRocket, onlyPrintYaoNumber)
            if not onlyPrintYaoNumber:
                if rocketPayload:
                    title = f'{startYear}年{rocketPayload}运载火箭发射历史' if startYear else f'{rocketPayload}运载火箭发射历史'
                elif onlyFailed:
                    title = '失败运载火箭发射历史'
                else:
                    years = f'{startYear}~{endYear}年' if startYear != endYear else f'{startYear}年'
                    title = years + '运载火箭发射历史'
                html += myHtml.createHtmlTable(dfRocketList, title, retiredRockets=retiredRockets, isLunarNewYear=isLunarNewYear, isFirstLast=isFirstLast, isMaiden=isMaiden)
        if len(dfPayloadList[0]) > 0:
            myHtml.printList(dfPayloadList, rocketPayload, False, onlyPrintYaoNumber)
            if not onlyPrintYaoNumber:
                title = f'{startYear}年{rocketPayload}载荷发射历史' if startYear else f'{rocketPayload}载荷发射历史'
                html += myHtml.createHtmlTable(dfPayloadList, title, retiredRockets=retiredRockets)
        if len(dfLocationList[0]) > 0:
            myHtml.printList(dfLocationList, rocketPayload, False, onlyPrintYaoNumber)
            if not onlyPrintYaoNumber:
                title = f'{startYear}年{rocketPayload}发射历史' if startYear else f'{rocketPayload}发射历史'
                html += myHtml.createHtmlTable(dfLocationList, title, retiredRockets=retiredRockets)
    return html, title

###############################################################################
def parseYears(rocketPayload):
    years = ''
    if len(rocketPayload) == 4 and rocketPayload.isdigit():
        years = rocketPayload
    elif len(rocketPayload) == 9 and rocketPayload[4:5] == '-':
        yearsList = rocketPayload.split('-')
        if yearsList[0].isdigit() and yearsList[1].isdigit():
            years = rocketPayload
    return years

# Print Rockets List
################################################################################################
def printRocketsPayloadsList(df, years=None, rocketsPayloads=None, onlyPrintYaoNumber=False):
    html = ''
    if years and rocketsPayloads:
        for year in years:
            for rocketPayload in rocketsPayloads:
                if rocketPayload != "遥感" and rocketPayload[0] == '遥':
                    htmlTemp, filename = printRocketPayloadList(df, rocketPayload, startYear=year[:6], endYear=year[:6], onlyPrintYaoNumber=onlyPrintYaoNumber, printYao=True)
                elif rocketPayload == '失败':
                    htmlTemp, filename = printRocketPayloadList(df, None, startYear=year[:6], endYear=year[:6], onlyPrintYaoNumber=onlyPrintYaoNumber, onlyFailed=True)
                elif rocketPayload == '春节':
                    htmlTemp, filename = printRocketPayloadList(df, rocketPayload, startYear=year[:6], endYear=year[:6], onlyPrintYaoNumber=onlyPrintYaoNumber, isLunarNewYear=True)
                elif rocketPayload == '年初年末':
                    htmlTemp, filename = printRocketPayloadList(df, rocketPayload, startYear=year[:6], endYear=year[:6], onlyPrintYaoNumber=onlyPrintYaoNumber, isFirstLast=True)
                elif rocketPayload == '首飞':
                    htmlTemp, filename = printRocketPayloadList(df, rocketPayload, startYear=year[:6], endYear=year[:6], onlyPrintYaoNumber=onlyPrintYaoNumber, isMaiden=True)
                elif rocketPayload in '1月,2月,3月,4月,5月,6月,7月,8月,9月,10月,11月,12月':
                    plotMonth = int(rocketPayload.split('月')[0])
                    htmlTemp, filename = printRocketPayloadList(df, rocketPayload, startYear=year[:6], endYear=year[:6], onlyPrintYaoNumber=onlyPrintYaoNumber, plotMonth=plotMonth)
                else:
                    htmlTemp, filename = printRocketPayloadList(df, rocketPayload, startYear=year[:6], endYear=year[:6], onlyPrintYaoNumber=onlyPrintYaoNumber)
                html += htmlTemp
    elif years:
        for year in years:
            htmlTemp, filename = printRocketPayloadList(df, startYear=year[:4], endYear=year[-4:], onlyPrintYaoNumber=onlyPrintYaoNumber)
            html += htmlTemp
    elif rocketsPayloads:
        for rocketPayload in rocketsPayloads:
            if rocketPayload != "遥感" and rocketPayload[0] == '遥':
                htmlTemp, filename = printRocketPayloadList(df, rocketPayload, onlyPrintYaoNumber=onlyPrintYaoNumber, printYao=True)
            elif rocketPayload == '失败':
                htmlTemp, filename = printRocketPayloadList(df, None, onlyPrintYaoNumber=onlyPrintYaoNumber, onlyFailed=True)
            elif rocketPayload == '春节':
                htmlTemp, filename = printRocketPayloadList(df, rocketPayload, onlyPrintYaoNumber=onlyPrintYaoNumber, isLunarNewYear=True)
            elif rocketPayload == '年初年末':
                htmlTemp, filename = printRocketPayloadList(df, rocketPayload, onlyPrintYaoNumber=onlyPrintYaoNumber, isFirstLast=True)
            elif rocketPayload == '首飞':
                htmlTemp, filename = printRocketPayloadList(df, rocketPayload, onlyPrintYaoNumber=onlyPrintYaoNumber, isMaiden=True)
            elif rocketPayload in '1月,2月,3月,4月,5月,6月,7月,8月,9月,10月,11月,12月':
                plotMonth = int(rocketPayload.split('月')[0])
                htmlTemp, filename = printRocketPayloadList(df, rocketPayload, onlyPrintYaoNumber=onlyPrintYaoNumber, plotMonth=plotMonth)
            else:
                htmlTemp, filename = printRocketPayloadList(df, rocketPayload, onlyPrintYaoNumber=onlyPrintYaoNumber)
            html += htmlTemp
    if html:
        filename = f'{TEMP_FILE_PATH}{filename}.html'
        myFile.saveTextFile(filename, html, noSound=True)

# 年度别发射日统计
################################################################################################
def plot1(cn_font, df, startYear, endYear=None, upperStages=None, SeriesDict=None, printLast=True):
    title = '中国运载火箭发射日统计'
    plotGraphByDate(cn_font, df, title, startYear, endYear, upperStages, SeriesDict, printLast)

# 现役系列别发射日统计
################################################################################################
def plot2(cn_font, df, rockets, upperStages=None, plotLast=True, dfLastLaunch=None):
    for rocket in rockets:
        title = f'中国{rocket}运载火箭发射日统计'
        rocket = '' if rocket == '全部' else rocket
        plotGraphByRocketsDate(cn_font, df, title, rocket, upperStages=upperStages, plotLast=plotLast)

        if rocket == '':
            plotGraphByRocketsMonth(cn_font, df, rocket, upperStages, plotLast, dfLastLaunch)

# 现役系列别月别发射日统计
################################################################################################
def plotGraphByRocketsMonth(cn_font, df, rocket, upperStages=None, plotLast=True, dfLastLaunch=None):
    month = dfLastLaunch[myExcel.EXCEL_COLUMN_DATE].month
    for m in range(1, 13):
        title = f'中国{rocket}运载火箭{m:02}月发射日统计'

        if m == month or not plotLast:
            plotGraphByRocketsDate(cn_font, df, title, rocket, upperStages=upperStages, plotLast=plotLast, plotMonth=m)

# 现役火箭别发射日统计
################################################################################################
def plot3(cn_font, df, rockets, upperStages=None, plotLast=True):
    for rocket in rockets:
        title = f'中国{rocket}运载火箭发射日统计'
        plotGraphByRocketDate(cn_font, df, title, rocket, False, upperStages=upperStages, plotLast=plotLast)

# 地点别发射日统计
################################################################################################
def plot4(cn_font, df, locations, upperStages=None, plotLast=True):
    for location in locations:
        title = f'中国{location}运载火箭发射日统计'
        plotGraphByLocationDate(cn_font, df, title, location, upperStages=upperStages, plotLast=plotLast)

# 卫星别发射日统计
################################################################################################
def plot5(cn_font, df, payloads, upperStages=None, plotLast=True):
    for payload in payloads:
        title = payload[1:] if payload[:1] == '^' else payload
        if payload == '神舟':
            title = f'中国{title}载人飞船发射日统计'
        elif payload == '天舟':
            title = f'中国{title}货运飞船发射日统计'
        elif payload == '嫦娥':
            title = f'中国{title}探月载荷发射日统计'
        elif payload == '天问':
            title = f'中国{title}探火星载荷发射日统计'
        elif payload == '空间站':
            title = f'中国{title}载荷发射日统计'
        else:
            title = f'中国{title.split("~")[0]}载荷发射日统计'
        plotGraphByPayloadDate(cn_font, df, title, payload, upperStages=upperStages, plotLast=plotLast)

# 系列别失败发射日统计
################################################################################################
def plot6(cn_font, df, rockets, upperStages=None, plotLast=True):
    for rocket in rockets:
        title = f'中国{rocket}运载火箭失败发射日统计'
        plotGraphByRocketsDate(cn_font, df, title, rocket, True, upperStages=upperStages, plotLast=plotLast)

# 系列别退役火箭发射日统计
################################################################################################
def plot7(cn_font, df, rocketsCZ, rocketsNCZ, upperStages=None, plotLast=True):
    if rocketsCZ:
        title = f'中国长征退役运载火箭发射日统计'
        plotGraphByRocketDate(cn_font, df, title, rocketsCZ, True, upperStages, plotLast=plotLast)

    if rocketsNCZ:
        title = f'中国其他退役运载火箭发射日统计'
        plotGraphByRocketDate(cn_font, df, title, rocketsNCZ, True, upperStages, plotLast=plotLast)

    if rocketsCZ and rocketsNCZ:
        title = f'中国全部退役运载火箭发射日统计'
        plotGraphByRocketDate(cn_font, df, title, rocketsCZ + rocketsNCZ, True, upperStages, plotLast=plotLast)

# 火箭别退役火箭发射日统计
################################################################################################
def plot8(cn_font, df, rocketsCZ, rocketsNCZ, upperStages=None, plotLast=True):
    if rocketsCZ:
        for rocket in rocketsCZ:
            title = f'中国{rocket}退役运载火箭发射日统计'
            plotGraphByRocketDate(cn_font, df, title, rocket, True, upperStages, plotLast=plotLast)

    if rocketsNCZ:
        for rocket in rocketsNCZ:
            title = f'中国{rocket}退役运载火箭发射日统计'
            plotGraphByRocketDate(cn_font, df, title, rocket, True, upperStages, plotLast=plotLast)

################################################################################################
def main():
    cn_font = myPlotInit.init()
    excelFile = f"{DATA_FILE_PATH}ChinaRocketLaunch.xlsx"
    sheetName = "发射纪录"
    df = myExcel.parseExcelSheetLaunch(excelFile, sheetName)
    dictUpperStages, _ = myPlot.readUpperStageDict(df)

    # 年初年末统计
    # plotGraphForFirstLast(cn_font, df, dictUpperStages)

    # 春节前后统计
    # plotGraphForLunarNewYear(cn_font, df, dictUpperStages)

    # 首飞日统计
    # plotGraphForMaiden(cn_font, df, dictUpperStages)

    # 年度别发射日统计
    startYears = ['1970', '2000', '2010', '2014', '2017', '2019', '2021', '2022', '2023']
    startYears = []
    if startYears:
        for year in startYears:
            plot1(cn_font, df, year, upperStages=dictUpperStages)

    # 现役系列别发射日统计
    rockets = ['', '长征', '上面级', '其他', '民营']
    rockets += ['长征三号甲系列', '长征四号系列', '长征五号系列', '长征六号系列', '长征七号系列', '长征十一号系列']
    rockets += ['快舟系列', '朱雀系列', '捷龙系列', '谷神星系列', '星河系列', '力箭系列', '天龙系列']
    rockets = []
    if rockets:
        plot2(cn_font, df, rockets, dictUpperStages, plotLast=True)

    # 现役火箭别发射日统计
    rockets = ['长征三号乙', '长征二号丁', '长征二号丙', '长征四号丙', '长征四号乙', '长征二号己', '长征十一号']
    rockets += ['长征六号', '长征七号', '长征五号', '长征七号甲', '长征五号乙', '长征十一号海', '长征六号甲', '长征八号']
    rockets += ['快舟一号甲', '快舟十一号', '谷神星一号', '谷神星一号海', '双曲线一号', '力箭一号']
    rockets += ['朱雀二号', '捷龙一号', '捷龙三号', '天龙二号']
    rockets = []
    if rockets:
        plot3(cn_font, df, rockets, dictUpperStages)

    # 地点别发射日统计
    locations = ['酒泉', '太原', '西昌', '文昌', '海上']
    locations = []
    if locations:
        plot4(cn_font, df, locations, dictUpperStages)

    # 卫星别发射日统计
    payloads = ['^吉林一号', '^北斗', '^风云', '^神舟', '^天舟', '^中星','^遥感', '^高分', '^天链', '^天绘', '^海洋']
    payloads += ['天启', '资源', '试验']
    payloads = []
    if payloads:
        plot5(cn_font, df, payloads, dictUpperStages)

    # 系列别失败发射日统计
    rockets = ['长征', '其他']
    rockets = []
    if rockets:
        plot6(cn_font, df, rockets, dictUpperStages)

    # 退役火箭类别发射日统计
    rocketsCZ = ['长征三号甲', '长征三号丙', '长征三号', '长征二号捆', '长征二号', '长征二号甲', '长征四号甲', '长征一号'] 
    rocketsNCZ = ['风暴一号', '开拓者一号', '快舟一号T', '快舟一号', '开拓者二号', '朱雀一号', 'OS-M']
    rocketsCZ, rocketsNCZ = [], []
    if rocketsCZ or rocketsNCZ:
        plot7(cn_font, df, rocketsCZ, rocketsNCZ, dictUpperStages)
        plot8(cn_font, df, rocketsCZ, rocketsNCZ, dictUpperStages)

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')
    
if __name__ == "__main__":
    showRunTime("main()")