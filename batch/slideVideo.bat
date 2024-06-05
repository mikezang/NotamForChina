ffmpeg -hide_banner ^
	-i "C:\zang\python\RocketLaunch\videos\民营.mp4" ^
	-filter_complex_script %1.txt ^
	 -t 100 -y %2.mp4
