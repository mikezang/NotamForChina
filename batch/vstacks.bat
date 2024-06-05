@echo off

IF [%1]==[] goto usage
IF [%2]==[] GOTO usage

cd \zang\python\Rocket*

ffmpeg -loglevel fatal -i %1 -i %2 -filter_complex "[0][1]vstack"  %3

rem ffplay %1 -loop 0 -af "volume=0.1" -left 0
rem ffmpeg -i %1.mp4 -i %2.mp4 -filter_complex "[0][1]vstack"  images\vstack.mp4
rem ffmpeg -i %1.mp4 -i %2.mp4 -filter_complex "[0][1]vstack" -t 10 images\joined.mp4


goto :EOF

:usage
@echo Merge two videos in verticle stacks
@echo Usage: %0 topVideoName BottomVideName 
@echo   topVideoName without extension
@echo   BottomVideName without extension
goto :EOF
exit /B 1

:EOF


