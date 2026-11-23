@echo off
rem Lale 3B fizik penceresi, ONERI-MAKARA varyanti (VARSAYIM): oneri firmware (kapali cevrim PI, oneri/donus-omni dali) + on iki teker
rem makarali omni (aday Nexus 127 mm, gobek + 22 makara; secilmedi). Bugunku robot DEGIL. Bugunku robot icin: simulasyon3b.bat.
rem Kure modeli (eski, daha hizli): simulasyon3b.bat oda_rampa ONERI-ADAY. Tuslar ve varyantlar: kod\SIMULASYON.md.
call "%~dp0simulasyon3b.bat" oda_rampa ONERI-MAKARA %1 %2 %3 %4
