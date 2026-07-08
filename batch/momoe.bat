@echo off

IF [%1]==[] goto usage
IF [%2]==[] goto usage

cd \zang\python\Rocket*

call merge %1 %2 rem videos\中国运载火箭发射统计-momoe.mp4

goto :EOF

:usage
@echo Merge momoe music to video
@echo Usage: %0 no
@echo   no merge music list no
goto :EOF
exit /B 1

:EOF
