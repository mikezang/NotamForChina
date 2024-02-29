@echo off

title "AWS SAM package/deploy/check stacks scripts"
rem SET currentPath=%~dp0
rem cd %currentPath%

set template=template.yaml
set stackName=
set s3Prefix=
set envType=
set bucketName=

IF [%1]==[] GOTO:usage
set p1=%1
set p1=%p1:~-5%
IF not [%p1%]==[.yaml] goto:defaultTemplate
IF [%2]==[] GOTO:usage
set template=%1
set stackName=%2
set s3Prefix=%2
IF not [%3]==[] set envType=%3
IF not [%4]==[] set bucketName=%4
goto:0

:defaultTemplate
set stackName=%1
set s3Prefix=%1
IF not [%2]==[] set envType=%2
IF not [%3]==[] set bucketName=%3

:0
echo Package Cloudformation resource and Deploy it.
echo *********************** help info ********************************************************
echo  0 : print this help info
echo  1 : package %template% %stackName%
echo  2 : deploy %s3Prefix% %envType% %bucketName%
echo  3 : deploy %s3Prefix% %envType% %bucketName% us-east-1 
echo  9 : describe-stack-events %stackName%
echo  X : Exit
echo Usage: %0 [TemplateName] StackName [EnvType] [BucketName]
echo        TemplateName:   TemplateName.yaml ([template.yaml])
echo        StackName:      Stack name
echo        EnvType:        API stage name ([stag] or prod)
echo        BucketName:     Bucket name ([gaia-stag-static-bucket] or gaia-prod-static-bucket)
echo ******************************************************************************************

:1
set/p option=please input :
if "%option%"=="0" goto 0
if "%option%"=="1" call package %template% %s3Prefix% && GOTO 0
if "%option%"=="2" call deploy %s3Prefix% %envType% %bucketName% && GOTO 0
if "%option%"=="3" call deploy %s3Prefix% %envType% %bucketName% us-east-1 && GOTO 0
if "%option%"=="9" call check %stackName% && GOTO 0
if "%option%"=="x" GOTO EOF
if "%option%"=="X" GOTO EOF
GOTO 1
pause

:usage
echo Package Cloudformation resource and Deploy it.
echo Usage: %0 [TemplateName] StackName [EnvType] [BucketName]
echo        TemplateName:   Template name ([template.yaml])
echo        StackName:   Stack name
echo        EnvType:     API stage name ([stag] or prod)
echo        BucketName:  Bucket name ([gaia-stag-static-bucket] or gaia-prod-static-bucket)

:EOF
exit /B 1
