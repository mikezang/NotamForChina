@ECHO OFF

rem CHCP 65001

IF [%1]==[] goto usage
IF [%2]==[] GOTO usage


rem **********************************************************************
rem create video from png file 
call png2mp4 %1 %2 %1-%2s
rem dir %1-%2s.mp4
rem echo.
echo Create %1-%2s.mp4 (%2 seconds video from %1.png)
rem echo.
rem pause


rem **********************************************************************
rem add countodown
call addCountdown %1-%2s %2
rem dir %1-%2s-countdown.mp4
echo Create %1-%2s-last.mp4 (countdown %2 seconds to %1-%2s.mp4)

goto :EOF


:usage
@echo Create countdown video
@echo Usage: %0 videoName 
@echo   videoName withuut extension
goto :EOF
exit /B 1

:EOF
