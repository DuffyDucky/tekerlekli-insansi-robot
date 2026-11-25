@echo off
rem Lale sanal ray (3B pencere): LiDAR YOK; kafa kamerasi + duvar etiketleri (AprilTag 36h11) + enkoder + on sonar.
rem Ornek: sanalray.bat koridor_3 ab      sanalray.bat koridor_5 kayip --kafa tarayan
rem Ek argumanlar: --kafa sabit|tarayan --aralik kavsak|3|5|8|12 --donus 0|0.14|0.25 --birak 0..4 --hiz 2
rem Ayrinti: kod\fizik\sanalray\BENIOKU.md. Robot ONERI varyanti (oneri firmware + on omni, VARSAYIM).
cd /d "%~dp0"
if "%LALE_SIM_VENV%"=="" set "LALE_SIM_VENV=%LOCALAPPDATA%\lale-sim-venv"
if not exist "%LALE_SIM_VENV%\Scripts\python.exe" (
  echo Fizik sanal ortami yok: %LALE_SIM_VENV%
  echo Kurulum: kod\SIMULASYON.md Fizik simulasyonu bolumu.
  pause
  exit /b 2
)
set "SAHNE=%~1"
if "%SAHNE%"=="" set "SAHNE=koridor_3"
set "GOREV=%~2"
if "%GOREV%"=="" set "GOREV=ab"
"%LALE_SIM_VENV%\Scripts\python.exe" fizik\sanalray\demo.py --koridor %SAHNE% --gorev %GOREV% %3 %4 %5 %6 %7 %8
if errorlevel 1 pause
