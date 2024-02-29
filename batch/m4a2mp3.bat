@echo off

IF [%1]==[] goto usage


ffmpeg -i %1.m4a -ar 44100 -ab 128k %1.mp3

exit /B 1
goto :eof

:usage
@echo Convert m4a to mp3
@echo Usage: %0 m4aFileWithoutExtension
exit /B 1
