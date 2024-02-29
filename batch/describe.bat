@echo off

if [%1] == [] goto:usage
if [%2] == [] goto:usage

set dateFormat=%date:/=-%
set stackName=%1
set region=%2

@REM set command=aws cloudformation describe-stack-events --no-verify-ssl
@REM set command=%command% --stack-name %stackName%
@REM set command=%command% --region %region%
@REM set command=%command% 

@REM echo %command%
@REM %command% 

echo "aws cloudformation describe-stack-events --no-verify-ssl --stack-name %stackName% --region %region% | find /i "%dateFormat%" | find /i "failed""
aws cloudformation describe-stack-events --no-verify-ssl --stack-name %stackName% --region %region%|find /i "%dateFormat%"|find /i "failed"
goto:EOF

:usage
echo Describe stack 
echo Usage: %0 stackName region
echo        stackName:   Stack Name
echo        region:      Region ID
exit /B 1

:EOF