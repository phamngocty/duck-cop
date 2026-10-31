# 🦆 ESP32-C3 SPEED FX AUDIO STUDIO
### 🌐 Phòng Thu Âm Thanh & Nạp Còi Xe Trực Tiếp 1-Click (Web Serial)

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Demo-00f0aa?style=for-the-badge&logo=github)](https://phamngocty.github.io/duck-cop/)
[![Microcontroller](https://img.shields.io/badge/MCU-ESP32--C3%20Super%20Mini-00d2ff?style=for-the-badge&logo=espressif)](https://www.espressif.com/)
[![Web Serial](https://img.shields.io/badge/Web%20Serial%20API-Chrome%20%2F%20Edge%20%2F%20Android-ffb834?style=for-the-badge&logo=googlechrome)](https://developer.mozilla.org/en-US/docs/Web/API/Web_Serial_API)
[![Audio Power](https://img.shields.io/badge/Amply-PAM8403%20%2F%20PAM8610-ff4772?style=for-the-badge)](https://en.wikipedia.org/wiki/Class-D_amplifier)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

> **Kênh sáng tạo & Bản quyền:** [TỰ LÀM ĐIỆN TỬ](https://www.youtube.com/) (Tác giả: **Tỷ**)  
> **Phiên bản:** v2.0.0 (Fast Boot < 1ms, Zero-Delay, 100% Full Volume, Web Serial 1-Click, LittleFS Partition 0x1E0000)

---

## 📖 1. TỔNG QUAN DỰ ÁN (TL;DR)

**ESP32-C3 Speed FX Audio Studio** là giải pháp phần mềm và phần cứng toàn diện biến vi điều khiển **ESP32-C3 Super Mini** kết hợp mạch khuếch đại **PAM8403 (2x3W)** thành một chiếc còi xe máy thông minh, siêu tốc và độc đáo:
- **Kêu tức thì trong $< 1\text{ ms}$:** Khớp trọn vẹn với chu kỳ chớp ngắt quãng của rơ-le xi nhan xe máy (~350ms BẬT / 350ms TẮT), không bao giờ bị câm hoặc hụt tiếng như các module MP3 truyền thống (DFPlayer Mini, JQ6500).
- **Âm lượng cực đại 100%:** Bơm trực tiếp dữ liệu RAW PCM 8-bit ra PWM với biên độ đỉnh-đỉnh $V_{pp} = 3.3\text{V}$, âm thanh đanh giòn, vang xa khắp đường phố.
- **Triệt tiêu hoàn toàn tiếng "BỤP":** Khóa mức phân cực DC 128 (1.65V) ngay vi-giây đầu tiên, bảo vệ củ loa tuyệt đối.
- **Nạp âm thanh 1-Click qua Web Serial:** Người dùng chỉ cần vào trang web GitHub Pages bằng trình duyệt Chrome/Edge (trên máy tính hoặc điện thoại Android cắm cáp OTG Type-C), cắt nhạc và bấm nạp trực tiếp vào còi xe trong 3 giây mà **không cần cài đặt Python, driver hay phần mềm phức tạp nào!**

---

## 🚀 2. TRẢI NGHIỆM TRỰC TUYẾN TRÊN GITHUB PAGES

Truy cập ngay phòng thu âm thanh trực tuyến:  
👉 **[ESP32-C3 Audio Studio Online](https://phamngocty.github.io/duck-cop/)** *(Thay bằng URL repo của bạn)*

### Thao tác 3 bước đơn giản:
1. **Chọn âm thanh:** Chọn các mẫu có sẵn trong thư viện độc quyền (Vịt còi xe, Vịt kêu đơn, Bò rống, Còi cảnh sát...) hoặc bấm tải file MP3/WAV yêu thích từ thiết bị.
2. **Cắt nhạc & Tùy chỉnh:** Kéo chọn đoạn sóng âm ưng ý, kéo thanh âm lượng (100% - 250%) và bấm nghe thử trực tiếp.
3. **Nạp vào còi xe:** Cắm cáp USB Type-C từ còi xe vào máy tính hoặc điện thoại Android (qua đầu chuyển OTG) $\rightarrow$ Bấm nút **`⚡ Nạp Còi Xe (Web Serial)`** ở góc trên $\rightarrow$ Chọn cổng COM $\rightarrow$ Xong trong 3 giây!

---

## ⚙️ 3. ĐỘT PHÁ CÔNG NGHỆ & THÔNG SỐ KỸ THUẬT

| Thông số | Giá trị kỹ thuật | Ý nghĩa thực tế |
| :--- | :--- | :--- |
| **Vi điều khiển** | ESP32-C3 Super Mini (RISC-V 160MHz) | Kích thước siêu nhỏ gọn, dễ giấu vào dàn áo xe máy |
| **Tốc độ khởi động (Boot Time)** | **$< 1\text{ ms}$** (Zero-Overhead Fast Boot) | Không có delay, kêu ngay microsecond đầu tiên khi có điện |
| **Tần số sóng mang PWM** | **156.25 kHz** (8-bit LEDC) | Vượt xa ngưỡng nghe tai người (20Hz - 20kHz), âm thanh sạch |
| **Mạch lọc giải điều chế** | Mạch lọc RC Low-Pass: $R = 1\text{ k}\Omega$, $C = 100\text{ nF}$ (104) | Triệt tiêu triệt để sóng mang PWM, tái tạo sóng âm analog êm dịu |
| **Mạch công suất âm thanh** | PAM8403 (Stereo Class-D 2x3W) hoặc PAM8610 (15W) | Hiệu suất cao > 90%, không tỏa nhiệt, tiếng còi to rõ |
| **Điện áp hoạt động** | 12V DC qua mạch hạ áp Mini360 / MP1584 hạ về 5.0V | Hoạt động an toàn với hệ thống điện ắc quy xe máy/ô tô |
| **Bộ nhớ Flash nạp âm thanh** | Phân vùng `littlefs` tại offset `0x1E0000` (dung lượng 2.1 MB) | Nạp âm thanh độc lập mà không ảnh hưởng đến firmware vi điều khiển |

---

## 🔌 4. SƠ ĐỒ ĐẤU DÂY & KẾT NỐI PHẦN CỨNG

### 4.1. Sơ đồ khối nguyên lý

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

### 4.2. Bảng chân kết nối (Pinout Mapping)

| Tên chân | Chân ESP32-C3 | Kết nối phần cứng | Chức năng chi tiết |
| :--- | :---: | :--- | :--- |
| **`AUDIO_PIN`** | **GPIO3** | Nối qua trở $1\text{ k}\Omega$ + tụ $100\text{ nF}$ xuống GND $\rightarrow$ Ngõ `L_IN` PAM8403 | Xuất tín hiệu âm thanh PWM 156.25 kHz (8-bit) |
| **`LED_PIN`** | **GPIO8** | Đèn LED xanh tích hợp sẵn trên mạch Super Mini | Active LOW (Sáng đèn khi còi phát âm thanh) |
| **`BOOT_PIN`** | **GPIO9** | Nút bấm BOOT trên mạch | Nhấn nhả = Đổi âm; Nhấn giữ = Mở cài đặt |
| **`EXT_BUTTON_PIN`**| **GPIO1** | Nối dây ra nút bấm phụ ngoài tay lái xe (Active LOW) | Bấm đổi tiếng tiện lợi trực tiếp trên ghi-đông xe |
| **`5V`** | **5V** | Nối với ngõ ra 5.0V của mạch hạ áp Mini360 | Nguồn nuôi vi điều khiển và mạch công suất |
| **`GND`** | **GND** | Nối chung Mass toàn mạch | Điểm quy chiếu điện áp hệ thống |

---

## 🎵 5. DANH MỤC ÂM THANH MẶC ĐỊNH (SOUND BANK)

Mạch hỗ trợ lưu trữ nhiều tiếng còi độc lập:
- 🦆 **Slot 0:** **Vịt Còi Xe Chuẩn (Duck 2 - 32kHz)** $\rightarrow$ Tiếng vịt đanh giòn, 800 mẫu đệm DC êm dịu, kêu cực vang dội.
- 🦆 **Slot 1:** **Vịt Kêu Đơn (Duck 1 - 16kHz)** $\rightarrow$ Tiếng quạc ngắn gọn, dứt khoát 1 nhịp.
- 🐮 **Slot 2:** **Bò Rống (Cow Mooing - 16kHz)** $\rightarrow$ Tiếng bò kêu hài hước, độc lạ và trầm ấm.
- 🚨 **Slot 3:** **Còi Cảnh Sát (Police Siren - 16kHz)** $\rightarrow$ Tiếng hụ còi ưu tiên dồn dập, mạnh mẽ.
- 🔊 **Slot 4:** **Còi Bíp Xi-nhan (Beep Beep - 16kHz)** $\rightarrow$ Tiếng bíp kép thanh mảnh, hiện đại.
- 🎵 **Slot 5:** **Âm Tự Nạp (LittleFS Custom Audio)** $\rightarrow$ Phát file âm thanh riêng do chính bạn tải lên qua Web Studio.

---

## 🛠️ 6. HƯỚNG DẪN SỬ DỤNG CHO NGƯỜI DÙNG

### Cách 1: Nạp trực tuyến 1-Click trên Web (Khuyên dùng)
1. Truy cập trang web GitHub Pages của dự án trên trình duyệt Chrome, Edge, Cốc Cốc hoặc Chrome trên Android.
2. Tải bài hát hoặc chọn tiếng còi mong muốn, kéo chuột cắt đoạn hay nhất.
3. Cắm cáp USB Type-C từ còi xe vào máy tính hoặc cắm đầu OTG vào điện thoại Android.
4. Bấm nút **`⚡ Nạp Còi Xe (Web Serial)`** $\rightarrow$ Chọn cổng COM kết nối $\rightarrow$ Mạch tự nạp và khởi động lại sau 3 giây!

### Cách 2: Đổi tiếng còi trực tiếp trên xe máy (Không cần máy tính)
1. Bật khóa xe máy (cấp điện liên tục cho mạch còi).
2. Nhấn nhả nhanh nút bấm phụ trên tay lái (nhấn dưới 1.5 giây rồi thả ra).
3. Còi sẽ nhảy ngay sang tiếng tiếp theo:
   $$\text{Slot 0} \longrightarrow \text{Slot 1} \longrightarrow \text{Slot 2} \longrightarrow \text{Slot 3} \longrightarrow \text{Slot 4} \longrightarrow \text{Slot 5} \longrightarrow \text{Slot 0}$$
4. Còi phát thử ngay tiếng mới tại chỗ và tự động lưu nhớ vĩnh viễn vào bộ nhớ RTC SRAM / NVS Flash (tắt khóa xe bật lại vẫn kêu đúng tiếng đã chọn).

### Cách 3: Nạp offline trên máy tính Windows (Khi không có mạng)
1. Tải toàn bộ thư mục repo này về máy tính.
2. Cắm cáp USB Type-C từ còi xe vào máy tính.
3. Nhấp đúp chuột vào file **`nap_tieng_coi.bat`** để khởi chạy Audio Studio cục bộ qua cổng `http://localhost:8765` và nạp âm thanh offline.

---

## ❓ 7. CÂU HỎI THƯỜNG GẶP (TROUBLESHOOTING)

1. **Tại sao còi lại kêu to rõ hơn hẳn các mạch còi thông thường?**
   - Phiên bản v2.0 đã loại bỏ hoàn toàn các thuật toán giảm biên độ số và bộ lọc làm mềm âm thanh trong ngắt Timer. Byte PCM $0 - 255$ được bơm trực tiếp ra chân PWM với biên độ đỉnh-đỉnh $V_{pp} = 3.3\text{V}$, giúp amply Class-D khai thác trọn vẹn 100% công suất 3W.
2. **Còi có bị câm nếu file nạp vào bị lỗi không?**
   - Hoàn toàn không. Firmware có cơ chế tự kiểm tra lỗi thông minh: Nếu file trong phân vùng Flash bị lỗi hoặc chưa có, mạch sẽ tự động nhảy về Slot 0 (Vịt còi xe chuẩn) để còi luôn luôn hoạt động bình thường trên đường.
3. **Mạch có chống nước không?**
   - Khi lắp đặt lên xe máy, bạn cần đặt mạch vi điều khiển và mạch hạ áp vào hộp nhựa bảo vệ chống nước, dán keo nến hoặc silicon kín các đầu dây ra vào.

---

## 📞 LIÊN HỆ & BẢN QUYỀN

- **Tác giả:** Phạm Ngọc Tỷ
- **Kênh YouTube:** [TỰ LÀM ĐIỆN TỬ](https://www.youtube.com/)
- **Kênh TikTok:** [@tulamdientu](https://www.tiktok.com/)
- Mọi đóng góp, báo lỗi hoặc yêu cầu tính năng mới xin vui lòng tạo [Issue](https://github.com/phamngocty/duck-cop/issues) hoặc gửi Pull Request!

---
*Chúc bạn có những trải nghiệm chế tạo thú vị và độc đáo cùng chiếc còi xe thông minh ESP32-C3!*

