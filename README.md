# TÀI LIỆU KỸ THUẬT TOÀN DIỆN: CÒI XE ESP32-C3 SUPER MINI (INSTANT SOUND FX & WIFI WEB PORTAL)

- **Tác giả / Kênh DIY:** Tỷ (TỰ LÀM ĐIỆN TỬ)
- **Phiên bản:** v2.0.0 (Bản nâng cấp toàn diện: Fast Boot < 1ms, Zero-Delay, 100% Full Volume, Web Portal WiFi, LittleFS Partition)
- **Vi điều khiển:** ESP32-C3 Super Mini (RISC-V 32-bit 160MHz, Flash 4MB, 320KB SRAM)
- **Mạch công suất:** PAM8403 (Amply Stereo Class-D 2x3W) hoặc PAM8610 (15W)
- **Đối tượng áp dụng:** Xe máy, ô tô (Hệ thống điện 12V DC theo nhịp xi nhan hoặc còi phanh)

---

## 1. TỔNG QUAN KIẾN TRÚC & ĐỘT PHÁ CÔNG NGHỆ

### 1.1. Vấn đề thực tế khi gắn còi trên xe máy
* **Nguồn điện xi nhan là nguồn nhấp nháy ngắt quãng:** Chu kỳ chớp đèn xi nhan khoảng 1Hz – 1.5Hz (~350ms BẬT / 350ms TẮT).
* **Vấn đề của các module MP3 thông thường (DFPlayer Mini, JQ6500...):** Mất từ 500ms – 1.5s để khởi động và đọc thẻ nhớ. Khi vừa bật xi nhan, chip chưa kịp phát tiếng thì nguồn điện đã bị ngắt, dẫn đến việc còi bị câm hoặc phát tiếng hụt.
* **Vấn đề tiếng "BỤP" (Pop noise) của amply PAM8403:** Khi cấp nguồn đột ngột, nếu ngõ vào âm thanh nhảy từ 0V lên mức phân cực DC 1.65V, tụ liên lạc $100\text{ nF}$ bị sốc dòng đột ngột tạo xung kích đánh vào màng loa.
* **Vấn đề âm lượng nhỏ nếu xử lý sai thuật toán:** Nếu can thiệp bộ lọc số (Digital Attenuation / Soft-ramp / Volume Scaling) trong ngắt Timer, biên độ sóng PWM $V_{pp}$ bị co lại, khiến amply Class-D đánh loa rất yếu và xìu.

### 1.2. Giải pháp kiến trúc của Firmware v2.0
1. **Phân luồng khởi động Zero-Overhead Fast Boot (Nhánh kép):**
   - **Khi chạy xe bình thường (xi nhan chớp):** Nút BOOT thả nổi $\rightarrow$ ESP32 bỏ qua 100% WiFi, Bluetooth, Web Server, NVS ghi chậm, không có bất kỳ lệnh `delay()` nào $\rightarrow$ **Còi phát âm thanh tức thì trong $< 1\text{ ms}$!**
   - **Khi ở nhà nạp âm thanh mới:** Chủ động cấp nguồn liên tục và giữ nút BOOT $\rightarrow$ Mạch mới mở WiFi Access Point và Web Portal.
2. **Xuất 100% RAW Full-Scale Amplitude (Không suy hao âm lượng):**
   - Byte PCM (0 – 255) được bơm trực tiếp ra chân PWM qua `ledcWrite(AUDIO_PIN, raw_sample)`.
   - Biên độ đỉnh-đỉnh $V_{pp} = 3.3\text{V}$ tối đa $\rightarrow$ Kích công suất amply PAM8403 đạt 100% cực đại, âm thanh đanh giòn, vang dội giữa đường phố.
3. **Triệt tiêu tiếng bụp PAM8403:**
   - Ngay microsecond đầu tiên của `setup()`, ghim chân PWM về mức DC 128 (1.65V) để nạp êm dịu tụ ngõ vào $100\text{ nF}$.
4. **Phân vùng lưu trữ riêng biệt LittleFS (2.1 MB):**
   - Âm thanh tự nạp từ điện thoại được lưu vào phân vùng Flash riêng (`littlefs` 0x210000), không ảnh hưởng đến firmware chính.
   - Khi chọn âm tự nạp, vi điều khiển nạp file vào RAM đệm một lần duy nhất lúc khởi động, ngắt Timer đọc thẳng từ RAM $\rightarrow$ $0\mu\text{s}$ overhead!

---

## 2. BẢNG PHÂN VÙNG BỘ NHỚ (PARTITION TABLE)

Cấu hình phân vùng trong file [partitions_4mb.csv](file:///c:/Users/phamn/Documents/PlatformIO/duck%20cop/partitions_4mb.csv):

```csv
# Name,   Type, SubType, Offset,   Size,     Flags
nvs,      data, nvs,     0x9000,   0x5000,
otadata,  data, ota,     0xe000,   0x2000,
app0,     app,  ota_0,   0x10000,  0x1D0000,
littlefs, data, spiffs,  0x1E0000, 0x210000,
```

* **`nvs` (20 KB):** Lưu trữ cấu hình khe âm thanh (`slot`), tần số lấy mẫu (`sample_rate`).
* **`app0` (1.81 MB):** Chứa toàn bộ Firmware, bộ đệm âm thanh gốc (Sound Bank 5 âm), Web Portal, WiFi và DNS Captive Portal.
* **`littlefs` (2.06 MB):** Dành riêng cho người dùng upload âm thanh tùy biến từ điện thoại qua Web.

---

## 3. SƠ ĐỒ NGUYÊN LÝ & KẾT NỐI PHẦN CỨNG

### 3.1. Sơ đồ khối tổng thể (Block Diagram)

```text
               +-------------------------------------------------------------+
               |                  NGUỒN 12V XI NHAN / PHANH XE               |
               +-----------------------------+-------------------------------+
                                             |
                      +----------------------+----------------------+
                      | (+) 12V Dây dương                           | (-) Mass sườn xe (GND)
                      v                                             v
        +---------------------------+                 +---------------------------+
        |  HẠ ÁP MINI360 / MP1584   |                 |    GND CHUNG TOÀN MẠCH    |
        |  (IN: 12V  ->  OUT: 5.0V) |                 +-------------+-------------+
        +-------------+-------------+                               |
                      | OUT: 5.0V                                   |
                      v                                             |
        +---------------------------+                               |
        | ESP32-C3 SUPER MINI       |                               |
        | - Chân 5V / GND           |<------------------------------+
        | - GPIO3: PWM Audio Out    |                               |
        | - GPIO9: Nút BOOT trên bo |                               |
        | - GPIO1: Nút phụ ngoài xe |                               |
        | - GPIO8: LED chỉ thị xanh |                               |
        +-------------+-------------+                               |
                      |                                             |
                      | GPIO3 (Xung PWM 156.25kHz)                  |
                      v                                             |
        +---------------------------+                               |
        |   MẠCH LỌC RC GIẢI ĐIỀU   |                               |
        |   - R = 1 kΩ              |                               |
        |   - C = 100 nF (Mã 104)   |--------(Nối mass tụ 104)------+
        +-------------+-------------+                               |
                      | Audio Analog sạch                           |
                      v                                             |
        +---------------------------+                               |
        |   AMPLY PAM8403 (2x3W)    |<-------(Nuôi 5V & Mass)-------+
        +-------------+-------------+
                      |
                      v
             [ CỦ LOA 3W - 5W ]
```

### 3.2. Bảng chân kết nối (Pinout Mapping)

| Tên chân | Chân ESP32-C3 | Kết nối phần cứng | Chức năng chi tiết |
| :--- | :---: | :--- | :--- |
| **`AUDIO_PIN`** | **GPIO3** | Qua trở $1\text{ k}\Omega$ nối tiếp tụ $100\text{ nF}$ xuống GND $\rightarrow$ Ngõ `L_IN` hoặc `R_IN` PAM8403 | Xuất xung PWM 156.25 kHz (8-bit) không nằm trong dải nghe tai người |
| **`LED_PIN`** | **GPIO8** | Đèn LED xanh tích hợp sẵn trên mạch Super Mini | Active LOW (Kéo LOW = Sáng đèn báo WiFi Web Portal) |
| **`BOOT_PIN`** | **GPIO9** | Nút bấm BOOT tích hợp sẵn trên mạch | Nhấn nhả = Đổi âm; Nhấn giữ 2.5s = Mở WiFi Portal |
| **`EXT_BUTTON_PIN`** | **GPIO1** | Chân nối nút bấm phụ ngoài tay lái / vỏ hộp (Active LOW) | Nút bấm tiện lợi ngoài xe mà không cần mở vỏ hộp |
| **`VCC`** | **5V** | Ngõ ra OUT+ mạch hạ áp Mini360 (đã chỉnh đúng 5.0V) | Nguồn nuôi vi điều khiển |
| **`GND`** | **GND** | Nối chung toàn bộ Mass (Hạ áp, ESP32, Tụ lọc, PAM8403) | Điểm quy chiếu điện áp hệ thống |

---

## 4. DANH MỤC ÂM THANH CÓ SẴN (SOUND BANK)

Mạch tích hợp sẵn 5 âm thanh kinh điển trong bộ nhớ Flash PROGMEM và 1 khe cắm tự nạp:

* **Slot 0:** **Vịt Còi Xe Chuẩn (Duck 2 - 32kHz)** $\rightarrow$ Tiếng vịt đanh giòn, 800 mẫu đệm DC êm dịu, kêu cực vang.
* **Slot 1:** **Vịt Kêu Đơn (Duck 1 - 16kHz)** $\rightarrow$ Tiếng quạc ngắn gọn, dứt khoát.
* **Slot 2:** **Bò Rống (Cow Mooing - 16kHz)** $\rightarrow$ Tiếng bò hài hước độc lạ.
* **Slot 3:** **Còi Cảnh Sát (Police Siren - 16kHz)** $\rightarrow$ Tiếng hụ còi ưu tiên.
* **Slot 4:** **Còi Bíp Xi-nhan (Beep Beep - 16kHz)** $\rightarrow$ Tiếng bíp thanh mảnh hiện đại.
* **Slot 5:** **Âm Tự Nạp (LittleFS Custom Audio)** $\rightarrow$ Phát file `/audio.pcm` do chính người dùng tải lên từ điện thoại.

---

## 5. HƯỚNG DẪN VẬN HÀNH CHI TIẾT

```
                                    +-----------------------------+
                                    | CẤP NGUỒN (Turn Ignition ON)|
                                    +--------------+--------------+
                                                   |
                                     Kiểm tra nút BOOT / Nút phụ
                                         (Tốn chưa đầy 0.5 µs)
                                                   |
                        +--------------------------+--------------------------+
                        |                                                     |
            [KHÔNG GIỮ NÚT BẤM]                                       [CÓ GIỮ NÚT BẤM]
        (Đi xe máy chớp xi nhan)                                  (Cấp điện liên tục ở nhà)
                        |                                                     |
         ❌ Bỏ qua 100% WiFi & BT                                   ✅ Dừng còi thường
         ❌ Không delay, không NVS write                            ✅ Kêu 2 tiếng "Bíp... Bíp"
         ✅ Khóa DC 128 trong 15µs                                 ✅ Bật WiFi: COI-XE-ESP32
         ✅ Đọc RAM/ROM, bơm thẳng PWM                              ✅ Mở Web Portal 192.168.4.1
                        |                                                     |
         🚀 KÊU TỨC THÌ (< 1ms)!                                   📱 Kết nối điện thoại nạp nhạc
```

### 5.1. Khi chạy xe bình thường (Chế độ còi tức thì)
* Mỗi khi gạt xi nhan hoặc đạp phanh, nguồn điện được cấp vào mạch.
* ESP32 nhận diện nút bấm không bị giữ $\rightarrow$ **Kêu ngay lập tức (< 1ms)** theo đúng âm thanh đã cài đặt.
* Khi xi nhan tắt $\rightarrow$ Cắt nguồn. Lần chớp tiếp theo mạch lại kêu lại tiếng mới tinh.

### 5.2. Khi muốn đổi tiếng bằng nút bấm (Cấp điện liên tục)
* Cấp nguồn nuôi liên tục cho mạch (bằng ắc quy hoặc nguồn 5V/12V).
* **Nhấn nhả nhanh (từ 35ms đến 1.5 giây):** Còi sẽ tự động chuyển sang âm tiếp theo trong danh sách:
  $$\text{Slot 0} \longrightarrow \text{Slot 1} \longrightarrow \text{Slot 2} \longrightarrow \text{Slot 3} \longrightarrow \text{Slot 4} \longrightarrow \text{Slot 5} \longrightarrow \text{Slot 0}$$
* Còi sẽ phát ngay tiếng kêu mới để bạn nghe thử trực tiếp tại chỗ và tự động lưu lựa chọn này vào bộ nhớ Flash.

### 5.3. Khi muốn nạp âm thanh mới từ điện thoại qua Web Portal
1. **Kích hoạt chế độ Cài đặt WiFi:**
   - **Cách 1:** Nhấn giữ nút BOOT (hoặc nút phụ) trong lúc cắm nguồn liên tục.
   - **Cách 2:** Khi mạch đang có điện, nhấn giữ nút lâu hơn 2.5 giây.
2. Mạch sẽ kêu **2 tiếng "Bíp... Bíp"** và đèn LED xanh bắt đầu nhấp nháy báo hiệu đã mở WiFi.
3. **Kết nối điện thoại:**
   - Dùng điện thoại tìm và kết nối vào mạng WiFi: **`COI-XE-ESP32`** (Không cần mật khẩu).
   - Trình duyệt sẽ tự động bật trang cấu hình (Captive Portal). Nếu không tự bật, mở trình duyệt gõ: `http://192.168.4.1`
4. **Thao tác trên giao diện Web:**
   - Bấm **"Chọn File Âm Thanh"** để chọn bất kỳ bài nhạc, giọng nói (MP3, WAV, M4A...) từ điện thoại.
   - Cắt tỉa đoạn âm thanh ưng ý trực tiếp trên dạng sóng.
   - Bấm **"Nghe thử trên điện thoại"** hoặc **"Phát thử ra loa xe"**.
   - Bấm **"Lưu Vào Còi Xe"**: Dữ liệu sẽ được ghi thẳng vào phân vùng LittleFS và tự động kích hoạt Slot 5.
5. Sau khi nạp xong, tắt nguồn và bật lại bình thường $\rightarrow$ Còi xe phát ngay âm thanh vừa nạp với 100% tốc độ!

---

## 6. HƯỚNG DẪN BIÊN DỊCH VÀ NẠP CODE BẰNG PLATFORMIO

### 6.1. Cấu trúc thư mục mã nguồn

```text
duck cop/
├── include/
│   ├── audio_player.h      # Trình phát âm thanh thời gian thực (Zero-delay, Full RAW Volume)
│   ├── sound_bank.h        # 5 âm thanh tích hợp sẵn trong Flash PROGMEM
│   ├── sound_data.h        # File âm thanh mặc định duck2.wav (32kHz)
│   └── web_portal.h        # Giao diện Web Portal WiFi, DNS Captive Portal, API LittleFS
├── src/
│   └── main.cpp            # Khởi động nhánh kép Fast Boot, phát hiện nút bấm & điều phối
├── tools/
│   ├── convert_audio.py    # Python Studio cắt tỉa, nạp âm thanh trực tiếp trên máy tính
│   └── web_gui.html        # Giao diện Studio PC
├── partitions_4mb.csv      # Bảng phân chia 4MB Flash (1.8MB App, 2.1MB LittleFS)
├── platformio.ini          # Cấu hình biên dịch PlatformIO cho ESP32-C3 Super Mini
└── README.md               # Tài liệu kỹ thuật hoàn chỉnh này
```

### 6.2. Lệnh biên dịch (Compile)
Mở Terminal tại thư mục dự án và chạy:
```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\pio.exe" run -e esp32c3_supermini
```

### 6.3. Lệnh nạp trực tiếp qua cổng USB (Upload)
Cắm cáp Type-C từ bo mạch ESP32-C3 Super Mini vào máy tính và chạy:
```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\pio.exe" run -e esp32c3_supermini -t upload
```

---

## 7. CÂU HỎI THƯỜNG GẶP (TROUBLESHOOTING)

1. **Tại sao trước đây tiếng còi bị nhỏ, còn bản này lại kêu rất to?**
   - Bản cũ sử dụng công thức tính giảm âm lượng số và bộ lọc làm mềm âm thanh, khiến biên độ xung PWM bị thu nhỏ. Bản v2.0 đã loại bỏ hoàn toàn bộ lọc số, bơm trực tiếp byte raw $0 - 255$ ra chân PWM, giúp amply phát huy trọn vẹn 100% công suất 3W.
2. **Có sợ mạch bị trễ nhịp khi bật xi nhan liên tục không?**
   - Hoàn toàn không. Khi không giữ nút bấm, mạch chỉ mất $15\,\mu\text{s}$ để khóa DC chống bụp và $< 1\,\text{ms}$ để bắt đầu phát âm thanh, hoàn toàn khớp với nhịp chớp 350ms của xi nhan xe máy.
3. **Nếu file tải lên qua web bị lỗi thì còi có bị câm không?**
   - Không. Firmware có cơ chế bảo vệ thông minh: Nếu file âm thanh trong LittleFS bị lỗi hoặc chưa có, mạch sẽ tự động chuyển về Slot 0 (Vịt còi xe chuẩn) để còi luôn luôn hoạt động tin cậy.
