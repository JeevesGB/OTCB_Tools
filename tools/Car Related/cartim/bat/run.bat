@echo off
cd /d "%~dp0.."

echo Running CAR TIM extractor...
echo.

python run.py

echo.
echo Finished.
pause