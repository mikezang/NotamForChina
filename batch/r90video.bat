@ECHO OFF

IF [%1]==[] goto usage
IF [%2]==[] GOTO usage


ffmpeg -i %1 -vf transpose=1 -metadata:s:v:0 rotate=0 %2


GOTO :eof


:usage
@echo Rotate right 90Åãvideo
@echo Usage: %0 oldFilenameExt newFilenameExt
@echo        oldFilenameExt:	Old video Filename with extension
@echo        newFilenameExt:	New video Filename with extension
exit /B 1


