@echo off

SETLOCAL

IF [%1]==[] GOTO usage
IF [%2]==[] GOTO usage

set file=%1
FOR %%i IN ("%file%") DO (
    SET filedrive=%%~di
    SET filepath=%%~pi
    SET filename=%%~ni
    SET fileextension=%%~xi
)


ffmpeg -i %1 -c copy -map 0 -segment_time %2 -f segment %filename%-%%03d%fileextension%

GOTO EOF


:usage
@echo Split video file to multiple files
@echo Usage: %0 filenameExt sengmentLength
@echo        filenameExt:	    Video Filename with extension
@echo        sengmentLength:	Split file segment length
exit /B 1


:EOF
ENDLOCAL
