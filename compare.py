from os import makedirs, path
from pathlib import Path
from datetime import datetime, time, timedelta

from myModules import myFile
from myModules import myDict
from myModules import myGUI
from myModules import myExcept
from myModules import myKml

TEMP_FILE_PATH = './temp/'
HISTORY_DIR = Path("./histories/")
KMLS_DIR = HISTORY_DIR / "kmls/"
PREDICT_DIR = HISTORY_DIR / "predict/"
TEMP_DIR = Path("./temp/")

################################################################################################
def plotLaunchCenter(axs):
    cities = ('酒泉', '太原', '西昌', '文昌')
    names = ('酒泉卫星发射中心', '太原卫星发射中心', '西昌卫星发射中心', '文昌航天发射场')
    from myModules import myConfig
    for i, lc in enumerate(cities):
        _, lonlat, color = myConfig.readConfig(lc)
        lon, lat = lonlat.split(',')

# def getLayoutTest():
#     import FreeSimpleGUI as sg
#     layout = [
#         [
#             sg.Text("Selected Files:"), 
#             sg.Input(key="-IN-")
#         ],
#         [
#             sg.Radio("Text Files (*.txt)", "DOCS", default=True, key="-TXT-"),
#             sg.Radio("Data Files (*.csv)", "DOCS", key="-DATA-")
#         ],
#         # Use a standard Button instead of FileBrowse/FilesBrowse
#         [
#             sg.Button("Browse Files", key="-MANUAL_BROWSE-"), 
#             sg.Button("Exit")
#         ]
#     ]
#     return layout

# def showWindowTest():
#     import FreeSimpleGUI as sg
#     window = sg.Window("Flicker-Free Dynamic Filter", getLayoutTest())

#     while True:
#         event, values = window.read()
        
#         if event in (sg.WIN_CLOSED, "Exit"):
#             break
            
#         if event == "-MANUAL_BROWSE-":
#             # 1. Determine file types quietly based on user selections
#             if values["-TXT-"]:
#                 current_types = (("Text Files", "*.txt"), ("All Files", "*.*"))
#             else:
#                 current_types = (("Data Files", "*.csv"), ("All Files", "*.*"))
                
#             # 2. Call the native dialog directly to prevent PySimpleGUI button flickering
#             # (Use askopenfilename for a single file, or askopenfilenames for multiple files)
#             from tkinter import filedialog
#             file_paths = filedialog.askopenfilenames(filetypes=current_types)
            
#             # 3. Update the layout input text manually if files were chosen
#             if file_paths:
#                 # Replicates FilesBrowse by joining paths with a semicolon
#                 window["-IN-"].update(";".join(file_paths))

#     window.close()

################################################################################################
# headersRow starts from 0
def readShipMoveData(excelFile, sheetName=None, skipRows=None, headers=None):
    if excelFile[-4:] == '.xls':
        oldExcelFile = excelFile
        excelFile = excelFile.replace('.xls', '.xlsx')
        import pyexcel as xls
        xls.save_book_as(file_name=oldExcelFile, dest_file_name=excelFile)
    import pandas as pd
    import numpy as np
    df = pd.read_excel(excelFile, sheetName, skiprows=skipRows, dtype={'速度': float}) # Convert the worksheet to a DataFrame
    df.replace('-', np.nan, inplace=True) # Replace '-' with NaN
    df.replace([None, np.nan], '', inplace=True) # Replace None with empty string
    df = df[df['速度'] > 1.0]
    return df

################################################################################################
def removeChars(d):
    return d.replace('-', '').replace(' ', '').replace(':', '')

#####################################################################################
def createShipTrackLinesKmlFile(newFile):
    from myModules import myShape
    from simplekml import Kml

    df = readShipMoveData(newFile, '船舶轨迹', skipRows=1)
    mmsiKey = str(df['mmsi'].iloc[0])
    startDate = removeChars(df['时间'].iloc[0])[:12]
    endDate = removeChars(df['时间'].iloc[-1])[:12]
    from myModules import myConfig
    mmsi = myConfig.readConfig(['LaunchShipMMSI'])
    shipName = myConfig.readConfig(['LaunchShipName'])
    shipNameDict = dict(zip(mmsi, shipName))
    shipName = shipNameDict[mmsiKey] if mmsiKey in shipNameDict else f'MMSI{mmsiKey}'
    # title = f'{startDate}-{endDate}-{shipName}-航迹'
    title = f'{endDate[:4]}年{endDate[4:6]}月{endDate[6:8]}日{endDate[8:10]}时{endDate[10:12]}分{shipName}航迹'
    coords = df[['经度', '纬度']].values.tolist()
    kml = Kml()
    myShape.drawLine(kml, coords, shipName)
    myShape.updateKmlFile(kml, title, myShape.KML_PATH)

################################################################################################
def parse_time(s):
    from re import fullmatch
    m = fullmatch(
        r"(\d{1,2})时(\d{1,2})分"
        r"(?:(\d{1,2})"                 # seconds
        r"(?:\.(\d{1,6}))?秒"           # .345秒 (optional)
        r"?)?"
        r"(?:(\d{1,3})毫秒)?",          # 345毫秒 (optional)
        s
    )

    if not m:
        raise ValueError(f"Invalid time: {s}")

    h = int(m.group(1))
    mnt = int(m.group(2))
    sec = int(m.group(3) or 0)

    if m.group(4):
        micro = int(m.group(4).ljust(6, "0"))
    elif m.group(5):
        micro = int(m.group(5)) * 1000
    else:
        micro = 0
    return time(h, mnt)
    # return time(h, mnt, sec, micro)

################################################################################################
def findLaunchTime(iousList, startTimeList, dfLaunchTime, columnList):
    columnFir = columnList[2]
    columnNumber = columnList[3]
    columnLaunchTime = columnList[-1]
    columnStartTime = columnList[-2]
    timeList = []

    for ious, startTimes in zip(iousList, startTimeList):
        startTimes.insert(0, startTimes[0])
        startTimes.insert(0, startTimes[0])
        subTimeList = []
        
        for iou, startTime in zip(ious, startTimes):
            if iou.endswith('IoU') or iou.endswith('Max DZ Count'):
                subTimeList.append('-')
            else:
                if ("MSA" in iou or "NAV" in iou or "PAC" in iou) and "+" not in iou:
                    subTimeList.append('-')
                else:
                    firNews, firOlds = iou.split(' = ')[1].split(' IoU ')
                    firOld, numberOld = firOlds.rsplit('/', 2)[0], '/'.join(firOlds.rsplit('/', 2)[1:])
                    cond = ((dfLaunchTime[columnFir] == firOld) & (dfLaunchTime[columnNumber] == numberOld))

                    import pandas as pd
                    dfLaunchTime[columnLaunchTime] = pd.to_datetime(dfLaunchTime[columnLaunchTime], errors="coerce")
                    dfLaunchTime[columnStartTime] = pd.to_datetime(dfLaunchTime[columnStartTime], errors="coerce")

                    df1 = dfLaunchTime.loc[cond, columnLaunchTime]
                    df2 = dfLaunchTime.loc[cond, columnStartTime]

                    if df1.notna().any() and df2.notna().any():
                        try:
                            newStartTime = datetime.strptime(startTime, '%Y年%m月%d日%H时%M分')
                            result = (df1 - df2).iloc[0]
                            newLuanchTime = datetime.strftime(newStartTime + result, '%Y年%m月%d日%H时%M分')
                            subTimeList.append(newLuanchTime)
                        except ValueError:
                            subTimeList.append('-')
                    else:
                        subTimeList.append('-')
        timeList.append(subTimeList)
    return timeList

################################################################################################
def compareKmls(newFile=None, newKml=None, isPool=True):
    from myModules import myShape
    from myModules import myConfig
    from glob import glob
    from myModules import myPlotInit

    print('The filename you chose was: ', newFile)
    print('Comapre to history KML files...')

    if newKml:
        newGdf = myShape.convertKmlToGdf(newKml)
    else:
        sites, sitesSea = myConfig.readConfigSitesSea(newFile)
        if sites is None:
            print(f'{newFile} not included {sitesSea}')
            raise ValueError(f"Invalid locations: {sites}")
    
    cn_font = myPlotInit.init()
    newGdf = myShape.mergeDzs(myKml.readKmlFileToGdf(newFile))

    if newGdf.empty:
        print(f"No Data in {newFile}!")
        return 

    matchDicts = {}
    unMatchDicts = {}
    siteFolders = myConfig.readConfigSitesFolders()
    filename = path.basename(newFile)
    newTitle = filename #myFile.getTitle(newFile)
    newTitle = newTitle if '时' in newTitle else newTitle.replace('日', '日??时??分', 1)
    matchedPath = f'{TEMP_FILE_PATH}match/{filename.split("+")[0]}'
    unMatchedPath = f'{TEMP_FILE_PATH}unmatch/{filename.split("+")[0]}'
    myFile.removeFile(f'{TEMP_FILE_PATH}match/*.*')
    myFile.removeFile(f'{TEMP_FILE_PATH}unmatch/*.*')
    tasks = []

    if isPool:
        for site in sites:
            oldFiles = myConfig.parseFilesFromSite(siteFolders, site)
            
            for oldFile in oldFiles:
                tasks.append((cn_font, newGdf, oldFile, matchedPath, unMatchedPath, newTitle))

        from multiprocessing import Pool, cpu_count
        with Pool(processes=cpu_count()) as pool:
            for matchDict, unMatchDict in pool.imap_unordered(compareTwoKmls, tasks, chunksize=4):
                matchDicts.update(matchDict)
                unMatchDicts.update(unMatchDict)

    else:
        for site in sites:
            oldFiles = myConfig.parseFilesFromSite(siteFolders, site)
            
            for oldFile in oldFiles:
                task = (cn_font, newGdf, oldFile, matchedPath, unMatchedPath, newTitle)
                matchDict, unMatchDict = compareTwoKmls(task)
                matchDicts.update(matchDict)
                unMatchDicts.update(unMatchDict)

    return matchDicts, unMatchDicts, matchedPath, unMatchedPath

################################################################################################
def compareTwoKmls(args):
    from myModules import myShape
    cn_font, newGdf, oldFile, matchedPath, unMatchedPath, newTitle = args
    try:
        try:
            oldGdf = myShape.mergeDzs(myKml.readKmlFileToGdf(oldFile))

            if not oldGdf.empty:
                fig, ax = myShape.getFigure(setAspectEqual=True, plotGrid=True)
                oldTitle = path.basename(oldFile).split("+")[0] #myFile.getTitle(oldFile)
                myShape.plotTwoNoatms(ax, newGdf, oldGdf)
                iouList, startTimeList, _ = myShape.plotPolygonsIntersection(fig, ax, cn_font, newGdf, newTitle, oldGdf, oldTitle)
                matchDict, unMatchDict = saveToPngFile(fig, oldFile, iouList, startTimeList, matchedPath, unMatchedPath, newTitle, oldTitle)

        except Exception as e:
            print(f"No Data in {oldFile}!")
            myExcept.printExceptionTrace()

    except Exception as e:
        myExcept.printExceptionTrace()

    return matchDict, unMatchDict

#####################################################################################
def saveToPngFile(fig, oldFile, iouList, startTimeList, savePath1, savePath2, newTitle, oldTitle):
    matchDict = {}
    unMatchDict = {}
    filename = oldFile.name.replace(".kml", ".png")
    oldFilename = oldFile.name
    launchDatetime = oldFilename[:17]
    launchDatetime = datetime.strptime(launchDatetime, "%Y年%m月%d日%H时%M分")

    from myModules import myPlot
    myPlot.saveFig(fig, f'{savePath1 if iouList else savePath2}/{filename}', False, False)

    if iouList:
        matchDict[(launchDatetime.date(), launchDatetime.time())] = [iouList, startTimeList, oldFilename.replace('.kml', '.png')]
        print(f'{newTitle.split("+")[0]+".kml"} IoU {oldTitle}')
        for iou in iouList:
            print(f'    {iou}') 
        print('')
    else:
        unMatchDict[(launchDatetime.date(), launchDatetime.time())] = [None, None, oldFilename.replace('.kml', '.png')]

    return matchDict, unMatchDict

################################################################################################
def createCompareResult(newFile, matchDict, unMatchDict, matchedPath, unMatchedPath):
    from myModules import myConfig
    retiredRockets = myConfig.readConfigRetiredDict()
    excelFile, sheetLaunch, SheetLaunchTime = myConfig.readConfig(['ExcelFile', 'SheetLaunch', 'SheetLaunchTime'])

    from myModules import myExcel
    dfLaunch = myExcel.parseExcelSheetLaunch(excelFile, sheetLaunch, withCancel=True)
    newFilename = newFile.split('/')[-1].split("\\")[-1].replace('.kml', '')
    try:
        arr = newFilename.split("+")
        newFilename = arr[0]
        orbit = arr[1] if len(arr) == 2 else "近地轨道"
    except Exception:
        myExcept.printExceptionTrace()

    # for without overlap drop zone
    unMatchDict = myDict.sortDictByKey(unMatchDict)
    keyList = list(unMatchDict.keys())
    valuesList = list(unMatchDict.values())

    if keyList and valuesList:
        from myModules import myHtml

        _, _, imageList = zip(*valuesList)
        dfMatchList = [dfLaunch[
            dfLaunch.assign(
                日期=dfLaunch['日期'].dt.date, Time=dfLaunch['时间\n（UTC+8）'].map(parse_time))[['日期', 'Time']]
            .apply(tuple, axis=1).isin(keyList)
        ]]

        title1 = f'{newFilename}同发射地不同轨道落区发射历史'
        title2 = f'{newFilename}同发射地相同轨道落区发射历史'
        title = [title1, title2]
        html1, html2 = myHtml.createHtmlTable(dfMatchList, title, None, imageList, retiredRockets, None, orbit=orbit)

        if html1:
            fullFilename = f'{unMatchedPath}/{title1}.html'
            myFile.saveTextFile(fullFilename, html1)

        if html2:
            fullFilename = f'{unMatchedPath}/{title2}.html'
            myFile.saveTextFile(fullFilename, html2)

    # for with overlap drop zone
    matchDict = myDict.sortDictByKey(matchDict)
    keyList = list(matchDict.keys())
    valuesList = list(matchDict.values())

    if keyList and valuesList:
        iousList, startTimeList, imageList = zip(*valuesList)
        columnList = myConfig.readConfig(['ColumnLaunchTime'])
        
        dfMatchList = [dfLaunch[
            dfLaunch.assign(
                日期=dfLaunch['日期'].dt.date, Time=dfLaunch['时间\n（UTC+8）'].map(parse_time))[['日期', 'Time']]
                # 日期=dfLaunch['日期'].dt.date, Time=dfLaunch['时间\n（UTC+8）'].map(parse_time))[['日期', 'Time', '地点']]
            .apply(tuple, axis=1).isin(keyList)
        ]]

        dfLaunchTime = myExcel.parseExcelSheetLaunchTime(excelFile, SheetLaunchTime, columnList)
        dfMatchTime = findLaunchTime(iousList, startTimeList, dfLaunchTime, columnList)
        
        myHtml.printList(dfMatchList, newFile)
        title = f'{newFilename}重叠轨道落区发射历史'
        html = myHtml.createHtmlTable(dfMatchList, title, iousList, imageList, retiredRockets, dfMatchTime)

        if html:
            fullFilename = f'{matchedPath}/{title}.html'
            myFile.saveTextFile(fullFilename, html, noSound=True)
    # return matchDict, unMatchDict, savePath1, savePath2

################################################################################################
def parseFile(files: list, values={}):
    from myModules import myFile

    start = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    notamDict = {}

    for newFile in files:
        if not newFile:
            raise ValueError("No filename supplied")

        if newFile.endswith('.txt'):
            from myModules import myNotam

            if values[KEY_HISTORY_NOTICE]:
                notamDict.update(myNotam.parseHistoricalNotice(newFile))
            elif values["-CUURENT_NOTICE-"]:
                print('Parsing file: ', newFile)
                if 'msa' in newFile:
                    notamDict.update(myNotam.parseMsaFromTextFile(newFile))
                elif 'notam' in newFile:
                    notamDict.update(myNotam.parseNotamFromTextFile(newFile))

            if notamDict:
                notamDict = myDict.sortDictByValue(notamDict)

                if  values[KEY_CURRENT_NOTICE]:
                    notamDict = myNotam.parseLaunch(notamDict)

                isNew, dataString = myFile.updateTempFile(notamDict)
                filenames = []

                if isNew:
                    from myModules import myShape
                    filenames = myShape.createKmlFile(notamDict)
                myDict.printNotam(dataString, filenames, start)

        elif values[KEY_COMPARE_KMLS] and newFile.endswith('.kml'):
            matchDict, unMatchDict, matchedPath, unMatchedPath = compareKmls(newFile)
            createCompareResult(newFile, matchDict, unMatchDict, matchedPath, unMatchedPath)

        elif values[KEY_SHIP_ROUTE] and (newFile.endswith('.xls') or newFile.endswith('.xlsx')):
            print('Filename: ', newFile)
            createShipTrackLinesKmlFile(newFile)
            myFile.playSound()
            print('\nFinished comparing!')

        else:
            print("Unsupported file: ", newFile)

################################################################################################
def parseSameOrbit(dfList, imageList):
    dfSameOrbitList = []
    dfOthersList = []
    sameOrbitImageList = []
    otherImageList = []

    for df in dfList:
        condition = df['轨道'] == '近地轨道'
        dfSameOrbitList.append(df[condition].copy())
        dfOthersList.append(df[~condition].copy())

    from myModules import myDataFrame
    dfSameOrbitList = myDataFrame.splitToPages(dfSameOrbitList, 100)
    dfOthersList = myDataFrame.splitToPages(dfOthersList, 100)
    return dfSameOrbitList, sameOrbitImageList, dfOthersList, otherImageList

################################################################################################
KML_FILE = ("KML Files", "*.kml")
TEXT_FILE = ("TEXT Files", "*.txt")
EXCEL_FILE = ("EXCEL Files", "*.xls,*xlsx")

KEY_COMPARE_KMLS = "-COMPARE_KMLS-"
KEY_HISTORY_NOTICE = "-HISTORY_NOTICE-"
KEY_CURRENT_NOTICE = "-CURRENT_NOTICE-"
KEY_SHIP_ROUTE = "-SHIP_ROUTE-"

BROWSE_FILE_TYPES = {
    KEY_COMPARE_KMLS: (KML_FILE[0], KML_FILE[1], "Compare With Historical Launches"),
    KEY_HISTORY_NOTICE: (TEXT_FILE[0], TEXT_FILE[1], "Create KML File for  Historical Launch"),
    KEY_CURRENT_NOTICE: (TEXT_FILE[0], TEXT_FILE[1], "Create KML File"),
    KEY_SHIP_ROUTE: (EXCEL_FILE[0], EXCEL_FILE[1], "Create KML File For Ship Move route")
}

################################################################################################
def getLayout():
    import FreeSimpleGUI as sg
    layout = [
        [
            sg.Column([
                [sg.Radio(f"{", ".join(BROWSE_FILE_TYPES[KEY_COMPARE_KMLS])}", "DOCS", key="-COMPARE_KMLS-", enable_events=True, default=True)], 
                [sg.Radio(f"{", ".join(BROWSE_FILE_TYPES[KEY_HISTORY_NOTICE])}", "DOCS", key="-HISTORY_NOTICE-", enable_events=True)],
                [sg.Radio(f"{", ".join(BROWSE_FILE_TYPES[KEY_CURRENT_NOTICE])}", "DOCS", key="-CURRENT_NOTICE-", enable_events=True)],
                [sg.Radio(f"{", ".join(BROWSE_FILE_TYPES[KEY_SHIP_ROUTE])}", "DOCS", key="-SHIP_ROUTE-", enable_events=True)],
                [sg.Text('Select File:')]
            ])
        ],
        [
            sg.In(key='-FILES-'), 
            sg.FilesBrowse(key="-BROWSE-", file_types=((BROWSE_FILE_TYPES[KEY_COMPARE_KMLS][0], BROWSE_FILE_TYPES[KEY_COMPARE_KMLS][1]),)),
        ],
        [
            sg.Open(), 
            sg.Push(), 
            sg.Exit()
        ],
    ]
    return layout

################################################################################################
def showWindow():
    import FreeSimpleGUI as sg
    window = sg.Window('Select file to parse...', getLayout())

    while True:
        event, values = window.read()
        # print(f"{event = }")
        # for k, v in values.items():
        #     print(f"{k = }. {v = }")

        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        else:
            if event in [KEY_COMPARE_KMLS, KEY_HISTORY_NOTICE, KEY_CURRENT_NOTICE, KEY_SHIP_ROUTE]:
                window["-BROWSE-"].FileTypes = ((BROWSE_FILE_TYPES[event][0], BROWSE_FILE_TYPES[event][1]),)

        if values["-FILES-"]:
            window.minimize()
            files = values['-FILES-'].split(';')
            # print(f"{files}")
            parseFile(files, values)
            window.Normal()
    window.close()

################################################################################################
HISTORY_DIR = Path("./histories/kmls/")

def main(debug=False):
    import locale
    import sys
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    sys.stdout.reconfigure(encoding='UTF-8')

    if len(sys.argv) > 1 and sys.argv[1].endswith(".kml"):
        newKmlPath = list(PREDICT_DIR.rglob(sys.argv[1]))

        if not newKmlPath or not newKmlPath[0].is_file():
            newKmlPath = list(TEMP_DIR.rglob(sys.argv[1]))

        if not newKmlPath or not newKmlPath[0].is_file():
            raise ValueError(f"Not found file: '{sys.argv[1]}'")

        newFile = str(newKmlPath[0].resolve())
        matchDict, unMatchDict, matchedPath, unMatchedPath = compareKmls(newFile)
        createCompareResult(newFile, matchDict, unMatchDict, matchedPath, unMatchedPath)
    else:
        myGUI.setScreenDpiAware()
        showWindow()

################################################################################################
def showRunTime(func):
    from timeit import timeit
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}\n')

################################################################################################
if __name__ == "__main__":
    showRunTime("main()")