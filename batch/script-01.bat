@echo off
ffmpeg -hide_banner -loglevel fatal ^
	-framerate 1 -loop 1 -i "C:\zang\python\RocketLaunch\calendar\197004.png" ^
	-framerate 1 -loop 1 -i "C:\zang\python\RocketLaunch\calendar\197103.png" ^
	-filter_complex_script script-01.txt ^
	-t 5 -r 1 -y v01.mp4
