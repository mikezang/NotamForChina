@echo off

chcp 65001
cd \zang\python\Rocket*

:Usage
@echo.
@echo ====================================================================
@echo Run plot to Create All Chart Bar Race Videos in other command window
@echo Check merge list for new page
call parsefilename
@echo 0  - Create cover.mp4
@echo 1  - Create 中国运载火箭发射统计（今年）.mp4 by mergelist\ListImageThisYear.txt
@echo 2  - Create 中国运载火箭发射统计（月别）.mp4 by mergelist\ListImageMonth.txt
@echo 3  - Create 中国运载火箭发射统计（地别）.mp4 by mergelist\ListImageLocation.txt
@echo 4  - Create 中国运载火箭发射统计（箭别）.mp4 by mergelist\ListImageRocket.txt
@echo 5  - Create 中国运载火箭发射统计（全部）.mp4 by mergelist\ListImageAll.txt
@echo 6  - Create 中国运载火箭发射动态图.mp4 by mergelist\ListVideoBarChartRace.txt
@echo 7  - Create 中国运载火箭发射统计.mp4 by mergelist\ListVideoAll.txt
@echo 81 - Create 中国运载火箭发射统计-祝福祖国.mp4 with 祝福祖国.mp3
@echo 82 - Create 中国运载火箭发射统计-歌唱祖国音乐.mp4 with 歌唱祖国音乐.mp3
@echo 83 - Create 中国运载火箭发射统计-山口百惠.mp4 with 山口百惠歌曲
@echo 91 - Create 中国航天员在轨历史动态条形图-歌唱祖国音乐.mp4 with 歌唱祖国音乐.mp3
@echo 92 - Create 中国航天员在轨历史动态条形图-山口百惠.mp4 with 山口百惠歌曲
@echo A0 - Create calendar Videos by mergelist\ListImageCalendar.txt
@echo A1 - Create calendarLastMonth Videos by mergelist\ListImageCalendarLastMonth.txt
rem @echo A2 - Create calendarPast.mp4 by mergelist\ListVideoCalendarPast.txt
@echo A2 - Create calendar.mp4 by mergelist\ListVideoCalendar.txt
@echo A3 - Create calendar-歌唱祖国音乐.mp4 with 歌唱祖国音乐.mp3
@echo A4 - Create calendar-山口百惠.mp4 with 山口百惠歌曲
@echo X  - Exit

:Input
for /f %%a in ('powershell -Command "(Get-Date -Day 1).AddMonths(1).AddDays(-1).ToString('yyyyMMdd')"') do set defaultDate=%%a
set coverDate=%defaultDate%

set YEAR=%date:~0,4%

set option=
set/p option=Select :
if "%option%"=="x" GOTO EOF
if "%option%"=="X" GOTO EOF
if "%option%"=="0" echo 截止日期：%coverDate% && pause && call cover %coverDate% && GOTO Usage
if "%option%"=="1" call merge.bat mergelist\ListImageThisYear.txt videos\中国运载火箭发射统计（今年）.mp4 && GOTO Usage
if "%option%"=="2" call merge.bat mergelist\ListImageMonth.txt videos\中国运载火箭发射统计（月别）.mp4 && GOTO Usage
if "%option%"=="3" call merge.bat mergelist\ListImageLocation.txt videos\中国运载火箭发射统计（地别）.mp4 && GOTO Usage
if "%option%"=="4" call merge.bat mergelist\ListImageRocket.txt videos\中国运载火箭发射统计（箭别）.mp4 && GOTO Usage
if "%option%"=="5" call merge.bat mergelist\ListImageAll.txt videos\中国运载火箭发射统计（全部）.mp4 && GOTO Usage
if "%option%"=="6" call merge.bat mergelist\ListVideoBarChartRace.txt videos\中国运载火箭发射动态图.mp4 && GOTO Usage
if "%option%"=="7" call merge.bat mergelist\ListVideoAll.txt videos\中国运载火箭发射统计.mp4 && GOTO Usage 
if "%option%"=="81" call merge.bat 1 videos\中国运载火箭发射统计-祝福祖国.mp4 && GOTO Usage
if "%option%"=="82" call merge.bat 1 videos\中国运载火箭发射统计-歌唱祖国音乐.mp4 && GOTO Usage
if "%option%"=="83" goto :Momoe1
if "%option%"=="91" call merge.bat 1 videos\中国航天员在轨历史动态条形图.mp4 && GOTO Usage
if "%option%"=="92" goto :Momoe2
if "%option%"=="a0" call merge.bat mergelist\ListImageCalendar.txt calendar\videos\9999.mp4 && GOTO Usage
if "%option%"=="A0" call merge.bat mergelist\ListImageCalendar.txt calendar\videos\9999.mp4 && GOTO Usage
if "%option%"=="a1" call merge.bat mergelist\ListImageCalendarLastMonth.txt calendar\videos\9999.mp4 && GOTO Usage
if "%option%"=="A1" call merge.bat mergelist\ListImageCalendarLastMonth.txt calendar\videos\9999.mp4 && GOTO Usage
rem if "%option%"=="a2" call merge.bat mergelist\ListVideoCalendarPast.txt calendar\videos\calendarPast.mp4 && GOTO Usage
rem if "%option%"=="A2" call merge.bat mergelist\ListVideoCalendarPast.txt calendar\videos\calendarPast.mp4 && GOTO Usage
if "%option%"=="a2" call merge.bat mergelist\ListVideoCalendar.txt videos\calendar.mp4 && GOTO Usage
if "%option%"=="A2" call merge.bat mergelist\ListVideoCalendar.txt videos\calendar.mp4 && GOTO Usage
if "%option%"=="a3" call merge.bat 1 videos\calendar.mp4 && GOTO Usage
if "%option%"=="A3" call merge.bat 1 videos\calendar.mp4 && GOTO Usage
if "%option%"=="a4" goto :Momoe3 
if "%option%"=="A4" goto :Momoe3 
goto Usage
exit /B 1

:Concat
call merge.bat mergelist\ListVideoAll.txt videos\中国运载火箭发射统计.mp4 
rem call copy videos\中国运载火箭发射统计.mp4 videos\中国运载火箭发射统计-山口百惠.mp4  
GOTO Usage

:Momoe1
call match.bat videos\中国运载火箭发射统计.mp4 None mergelist\ListMusicMomoe.txt 10 10 %YEAR%
set/p mergeNo=Input Merge Number : 
call merge.bat %mergeNo% videos\中国运载火箭发射统计-山口百惠.mp4
GOTO Usage

:Momoe2
rem call copy videos\中国航天员在轨历史动态条形图.mp4 videos\中国航天员在轨历史动态条形图-山口百惠.mp4
call match.bat videos\中国航天员在轨历史动态条形图.mp4 None None 10 10 %YEAR%
set/p mergeNo=Input Merge Number : 
call merge.bat %mergeNo% videos\中国航天员在轨历史动态条形图-山口百惠.mp4
GOTO Usage

:Momoe3
rem call copy videos\calendar.mp4 videos\calendar-山口百惠.mp4 
call match.bat videos\calendar.mp4 None None 10 10 %YEAR% 
set/p mergeNo=Input Merge Number : 
call merge.bat %mergeNo% videos\calendar-山口百惠.mp4 
GOTO Usage

:EOF
