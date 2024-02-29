@echo off

IF [%1]==[] GOTO:usage
IF [%2]==[] GOTO:usage

set template=%1
set packaged=%template:template=packaged%
set s3Prefix=%2

@REM set p1=%1
@REM set p1=%p1:~-5%
@REM IF not [%p1%]==[.yaml] goto:defaultTemplate

set command=sam package
ipconfig/all | find  "Cisco" 2>&1
if %errorlevel%==0 set command=aws cloudformation package --no-verify-ssl

set command=%command% --template-file %template%
set command=%command% --output-template-file %packaged% 
set command=%command% --s3-bucket sam-cli-source-bucket
set command=%command% --s3-prefix %s3Prefix%
goto:RUN

:usage
echo Package SAM template to creates a zip of your code and dependencies and uploads it to S3
echo Usage: %0 [TemplateName] s3-prefix
echo        TemplateName:   TemplateName (include .yaml)
echo        s3-prefix:      s3 folder name
exit /B 1

:RUN
echo %command%
%command%