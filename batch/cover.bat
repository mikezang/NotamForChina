@echo off
chcp 65001

rem IF [%1]==[] GOTO usage

cd \zang\python\Rocket*

python createImage.py "%1"

echo Create cover video
ffmpeg -framerate 20 -loop 1 -i images/cover.png -i videos/coverBase.mp4 -filter_complex "[1:v]scale=864:504[video];[0:v][video]concat=n=2:v=1:a=0" -t 5 -c:v libx264 -pix_fmt yuv420p -y videos\cover.mp4


rem ffmpeg -loop 1 -t 5 -i images/cover.png -i videos/中国运载火箭发射统计-music.mp4 -filter_complex "[0:v]scale=864:504,setsar=1[cover];[1:v]scale=864:504[video];[cover][video]concat=n=2:v=1:a=0" -c:v libx264 -pix_fmt yuv420p -y videos\中国运载火箭发射统计-music-cover.mp4

goto :EOF


:usage
echo Cretae cover video for deadline
echo %0 deadline
echo   deadline: "2024年10月31日"

:EOF
exit /b 1
