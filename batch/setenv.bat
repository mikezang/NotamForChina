@echo off

IF [%1]==[] goto usage
IF [%2]==[] goto usage

cd \zang\python

%1.exe -m virtualenv %2

exit /B 1
goto :eof

:usage
@echo Set Python Virtual Environment
@echo Usage: %0 pythonVrsion venvName
exit /B 1
