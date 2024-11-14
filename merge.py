from datetime import timedelta
from shutil import move, rmtree
from subprocess import run
from sys import argv
from timeit import timeit
from os import system, chdir, makedirs, path

from myModules import myFile
from myModules import myDate

################################################################################################
def createSlideScriptNew(inputList, index, countdown=10, duration=0, width=864, height=504, fontPath='/WINDOWS/Fonts/Arial.ttf'):
    if index == 0:
        if myFile.isImageFile(inputList[index]):
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
        if myFile.isImageFile(inputList[index]):
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

    if myFile.isImageFile(inputList[index]):
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
    cmd = f'@echo off\nffmpeg -hide_banner -loglevel fatal {myFile.keepOneLineChar()}\n'
    if myFile.isImageFile(inputList[index]):
        if index > 0:
            cmd += f'\t-loop 1 -i "{inputList[index - 1]}" {myFile.keepOneLineChar()}\n'
        cmd += f'\t-loop 1 -i "{inputList[index]}" {myFile.keepOneLineChar()}\n'
    else:
        if index > 0:
            cmd += f'\t-sseof -0.03 -i "{inputList[index - 1]}" {myFile.keepOneLineChar()}\n'
            cmd += f'\t-vframes 1 -c:v png -f image2pipe - | ffmpeg  {myFile.keepOneLineChar()}\n'
            cmd += f'\t-hide_banner -loglevel fatal -i - {myFile.keepOneLineChar()}\n'
        cmd += f'\t-i "{inputList[index]}" {myFile.keepOneLineChar()}\n'
    cmd += f'\t-filter_complex_script script-{index:02}.txt {myFile.keepOneLineChar()}\n'
    cmd += f'\t-t {countdown+duration} -y v{index:02}.mp4\n'
    return cmd

################################################################################################
def createSlideScript(inputList, index, countdown=10, duration=0, width=864, height=504, fontPath='/WINDOWS/Fonts/Arial.ttf'):
    if myFile.isImageFile(inputList[index]):
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
    cmd = f'@echo off\nffmpeg -hide_banner -loglevel fatal {myFile.keepOneLineChar()}\n'
    if myFile.isImageFile(inputList[index]):
        if index > 0:
            cmd += f'\t-framerate 20 -loop 1 -i "{inputList[index - 1]}" {myFile.keepOneLineChar()}\n'
        cmd += f'\t-framerate 20 -loop 1 -i "{inputList[index]}" {myFile.keepOneLineChar()}\n'
    else:
        if index > 0:
            cmd += f'\t-sseof -0.05 -i "{inputList[index - 1]}" {myFile.keepOneLineChar()}\n'
            cmd += f'\t-vframes 1 -c:v png -f image2pipe - | ffmpeg  {myFile.keepOneLineChar()}\n'
            cmd += f'\t-hide_banner -loglevel fatal -i - {myFile.keepOneLineChar()}\n'
        cmd += f'\t-i "{inputList[index]}" {myFile.keepOneLineChar()}\n'
    cmd += f'\t-filter_complex_script script-{index:02}.txt {myFile.keepOneLineChar()}\n'
    cmd += f'\t-t {countdown+duration} -r 20 -y v{index:02}.mp4\n'
    return cmd

################################################################################################
def change2WorkFolder(outputFileInfo):
    system('chcp 65001')
    chdir(outputFileInfo.folderName)
    tmpFolder = f'.tmp_{outputFileInfo.baseName}'
    makedirs(tmpFolder, exist_ok=True)
    chdir(tmpFolder)
    return tmpFolder

def moveFile(inputFileInfo, outputVideoFile, ):
    outputPath = f'{inputFileInfo.absFolder}\\{outputVideoFile}'.replace('\\', '\\\\')
    move(outputVideoFile, outputPath)

def deleteTmpFolder(tmpFolder):
    chdir('../')
    rmtree(tmpFolder)

################################################################################################
def createMusicCommand(inputFileInfo, outputVideoFile, musicFile=None):
    inputPath = f'{inputFileInfo.absFolder}\\{inputFileInfo.baseName}'.replace('\\', '\\\\')
    cmd = '@echo off\n'
    if musicFile:
        cmd += f'ffmpeg -loglevel fatal {myFile.keepOneLineChar()}\n'
        cmd += f'\t-i {musicFile.replace("\\", "\\\\")} {myFile.keepOneLineChar()}\n'
        cmd += f'\t-i {inputPath} {myFile.keepOneLineChar()}\n'
    else:
        cmd += f'ffmpeg -loglevel fatal -f concat -safe 0 -i script-99.txt -f mp3 - | ffmpeg {myFile.keepOneLineChar()}\n'
        cmd += f'\t-loglevel fatal -i - -i {inputPath} {myFile.keepOneLineChar()}\n'
    cmd += f'\t-c copy -map 0:a -map 1:v {myFile.keepOneLineChar()}\n'
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
    inputFileInfo = myFile.parseFileInfo(outputFilename)
    tmpFolder = change2WorkFolder(inputFileInfo)
    inputVideoFile = inputFileInfo.baseName
    outputVideoFile = f'{inputVideoFile.replace('.mp4', '-music.mp4')}'

    script = createMusicScript(musicList)
    myFile.saveTextFile('script-99.txt', script, openFile=False, noSound=True, showMsg=False)
    cmd = createMusicCommand(inputFileInfo, outputVideoFile)
    myFile.saveTextFile('script-99.bat', cmd, openFile=False, noSound=True, showMsg=False)
    msg = '\n'.join([path.basename(m) for m in musicList])
    print(f'Adding\n{msg}\nto {outputVideoFile}...')
    run('script-99.bat')

    moveFile(inputFileInfo, outputVideoFile)
    deleteTmpFolder(tmpFolder)

################################################################################################
def mergeSlideToVideo(inputList, outputFilename, slide=None, countdown=10, width=864, height=504, fontPath='/WINDOWS/Fonts/Arial.ttf'):
    inputList = [path.abspath(image) for image in inputList]
    outputFileInfo = myFile.parseFileInfo(outputFilename)
    tmpFolder = change2WorkFolder(outputFileInfo)
    videoFile = f'{outputFileInfo.baseName}'
    videoText = ''
    msg = ''

    for index, _ in enumerate(inputList):
        if slide or countdown > 0:
            videoText += f'file v{index:02}.mp4\n'
            duration = 0 if myFile.isImageFile(inputList[index]) else int(myFile.getFileDuration(inputList[index]))
            script = createSlideScript(inputList, index, countdown, duration, width, height, fontPath)
            myFile.saveTextFile(f'script-{index:02}.txt', script, False, True, False)
            cmd = createSlideCommand(inputList, index, countdown, duration)
            myFile.saveTextFile(f'script-{index:02}.bat', cmd, False, True, False)
            print(f'Creating {index:02}.mp4 from {path.basename(inputList[index])}...')
            system(f'script-{index:02}.bat')
            msg = videoText
        else:
            videoText += f'file {inputList[index].replace('\\', '\\\\')}\n'
            msg += f'{inputList[index].split('\\')[-1]}\n'

    myFile.saveTextFile('script-99.txt', videoText, False, True, False)
    if slide or countdown > 0:
        cmd = f'@echo off\nffmpeg -loglevel fatal -f concat -safe 0 -i script-99.txt -codec copy -y {videoFile}\n'
    else:
        cmd = f'@echo off\nffmpeg -loglevel fatal -f concat -safe 0 -i script-99.txt -y {videoFile}\n'

    myFile.saveTextFile('script-99.bat', cmd, False, True, False)
    print(f'Merging\n{msg}to {videoFile}...')
    run('script-99.bat')

    moveFile(outputFileInfo, videoFile)
    deleteTmpFolder(tmpFolder)

################################################################################################
def readMusicListFile(filename, lineNo):
    inputList = myFile.readTextFile(filename, True)
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
    myDate.setStartTime()

    if len(argv) <= 1:
        showUsage()
        return
    
    if argv[1].isdigit():
        lineNo = int(argv[1])       # 012
        outputFilename = argv[2]    # outputFilename.mp4
        musicFilename = f'mergelist/{path.basename(outputFilename).replace(".mp4", ".txt")}'

        if not myFile.isTextFile(musicFilename):
            showUsage()
            return
        
        musicList = [path.abspath(image) for image in readMusicListFile(musicFilename, lineNo)]
        mergeMusicToVideo(musicList, outputFilename)
    else:
        inputListFilename = argv[1] # inputList.txt
        
        if not myFile.isTextFile(inputListFilename):
            showUsage()
            return
            
        outputFilename = argv[2]    # outputFilename.mp4
        inputList = myFile.readTextFile(inputListFilename, True)
        inputList, slide, countdown = parseInputFile(inputList)
        mergeSlideToVideo(inputList, outputFilename, slide, countdown)
    myDate.showRunTime()
    myFile.playSound()
    return

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')
    
if __name__ == "__main__":
    showRunTime("main()")

