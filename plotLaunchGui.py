from sys import path
from timeit import timeit
from datetime import timedelta
from openpyxl import load_workbook as loadXLSX
import PySimpleGUI as sg

path.append('./')

import constants
import myUtils
import myPlot
import plotLaunchByDate
import plotLaunchByLocation
import plotLaunchByRocket
import plotLaunchByYearMonth
import plotLaunchBarChartRace

CHROME = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

################################################################################################
def splitStringToList(text, n=10):
    oldList = text.split(',') if isinstance(text, str) else text
    subLists = [oldList[i:i+n] for i in range(0, len(oldList), n)]
    return subLists

################################################################################################
def splitStringToListByText(text: str):
    oldList = text.split(',')
    subLists = []
    sub = []
    isFirst = True
    for item in oldList:
        if not item.startswith('长征') and isFirst:
            isFirst = False
            subLists.append(sub)
            sub = []
            sub.append(item)
        else:
            sub.append(item)
    subLists.append(sub)
    return subLists

################################################################################################
def getYearsFrame(years:str, lastYear):
    subYears = splitStringToList(years)
    yearsTitle = [sg.Checkbox('选择全发射期间', key='year01', enable_events=True)]
    layout1 = [yearsTitle]
    for i, subYear in enumerate(subYears):
        checkbox = [sg.Checkbox(item, key=f'year-{i * 10 + j + 1}', default=True if item == lastYear else False) for j, item in enumerate(subYear)]
        layout1.append(checkbox)
    return [sg.Frame('发射期间（统计条形图/动态条形图）', layout1)]

def getRocketsFrame(rockets, retired, lastRocket):
    rocketsCZ = splitStringToList(rockets[0])
    rocketsNCZ = splitStringToList(rockets[1])
    retiredCZ = splitStringToList(retired[0])
    retiredNCZ = splitStringToList(retired[1])
    rocketsTitle = [
        sg.Checkbox('选择全运载火箭', key='rocket01', enable_events=True),
        sg.Checkbox('仅生成最后图表', key='rocket02', default=True),
        sg.Checkbox('退役火箭', key='rocket03', enable_events=True),
        # sg.Checkbox('发射失败', key='rocket03'),
    ]
    rockets = [rocketsTitle]
    row1, row2 = [], []
    for i, subRocket in enumerate(rocketsCZ):
        checkbox = [sg.Checkbox(item, key=f'rocket-CZ{i * 10 + j + 1}', size=(12, 1), default=True if item == lastRocket else False) for j, item in enumerate(subRocket)]
        row1.append(checkbox)
    for i, subRocket in enumerate(rocketsNCZ):
        checkbox = [sg.Checkbox(item, key=f'rocket-NCZ{i * 10 + j + 1}', size=(12, 1), default=True if item == lastRocket else False) for j, item in enumerate(subRocket)]
        row1.append(checkbox)
    for i, subRetired in enumerate(retiredCZ):
        checkbox = [sg.Checkbox(item, key=f'retired-CZ{i * 10 + j + 1}', size=(12, 1)) for j, item in enumerate(subRetired)]
        row2.append(checkbox)
    for i, subRetired in enumerate(retiredNCZ):
        checkbox = [sg.Checkbox(item, key=f'retired-NCZ{i * 10 + j + 1}', size=(12, 1)) for j, item in enumerate(subRetired)]
        row2.append(checkbox)
    rockets.append([sg.Column(row1, key='rockets'), sg.Column(row2, key='retired', visible=False)])
    return [sg.Frame('运载火箭（统计条形图）', rockets)]  

def getSeriesFrame(series, lastSeries, lastResult):
    seriesCZ = splitStringToList(series[0])
    seriesNCZ = splitStringToList(series[1])
    seriesAll = splitStringToList(series[4])
    seriesTitle = [
        sg.Checkbox('选择全运载火箭系列', key='series01', enable_events=True),
        sg.Checkbox('仅生成最后图表', key='series02', default=True),
        sg.Checkbox('退役火箭系列', key='series03', enable_events=True),
        sg.Checkbox('发射失败系列', key='series04', default=not lastResult, enable_events=True),
        sg.Checkbox('首飞发射', key='series05', enable_events=False),
        sg.Checkbox('春节前后发射', key='series06', enable_events=False),
        sg.Checkbox('年初年末发射', key='series07', enable_events=False),
    ]
    row = [seriesTitle]
    for i, subSeries in enumerate(seriesAll):
        checkbox = [sg.Checkbox(item, key=f'series-{i * 10 + j + 1}', size=(12, 1), default=True if item in lastSeries else False) for j, item in enumerate(subSeries)]
        row.append(checkbox)      
    for i, subSeries in enumerate(seriesCZ):
        checkbox = [sg.Checkbox(item, key=f'series-CZ{i * 10 + j + 1}', size=(12, 1), default=True if item in lastSeries else False) for j, item in enumerate(subSeries)]
        row.append(checkbox)      
    for i, subSeries in enumerate(seriesNCZ):
        checkbox = [sg.Checkbox(item, key=f'series-NCZ{i * 10 + j + 1}', size=(12, 1), default=True if item in lastSeries else False) for j, item in enumerate(subSeries)]
        row.append(checkbox)      
    return [sg.Frame('运载火箭系列（统计条形图）', row)]

def getLocationsFrame(locations, lastLocation):
    subLocations = splitStringToList(locations)
    locationTitle = [
        sg.Checkbox('选择全发射位置', key='location01', enable_events=True),
        sg.Checkbox('仅生成最后图表', key='location02', default=True),
    ]
    layout5 = [locationTitle]
    for i, subLocation in enumerate(subLocations):
        checkbox = []
        for j, item in enumerate(subLocation[:6]):
            if j < len(subLocation) - 1:
                checkbox.append(sg.Checkbox(item, key=f'location-{i * 10 + j + 1}', 
                        size=(10, 1), default=True if item == lastLocation else False))
            else:
                checkbox.append(sg.Checkbox(item, key=f'location-{i * 10 + j + 1}', 
                        default=True if item == lastLocation else False))
        layout5.append(checkbox)      
    return sg.Frame('发射位置（统计条形图）', layout5)

def getCategoriesFrame(categories, lastCategory):
    subCategories = splitStringToList(categories)
    categoriesTitle = [sg.Checkbox('选择全运载火箭分类', key='category01', enable_events=True)]
    layout2 = [categoriesTitle]
    for i, subCategory in enumerate(subCategories):
        checkbox = [sg.Checkbox(item, key=f'category-{i * 10 + j + 1}', size=(10, 1), 
                    default=True if item in lastCategory else False) for j, item in enumerate(subCategory)]
        layout2.append(checkbox)      
    return sg.Frame('运载火箭分类（动态条形图）', layout2)

def getPayloadsFrame(payloads):
    subPayloads = splitStringToList(payloads, 11)
    payloadsTitle = [sg.Checkbox('选择全卫星系列', key='payload01', enable_events=True),
                     sg.Checkbox('仅生成最后图表', key='payload02', default=True)]
    layout = [payloadsTitle]
    for i, subPayload in enumerate(subPayloads):
        checkbox = [sg.Checkbox(item if item[0] != '^' else item[1:], 
                    text_color=sg.theme_element_text_color() if item[0] != '^' else 'orange', 
                    key=f'payload-{i * 11 + j + 1}', size=(10, 1)) for j, item in enumerate(subPayload)]
        layout.append(checkbox)
    return [sg.Frame('卫星系列（统计条形图，无色=卫星名含有文字，桔色=卫星名开头文字）', layout)]

def getButton():
    button = [
        sg.Button(constants.BUTTON1_LABEL, font=("Helvetica", 14)), 
        sg.Button(constants.BUTTON2_LABEL, font=("Helvetica", 14)), 
        # sg.Push(), 
        # sg.Button('Show Chart Pictures', font=("Helvetica", 14)), 
        # sg.Button('Play Bar Chart Race Videos', font=("Helvetica", 14)), 
        sg.Push(), 
        sg.Button('Exit', font=("Helvetica", 14))
    ]
    return button

################################################################################################
def getWindow(years, rockets, series, retired, privates, locations, categories, payloads, lastLaunch):
    lastYear = lastLaunch[0]
    lastRocket = lastLaunch[1]
    lastNumber = lastLaunch[2]
    lastUpperStage = lastLaunch[3]
    lastSeries = lastLaunch[4]
    lastCategory = lastSeries
    lastCategory.append('系列')
    lastLocation = lastLaunch[5]
    lastResult = lastLaunch[6]

    # Green & tan color scheme      
    make_dpi_aware()
    sg.theme('Python')
    sg.set_options(text_justification='right')      

    layout = []
    layout.append(getYearsFrame(years, lastYear))  
    layout.append(getRocketsFrame(rockets, retired, lastRocket))  
    layout.append(getSeriesFrame(series, lastSeries, lastResult))  
    layout.append([getLocationsFrame(locations, lastLocation), getCategoriesFrame(categories, lastCategory)])  
    # console_layout = [sg.Output(size=(120, 10), font='Courier 10')]
    # frame_layout.append(button)
    # layout.append([sg.Frame("Output console", frame_layout)])  
    layout.append(getPayloadsFrame(payloads))
    # layout.append(console_layout)
    layout.append(getButton())  

    window = sg.Window('中国运载火箭发射统计图表作成', layout, finalize=True, font=("Helvetica", 12))      
    return window

def getResolution():
    import tkinter
    root = tkinter.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    return width, height

################################################################################################
def make_dpi_aware():
    import ctypes
    import platform
    if myUtils.isWindows() and int(platform.release()) >= 8:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)

################################################################################################
def getLastSeries(lastRocket, series, privates, lastUpperStage):
    lastSeries = ['全部']
    if lastRocket.startswith('长征'):
        lastSeries.append('长征')
    if lastUpperStage:
        lastSeries.append('上面级')
    if not lastRocket.startswith('长征'):
        lastSeries.append('其他')
    if lastRocket in privates:
        lastSeries.append('民营')
    listSeries = series[0].split(',')
    listSeries.extend(series[1].split(','))
    rocketProfix = lastRocket[:4] if lastRocket.startswith('长征') else lastRocket[:2]
    for series in listSeries:
        if series.startswith(rocketProfix):
            lastSeries.append(series)
            break
    return lastSeries

################################################################################################
def toogleAllCheckbox(window, values, prefix):
    prefix1 = 'rocket-' if prefix == 'retired-' else prefix
    isCheckAll = values[prefix1[:-1] + '01']
    for key, value in values.items():
        if prefix in key:
            window[key].update(isCheckAll)

################################################################################################
def getSelectedItems(values, items, prefix):
    itemsSelect = []
    itemsChecked = [element for element in values if values[element]==True and prefix in element]
    for itemChecked in itemsChecked:
        if '-' in itemChecked:
            if '-NCZ' in itemChecked:
                index = int(itemChecked.split('-NCZ')[1]) - 1
                itemsSelect.append(items[1].split(',')[index])
            elif '-CZ' in itemChecked:
                index = int(itemChecked.split('-CZ')[1]) - 1
                itemsSelect.append(items[0].split(',')[index])
            else:
                index = int(itemChecked.split('-')[1]) - 1
                if isinstance(items, str):
                    itemsSelect.append(items.split(',')[index])
                else:
                    itemsSelect.append(items[4].split(',')[index])
    return itemsSelect

################################################################################################
def getLastLaunch(dfLastLaunch, series, privates, dictUpperStage):
    lastYear = myUtils.getJapanDate()[:4]
    lastRocket = dfLastLaunch[constants.EXCEL_COLUMN_ROCKET]
    lastNumber = dfLastLaunch[constants.EXCEL_COLUMN_NUMBER]
    lastResult = True if dfLastLaunch[constants.EXCEL_COLUMN_RESULT] == '成功' else False
    lastUpperStage = (lastRocket+lastNumber) in dictUpperStage
    lastSeries = getLastSeries(lastRocket, series, privates, lastUpperStage)
    lastLocation = dfLastLaunch[constants.EXCEL_COLUMN_LOCATION]
    lastLaunch = [lastYear, lastRocket, lastNumber, lastUpperStage, lastSeries, lastLocation, lastResult]
    return lastLaunch

################################################################################################
def removeSeriesText(rocketsChecked):
    rockets = []
    for rocket in rocketsChecked:
        if '全部' ==  rocket:
            rockets.append('')
        elif rocket in '长征,上面级,其他,民营':
            rockets.append(rocket)
        else:
            rockets.append(rocket+'系列')
    return rockets

################################################################################################
def splitYearsChecked(yearsChecked):
    years = []
    for year in yearsChecked:
        if '～' in year:
            arr = year.split('～')
            years.append([arr[0], arr[1]])
        else:
            years.append([year])
    return years

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
def showRetiredRockets(window, values, rocket):
    isChecked = values['rocket03']
    window['rockets'].update(visible=not isChecked)
    window['retired'].update(visible=isChecked)
    if isChecked:
        for key, value in values.items():
            if 'retired-' in key:
                window[key].update(True)    

################################################################################################
def showFirstLastLunarNewYearSeries(window, values):
    isChecked = values['series06'] | values['series07']
    for key, value in values.items():
        if 'series-' in key:
            if isChecked:
                if key in 'series-1':
                    window[key].update(True)    
                else:
                    window[key].update(disabled=True)
                    window[key].update(text_color='gray')
                    window[key].update(False)
            else:
                window[key].update(disabled=False)
                window[key].update(text_color=sg.theme_element_text_color())
                window[key].update(False)

################################################################################################
def showRetiredMaidenSeries(window, values):
    isChecked = values['series03'] | values['series04'] | values['series05']
    for key, value in values.items():
        if 'series-' in key:
            if isChecked:
                if key in 'series-1,series-2,series-4':
                    window[key].update(True)    
                else:
                    window[key].update(disabled=True)
                    window[key].update(text_color='gray')
                    window[key].update(False)
            else:
                window[key].update(disabled=False)
                window[key].update(text_color=sg.theme_element_text_color())
                window[key].update(False)

################################################################################################
def splitRetiredRockets(retiredChecked):
    cz, ncz = [], []
    for item in retiredChecked:
        if item.startswith('长征'):
            cz.append(item)
        else:
            ncz.append(item)
    return cz, ncz
    
################################################################################################
def handleEvents(excelSheet1, event, window, values, years, rockets, retired, series, locations, categories, payloads, dictUpperStage, dfLastLaunch):
    if event == 'year01':
        toogleAllCheckbox(window, values, 'year-')
    elif event == 'rocket01':
        toogleAllCheckbox(window, values, 'rocket-')
        toogleAllCheckbox(window, values, 'retired-')
    elif event == 'rocket03':
        showRetiredRockets(window, values, 'rocket-')
    elif event == 'series01':
        toogleAllCheckbox(window, values, 'series-')
    elif event in 'series03,series04,series05':
        showRetiredMaidenSeries(window, values)
    elif event in 'series06,series07':
        showFirstLastLunarNewYearSeries(window, values)
    elif event == 'location01':
        toogleAllCheckbox(window, values, 'location-')
    elif event == 'category01':
        toogleAllCheckbox(window, values, 'category-')
    elif event == 'payload01':
        toogleAllCheckbox(window, values, 'payload-')
    elif event == constants.BUTTON1_LABEL:
        window.minimize()
        cn_font = myPlot.init()
        yearsChecked = getSelectedItems(values, years, 'year')
        rocketsChecked = getSelectedItems(values, rockets, 'rocket')
        retiredChecked = getSelectedItems(values, retired, 'retired')
        seriesChecked = getSelectedItems(values, series, 'series')
        locationsChecked = getSelectedItems(values, locations, 'location')
        payloadsChecked = getSelectedItems(values, payloads, 'payload')
        rocketPrintLast = values['rocket02']
        rocketRetired = values['rocket03']
        seriesPrintLast = values['series02']
        seriesRetired = values['series03']
        seriesFailed = values['series04']
        seriesMaiden = values['series05']
        seriesLunarNewYear = values['series06']
        seriesFirstLast = values['series07']
        locationPrintLast = values['location02']
        payloadPrintLast = values['payload02']

        if yearsChecked:
            print(f'\nYear Checked: {yearsChecked}')
            yearsChecked = splitYearsChecked(yearsChecked)
            plotLaunchByLocation.plot2(cn_font, excelSheet1)
            for years in yearsChecked:
                if len(years) == 2:
                    plotLaunchByDate.plot1(cn_font, excelSheet1, years[0], years[1], dictUpperStage)
                else:
                    plotLaunchByDate.plot1(cn_font, excelSheet1, years[0], upperStage=dictUpperStage)

                plotLaunchByYearMonth.plot1(cn_font, excelSheet1, years)
                for year in years:
                    plotLaunchByRocket.plot1(cn_font, excelSheet1, year)
                    plotLaunchByLocation.plot2(cn_font, excelSheet1, year)

        if rocketsChecked or retiredChecked:
            if rocketsChecked:
                print(f'\nRocket Checked: {rocketsChecked}')
                plotLaunchByDate.plot3(cn_font, excelSheet1, rocketsChecked, dictUpperStage, rocketPrintLast)
            if rocketRetired:
                print(f'\nRetired Checked: {retiredChecked}')
                retiredCZ, retiredNCZ = splitRetiredRockets(retiredChecked)
                plotLaunchByDate.plot8(cn_font, excelSheet1, retiredCZ, retiredNCZ, dictUpperStage, seriesPrintLast)

        if seriesChecked:
            print(f'\nSeries Checked: {seriesChecked}')
            if seriesFailed or seriesRetired:
                if seriesFailed:
                    plotLaunchByDate.plot6(cn_font, excelSheet1, seriesChecked, dictUpperStage, seriesPrintLast)
                if seriesRetired:
                    plotLaunchByDate.plot7(cn_font, excelSheet1, retired[0].split(','), retired[1].split(','), dictUpperStage, seriesPrintLast)
            else:
                seriesChecked = removeSeriesText(seriesChecked)
                plotLaunchByDate.plot2(cn_font, excelSheet1, seriesChecked, dictUpperStage, seriesPrintLast, dfLastLaunch)

            if seriesMaiden:
                plotLaunchByDate.plotGraphForMaiden(cn_font, excelSheet1, dictUpperStage)
            if seriesLunarNewYear:
                plotLaunchByDate.plotGraphForLunarNewYear(cn_font, excelSheet1, dictUpperStage)
            if seriesFirstLast:
                plotLaunchByDate.plotGraphForFirstLast(cn_font, excelSheet1, dictUpperStage)

        if locationsChecked:
            print(f'\nLocation Checked: {locationsChecked}')
            plotLaunchByDate.plot4(cn_font, excelSheet1, locationsChecked, dictUpperStage, locationPrintLast)
            plotLaunchByLocation.plot2(cn_font, excelSheet1)

        if payloadsChecked:
            print(f'\nPayload Checked: {payloadsChecked}')
            plotLaunchByDate.plot5(cn_font, excelSheet1, payloadsChecked, dictUpperStage, payloadPrintLast)
        myUtils.playSound()

    elif event == constants.BUTTON2_LABEL:
        window.minimize()
        cn_font = myPlot.init(True)
        yearsChecked = getSelectedItems(values, years, 'year')
        if yearsChecked:
            print(f'\nYear Checked: {yearsChecked}')
            plotLaunchBarChartRace.plot1(excelSheet1, yearsChecked)

        categoriesChecked = getSelectedItems(values, categories, 'category')
        if categoriesChecked:
            print(f'\nCategory Checked: {categoriesChecked}')
            plotLaunchBarChartRace.plot2(excelSheet1, categoriesChecked)

################################################################################################
def main():
    excelFile, sheetNames, years, rockets, retired, series, privates, locations, categories, payloads = myUtils.readConfig()
    excelBook = loadXLSX(excelFile, data_only=True, read_only=True)
    excelSheet1 = excelBook[sheetNames[0]]
    # excelSheet2 = excelBook[sheetNames[1]]
    # excelBook.close()

    # TODO read 退役，民营数据 from excel file not from config.ini
    # dfList = myPlot.parseExcelSheetToDataFrame(excelSheet1, rocket='上面级+最后发射')
    # dfUpperStages = dfList[:-1] # 上面级
    # dfLastLaunch = dfList[-1] # 最后的发射
    dictUpperStage, dfLastLaunch = myPlot.readUpperStageDict()
    lastLaunch = getLastLaunch(dfLastLaunch, series, privates, dictUpperStage)

    window = getWindow(years, rockets, series, retired, privates, locations, categories, payloads, lastLaunch)
    moveWindow(window, y=0)

    while True:
        event, values = window.read(timeout=0)

        if event == sg.WIN_CLOSED or event == 'Exit':
            break

        handleEvents(excelSheet1, event, window, values, years, rockets, retired, series, locations, categories, payloads, dictUpperStage, dfLastLaunch)
        window.Normal()
    
    window.close()

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')
    
if __name__ == "__main__":
    showRunTime("main()")