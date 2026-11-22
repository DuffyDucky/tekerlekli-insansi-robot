@echo off
rem Lale 3B fizik penceresi, ONERI varyanti (VARSAYIM): oneri firmware (kapali cevrim PI, oneri/donus-omni dali) + on iki teker omni.
rem Bugunku robot DEGIL. Bugunku robot icin: simulasyon3b.bat. Tuslar ve varyantlar: kod\SIMULASYON.md.
call "%~dp0simulasyon3b.bat" oda_rampa ONERI %1 %2 %3 %4
