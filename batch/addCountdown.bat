rem @echo off

rem Add countdown to video
rem %1 video file without extension
rem %2 countdown time

IF [%1]==[] goto usage
IF [%2]==[] GOTO usage


if [%3]==[96] (
  ffmpeg -loglevel quiet -i %1.mp4 -filter_complex "drawtext=fontfile='/WINDOWS/Fonts/Arial.ttf':text='%%{eif\:%2-t\:d}':fontcolor=red:fontsize=96:x=w-tw-40:y=th-40:box=1:boxcolor=orange@0.4:boxborderw=40:enable='between(t,0,%2)'" -c:a copy -c:v libx264 -y %1-countdown.mp4
) else (
  ffmpeg -loglevel quiet -i %1.mp4 -filter_complex "drawtext=fontfile='/WINDOWS/Fonts/Arial.ttf':text='%%{eif\:%2-t\:d}':fontcolor=red:fontsize=24:x=w-tw-10:y=th-10:box=1:boxcolor=orange@0.4:boxborderw=10:enable='between(t,0,%2)'" -c:a copy -c:v libx264 -y %1-countdown.mp4
)

rem ffmpeg -loglevel quiet -i %1.mp4 -filter_complex "drawtext=fontfile='/WINDOWS/Fonts/Arial.ttf':text='%%{eif\:%2-t\:d}':fontcolor=black:fontsize=24:x=w-tw-27:y=th-10:box=1:boxcolor=orange@0.4:boxborderw=10:enable='between(t,0,%2)'" -c:a copy -c:v libx264 -y %1-countdown.mp4

goto :EOF


:usage
@echo Add countdown to video
@echo Usage: %0 videoName time fontSize
@echo   videoName without extension
@echo   time to countdown
@echo   fontSize to countdown
goto :EOF
exit /B 1

:EOF
