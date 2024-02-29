@ECHO OFF

IF [%1]==[] goto usage
IF [%2]==[] GOTO usage
IF [%3]==[] GOTO usage
IF [%4]==[] GOTO usage

ffmpeg -i %1 -ss %2 -to %3 -c copy %4

GOTO :eof


:usage
@echo Split video file from soecific time to specific time
@echo Usage: %0 oldFilenameExt fromTimeSeconds toTime newFilenameExt
@echo        oldFilenameExt:	Old video Filename with extension
@echo        newFilenameExt:	New video Filename with extension
exit /B 1
