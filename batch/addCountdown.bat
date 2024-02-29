rem create video
ffmpeg -loglevel quiet -i %1.mp4 -filter_complex "drawtext=fontfile='/WINDOWS/Fonts/Arial.ttf':text='%%{eif\:%2-t\:d}':fontcolor=black:fontsize=24:x=w-tw-10:y=th-10:box=1:boxcolor=orange@0.4:boxborderw=10:enable='between(t,0,%2)'" -c:a copy -c:v libx264 -y %1-countdown.mp4

rem ffmpeg -loglevel quiet -i %1.mp4 -filter_complex "drawtext=fontfile='/WINDOWS/Fonts/Arial.ttf':text='%%{eif\:%2-t\:d}':fontcolor=black:fontsize=24:x=w-tw-27:y=th-10:box=1:boxcolor=orange@0.4:boxborderw=10:enable='between(t,0,%2)'" -c:a copy -c:v libx264 -y %1-countdown.mp4

