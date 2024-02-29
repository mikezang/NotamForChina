@echo off
rem if [%1] == [] goto 2023

cd C:\zang\python\RocketLaunch

chcp 65001

call countdown videos\1970～1979全部-last 10
call :duration videos\1970～1979全部.mp4
set x=%errorlevel%
echo 01. total length: %x%, video length: %errorlevel%, 

call :duration videos\1970～1979全部-last-10s.mp4
set /a x=%x%+%errorlevel%
echo 02. total length: %x%, video length: %errorlevel%, 
echo.

call countdown videos\1980～1989全部-last 10
call :duration videos\1980～1989全部.mp4
set /a x=%x%+%errorlevel%
echo 03. total length: %x%, video length: %errorlevel%, 

call :duration videos\1980～1989全部-last-10s.mp4
set /a x=%x%+%errorlevel%
echo 04. total length: %x%, video length: %errorlevel%, 
echo.

call countdown videos\1990～1999全部-last 10
call :duration videos\1990～1999全部.mp4
set /a x=%x%+%errorlevel%
echo 05. total length: %x%, video length: %errorlevel%, 

call :duration videos\1990～1999全部-last-10s.mp4
set /a x=%x%+%errorlevel%
echo 06. total length: %x%, video length: %errorlevel%, 
echo.

call countdown videos\2000～2009全部-last 10
call :duration videos\2000～2009全部.mp4
set /a x=%x%+%errorlevel%
echo 07. total length: %x%, video length: %errorlevel%, 

call :duration videos\2000～2009全部-last-10s.mp4
set /a x=%x%+%errorlevel%
echo 08. total length: %x%, video length: %errorlevel%, 
echo.

call countdown videos\2010全部-last 10
call :duration videos\2010全部.mp4
set /a x=%x%+%errorlevel%
echo 09. total length: %x%, video length: %errorlevel%, 

call :duration videos\2010全部-last-10s.mp4
set /a x=%x%+%errorlevel%
echo 10. total length: %x%, video length: %errorlevel%, 
echo.

call countdown videos\2011全部-last 10
call :duration videos\2011全部.mp4
set /a x=%x%+%errorlevel%
echo 11. total length: %x%, video length: %errorlevel%, 

call :duration videos\2011全部-last-10s.mp4
set /a x=%x%+%errorlevel%
echo 12. total length: %x%, video length: %errorlevel%, 
echo.

call countdown videos\2012全部-last 10
call :duration videos\2012全部.mp4
set /a x=%x%+%errorlevel%
echo 13. total length: %x%, video length: %errorlevel%, 

call :duration videos\2012全部-last-10s.mp4
set /a x=%x%+%errorlevel%
echo 14. total length: %x%, video length: %errorlevel%, 
echo.

call countdown videos\2013全部-last 10
call :duration videos\2013全部.mp4
set /a x=%x%+%errorlevel%
echo 15. total length: %x%, video length: %errorlevel%, 

call :duration videos\2013全部-last-10s.mp4
set /a x=%x%+%errorlevel%
echo 16. total length: %x%, video length: %errorlevel%, 
echo.

call countdown videos\2014全部-last 10
call :duration videos\2014全部.mp4
set /a x=%x%+%errorlevel%
echo 17. total length: %x%, video length: %errorlevel%, 

call :duration videos\2014全部-last-10s.mp4
set /a x=%x%+%errorlevel%
echo 18. total length: %x%, video length: %errorlevel%, 
echo.

call countdown videos\2015全部-last 10
call :duration videos\2015全部.mp4
set /a x=%x%+%errorlevel%
echo 19. total length: %x%, video length: %errorlevel%, 

call :duration videos\2015全部-last-10s.mp4
set /a x=%x%+%errorlevel%
echo 20. total length: %x%, video length: %errorlevel%, 
echo.

call countdown videos\2016全部-last 10
call :duration videos\2016全部.mp4
set /a x=%x%+%errorlevel%
echo 21. total length: %x%, video length: %errorlevel%, 

call :duration videos\2016全部-last-10s.mp4
set /a x=%x%+%errorlevel%
echo 22. total length: %x%, video length: %errorlevel%, 
echo.

call countdown videos\2017全部-last 10
call :duration videos\2017全部.mp4
set /a x=%x%+%errorlevel%
echo 23. total length: %x%, video length: %errorlevel%, 

call :duration videos\2017全部-last-10s.mp4
set /a x=%x%+%errorlevel%
echo 24. total length: %x%, video length: %errorlevel%, 
echo.

call countdown videos\2018全部-last 10
call :duration videos\2018全部.mp4
set /a x=%x%+%errorlevel%
echo 25. total length: %x%, video length: %errorlevel%, 

call :duration videos\2018全部-last-10s.mp4
set /a x=%x%+%errorlevel%
echo 26. total length: %x%, video length: %errorlevel%, 
echo.

call countdown videos\2019全部-last 10
call :duration videos\2019全部.mp4
set /a x=%x%+%errorlevel%
echo 27. total length: %x%, video length: %errorlevel%, 

call :duration videos\2019全部-last-10s.mp4
set /a x=%x%+%errorlevel%
echo 28. total length: %x%, video length: %errorlevel%, 
echo.

call countdown videos\2020全部-last 10
call :duration videos\2020全部.mp4
set /a x=%x%+%errorlevel%
echo 29. total length: %x%, video length: %errorlevel%, 

call :duration videos\2020全部-last-10s.mp4
set /a x=%x%+%errorlevel%
echo 30. total length: %x%, video length: %errorlevel%, 
echo.

call countdown videos\2021全部-last 10
call :duration videos\2021全部.mp4
set /a x=%x%+%errorlevel%
echo 31. total length: %x%, video length: %errorlevel%, 

call :duration videos\2021全部-last-10s.mp4
set /a x=%x%+%errorlevel%
echo 32. total length: %x%, video length: %errorlevel%, 
echo.

call countdown videos\2022全部-last 10
call :duration videos\2022全部.mp4
set /a x=%x%+%errorlevel%
echo 33. total length: %x%, video length: %errorlevel%, 

call :duration videos\2022全部-last-10s.mp4
set /a x=%x%+%errorlevel%
echo 34. total length: %x%, video length: %errorlevel%, 
echo.

:2023
call countdown videos\2023全部-last 10
call :duration videos\2023全部.mp4
set /a x=%x%+%errorlevel%
echo 35. total length: %x%, video length: %errorlevel%, 

call :duration videos\2023全部-last-10s.mp4
set /a x=%x%+%errorlevel%
echo 36. total length: %x%, video length: %errorlevel%, 
echo.

:2024
call countdown videos\2024全部-last 10
call :duration videos\2024全部.mp4
set /a x=%x%+%errorlevel%
echo 37. total length: %x%, video length: %errorlevel%, 

echo Create videolist.txt
echo file 'videos/1970～1979全部.mp4'                     > videolist.txt
echo file 'videos/1970～1979全部-last-10s-countdown.mp4' >> videolist.txt
echo file 'videos/1980～1989全部.mp4'                    >> videolist.txt
echo file 'videos/1980～1989全部-last-10s-countdown.mp4' >> videolist.txt
echo file 'videos/1990～1999全部.mp4'                    >> videolist.txt
echo file 'videos/1990～1999全部-last-10s-countdown.mp4' >> videolist.txt
echo file 'videos/2000～2009全部.mp4'                    >> videolist.txt
echo file 'videos/2000～2009全部-last-10s-countdown.mp4' >> videolist.txt
echo file 'videos/2010全部.mp4'                          >> videolist.txt
echo file 'videos/2010全部-last-10s-countdown.mp4'       >> videolist.txt
echo file 'videos/2011全部.mp4'                          >> videolist.txt
echo file 'videos/2011全部-last-10s-countdown.mp4'       >> videolist.txt
echo file 'videos/2012全部.mp4'                          >> videolist.txt
echo file 'videos/2012全部-last-10s-countdown.mp4'       >> videolist.txt
echo file 'videos/2013全部.mp4'                          >> videolist.txt
echo file 'videos/2013全部-last-10s-countdown.mp4'       >> videolist.txt
echo file 'videos/2014全部.mp4'                          >> videolist.txt
echo file 'videos/2014全部-last-10s-countdown.mp4'       >> videolist.txt
echo file 'videos/2015全部.mp4'                          >> videolist.txt
echo file 'videos/2015全部-last-10s-countdown.mp4'       >> videolist.txt
echo file 'videos/2016全部.mp4'                          >> videolist.txt
echo file 'videos/2016全部-last-10s-countdown.mp4'       >> videolist.txt
echo file 'videos/2017全部.mp4'                          >> videolist.txt
echo file 'videos/2017全部-last-10s-countdown.mp4'       >> videolist.txt
echo file 'videos/2018全部.mp4'                          >> videolist.txt
echo file 'videos/2018全部-last-10s-countdown.mp4'       >> videolist.txt
echo file 'videos/2019全部.mp4'                          >> videolist.txt
echo file 'videos/2019全部-last-10s-countdown.mp4'       >> videolist.txt
echo file 'videos/2020全部.mp4'                          >> videolist.txt
echo file 'videos/2020全部-last-10s-countdown.mp4'       >> videolist.txt
echo file 'videos/2021全部.mp4'                          >> videolist.txt
echo file 'videos/2021全部-last-10s-countdown.mp4'       >> videolist.txt
echo file 'videos/2022全部.mp4'                          >> videolist.txt
echo file 'videos/2022全部-last-10s-countdown.mp4'       >> videolist.txt
echo file 'videos/2023全部.mp4'                          >> videolist.txt
echo file 'videos/2023全部-last-10s-countdown.mp4'       >> videolist.txt
echo file 'videos/2024全部.mp4'                          >> videolist.txt
echo file 'videos/2024全部-last-10s-countdown.mp4'       >> videolist.txt
echo.

echo Create videos\merge-years.mp4 (concat above videos to videos\merge-years.mp4)
call concat videolist videos\merge-years.mp4
echo.

rem echo Create videos\merge-years-music.mp4 (music\歌唱祖国-6m.mp3 to videos\merge-years.mp4)
rem call addmp32mp4 music\歌唱祖国-6m videos\merge-years
rem echo.

echo Remove all temporary files
del videos\1970～1979全部-last-10s.mp4
del videos\1980～1989全部-last-10s.mp4
del videos\1990～1999全部-last-10s.mp4
del videos\2000～2009全部-last-10s.mp4
del videos\2010全部-last-10s.mp4
del videos\2011全部-last-10s.mp4
del videos\2012全部-last-10s.mp4
del videos\2013全部-last-10s.mp4
del videos\2014全部-last-10s.mp4
del videos\2015全部-last-10s.mp4
del videos\2016全部-last-10s.mp4
del videos\2017全部-last-10s.mp4
del videos\2018全部-last-10s.mp4
del videos\2019全部-last-10s.mp4
del videos\2020全部-last-10s.mp4
del videos\2021全部-last-10s.mp4
del videos\2022全部-last-10s.mp4
del videos\2023全部-last-10s.mp4
del videos\1970～1979全部-last-10s-countdown.mp4
del videos\1980～1989全部-last-10s-countdown.mp4
del videos\1990～1999全部-last-10s-countdown.mp4
del videos\2000～2009全部-last-10s-countdown.mp4
del videos\2010全部-last-10s-countdown.mp4
del videos\2011全部-last-10s-countdown.mp4
del videos\2012全部-last-10s-countdown.mp4
del videos\2013全部-last-10s-countdown.mp4
del videos\2014全部-last-10s-countdown.mp4
del videos\2015全部-last-10s-countdown.mp4
del videos\2016全部-last-10s-countdown.mp4
del videos\2017全部-last-10s-countdown.mp4
del videos\2018全部-last-10s-countdown.mp4
del videos\2019全部-last-10s-countdown.mp4
del videos\2020全部-last-10s-countdown.mp4
del videos\2021全部-last-10s-countdown.mp4
del videos\2022全部-last-10s-countdown.mp4
del videos\2023全部-last-10s-countdown.mp4
del videos\2024全部-last-10s-countdown.mp4
rem del videos\merge-years.mp4
echo.

echo Create Convert to 12800 tbn
move videos\merge-years.mp4 videos\merge-years-10240.mp4
ffmpeg -loglevel quiet -i videos\merge-years-10240.mp4 -c copy -video_track_timescale 12800 videos\merge-years.mp4
echo.

call addmp32mp4 music\歌唱祖国-6m videos\merge-years

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
