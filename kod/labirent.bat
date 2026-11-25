@echo off
rem Lale labirent gosterimi (3B pencere): kesif beyni (kod\fizik\kesif, on bilgisiz) + labirent hakemi (900 s).
rem Kullanim: labirent.bat [sahne] [hiz]   ornek: labirent.bat labirent_9x9_t1 4   (varsayilan labirent_9x9_t1, hiz 4)
rem Tuslar: 6 / 9 hiz - / +, 7 duraklat, 8 kamera ust / izle, Shift+8 bastan, Shift+7 / Shift+9 onceki / sonraki labirent,
rem Enter basaridan sonra 2. tur (robotun kendi haritasiyla). Ayrinti: kod\SIMULASYON.md "Labirent sahneleri".
cd /d "%~dp0"
if "%LALE_SIM_VENV%"=="" set "LALE_SIM_VENV=%LOCALAPPDATA%\lale-sim-venv"
if not exist "%LALE_SIM_VENV%\Scripts\python.exe" (
  echo Fizik sanal ortami yok: %LALE_SIM_VENV%
  echo Kurulum: kod\SIMULASYON.md Fizik simulasyonu bolumu.
  pause
  exit /b 2
)
set "SAHNE=%~1"
if "%SAHNE%"=="" set "SAHNE=labirent_9x9_t1"
set "HIZ=%~2"
set "ILK=-"
if defined HIZ set "ILK=%HIZ:~0,1%"
if "%ILK%"=="-" (
  "%LALE_SIM_VENV%\Scripts\python.exe" fizik\gorunum3b.py --sahne %SAHNE% --beyin kesif.beyin:KesifBeyni --hakem labirent --hiz 4 %2 %3 %4 %5 %6
) else (
  "%LALE_SIM_VENV%\Scripts\python.exe" fizik\gorunum3b.py --sahne %SAHNE% --beyin kesif.beyin:KesifBeyni --hakem labirent --hiz %HIZ% %3 %4 %5 %6
)
if errorlevel 1 pause
