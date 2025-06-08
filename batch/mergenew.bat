@echo off

chcp 65001

IF [%1]==[] goto usage

cd \zang\python\Rocket*

call cover %1

rem pause
rem goto :MergeAll

call merge mergelist\ListImageThisYear.txt videos\中国运载火箭发射统计（今年）.mp4
call merge mergelist\ListImageMonth.txt videos\中国运载火箭发射统计（月别）.mp4
call merge mergelist\ListImageLocation.txt videos\中国运载火箭发射统计（地别）.mp4
call merge mergelist\ListImageRocket.txt videos\中国运载火箭发射统计（箭别）.mp4
call merge mergelist\ListImageAll.txt videos\中国运载火箭发射统计（全部）.mp4
call merge mergelist\ListVideoBarChartRace.txt videos\至2025中国运载火箭发射动态图.mp4

rem call merge mergelist\ListVideoYear.txt videos\中国运载火箭发射动态图（年别）.mp4
rem call merge mergelist\ListVideoCategory.txt videos\至2025中国运载火箭发射动态图（分类）.mp4
rem call merge mergelist\ListImageComplex.txt videos\中国运载火箭发射综合统计.mp4

:MergeAll
call merge mergelist\ListVideoAll.txt videos\中国运载火箭发射统计.mp4
echo coping videos\中国运载火箭发射统计.mp4 to videos\中国运载火箭发射统计-momoe.mp4
call copy videos\中国运载火箭发射统计.mp4 videos\中国运载火箭发射统计-momoe.mp4

call match videos\中国运载火箭发射统计.mp4 music/歌唱祖国音乐.mp3
call merge 1 videos\中国运载火箭发射统计.mp4

call match videos\中国运载火箭发射统计-momoe.mp4 "" mergelist\ListMusicMomoe.txt 10 0 200

rem call merge ? videos\中国运载火箭发射统计-momoe.mp4
rem echo merge ? videos\中国运载火箭发射统计-momoe.mp4
echo merge momoe's music to video
echo momoe ?

goto :EOF

@echo Create Coverimage for video
@echo Usage: %0 deadline
@echo   deadloine last date to print
:Usage
@echo.
@echo ==============================
@echo A - Create All Chart Bar Race Videos
@echo 0 - Create cover.mp4
@echo 1 - Create 中国运载火箭发射统计（今年）.mp4　　by mergelist\ListImageThisYear.txt
@echo 2 - Create 中国运载火箭发射统计（月别）.mp4　　by mergelist\ListImageMonth.txt
@echo 3 - Create 中国运载火箭发射统计（地别）.mp4　　by mergelist\ListImageLocation.txt
@echo 4 - Create 中国运载火箭发射统计（箭别）.mp4　　by mergelist\ListImageRocket.txt
@echo 5 - Create 中国运载火箭发射统计（全部）.mp4　　by mergelist\ListImageAll.txt
@echo 6 - Create 中国运载火箭发射动态图.mp4　　　　　by mergelist\ListVideoBarChartRace.txt
@echo 7 - Create 中国运载火箭发射统计.mp4　　　　　　by mergelist\ListVideoAll.txt
@echo 8 - Create 中国运载火箭发射统计-music.mp4 
@echo 9 - Create 中国运载火箭发射统计-momoe-music.mp4 
@echo X - Exit

:Input
set option=
set/p option=Select :
if "%option%"=="x" GOTO EOF
if "%option%"=="X" GOTO EOF
if "%option%"=="a" call plotAllVideos && GOTO EOF
if "%option%"=="A" call plotAllVideos && GOTO EOF
if "%option%"=="0" set/p coverDate=Input Cover Date : && call cover %coverDate% && GOTO Usage
if "%option%"=="1" call merge mergelist\ListImageThisYear.txt videos\中国运载火箭发射统计（今年）.mp4 && GOTO Usage
if "%option%"=="2" call merge mergelist\ListImageMonth.txt videos\中国运载火箭发射统计（月别）.mp4 && GOTO Usage
if "%option%"=="3" call merge mergelist\ListImageLocation.txt videos\中国运载火箭发射统计（地别）.mp4 && GOTO Usage
if "%option%"=="4" call merge mergelist\ListImageRocket.txt videos\中国运载火箭发射统计（箭别）.mp4 && GOTO Usage
if "%option%"=="5" call merge mergelist\ListImageAll.txt videos\中国运载火箭发射统计（全部）.mp4 && GOTO Usage
if "%option%"=="6" call merge mergelist\ListVideoBarChartRace.txt videos\中国运载火箭发射动态图.mp4 && GOTO Usage
if "%option%"=="7" call merge mergelist\ListVideoAll.txt videos\中国运载火箭发射统计.mp4 && call copy videos\中国运载火箭发射统计.mp4 videos\中国运载火箭发射统计-momoe.mp4 && GOTO Usage
if "%option%"=="8" call match videos\中国运载火箭发射统计.mp4 music/歌唱祖国音乐.mp3 && call merge 1 videos\中国运载火箭发射统计.mp4 && GOTO Usage
if "%option%"=="9" call match videos\中国运载火箭发射统计-momoe.mp4 "" mergelist\ListMusicMomoe.txt 10 0 200 && set/p mergeNo=Input Merge Number : && call momoe %mergeNo% && GOTO Usage
goto Usage
exit /B 1

:EOF
