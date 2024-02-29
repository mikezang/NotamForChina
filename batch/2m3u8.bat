@ECHO OFF

IF [%1]==[] GOTO usage
IF [%2]==[] GOTO usage
IF [%3]==[] GOTO usage
IF [%4]==[] GOTO usage

SETLOCAL
rem SET dir=c:\zang\videos\%1\%2\%4
rem IF NOT EXIST %dir% md %dir%

cd %dir%

rem IF NOT EXIST %1 GOTO :ERROR1

rem Use ffprobe to get video duration
rem ffprobe -v error -show_entries format^=duration -of default^=noprint_wrappers^=1:nokey^=1 %3
FOR /F "delims=" %%I IN ('ffprobe -v error -show_entries format^=duration -of default^=noprint_wrappers^=1:nokey^=1 %3 2^>^&1') DO SET "duration=%%I"
rem ECHO Duration is: %duration%(s)


SET ts_counts=60
SET TEMP=%duration%
SET VALUE_U=
SET VALUE_L=

rem Get the integer of duration
:LOOP
SET VALUE_U=%VALUE_U%%TEMP:~0,1%
SET TEMP=%TEMP:~1%
IF NOT "%TEMP%"=="" IF NOT "%TEMP:~0,1%"=="." GOTO LOOP

IF NOT "%TEMP%"=="" (
    SET VALUE_L=%TEMP:~1%
)

rem Plus 1 to duration
SET /a "VALUE_U=%VALUE_U%+1"

rem Calculate duration for ts file when limit to 60 ts files 
SET /a "seconds=(%VALUE_U%)/%ts_counts%+1"

rem Split vedio file to ts files in calculated duration
ffmpeg -i %3 -codec: copy -start_number 0 -hls_time %seconds% -hls_list_size 0 -f hls -hls_segment_filename "%4-%%3d.ts" %4.m3u8

ECHO.
ECHO %1 duration is: %duration%(s), about %VALUE_U%(s), splitted into about %ts_counts% ts files, every ts file duration is about: %seconds%(s).

GOTO EOF


:ERROR1
ECHO %1 not found.
GOTO :EOF

:usage
@echo Convert video file to HLS Streaming files (.m3u8 and .ts)
@echo Usage: %0 evn deptCode oldFilenameExt newFilename
@echo        env:		prod or stag
@echo        deptCode:		4 digit number
@echo        oldFilenameExt:	Old video Filename with extension
@echo        newFilename:	New video Filename only
exit /B 1


:EOF
ENDLOCAL

