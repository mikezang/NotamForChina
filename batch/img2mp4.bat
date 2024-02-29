@ECHO OFF

IF [%1]==[] goto usage
IF [%2]==[] goto usage
IF [%3]==[] goto usage

ffmpeg -loglevel quiet -loop 1 -t %2 -i %1 -c:v libx264 -pix_fmt yuv420p -vf "scale=864:504" -y %3.mp4

rem ffmpeg -loglevel quiet -loop 1 -t %2 -i %1 -c:v libx264 -video_track_timescale 10240 -pix_fmt yuv420p -vf "scale=864:504" -y %3.mp4

rem ffmpeg -loglevel quiet -loop 1 -t %2 -i %1 -c:v libx264 -pix_fmt yuv420p -vf "scale=1920:1080" %3.mp4
rem ffmpeg -loop 1 -framerate 30 -t %2 -i %1 -c:v libx264 -pix_fmt yuv420p -vf "scale=1920:-1" %3.mp4


goto :eof

:usage
@echo Covert image to video
@echo Usage: %0 jpg/pngFilename videoTime videoFilename
@echo   jpg/pngFilename with extension
@echo   videoTime in seconds
@echo   videoFilename without extension
@exit /B 1

