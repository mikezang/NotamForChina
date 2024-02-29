rem @echo off

IF [%1]==[] goto usage
IF [%2]==[] goto usage


ffmpeg -r 1 -i %1 -vf scale=640:-1 %2.gif
goto eof

:usage
@echo Convert images to gif
@echo Usage: %0 images_filename gif_filename
@echo        images_filename: with wildcard
@echo        gif_filename:	without extension
exit /B 1

:eof
