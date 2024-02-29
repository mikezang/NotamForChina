@echo off

echo %1, %2, %3
IF [%1]==[] goto usage
IF [%2]==[] goto usage
IF [%3]==[] goto 2join
IF [%4]==[] GOTO 3join


:2join
echo Stack %1.mp4 and %2.mp4 on horizon
ffmpeg -loglevel quiet -i %1.mp4 -i %2.mp4 -filter_complex "[0][1]hstack"  %1-hstack.mp4
GOTO :eof

:3join
echo Stack %1.mp4, %2.mp4 and %3.mp4 on horizon
ffmpeg -i %1.mp4 -i %2.mp4 -i %3.mp4 -filter_complex "[0:v][1:v][2:v]hstack=inputs=3[v]" -map "[v]" %1-3hstack.mp4

rem ffplay %1 -loop 0 -af "volume=0.1" -left 0
rem ffmpeg -i %1.mp4 -i %2.mp4 -filter_complex "[0][1]vstack"  images\vstack.mp4
rem ffmpeg -i %1.mp4 -i %2.mp4 -filter_complex "[0][1]vstack" -t 10 images\joined.mp4

GOTO :eof


:usage
@echo Join videos on horizontal stack
@echo Usage: %0 video1 video2 [video3]
@echo        without extension as mp4
exit /B 1
