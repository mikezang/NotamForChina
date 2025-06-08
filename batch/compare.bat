@echo off
cd \zang\python\RocketLaunch

echo starting compare in background ...
start /b python compare.py %1 run
