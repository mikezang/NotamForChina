@echo off
chcp 65001

cd C:\zang\python\RocketLaunch

ffmpeg -f concat -safe 0 -i mergeList/calendar.txt -vf "fps=1,scale=3356:2372,drawtext=fontfile='/zang/python/RocketLaunch/fonts/simkai.ttf':text='%%{eif\:5-mod(n\,5)\:d}':x=w-tw-40:y=40:fontsize=96:fontcolor=red:box=1:boxcolor=orange@0.4:boxborderw=40" -c:v libx264 -crf 28 -preset veryslow -pix_fmt yuv420p videos/calendar.mp4
