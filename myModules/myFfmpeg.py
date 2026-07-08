import subprocess
import ffmpeg
from ffmpeg import probe

from myModules import myFile

def trimFrames(inputFile, startFrame, endFrame, outputFile):
    inputVideo = ffmpeg.input(inputFile)
    outputVideo = ffmpeg.output(inputVideo.trim(start_frame=startFrame, end_frame=endFrame), outputFile)
    ffmpeg.run(outputVideo)

# TODO: resume plot the newest part for shorter time
# remove last count(removeFramesCount) of frames from old mp4 file
# plot last count(plotFramesCount) of frames newPart mp4 file
# merge newPart to old as new mp4 file
# ffmpeg -i IN -c copy -bsf:v noise=drop=between(n\,20\,30) OUT
def testTrimMergeVideo(oldVideo, oldFile, newFile):
    oldFrames, _ = myFile.readTextFile(oldFile)
    newFrames, _ = myFile.readTextFile(newFile)
    oldList, newList = diffFrames(oldFrames, newFrames)
    trimFrames(oldVideo, oldList[1] - oldList[2], oldList[1], 
                           oldVideo.replace('.mp4', f'-trim{oldList[2]}.mp4'))

################################################################################################
def diffFrames(oldFramesList: list, newFramesList: list):
    oldDiffList = sorted(list(set(oldFramesList) - set(newFramesList)))
    newDiffList = sorted(list(set(newFramesList) - set(oldFramesList)))
    oldFrames = [oldDiffList]
    newFrames = [newDiffList]
    oldFrames.append(len(oldFramesList))
    newFrames.append(len(newFramesList))
    oldFrames.append(len(oldDiffList))
    newFrames.append(len(newDiffList))
    return oldFrames, newFrames 
