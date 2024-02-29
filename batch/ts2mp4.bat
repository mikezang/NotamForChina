

rem ffmpeg -f concat -i list.txt -codec copy -y 【2023年度法務部News】vol.3テーマ「小口リース取引に関する裁判例について」.mp4

ffmpeg -f concat -i %1 -codec copy -y %2.mp4
