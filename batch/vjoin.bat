ffmpeg -loglevel quiet -i %1.mp4 -i %2.mp4 -filter_complex "[0][1]vstack"  %1-vstack.mp4

rem ffplay %1 -loop 0 -af "volume=0.1" -left 0
rem ffmpeg -i %1.mp4 -i %2.mp4 -filter_complex "[0][1]vstack"  images\vstack.mp4
rem ffmpeg -i %1.mp4 -i %2.mp4 -filter_complex "[0][1]vstack" -t 10 images\joined.mp4
