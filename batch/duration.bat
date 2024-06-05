@ECHO OFF

SETLOCAL
if not exist %1 goto :EOF1

for /F "delims=" %%I in ('ffprobe.exe -v error -show_entries format^=duration -of default^=nw^=1:nk^=1 %1 2^>^&1') do set "duration=%%I"
rem echo Duration is(s): %duration%


SET TEMP=%duration%
SET VALUE_U=
SET VALUE_L=

:LOOP
SET VALUE_U=%VALUE_U%%TEMP:~0,1%
SET TEMP=%TEMP:~1%
IF NOT "%TEMP%"=="" IF NOT "%TEMP:~0,1%"=="." GOTO LOOP

IF NOT "%TEMP%"=="" (
    SET VALUE_L=%TEMP:~1%
)

rem SET /a "VALUE_U=%VALUE_U%+100"
rem SET /a "VALUE_U=%VALUE_U%-100"

echo The %duration%(s) is duration of %1

goto EOF

SET ts_counts=60
SET /a "seconds=(%VALUE_U%)/%ts_counts%+1"
ECHO ts file counts: %ts_counts%
ECHO  Seconds is(s): %seconds%
GOTO EOF
ENDLOCAL

:EOF1
ECHO %1 not found.

:EOF
