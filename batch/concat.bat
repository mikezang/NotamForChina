@ECHO OFF

IF [%1]==[] goto usage
IF [%2]==[] GOTO usage

if [%1] == [musiclist] (
	ffmpeg -loglevel quiet -f concat -safe 0 -i %1.txt -y %2
) else (
	ffmpeg -loglevel quiet -f concat -safe 0 -i %1.txt -c copy -y %2
)

rem rem ffmpeg -f concat -safe 0 -i %1 -c copy %2
rem ffmpeg -i %1.mp4 -i %2.mp4 -filter_complex "[0]adelay=0[a0];[1]adelay=5000[a1];[a0][a1]amix=inputs=2" %1-merge.mp4

GOTO :eof


:usage
@echo Concat video files to one file
@echo Usage: %0 file_list_file newFilenameExt
@echo        file_list_file:	Old video Filenames list
@echo        newFilenameExt:	New video Filename with extension
exit /B 1

:EOF

