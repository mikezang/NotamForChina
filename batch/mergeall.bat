@echo off

chcp 65001

rem call mergepngs
rem call mergeyears
call mergetypes

echo Create videolist.txt
echo file 'videos/merge-pngs.mp4'   > videolist.txt
echo file 'videos/merge-years.mp4' >> videolist.txt
echo file 'videos/merge-types.mp4  >> videolist.txt
echo.

echo Create videos\merge-all.mp4 (concat above videos to videos\merge-all.mp4)
call concat videolist videos\merge-all.mp4
echo.

echo Create videos\merge-all-music.mp4 (music\歌唱祖国音乐-27m.mp3 to videos\merge-all.mp4)
call addmp32mp4 music\歌唱祖国音乐-27m videos\merge-all
echo.

echo Create videos\merge-all-music.mp4 (music\momoe.mp3 to videos\merge-all-momoe.mp4)
call addmp32mp4 music\momoe videos\merge-all videos\merge-all-momoe
echo.

echo Remove all temporary files
rem del videos\merge-pngs.mp4
rem del videos\merge-years.mp4
rem del videos\merge-types.mp4
del videos\merge-years-10240.mp4
del videos\merge-types-10240.mp4
rem del videos\merge-all.mp4
