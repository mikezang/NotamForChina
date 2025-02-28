@echo off

IF [%1]==[] goto usage


cd \zang\python

%1\Scripts\deactivate
goto EOF

:usage
@echo activate Python Virtual Environment
@echo Usage: %0 Virtual Environment Name
exit /B 1

:EOF
