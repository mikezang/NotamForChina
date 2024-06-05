ffmpeg -hide_banner ^
	-i "C:\zang\python\RocketLaunch\videos\民营.mp4" ^
	-i "C:\zang\python\RocketLaunch\videos\其他.mp4" ^
	-i "C:\zang\python\RocketLaunch\videos\years\2024全部.mp4" ^
	-filter_complex_script %1.txt ^
	-t 60 -y %2.mp4
