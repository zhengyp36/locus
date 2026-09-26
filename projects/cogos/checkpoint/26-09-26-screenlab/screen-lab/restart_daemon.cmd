@echo off
taskkill /f /im pythonw.exe >nul 2>&1
ping -n 2 127.0.0.1 >nul
start "" "C:\Program Files\Python311\pythonw.exe" "C:\Users\screen.TABLET-BBT8EQB4\screenlab\daemon.pyw"
exit /b 0
