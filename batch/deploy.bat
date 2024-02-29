@echo off

IF [%1]==[] GOTO:usage
IF [%2]==[] GOTO:usage
@REM IF [%3]==[] GOTO:usage

set packaged=%1
set s3Prefix=%2
set stackName=%2
set region=ap-northeast-1
set envType=stag
set Nonce=

IF not [%3]==[] set region=%3
IF not [%4]==[] set EnvType=%4
IF not [%5]==[] set Nonce=%5

set command=sam deploy
ipconfig/all|find  "Cisco"
if %errorlevel%==0 set command=aws cloudformation deploy --no-verify-ssl

set command=%command% --template-file %packaged%
set command=%command% --s3-prefix %s3Prefix%
set command=%command% --stack-name %stackName%
set command=%command% --capabilities CAPABILITY_NAMED_IAM
set command=%command% --region %region%
set command=%command% --parameter-overrides EnvType=%envType% Nonce=%Nonce%

@REM IF not [%BucketName%]==[] set command=%command% BucketName=%BucketName%
goto:RUN

:usage
@echo Deploy SAM package to creates a Cloudformation Stack and deploys your resources.
@echo Usage: %0 templateName stackName EnvType region
@echo        templateName:  Template name
@echo        StackNamet:    stack name
@echo        envType:       API stage name (stag or prod)
@echo        region:        region
@REM @echo        bucketName:    Bucket name (gaia-stag-static-bucket or gaia-prod-static-bucket)
exit /B 1

:RUN
echo %command%
%command%
