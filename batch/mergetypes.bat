rem @echo off
chcp 65001

cd C:\zang\python\RocketLaunch

call countdown videos\民营-last 10
call :duration videos\民营.mp4
rem call :getInteger %errorlevel%
set x=%errorlevel%
echo 01. total length: %x%, video length: %errorlevel%, 

call :duration videos\民营-last-10s.mp4
rem call :getInteger %errorlevel%
set /a x=%x%+%errorlevel%
echo 02. total length: %x%, video length: %errorlevel%, 
echo.

call countdown videos\其他-last 10
call :duration videos\其他.mp4
rem call :getInteger %errorlevel%
set /a x=%x%+%errorlevel%
echo 03. total length: %x%, video length: %errorlevel%, 

call :duration videos\其他-last-10s.mp4
rem call :getInteger %errorlevel%
set /a x=%x%+%errorlevel%
echo 04. total length: %x%, video length: %errorlevel%, 
echo.

call countdown videos\长征-last 10
call :duration videos\长征.mp4
rem call :getInteger %errorlevel%
set /a x=%x%+%errorlevel%
echo 05. total length: %x%, video length: %errorlevel%, 

call :duration videos\长征-last-10s.mp4
rem call :getInteger %errorlevel%
set /a x=%x%+%errorlevel%
echo 06. total length: %x%, video length: %errorlevel%, 
echo.

call countdown videos\系列-last 10
call :duration videos\系列.mp4
rem call :getInteger %errorlevel%
set /a x=%x%+%errorlevel%
echo 07. total length: %x%, video length: %errorlevel%, 

call :duration videos\系列-last-10s.mp4
rem call :getInteger %errorlevel%
set /a x=%x%+%errorlevel%
echo 08. total length: %x%, video length: %errorlevel%, 
echo.

call countdown videos\全部-last 10
call :duration videos\全部.mp4
rem call :getInteger %errorlevel%
set /a x=%x%+%errorlevel%
echo 09. total length: %x%, video length: %errorlevel%, 

rem call :duration music\歌唱祖国-15m.mp3
rem call :getInteger %errorlevel%
set y=%errorlevel%
set /a z=%y%-%x%
rem echo music length: %y%, video length: %x%, last video length: %z%

rem goto :eof

rem call :duration videos\全部-last-10s.mp4
rem call :getInteger %errorlevel%
set /a x=%x%+%errorlevel%
echo 10. total length: %x%, video length: %errorlevel%, 
rem echo 11. music lenght: %y%
echo.

echo Create videolist.txt
echo file 'videos/民营.mp4'                     > videolist.txt
echo file 'videos/民营-last-10s-countdown.mp4' >> videolist.txt
echo file 'videos/其他.mp4'                    >> videolist.txt
echo file 'videos/其他-last-10s-countdown.mp4' >> videolist.txt
echo file 'videos/长征.mp4'                    >> videolist.txt
echo file 'videos/长征-last-10s-countdown.mp4' >> videolist.txt
echo file 'videos/系列.mp4'                    >> videolist.txt
echo file 'videos/系列-last-10s-countdown.mp4' >> videolist.txt
echo file 'videos/全部.mp4'                    >> videolist.txt
echo file 'videos/全部-last-10s-countdown.mp4' >> videolist.txt
echo.

echo Create videos\merge-types.mp4 (concat above videos to videos\merge-types.mp4)
call concat videolist videos\merge-types.mp4
echo.

echo Create videolist.txt
rem echo file 'videos/其他.mp4'                    > videolist.txt
rem echo file 'videos/其他-last-10s-countdown.mp4' >> videolist.txt
rem echo file 'videos/长征.mp4'                    > videolist.txt
rem echo file 'videos/长征-last-10s-countdown.mp4' >> videolist.txt
rem echo file 'videos/全部.mp4'                    >> videolist.txt
rem echo file 'videos/全部-last-10s-countdown.mp4' >> videolist.txt
rem echo.

rem echo Create videos\merge-types.mp4 (concat above videos to videos\merge-types1.mp4)
rem call concat videolist videos\merge-types1.mp4
rem echo.

rem echo Create videos\merge-all-music.mp4 (music\歌唱祖国-9m.mp3 to videos\merge-types1.mp4)
rem call addmp32mp4 music\歌唱祖国-9m videos\merge-types1
rem echo.

echo Remove all temporary files
del videos\民营-last-10s.mp4
del videos\其他-last-10s.mp4
del videos\长征-last-10s.mp4
del videos\系列-last-10s.mp4
del videos\全部-last-10s.mp4
del videos\民营-last-10s-countdown.mp4
del videos\其他-last-10s-countdown.mp4
del videos\长征-last-10s-countdown.mp4
del videos\系列-last-10s-countdown.mp4
del videos\全部-last-10s-countdown.mp4
del videos\merge-types.mp4
echo.

echo Create Convert to 12800 tbn
move videos\merge-types.mp4 videos\merge-types-10240.mp4
ffmpeg -loglevel quiet -i videos\merge-types-10240.mp4 -c copy -video_track_timescale 12800 videos\merge-types.mp4
echo.

echo Resize to last image 1920 width resolution
call resizepng videos\全部-last

goto :eof

rem # addmp32mp4 71-ラスト・ソング 
rem # addmp32mp4 99-一恵 
rem # addmp32mp4 91-さよならの向う側 
rem # addmp32mp4 80-DANCIN’INTHERAIN 
rem # addmp32mp4 95-Thisismytrial~私の試練 
rem # addmp32mp4 94-テレパシーナ 
rem # addmp32mp4 72-曼珠沙華 
rem # addmp32mp4 47-歌い継がれてゆく歌のように 
rem # addmp32mp4 83-娘たち 
rem # addmp32mp4 44-オレンジ・ブロッサム・ブルース 
rem # addmp32mp4 82-しなやかに歌って
rem # addmp32mp4 62-ただよいの中で 
rem # addmp32mp4 98-CrazyLove 
rem # addmp32mp4 56-青い羊歯(しだ)~アジアンタム 
rem # addmp32mp4 41-パールカラーにゆれて 

:duration
set x1=%~1
for /F "delims=" %%I in ('ffprobe.exe -v error -show_entries format^=duration -of default^=noprint_wrappers^=1:nokey^=1 %x1% 2^>^&1') do set "duration=%%I"
rem echo Duration is(s): %duration%
exit /b %duration%

:getInteger
set a=%~1
if [%a:~3,1%] == [.] (
   set b=%a:~0,3%
) else (
   set b=%a:~0,2%
)

:eof
exit /b %b%
