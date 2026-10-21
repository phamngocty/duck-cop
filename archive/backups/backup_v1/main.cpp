/**
 * ============================================================================
 * DỰ ÁN: CÒI XE ESP32-C3 SUPER MINI (INSTANT SOUND FX & AUTO WEB PORTAL >=5S)
 * Tác giả: Tỷ (TỰ LÀM ĐIỆN TỬ)
 * Vi điều khiển: ESP32-C3 Super Mini (RISC-V 160MHz, Flash 4MB)
 * Mạch công suất: PAM8403 / PAM8610 (Class-D)
 * Chân xuất âm thanh: GPIO3 (Qua mạch lọc RC 1kΩ + 104 vào ngõ Audio IN)
 * Nút cấu hình: Nút BOOT (GPIO9) trên bo mạch & Nút phụ ngoài xe (GPIO1)
 * Đèn báo trạng thái: LED Xanh (GPIO8) tích hợp trên mạch (Active LOW)
 * ============================================================================
 *
 * KIẾN TRÚC THỰC THI "KÊU TRƯỚC - ĐẾM GIỜ SAU" (EXECUTE FIRST, CHECK LATER):
 * 1. Chế độ chạy xe bình thường (Gạt xi nhan / Nhấp phanh):
 *    - Khởi động tức thì < 1ms từ RAM/ROM, TẮT SẠCH WiFi/Bluetooth ngay từ đầu.
 *    - Khóa DC 128 (1.65V) trong vòng 15µs để triệt tiêu hoàn toàn tiếng BỤP loa.
 *    - Xuất thẳng 100% RAW công suất cực đại (không bóp volume số).
 *    - Xi nhan tắt sau ~350ms -> Mạch ngắt nguồn, kết thúc chu kỳ dứt khoát.
 *
 * 2. Tự động chuyển sang WiFi Web Portal khi giữ điện >= 5 giây:
 *    - Khi bấm giữ nút tìm xe trên remote (hoặc đè phanh / cắm nguồn liên tục ở nhà):
 *      + Giây đầu tiên: Vẫn phát ngay 1 tiếng còi quen thuộc.
 *      + Sau 5 giây nguồn điện vẫn duy trì: Kêu 2 tiếng "Bíp... Bíp", LED xanh nhấp nháy,
 *        tự động bật WiFi Access Point "COI-XE-ESP32" (IP: 192.168.4.1).
 *      + Mở điện thoại kết nối vào Web để nghe thử, cắt tỉa và nạp âm thanh vào LittleFS.
 *
 * 3. Chế độ đổi tiếng nhanh bằng nút bấm (khi có điện):
 *    - Nhấn nhả nhanh nút BOOT hoặc nút phụ (35ms - 1.5s): Đổi ngay sang âm tiếp theo
 *      trong Sound Bank, còi kêu thử trực tiếp và tự động lưu Flash.
 */

#include <Arduino.h>
#include <WiFi.h>
#include "audio_player.h"
#include "web_portal.h"

#define CONFIG_HOLD_TIME_MS   5000U // Cấp điện liên tục >= 5 giây để kích hoạt WiFi

static unsigned long powerOnTime = 0;
static bool is_setting_mode = false;
static WebPortal webPortal;

// Kích hoạt chế độ Cài đặt WiFi (Setting Mode)
static void enterSettingMode() {
    if (is_setting_mode) return;
    is_setting_mode = true;

    // Dừng phát âm thanh còi thông thường
    AudioPlayer::instance().stop();

    // Kêu 2 tiếng "Bíp... Bíp" vang rõ báo hiệu đã vào WiFi Web Portal
    AudioPlayer::instance().playBeep(1800, 90);
    delay(100);
    AudioPlayer::instance().playBeep(2400, 140);

    // Bật nhấp nháy đèn LED và phát WiFi Access Point "COI-XE-ESP32"
    webPortal.start();
}

// Xử lý nút bấm khi có điện:
// - Nhấn nhả nhanh (35ms - 1.5s): Đổi tiếng còi tiếp theo trong Sound Bank
// - Nhấn giữ lâu (>= 2.5s): Chuyển ngay sang chế độ WiFi Setting Mode
static void checkSoundSwitchButton() {
    static unsigned long press_start = 0;
    static bool is_pressed = false;
    static bool long_press_done = false;

    bool btn_down = (digitalRead(BOOT_PIN) == LOW) || (digitalRead(EXT_BUTTON_PIN) == LOW);

    if (btn_down) {
        if (!is_pressed) {
            is_pressed = true;
            press_start = millis();
            long_press_done = false;
        } else {
            if (!long_press_done && (millis() - press_start >= 2500)) {
                long_press_done = true;
                enterSettingMode();
            }
        }
    } else {
        if (is_pressed) {
            unsigned long duration = millis() - press_start;
            is_pressed = false;
            if (!long_press_done && duration >= 35 && duration < 2000) {
                AudioPlayer::instance().nextSlot();
            }
        }
    }
}

void setup() {
    // 1. KHỞI TẠO SIÊU TỐC & PHÁT ÂM THANH NGAY LẬP TỨC (< 1ms từ Flash ROM)
    // - Khóa DC 128 (1.65V) chống bụp PAM8403 trong < 15µs
    // - Bơm mẫu âm thanh trực tiếp 100% RAW công suất cực đại
    // - Tuyệt đối không bật/tắt WiFi ở setup để tránh trễ boot
    AudioPlayer::instance().initFast();

    // 2. GHI NHẬN MỐC THỜI GIAN CẤP ĐIỆN ĐỂ BẮT ĐẦU ĐẾM GIỜ NGẦM
    powerOnTime = millis();
}

void loop() {
    if (is_setting_mode) {
        // Đang trong chế độ WiFi Web Portal: Xử lý request từ điện thoại
        webPortal.handle();

        // Nhấp nháy đèn LED xanh báo hiệu WiFi đang mở
        static unsigned long last_blink = 0;
        if (millis() - last_blink >= 250) {
            last_blink = millis();
            digitalWrite(LED_PIN, !digitalRead(LED_PIN));
        }
        delay(2);
    } else {
        // Đang trong chế độ còi bình thường:
        
        // 1. Kiểm tra bộ đếm giờ ngầm: Nếu điện vẫn cấp liên tục >= 5 giây (Bấm giữ tìm xe / cắm sạc)
        if (millis() - powerOnTime >= CONFIG_HOLD_TIME_MS) {
            enterSettingMode();
            return;
        }

        // 2. Quét nút bấm đổi bài nhanh hoặc ép vào WiFi
        checkSoundSwitchButton();
        delay(10);
    }
}
