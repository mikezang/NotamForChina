from datetime import timedelta
from pathlib import Path
from shutil import move, rmtree
import shutil
from subprocess import run
from sys import argv
from timeit import timeit
from os import system, chdir, makedirs, path, getcwd

from myModules import myFile
from myModules import myDate

MUSIC_PATH = 'music/'
MOMOE_MUSIC_PATH = MUSIC_PATH + 'momoe/'
FONT_PATH = '/zang/python/RocketLaunch/fonts/SimKai.ttf'

################################################################################################
def createSlideScriptNew(inputList, index, countdown=10, duration=0, width=1920, height=1080, fontPath=FONT_PATH):
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

################################################################################################
def createSlideCommandNew(inputList, index, countdown=10, duration=0, filter_complex_script="-/filter_complex"):
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
    cmd += f'\t{filter_complex_script} script-{index:02}.txt {myFile.keepOneLineChar()}\n'
    cmd += f'\t-t {countdown+duration} -y v{index:02}.mp4\n'
    return cmd

################################################################################################
def createSlideScript(inputList, index, countdown=10, duration=0, width=1920, height=1080, fontsize=24, boxsize=10, fontPath=FONT_PATH):
    if myFile.isImageFile(inputList[index]):
        pauseDuration = countdown
        if index == 0:
            script = f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:-1:-1,setsar=1[s0];\n"
            script += f"[s0]split=2[bg][s1];\n"
            script += f"[bg]drawbox=color=black:t=fill[bg];\n"
            script += f"[bg][s1]overlay=x='if(lt(t,{countdown}),"
        else:
            script = f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:-1:-1,setsar=1[s0];\n"
            script += f"[1:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:-1:-1,setsar=1[s1];\n"
            script += f"color=white:{width}x{height}[bg];\n"
            script += f"[bg][s0]overlay=x=0-w*t[bg];\n"
            script += f"[bg][s1]overlay=x='if(lt(t,{countdown}),"
        script += f"max(W-w*t,0),max(-w*(t-{countdown}),-W))'[s3],\n"
    else:
        pauseDuration =  countdown + duration
        if index == 0:
            script = f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:-1:-1,setsar=1[s0];\n"
            script += f"[s0]split=2[bg][s1];\n"
            script += f"[bg]drawbox=color=black:t=fill[bg];\n"
            script += f"[bg][s1]overlay=y='if(lt(t,{pauseDuration}),"
            script += f"max(H-h*t,0),max(-h*(t-{pauseDuration}),-H))'[s2],\n"
            script += f"[s2]tpad=stop_mode=clone:stop_duration={countdown}[s3];\n"
        else:
            script = f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:-1:-1,setsar=1[s0];\n"
            script += f"[1:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:-1:-1,setsar=1[s1];\n"
            script += f"color=white:{width}x{height}[bg];\n"
            script += f"[bg][s0]overlay=y=0-h*t[bg];\n"
            script += f"[bg][s1]overlay=y='if(lt(t,{pauseDuration}),"
            script += f"max(H-h*t,0),max(-h*(t-{pauseDuration}),-H))'[s2],\n"
            script += f"[s2]tpad=stop_mode=clone:stop_duration={pauseDuration}[s3];\n"
    script += f"[s3]drawtext=fontfile='{fontPath}':text='%{{eif\\:{pauseDuration}-t\\:d}}':\n"
    script += f"box=1:boxborderw={boxsize}:boxcolor=orange@0.4:\n"
    script += f"x=w-tw-{boxsize}:y={boxsize}:fontsize={fontsize}:fontcolor=red:enable='between(t,{duration},{pauseDuration})';\n"
    return script

################################################################################################
def ffmpegVersion7():
    import subprocess
    import re
    version = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True).stdout.splitlines()[0]
    version = re.search(r"ffmpeg version (\S+)", version).group(1)
    return version.startswith("n7.")

################################################################################################
def createSlideCommand(inputList, index, filenameMp4, countdown=10, duration=0, fps=20, filter_complex_script="-/filter_complex"):
    cmd = f'@echo off\nffmpeg -hide_banner -loglevel fatal {myFile.keepOneLineChar()}\n'
    if myFile.isImageFile(inputList[index]):
        if index > 0:
            cmd += f'\t-framerate {fps} -loop 1 -i "{inputList[index - 1]}" {myFile.keepOneLineChar()}\n'
        cmd += f'\t-framerate {fps} -loop 1 -i "{inputList[index]}" {myFile.keepOneLineChar()}\n'
    else:
        if index > 0:
            cmd += f'\t-sseof -0.05 -i "{inputList[index - 1]}" {myFile.keepOneLineChar()}\n'
            cmd += f'\t-vframes 1 -c:v png -f image2pipe - | ffmpeg  {myFile.keepOneLineChar()}\n'
            cmd += f'\t-hide_banner -loglevel fatal -i - {myFile.keepOneLineChar()}\n'
        cmd += f'\t-i "{inputList[index]}" {myFile.keepOneLineChar()}\n'
    cmd += f'\t{filter_complex_script} script-{filenameMp4}.txt {myFile.keepOneLineChar()}\n'
    cmd += f'\t-t {countdown+duration} -r {fps} -y {filenameMp4}.mp4\n'
    return cmd

################################################################################################
def change2WorkFolder(outputFileInfo):
    system('chcp 65001')
    if outputFileInfo.folderName:
        chdir(outputFileInfo.folderName)
    tmpFolder = f'.tmp_{outputFileInfo.baseName}'
    makedirs(tmpFolder, exist_ok=True)
    chdir(tmpFolder)
    return tmpFolder

def moveFile(inputFileInfo, outputVideoFile):
    outputPath = f'{inputFileInfo.absFolder}\\{outputVideoFile}'.replace('\\', '\\\\')
    move(outputVideoFile, outputPath)

################################################################################################
def createMusicCommand(inputFileInfo, inputVideoFile, outputVideoFile, musicFile=None):
    inputPath = f'{inputFileInfo.absFolder}\\{inputVideoFile}'.replace('\\', '\\\\')
    cmd = '@echo off\n'
    if musicFile:
        cmd += f'ffmpeg -loglevel fatal {myFile.keepOneLineChar()}\n'
        cmd += f'\t-i {musicFile.replace("\\", "\\\\")} {myFile.keepOneLineChar()}\n'
        cmd += f'\t-i {inputPath} {myFile.keepOneLineChar()}\n'
        cmd += f'\t-c copy -map 0:a -map 1:v {myFile.keepOneLineChar()}\n'
    else:
        cmd += f'ffmpeg -loglevel fatal -f concat -safe 0 -i script-99.txt -c copy temp_music.mp3\n'
        cmd += f'ffmpeg -loglevel fatal -stream_loop -1 -i temp_music.mp3 -i {inputPath} {myFile.keepOneLineChar()}\n'
        cmd += f'\t-shortest {myFile.keepOneLineChar()}\n'
        cmd += f'\t-c:v copy -c:a libmp3lame -b:a 128k {myFile.keepOneLineChar()}\n'
        cmd += f'\t-map 0:a -map 1:v {myFile.keepOneLineChar()}\n'
    cmd += f'\t-y {outputVideoFile}\n'
    return cmd

################################################################################################
def createMusicScript(musicList):
    script = ''
    for line in musicList:
        script += f'file {line.replace("\\", "\\\\")}\n'
    return script

################################################################################################
def mergeMusicToVideo(musicList, outputFilename, suffix="music"):
    inputFileInfo = myFile.parseFileInfo(outputFilename)
    tmpFolder = change2WorkFolder(inputFileInfo)

    if "-" in inputFileInfo.baseName:
        outputVideoFile = inputFileInfo.baseName
        inputVideoFile = outputVideoFile.split("-")[0] + ".mp4"
    else:
        inputVideoFile = inputFileInfo.baseName
        outputVideoFile = inputVideoFile.replace(".mp4", f"-{suffix}.mp4")

    script = createMusicScript(musicList)
    myFile.saveTextFile('script-99.txt', script, openFile=False, noSound=True, showMsg=False)
    cmd = createMusicCommand(inputFileInfo, inputVideoFile, outputVideoFile)
    myFile.saveTextFile('script-99.bat', cmd, openFile=False, noSound=True, showMsg=False)
    msg = '\n'.join([path.basename(m) for m in musicList])
    print(f'Adding\n{msg}\nto {outputVideoFile}...')
    run('script-99.bat')

    moveFile(inputFileInfo, outputVideoFile)

    chdir('../')
    rmtree(tmpFolder)

################################################################################################
def mergeSlideToVideo(inputList, outputFilename, slide=None, countdown=10, fps=20, width=1920, height=1080, fontsize=24, boxsize=10, copyFile=False, mergeFile=True, keepFilename=False, fontPath=FONT_PATH):
    inputList = [path.abspath(image) for image in inputList]
    outputFileInfo = myFile.parseFileInfo(outputFilename)
    tmpFolder = change2WorkFolder(outputFileInfo)
    videoFile = f'{outputFileInfo.baseName}'
    videoText = ''
    msg = ''

    import subprocess
    filter_complex_script = "-/filter_complex" if ffmpegVersion7 else "-filter_complex_script"
    for index, _ in enumerate(inputList):
        if slide or countdown > 0:
            filenameMp4 = inputList[index].split('.')[0].split('\\')[-1] if keepFilename else f'{index:06}'
            videoText += f'file {filenameMp4}.mp4\n'
            duration = 0 if myFile.isImageFile(inputList[index]) else int(myFile.getFileDuration(inputList[index]))
            script = createSlideScript(inputList, index, countdown, duration, width, height, fontsize, boxsize, fontPath)
            myFile.saveTextFile(f'script-{filenameMp4}.txt', script, False, True, False)
            cmd = createSlideCommand(inputList, index, filenameMp4, countdown, duration, fps, filter_complex_script)
            myFile.saveTextFile(f'script-{filenameMp4}.bat', cmd, False, True, False)
            print(f'Creating {filenameMp4}.mp4 from {path.basename(inputList[index])}...')
            msg = videoText

            # system(f'script-{filenameMp4}.bat')
            result = subprocess.run(f'script-{filenameMp4}.bat', capture_output=True, text=True, shell=True)
            if result.stderr:
                print("Return code:", result.returncode)
                print("stdout:", result.stdout)
                print("stderr:", result.stderr)
                raise

            if copyFile:
                print(f'Copy {filenameMp4}.mp4 to ../')
                shutil.copy2(f'{filenameMp4}.mp4', '../')
        else:
            videoText += f'file {inputList[index].replace('\\', '\\\\')}\n'
            msg += f'{inputList[index].split('\\')[-1]}\n'

    if mergeFile:
        scriptName = 'scriptMerge'
        myFile.saveTextFile(f'{scriptName}.txt', videoText, False, True, False)
        # if slide or countdown > 0:
        #     cmd = f'@echo off\nffmpeg -hide_banner -f concat -safe 0 -i {scriptName}.txt -codec copy -y {videoFile}\n'
        # else:
        cmd = f'@echo off\nffmpeg -hide_banner -f concat -safe 0 -i {scriptName}.txt -c copy -y {videoFile}\n'

        myFile.saveTextFile(f'{scriptName}.bat', cmd, False, True, False)
        print(f'Merging\n{msg}to {videoFile}...')
        run(f'{scriptName}.bat')
        moveFile(outputFileInfo, videoFile)

    chdir('../')
    rmtree(tmpFolder)

################################################################################################
def readMusicListFile(filename, lineNo):
    inputList, _ = myFile.readTextFile(filename, True)
    musicList = inputList[lineNo - 1].split(',')
    return musicList

################################################################################################
# the merge list file format
# #slide=           ;this is Not yet implemented
# #countdown=       ;default 10 seconds
# #fps=              ;default 20
# #width=           ;default 1920 pixels
# #height=          ;default 1080 pixels
# #fontsize=        ;default 24, boxsize * 2.4
# #boxsize=         ;default 10, fontsize * 10 / 24
# #copyFile=        ;default False
# #mergeFile=       ;default True
def parseInputFile(inputList):
    inputListNew = []
    slide = None
    countdown = 0
    fps = 20
    width = 1920
    height = 1080
    fontsize = 24
    boxsize = 10
    copyFile = False
    mergeFile = True
    keepFilename = False

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
            elif 'fps=' in lineTrim:
                fps = lineTrim.split('=')[1]
                fps = int(fps) if fps.isdigit() else 20
            elif 'width=' in lineTrim:
                width = lineTrim.split('=')[1]
                width = int(width) if width.isdigit() else 1920
            elif 'height=' in lineTrim:
                height = lineTrim.split('=')[1]
                height = int(height) if height.isdigit() else 1080
            elif 'fontsize=' in lineTrim:
                fontsize = lineTrim.split('=')[1]
                fontsize = int(fontsize) if fontsize.isdigit() else 24
                boxsize = int(fontsize * 10 / 24)
            elif 'boxsize=' in lineTrim:
                boxsize = lineTrim.split('=')[1]
                boxsize = int(boxsize) if boxsize.isdigit() else 10
                fontsize = int(boxsize * 2.4)
            elif 'copyFile=' in lineTrim:
                copyFile = lineTrim.split('=')[1]
                copyFile = True if copyFile in ['True', 'true', 'Yes', 'yes'] else False
            elif 'mergeFile=' in lineTrim:
                mergeFile = lineTrim.split('=')[1]
                mergeFile = True if mergeFile in ['True', 'true', 'Yes', 'yes'] else False
            elif 'keepFilename=' in lineTrim:
                keepFilename = lineTrim.split('=')[1]
                keepFilename = True if keepFilename in ['True', 'true', 'Yes', 'yes'] else False

    return inputListNew, slide, countdown, fps, width, height, fontsize, boxsize, copyFile, mergeFile, keepFilename

################################################################################################
def showUsage():
    print('Merge images/Videos to Video with/without slide and countodown')
    print(f'python {argv[0]} imageList/videoList videoName')
    print('Usage:')
    print('  imageList/videoList: image or video List')
    print('  videoName: Video filename\n')
    print('  List file format:')
    print('     #slide=           ;this is Not yet implemente')
    print('     #countdown=       ;default 10 seconds')
    print('     #fps=             ;default 20')
    print('     #width=           ;default 1920 pixels')
    print('     #height=          ;default 1080 pixels')
    print('     #fontsize=        ;default 24, boxsize * 2.4')
    print('     #boxsize=         ;default 10, fontsize * 10 / 24')
    print('     #copyFile=        ;default False')
    print('     #mergeFile=       ;default True\n')
    print('Add music to Video')
    print(f'python {argv[0]} msuicListIndex videoName')
    print('Usage:')
    print('  msuicListIndex: music list index number')
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
        
        musicList = [path.abspath(MUSIC_PATH + music) if music == '歌唱祖国音乐.mp3' or music == "祝福祖国.mp3" else path.abspath(MOMOE_MUSIC_PATH + music) for music in readMusicListFile(musicFilename, lineNo)]
        if '歌唱祖国音乐' == musicList[0][-10:-4]:
            music = "歌唱祖国音乐"
        elif "祝福祖国" == musicList[0][-8:-4]:
            music = "祝福祖国"
        else:
            music = "music"
        mergeMusicToVideo(musicList, outputFilename, music)
    else:
        inputListFilename = argv[1] # inputList.txt
        
        if not Path(inputListFilename).is_file() and  myFile.isTextFile(inputListFilename):
            showUsage()
            return
            
        outputFilename = argv[2]    # outputFilename.mp4
        print(f'Creating file: {outputFilename}')
        inputList, _ = myFile.readTextFile(inputListFilename, True, False)
        inputList, slide, countdown, fps, width, height, fontsize, boxsize, copyFile, mergeFile, keepFilename = parseInputFile(inputList)
        mergeSlideToVideo(inputList, outputFilename, slide, countdown, fps, width, height, fontsize, boxsize, copyFile, mergeFile, keepFilename)
    myDate.showRunTime()
    myFile.playSound()
    return

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')
    
if __name__ == "__main__":
    showRunTime("main()")

