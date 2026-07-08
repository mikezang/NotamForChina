@echo off
chcp 65001

rem IF [%1]==[] GOTO usage

cd \zang\python\Rocket*

python createImage.py "%1"

echo Create cover video
ffmpeg -framerate 20 -loop 1 -i images/cover.png -i videos/coverBase.mp4 -filter_complex "[1:v]scale=1920:1080[video];[0:v][video]concat=n=2:v=1:a=0" -t 5 -c:v libx264 -pix_fmt yuv420p -y videos\cover.mp4
ffmpeg -framerate 20 -loop 1 -i images/cover1.png -i videos/coverBase.mp4 -filter_complex "[1:v]scale=1920:1080[video];[0:v][video]concat=n=2:v=1:a=0" -t 5 -c:v libx264 -pix_fmt yuv420p -y videos\cover1.mp4
ffmpeg -framerate 20 -loop 1 -i images/cover2.png -i videos/coverBase.mp4 -filter_complex "[1:v]scale=1920:1080[video];[0:v][video]concat=n=2:v=1:a=0" -t 5 -c:v libx264 -pix_fmt yuv420p -y videos\cover2.mp4
ffmpeg -framerate 20 -loop 1 -i images/cover3.png -i videos/coverBase.mp4 -filter_complex "[1:v]scale=1920:1080[video];[0:v][video]concat=n=2:v=1:a=0" -t 5 -c:v libx264 -pix_fmt yuv420p -y videos\cover3.mp4

goto :EOF


:usage
echo Cretae cover video for deadline
echo %0 deadline
echo   deadline: "2024年10月31日"

:EOF
exit /b 1
