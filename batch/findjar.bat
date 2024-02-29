@echo off
setlocal EnableDelayedExpansion

for %%j in (*.jar) do (
    ECHO %%j
    jdeps -s %%j | find /i "commons-collections"

    IF "!ERRORLEVEL!"=="0" (
rem        ECHO %%j
    ) ELSE (
rem        ECHO %%j
    )
)
