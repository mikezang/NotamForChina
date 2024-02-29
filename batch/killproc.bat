@echo off

if [%1]==[] goto :Usage 

echo Scanning and Killing Multi-Processes [%1]
rem Set "Processes=firefox.exe"

for %%a in (%1) Do (
    for /f %%b in ('tasklist /NH /FI "imagename eq %%a"') Do (
        if [%%b]==[%%a] (
            echo %%b is running
rem            Color 0C
            echo  Killing %%b ...
            Taskkill /f /im "%%b"
            pause
        ) else (
rem            Color 0F
            echo %%a is not running
            goto :EOF
        )
    )
)

:Usage
echo Usage: killproc proc1[[,proc2], ....]

:EOF
