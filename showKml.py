from datetime import timedelta
from timeit import timeit
import PySimpleGUI as sg
import os
# sys.path.append("myModues")
from myModules import constants
from myModules import myUtils
from myModules import myPlot

BUTTON_SAVE = 'Save'
BUTTON_DISPLAY_MODE = 'Display Mode'
BUTTON_SHOW_LINES = 'Show Lines'
BUTTON_COMPARE = 'Compare KML'
BUTTON_EXIT = 'Exit'

NEW_FOLDER = 'NewFolder'
NEW_SUBFOLDERS = 'NewSubfolders'
OLD_FOLDER = 'OldFolder'
OLD_SUBFOLDERS = 'OldSubfolders'

size = (900, 900)

os.environ['CARTOPY_USERS_BACKGROUNDS'] = './ne_50m'

################################################################################################
def main():
    myUtils.setStartTime()
    myPlot.setScreenDpiAware()    
    cn_font = myPlot.init()

    window, newSubfolders, oldSubfolders = getWindow()
    myPlot.moveWindow(window, y=0)
    window[NEW_FOLDER].bind("<Return>", "_Enter")
    window[OLD_FOLDER].bind("<Return>", "_Enter")

    newSelectedFile = ''
    oldSelectedFile = ''
    projection = False
    plotAll = False

    while True:
        event, values = window.read(timeout=0)
        if event == sg.WIN_CLOSED or event == BUTTON_EXIT:
            break
        newSubfolders, newSelectedFile, oldSubfolders, oldSelectedFile, projection, plotAll = \
            handleEvents(window, event, values, cn_font, newSubfolders, newSelectedFile, oldSubfolders, oldSelectedFile, projection=projection, plotAll=plotAll)
        window.Normal()
    window.close()

################################################################################################
def getWindow():
    myPlot.make_dpi_aware()
    sg.theme('Python')
    sg.set_options(text_justification='right')
    newPath = 'c:/users/w802479/downloads'
    oldPath = './notams/maps'
    newSubfolders, newExtList = myUtils.listFoldersFiles(newPath)
    oldSubfolders, oldExtList = myUtils.listFoldersFiles(oldPath)
    # subfolders, extList = myUtils.listFoldersFiles('notams/maps')
    layout = []
    layout.append(getMiddleFrame(newSubfolders, newPath, oldSubfolders, oldPath))
    window = sg.Window('Show KML/Image file and Compare KML files', layout, finalize=True, font=("Helvetica", 12))      
    return window, newSubfolders, oldSubfolders

################################################################################################
def getButton():
    button = [
        sg.Button(BUTTON_SAVE, font=("Helvetica", 14)), 
        sg.Push(), 
        sg.Button(BUTTON_DISPLAY_MODE, font=("Helvetica", 14), disabled=True), 
        sg.Button(BUTTON_SHOW_LINES, font=("Helvetica", 14), disabled=True), 
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
def getMiddleFrame(newSubFolders, newPath, oldSubFolder, oldPath):
    newFolders = [
        [sg.Input(os.path.abspath(newPath), readonly=False, justification='left',
            key=NEW_FOLDER, enable_events=True, size=60,
            disabled_readonly_background_color=sg.theme_input_background_color()),
        ],
        [sg.Listbox(newSubFolders, size=(60, 15), key=NEW_SUBFOLDERS, enable_events=True,
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, bind_return_key=True,
            highlight_background_color='blue', highlight_text_color='white')]
    ]
    oldFolders = [
        [sg.Input(os.path.abspath(oldPath), readonly=True, justification='left',
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

    imageBorder = [[sg.Image(key="-IMAGE-", size=size)]]
    layout = [[
            sg.Column(columnFolders), 
            sg.Frame("Selected File", imageBorder, size=(size[0]+20, size[1]+20), 
                     element_justification='center', vertical_alignment='center')
    ]]
    return layout

################################################################################################
def saveElementAsFile(element, filename):
    """
    Saves any element as an image file.  Element needs to have an underlyiong Widget available (almost if not all of them do)
    :param element: The element to save
    :param filename: The filename to save to. The extension of the filename determines the format (jpg, png, gif, ?)
    """
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
    newSubfolders, _ = myUtils.listFoldersFiles(folderValue)
    window[subfolderName].update(values=newSubfolders)

################################################################################################
def toogleButtons(window, disabled):
    window[BUTTON_DISPLAY_MODE].update(disabled=disabled)
    window[BUTTON_SHOW_LINES].update(disabled=disabled)

################################################################################################
def toogleOldFolders(window, readonly):
    window[OLD_FOLDER].update(readonly=readonly)
    window[OLD_SUBFOLDERS].update(disabled=readonly)

################################################################################################
def handleEvents(window, event, values, cn_font, newSubfolders, newSelectedFile, oldSubfolders, oldSelectedFile=None, projection=False, plotAll=False):
    if event == NEW_FOLDER + '_Enter':
        newPath = os.path.abspath(values[NEW_FOLDER])
        if os.path.isdir(newPath):
            updateFolders(window, NEW_FOLDER, newPath, NEW_SUBFOLDERS)
        else:
            window[NEW_FOLDER].update(select=True)
    elif event == OLD_FOLDER + '_Enter':
        oldPath = os.path.abspath(values[OLD_FOLDER])
        if os.path.isdir(oldPath):
            updateFolders(window, OLD_FOLDER, oldPath, OLD_SUBFOLDERS)
        else:
            window[OLD_FOLDER].update(select=True)
    elif event == NEW_SUBFOLDERS:
        toogleButtons(window, True)
        toogleOldFolders(window, True)
        newFolder = values[NEW_FOLDER]
        selectedFiles = values[NEW_SUBFOLDERS]
        if len(selectedFiles) == 1:
            newSelectedFile = os.path.abspath(newFolder + '/' + selectedFiles[0])
            if os.path.isdir(newSelectedFile):
                updateFolders(window, NEW_FOLDER, newSelectedFile, NEW_SUBFOLDERS)
            else:
                if newSelectedFile.endswith('.kml'):
                    oldSelectedFile = None
                    image = myPlot.getImageFromKml(cn_font, newSelectedFile, oldSelectedFile, size=size, projection=projection, plotAll=plotAll)
                    window["-IMAGE-"].update(data=image)
                    toogleButtons(window, False)
                    toogleOldFolders(window, False)
                    location, _ = myUtils.getLocation(newSelectedFile)
                    oldFolder = os.path.abspath(constants.KML_FOLDERS[location])
                    updateFolders(window, OLD_FOLDER, oldFolder, OLD_SUBFOLDERS)
                elif selectedFiles[0][-4:] in '.gif,.png,.jpg,.jpeg':
                    image = myPlot.getImage(newSelectedFile, size=size)
                    window["-IMAGE-"].update(data=image)
    elif event == OLD_SUBFOLDERS:
        toogleButtons(window, True)
        oldFolder = values[OLD_FOLDER]
        selectedFiles = values[OLD_SUBFOLDERS]
        if len(selectedFiles) == 1:
            oldSelectedFile = os.path.abspath(oldFolder + '/' + selectedFiles[0])
            if os.path.isdir(oldSelectedFile):
                updateFolders(window, OLD_FOLDER, oldSelectedFile, OLD_SUBFOLDERS)
            else:
                if oldSelectedFile.endswith('.kml'):
                    image = myPlot.getImageFromKml( cn_font, newSelectedFile, oldSelectedFile, size=size, projection=projection, plotAll=plotAll)
                    window["-IMAGE-"].update(data=image)
                    toogleButtons(window, False)
    elif event == BUTTON_SHOW_LINES:
        if newSelectedFile.endswith('.kml'):
            plotAll = not plotAll
            image = myPlot.getImageFromKml(cn_font, newSelectedFile, oldSelectedFile, size=size, projection=projection, plotAll=plotAll)
            window["-IMAGE-"].update(data=image)
    elif event == BUTTON_DISPLAY_MODE:
        projection = not projection
        image = myPlot.getImageFromKml(cn_font, newSelectedFile, oldSelectedFile, size=size, projection=projection, plotAll=plotAll)
        window["-IMAGE-"].update(data=image)
    elif event == BUTTON_SAVE:
        filename = sg.popup_get_file('Choose file (PNG, JPG, GIF) to save to', save_as=True)
        saveElementAsFile(window['-IMAGE-'], filename)
    return newSubfolders, newSelectedFile, oldSubfolders, oldSelectedFile, projection, plotAll

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')
    
if __name__ == "__main__":
    showRunTime("main()")

