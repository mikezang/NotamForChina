@ECHO OFF

IF [%1]==[] goto usage

ffmpeg -loglevel quiet -i videos\00.png2mp4-base.mp4 -i %1.png -filter_complex "[0:v][1:v] overlay=0:0" -c:a copy -shortest -t %2 -y %1-%2s.mp4 


rem ffmpeg -r 25 -i %1.jpg -c:v libx264 -vf tpad=stop_mode=clone:stop_duration=2,fps=25 -pix_fmt yuv420p out.mp4

goto :EOF

:usage
@echo Create countdown video
@echo Usage: %0 pngFilename videoTime videoFilename
@echo   pngFilename without extension
@echo   videoTime in seconds
@echo   videoFilename without extension
@exit /B 1

