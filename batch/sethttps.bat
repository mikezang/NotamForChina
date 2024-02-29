@echo off
IF "%HTTPS_PROXY%" == "" (
    echo set HTTPS_PROXY to http://proxy-tky.i.smflc.co.jp:80
    echo set HTTP_PROXY to http://proxy-tky.i.smflc.co.jp:80
    echo set NO_PROXY 127.0.0.1,localhost,github.iqa.smfl.co.jp
    echo set config_strict_ssl false
    rem echo set NODE_TLS_REJECT_UNAUTHORIZED 0
    echo set DART_VM_OPTIONS -DSILENT_OBSERVATORY=true

    setx HTTPS_PROXY http://proxy-tky.i.smflc.co.jp:80
    setx HTTP_PROXY http://proxy-tky.i.smflc.co.jp:80
    setx NO_PROXY 127.0.0.1,localhost,github.iqa.smfl.co.jp
    setx config_strict_ssl false
    rem setx NODE_TLS_REJECT_UNAUTHORIZED 0
    setx DART_VM_OPTIONS -DSILENT_OBSERVATORY=true
    copy C:\Users\120000843\.gradle\gradle.properties.proxy C:\Users\120000843\.gradle\gradle.properties
) ELSE (
    echo reset HTTPS_PROXY
    echo reset HTTP_PROXY
rem echo set NO_PROXY 127.0.0.1,localhost,github.iqa.smfl.co.jp,api.smfl.co.jp
    setx HTTPS_PROXY ""
    setx HTTP_PROXY ""
rem echo set NO_PROXY localhost,github.iqa.smfl.co.jp
    del C:\Users\120000843\.gradle\gradle.properties
)
