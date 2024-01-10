from datetime import timedelta
import logging
import time
from timeit import timeit

import myUtils

def createVideoFromPicture():
    return

def addCountdownToVideo():
    # Create 10 seconds pause video from png file
    # ffmpeg -i %1.mp4 -vf tpad=stop_mode=clone:stop_duration=%2 %1-%2s.mp4
    # stream = ffmpeg.input(pngFilename)
    # stream = ffmpeg.filter(stream, '-vf', fps=25, round='up')
    # stream = ffmpeg.output(stream, 'dummy2.mp4')
    # ffmpeg.run(stream)
    return

def concatVideosToOneVideo():
    return

def addMusicToVideo():
    return

def calcLastVideoCountdown():
    return

def main():
    logFilename = f"temp/{time.strftime('%Y%m%d-%H%M%S')}.log"
    myUtils.setLogging(logFilename)
    myLogger = logging.getLogger('main')

    myLogger.info(f'Start: *****************************')

    # myPlot.init(True)

    # myLogger.info(f'Start reading data:')
    # excelFile = "data/ChinaRocketLaunch.xlsx"
    # sheetName = "发射纪录"
    # excelBook = loadXLSX(excelFile, data_only=True, read_only=True)
    # myLogger.info(f'End reading data:')

    fileList = ('01.民营', '02.其他', '03.长征', '04.系列', '05.全部')
    path = 'video/'
    for i, file in enumerate(fileList):
        videoFile1 = f'{path}{file}.mp4'
        pngFile = f'{path}{file}-last.png'

        if i < len(fileList):
            videoFile2 = f'{path}{file}-last-10s.mp4'
            videoFile3 = f'{path}{file}-last-10s-countdown.mp4'
        else:
            lastLength = calcLastVideoCountdown()
            videoFile2 = f'{path}{file}-last-{lastLength}s.mp4'
            videoFile3 = f'{path}{file}-last-{lastLength}s-countdown.mp4'

        createVideoFromPicture(pngFile, videoFile2)
        addCountdownToVideo(videoFile2, videoFile3)

    concatVideosToOneVideo()
    addMusicToVideo()

    myLogger.info(f'End: *******************************')

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')
    
if __name__ == "__main__":
    showRunTime("main()")

