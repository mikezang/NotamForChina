ffmpeg -loglevel quiet -sseof -3 -i %1.mp4 -vsync 0 -q:v 31 -update true %1.png
