@echo off

rem ffmpeg -i %1 -vf scale=320:240 output_320x240.png
rem ffmpeg -i %1 -vf scale=-2:720
rem %1 image filename with extension
rem %2 slide time

IF [%1]==[] goto usage
IF [%2]==[] GOTO usage

ffmpeg -loglevel quiet -loop 1 -i %1 -filter_complex "split=2[bg][slider];[bg]drawbox=c=white:t=fill[bg];[bg][slider]overlay=x='max(W-w*t,0)':y=0" -t %2 -y %3.mp4

goto :EOF

:usage
@echo Create slide from left to center video from image
@echo Usage: %0 imageName time videoName 
@echo   imageName: image filename with extension
@echo   time: time to countdown
@echo   videoName: video filename without extension
goto :EOF
exit /B 1

:EOF

