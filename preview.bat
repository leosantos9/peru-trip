@echo off
cd /d "%~dp0"
py -3 scripts\build.py
if errorlevel 1 (
  echo The website build failed. Check the message above.
  pause
  exit /b 1
)
py -3 scripts\validate.py
if errorlevel 1 (
  echo The website validation failed. Check the message above.
  pause
  exit /b 1
)
start "" "http://127.0.0.1:8765/"
py -3 -m http.server 8765 --bind 127.0.0.1 --directory "%~dp0dist"
pause
