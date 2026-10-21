@echo off
chcp 65001 >nul
title Nạp Tiếng Còi Xe ESP32-C3 - Speed FX Standalone
color 0b

echo =================================================================
echo   🦆 CÔNG CỤ NẠP ÂM THANH CÒI XE ESP32-C3 (1-CLICK NẠP NHANH)
echo   Tương thích: Flash 0x1E0000 ^| 0%% WiFi ^| Khởi động tức thì
echo   Bản quyền: Tự Làm Điện Tử
echo =================================================================
echo.

:: 1. Tự động kiểm tra file sound_bank.bin mới xuất từ trình duyệt trong Downloads
set "DL_BIN=%USERPROFILE%\Downloads\sound_bank.bin"
if exist "%DL_BIN%" (
    echo [*] Phat hien file sound_bank.bin moi tu Audio Studio trong Downloads!
    echo     Dang cap nhat vao thu muc...
    copy /y "%DL_BIN%" "%~dp0sound_bank.bin" >nul
    del "%DL_BIN%" >nul
    echo [+] Da cap nhat goi am thanh moi nhat!
    echo.
)

:: 2. Đảm bảo có thư mục sounds_input
if not exist "%~dp0sounds_input" mkdir "%~dp0sounds_input"

:: 3. Kiểm tra file sound_bank.bin
if not exist "%~dp0sound_bank.bin" (
    echo [*] Chua co sound_bank.bin, dang tu dong dong goi...
    if exist "%~dp0build_sound_bank.py" (
        python "%~dp0build_sound_bank.py" --build
    )
)

echo.
echo =================================================================
echo   ĐANG KẾT NỐI VÀ NẠP VÀO CÒI XE QUA CỔNG USB TYPE-C...
echo   (Vui lòng cắm cáp USB nối còi xe với máy tính)
echo =================================================================
echo.

:: 4. Ưu tiên nạp bằng esptool.exe độc lập (Không cần cài đặt Python)
if exist "%~dp0esptool.exe" (
    "%~dp0esptool.exe" --chip esp32c3 --baud 460800 write_flash 0x1E0000 "%~dp0sound_bank.bin"
) else (
    python "%~dp0build_sound_bank.py" --flash
)

if %errorlevel% equ 0 (
    echo.
    echo =================================================================
    echo   🎉 NẠP THÀNH CÔNG 100%! 
    echo   Bạn có thể rút cáp USB, bật khóa xe và bấm còi trải nghiệm ngay!
    echo =================================================================
) else (
    echo.
    echo =================================================================
    echo   [-] Nạp thất bại!
    echo   Gợi ý khắc phục:
    echo   1. Đảm bảo cáp USB Type-C cắm chắc chắn và có truyền dữ liệu.
    echo   2. Thử đổi sang cổng USB khác trên máy tính.
    echo =================================================================
)

echo.
echo Nhấn phím bất kỳ để thoát...
pause >nul
