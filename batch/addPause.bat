ffmpeg -loglevel quiet -i %1.mp4 -vf tpad=stop_mode=clone:stop_duration=%2 %1-%2s.mp4


rem ffmpeg -i %1.mp4 -t %2  -c:v libx264 -c:a copy -y %1-%s.mp4