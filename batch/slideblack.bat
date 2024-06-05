rem ffmpeg -loop 1 -i %1.png -loop 1 -i %2.png -filter_complex "[0]split=2[bg][v]; [bg]drawbox=c=black:t=fill[bg]; [bg][v]overlay=x='if(lt(t,10),max(W-w*t,0),max(0-w*(t-10),0-W))'[bg]; [bg][1]overlay=x='if(between(t,10,20),max(W-w*(t-10),0),max(0-w*(t-20),0-W))',drawtext=fontfile='/WINDOWS/Fonts/Arial.ttf':text='%%{eif\:10-t\:d}':fontcolor=red:fontsize=96:x=w-tw-40:y=th-40:box=1:boxcolor=orange@0.4:boxborderw=40:enable='between(t,0,10)'" -c:a copy -c:v libx264 -t 22 -y videos\output.mp4

rem slide image from right to center, wait 10 seconds, then slide from center left
ffmpeg -loop 1 -i %1.png -loop 1 -i %2.png -filter_complex_script slideright2left.txt -t 22 -c:a copy -c:v libx264 -y videos\output.mp4

rem add countdown
rem ffmpeg -i %1.mp4 -filter_complex "drawtext=fontfile='/WINDOWS/Fonts/Arial.ttf':text='%%{eif\:%2-t\:d}':fontcolor=red:fontsize=24:x=w-tw-10:y=th-10:box=1:boxcolor=orange@0.4:boxborderw=10:enable='between(t,0,%2)'" -c:a copy -c:v libx264 -y %1-countdown.mp4

:EOF
