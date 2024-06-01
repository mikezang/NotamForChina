from datetime import timedelta
import shutil
import subprocess
from sys import argv
from timeit import timeit
import PySimpleGUI as sg
import os

import myUtils
import myPlot

size = (900, 900)

################################################################################################
def main():
    myUtils.setStartTime()
    myPlot.setScreenDpiAware()    
    cn_font = myPlot.init()

    window, subfolders = getWindow()
    myPlot.moveWindow(window, y=0)
    window['Folder'].bind("<Return>", "_Enter")

    selectedFiles = []
    selectedFileTimes = []
    orthographic = False
    plotAll = False

    while True:
        event, values = window.read(timeout=0)
        if event == sg.WIN_CLOSED or event == BUTTON_EXIT:
            break
        subfolders, selectedFiles, selectedFileTimes, orthographic, plotAll = handleEvents(window, event, values, cn_font, subfolders, selectedFiles, selectedFileTimes, orthographic, plotAll)
        window.Normal()
    window.close()

################################################################################################
def getWindow():
    myPlot.make_dpi_aware()
    sg.theme('Python')
    sg.set_options(text_justification='right')      
    subfolders, extList = myUtils.listFoldersFiles('notams/maps')
    layout = []
    layout.append(getMiddleFrame(subfolders, extList))
    # layout.append(getButton())  
    window = sg.Window('Show KML file in Image', layout, finalize=True, font=("Helvetica", 12))      
    return window, subfolders

################################################################################################
def getWindow1():
    myPlot.make_dpi_aware()
    sg.theme('Python')
    sg.set_options(text_justification='right')      
    subfolders, extList = myUtils.listFoldersFiles()
    layout = []
    layout.append([getTopFrame()])  
    layout.append(getMiddleFrame(subfolders, extList))
    layout.append([getBottomFrame()])  
    layout.append(getButton())  
    window = sg.Window('Merge pictures/videos to video', layout, finalize=True, font=("Helvetica", 12))      
    return window, subfolders

BUTTON_SAVE = 'Save'
BUTTON_DISPLAY_MODE = 'Display Mode'
BUTTON_SHOW_LINES = 'Show Lines'
BUTTON_EXIT = 'Exit'

################################################################################################
def getButton():
    button = [
        sg.Button(BUTTON_SAVE, font=("Helvetica", 14)), 
        sg.Push(), 
        sg.Button(BUTTON_DISPLAY_MODE, font=("Helvetica", 14), disabled=True), 
        sg.Button(BUTTON_SHOW_LINES, font=("Helvetica", 14), disabled=True), 
        sg.Push(), 
        sg.Button(BUTTON_EXIT, font=("Helvetica", 14))
    ]
    return button

################################################################################################
def getTopFrame():
    # lastYear = '2024'
    # subYears = ['20232024']
    # yearsTitle = [sg.Checkbox('选择合成类型', key='fileType', enable_events=True)]
    # for i, subYear in enumerate(subYears):
    checkbox = [sg.Radio('合成图像视频', 'siwtchLayout', key='fileType101', enable_events=True, default=True),
                sg.Radio('配乐视频', 'siwtchLayout', key='fileType102', enable_events=True),
                sg.Radio('显示图像', 'siwtchLayout', key='fileType103', enable_events=True),
                sg.Radio('播放视频', 'siwtchLayout', key='fileType104', enable_events=True)]
    layout = [checkbox]
    return sg.Frame('选择任务类型', layout)

################################################################################################
def getBottomFrame():
    lastYear = '2024'
    subYears = ['2023', '2024']
    yearsTitle = [sg.Checkbox('选择全发射期间', key='year01', enable_events=True)]
    layout = [yearsTitle]
    # for i, subYear in enumerate(subYears):
    #     checkbox = [sg.Checkbox(item, key=f'year-{i * 10 + j + 1}', default=True if item == lastYear else False) for j, item in enumerate(subYear)]
    #     layout.append(checkbox)
    return sg.Frame('Bttom Frame', layout)

################################################################################################
def getMiddleFrame(subfolders, extList, curPath: str='.', ):
    columnSubFolders = [
        [sg.Input(os.path.abspath(curPath), readonly=False, justification='left',
            key='Folder', enable_events=True, size=60,
            disabled_readonly_background_color=sg.theme_input_background_color()),
        ],
        [sg.Listbox(subfolders, size=(60, 30), key='Subfolders', enable_events=True,
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, bind_return_key=True,
            highlight_background_color='blue', highlight_text_color='white')],
        getButton(),
    ]
    imageBorder = [[sg.Image(key="-IMAGE-", size=size)]]
    layout = [[
            sg.Column(columnSubFolders), 
            sg.Frame("Selected File", imageBorder, size=(size[0]+20, size[1]+20),
                vertical_alignment='center')
    ]]
    return layout

################################################################################################
def getMiddleFrame1(subfolders, extList, curPath: str='.', ):
    selected = []
    columnSubFolders = [
        [#sg.Text('Folder:'), 
         sg.Input(os.path.abspath(curPath), readonly=True, justification='left',
            key='Folder', enable_events=True, size=25,
            disabled_readonly_background_color=sg.theme_input_background_color()),
        #  sg.Text('Ext.:'), 
         sg.Combo(extList, default_value='*.*', size=(3, 1), key='Extension', enable_events=True)],        
        [sg.Listbox(subfolders, size=(25, 20), key='Subfolders',
            select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED, bind_return_key=True,
            highlight_background_color='blue', highlight_text_color='white')],
    ]
    columnButtons1 = [
        [sg.Button('→')], [sg.Button('→\n→')], 
        [sg.HorizontalSeparator(color='red', p=((0,0),(20,20)))],
        [sg.Button('←')], [sg.Button('←\n←')]
    ]

    frame_selected = [[sg.Listbox(selected, size=(30, 20), key='Selected',
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE)]]
    
    columnTimesize = [
        [sg.Text('Sum:'), 
         sg.Input('00:12:34', size=8, readonly=True, justification='left', key='TotalTime', enable_events=True, 
            disabled_readonly_background_color=sg.theme_input_background_color())],
        [sg.Listbox(selected, size=(10, 20), key='TimeSize',
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, disabled=False)]
        # TODO: '☑' and '☐' https://github.com/PySimpleGUI/PySimpleGUI/issues/3706
    ]
    columnButtons2 = [
        [sg.Button('↑')], [sg.Button('↑↑')], 
        [sg.HorizontalSeparator(color='red', p=((0,0),(20,20)))],
        [sg.Button('↓')], [sg.Button('↓↓')]
    ]


    layout = [[
            sg.Column(columnSubFolders), 
            sg.Column(columnButtons1, element_justification='center'),
            sg.Frame("Selected Files", frame_selected),
            sg.Column(columnTimesize),
            sg.Column(columnButtons2, element_justification='center'),
            # TODO: add list to show mp3/mp4 time or image size
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
def handleEvents(window, event, values, cn_font, subfolders: list, selectedFiles: list, selectedFileTimes: list, orthographic=False, plotAll=False) :
    if event == 'Folder_Enter':
        curPath = values['Folder']
        selectedItem = '*.*'
        subfolders, extList = myUtils.listFoldersFiles(curPath, selectedItem)
        window['Subfolders'].update(values=subfolders)
    elif event == 'Subfolders':
        window[BUTTON_DISPLAY_MODE].update(disabled=True)
        window[BUTTON_SHOW_LINES].update(disabled=True)
        selectedItems = values['Subfolders']
        if len(selectedItems) == 1:
            if os.path.isdir(selectedItems[0]):
                curPath = selectedItems[0]
                selectedItem = '*.*'
                subfolders, extList = myUtils.listFoldersFiles(curPath, selectedItem)
                window['Subfolders'].update(values=subfolders)
                window['Folder'].update(value=os.path.abspath('.'))
            else:
                folder = values['Folder']
                filename = f'{folder}/{selectedItems[0]}'
                if selectedItems[0].endswith('.kml'):
                    image = myPlot.getImageFromKml(filename, cn_font, size=size, orthographic=orthographic, plotAll=plotAll)
                    window["-IMAGE-"].update(data=image)
                    isKmlFile = True
                    window[BUTTON_DISPLAY_MODE].update(disabled=False)
                    window[BUTTON_SHOW_LINES].update(disabled=False)
                elif selectedItems[0][-4:] in '.png,.jpg,.jpeg':
                    image = myPlot.getImage(filename, size=size)
                    window["-IMAGE-"].update(data=image)
    elif event == BUTTON_DISPLAY_MODE:
        orthographic = not orthographic
        selectedItems = values['Subfolders']
        folder = values['Folder']
        filename = f'{folder}/{selectedItems[0]}'
        image = myPlot.getImageFromKml(filename, cn_font, size=size, orthographic=orthographic, plotAll=plotAll)
        window["-IMAGE-"].update(data=image)
    elif event == BUTTON_SHOW_LINES:
        plotAll = not plotAll
        selectedItems = values['Subfolders']
        folder = values['Folder']
        filename = f'{folder}/{selectedItems[0]}'
        image = myPlot.getImageFromKml(filename, cn_font, size=size, orthographic=orthographic, plotAll=plotAll)
        window["-IMAGE-"].update(data=image)
    elif event == BUTTON_SAVE:
        filename = sg.popup_get_file('Choose file (PNG, JPG, GIF) to save to', save_as=True)
        saveElementAsFile(window['-IMAGE-'], filename)

    return subfolders, selectedFiles, selectedFileTimes, orthographic, plotAll
    # elif event == 'Extension':
    #     selectedItem = values['Extension']
    #     subfolders, extList = myUtils.listFoldersFiles(os.path.curdir, selectedItem)
    #     window['Subfolders'].update(values=subfolders)
    # elif event == '→':
    #     selectedItems = values['Subfolders']
    #     if selectedItems:
    #         for item in selectedItems:
    #             if os.path.isfile(item):
    #                 subfolders.remove(item)
    #                 selectedFiles.append(item)
    #                 # selectedFiles.insert(0, item)
    #                 if myUtils.isAudioFile(item) or myUtils.isVideoFile(item):
    #                     fileTime = myUtils.second2Time(myPlot.getVideoTime(item))
    #                     selectedFileTimes.append(f'{fileTime} ☑')
    #                     # selectedFileTimes.insert(0, f'{fileTime}')
    #                 elif myUtils.isImageFile(item):
    #                     w, h = myUtils.getImageSize(item)
    #                     selectedFileTimes.append(f'{w}x{h}')
    #                     # selectedFileTimes.insert(0, f'{w}x{h}')
    #         subfolders = sorted(subfolders)
    #         window['Selected'].update(values=selectedFiles)
    #         window['TimeSize'].update(values=selectedFileTimes)
    #         window['Subfolders'].update(values=subfolders)
    # elif event == '→\n→':
    #     return
    # elif event == '←':
    #     selectedItems = values['Selected']
    #     if selectedItems:
    #         for item in selectedItems:
    #             selectedFiles.remove(item)
    #         # TODO if not same folder skip
    #         subfolders = sorted(subfolders.extend(selectedItems))
    #         window['Selected'].update(values=selectedFiles)
    #         window['Subfolders'].update(values=subfolders)
    # elif event == '←\n←':
    #     return
    # elif event == '↑':
    #     selectedItems = values['Selected']
    #     if selectedItems:
    #         selectedIndex = selectedFiles.index(selectedItems[0])
    #         if selectedIndex > 0:
    #             selectedFiles = myUtils.swapListItems(selectedFiles, selectedIndex, selectedIndex - 1)
    #         selectedIndex = selectedFiles.index(selectedItems[0])
    #         window['Selected'].update(values=selectedFiles, set_to_index=[selectedIndex], scroll_to_index=selectedIndex)
    # elif event == '↑↑':
    #     selectedItems = values['Selected']
    #     if selectedItems:
    #         selectedIndex = selectedFiles.index(selectedItems[0])
    #         if selectedIndex > 0:
    #             selectedFiles.remove(selectedItems[0])
    #             selectedFiles.insert(0, selectedItems[0])
    #         selectedIndex = selectedFiles.index(selectedItems[0])
    #         window['Selected'].update(values=selectedFiles, set_to_index=[selectedIndex], scroll_to_index=selectedIndex)
    # elif event == '↓':
    #     selectedItems = values['Selected']
    #     if selectedItems:
    #         selectedIndex = selectedFiles.index(selectedItems[0])
    #         if selectedIndex < len(selectedFiles) - 1:
    #             selectedFiles = myUtils.swapListItems(selectedFiles, selectedIndex, selectedIndex + 1)
    #         selectedIndex = selectedFiles.index(selectedItems[0])
    #         window['Selected'].update(values=selectedFiles, set_to_index=[selectedIndex], scroll_to_index=selectedIndex)
    # elif event == '↓↓':
    #     selectedItems = values['Selected']
    #     if selectedItems:
    #         selectedIndex = selectedFiles.index(selectedItems[0])
    #         if selectedIndex < len(selectedFiles) - 1:
    #             selectedFiles.remove(selectedItems[0])
    #             selectedFiles.append(selectedItems[0])
    #         selectedIndex = selectedFiles.index(selectedItems[0])
    #         window['Selected'].update(values=selectedFiles, set_to_index=[selectedIndex], scroll_to_index=selectedIndex)
    # elif event == constants.BUTTON1_LABEL:
    #     window.minimize()
    #     cn_font = myPlot.init()

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')
    
if __name__ == "__main__":
    showRunTime("main()")

