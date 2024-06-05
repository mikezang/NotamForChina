IF [%1]==[] GOTO usage

ffmpeg -loglevel quiet -sseof -3 -i %1.mp4 -vsync 0 -q:v 31 -update true %1.png

goto EOF

:usage
echo Extract last frame to png file
echo Usage: %0 videoName
echo    videoName: video name without extension
exit /B 1


:EOF
ENDLOCAL
