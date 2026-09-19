@echo off
python build_network.py
if errorlevel 1 exit /b %errorlevel%
echo SUMO network build complete.
