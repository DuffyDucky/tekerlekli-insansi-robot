@echo off
rem Lale 3B fizik penceresi (Y0f). Sahne: oda_rampa (varsayilan) ya da rampa_parkuru. Tuslar: kod\SIMULASYON.md.
rem Ikinci arguman V ile baslarsa donus varyanti: V0 bugunku robot (varsayilan); V1 V2 V3 V4 V1+V3 V2+V3 VARSAYIM. Ornek: simulasyon3b.bat oda_rampa V3
rem Sanal ortam: LALE_SIM_VENV (yoksa %%LOCALAPPDATA%%\lale-sim-venv). Kurulum: kod\SIMULASYON.md "Fizik simulasyonu (Y0f)".
cd /d "%~dp0"
if "%LALE_SIM_VENV%"=="" set "LALE_SIM_VENV=%LOCALAPPDATA%\lale-sim-venv"
if not exist "%LALE_SIM_VENV%\Scripts\python.exe" (
  echo Fizik sanal ortami yok: %LALE_SIM_VENV%
  echo Kurulum: kod\SIMULASYON.md Fizik simulasyonu bolumu. 2B simulasyon icin: simulasyon.bat
  pause
  exit /b 2
)
set "SAHNE=%~1"
if "%SAHNE%"=="" set "SAHNE=oda_rampa"
set "VARYANT=%~2"
if /i "%VARYANT:~0,1%"=="V" (
  "%LALE_SIM_VENV%\Scripts\python.exe" fizik\gorunum3b.py --sahne %SAHNE% --varyant "%VARYANT%" %3 %4 %5 %6
) else (
  "%LALE_SIM_VENV%\Scripts\python.exe" fizik\gorunum3b.py --sahne %SAHNE% %2 %3 %4 %5 %6
)
if errorlevel 1 pause
