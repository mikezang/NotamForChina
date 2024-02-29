@echo off
setlocal enabledelayedexpansion

if "%~1"=="" (
    echo Usage: kml2kmz pathToKmlFiles
    exit /b
)

set "source=%~1"

for /r "%source%" %%f in (*.kml) do (
	set "kmlfile=%%~ff"
    set "folder=%%~dpf"
    set "filename=%%~nf"
    set "kmzfile=!folder!!filename!.kmz"
	set "zipfile=!folder!!filename!.zip"
	set "docfile=!folder!doc.kml"
	set "kmltime=%%~tf"

	call :process_kml "!kmlfile!" "!folder!" "!filename!" "!kmltime!" "!kmzfile!" "!zipfile!" "!docfile!"
)

goto :eof

:process_kml
set "kmlfile=%~1"
set "folder=%~2"
set "filename=%~3"
set "kmltime=%~4"
set "kmzfile=%~5"
set "zipfile=%~6"
set "docfile=%~7"

rem echo folder: %folder%
rem echo filename: %filename%
rem echo kmltime: %kmltime%
rem echo kmzfile: %kmzfile%
rem echo zipfile: %zipfile%
rem echo docfile: %docfile%

if exist "%kmzfile%" (
    for %%g in ("%kmzfile%") do set "kmztime=%%~tg"
	rem echo kmztime: !kmztime!

    if "%kmltime%" gtr "!kmztime!" (
	    copy "%kmlfile%" "%docfile%"
	    7z.exe a "%zipfile%" "%docfile%"
	    move /y "%zipfile%" "%kmzfile%"
	    del "%docfile%"
	)
) else (
    copy "%kmlfile%" "%docfile%"
    7z.exe a "%zipfile%" "%docfile%"
    move /y "%zipfile%" "%kmzfile%"
    del "%docfile%"
)
