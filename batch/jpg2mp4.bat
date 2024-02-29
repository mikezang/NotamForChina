@ECHO OFF

IF [%1]==[] goto usage


ffmpeg -framerate 1/10 -i %1.jpg -filter_complex "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" -pix_fmt yuv420p -r 30 %1.mp4


goto :eof

:usage
@echo Covert image to video
@echo Usage: %0 jpg/pngFilename videoTime videoFilename
@echo   jpg/pngFilename with extension
@echo   videoTime in seconds
@echo   videoFilename without extension
@exit /B 1