@echo off

set today=%date%

for /f %%i in ('dir /b /a-d *.kml') do call :process %%i
goto :eof

:process
set x=%1
set ext=%x:*.=%
set year=%x:~0,4%
set month=%x:~5,2%
set day=%x:~8,2%

set filename=%year%/%month%/%day%
if %filename% LSS %today% echo del %x%
rem echo %today%
rem echo %filename%

goto :eof

for /f "delims=_" %%i in ("%x%") do set fileno=%%i
for /f "tokens=1,*delims=-" %%i in ("%x%") do (
  set x1=%%i
  set x2=%%j
)
for /f "tokens=1,* delims=." %%i in ("%x2%") do (
  set dat=%%i
  set ext=%%j
)
set id2=%x1:~-9%
for /f "tokens=1,* delims=_" %%i in ("%x1:~0,-10%") do set id1=%%j
echo filename   %x%
echo ------------------------
echo    Nr. %fileno%
echo    ID1 %id1%
echo    ID2 %id2%
echo    Date    %dat%
echo    Ext.    %ext%
echo ------------------------
echo convert - "%fileno%" -annotate "%id1%" -annotate2 "%id2% -annotate "%dat%"
echo(
echo(
goto :eof
