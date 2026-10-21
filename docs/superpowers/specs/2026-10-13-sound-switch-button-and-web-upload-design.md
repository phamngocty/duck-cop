# Bản Thiết Kế Hệ Thống: Còi Xe ESP32-C3 Đổi Âm Thanh Qua Nút & Nạp Âm Thanh Qua Web (LittleFS)

- **Ngày tạo:** 13/10/2026
- **Thiết bị:** ESP32-C3 Super Mini (RISC-V 160MHz, Flash 4MB)
- **Mạch công suất:** PAM8403 (Amply Stereo 2x3W Class-D)
- **Mục tiêu:** Còi xe phản hồi tức thì (< 2ms khi cấp nguồn), đổi âm thanh qua nút bấm, nạp âm thanh mới từ điện thoại qua Web Portal vào phân vùng LittleFS riêng mà không cần nạp code bằng PC.

---

## 1. Yêu Cầu & Giới Hạn Kỹ Thuật

1. **Tốc độ phản hồi tức thì (Instant Audio FX):**
   - Khi bật khóa xe thông thường, còi phải phát ra tiếng ngay lập tức (< 2ms) mà không bị độ trễ do khởi động WiFi hay hệ thống mạng.
   - Triệt tiêu 100% tiếng bụp (DC pop noise) của amply PAM8403 khi cấp nguồn bằng cách khóa mức DC 128 (1.65V) trong vòng < 20µs.
2. **Cơ chế đổi âm thanh qua nút (Button Switching):**
   - Hỗ trợ nút BOOT (GPIO9) tích hợp trên bo mạch và nút phụ (GPIO1) câu dây ra tay lái/vỏ hộp.
   - Nhấn nhả nhanh (< 1.5s): Chuyển tuần tự qua các âm thanh trong Sound Bank (Slot 0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 0), còi kêu thử ngay 1 lần và lưu lại vào NVS Preferences.
   - Nhấn giữ lâu (> 2.5s) hoặc giữ nút khi bật khóa xe: Kêu 2 tiếng "Bíp... Bíp" và chuyển sang Chế độ Web Portal.
3. **Nạp âm thanh qua Web vào phân vùng riêng (Web Upload via LittleFS):**
   - Phân vùng LittleFS riêng biệt (~2.1MB) không ảnh hưởng tới code chính (Firmware App0 1.8MB).
   - Trình duyệt điện thoại tự giải mã MP3/WAV/M4A thành 8-bit Unsigned PCM (16kHz hoặc 32kHz) qua Web Audio API.
   - Truyền stream mảng byte PCM vào LittleFS `/audio.pcm` trên ESP32.
   - Có nút nghe thử trên điện thoại và phát thử ra loa xe trước khi lưu.

---

## 2. Phân Bổ Bộ Nhớ & Bảng Phân Vùng (Partition Table)

File cấu hình phân vùng `partitions_4mb.csv`:
```csv
# Name,   Type, SubType, Offset,  Size, Flags
nvs,      data, nvs,     0x9000,  0x5000,
otadata,  data, ota,     0xe000,  0x2000,
app0,     app,  ota_0,   0x10000, 0x1D0000,
littlefs, data, spiffs,  0x1E0000,0x210000,
```
- `app0`: 1.8125 MB (đủ cho Firmware kèm WiFi stack, WebServer, DNS Captive Portal, Sound Bank).
- `littlefs`: 2.0625 MB (dành riêng cho lưu trữ âm thanh tùy biến nạp từ Web).

---

## 3. Kiến Trúc Phần Cứng (Pinout)

| Tên chân | GPIO | Chức năng | Ghi chú |
|---|---|---|---|
| `AUDIO_PIN` | GPIO3 | Xuất LEDC PWM 156.25kHz 8-bit | Nối qua mạch lọc RC ($1\text{k}\Omega + 100\text{nF}$) vào ngõ Audio L/R PAM8403 |
| `LED_PIN` | GPIO8 | Đèn LED xanh tích hợp | Active LOW (Sáng khi LOW, Tắt khi HIGH) |
| `BOOT_PIN` | GPIO9 | Nút BOOT trên mạch | Active LOW (Pull-up nội bộ) |
| `EXT_BUTTON_PIN` | GPIO1 | Nút bấm phụ ngoài xe | Active LOW (Pull-up nội bộ) |

---

## 4. Danh Mục Âm Thanh (Sound Bank)

- **Slot 0:** Vịt Còi Xe Chuẩn (Duck 2 - 32kHz, đệm êm 128)
- **Slot 1:** Vịt Kêu Đơn (Duck 1 - 16kHz)
- **Slot 2:** Bò Rống (Cow Mooing - 16kHz)
- **Slot 3:** Còi Cảnh Sát (Siren - 16kHz)
- **Slot 4:** Còi Bíp Xi-nhan (Beep Beep - 16kHz)
- **Slot 5:** Âm Thanh Tự Nạp (Custom Audio từ LittleFS `/audio.pcm`)

---

## 5. Quy Trình Vận Hành (State Machine)

### Chế độ 1: Còi xe bình thường (Normal Mode)
1. Cấp nguồn: Cấu hình LEDC PWM và ghim mức 128 trong < 20µs.
2. Kiểm tra nút bấm: Nếu không giữ nút, tắt toàn bộ WiFi/BT (`WiFi.mode(WIFI_OFF)`).
3. Đọc NVS để lấy `slot` đã lưu. Nếu là Slot 5, load file `/audio.pcm` từ LittleFS vào RAM buffer.
4. Kích hoạt Hardware Timer ISR phát âm thanh ngay lập tức.
5. Vòng lặp `loop()` giám sát nút bấm:
   - Nhấn nhả nhanh (< 1.5s): Đổi slot, phát thử, lưu NVS.
   - Nhấn giữ lâu (> 2.5s): Gọi `enterSettingMode()`.

### Chế độ 2: Cài đặt Web Portal (Setting Mode)
1. Kêu 2 tiếng "Bíp... Bíp" tần số 1800Hz và 2400Hz.
2. Nhấp nháy đèn LED GPIO8 chu kỳ 120ms.
3. Kích hoạt WiFi AP: `COI-XE-ESP32` (Không mật khẩu, IP: `192.168.4.1`).
4. Khởi chạy DNSServer (Captive Portal) và WebServer phục vụ trang HTML/JS.
5. Người dùng truy cập Web:
   - Chọn âm trong Sound Bank có sẵn để đổi.
   - Hoặc tải file nhạc bất kỳ từ điện thoại, chuyển đổi trên trình duyệt sang 8-bit PCM.
   - Nghe thử trên điện thoại hoặc phát thử trực tiếp ra loa xe.
   - Bấm lưu: Ghi vào LittleFS `/audio.pcm` và tự động chọn Slot 5.

---

## 6. Tiêu Chí Nghiệm Thu (Verification Checklist)

- [ ] Biên dịch thành công với PlatformIO môi trường `esp32c3_supermini`.
- [ ] Khởi động tức thì < 2ms, không có tiếng bụp loa PAM8403.
- [ ] Bấm nhả nút đổi âm thanh mượt mà giữa 6 slot và lưu trạng thái vào NVS.
- [ ] Nhấn giữ nút vào được chế độ WiFi AP `COI-XE-ESP32`.
- [ ] Truy cập trang web `192.168.4.1`, nạp file nhạc mới vào LittleFS thành công.
- [ ] Tắt nguồn bật lại, âm thanh mới nạp phát ra tức thì.
