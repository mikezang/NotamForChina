from datetime import timedelta
import shutil
import subprocess
from sys import argv
from timeit import timeit
import PySimpleGUI as sg
import os

import myUtils
import myPlot

################################################################################################
def createSlideScriptNew(inputList, index, countdown=10, duration=0, width=864, height=504, fontPath='/WINDOWS/Fonts/Arial.ttf'):
    if index == 0:
        if myUtils.isImageFile(inputList[index]):
            pauseDuration = countdown
            script = f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:-1:-1,setsar=1[s0];\n"
            script += "[s0]split=2[bg][s1];\n"
            script += "[bg]drawbox=color=black:t=fill[bg];\n"
            script += f"[bg][s1]overlay=x='if(between(t,0,{countdown}),"
            script += f"max(W-w*t,0),max(0-w*(t-{countdown}),0-W))'[s3],\n"
        else:
            pauseDuration =  countdown + duration
            script = f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:-1:-1,setsar=1[s0];\n"
            script += "[s0]split=2[bg][s1];\n"
            script += f"[bg]drawbox=color=black:t=fill[bg];\n"
            script += f"[bg][s1]overlay=y='if(between(t,0,{pauseDuration}),"
            script += f"max(H-h*t,0),max(0-h*(t-{pauseDuration}),0-H))'[s2],\n"
            script += f"[s2]tpad=stop_mode=clone:stop_duration={countdown}[s3];\n"
    else:
        if myUtils.isImageFile(inputList[index]):
            pauseDuration = countdown
            script = f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:-1:-1,setsar=1[s0];\n"
            script += f"[1:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:-1:-1,setsar=1[s1];\n"
            script += f"color=white:{width}x{height}[bg];\n"
            script += f"[bg][s0]overlay=x=0-w*t[bg];\n"
            script += f"[bg][s1]overlay=x='if(between(t,0,{countdown}),"
            script += f"max(W-w*t,0),max(0-w*(t-{countdown}),0-W))'[s3],\n"
        else:
            pauseDuration =  countdown + duration
            script = f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:-1:-1,setsar=1[s0];\n"
            script += f"[1:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:-1:-1,setsar=1[s1];\n"
            script += f"color=white:{width}x{height}[bg];\n"
            script += f"[bg][s0]overlay=y=0-h*t[bg];\n"
            script += f"[bg][s1]overlay=y='if(between(t,0,{pauseDuration}),"
            script += f"max(H-h*t,0),max(0-h*(t-{pauseDuration}),0-H))'[s2],\n"
            script += f"[s2]tpad=stop_mode=clone:stop_duration={pauseDuration}[s3];\n"
    script += f"[s3]drawtext=fontfile='{fontPath}':text='%{{eif\\:{pauseDuration}-t\\:d}}':\n"
    script += f"box=1:boxborderw=10:boxcolor=orange@0.4:\n"
    script += f"x=w-tw-10:y=10:fontsize=24:fontcolor=red:enable='between(t,{duration},{pauseDuration})';\n"
    return script

    if myUtils.isImageFile(inputList[index]):
        pauseDuration = countdown
        if index == 0:
            script = f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:-1:-1,setsar=1[s0];\n"
            script += "[s0]split=2[bg][s1];\n"
            script += "[bg]drawbox=color=black:t=fill[bg];\n"
            script += f"[bg][s1]overlay=x='if(between(t,0,{countdown}),"
        else:
            script = f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:-1:-1,setsar=1[s0];\n"
            script += f"[1:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:-1:-1,setsar=1[s1];\n"
            script += f"color=white:{width}x{height}[bg];\n"
            script += f"[bg][s0]overlay=x=0-w*t[bg];\n"
            script += f"[bg][s1]overlay=x='if(between(t,0,{countdown}),"
        script += f"max(W-w*t,0),max(0-w*(t-{countdown}),0-W))'[s3],\n"
    else:
        pauseDuration =  countdown + duration
        if index == 0:
            script = f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:-1:-1,setsar=1[s0];\n"
            script += "[s0]split=2[bg][s1];\n"
            script += f"[bg]drawbox=color=black:t=fill[bg];\n"
            script += f"[bg][s1]overlay=y='if(between(t,0,{pauseDuration}),"
            script += f"max(H-h*t,0),max(0-h*(t-{pauseDuration}),0-H))'[s2],\n"
            script += f"[s2]tpad=stop_mode=clone:stop_duration={countdown}[s3];\n"
        else:
            script = f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:-1:-1,setsar=1[s0];\n"
            script += f"[1:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:-1:-1,setsar=1[s1];\n"
            script += f"color=white:{width}x{height}[bg];\n"
            script += f"[bg][s0]overlay=y=0-h*t[bg];\n"
            script += f"[bg][s1]overlay=y='if(between(t,0,{pauseDuration}),"
            script += f"max(H-h*t,0),max(0-h*(t-{pauseDuration}),0-H))'[s2],\n"
            script += f"[s2]tpad=stop_mode=clone:stop_duration={pauseDuration}[s3];\n"
    script += f"[s3]drawtext=fontfile='{fontPath}':text='%{{eif\\:{pauseDuration}-t\\:d}}':\n"
    script += f"box=1:boxborderw=10:boxcolor=orange@0.4:\n"
    script += f"x=w-tw-10:y=10:fontsize=24:fontcolor=red:enable='between(t,{duration},{pauseDuration})';\n"
    return script

################################################################################################
def createSlideCommandNew(inputList, index, countdown=10, duration=0):
    cmd = f'@echo off\nffmpeg -hide_banner -loglevel fatal {myUtils.keepOneLineChar()}\n'
    if myUtils.isImageFile(inputList[index]):
        if index > 0:
            cmd += f'\t-loop 1 -i "{inputList[index - 1]}" {myUtils.keepOneLineChar()}\n'
        cmd += f'\t-loop 1 -i "{inputList[index]}" {myUtils.keepOneLineChar()}\n'
    else:
        if index > 0:
            cmd += f'\t-sseof -0.03 -i "{inputList[index - 1]}" {myUtils.keepOneLineChar()}\n'
            cmd += f'\t-vframes 1 -c:v png -f image2pipe - | ffmpeg  {myUtils.keepOneLineChar()}\n'
            cmd += f'\t-hide_banner -loglevel fatal -i - {myUtils.keepOneLineChar()}\n'
        cmd += f'\t-i "{inputList[index]}" {myUtils.keepOneLineChar()}\n'
    cmd += f'\t-filter_complex_script script-{index:02}.txt {myUtils.keepOneLineChar()}\n'
    cmd += f'\t-t {countdown+duration} -y v{index:02}.mp4\n'
    return cmd

################################################################################################
def createSlideScript(inputList, index, countdown=10, duration=0, width=864, height=504, fontPath='/WINDOWS/Fonts/Arial.ttf'):
    if myUtils.isImageFile(inputList[index]):
        pauseDuration = countdown
        if index == 0:
            script = f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:-1:-1,setsar=1[s0];\n"
            script += f"[s0]split=2[bg][s1];\n"
            script += f"[bg]drawbox=color=black:t=fill[bg];\n"
            script += f"[bg][s1]overlay=x='if(between(t,0,{countdown}),"
        else:
            script = f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:-1:-1,setsar=1[s0];\n"
            script += f"[1:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:-1:-1,setsar=1[s1];\n"
            script += f"color=white:{width}x{height}[bg];\n"
            script += f"[bg][s0]overlay=x=0-w*t[bg];\n"
            script += f"[bg][s1]overlay=x='if(between(t,0,{countdown}),"
        script += f"max(W-w*t,0),max(0-w*(t-{countdown}),0-W))'[s3],\n"
    else:
        pauseDuration =  countdown + duration
        if index == 0:
            script = f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:-1:-1,setsar=1[s0];\n"
            script += f"[s0]split=2[bg][s1];\n"
            script += f"[bg]drawbox=color=black:t=fill[bg];\n"
            script += f"[bg][s1]overlay=y='if(between(t,0,{pauseDuration}),"
            script += f"max(H-h*t,0),max(0-h*(t-{pauseDuration}),0-H))'[s2],\n"
            script += f"[s2]tpad=stop_mode=clone:stop_duration={countdown}[s3];\n"
        else:
            script = f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:-1:-1,setsar=1[s0];\n"
            script += f"[1:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:-1:-1,setsar=1[s1];\n"
            script += f"color=white:{width}x{height}[bg];\n"
            script += f"[bg][s0]overlay=y=0-h*t[bg];\n"
            script += f"[bg][s1]overlay=y='if(between(t,0,{pauseDuration}),"
            script += f"max(H-h*t,0),max(0-h*(t-{pauseDuration}),0-H))'[s2],\n"
            script += f"[s2]tpad=stop_mode=clone:stop_duration={pauseDuration}[s3];\n"
    script += f"[s3]drawtext=fontfile='{fontPath}':text='%{{eif\\:{pauseDuration}-t\\:d}}':\n"
    script += f"box=1:boxborderw=10:boxcolor=orange@0.4:\n"
    script += f"x=w-tw-10:y=10:fontsize=24:fontcolor=red:enable='between(t,{duration},{pauseDuration})';\n"
    return script

################################################################################################
def createSlideCommand(inputList, index, countdown=10, duration=0):
    cmd = f'@echo off\nffmpeg -hide_banner -loglevel fatal {myUtils.keepOneLineChar()}\n'
    if myUtils.isImageFile(inputList[index]):
        if index > 0:
            cmd += f'\t-framerate 20 -loop 1 -i "{inputList[index - 1]}" {myUtils.keepOneLineChar()}\n'
        cmd += f'\t-framerate 20 -loop 1 -i "{inputList[index]}" {myUtils.keepOneLineChar()}\n'
    else:
        if index > 0:
            cmd += f'\t-sseof -0.05 -i "{inputList[index - 1]}" {myUtils.keepOneLineChar()}\n'
            cmd += f'\t-vframes 1 -c:v png -f image2pipe - | ffmpeg  {myUtils.keepOneLineChar()}\n'
            cmd += f'\t-hide_banner -loglevel fatal -i - {myUtils.keepOneLineChar()}\n'
        cmd += f'\t-i "{inputList[index]}" {myUtils.keepOneLineChar()}\n'
    cmd += f'\t-filter_complex_script script-{index:02}.txt {myUtils.keepOneLineChar()}\n'
    cmd += f'\t-t {countdown+duration} -r 20 -y v{index:02}.mp4\n'
    return cmd

################################################################################################
def change2WorkFolder(outputFileInfo):
    os.system('chcp 65001')
    os.chdir(outputFileInfo.folderName)
    tmpFolder = f'.tmp_{outputFileInfo.baseName}'
    os.makedirs(tmpFolder, exist_ok=True)
    os.chdir(tmpFolder)
    return tmpFolder

def moveFile(inputFileInfo, outputVideoFile, ):
    outputPath = f'{inputFileInfo.absFolder}\\{outputVideoFile}'.replace('\\', '\\\\')
    shutil.move(outputVideoFile, outputPath)

def deleteTmpFolder(tmpFolder):
    os.chdir('../')
    shutil.rmtree(tmpFolder)

################################################################################################
def createMusicCommand(inputFileInfo, outputVideoFile, musicFile=None):
    inputPath = f'{inputFileInfo.absFolder}\\{inputFileInfo.baseName}'.replace('\\', '\\\\')
    cmd = '@echo off\n'
    if musicFile:
        cmd += f'ffmpeg -loglevel fatal {myUtils.keepOneLineChar()}\n'
        cmd += f'\t-i {musicFile.replace("\\", "\\\\")} {myUtils.keepOneLineChar()}\n'
        cmd += f'\t-i {inputPath} {myUtils.keepOneLineChar()}\n'
    else:
        cmd += f'ffmpeg -loglevel fatal -f concat -safe 0 -i script-99.txt -f mp3 - | ffmpeg {myUtils.keepOneLineChar()}\n'
        cmd += f'\t-loglevel fatal -i - -i {inputPath} {myUtils.keepOneLineChar()}\n'
    cmd += f'\t-c copy -map 0:a -map 1:v {myUtils.keepOneLineChar()}\n'
    cmd += f'\t-y {outputVideoFile}\n'
    return cmd

################################################################################################
def createMusicScript(musicList):
    script = ''
    for line in musicList:
        script += f'file {line.replace("\\", "\\\\")}\n'
    return script

################################################################################################
def mergeMusicToVideo(musicList, outputFilename):
    inputFileInfo = myUtils.parseFileInfo(outputFilename)
    tmpFolder = change2WorkFolder(inputFileInfo)
    inputVideoFile = inputFileInfo.baseName
    outputVideoFile = f'{inputVideoFile.replace('.mp4', '-music.mp4')}'

    # if len(musicList) == 1:
    #     cmd = createMusicCommand(inputFileInfo, outputVideoFile, musicList[0])
    #     myUtils.saveTextFile('script-99.bat', cmd, openFile=False, noSound=True, showMsg=False)
    # else:
    script = createMusicScript(musicList)
    myUtils.saveTextFile('script-99.txt', script, openFile=False, noSound=True, showMsg=False)
    cmd = createMusicCommand(inputFileInfo, outputVideoFile)
    myUtils.saveTextFile('script-99.bat', cmd, openFile=False, noSound=True, showMsg=False)
    msg = '\n'.join([os.path.basename(m) for m in musicList])
    print(f'Adding\n{msg}\nto {outputVideoFile}...')
    subprocess.run('script-99.bat')

    moveFile(inputFileInfo, outputVideoFile)
    deleteTmpFolder(tmpFolder)

################################################################################################
def mergeSlideToVideo(inputList, outputFilename, slide=None, countdown=10, width=864, height=504, fontPath='/WINDOWS/Fonts/Arial.ttf'):
    # myUtils.setStartTime()
    inputList = [os.path.abspath(image) for image in inputList]
    outputFileInfo = myUtils.parseFileInfo(outputFilename)
    tmpFolder = change2WorkFolder(outputFileInfo)
    videoFile = f'{outputFileInfo.baseName}'
    videoText = ''
    msg = ''

    for index, _ in enumerate(inputList):
        if slide or countdown > 0:
            videoText += f'file v{index:02}.mp4\n'
            duration = 0 if myUtils.isImageFile(inputList[index]) else int(myPlot.getFileDuration(inputList[index]))
            script = createSlideScript(inputList, index, countdown, duration, width, height, fontPath)
            myUtils.saveTextFile(f'script-{index:02}.txt', script, False, True, False)
            cmd = createSlideCommand(inputList, index, countdown, duration)
            myUtils.saveTextFile(f'script-{index:02}.bat', cmd, False, True, False)
            print(f'Creating {index:02}.mp4 from {os.path.basename(inputList[index])}...')
            os.system(f'script-{index:02}.bat')
            msg = videoText
        else:
            videoText += f'file {inputList[index].replace('\\', '\\\\')}\n'
            msg += f'{inputList[index].split('\\')[-1]}\n'

    myUtils.saveTextFile('script-99.txt', videoText, False, True, False)
    if slide or countdown > 0:
        cmd = f'@echo off\nffmpeg -loglevel fatal -f concat -safe 0 -i script-99.txt -codec copy -y {videoFile}\n'
    else:
        cmd = f'@echo off\nffmpeg -loglevel fatal -f concat -safe 0 -i script-99.txt -y {videoFile}\n'

    myUtils.saveTextFile('script-99.bat', cmd, False, True, False)
    print(f'Merging\n{msg}to {videoFile}...')
    subprocess.run('script-99.bat')

    moveFile(outputFileInfo, videoFile)
    deleteTmpFolder(tmpFolder)
    # myUtils.showRunTime()
    # myUtils.playSound()

################################################################################################
def readMusicListFile(filename, lineNo):
    inputList = myUtils.readTextFile(filename, True)
    musicList = inputList[lineNo - 1].split(',')
    return musicList

################################################################################################
def parseInputFile(inputList):
    inputListNew = []
    slide = None
    countdown = 10

    for line in inputList:
        if line[0] != '#':
            inputListNew.append(line)
        else:
            lineTrim = line.strip()
            if 'slide=' in lineTrim:
                slide = lineTrim.split('=')[1] 
            elif 'countdown=' in lineTrim:
                countdown = lineTrim.split('=')[1]
                countdown = int(countdown) if countdown.isdigit() else 0
    return inputListNew, slide, countdown

################################################################################################
def showUsage():
    print('Merge images/Videos to Video with/without slide and countodown')
    print(f'python {argv[0]} imageList/videoList videoName')
    print('Usage:')
    print('  imageList/videoList: image or video List')
    print('  videoName: Video filename\n')
    print('Add music to Video')
    print(f'python {argv[0]} msuicListIndex videoName')
    print('Usage:')
    print('  music list index number')
    print('  videoName: Video filename')

################################################################################################
def main():
    myUtils.setStartTime()

    if len(argv) <= 1:
        showUsage()
        return
    
    if argv[1].isdigit():
        lineNo = int(argv[1])       # 012
        outputFilename = argv[2]    # outputFilename.mp4
        musicFilename = f'mergelist/{os.path.basename(outputFilename).replace(".mp4", ".txt")}'

        if not myUtils.isTextFile(musicFilename):
            showUsage()
            return
        
        musicList = [os.path.abspath(image) for image in readMusicListFile(musicFilename, lineNo)]
        mergeMusicToVideo(musicList, outputFilename)
    else:
        inputListFilename = argv[1] # inputList.txt
        
        if not myUtils.isTextFile(inputListFilename):
            showUsage()
            return
            
        outputFilename = argv[2]    # outputFilename.mp4
        inputList = myUtils.readTextFile(inputListFilename, True)
        inputList, slide, countdown = parseInputFile(inputList)
        mergeSlideToVideo(inputList, outputFilename, slide, countdown)
    myUtils.showRunTime()
    myUtils.playSound()
    return

    window, subfolders = getWindow()
    myPlot.moveWindow(window, y=0)
    selectedFiles = []
    selectedFileTimes = []

    while True:
        event, values = window.read(timeout=0)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        subfolders, selectedFiles, selectedFileTimes = handleEvents(window, event, values, subfolders, selectedFiles, selectedFileTimes)
        window.Normal()
    window.close()

################################################################################################
def getWindow():
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

################################################################################################
def getButton():
    button = [
        sg.Button('Start Task', font=("Helvetica", 14)), 
        # sg.Button('Button2', font=("Helvetica", 14)), 
        # sg.Push(), 
        # sg.Button('Show Chart Pictures', font=("Helvetica", 14)), 
        # sg.Button('Play Bar Chart Race Videos', font=("Helvetica", 14)), 
        sg.Push(), 
        sg.Button('Exit', font=("Helvetica", 14))
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
def handleEvents(window, event, values, subfolders: list, selectedFiles: list, selectedFileTimes: list):
    # font = ("Courier New", 11)
    # entry = window['Main'].Widget
    # input_size = entry.winfo_width() // sg.Text.char_width_in_pixels(font)
    
    if event == 'Subfolders':
        selectedItems = values['Subfolders']
        if len(selectedItems) == 1:
            if os.path.isdir(selectedItems[0]):
                curPath = selectedItems[0]
                selectedItem = values['Extension']
                subfolders, extList = myUtils.listFoldersFiles(curPath, selectedItem)
                window['Subfolders'].update(values=subfolders)
                window['Extension'].update(values=extList, value='*.*')
                window['Folder'].update(os.path.abspath(curPath))
            else:
                if selectedItems[0].endswith('.txt'):
                    lines = myUtils.readTextFile(selectedItems[0])
                    selectedFiles.extend(lines)
                    window['Selected'].update(values=selectedFiles)
    elif event == 'Extension':
        selectedItem = values['Extension']
        subfolders, extList = myUtils.listFoldersFiles(os.path.curdir, selectedItem)
        window['Subfolders'].update(values=subfolders)
    elif event == '→':
        selectedItems = values['Subfolders']
        if selectedItems:
            for item in selectedItems:
                if os.path.isfile(item):
                    subfolders.remove(item)
                    selectedFiles.append(item)
                    # selectedFiles.insert(0, item)
                    if myUtils.isAudioFile(item) or myUtils.isVideoFile(item):
                        fileTime = myUtils.second2Time(myPlot.getVideoTime(item))
                        selectedFileTimes.append(f'{fileTime} ☑')
                        # selectedFileTimes.insert(0, f'{fileTime}')
                    elif myUtils.isImageFile(item):
                        w, h = myUtils.getImageSize(item)
                        selectedFileTimes.append(f'{w}x{h}')
                        # selectedFileTimes.insert(0, f'{w}x{h}')
            subfolders = sorted(subfolders)
            window['Selected'].update(values=selectedFiles)
            window['TimeSize'].update(values=selectedFileTimes)
            window['Subfolders'].update(values=subfolders)
    elif event == '→\n→':
        return
    elif event == '←':
        selectedItems = values['Selected']
        if selectedItems:
            for item in selectedItems:
                selectedFiles.remove(item)
            # TODO if not same folder skip
            subfolders = sorted(subfolders.extend(selectedItems))
            window['Selected'].update(values=selectedFiles)
            window['Subfolders'].update(values=subfolders)
    elif event == '←\n←':
        return
    elif event == '↑':
        selectedItems = values['Selected']
        if selectedItems:
            selectedIndex = selectedFiles.index(selectedItems[0])
            if selectedIndex > 0:
                selectedFiles = myUtils.swapListItems(selectedFiles, selectedIndex, selectedIndex - 1)
            selectedIndex = selectedFiles.index(selectedItems[0])
            window['Selected'].update(values=selectedFiles, set_to_index=[selectedIndex], scroll_to_index=selectedIndex)
    elif event == '↑↑':
        selectedItems = values['Selected']
        if selectedItems:
            selectedIndex = selectedFiles.index(selectedItems[0])
            if selectedIndex > 0:
                selectedFiles.remove(selectedItems[0])
                selectedFiles.insert(0, selectedItems[0])
            selectedIndex = selectedFiles.index(selectedItems[0])
            window['Selected'].update(values=selectedFiles, set_to_index=[selectedIndex], scroll_to_index=selectedIndex)
    elif event == '↓':
        selectedItems = values['Selected']
        if selectedItems:
            selectedIndex = selectedFiles.index(selectedItems[0])
            if selectedIndex < len(selectedFiles) - 1:
                selectedFiles = myUtils.swapListItems(selectedFiles, selectedIndex, selectedIndex + 1)
            selectedIndex = selectedFiles.index(selectedItems[0])
            window['Selected'].update(values=selectedFiles, set_to_index=[selectedIndex], scroll_to_index=selectedIndex)
    elif event == '↓↓':
        selectedItems = values['Selected']
        if selectedItems:
            selectedIndex = selectedFiles.index(selectedItems[0])
            if selectedIndex < len(selectedFiles) - 1:
                selectedFiles.remove(selectedItems[0])
                selectedFiles.append(selectedItems[0])
            selectedIndex = selectedFiles.index(selectedItems[0])
            window['Selected'].update(values=selectedFiles, set_to_index=[selectedIndex], scroll_to_index=selectedIndex)
    # elif event == constants.BUTTON1_LABEL:
    #     window.minimize()
    #     cn_font = myPlot.init()
    # elif event == constants.BUTTON2_LABEL:
    #     window.minimize()
    #     cn_font = myPlot.init(True)

    return subfolders, selectedFiles, selectedFileTimes

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')
    
if __name__ == "__main__":
    showRunTime("main()")

