from sys import argv
from timeit import timeit
from datetime import datetime, timedelta
from re import findall 

from myModules import myExcel
from myModules import myFile
from myModules import myConfig
from myModules import myGUI
from myModules import myPlotInit

# CHROME = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
BUTTON1_IMAGE = '统计条形图作成'
BUTTON2_VIDEO = '发射动态条形图作成'
BUTTON3_VIDEO = '航天员动态条形图作成'
DATA_FILE_PATH = './data/'
EXCEL_FILE = myConfig.readConfig('ExcelFile', False)
SHEET_LAUNCH = myConfig.readConfig('SheetLaunch', False)
SHEET_TAIKO = myConfig.readConfig('SheetTaiko', False)

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
    import FreeSimpleGUI as sg
    subYears = splitStringToList(years, 15)
    yearsTitle = [
        sg.Checkbox('选择全发射期间', key='year01', enable_events=True),
        sg.Checkbox('仅生成最后图表', key='year02', default=True),
    ]
    layout1 = [yearsTitle]
    for i, subYear in enumerate(subYears):
        checkbox = [sg.Checkbox(item, key=f'year-{i * 10 + j + 1}', default=True if item == lastYear else False) for j, item in enumerate(subYear)]
        layout1.append(checkbox)
    return [sg.Frame('发射期间（统计条形图/动态条形图）', layout1)]

def getRocketsFrame(rockets, retired, lastRocket):
    import FreeSimpleGUI as sg
    rocketsCZ = splitStringToList(rockets[0])
    rocketsNCZ = splitStringToList(rockets[1])
    retiredCZ = splitStringToList(retired[0])
    retiredNCZ = splitStringToList(retired[1])
    rocketsTitle = [
        sg.Checkbox('选择全运载火箭', key='rocket01', enable_events=True),
        sg.Checkbox('仅生成最后图表', key='rocket02', default=True),
        sg.Checkbox('退役火箭', key='rocket03', enable_events=True),
        sg.Checkbox('显示发射一览', key='rocket04', default=False),
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
    return sg.Frame('运载火箭（统计条形图）', rockets)

def getSeriesFrame(series, lastSeries, lastResult, lastNumber, lastLaunchDate):
    import FreeSimpleGUI as sg
    seriesCZ = splitStringToList(series[0])
    seriesNCZ = splitStringToList(series[1])
    seriesCZRockets = splitStringToList(series[2])
    seriesNCZRockets = splitStringToList(series[3])
    seriesAll = splitStringToList(series[4])
    year = str(lastLaunchDate.year)
    springFestival = myConfig.readConfigSpringFestival(year)[0]
    before = (datetime.strptime(springFestival, '%Y-%m-%d') - lastLaunchDate).days
    after = (lastLaunchDate - datetime.strptime(springFestival, '%Y-%m-%d')).days
    checkSpringFestival = (before > 0 and before < 15) or (after > 0 and after < 15)
    firstInYear = (lastLaunchDate - datetime.strptime(f'{year}0101', '%Y%m%d')).days
    lastInYear = (datetime.strptime(f'{year}1231', '%Y%m%d') - lastLaunchDate).days
    checkFirstLast = (firstInYear > 0 and firstInYear < 15) or (lastInYear > 0 and lastInYear < 15)

    seriesTitle = [
        sg.Checkbox('选择全运载火箭系列', key='series01', enable_events=True),
        sg.Checkbox('仅生成最后图表', key='series02', default=True),
        sg.Checkbox('退役火箭系列', key='series03', enable_events=True),
        sg.Checkbox('发射失败系列', key='series04', enable_events=True, default=not lastResult),
        sg.Checkbox('首飞发射', key='series05', enable_events=False, default=lastNumber == '遥1'),
        sg.Checkbox('春节前后发射', key='series06', enable_events=False, default=checkSpringFestival),
        sg.Checkbox('年初年末发射', key='series07', enable_events=False, default=checkFirstLast),
    ]
    row = [seriesTitle]
    for i, subSeries in enumerate(seriesAll):
        checkbox = [sg.Checkbox(item, key=f'series-{i * 10 + j + 1}', size=(12, 1), 
                                default=True if item in lastSeries else False) 
                                for j, item in enumerate(subSeries)]
        row.append(checkbox)      
    for i, subSeries in enumerate(seriesCZ):
        checkbox = [sg.Checkbox(rocket, key=f'series-CZ{i * 10 + j + 1}', size=(12, 1), 
                                default=True if rocket in lastSeries else False, tooltip=rockets.replace('|', ',')) 
                                for j, (rocket, rockets) in enumerate(zip(subSeries, seriesCZRockets[i]))]
                                
        row.append(checkbox)      
    for i, subSeries in enumerate(seriesNCZ):
        checkbox = [sg.Checkbox(rocket, key=f'series-NCZ{i * 10 + j + 1}', size=(12, 1),
                                default=True if rocket in lastSeries else False, tooltip=rockets.replace('|', ',')) 
                                for j, (rocket, rockets) in enumerate(zip(subSeries, seriesNCZRockets[i]))]
        row.append(checkbox)      
    return sg.Frame('运载火箭系列（统计条形图）', row)

def getLocationsFrame(locations, lastLocation):
    import FreeSimpleGUI as sg
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
                checkbox.append(sg.Checkbox(item, key=f'location-{i * 10 + j + 1}', default=True if item == lastLocation else False))
            else:
                checkbox.append(sg.Checkbox(item, key=f'location-{i * 10 + j + 1}', default=True if item == lastLocation else False))
        layout5.append(checkbox)      
    return sg.Frame('发射位置（统计条形图）', layout5)

def getCategoriesFrame(categories, lastCategory):
    import FreeSimpleGUI as sg
    subCategories = categories.split(',')
    categoriesTitle = [sg.Checkbox('选择全运载火箭分类', key='category01', enable_events=True, default=True)]
    layout2 = [categoriesTitle]
    layout2.append([sg.Checkbox(item, key=f'category-{i + 1}', default=True) for i, item in enumerate(subCategories)])      
    return sg.Frame('运载火箭分类（动态条形图）', layout2)

def getTaikonautsFrame(taikonauts):
    import FreeSimpleGUI as sg
    subTaikonauts = taikonauts.split(',')
    layout2 = [[sg.Radio(subTaikonauts[0], 'taikonaut', key='taikonaut-1', enable_events=True, default=True), 
                sg.Radio(subTaikonauts[1], 'taikonaut', key='taikonaut-2', enable_events=True)]]
    lastLaunchDate = datetime.strptime(subTaikonauts[3].split('(')[1][:-1], '%Y年%m月%d日')
    days = (datetime.today() - lastLaunchDate).days
    layout2.append([sg.Radio(subTaikonauts[2], 'taikonaut', key='taikonaut-3', enable_events=True),
                    sg.Radio(f'{subTaikonauts[3]}＝在轨{days}日', 'taikonaut', key='taikonaut-4', enable_events=True)])
    return sg.Frame('在轨航天员分类（动态条形图）', layout2)

def getPayloadsFrame(payloads, lastPayload:tuple):
    import FreeSimpleGUI as sg
    subPayloads = splitStringToList(payloads, 11)
    payloadsTitle = [sg.Checkbox('选择全载荷系列', key='payload01', enable_events=True),
                     sg.Checkbox('仅生成最后图表', key='payload02', default=True)]
    layout = [payloadsTitle]

    css = ''
    for payload in lastPayload:
        if payload in myConfig.readConfig(['空间站']):
            css = '空间站' 
            break
            
    for i, subPayload in enumerate(subPayloads):
        checkbox = [sg.Checkbox(item if item[0] != '^' else item[1:], 
                    text_color=sg.theme_element_text_color() if item[0] != '^' else 'orange', 
                    default=True if item == css or item in lastPayload or item[1:] in lastPayload else False,
                    key=f'payload-{i * 11 + j + 1}', size=(10, 1)) for j, item in enumerate(subPayload)]
        layout.append(checkbox)
    return sg.Frame('载荷系列（统计条形图，无色=载荷名含有文字，桔色=载荷名开头文字）', layout)

################################################################################################
def getButton():
    import FreeSimpleGUI as sg
    button = [
        sg.Button(BUTTON1_IMAGE, font=("Helvetica", 14)), 
        sg.Button(BUTTON2_VIDEO, font=("Helvetica", 14)), 
        sg.Button(BUTTON3_VIDEO, font=("Helvetica", 14)), 
        sg.Push(), 
        sg.Button('Exit', font=("Helvetica", 14))
    ]
    return button

################################################################################################
def getWindow(years, rockets, series, retired, privates, locations, categories, taikonauts, payloads, lastLaunch):
    lastYear = lastLaunch[0]
    lastRocket = lastLaunch[1]
    lastNumber = lastLaunch[2]
    lastUpperStage = lastLaunch[3]
    lastSeries = lastLaunch[4]
    lastCategory = lastSeries
    lastCategory.append('系列')
    lastLocation = lastLaunch[5]
    lastResult = lastLaunch[6]
    lastPayload = lastLaunch[7]
    lastLaunchDate = lastLaunch[8]

    layout = []
    layout.append([getYearsFrame(years, lastYear)])  
    layout.append([getRocketsFrame(rockets, retired, lastRocket)])  
    layout.append([getSeriesFrame(series, lastSeries, lastResult, lastNumber, lastLaunchDate)])  
    layout.append([getLocationsFrame(locations, lastLocation), getCategoriesFrame(categories, lastCategory), getTaikonautsFrame(taikonauts)])  
    # layout.append([getPayloadsFrame(payloads, lastPayload)])
    layout.append(getButton())  

    import FreeSimpleGUI as sg
    window = sg.Window('中国运载火箭发射统计图表作成', layout, finalize=True, font=("Helvetica", 12))      
    return window

def getResolution():
    import tkinter
    root = tkinter.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    return width, height

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
def getSelectedItems(values, items, prefix) -> list:
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
def getLastLaunch(dfLastLaunch, series, privates, dictUpperStages, payloads):
    lastYear = str(datetime.today().year)
    lastRocket = dfLastLaunch[myExcel.EXCEL_COLUMN_ROCKET]
    lastNumber = dfLastLaunch[myExcel.EXCEL_COLUMN_NUMBER]
    lastRemarks = dfLastLaunch[myExcel.EXCEL_COLUMN_REMARKS]
    lastResult = True if dfLastLaunch[myExcel.EXCEL_COLUMN_RESULT] == '成功' else False
    lastUpperStage = f'{lastRocket}{lastNumber}/{lastRemarks}' in dictUpperStages
    lastSeries = getLastSeries(lastRocket, series, privates, lastUpperStage)
    lastLocation = dfLastLaunch[myExcel.EXCEL_COLUMN_LOCATION]
    lastPayload = getLastPayload(payloads, dfLastLaunch[myExcel.EXCEL_COLUMN_PAYLOAD])
    lastLaunchDate = dfLastLaunch[myExcel.EXCEL_COLUMN_DATE]
    lastLaunch = [lastYear, lastRocket, lastNumber, lastUpperStage, lastSeries, lastLocation, lastResult, lastPayload, lastLaunchDate]
    return lastLaunch

################################################################################################
def getLastPayload(payloads, lastPayloads):
    payloadsPattern = payloads.replace(',', '|')
    matched = findall(payloadsPattern, lastPayloads)
    lastPayload = matched if len(matched) > 0 else ''
    return tuple(set(lastPayload))

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

################################################################################################
def showRetiredRockets(window, values):
    isChecked = values['rocket03']
    window['rockets'].update(visible=not isChecked)
    window['retired'].update(visible=isChecked)
    if isChecked:
        for key, value in values.items():
            if 'retired-' in key:
                window[key].update(True)    

################################################################################################
def showFirstLastLunarNewYearSeries(window, values):
    import FreeSimpleGUI as sg
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
    import FreeSimpleGUI as sg
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
def handleEvents(window, event, values, df, years, rockets, retired, series, locations, categories, taikonauts, payloads, dictUpperStages, dfLastLaunch):
    # if event == 'taikonaut-1':
    #     window['taikonaut-1'].update(value=True)
    #     window['taikonaut-2'].update(value=False)
    # elif event == 'taikonaut-2':
    #     window['taikonaut-2'].update(value=True)
    #     window['taikonaut-1'].update(value=False)
    if event == 'year01':
        toogleAllCheckbox(window, values, 'year-')
    elif event == 'rocket01':
        toogleAllCheckbox(window, values, 'rocket-')
        toogleAllCheckbox(window, values, 'retired-')
    elif event == 'rocket03':
        showRetiredRockets(window, values)
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
    # elif event == 'payload01':
    #     toogleAllCheckbox(window, values, 'payload-')
    elif event == BUTTON1_IMAGE:
        window.minimize()
        import plotLaunchByDate
        import plotLaunchByRocket
        import plotLaunchByLocation
        import plotLaunchByYearMonth

        df = myExcel.parseExcelSheetLaunch(EXCEL_FILE, SHEET_LAUNCH)
        rocketList = values['rocket04'] # print list
        if rocketList:
            yearsChecked = getSelectedItems(values, years, 'year')
            if yearsChecked:
                years = splitYearsChecked(yearsChecked)
                for year in years:
                    plotLaunchByDate.printRocketsPayloadsList(df, year)

            rocketRetired = values['rocket03']
            if rocketRetired:
                rocketsChecked = getSelectedItems(values, retired, 'retired')
            else:
                rocketsChecked = getSelectedItems(values, rockets, 'rocket')
            plotLaunchByDate.printRocketsPayloadsList(df, rocketsChecked)

            # payloadsChecked = getSelectedItems(values, payloads, 'payload')
            # if payloadsChecked:
            #     plotLaunchByDate.printRocketsPayloadsList(df, payloadsChecked)
                                                          
            myFile.playSound()
            return
        
        yearsChecked = getSelectedItems(values, years, 'year')
        rocketsChecked = getSelectedItems(values, rockets, 'rocket')
        retiredChecked = getSelectedItems(values, retired, 'retired')
        seriesChecked = getSelectedItems(values, series, 'series')
        locationsChecked = getSelectedItems(values, locations, 'location')
        # payloadsChecked = getSelectedItems(values, payloads, 'payload')
        yearPrintLast = values['year02']
        rocketPrintLast = values['rocket02']
        rocketRetired = values['rocket03']
        seriesPrintLast = values['series02']
        seriesRetired = values['series03']
        seriesFailed = values['series04']
        seriesMaiden = values['series05']
        seriesLunarNewYear = values['series06']
        seriesFirstLast = values['series07']
        locationPrintLast = values['location02']
        # payloadPrintLast = values['payload02']
        cn_font = myPlotInit.init()

        if yearsChecked:
            print(f'\nYear Checked: {yearsChecked}', end='', flush=True)
            yearsChecked = splitYearsChecked(yearsChecked)

            if seriesChecked:
                print(f' and Series Checked: {seriesChecked}')
            else:
                print()
            for years in yearsChecked:
                for year in years:
                    if int(year) <= df.iloc[-1]['日期'].year:
                        plotLaunchByRocket.plot1(cn_font, df, year, seriesChecked)
                        plotLaunchByLocation.plot2(cn_font, df, year)
                    else:
                        print(f'No data in year {year}!')

                if int(years[0]) <= df.iloc[-1]['日期'].year:
                    if len(years) == 2:
                        plotLaunchByDate.plot1(cn_font, df, years[0], years[1], dictUpperStages, printLast=yearPrintLast)
                    else:
                        plotLaunchByDate.plot1(cn_font, df, years[0], upperStages=dictUpperStages, printLast=yearPrintLast)

                    plotLaunchByYearMonth.plot1(cn_font, df, years, seriesChecked, seriesPrintLast)

        if rocketsChecked or retiredChecked:
            if rocketsChecked:
                print(f'\nRocket Checked: {rocketsChecked}')
                plotLaunchByDate.plot3(cn_font, df, rocketsChecked, dictUpperStages, rocketPrintLast)
            if rocketRetired:
                print(f'\nRetired Checked: {retiredChecked}')
                retiredCZ, retiredNCZ = splitRetiredRockets(retiredChecked)
                plotLaunchByDate.plot8(cn_font, df, retiredCZ, retiredNCZ, dictUpperStages, seriesPrintLast)

        if seriesChecked:
            print(f'\nSeries Checked: {seriesChecked}')
            plotLaunchByYearMonth.plot1(cn_font, df, seriesList=seriesChecked, printLast=seriesPrintLast)
            plotLaunchByLocation.plot2(cn_font, df, seriesList=seriesChecked)

            if seriesMaiden:
                plotLaunchByDate.plotGraphForMaiden(cn_font, df, dictUpperStages, seriesChecked, seriesPrintLast)
            if seriesLunarNewYear:
                plotLaunchByDate.plotGraphForLunarNewYear(cn_font, df, dictUpperStages, seriesPrintLast)
            if seriesFirstLast:
                plotLaunchByDate.plotGraphForFirstLast(cn_font, df, dictUpperStages)
            if seriesFailed or seriesRetired:
                if seriesFailed:
                    plotLaunchByDate.plot6(cn_font, df, seriesChecked, dictUpperStages, seriesPrintLast)
                if seriesRetired:
                    plotLaunchByDate.plot7(cn_font, df, retired[0].split(','), retired[1].split(','), dictUpperStages, seriesPrintLast)
            plotLaunchByRocket.plot1(cn_font, df, seriesList=seriesChecked)
            seriesChecked = removeSeriesText(seriesChecked)
            plotLaunchByDate.plot2(cn_font, df, seriesChecked, dictUpperStages, seriesPrintLast, dfLastLaunch)

        if locationsChecked:
            print(f'\nLocation Checked: {locationsChecked}')
            plotLaunchByDate.plot4(cn_font, df, locationsChecked, dictUpperStages, locationPrintLast)

        # if payloadsChecked:
        #     print(f'\nPayload Checked: {payloadsChecked}')
        #     plotLaunchByDate.plot5(cn_font, df, payloadsChecked, dictUpperStages, payloadPrintLast)
        print('Plot finished!')
        myFile.playSound()
        window.Normal()

    elif event == BUTTON2_VIDEO:
        window.minimize()
        import plotLaunchBarChartRace
        cn_font = myPlotInit.init(True)
        categoriesChecked = getSelectedItems(values, categories, 'category-')

        if categoriesChecked:
            print(f'\nCategory Checked: {categoriesChecked}')
            df = myExcel.parseExcelSheetLaunch(EXCEL_FILE, SHEET_LAUNCH)
            startYear = categoriesChecked[0]
            for category in categoriesChecked:
                if category.isdigit():
                    plotLaunchBarChartRace.plot1(df, [category])
                else:
                    if startYear.isdigit():
                        plotLaunchBarChartRace.plot2(df, category, startYear)
                    else:
                        plotLaunchBarChartRace.plot2(df, category)
        print('Plot finished!')
        myFile.playSound()
        window.Normal()

    elif event == BUTTON3_VIDEO:
        window.minimize()
        import plotLaunchBarChartRace
        cn_font = myPlotInit.init(True)
        taikonautChecked = getSelectedItems(values, taikonauts, 'taikonaut-')

        if taikonautChecked:
            print(f'\nTaikonaut Checked: {taikonautChecked}')
            if '最初' in taikonautChecked[0]:
                plotLaunchBarChartRace.plot3(EXCEL_FILE, SHEET_TAIKO, plotLastFrames=False)
            else:
                dateLastLaunch = taikonautChecked[0].split('(')[1][:-1]
                yearTaikonaut = dateLastLaunch[:4]
                dateLatsLaunchDatetime = datetime.strptime(dateLastLaunch, '%Y年%m月%d日')
                today = datetime.today()
                days = (today - dateLatsLaunchDatetime).days + 1
                plotLaunchBarChartRace.plot3(EXCEL_FILE, SHEET_TAIKO, yearTaikonaut, days)
        print('Plot finished!')
        myFile.playSound()
        window.Normal()

################################################################################################
def printUsage():
    print('\nUsage:')
    print(f'  {"plot".ljust(26)} :显示画面')
    print(f'  {"plot yao".ljust(26)} :显示现役火箭未使用遥号')
    print(f'  {"plot 年".ljust(26 - 1)} :生成年全部发射')
    print(f'  {"plot 年月".ljust(26 - 2)} :生成年月全部发射')
    print(f'  {"plot 年/年月 下记其他选项".ljust(26 - 9)} :生成年其他选项发射')
    print(f'  {"plot 火箭名".ljust(26 - 3)} :生成火箭发射')
    print(f'  {"plot 载荷名".ljust(26 - 3)} :生成包含载荷名发射')
    print(f'  {"plot 发射地".ljust(26 - 3)} :生成发射地发射')
    print(f'  {"plot regexp".ljust(26 - 0)} :生成符合正则表达式发射')
    print(f'  {"plot 遥?".ljust(26 - 1)} :生成火箭发射遥?')
    print(f'  {"plot \"^载荷名\"".ljust(26 - 3)} :生成载荷名开始的发射')
    print(f'  {"plot \"?月\"".ljust(26 - 1)} :生成?月发射')
    print(f'  {"plot 春节".ljust(26 - 2)} :生成春节前后发射')
    print(f'  {"plot 年初年末".ljust(26 - 4)} :生成年初年末发射')
    print(f'  {"plot 首飞".ljust(26 - 2)} :生成首飞发射')
    print(f'  {"plot 空间站".ljust(26 - 3)} :生成空间站相关发射')
    print(f'  {"plot 上面级".ljust(26 - 3)} :生成上面级发射')

################################################################################################
def main():
    import locale
    import sys
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    sys.stdout.reconfigure(encoding='UTF-8')

    EXCEL_FILE, years, rockets, retired, series, privates, locations, categories, taikonauts, payloads = myConfig.readConfig()

    if len(argv) > 1:
        if argv[1].lower() == 'allvideos':
            import plotLaunchBarChartRace
            # cn_font = myPlotInit.init(True)
            year = str(datetime.today().year)
            categoriesChecked = ['民营', '其他', '长征', '系列', '全部', '在轨航天员']
            for category in categoriesChecked:
                if category == '在轨航天员':
                    plotLaunchBarChartRace.plot3(EXCEL_FILE, SHEET_TAIKO, year)
                else:
                    df = myExcel.parseExcelSheetLaunch(EXCEL_FILE, SHEET_LAUNCH)
                    plotLaunchBarChartRace.plot2(df, category, year)
            myFile.playSound()
            return
        elif argv[1].lower() == 'yao':
            import plotLaunchByDate
            df = myExcel.parseExcelSheetLaunch(EXCEL_FILE, SHEET_LAUNCH)
            rockets = myConfig.readConfigRockets()
            print('\n未使用遥号')
            plotLaunchByDate.printRocketsPayloadsList(df, rocketsPayloads=rockets, onlyPrintYaoNumber=True)
            return
        else:
            import plotLaunchByDate
            df = myExcel.parseExcelSheetLaunch(EXCEL_FILE, SHEET_LAUNCH)
            if argv[1].isdigit():
                years = argv[1].split('/')
                rocketsPayloads = argv[2].split('/') if len(argv) > 2 and argv[2].lower() != 'run' else None
            else:
                years = None                
                rocketsPayloads = argv[1].split('/')

            plotLaunchByDate.printRocketsPayloadsList(df, years=years, rocketsPayloads=rocketsPayloads)
            myFile.playSound()
            return
    
    printUsage()

    myGUI.setScreenDpiAware()

    from myModules import myPlot
    df = myExcel.parseExcelSheetLaunch(EXCEL_FILE, SHEET_LAUNCH)
    dictUpperStages, dfLastLaunch = myPlot.readUpperStageDict(df)
    lastLaunch = getLastLaunch(dfLastLaunch, series, privates, dictUpperStages, payloads)
    window = getWindow(years, rockets, series, retired, privates, locations, categories, taikonauts, payloads, lastLaunch)
    myGUI.moveWindow(window, y=0)
    import FreeSimpleGUI as sg

    while True:
        event, values = window.read(timeout=0)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        handleEvents(window, event, values, df, years, rockets, retired, series, locations, categories, taikonauts, payloads, dictUpperStages, dfLastLaunch)
    window.close()
    print()

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}\n')
    
if __name__ == "__main__":
    showRunTime("main()")