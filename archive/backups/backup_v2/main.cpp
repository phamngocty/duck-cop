/**
 * ============================================================================
 * DỰ ÁN: CÒI XI NHAN / CÒI PHANH HIỆU ỨNG ÂM THANH TỨC THÌ (INSTANT SOUND FX)
 * Vi điều khiển: ESP32-C3 Super Mini (RISC-V 160MHz, Flash 4MB)
 * Mạch công suất: PAM8403 (Amply Stereo 2x3W Class-D)
 * Chân xuất âm thanh: GPIO3 (Qua mạch lọc RC 1kΩ + 104 vào ngõ L/R của PAM8403)
 * ============================================================================
 *
 * NGUYÊN LÝ HOẠT ĐỘNG:
 * 1. LEDC High-Speed PWM:
 *    - Tạo sóng mang tần số ~156.25 kHz (8-bit) vượt xa dải nghe của tai người.
 *    - Mạch lọc RC bên ngoài (1kΩ + tụ 100nF) giải điều chế thành sóng Analog
 *      sạch đưa vào ngõ Audio In (L/R) của PAM8403.
 *
 * 2. Hardware Timer Interrupt:
 *    - Ngắt chính xác ở tần số lấy mẫu SOUND_SAMPLE_RATE (16000Hz / 22050Hz).
 *    - Mỗi lần ngắt cập nhật độ rộng xung PWM (0 - 255) từ mảng sound_data trong Flash.
 *
 * 3. Chống nóng loa & triệt tiêu tiếng bụp:
 *    - Khi không phát, giữ mức tĩnh lặng hoặc kéo về 0 để ngắt dòng DC vào PAM8403.
 */

#include <Arduino.h>
#include <esp_arduino_version.h>
#include "sound_data.h"

// Chân xuất PWM âm thanh (GPIO3 an toàn khi khởi động trên ESP32-C3)
#define AUDIO_PIN          3

// Cấu hình LEDC PWM
#define PWM_CHANNEL        0
#define PWM_FREQ           156250    // 156.25 kHz (Tần số sóng mang ngoài dải nghe)
#define PWM_RESOLUTION     8         // 8-bit tương ứng với dữ liệu PCM 0-255

// Cấu hình lặp lại âm thanh (1 = Lặp vô tận để test còi/loa, 0 = Kêu 1 lần)
#define ENABLE_LOOP_MODE   1
#define LOOP_PAUSE_MS      1500      // Khoảng nghỉ giữa mỗi lần kêu (1.5 giây)

static hw_timer_t *timer = NULL;
static volatile size_t sample_idx = 0;
static volatile bool is_playing = true;
static volatile uint32_t pause_ticks = 0;

// Trình phục vụ ngắt phần cứng: Tần số gọi = SOUND_SAMPLE_RATE
void IRAM_ATTR onSampleTimer() {
    if (is_playing) {
        if (sample_idx < SOUND_DATA_LENGTH) {
            uint8_t sample = sound_data[sample_idx++];
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
            ledcWrite(AUDIO_PIN, sample);
#else
            ledcWrite(PWM_CHANNEL, sample);
#endif
        } else {
#if ENABLE_LOOP_MODE
            is_playing = false;
            sample_idx = 0;
            pause_ticks = (SOUND_SAMPLE_RATE * LOOP_PAUSE_MS) / 1000;
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
            ledcWrite(AUDIO_PIN, 128);
#else
            ledcWrite(PWM_CHANNEL, 128);
#endif
#else
            // Phát xong 1 lần -> Tắt PWM để triệt tiêu dòng rò bảo vệ PAM8403
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
            ledcWrite(AUDIO_PIN, 0);
            timerAlarmDisable(timer);
#else
            ledcWrite(PWM_CHANNEL, 0);
            timerAlarmDisable(timer);
#endif
#endif
        }
    } else {
        if (pause_ticks > 0) {
            pause_ticks--;
        } else {
            is_playing = true;
        }
    }
}

void setup() {
    // 1. Cấu hình LEDC PWM tần số cao (156.25 kHz, 8-bit)
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
    ledcAttach(AUDIO_PIN, PWM_FREQ, PWM_RESOLUTION);
    ledcWrite(AUDIO_PIN, 128);
#else
    ledcSetup(PWM_CHANNEL, PWM_FREQ, PWM_RESOLUTION);
    ledcAttachPin(AUDIO_PIN, PWM_CHANNEL);
    ledcWrite(PWM_CHANNEL, 128);
#endif

    // 2. Cấu hình Hardware Timer ngắt ở tần số SOUND_SAMPLE_RATE
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
    timer = timerBegin(1000000); // 1 MHz resolution (1 tick = 1 us)
    timerAttachInterrupt(timer, &onSampleTimer);
    timerAlarm(timer, 1000000 / SOUND_SAMPLE_RATE, true, 0);
#else
    // Bộ chia tần: 80MHz / 80 = 1MHz (1 tick = 1us)
    timer = timerBegin(0, 80, true);
    timerAttachInterrupt(timer, &onSampleTimer, true);
    timerAlarmWrite(timer, 1000000 / SOUND_SAMPLE_RATE, true);
    timerAlarmEnable(timer);
#endif
}

void loop() {
    // Để trống - Toàn bộ việc phát âm thanh diễn ra trong ngắt phần cứng,
    // phản hồi tức thì dưới 1ms khi cấp nguồn!
    vTaskDelay(pdMS_TO_TICKS(1000));
}
