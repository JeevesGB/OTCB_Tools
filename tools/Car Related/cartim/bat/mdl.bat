@echo off
cd /d "%~dp0.."

echo Running CAR MDL extractor...
echo.

python mdl.py

echo.
echo Finished.
pause