from datetime import timedelta
from timeit import timeit
from os import path
import FreeSimpleGUI as sg

from myModules import myPlot
from myModules import myShape
from myModules import myExcel
from myModules import myFile
from myModules import myDate
from myModules import myGUI

BUTTON_SAVE = 'Save'
BUTTON_SHOW_ROUTE_BEARING = 'Show Route Bearing'
BUTTON_DISPLAY_MODE = 'Display Mode'
BUTTON_SHOW_NAMES = 'Show Names'
BUTTON_COMPARE = 'Compare KML'
BUTTON_EXIT = 'Exit'

NEW_FOLDER = 'NewFolder'
NEW_SUBFOLDERS = 'NewSubfolders'
OLD_FOLDER = 'OldFolder'
OLD_SUBFOLDERS = 'OldSubfolders'

GEOMTRIES_COUNT = 12

################################################################################################
def main():
    import locale
    import sys
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    sys.stdout.reconfigure(encoding='UTF-8')

    myDate.setStartTime()
    myGUI.setScreenDpiAware()    
    cn_font = myPlot.init()

    newNames = [[sg.Checkbox('', key=(0, i), visible=False, enable_events=True)] for i in range(GEOMTRIES_COUNT)]
    oldNames = [[sg.Checkbox('', key=(1, i), visible=False, enable_events=True)] for i in range(GEOMTRIES_COUNT)]

    window = getWindow(newNames, oldNames)
    for i in range(2):
        for j in range(GEOMTRIES_COUNT):
            window[(i, j)].widget.configure(indicatoron=False)

    myGUI.moveWindow(window, y=0)
    window[NEW_FOLDER].bind("<Return>", "_Enter")
    window[OLD_FOLDER].bind("<Return>", "_Enter")

    newSelectedFile = ''
    oldSelectedFile = ''
    projection = False
    plotLines = False
    plotPoints = False
    plotNames = False

    while True:
        event, values = window.read(timeout=0)
        # if event != '__TIMEOUT__':
        #     print(f'{event = }')
        #     print(f'{values = }')
        if event == sg.WIN_CLOSED or event == BUTTON_EXIT:
            break
        newSelectedFile, oldSelectedFile, projection, plotLines, plotPoints, plotNames, newNames, oldNames = \
            handleEvents(window, event, values, cn_font, newSelectedFile, oldSelectedFile, projection=projection, plotLines=plotLines, plotPoints=plotPoints, plotNames=plotNames, newNames=newNames, oldNames=oldNames)
        myGUI.moveWindow(window)
        window.Normal()
    window.close()

################################################################################################
def getWindow(newButtons, oldButtons):
    myGUI.setScreenDpiAware()
    sg.theme('Python')
    sg.set_options(text_justification='right')
    newPath = 'c:/users/w802479/downloads' if myFile.isWindows() else '/users/mikezang/downloads'
    oldPath = './notams/kmls'
    newSubfolders, _ = myFile.listFoldersFiles(newPath)
    oldSubfolders, _ = myFile.listFoldersFiles(oldPath)
    # subfolders, extList = myFile.listFoldersFiles('notams/maps')
    layout = getMiddleFrame(newSubfolders, newPath, oldSubfolders, oldPath, newButtons, oldButtons)
    window = sg.Window('Show KML/Image file and Compare KML files', layout, finalize=True, font=("Helvetica", 12))      
    return window

################################################################################################
def getButton():
    button = [
        sg.Button(BUTTON_SAVE, font=("Helvetica", 14), disabled=True), 
        sg.Button(BUTTON_SHOW_ROUTE_BEARING, font=("Helvetica", 14), disabled=True), 
        sg.Push(), 
        sg.Button(BUTTON_DISPLAY_MODE, font=("Helvetica", 14), disabled=True), 
        sg.Button(BUTTON_SHOW_NAMES, font=("Helvetica", 14), disabled=True), 
        # sg.Button(BUTTON_COMPARE, font=("Helvetica", 14), disabled=True), 
        sg.Push(), 
        sg.Button(BUTTON_EXIT, font=("Helvetica", 14))
    ]
    return button

################################################################################################
def getTopFrame():
    checkbox = [sg.Radio('合成图像视频', 'siwtchLayout', key='fileType101', enable_events=True, default=True),
                sg.Radio('配乐视频', 'siwtchLayout', key='fileType102', enable_events=True),
                sg.Radio('显示图像', 'siwtchLayout', key='fileType103', enable_events=True),
                sg.Radio('播放视频', 'siwtchLayout', key='fileType104', enable_events=True)]
    layout = [checkbox]
    return sg.Frame('选择任务类型', layout)

################################################################################################
def getMiddleFrame(newSubFolders, newPath, oldSubFolder, oldPath, newButtons, oldButtons):
    newFolders = [
        [sg.Input(path.abspath(newPath), readonly=False, justification='left',
            key=NEW_FOLDER, enable_events=True, size=60,
            disabled_readonly_background_color=sg.theme_input_background_color()),
        ],
        [sg.Listbox(newSubFolders, size=(60, 15), key=NEW_SUBFOLDERS, enable_events=True,
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, bind_return_key=True,
            highlight_background_color='blue', highlight_text_color='white')]
    ]
    oldFolders = [
        [sg.Input(path.abspath(oldPath), readonly=True, justification='left',
            key=OLD_FOLDER, enable_events=True, size=60,
            disabled_readonly_text_color='#A3A3A3',
            disabled_readonly_background_color=sg.theme_input_background_color()),
        ],
        [sg.Listbox(oldSubFolder, size=(60, 15), key=OLD_SUBFOLDERS, enable_events=True,
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, bind_return_key=True, disabled=True,
            highlight_background_color='blue', highlight_text_color='white')]
    ]
    columnFolders = [
        [sg.Frame('New File', newFolders)],
        [sg.Frame('Old File', oldFolders)],
        getButton()
    ]

    # newNames = [[sg.Checkbox('', f'{(0, i)}', key=(0, i), visible=False, enable_events=True)] for i in range(12)]
    buttons = newButtons
    buttons.append([sg.HorizontalSeparator(color='red', p=((0,0),(20,20)))])
    buttons.extend(oldButtons)

    imageBorder = [[sg.Image(key="-IMAGE-", size=myExcel.IMAGE_SIZE)]]
    
    layout = [[
            sg.Column(columnFolders), 
            sg.Frame("Selected File", imageBorder, size=(myExcel.IMAGE_SIZE[0]+20, myExcel.IMAGE_SIZE[1]+20), 
                     element_justification='center', vertical_alignment='center'),
            sg.Column(buttons)
    ]]
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
    if newNames:
        for i, (name, isShow) in enumerate(newNames.items()):
            window[(0, i)].update(text=name, visible=visible, value=isShow)
    else:
        i = -1
    for j in range(i+1, GEOMTRIES_COUNT):
        window[(0, j)].update(text='', visible=False)

    if oldNames:
        for i, (name, isShow) in enumerate(oldNames.items()):
            window[(1, i)].update(text=name, visible=visible, value=isShow)
    else:
        i = -1
    for j in range(i+1, GEOMTRIES_COUNT):
        window[(1, j)].update(text='', visible=False)

################################################################################################
def toogleButtons(window, disabled):
    window[BUTTON_SAVE].update(disabled=disabled)
    window[BUTTON_SHOW_ROUTE_BEARING].update(disabled=disabled)
    window[BUTTON_DISPLAY_MODE].update(disabled=disabled)
    window[BUTTON_SHOW_NAMES].update(disabled=disabled)

################################################################################################
def toogleOldFolders(window, readonly):
    window[OLD_FOLDER].update(readonly=readonly)
    window[OLD_SUBFOLDERS].update(disabled=readonly)

################################################################################################
def handleEvents(window, event, values, cn_font, newSelectedFile, oldSelectedFile=None, projection=False, plotLines=False, plotPoints=False, plotNames=False, newNames=None, oldNames=None):
    if event == NEW_FOLDER + '_Enter':
        newPath = path.abspath(values[NEW_FOLDER])
        if path.isdir(newPath):
            updateFolders(window, NEW_FOLDER, newPath, NEW_SUBFOLDERS)
        else:
            window[NEW_FOLDER].update(select=True)
    elif event == OLD_FOLDER + '_Enter':
        oldPath = path.abspath(values[OLD_FOLDER])
        if path.isdir(oldPath):
            updateFolders(window, OLD_FOLDER, oldPath, OLD_SUBFOLDERS)
        else:
            window[OLD_FOLDER].update(select=True)
    elif type(event) == tuple:
        if event[0] == 0:
            key = list(newNames)[event[1]]
            newNames[key] = values[event]
        else:
            key = list(oldNames)[event[1]]
            oldNames[key] = values[event]
        # TODO: add LineString or Point to check if LinsTring or Point
        # TODO: add zoom in/out
        if '°' in key:
            plotLines = values[event]
        image, newNames, oldNames = myShape.getImageFromKml(cn_font, newSelectedFile, oldSelectedFile, projection=projection, plotLines=plotLines, plotPoints=plotPoints, plotNames=plotNames, newNames=newNames, oldNames=oldNames)
        window["-IMAGE-"].update(data=image)
    elif event == NEW_SUBFOLDERS:
        toogleButtons(window, True)
        toogleOldFolders(window, True)
        newFolder = values[NEW_FOLDER]
        selectedFiles = values[NEW_SUBFOLDERS]
        if len(selectedFiles) == 1:
            newSelectedFile = path.abspath(newFolder + '/' + selectedFiles[0])
            if path.isdir(newSelectedFile):
                updateFolders(window, NEW_FOLDER, newSelectedFile, NEW_SUBFOLDERS)
            else:
                if newSelectedFile.endswith('.kml'):
                    plotLines = False
                    plotPoints = False
                    oldSelectedFile = None
                    image, newNames, oldNames = myShape.getImageFromKml(cn_font, newSelectedFile, oldSelectedFile, projection=projection, plotLines=plotLines, plotPoints=plotPoints, plotNames=plotNames)
                    if not image:
                        sg.popup_error(f'{newSelectedFile} open failed!', font=('Noto Serif CJK JP', 18))
                    else:
                        window["-IMAGE-"].update(data=image)
                        toogleGeometries(window, True, newNames, oldNames)
                        toogleButtons(window, False)
                        toogleOldFolders(window, False)
                        location, _ = myFile.getLocation(newSelectedFile)
                        if location:
                            kmlFolders = myFile.readConfigLocations()
                            oldFolder = path.abspath(kmlFolders[location[0]])
                            updateFolders(window, OLD_FOLDER, oldFolder, OLD_SUBFOLDERS)
                elif selectedFiles[0][-4:] in '.gif,.png,.jpg,.jpeg,.webp':
                    image = myPlot.getImage(newSelectedFile, size=myExcel.IMAGE_SIZE)
                    window["-IMAGE-"].update(data=image)
                    toogleGeometries(window, False)
                    window[BUTTON_SAVE].update(disabled=False)
    elif event == OLD_SUBFOLDERS:
        toogleButtons(window, True)
        oldFolder = values[OLD_FOLDER]
        selectedFiles = values[OLD_SUBFOLDERS]
        if len(selectedFiles) == 1:
            oldSelectedFile = path.abspath(oldFolder + '/' + selectedFiles[0])
            if path.isdir(oldSelectedFile):
                updateFolders(window, OLD_FOLDER, oldSelectedFile, OLD_SUBFOLDERS)
            else:
                if oldSelectedFile.endswith('.kml'):
                    image, newNames, oldNames = myShape.getImageFromKml(cn_font, newSelectedFile, oldSelectedFile, projection=projection, plotLines=plotLines, plotPoints=plotPoints, plotNames=plotNames)
                    toogleGeometries(window, True, newNames, oldNames)
                    window["-IMAGE-"].update(data=image)
                    toogleButtons(window, False)
    elif event == BUTTON_SHOW_NAMES:
        if newSelectedFile.endswith('.kml'):
            plotNames = not plotNames
            image, newNames, oldNames = myShape.getImageFromKml(cn_font, newSelectedFile, oldSelectedFile, projection=projection, plotLines=plotLines, plotPoints=plotPoints, plotNames=plotNames, newNames=newNames, oldNames=oldNames)
            window["-IMAGE-"].update(data=image)
    elif event == BUTTON_DISPLAY_MODE:
        projection = not projection
        image, newNames, oldNames = myShape.getImageFromKml(cn_font, newSelectedFile, oldSelectedFile, projection=projection, plotLines=plotLines, plotPoints=plotPoints, plotNames=plotNames, newNames=newNames, oldNames=oldNames)
        window["-IMAGE-"].update(data=image)
    elif event == BUTTON_SHOW_ROUTE_BEARING:
        if newSelectedFile.endswith('.kml'):
            if myShape.showRouteAngle(newSelectedFile, newNames) is not None:
                image, newNames, oldNames = myShape.getImageFromKml(cn_font, newSelectedFile, oldSelectedFile, projection=projection, plotLines=plotLines, plotPoints=plotPoints, plotNames=plotNames, newNames=newNames, oldNames=oldNames)
                window["-IMAGE-"].update(data=image)
    elif event == BUTTON_SAVE:
        filename = sg.popup_get_file('Choose file (PNG, JPG, GIF) to save to', save_as=True)
        saveElementAsFile(window['-IMAGE-'], filename)
    return newSelectedFile, oldSelectedFile, projection, plotLines, plotPoints, plotNames, newNames, oldNames

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')
    
if __name__ == "__main__":
    showRunTime("main()")
