@echo off

ffmpeg -i %1.png -vf scale=1920:-1 -frames:v 1 -update 1 -y %1-1920.png
