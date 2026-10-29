/**
 * ============================================================================
 * PHƯƠNG ÁN 1: CÒI XE SIÊU TỐC THUẦN TÚY 100% (STANDALONE SPEED FX)
 * Dựa trên 100% mã nguồn gốc BACKUP copy/main.cpp đã được kiểm chứng to rõ!
 * ============================================================================
 * - ĐẶC TÍNH:
 *   + 0% WiFi, 0% WebServer, 0% LwIP -> Không bao giờ bị sụt áp, không bị trễ boot!
 *   + Phát to rõ cực đại ngay microsecond đầu tiên khi vừa bật chìa khóa xe / xi nhan!
 *   + Hỗ trợ 4 Slot âm thanh mặc định trong PROGMEM + Tự động nạp Custom Sound Bank
 *     từ phân vùng Flash 0x1E0000 nếu khách hàng đã nạp gói âm thanh qua Tool.
 *
 *   Slot 0: Vịt Còi Xe Chuẩn (Duck 2)
 *   Slot 1: Vịt Kêu Đơn (Duck 1 - Quạc đanh giòn, cực to)
 *   Slot 2: Vịt Còi Đôi (Double Quack)
 *   Slot 3: Bò Rống (Cow Mooing)
 *
 * - CÁCH ĐỔI TIẾNG TRÊN XE (Không cần tháo dàn áo, không cần mở điện thoại):
 *   + Nối dây từ chân GPIO1 (hoặc nút BOOT GPIO9) ra nút bấm phụ trên tay lái xe.
 *   + Khi bật chìa khóa xe: Nhấn nhả nhanh nút 1 cái (35ms - 1.5s) -> Còi chuyển
 *     ngay sang tiếng tiếp theo, kêu thử ngay tiếng mới và tự động lưu nhớ!
 *   + Tắt khóa xe rồi bật lại -> Còi kêu đúng tiếng bạn đã chọn!
 * ============================================================================
 */

#include <Arduino.h>
#include <esp_arduino_version.h>
#include <Preferences.h>
#include <esp_partition.h>
#include <esp_spi_flash.h>
#include "sound_bank.h"

#define AUDIO_PIN          3     // Chân xuất PWM âm thanh (GPIO3 an toàn trên ESP32-C3)
#define LED_PIN            8     // Đèn LED tích hợp (Active LOW)
#define BOOT_PIN           9     // Nút BOOT trên bo mạch
#define EXT_BUTTON_PIN     1     // Nút bấm phụ trên tay lái xe (Active LOW)

#define PWM_CHANNEL        0
#define PWM_FREQ           156250    // 156.25 kHz (Tần số sóng mang ngoài dải nghe)
#define PWM_RESOLUTION     8         // 8-bit tương ứng với dữ liệu PCM 0-255
#define LOOP_PAUSE_MS      1500      // Khoảng nghỉ giữa mỗi lần kêu (1.5 giây)

// Cấu trúc gói âm thanh Custom Sound Bank nạp vào Flash
#define SOUND_BANK_MAGIC      0x4B435544  // 'D','U','C','K' in little-endian
#define SOUND_BANK_MAX_SLOTS  20          // Hỗ trợ mở rộng tối đa lên đến 20 Slot âm thanh

struct SoundSlotMeta {
    uint32_t offset;       // Byte offset tính từ đầu phân vùng Flash
    uint32_t length;       // Số mẫu PCM 8-bit
    uint16_t sample_rate;  // Tần số mẫu (16000, 22050, 32000...)
    uint16_t reserved;
    char     name[32];     // Tên tiếng còi hiển thị
};

struct SoundBankHeader {
    uint32_t magic;        // 0x4B435544
    uint16_t version;      // Phiên bản = 1
    uint16_t slot_count;   // Số lượng slot thực tế
    SoundSlotMeta slots[SOUND_BANK_MAX_SLOTS];
};

struct ActiveSound {
    const uint8_t* pcm_data;
    size_t length;
    uint32_t sample_rate;
};

// Mảng âm thanh hiện hành
static ActiveSound active_sounds[SOUND_BANK_MAX_SLOTS];
static uint8_t total_active_slots = 4; // Số slot thực tế đang dùng (Mặc định 4)

// Lưu slot vào RTC Slow Memory để đọc tức thì 0 microsecond lúc khởi động
RTC_DATA_ATTR uint8_t rtc_saved_slot = 0;
RTC_DATA_ATTR bool    rtc_valid = false;

static hw_timer_t *timer = NULL;
static volatile size_t sample_idx = 0;
static volatile bool is_playing = true;
static volatile uint32_t pause_ticks = 0;

static volatile const uint8_t* isr_pcm_data = sound_data;
static volatile size_t isr_pcm_length = SOUND_DATA_LENGTH;
static volatile uint32_t isr_sample_rate = SOUND_SAMPLE_RATE;
static uint8_t current_slot = 0;

// Trình phục vụ ngắt phần cứng: Tần số gọi = isr_sample_rate (Y hệt BACKUP copy)
void IRAM_ATTR onSampleTimer() {
    if (is_playing) {
        if (sample_idx < isr_pcm_length) {
            uint8_t sample = isr_pcm_data[sample_idx++];
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
            ledcWrite(AUDIO_PIN, sample);
#else
            ledcWrite(PWM_CHANNEL, sample);
#endif
            // Đèn LED sáng (LOW) khi đang phát âm thanh
            gpio_set_level((gpio_num_t)LED_PIN, 0);
        } else {
            is_playing = false;
            sample_idx = 0;
            pause_ticks = (isr_sample_rate * LOOP_PAUSE_MS) / 1000;
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
            ledcWrite(AUDIO_PIN, 128);
#else
            ledcWrite(PWM_CHANNEL, 128);
#endif
            // Đèn LED tắt (HIGH) khi nghỉ
            gpio_set_level((gpio_num_t)LED_PIN, 1);
        }
    } else {
        if (pause_ticks > 0) {
            pause_ticks--;
        } else {
            is_playing = true;
        }
    }
}

// Cấu hình slot âm thanh
static void applySlot(uint8_t slot) {
    if (slot >= total_active_slots) slot = 0;
    current_slot = slot;
    rtc_saved_slot = slot;
    rtc_valid = true;

    isr_pcm_data = active_sounds[slot].pcm_data;
    isr_pcm_length = active_sounds[slot].length;
    isr_sample_rate = active_sounds[slot].sample_rate;
}

// Chuyển sang tiếng tiếp theo khi nhấn nút trên tay lái
static void switchNextSound() {
    uint8_t next = (current_slot + 1) % total_active_slots;
    
    // Tạm dừng timer
    sample_idx = 0;
    pause_ticks = 0;
    is_playing = false;
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
    ledcWrite(AUDIO_PIN, 128);
#else
    ledcWrite(PWM_CHANNEL, 128);
#endif

    applySlot(next);

    // Lưu vào NVS để nhớ vĩnh viễn khi rút hẳn ắc quy
    Preferences prefs;
    if (prefs.begin("coi_config", false)) {
        prefs.putUChar("slot", current_slot);
        prefs.end();
    }

    // Cập nhật lại tần số ngắt timer
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
    timerAlarm(timer, 1000000 / isr_sample_rate, true, 0);
#else
    timerAlarmDisable(timer);
    timerAlarmWrite(timer, 1000000 / isr_sample_rate, true);
    timerWrite(timer, 0);
    timerAlarmEnable(timer);
#endif

    // Phát thử tiếng mới ngay lập tức
    sample_idx = 0;
    is_playing = true;
}

// Quét nút bấm đổi bài trên tay lái xe
static void checkButton() {
    static unsigned long press_start = 0;
    static bool is_pressed = false;

    bool btn_down = (digitalRead(BOOT_PIN) == LOW) || (digitalRead(EXT_BUTTON_PIN) == LOW);

    if (btn_down) {
        if (!is_pressed) {
            is_pressed = true;
            press_start = millis();
        }
    } else {
        if (is_pressed) {
            unsigned long duration = millis() - press_start;
            is_pressed = false;
            // Nhấn nhả nhanh (35ms - 1500ms) -> Đổi tiếng còi ngay!
            if (duration >= 35 && duration < 1500) {
                switchNextSound();
            }
        }
    }
}

// Khởi tạo danh sách âm thanh (Ưu tiên Flash Custom Sound Bank -> Dự phòng PROGMEM)
static void initSoundBank() {
    total_active_slots = 4;
    // 1. Nạp 4 âm thanh mặc định sẵn có trong mã nguồn PROGMEM
    for (int i = 0; i < 4; i++) {
        active_sounds[i].pcm_data = PRELOADED_SOUNDS[i].pcm_data;
        active_sounds[i].length = PRELOADED_SOUNDS[i].length;
        active_sounds[i].sample_rate = PRELOADED_SOUNDS[i].sample_rate;
    }
    for (int i = 4; i < SOUND_BANK_MAX_SLOTS; i++) {
        active_sounds[i] = active_sounds[0];
    }

    // 2. Kiểm tra xem khách hàng có nạp gói âm thanh Custom qua Tool vào Flash 0x1E0000 không
    const esp_partition_t *part = esp_partition_find_first(ESP_PARTITION_TYPE_DATA, ESP_PARTITION_SUBTYPE_DATA_SPIFFS, "littlefs");
    if (part != nullptr) {
        spi_flash_mmap_handle_t mmap_handle;
        const void *mapped_data = nullptr;
        // Ánh xạ phân vùng Flash trực tiếp vào vùng địa chỉ bộ nhớ (0 µs delay, 0 byte RAM)
        if (esp_partition_mmap(part, 0, part->size, SPI_FLASH_MMAP_DATA, &mapped_data, &mmap_handle) == ESP_OK) {
            const SoundBankHeader *bank = (const SoundBankHeader*)mapped_data;
            if (bank->magic == SOUND_BANK_MAGIC && bank->version == 1) {
                uint8_t count = bank->slot_count;
                if (count > SOUND_BANK_MAX_SLOTS) count = SOUND_BANK_MAX_SLOTS;
                if (count > 0) {
                    total_active_slots = count;
                    for (int i = 0; i < count; i++) {
                        if (bank->slots[i].length > 0 && (bank->slots[i].offset + bank->slots[i].length) <= part->size) {
                            active_sounds[i].pcm_data = ((const uint8_t*)mapped_data) + bank->slots[i].offset;
                            active_sounds[i].length = bank->slots[i].length;
                            active_sounds[i].sample_rate = bank->slots[i].sample_rate;
                        }
                    }
                }
            }
        }
    }
}

void setup() {
    // 1. Khởi tạo chân nút bấm & LED ngay từ microsecond đầu (kéo Pullup chống nhiễu / chân lơ lửng)
    pinMode(BOOT_PIN, INPUT_PULLUP);
    pinMode(EXT_BUTTON_PIN, INPUT_PULLUP);
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW); // LOW = Bật sáng ngay microsecond đầu tiên của setup()

    // 2. Cấu hình LEDC PWM tần số cao (156.25 kHz, 8-bit) - Khóa DC 128 chống bụp ngay lập tức
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
    ledcAttach(AUDIO_PIN, PWM_FREQ, PWM_RESOLUTION);
    ledcWrite(AUDIO_PIN, 128);
#else
    ledcSetup(PWM_CHANNEL, PWM_FREQ, PWM_RESOLUTION);
    ledcAttachPin(AUDIO_PIN, PWM_CHANNEL);
    ledcWrite(PWM_CHANNEL, 128);
#endif

    // 3. Khởi tạo kho âm thanh
    initSoundBank();

    // 4. Nạp slot âm thanh: Ưu tiên đọc từ RTC SRAM (0 microsecond, không tốn thời gian đọc Flash)
    uint8_t slot_to_play = 0;
    if (rtc_valid && rtc_saved_slot < total_active_slots) {
        slot_to_play = rtc_saved_slot;
    } else {
        // Cold boot lần đầu tiên: Đọc nhanh từ NVS
        Preferences prefs;
        if (prefs.begin("coi_config", true)) {
            slot_to_play = prefs.getUChar("slot", 0);
            prefs.end();
        }
        if (slot_to_play >= total_active_slots) slot_to_play = 0;
    }
    applySlot(slot_to_play);

    // 5. Cấu hình Hardware Timer ngắt ở tần số isr_sample_rate (Y hệt BACKUP copy)
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
    timer = timerBegin(1000000);
    timerAttachInterrupt(timer, &onSampleTimer);
    timerAlarm(timer, 1000000 / isr_sample_rate, true, 0);
#else
    timer = timerBegin(0, 80, true);
    timerAttachInterrupt(timer, &onSampleTimer, true);
    timerAlarmWrite(timer, 1000000 / isr_sample_rate, true);
    timerAlarmEnable(timer);
#endif
}

void loop() {
    // Quét nút bấm đổi bài liên tục
    checkButton();
    delay(10);
}
