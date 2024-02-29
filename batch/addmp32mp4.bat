@echo off

IF [%1]==[] goto usage
IF [%2]==[] GOTO usage
set output=%2-music.mp4
IF not [%3]==[] set output=%3.mp4

ffmpeg -loglevel quiet -i %2.mp4 -i %1.mp3 -c copy -map 0:v -map 1:a -y %output%

rem ffmpeg -i %1.mp4 -i music/11-Thisismytrial.mp3 -c copy  -map 0:v -map 1:a -y %1-music.mp4

rem ffmpeg -i %2.mp4 -i music/%1.mp3 -c copy -map 0:v -map 1:a -y %2(%1).mp4

rem ffmpeg -i %2.mp4 -i %1.mp3 -c copy -shortest -map 0:v -map 1:a -y %2-music.mp4

exit /B 1
goto :eof

:usage
@echo Add mp3 to mp4
@echo Usage: %0 musicFile videoFile
@echo        musicFile:	without extension
@echo        videoFile:	without extension
exit /B 1
