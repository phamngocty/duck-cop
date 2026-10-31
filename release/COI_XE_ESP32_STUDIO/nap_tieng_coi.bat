@echo off
chcp 65001 >nul
title ESP32-C3 Speed FX Audio Studio - Nạp Tiếng Còi Xe Trực Tiếp
color 0b

echo =================================================================
echo   ESP32-C3 SPEED FX AUDIO STUDIO - NẠP CÒI XE TRỰC TIẾP 1-CLICK
echo   Tự Làm Điện Tử - Flash Offset: 0x1E0000 - Web Serial API
echo =================================================================
echo.
echo [*] Link Web nạp trực tuyến (Không cần mở file này):
echo     https://phamngocty.github.io/duck-cop/
echo.
echo [*] Đang khởi động máy chủ Web Studio tại http://localhost:8765 ...
echo [*] Trình duyệt web sẽ tự động mở trong giây lát.
echo.
echo =================================================================
echo   HƯỚNG DẪN NẠP TIẾNG CÒI:
echo   1. Chọn tiếng, chỉnh âm lượng và cắt đoạn sóng âm ưng ý.
echo   2. Cắm cáp USB Type-C từ còi xe vào máy tính.
echo   3. Bấm nút [⚡ Nạp Còi Xe (Web Serial)] trên thanh công cụ web.
echo   4. Chọn cổng COM của còi xe và chờ nạp trong 3 giây!
echo =================================================================
echo.
echo [*] Giữ cửa sổ này mở trong khi dùng Web. Nhấn Ctrl+C để đóng.
echo.

where python >nul 2>nul
if %errorlevel% neq 0 goto :NO_PYTHON

python "%~dp0convert_audio.py"
goto :EOF

:NO_PYTHON
echo [!] Máy tính chưa cài đặt Python để chạy máy chủ local.
echo [*] Đang mở trực tiếp giao diện Web Studio bằng trình duyệt...
start "" "%~dp0index.html"
echo.
echo [!] LƯU Ý TRÌNH DUYỆT:
echo     Nếu mở trực tiếp file offline, Chrome/Edge có thể chặn mở cổng COM.
echo     Bạn nên mở bản Online chính thức qua link HTTPS để nạp 1-click:
echo     👉 https://phamngocty.github.io/duck-cop/
echo.
pause
