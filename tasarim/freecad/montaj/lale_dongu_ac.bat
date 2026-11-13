@echo off
rem Lale montaj hareket dongusu: cift tikla -> FreeCAD 1.1 acilir, robot-montaj.FCStd yuklenir, lale_dongu.FCMacro baslar.
rem Durdurmak: FreeCAD'de makroyu ikinci kez calistir (Makro > Son makrolar) ya da Python konsolunda App._lale_dongu.durdur()
rem Yolda "u" (Masaustu) gibi ASCII disi harf var: FreeCAD bu yolu argumanla alinca cokebiliyor. Bu yuzden makro yolu ortam
rem degiskeniyle (UTF-16, kod sayfasindan bagimsiz) verilir; FreeCAD'e yalniz %TEMP% altindaki ASCII bir baslatici gecilir.
chcp 65001 >nul
setlocal
set "LALE_MONTAJ_DIZIN=%~dp0"
set "LALE_MAKRO=%~dp0lale_dongu.FCMacro"
set "FC=%LOCALAPPDATA%\Programs\FreeCAD 1.1\bin\freecad.exe"
if not exist "%FC%" (
  echo FreeCAD 1.1 bulunamadi: "%FC%"
  pause
  exit /b 1
)
if not exist "%LALE_MAKRO%" (
  echo Makro bulunamadi: "%LALE_MAKRO%"
  pause
  exit /b 1
)
set "BASLAT=%TEMP%\lale_dongu_baslat.py"
> "%BASLAT%" echo # lale_dongu_ac.bat tarafindan yazildi: LALE_MAKRO ortam degiskenindeki makroyu GUI hazir olunca calistirir
>>"%BASLAT%" echo import os
>>"%BASLAT%" echo from PySide import QtCore
>>"%BASLAT%" echo _p = os.environ["LALE_MAKRO"]
>>"%BASLAT%" echo def _lale_calistir():
>>"%BASLAT%" echo     exec(compile(open(_p, encoding="utf-8").read(), _p, "exec"), {"__file__": _p, "__name__": "__main__"})
>>"%BASLAT%" echo QtCore.QTimer.singleShot(1500, _lale_calistir)
start "" "%FC%" "%BASLAT%"
endlocal
