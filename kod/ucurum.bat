@echo off
rem Ucurum sensoru gosterimi (3B pencere): robot asagi inen merdivene yurur, ESP32 ucurum denetcisi Pi'den bagimsiz durdurur.
rem Kullanim: ucurum.bat [sahne] [ek secenekler]   sahne: merdiven_17x30 (varsayilan), merdiven_15x28, merdiven_19x25, bosluk_3m, kuyu, kose
rem Ornek: ucurum.bat kose --beyin-arg v=0.39     Pencerede F7 bastan (denetci sifirlanir). Ayrinti: kod\fizik\ucurum\BENIOKU.md
cd /d "%~dp0"
if "%LALE_SIM_VENV%"=="" set "LALE_SIM_VENV=%LOCALAPPDATA%\lale-sim-venv"
if not exist "%LALE_SIM_VENV%\Scripts\python.exe" (
  echo Fizik sanal ortami yok: %LALE_SIM_VENV%
  echo Kurulum: kod\SIMULASYON.md Fizik simulasyonu bolumu.
  pause
  exit /b 2
)
set "SAHNE=%~1"
if "%SAHNE%"=="" set "SAHNE=merdiven_17x30"
set "ILK=%SAHNE:~0,1%"
if "%ILK%"=="-" (
  "%LALE_SIM_VENV%\Scripts\python.exe" fizik\gorunum3b.py --eklenti ucurum.demo --sahne ucurum_merdiven_17x30 --varyant ONERI --beyin ucurum.demo:YuruBeyni %1 %2 %3 %4 %5 %6
) else (
  "%LALE_SIM_VENV%\Scripts\python.exe" fizik\gorunum3b.py --eklenti ucurum.demo --sahne ucurum_%SAHNE% --varyant ONERI --beyin ucurum.demo:YuruBeyni %2 %3 %4 %5 %6
)
if errorlevel 1 pause
