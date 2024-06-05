ffmpeg -loop 1 -i "C:\zang\python\RocketLaunch\images\中国全部运载火箭发射数统计.png" -loop 1 -i "C:\zang\python\RocketLaunch\images\中国长征运载火箭发射数统计.png" -filter_complex_script %1.txt -t 30 -y %1.mp4 -hide_banner
