@ECHO OFF

IF [%1]==[] goto usage
IF [%2]==[] GOTO usage
IF [%3]==[] GOTO usage

ffmpeg -i %1 -ss %2 -c copy %3

GOTO :eof


:usage
@echo Split video file from soecific time
@echo Usage: %0 oldFilenameExt fromTimeSeconds newFilenameExt
@echo        oldFilenameExt:	Old video Filename with extension
@echo        newFilenameExt:	New video Filename with extension
exit /B 1
