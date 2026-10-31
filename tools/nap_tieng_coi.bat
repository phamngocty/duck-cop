@echo off
chcp 65001 >nul
title ESP32-C3 Speed FX Audio Studio - Nap Tieng Coi Xe Truc Tiep
color 0b

echo =================================================================
echo   ESP32-C3 SPEED FX AUDIO STUDIO - NAP COI XE TRUC TIEP
echo   Tu Lam Dien Tu - Flash 0x1E0000 - Web Serial 1-Click
echo =================================================================
echo.
echo [*] Dang khoi dong may chu Web Studio tai http://localhost:8765 ...
echo [*] Trinh duyet web se tu dong mo trong giay lat.
echo.
echo =================================================================
echo   HUONG DAN NAP TREN WEB:
echo   1. Chon tieng, chinh am luong va cat doan song am ung y.
echo   2. Cam cap USB Type-C tu coi xe vao may tinh.
echo   3. Bam nut [Nap Coi Xe (Web Serial)] tren thanh cong cu web.
echo   4. Chon cong COM cua coi xe va cho nap trong 3 giay!
echo =================================================================
echo.
echo [*] Giu cua so nay mo trong khi dung Web. Nhan Ctrl+C de dong.
echo.

where python >nul 2>nul
if %errorlevel% neq 0 goto :NO_PYTHON

python "%~dp0convert_audio.py"
goto :EOF

:NO_PYTHON
echo [!] May tinh chua cai dat Python de chay may chu local.
echo [*] Dang mo truc tiep giao dien Web Studio bang trinh duyet...
start "" "%~dp0index.html"
echo.
echo [!] LUU Y TRINH DUYET:
echo     Neu mo truc tiep tu file, Chrome/Edge co the chan mo cong COM.
echo     Ban co the mo ban Online qua GitHub Pages HTTPS de nap 1-click
echo     hoac cai dat Python de chay may chu local http://localhost:8765.
echo.
pause
