@echo off
rem Lale gezinme (3B pencere): A'dan B'ye: bilinen koridor + baslangic, kapidan kapiya. Varyant ONERI (oneri firmware + on omni, VARSAYIM).
rem Ornek: gezinme-ab.bat koridor_3   (sahne koridor_1..koridor_6; ek argumanlar: --hedef kapi_3 --tohum 2)
rem Tuslar: F6 sonraki durak, F7 bastan, Shift+F7 rastgele birak, 7 duraklat, F8 LiDAR noktalari. Ayrinti: kod\SIMULASYON.md "Gezinme".
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
"%LALE_SIM_VENV%\Scripts\python.exe" fizik\gorunum3b.py --sahne %SAHNE% --senaryo ab %2 %3 %4 %5 %6
if errorlevel 1 pause
