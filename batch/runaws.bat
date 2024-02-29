@echo off

IF [%1]==[] GOTO usage

aws --no-verify-ssl %1 %2 %3 %4 %5
goto:EOF

:usage
@echo Run AWS command with --no-verify-ssl
@echo Usage: %0 [options] command subcommand [parameters]
@echo        [options]:    aws command options
@echo        command:      aws command
@echo        subcommand:   aws sub command
@echo        [parameters]: aws command parameters
exit /B 1

:EOF
