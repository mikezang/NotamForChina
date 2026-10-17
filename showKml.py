from datetime import timedelta
import io
from pathlib import Path
from timeit import timeit
from os import path
import FreeSimpleGUI as sg
from PIL import Image

from myModules import myPlotInit
from myModules import myExcel
from myModules import myFile
from myModules import myConfig
from myModules import myGUI
from myModules import mySys
from myModules import myExcept

BUTTON_MOVE_UP = "Move Center Up"
BUTTON_MOVE_DOWN = "Move Center Down"
BUTTON_MOVE_LEFT = "Move Center Left"
BUTTON_MOVE_RIGHT = "Move Center Right"

BUTTON_ZOOM_IN = "Zoom In"
BUTTON_ZOOM_OUT = "Zoom Out"
BUTTON_ZOOM_AUTO = "Zoom Auto"

BUTTON_FOLDER_SYNC_NEW = 'Folder Sync'
BUTTON_FOLDER_SYNC_OLD = 'Folder Sync'

BUTTON_SAVE = 'Save'
BUTTON_SHOW_ROUTE_BEARING = 'Show Route Bearing'
BUTTON_DISPLAY_MODE = 'Display Mode'
BUTTON_SHOW_NAMES = 'Show Names'
BUTTON_COMPARE = 'Compare KML'
BUTTON_EXIT = 'Exit'
BUTTON_SHOW_MERGE_OVERLAP = "Show Merge Overlap Drop Zones"

KEY_NEW_FOLDER = '=NEW_FOLDER='
KEY_NEW_SUB_FOLDERS = '=NEW_SUB_FOLDER='
KEY_OLD_FOLDER = '=OLD_FOLDER='
KEY_OLD_SUB_FOLDER = '=OLD_SUB_FOLDER='
KEY_IMAGE_WINDOW = '=IMAGE='

KEY_ZOOM_IN = "=ZOOM_IN="
KEY_ZOOM_OUT = "=ZOOM_OUT="
KEY_ZOOM_AUTO = "=ZOOM_AUTO="

KEY_MOVE_UP = "=MOVE_TOP="
KEY_MOVE_RIGHT = "=MOVE_RIGHT="
KEY_MOVE_DOWN = "=MOVE_BOTTOM="
KEY_MOVE_LEFT = "=MOVE_LEFT="

KEY_FOCUS_CENTER = "=FOCUS_CENTER_?="
KEY_NEW_GEOMETRY = "=NEW_GEOMETRY_?="
KEY_OLD_GEOMETRY = "=OLD_GEOMETRY_?="

KEY_ZOOM_MOVE_LIST = [KEY_ZOOM_AUTO, KEY_ZOOM_IN, KEY_ZOOM_OUT, KEY_MOVE_UP, KEY_MOVE_RIGHT, KEY_MOVE_DOWN, KEY_MOVE_LEFT]
KEY_MOVE_LIST = [KEY_MOVE_UP, KEY_MOVE_RIGHT, KEY_MOVE_DOWN, KEY_MOVE_LEFT]


MAX_GEOMTRIES_COUNT = 15

def getButtonsOnRight():
    zoomButtons = [
        [sg.Button(BUTTON_MOVE_UP, key=KEY_MOVE_UP, visible=False, enable_events=True, disabled=True, font=('Any', 9))], 
        [sg.Button(BUTTON_MOVE_DOWN, key=KEY_MOVE_DOWN, visible=False, enable_events=True, disabled=True, font=('Any', 9))], 
        [sg.Button(BUTTON_MOVE_LEFT, key=KEY_MOVE_LEFT, visible=False, enable_events=True, disabled=True, font=('Any', 9))], 
        [sg.Button(BUTTON_MOVE_RIGHT, key=KEY_MOVE_RIGHT, visible=False, enable_events=True, disabled=True, font=('Any', 9))], 
        [sg.Button(BUTTON_ZOOM_IN, key=KEY_ZOOM_IN, visible=False, enable_events=True, disabled=True, font=('Any', 9))], 
        [sg.Button(BUTTON_ZOOM_OUT, key=KEY_ZOOM_OUT, visible=False, enable_events=True, disabled=True, font=('Any', 9))],
        [sg.Checkbox(BUTTON_ZOOM_AUTO, key=KEY_ZOOM_AUTO, visible=False, enable_events=True, default=True, font=('Any', 9))]
    ]
    newNames = [[
            # sg.Column([[sg.Checkbox('', key=(0, j), visible=False, enable_events=True)]], pad=(0, 0)),
            sg.Column([[sg.Checkbox('', key=KEY_NEW_GEOMETRY.replace("?", str(j)), visible=False, enable_events=True, font=('Any', 9))]], pad=(0, 0)),
            sg.Push(), 
            sg.Column([[sg.Checkbox('C', key=KEY_FOCUS_CENTER.replace("?", str(j)), visible=False, enable_events=True, disabled=True, font=('Any', 9))]], pad=(0, 0))
        ] for j in range(MAX_GEOMTRIES_COUNT)]

    # oldNames = [[sg.Checkbox('', key=(1, i), visible=False, enable_events=True)] for i in range(MAX_GEOMTRIES_COUNT)]
    oldNames = [[sg.Checkbox('', key=KEY_OLD_GEOMETRY.replace("?", str(i)), visible=False, enable_events=True, font=('Any', 9))] for i in range(MAX_GEOMTRIES_COUNT)]
    return newNames, oldNames, zoomButtons

################################################################################################
def getWindow(newButtons, oldButtons, zoomButtons):
    myGUI.setScreenDpiAware()
    sg.theme('Python')
    sg.set_options(text_justification='right')
    newPath = 'c:/users/w802479/downloads' if mySys.isWindows() else '/users/mikezang/downloads'
    oldPath = './histories/kmls'
    newSubfolders, _ = myFile.listFoldersFiles(newPath)
    oldSubfolders, _ = myFile.listFoldersFiles(oldPath)
    # subfolders, extList = myFile.listFoldersFiles('histories/maps')
    layout = getWindowLayout(newSubfolders, newPath, oldSubfolders, oldPath, newButtons, oldButtons, zoomButtons)
    window = sg.Window('Show KML/Image file and Compare KML files', layout, finalize=True, font=("Helvetica", 12))      
    return window

################################################################################################
def getButton():
    button = [
        sg.Button(BUTTON_SAVE, font=("Helvetica", 14), disabled=True), 
        sg.Button(BUTTON_SHOW_ROUTE_BEARING, font=("Helvetica", 14), disabled=True), 
        sg.Button(BUTTON_DISPLAY_MODE, font=("Helvetica", 14), disabled=True), 
        sg.Button(BUTTON_SHOW_NAMES, font=("Helvetica", 14), disabled=True), 
        # sg.Button(BUTTON_COMPARE, font=("Helvetica", 14), disabled=True), 
        sg.Button(BUTTON_SHOW_MERGE_OVERLAP, font=("Helvetica", 14), disabled=True), 
        sg.Push(), 
        sg.Button(BUTTON_EXIT, font=("Helvetica", 14))
    ]
    return button

################################################################################################
# def getTopFrame():
#     checkbox = [sg.Radio('合成图像视频', 'siwtchLayout', key='fileType101', enable_events=True, default=True),
#                 sg.Radio('配乐视频', 'siwtchLayout', key='fileType102', enable_events=True),
#                 sg.Radio('显示图像', 'siwtchLayout', key='fileType103', enable_events=True),
#                 sg.Radio('播放视频', 'siwtchLayout', key='fileType104', enable_events=True)]
#     layout = [checkbox]
#     return sg.Frame('选择任务类型', layout)

def getNewFolders(newPath, newSubFolders):
    newFolders = [
        [
            sg.Input(path.abspath(newPath), readonly=False, justification='left',
                key=KEY_NEW_FOLDER, enable_events=True, size=50,
                disabled_readonly_background_color=sg.theme_input_background_color()),
            sg.Button(BUTTON_FOLDER_SYNC_NEW, size=10, disabled=False)
        ],
        [sg.Listbox(newSubFolders, size=(60, 15), key=KEY_NEW_SUB_FOLDERS, enable_events=True,
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, bind_return_key=True,
            highlight_background_color='blue', highlight_text_color='white')
        ]
    ]
    return newFolders

def getOldFolders(oldPath, oldSubFolder):
    oldFolders = [
        [
            sg.Input(path.abspath(oldPath), readonly=True, justification='left',
                key=KEY_OLD_FOLDER, enable_events=True, size=50,
                disabled_readonly_text_color='#A3A3A3',
                disabled_readonly_background_color=sg.theme_input_background_color()),
            sg.Button(BUTTON_FOLDER_SYNC_OLD, size=10, font=("Helvetica", 10), disabled=False)
        ],
        [sg.Listbox(oldSubFolder, size=(60, 15), key=KEY_OLD_SUB_FOLDER, enable_events=True,
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, bind_return_key=True, disabled=True,
            highlight_background_color='blue', highlight_text_color='white')
        ]
    ]
    return oldFolders

################################################################################################
def getWindowLayout(newSubFolders, newPath, oldSubFolder, oldPath, newButtons, oldButtons, zoomButtons):
    newFolders = getNewFolders(newPath, newSubFolders)
    oldFolders = getOldFolders(oldPath, oldSubFolder)
    columnFolders = [[sg.Frame('New File', newFolders)], [sg.Frame('Old File', oldFolders)]]

    imageBorder = [[sg.Image(key=KEY_IMAGE_WINDOW, size=myExcel.IMAGE_SIZE)]]
    
    buttons = zoomButtons.copy()
    buttons.append([sg.HorizontalSeparator(color='red', p=((0,0),(20,20)))])

    buttons.extend(newButtons)
    buttons.append([sg.HorizontalSeparator(color='red', p=((0,0),(20,20)))])
    buttons.extend(oldButtons)

    layout = [
        [
            sg.Column(columnFolders), 
            sg.Frame("Selected File", imageBorder, size=(myExcel.IMAGE_SIZE[0]+20, myExcel.IMAGE_SIZE[1]+20), element_justification='center', vertical_alignment='center'),
            sg.Column(buttons)], 
        [getButton()]]
    return layout

################################################################################################
def saveElementAsFile(element, filename):
    from PIL import ImageGrab
    widget = element.Widget
    x, y = widget.winfo_rootx(), widget.winfo_rooty()
    w, h = x + widget.winfo_width(), y + widget.winfo_height()
    box = (x, y, w, h)
    grab = ImageGrab.grab(bbox=box)
    grab.save(filename)

################################################################################################
def updateFolders(window, folderName, folderValue, subfolderName):
    window[folderName].update(select=False)
    window[folderName].update(value=folderValue)
    newSubfolders, _ = myFile.listFoldersFiles(folderValue)
    window[subfolderName].update(values=newSubfolders)

################################################################################################
def toogleGeometries(window, visible, newNames=None, oldNames=None):
    for key in KEY_ZOOM_MOVE_LIST: # zoom buttons
        window[key].update(visible=visible)

    if newNames:
        for j, (name, isShow) in enumerate(newNames.items()):
            window[KEY_NEW_GEOMETRY.replace("?", str(j))].update(text=name[:20], visible=visible, value=isShow)
            window[KEY_FOCUS_CENTER.replace("?", str(j))].update(visible=visible, disabled=not isShow, value=False)
        i = j
    else:
        i = -1

    for j in range(i + 1, MAX_GEOMTRIES_COUNT):
        window[KEY_NEW_GEOMETRY.replace("?", str(j))].update(text='', visible=False)
        window[KEY_FOCUS_CENTER.replace("?", str(j))].update(visible=False)

    if oldNames:
        for j, (name, isShow) in enumerate(oldNames.items()):
            window[KEY_OLD_GEOMETRY.replace("?", str(j))].update(text=name, visible=visible, value=isShow)
        i = j
    else:
        i = -1

    for j in range(i + 1, MAX_GEOMTRIES_COUNT):
        window[KEY_OLD_GEOMETRY.replace("?", str(j))].update(text='', visible=False)

################################################################################################
def toogleButtons(window, disabled):
    window[BUTTON_SAVE].update(disabled=disabled)
    window[BUTTON_SHOW_ROUTE_BEARING].update(disabled=disabled)
    window[BUTTON_DISPLAY_MODE].update(disabled=disabled)
    window[BUTTON_SHOW_NAMES].update(disabled=disabled)
    window[BUTTON_SHOW_MERGE_OVERLAP].update(disabled=disabled)

################################################################################################
def toogleOldFolders(window, readonly):
    window[KEY_OLD_FOLDER].update(readonly=readonly)
    window[KEY_OLD_SUB_FOLDER].update(disabled=readonly)

################################################################################################
def getImage(filename, resize=True, size=myExcel.IMAGE_SIZE):
    im = Image.open(filename)
    if resize:
        if im.size[0] > im.size[1]:
            resize = [size[0], size[1] * im.size[1] / im.size[0]]
        else:
            resize = [size[0] * im.size[0] / im.size[1], size[1]]
        resize = map(int, resize)
        im = im.resize(tuple(resize), Image.LANCZOS)
    with io.BytesIO() as buffer:
        im.save(buffer, format='PNG')
        image = buffer.getvalue()
    return image

################################################################################################
def scaleExtent(currentExtent, factor):
    minLon, minLat, maxLon, maxLat = currentExtent
    centerLon = (minLon + maxLon) / 2
    centerLat = (minLat + maxLat) / 2
    width = (maxLon - minLon) * factor
    height = (maxLat - minLat) * factor
    return centerLon - width / 2, centerLat - height / 2, centerLon + width / 2, centerLat + height / 2

################################################################################################
def moveExtent(zoomExtent, direction, fraction=0.5):
    minLon, minLat, maxLon, maxLat = zoomExtent
    lonMove = (maxLon - minLon) * fraction
    latMove = (maxLat - minLat) * fraction

    if direction == "left":
        lonMove = -lonMove
        latMove = 0

    elif direction == "right":
        lonMove = +lonMove
        latMove = 0

    elif direction == "up":
        latMove = +latMove
        lonMove = 0

    elif direction == "down":
        latMove = -latMove
        lonMove = 0

    return (minLon + lonMove, minLat + latMove, maxLon + lonMove, maxLat + latMove)

################################################################################################
def handleEvents(window, event, values, cn_font, newSelectedFile, oldSelectedFile=None, projection=False, plotLines=False, 
                 plotPoints=False, plotNames=False, newNames=None, oldNames=None, zoomExtent=None, centerIndex=None, 
                 autoExtent=None, manualExtentBeforeC=None, merged=True):

    zoomExtent = None if values[KEY_ZOOM_AUTO] == True else zoomExtent

    if event in KEY_ZOOM_MOVE_LIST:
        if event == KEY_ZOOM_AUTO:
            recenter = False
            if values[KEY_ZOOM_AUTO] == True: # zoom auto ON
                zoomExtent =  None
                for key in KEY_ZOOM_MOVE_LIST[1:]:
                    window[key].update(disabled=True)
            else:  # zoom auto OFF
                zoomExtent = autoExtent
                for key in KEY_ZOOM_MOVE_LIST[1:]:
                    window[key].update(disabled=False)
        elif event == KEY_ZOOM_IN:
            recenter = False
            zoomExtent =  scaleExtent(zoomExtent, 0.8)

        elif event == KEY_ZOOM_OUT:
            recenter = False
            zoomExtent =  scaleExtent(zoomExtent, 1.25)

        elif event in KEY_MOVE_LIST:
            # clear all C buttons
            centerIndex = None
            for key in range(0, MAX_GEOMTRIES_COUNT):
                window[KEY_FOCUS_CENTER.replace("?", str(key))].update(False) 

            if event == KEY_MOVE_UP:
                recenter = False
                zoomExtent = moveExtent(zoomExtent, "up", fraction=0.5)

            elif event == KEY_MOVE_DOWN:
                recenter = False
                zoomExtent = moveExtent(zoomExtent, "down", fraction=0.5)

            elif event == KEY_MOVE_LEFT:
                recenter = False
                zoomExtent = moveExtent(zoomExtent, "left", fraction=0.5)

            elif event == KEY_MOVE_RIGHT:
                recenter = False
                zoomExtent = moveExtent(zoomExtent, "right", fraction=0.5)

        if Path(newSelectedFile).is_file():
            from myModules import myShape
            image, newNames, oldNames, zoomExtent, centerIndex, autoExtent, merged = myShape.getImageFromKml(cn_font, newSelectedFile, oldSelectedFile, 
                    projection=projection, plotLines=plotLines, plotPoints=plotPoints, plotNames=plotNames, newNames=newNames, oldNames=oldNames, 
                    zoomExtent=zoomExtent, recenter=recenter, centerIndex=centerIndex, merged=merged)
            if not image:
                sg.popup_error(f'Invalid KML file: {newSelectedFile}!', font=('Noto Serif CJK JP', 18))
            else:
                window[KEY_IMAGE_WINDOW].update(data=image)
        else:
            sg.popup_error(f'{newSelectedFile} open failed!', font=('Noto Serif CJK JP', 18))

    elif event.startswith(KEY_NEW_GEOMETRY[:-2]):
        recenter = values[KEY_ZOOM_AUTO]

        for j in range(MAX_GEOMTRIES_COUNT):
            window[KEY_FOCUS_CENTER.replace("?", str(j))].update(False)

        index = event.split("_")[-1][:-1]
        window[KEY_FOCUS_CENTER.replace("?", index)].update(disabled=not values[event], value=False)
        key = list(newNames)[int(index)]
        newNames[key] = values[event]
        plotLines = True

        if Path(newSelectedFile).is_file():
            from myModules import myShape
            image, newNames, oldNames, zoomExtent, centerIndex, autoExtent, merged = myShape.getImageFromKml(cn_font, newSelectedFile, oldSelectedFile, 
                    projection=projection, plotLines=plotLines, plotPoints=plotPoints, plotNames=plotNames, newNames=newNames, oldNames=oldNames, 
                    zoomExtent=zoomExtent, recenter=recenter, centerIndex=centerIndex, merged=merged)
            if not image:
                sg.popup_error(f'Invalid KML file: {newSelectedFile}!', font=('Noto Serif CJK JP', 18))
            else:
                window[KEY_IMAGE_WINDOW].update(data=image)
        else:
            sg.popup_error(f'{newSelectedFile} open failed!', font=('Noto Serif CJK JP', 18))

    elif event.startswith(KEY_OLD_GEOMETRY[:-2]):
        recenter = values[KEY_ZOOM_AUTO]
        index = event.split("_")[-1][:-1]
        key = list(oldNames)[int(index)]
        oldNames[key] = values[event]

    elif event.startswith(KEY_FOCUS_CENTER[:-2]):
        recenter = values[KEY_ZOOM_AUTO]

        if values[event]: # Button C ON
            if not values[KEY_ZOOM_AUTO]:
                manualExtentBeforeC = zoomExtent

            for j in range(MAX_GEOMTRIES_COUNT):
                if event != KEY_FOCUS_CENTER.replace("?", str(j)):
                    window[KEY_FOCUS_CENTER.replace("?", str(j))].update(False)
                else:
                    centerIndex = j

        else: # Button C OFF
            centerIndex = None
            if not values[KEY_ZOOM_AUTO] and manualExtentBeforeC is not None:
                zoomExtent = manualExtentBeforeC
                manualExtentBeforeC = None

        if Path(newSelectedFile).is_file():
            from myModules import myShape
            image, newNames, oldNames, zoomExtent, centerIndex, autoExtent, merged = myShape.getImageFromKml(cn_font, newSelectedFile, oldSelectedFile, 
                    projection=projection, plotLines=plotLines, plotPoints=plotPoints, plotNames=plotNames, newNames=newNames, oldNames=oldNames, 
                    zoomExtent=zoomExtent, recenter=recenter, centerIndex=centerIndex, merged=merged)
            if not image:
                sg.popup_error(f'Invalid KML file: {newSelectedFile}!', font=('Noto Serif CJK JP', 18))
            else:
                window[KEY_IMAGE_WINDOW].update(data=image)
        else:
            sg.popup_error(f'{newSelectedFile} open failed!', font=('Noto Serif CJK JP', 18))

    # Handle folder
    elif event == KEY_NEW_FOLDER + '_Enter':
        newPath = path.abspath(values[KEY_NEW_FOLDER])
        if path.isdir(newPath):
            updateFolders(window, KEY_NEW_FOLDER, newPath, KEY_NEW_SUB_FOLDERS)
        else:
            window[KEY_NEW_FOLDER].update(select=True)
    elif event == KEY_OLD_FOLDER + '_Enter':
        oldPath = path.abspath(values[KEY_OLD_FOLDER])
        if path.isdir(oldPath):
            updateFolders(window, KEY_OLD_FOLDER, oldPath, KEY_OLD_SUB_FOLDER)
        else:
            window[KEY_OLD_FOLDER].update(select=True)

    # Hanlde new sub folders
    elif event == KEY_NEW_SUB_FOLDERS:
        recenter = True
        toogleButtons(window, True)
        toogleOldFolders(window, True)
        newFolder = values[KEY_NEW_FOLDER]
        selectedFiles = values[KEY_NEW_SUB_FOLDERS]

        if len(selectedFiles) == 1:
            newSelectedFile = path.abspath(newFolder + '/' + selectedFiles[0])
            
            if path.isdir(newSelectedFile):
                updateFolders(window, KEY_NEW_FOLDER, newSelectedFile, KEY_NEW_SUB_FOLDERS)
            else:
                if not Path(newSelectedFile).is_file():
                    sg.popup_error(f'Not found FILE: {newSelectedFile} !', font=('Noto Serif CJK JP', 18))
                else:
                    if newSelectedFile.endswith('.kml'):
                        from myModules import myShape
                        plotLines = False
                        plotPoints = False
                        oldSelectedFile = None
                        image, newNames, oldNames, zoomExtent, centerIndex, autoExtent, merged = myShape.getImageFromKml(cn_font, newSelectedFile, 
                                        oldSelectedFile, projection=projection, plotLines=plotLines, plotPoints=plotPoints, plotNames=plotNames, 
                                        zoomExtent=zoomExtent, merged=merged)
                        if not image:
                            sg.popup_error(f'Invalid KML file: {newSelectedFile}!', font=('Noto Serif CJK JP', 18))
                        else:
                            window[KEY_IMAGE_WINDOW].update(data=image)
                            toogleGeometries(window, True, newNames, oldNames)
                            toogleButtons(window, False)
                            toogleOldFolders(window, False)
                            site, _ = myConfig.readConfigSites(newSelectedFile)
                            if site:
                                kmlFolders = myConfig.readConfigSitesFolders()
                                oldFolder = path.abspath(kmlFolders[site[0]])
                                updateFolders(window, KEY_OLD_FOLDER, oldFolder, KEY_OLD_SUB_FOLDER)
                    elif newSelectedFile[0][-4:] in '.gif,.png,.jpg,.jpeg,.webp':
                        image = getImage(newSelectedFile, size=myExcel.IMAGE_SIZE)
                        window[KEY_IMAGE_WINDOW].update(data=image)
                        toogleGeometries(window, False)
                        window[BUTTON_SAVE].update(disabled=False)

    # Hanlde old sub folders
    elif event == KEY_OLD_SUB_FOLDER:
        recenter = True
        from myModules import myShape
        toogleButtons(window, True)
        oldFolder = values[KEY_OLD_FOLDER]
        selectedFiles = values[KEY_OLD_SUB_FOLDER]
        if len(selectedFiles) == 1:
            oldSelectedFile = path.abspath(oldFolder + '/' + selectedFiles[0])
            if path.isdir(oldSelectedFile):
                updateFolders(window, KEY_OLD_FOLDER, oldSelectedFile, KEY_OLD_SUB_FOLDER)
            else:
                if oldSelectedFile.endswith('.kml'):
                    from myModules import myShape
                    image, newNames, oldNames, zoomExtent, centerIndex, autoExtent, merged = myShape.getImageFromKml(cn_font, newSelectedFile, 
                                oldSelectedFile, projection=projection, plotLines=plotLines, plotPoints=plotPoints, plotNames=plotNames, 
                                zoomExtent=zoomExtent, merged=merged)
                    toogleGeometries(window, True, newNames, oldNames)
                    window[KEY_IMAGE_WINDOW].update(data=image)
                    toogleButtons(window, False)

    # Hanlde button at bottom
    elif event == BUTTON_FOLDER_SYNC_NEW:
        newFolder = values[KEY_OLD_FOLDER]
        updateFolders(window, KEY_NEW_FOLDER, newFolder, KEY_NEW_SUB_FOLDERS)

    elif event == BUTTON_FOLDER_SYNC_OLD:
        oldFolder = values[KEY_NEW_FOLDER]
        updateFolders(window, KEY_OLD_FOLDER, oldFolder, KEY_OLD_SUB_FOLDER)

    elif event == BUTTON_SHOW_NAMES:
        if newSelectedFile.endswith('.kml'):
            from myModules import myShape
            plotNames = not plotNames
            image, newNames, oldNames, zoomExtent, centerIndex, autoExtent, merged = myShape.getImageFromKml(cn_font, newSelectedFile, oldSelectedFile, 
                        projection=projection, plotLines=plotLines, plotPoints=plotPoints, plotNames=plotNames, newNames=newNames, oldNames=oldNames, 
                        zoomExtent=zoomExtent, merged=merged)
            window[KEY_IMAGE_WINDOW].update(data=image)

    elif event == BUTTON_DISPLAY_MODE:
        from myModules import myShape
        projection = not projection
        image, newNames, oldNames, zoomExtent, centerIndex, autoExtent, merged = myShape.getImageFromKml(cn_font, newSelectedFile, oldSelectedFile, 
                        projection=projection, plotLines=plotLines, plotPoints=plotPoints, plotNames=plotNames, newNames=newNames, oldNames=oldNames, 
                        zoomExtent=zoomExtent, merged=merged)
        window[KEY_IMAGE_WINDOW].update(data=image)

    elif event == BUTTON_SHOW_ROUTE_BEARING:
        from myModules import myShape
        if newSelectedFile.endswith('.kml'):
            if myShape.showRouteAngle(newSelectedFile, newNames) is not None:
                image, newNames, oldNames, zoomExtent, centerIndex, autoExtent, merged = myShape.getImageFromKml(cn_font, newSelectedFile, oldSelectedFile, 
                        projection=projection, plotLines=plotLines, plotPoints=plotPoints, plotNames=plotNames, newNames=newNames, oldNames=oldNames, 
                        zoomExtent=zoomExtent, merged=merged)
                window[KEY_IMAGE_WINDOW].update(data=image)

    elif event == BUTTON_SHOW_MERGE_OVERLAP:
        from myModules import myShape
        merged = not merged
        newNames = None
        oldNames = None
        image, newNames, oldNames, zoomExtent, centerIndex, autoExtent, merged = myShape.getImageFromKml(cn_font, newSelectedFile, oldSelectedFile, 
                projection=projection, plotLines=plotLines, plotPoints=plotPoints, plotNames=plotNames, newNames=newNames, oldNames=oldNames, 
                zoomExtent=zoomExtent, merged=merged)
        window[KEY_IMAGE_WINDOW].update(data=image)
        toogleGeometries(window, True, newNames, oldNames)

    elif event == BUTTON_SAVE:
        filename = sg.popup_get_file('Choose file (PNG, JPG, GIF) to save to', save_as=True)
        saveElementAsFile(window[KEY_IMAGE_WINDOW], filename)

    return newSelectedFile, oldSelectedFile, projection, plotLines, plotPoints, plotNames, \
        newNames, oldNames, zoomExtent, centerIndex, autoExtent, manualExtentBeforeC, merged

################################################################################################
def main():
    import locale
    import sys
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    sys.stdout.reconfigure(encoding='UTF-8')

    # from myModules import myDate
    # myDate.setStartTime()
    myGUI.setScreenDpiAware()    
    cn_font = myPlotInit.init()

    try:
        newNames, oldNames, zoomButtons = getButtonsOnRight()
        window = getWindow(newNames, oldNames, zoomButtons)

        for j in range(MAX_GEOMTRIES_COUNT):
            window[KEY_FOCUS_CENTER.replace("?", str(j))].widget.configure(indicatoron=False)
            window[KEY_NEW_GEOMETRY.replace("?", str(j))].widget.configure(indicatoron=False)
            window[KEY_OLD_GEOMETRY.replace("?", str(j))].widget.configure(indicatoron=False)

        window[KEY_ZOOM_AUTO].widget.configure(indicatoron=False)

        myGUI.moveWindow(window, y=0)
        window[KEY_NEW_FOLDER].bind("<Return>", "_Enter")
        window[KEY_OLD_FOLDER].bind("<Return>", "_Enter")

        newSelectedFile = ''
        oldSelectedFile = ''
        projection = False
        plotLines = False
        plotPoints = False
        plotNames = False
        zoomExtent = None
        centerIndex = None
        autoExtent = None
        # zoomExtentPrev = None
        # centerIndexPrev = None
        # autoExtentPrev = None
        manualExtentBeforeC = None
        merged = False

        while True:
            event, values = window.read(timeout=0)
            if event == sg.WIN_CLOSED or event == BUTTON_EXIT:
                break

            newSelectedFile, oldSelectedFile, projection, plotLines, plotPoints, plotNames, newNames, oldNames, \
                zoomExtent, centerIndex, autoExtent, manualExtentBeforeC, merged = \
                handleEvents(window, event, values, cn_font, newSelectedFile, oldSelectedFile, projection=projection, 
                            plotLines=plotLines, plotPoints=plotPoints, plotNames=plotNames, 
                            newNames=newNames, oldNames=oldNames, zoomExtent=zoomExtent, centerIndex=centerIndex, 
                            autoExtent=autoExtent, manualExtentBeforeC=manualExtentBeforeC, merged=merged)

            myGUI.moveWindow(window)
            window.Normal()
        window.close()
    except:
        myExcept.printExceptionTrace()
        pass

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')
    
if __name__ == "__main__":
    showRunTime("main()")
