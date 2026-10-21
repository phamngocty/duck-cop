# Tài Liệu Kỹ Thuật: Hướng Dẫn Vận Hành & Nạp Âm Thanh Còi Xe ESP32-C3 Super Mini

## 1. Tóm Tắt Nhanh Các Chế Độ Hoạt Động ("Kêu Trước - Đếm Giờ Sau")

| Nhu Cầu | Thao Tác | Phản Hồi Của Mạch |
| :--- | :--- | :--- |
| **Đi xe máy (Xi nhan / Còi phanh)** | Bật khóa xe / Gạt xi nhan bình thường. | **Kêu tức thì (< 1ms)** từ RAM/ROM, 100% công suất cực đại, không tiếng bụp, tắt sạch WiFi/BT. |
| **Vào Web Portal Đổi Tiếng / Nạp Nhạc bằng Remote hoặc Phanh** | Bấm giữ nút tìm xe trên remote (hoặc đè giữ phanh / cắm sạc ở nhà) **liên tục $\ge 5$ giây**. | **Giây đầu tiên:** Kêu 1 tiếng còi quen thuộc.<br>**Đến giây thứ 5:** Còi phát **2 tiếng "Bíp... Bíp"**, LED xanh nhấp nháy, tự động mở WiFi **`COI-XE-ESP32`** (IP: `192.168.4.1`). |
| **Đổi tiếng nhanh bằng nút bấm** | Khi mạch có điện, **nhấn nhả nhanh nút BOOT** (hoặc nút phụ) trong vòng 0.1s - 1.5s. | Còi phát ngay tiếng mới để nghe thử và tự động lưu vào bộ nhớ Flash. |

---

## 2. Danh Sách 6 Khe Âm Thanh (Sound Bank)

Mỗi lần nhấn nhả nhanh nút bấm (hoặc chọn trên Web), mạch sẽ chuyển tuần tự:
1. **Slot 0:** Vịt Còi Xe Chuẩn (Duck 2 - 16kHz) - Tiếng vịt giòn giã kinh điển, 160 mẫu đệm DC êm ái.
2. **Slot 1:** Vịt Kêu Đơn (Duck 1 - 16kHz) - Quạc ngắn gọn dứt khoát.
3. **Slot 2:** Vịt Còi Đôi (Double Quack - 16kHz) - Quạc quạc đôi vui tai.
4. **Slot 3:** Bò Rống (Cow Mooing - 16kHz) - Tiếng bò hài hước.
5. **Slot 4:** Còi Cảnh Sát (Police Siren - 16kHz) - Hụ còi ưu tiên.
6. **Slot 5:** Âm Tự Nạp (LittleFS Custom Audio) - Âm thanh do bạn tự cắt tỉa và nạp từ điện thoại.

---

## 3. Các Bước Nạp & Cắt Tỉa Âm Thanh Từ Điện Thoại Qua Web Studio

1. **Mở WiFi Còi Xe:**
   - **Cách 1 (Trên xe):** Bấm giữ nút tìm xe trên remote (hoặc đè phanh) liên tục **5 giây** cho đến khi nghe **2 tiếng Bíp... Bíp**.
   - **Cách 2 (Ở nhà):** Cấp nguồn liên tục 5V/12V, sau 5 giây mạch tự động phát WiFi (hoặc bấm giữ nút BOOT 2.5s).
2. **Kết nối điện thoại:**
   - Vào cài đặt WiFi trên điện thoại, kết nối vào mạng: **`COI-XE-ESP32`** (Không mật khẩu).
   - Trình duyệt sẽ tự động bật trang cấu hình Captive Portal. Nếu không tự bật, mở Safari/Chrome gõ: `http://192.168.4.1`
3. **Sử dụng Studio chuyên nghiệp trên Web:**
   - Giao diện Web tích hợp đầy đủ công cụ Audio Studio: hiển thị dạng sóng Waveform, thanh kéo cắt tỉa (Trim Handles), tăng giảm tốc độ phát.
   - Bấm **"Nghe thử"** trên điện thoại hoặc **"Phát thử ra loa xe"** (`/api/test_beep`).
   - Bấm **"Lưu Vào Còi Xe"**: Hệ thống sẽ chuyển đổi thành 8-bit PCM và nạp thẳng vào phân vùng riêng LittleFS (2.1 MB) của ESP32-C3, tự động kích hoạt Slot 5.
4. Tắt nguồn, bật lại xi nhan trên xe $\rightarrow$ Còi xe phát ngay âm thanh mới cực vang và tức thì!
