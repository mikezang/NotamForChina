@echo off

cd \zang\python\RocketLaunch

echo starting plot in background ...
start /b python plot.py %1 run
