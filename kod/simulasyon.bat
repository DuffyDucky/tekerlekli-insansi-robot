@echo off
rem Lale sahte ESP32 + tarayicida gorunum (Y0s). Kapatmak icin bu pencerede Ctrl+C.
cd /d "%~dp0"
py -3 araclar\sahte_esp32 %*
pause
