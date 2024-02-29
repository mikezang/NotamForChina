@ECHO OFF

IF [%1]==[] goto usage
IF [%2]==[] GOTO usage
IF [%3]==[] GOTO usage
IF [%4]==[] GOTO usage
IF [%5]==[] GOTO usage


rem SET dir=c:\zang\videos\%1\%2\%4
rem IF NOT EXIST %dir% md %dir%

rem cd %dir%

ffmpeg -i %3 -s 1280x720 -b:v 1000000 %4.%5

GOTO :eof

:usage
@echo Compress video file to 1280x720 resolution and 1000000 video bitrate
@echo Usage: %0 evn deptCode oldFilenameExt newFilename newExt
@echo        env:		prod or stag
@echo        deptCode:		4 digit number
@echo        oldFilenameExt:	Old video Filename with extension
@echo        newFilename:	New video Filename only
@echo        newExt:		New video Filename extension
exit /B 1