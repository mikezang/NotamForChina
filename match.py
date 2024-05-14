from datetime import timedelta
from functools import cache
import os
from sys import argv
from timeit import timeit
# from matplotlib import pyplot

import constants
import myUtils
import myPlot

################################################################################################
def findCombinations(musicList, timeList, index, current_tracks, current_duration, video_duration, results, count, threshold):
    if len(results) == count:
        return
    
    if abs(current_duration - video_duration) <= threshold:  # Adjust this threshold as necessary
        results.append((f'{current_duration:.6f}', current_tracks.copy()))

    for i in range(index, len(musicList)):
        if current_duration + timeList[i] <= video_duration:  # Prune the search space
            current_tracks.append(musicList[i])
            findCombinations(musicList, timeList, i + 1, current_tracks, current_duration + timeList[i], video_duration, results, count, threshold)
            current_tracks.pop()  # Backtrack after exploring this path

################################################################################################
def matchMusics2Video(videoName, favorites=[], threshold=1, index=0, count=100):
    myUtils.setStartTime()
    videoTime = myPlot.getFileDuration(videoName)
    musicList = [os.path.abspath(music) for music in constants.MUSIC_NAME_LIST]
    timeList = constants.MUSIC_TIME_LIST
    favoritesTime = 0
    results = []

    if favorites:
        favorites = [item for item in favorites.split(',')]
        musicList, timeList, favoritesTime = myUtils.removeItemsFromTwoLists(musicList, timeList, favorites)
    else:
        favorites = []

    findCombinations(musicList, timeList, index, favorites, favoritesTime, videoTime, results, count, threshold)
    sortedResults = sorted(results, key=lambda x: x[1], reverse=False)

    if sortedResults:
        lines = ''
        for i, result in enumerate(sortedResults, 1):
            print(f'{i:03}: {result[0]} {[os.path.basename(r) for r in result[1]]}')
            lines += f'{','.join(result[1])}\n'
        listFilename = f'mergelist/{os.path.basename(videoName).replace(".mp4", ".txt")}'
        myUtils.saveTextFile(listFilename, lines, openFile=False)
 
        for i, favorite in enumerate(favorites, 1):
            print(f'favorite{i:02}: {favorite}')
 
    print(f'\n{videoName=}, {videoTime=}, {index=}, {count=}, {threshold=}')
    myUtils.showRunTime()

################################################################################################
def usage():
    print(f'python {argv[0]} videoName favorites threshold index count')
    print('Usage:')
    print('  videoName: Video filename')
    print('  favorites: Favorite music filename list')
    print('  threshold: The threshold in seconds between video and music sum durations')
    print('  index: start index of music files list')
    print('  count: The amount of ouput')

################################################################################################
def parseArgv():
    if len(argv) > 5:
        videoName = argv[1]
        favorites = argv[2]
        threshold = float(argv[3])
        index = int(argv[4])
        count = int(argv[5])
    elif len(argv) > 4:
        videoName = argv[1]
        favorites = argv[2]
        threshold = float(argv[3])
        index = int(argv[4])
        count = 100
    elif len(argv) > 3:
        videoName = argv[1]
        favorites = argv[2]
        threshold = float(argv[3])
        index = 0
        count = 100
    elif len(argv) > 2:
        videoName = argv[1]
        favorites = argv[2]
        threshold = 1
        index = 0
        count = 100
    elif len(argv) > 1:
        videoName = argv[1]
        favorites = []
        threshold = 1
        index = 0
        count = 100
    return videoName, favorites, threshold, index, count

################################################################################################
def main():
    if len(argv) > 1:
        videoName, favorites, threshold, index, count = parseArgv()
        matchMusics2Video(videoName, favorites, threshold, index, count)
    else:
        usage()

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')
    
if __name__ == "__main__":
    showRunTime("main()")
