@echo off

chcp 65001

cd \zang\python\R*

rem echo %CD%
set /a x=0
echo # this is a comment > jpgmergelist.txt

for /F "skip=1 tokens=1-3" %%G IN (jpglist.txt) DO (
rem   echo %%~pG %%~dpG %%~nxG %%H %%I
rem   set line=%%G
rem   echo %line:~0,1%
rem  echo %CD%\%%G\%%H.jpg to %CD%\%%I\%%H.mp4
	echo Create %CD%\%%I\%%H.mp4
	call jpg2mp4 %CD%\%%G\%%H 10 %CD%\%%I\%%H
	call :duration %CD%\%%I\%%H.mp4
	rem set /a x=%x%+%errorlevel%
	rem echo total length: %x%
	rem echo file '%CD%\%%I\%%H.mp4' >> jpgmergelist.txt
	echo Create %CD%\%%I\%%H-countdown.mp4
	call addCountdown %CD%\%%I\%%H 10
	call :duration %CD%\%%I\%%H.mp4
	rem set /a x=%x%+%errorlevel%
	rem echo total length: %x%
	echo file '%%I\%%H-countdown.mp4' >> jpgmergelist.txt
	echo Delete %CD%\%%I\%%H.mp4
	del %CD%\%%I\%%H.mp4
	set /a x=%x%+1
	echo.
)

echo Create %CD%\videos\merge-jpgs.mp4 from jpgs
call concat jpgmergelist videos\merge-jpgs.mp4
rem ffmpeg -f concat -safe 0 -i jpgmergelist.txt -filter_complex "[0:v]fade=t=in:st=0:d=1:alpha=1,fade=t=out:st=9:d=1:alpha=1[v0]; [1:v]fade=t=in:st=0:d=1:alpha=1,fade=t=out:st=9:d=1:alpha=1[v1]; [2:v]fade=t=in:st=0:d=1:alpha=1,fade=t=out:st=9:d=1:alpha=1[v2]; [v0][0:a][v1][1:a][v2][2:a]concat=n=%x%:v=1:a=1[vout][aout]" -map "[vout]" -map "[aout]" videos\merge-jpgs.mp4
echo.

echo Create %CD%\videos\merge-jpgs-music.mp4
call addmp32mp4 music\歌唱祖国男女声合唱 videos\merge-jpgs

for /R videos %%G IN (*-countdown.mp4) DO (
	echo Delele %%G
	del %%G
)
echo.

echo Delele %CD%\videos\merge-jpgs.mp4
del %CD%\videos\merge-jpgs.mp4
echo.

goto :eof

:duration
set x1=%~1
for /F "delims=" %%Z in ('ffprobe.exe -v error -show_entries format^=duration -of default^=noprint_wrappers^=1:nokey^=1 %x1% 2^>^&1') do set "duration=%%Z"
rem echo Duration is(s): %duration%
exit /b %duration%
