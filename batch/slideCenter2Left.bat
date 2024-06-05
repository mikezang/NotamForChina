@echo off

rem ffmpeg -i %1 -vf scale=320:240 output_320x240.png
rem ffmpeg -i %1 -vf scale=-2:720
rem %1 image filename with extension
rem %2 slide time

IF [%1]==[] goto usage
IF [%2]==[] GOTO usage

rem ffmpeg -loglevel quiet -loop 1 -i %1 -filter_complex "split=2[bg][slider];[bg]drawbox=c=black:t=fill[bg];[bg][slider]overlay=x='-w*t':y=0" -t %3 -y %4.mp4

rem ffmpeg -i input.mp4 -loop 1 -i image.jpg -loop 1 -i image2.jpg -loop 1 -i image3.jpg 
 -filter_complex \
   "[1]scale=640:-1,drawbox=color=white:t=15,format=,fade=,rotate=[i1]; 
    [2]scale=,drawbox=,format=,fade=,rotate=[i2]; 
    [3]scale=1080:-1,format=,fade=[i3]; 
    [0][i1]overlay=shortest=1[o1]; 
    [o1][i2]overlay=shortest=1[o2]; 
    [o2][i3]overlay=shortest=1,drawtext=" 
 -b:v 10M finaloutput.mp4

ffmpeg -loop 1 -t 4 -i %1 -loop 1 -t 4 -i %2 -loop 1 -t 4 -i %3 -filter_complex "[0][1]xfade=duration=2:offset=2:transition=slideleft[v];[v][2]xfade=duration=2:offset=4:transition=slideleft" -y %5.mp4

rem ffmpeg -loop 1 -i %1 -loop 1 -i %2 -filter_complex "split=2[bg][slider];[bg]drawbox=c=white:t=fill[bg];[bg][slider]overlay=x='-w*t':y=0" -t %3 -y %4.mp4

goto :EOF

:usage
@echo Create slide from center to left video from image
@echo Usage: %0 imageName time videoName 
@echo   imageName: image filename with extension
@echo   time: time to countdown
@echo   videoName: video filename without extension
goto :EOF
exit /B 1

:EOF

