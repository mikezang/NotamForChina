@echo off

chcp 65001

set t=600
if not "%1" == "" set t=%1

cd C:\zang\python\RocketLaunch
:loop
python notam.py

echo;

pushd .
cd temp
for /f %%i in ('dir /b *.km?') do call :processKML %%i
for /f %%i in ('dir /b notam*.txt') do call :processTXT %%i

popd 
goto :sleep

:processKML
set now=%date%-%time:~0,5%
set now=%now: =0%
set x=%1
set ext=%x:*.=%
set year=%x:~0,4%
set month=%x:~5,2%
set day=%x:~8,2%
set hour=%x:~11,2%
set /a "hour=1%hour%-100"
set /a "hour=%hour%+1"
if %hour% LSS 10 set hour=0%hour%
set minute=%x:~14,2%
set filename=%year%/%month%/%day%-%hour%:%minute%
rem echo %filename%
rem echo %now%
if %filename% LSS %now% echo Delete file %x% & del "%x%" 
exit /b

:processTXT
set now=%date%
set x=%1
set ext=%x:*.=%
set year=%x:~5,4%
set month=%x:~9,2%
set day=%x:~11,2%
set filename=%year%/%month%/%day%
rem echo %filename%
rem echo %now%
if %filename% LSS %now% echo Delete file %x% & del "%x%" 
exit /b

:sleep
rem echo;
pushd .
cd temp
rem dir  *.kml
popd

rem echo;
if "%1" == "" goto :eof 
echo Press Ctrl+C to exit
timeout /t %t%
rem echo;

goto loop

:eof
