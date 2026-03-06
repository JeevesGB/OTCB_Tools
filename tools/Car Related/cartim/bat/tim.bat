@echo off
cd /d "%~dp0.."

echo Running CAR TIM extractor...
echo.

python tim.py

echo.
echo Finished.
pause