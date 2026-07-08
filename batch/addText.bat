@echo off
chcp 65001
setlocal EnableDelayedExpansion

:: Usgae: addText input.jpg/input.png

:: a2025年10月23日22时30分文昌长征五号.jpg/.png
set "name=%~n1" 
if "%name:~0,1%" GEQ "0" if "%name:~0,1%" LEQ "9" (
    set "title=%name%"
) else (
    set "title=%name:~1%"
)
set "ext=%~x1"
set "infile=%~1"

:: extract leading part + date
for /f "tokens=1 delims=年" %%a in ("%name%") do set "left=%%a"

:: last 4 chars of left is year
set "year=!left:~-4!"

:: everything before the year is prefix (may be empty)
set "prefix=!left:~0,-4!"

:: month, day, hour and minute
for /f "tokens=2 delims=年月" %%a in ("%name%") do set "month=%%a"
for /f "tokens=2 delims=月日" %%a in ("%name%") do set "day=%%a"
for /f "tokens=2 delims=日时" %%a in ("%name%") do set "hour=%%a"
for /f "tokens=2 delims=时分" %%a in ("%name%") do set "minute=%%a"

:: echo %day:-=%"
:: echo %day%"

if not "%day:-=%"=="%day%" (
    set "base=%prefix%%year%%month%%day%"
) else (
    set "base=%prefix%%year%%month%%day%-%hour%%minute%"
)

echo %base%

:: find available filename
set "outfile=%base%%ext%"
:: if not exist "%outfile%" goto done

:: set i=1
:: :loop
:: set "outfile=%base%-%i%%ext%"
:: if exist "%outfile%" (
::    set /a i+=1
::    goto loop
:: )

:done

:: Option: change font, size, color, etc.
set "file=/zang/python/RocketLaunch/fonts/simkai.ttf"
@REM set "file=/WINDOWS/Fonts/simhei.ttf"
@REM set "file=/WINDOWS/Fonts/simsun.ttc"
set "size=36"
set "color=red"

cd \users\w802479\downloads
:: echo Creating file: %outfile%

ffmpeg  -hide_banner -loglevel error ^
    -i "%infile%" -vf "drawtext=fontfile='%file%':text='%title%':fontcolor='%color%':fontsize='%size%':x=(w-text_w)/2:y=20,format=yuv420p" ^
    -update 1 -frames:v 1 -y "%outfile%"

