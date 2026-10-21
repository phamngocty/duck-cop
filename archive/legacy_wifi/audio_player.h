#ifndef AUDIO_PLAYER_H
#define AUDIO_PLAYER_H

#include <Arduino.h>
#include <esp_arduino_version.h>
#include <LittleFS.h>
#include <Preferences.h>
#include "sound_bank.h"

// Cấu hình chân phần cứng ESP32-C3 Super Mini
#define AUDIO_PIN          3     // Chân PWM ra mạch lọc RC (1k + 104) -> PAM8403 / PAM8610
#define LED_PIN            8     // Đèn LED tích hợp (Active LOW)
#define BOOT_PIN           9     // Nút BOOT trên mạch (Active LOW)
#define EXT_BUTTON_PIN     1     // Chân nút nhấn phụ ngoài xe (Active LOW)

// Cấu hình LEDC PWM (Tần số sóng mang ngoài dải nghe 156.25 kHz, 8-bit)
#define PWM_CHANNEL        0
#define PWM_FREQ           156250
#define PWM_RESOLUTION     8

// Đường dẫn file âm thanh trong LittleFS
#define AUDIO_FILE_PATH    "/audio.pcm"
#define CONFIG_NAMESPACE   "coi_config"

struct AudioSettings {
    uint16_t sample_rate;    // Tần số lấy mẫu (8000, 16000, 22050, 32000...)
    uint8_t  volume;         // 100%
    uint8_t  loop_mode;      // 0: Kêu 1 lần rồi tắt, 1: Lặp lại
    uint16_t loop_pause_ms;  // Khoảng nghỉ giữa các lần kêu (ms)
};

// =============================================================================
// CÁC BIẾN TOÀN CỤC PHẲNG CHO NGẮT TIMER (100% TRONG IRAM/BSS - KHÔNG CLASS/METHOD OVERHEAD)
// Giống 100% bản BACKUP copy để tiếng đầu tiên to rõ cực đại ngay từ microsecond đầu!
// =============================================================================
static volatile const uint8_t* isr_pcm_data = sound_data;
static volatile size_t isr_pcm_length = SOUND_DATA_LENGTH;
static volatile size_t isr_sample_idx = 0;
static volatile bool isr_is_playing = true;
static volatile uint32_t isr_pause_ticks = 0;
static volatile uint32_t isr_sample_rate = SOUND_SAMPLE_RATE;
static volatile bool isr_loop_mode = true;
static volatile uint16_t isr_loop_pause_ms = 1500;

// Trình phục vụ ngắt phần cứng thời gian thực: Tần số gọi = sample_rate (22050Hz / 16000Hz)
static void IRAM_ATTR onTimerISR() {
    if (isr_is_playing) {
        if (isr_sample_idx < isr_pcm_length) {
            uint8_t raw_sample = isr_pcm_data[isr_sample_idx++];
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
            ledcWrite(AUDIO_PIN, raw_sample);
#else
            ledcWrite(PWM_CHANNEL, raw_sample);
#endif
        } else {
            if (isr_loop_mode) {
                isr_is_playing = false;
                isr_sample_idx = 0;
                isr_pause_ticks = (isr_sample_rate * isr_loop_pause_ms) / 1000;
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
                ledcWrite(AUDIO_PIN, 128);
#else
                ledcWrite(PWM_CHANNEL, 128);
#endif
            } else {
                isr_is_playing = false;
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
                ledcWrite(AUDIO_PIN, 128);
#else
                ledcWrite(PWM_CHANNEL, 128);
#endif
            }
        }
    } else {
        if (isr_pause_ticks > 0) {
            isr_pause_ticks--;
        } else if (isr_loop_mode) {
            isr_sample_idx = 0;
            isr_is_playing = true;
        }
    }
}

// Lưu slot vào RTC Slow SRAM để nạp tức thì 0 microsecond khi bật khóa xe, giải phóng 100% Flash bus
RTC_DATA_ATTR uint8_t rtc_audio_slot = 0;
RTC_DATA_ATTR bool    rtc_audio_valid = false;

class AudioPlayer {
public:
    static AudioPlayer& instance() {
        static AudioPlayer inst;
        return inst;
    }

    AudioSettings settings;
    uint8_t*  active_pcm_data = (uint8_t*)sound_data;
    size_t    active_pcm_length = SOUND_DATA_LENGTH;
    bool      is_using_littlefs = false;
    uint8_t   current_slot = 0;  // 0-4: Preset có sẵn, 5: Tự nạp LittleFS

    hw_timer_t* sample_timer = nullptr;

    const char* getSlotName(uint8_t slot) {
        switch (slot) {
            case 0: return PRELOADED_SOUNDS[0].name;
            case 1: return PRELOADED_SOUNDS[1].name;
            case 2: return PRELOADED_SOUNDS[2].name;
            case 3: return PRELOADED_SOUNDS[3].name;
            case 4: return PRELOADED_SOUNDS[4].name;
            case 5: return "Am Tu Nap (LittleFS)";
            default: return "Khong xac dinh";
        }
    }

    // Khởi tạo siêu tốc (< 1ms): Khóa DC 128 chống bụp, nạp đúng tiếng đã lưu từ RTC/NVS, kích hoạt timer ngay
    void initFast() {
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
        ledcAttach(AUDIO_PIN, PWM_FREQ, PWM_RESOLUTION);
        ledcWrite(AUDIO_PIN, 128);
#else
        ledcSetup(PWM_CHANNEL, PWM_FREQ, PWM_RESOLUTION);
        ledcAttachPin(AUDIO_PIN, PWM_CHANNEL);
        ledcWrite(PWM_CHANNEL, 128);
#endif

        // Ưu tiên đọc slot từ RTC SRAM (0 microsecond, zero Flash bus contention)
        uint8_t saved_slot = 0;
        if (rtc_audio_valid && rtc_audio_slot < SOUND_BANK_COUNT) {
            saved_slot = rtc_audio_slot;
        } else {
            Preferences prefs;
            if (prefs.begin(CONFIG_NAMESPACE, true)) {
                saved_slot = prefs.getUChar("slot", 0);
                prefs.end();
            }
            if (saved_slot >= SOUND_BANK_COUNT) saved_slot = 0;
            rtc_audio_slot = saved_slot;
            rtc_audio_valid = true;
        }
        current_slot = saved_slot;

        if (saved_slot < 5) {
            active_pcm_data = (uint8_t*)PRELOADED_SOUNDS[saved_slot].pcm_data;
            active_pcm_length = PRELOADED_SOUNDS[saved_slot].length;
            settings.sample_rate = PRELOADED_SOUNDS[saved_slot].sample_rate;
            is_using_littlefs = false;
        } else {
            // LittleFS slot 5: nếu chưa mount FS lúc boot, phát an toàn Slot 0
            active_pcm_data = (uint8_t*)PRELOADED_SOUNDS[0].pcm_data;
            active_pcm_length = PRELOADED_SOUNDS[0].length;
            settings.sample_rate = PRELOADED_SOUNDS[0].sample_rate;
            is_using_littlefs = false;
            current_slot = 0;
        }

        isr_pcm_data = active_pcm_data;
        isr_pcm_length = active_pcm_length;
        isr_sample_rate = settings.sample_rate;
        isr_sample_idx = 0;
        isr_pause_ticks = 0;
        isr_is_playing = true;
        isr_loop_mode = true;
        isr_loop_pause_ms = 1500;

        settings.volume = 100;
        settings.loop_mode = 1;
        settings.loop_pause_ms = 1500;

        setupTimer(isr_sample_rate);
    }

    void setupTimer(uint32_t rate) {
        if (rate < 4000 || rate > 48000) rate = SOUND_SAMPLE_RATE;

#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
        if (sample_timer) {
            timerEnd(sample_timer);
            sample_timer = nullptr;
        }
        sample_timer = timerBegin(1000000);
        timerAttachInterrupt(sample_timer, &onTimerISR);
        timerAlarm(sample_timer, 1000000 / rate, true, 0);
#else
        if (sample_timer) {
            timerAlarmDisable(sample_timer);
            timerDetachInterrupt(sample_timer);
            timerEnd(sample_timer);
            sample_timer = nullptr;
        }
        sample_timer = timerBegin(0, 80, true); // 80MHz / 80 = 1MHz tick
        timerAttachInterrupt(sample_timer, &onTimerISR, true);
        timerAlarmWrite(sample_timer, 1000000 / rate, true);
        timerAlarmEnable(sample_timer);
#endif
    }

    void start() {
        isr_sample_idx = 0;
        isr_pause_ticks = 0;
        isr_is_playing = true;
    }

    void stop() {
        isr_is_playing = false;
        isr_pause_ticks = 0;
        isr_sample_idx = 0;
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
        ledcWrite(AUDIO_PIN, 128);
#else
        ledcWrite(PWM_CHANNEL, 128);
#endif
    }

    void saveSettings(const AudioSettings& newSettings) {
        settings = newSettings;
        isr_sample_rate = settings.sample_rate;
        isr_loop_mode = (settings.loop_mode != 0);
        isr_loop_pause_ms = settings.loop_pause_ms;

        Preferences prefs;
        prefs.begin(CONFIG_NAMESPACE, false);
        prefs.putUShort("rate", settings.sample_rate);
        prefs.putUChar("slot", current_slot);
        prefs.end();

        setupTimer(settings.sample_rate);
    }

    bool selectSlot(uint8_t slot, bool playImmediate = true, bool saveNVS = true) {
        if (slot >= SOUND_BANK_COUNT) slot = 0;

        stop();

        if (slot < 5) {
            if (active_pcm_data && is_using_littlefs) {
                free(active_pcm_data);
                active_pcm_data = nullptr;
            }
            active_pcm_data = (uint8_t*)PRELOADED_SOUNDS[slot].pcm_data;
            active_pcm_length = PRELOADED_SOUNDS[slot].length;
            settings.sample_rate = PRELOADED_SOUNDS[slot].sample_rate;
            is_using_littlefs = false;
            current_slot = slot;

            isr_pcm_data = active_pcm_data;
            isr_pcm_length = active_pcm_length;
            isr_sample_rate = settings.sample_rate;
        } else {
            bool loaded = false;
            LittleFS.begin(true);
            if (LittleFS.exists(AUDIO_FILE_PATH)) {
                File f = LittleFS.open(AUDIO_FILE_PATH, "r");
                if (f && f.size() > 0 && f.size() <= 2100000) {
                    if (active_pcm_data && is_using_littlefs) {
                        free(active_pcm_data);
                        active_pcm_data = nullptr;
                    }
                    active_pcm_length = f.size();
                    active_pcm_data = (uint8_t*)malloc(active_pcm_length);
                    if (active_pcm_data) {
                        f.read(active_pcm_data, active_pcm_length);
                        f.close();
                        is_using_littlefs = true;
                        current_slot = 5;
                        loaded = true;

                        isr_pcm_data = active_pcm_data;
                        isr_pcm_length = active_pcm_length;
                        isr_sample_rate = settings.sample_rate;
                    }
                }
                if (f) f.close();
            }

            if (!loaded) {
                return selectSlot(0, playImmediate, saveNVS);
            }
        }

        setupTimer(settings.sample_rate);

        rtc_audio_slot = current_slot;
        rtc_audio_valid = true;

        if (saveNVS) {
            Preferences prefs;
            prefs.begin(CONFIG_NAMESPACE, false);
            prefs.putUChar("slot", current_slot);
            prefs.putUShort("rate", settings.sample_rate);
            prefs.end();
        }

        if (playImmediate) {
            start();
        }

        return true;
    }

    void nextSlot() {
        uint8_t next = (current_slot + 1) % SOUND_BANK_COUNT;
        if (next == 5) {
            LittleFS.begin(true);
            if (!LittleFS.exists(AUDIO_FILE_PATH)) {
                next = 0;
            }
        }
        selectSlot(next, true, true);
    }

    // Phát tiếng bíp báo hiệu vào chế độ Web Portal (2 tiếng bíp vang dội)
    void playBeep(uint16_t freq_hz, uint16_t duration_ms) {
        bool was_playing = isr_is_playing;
        stop();

        uint32_t half_period_us = 500000 / freq_hz;
        uint32_t cycles = (freq_hz * duration_ms) / 1000;

        for (uint32_t i = 0; i < cycles; i++) {
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
            ledcWrite(AUDIO_PIN, 220);
#else
            ledcWrite(PWM_CHANNEL, 220);
#endif
            delayMicroseconds(half_period_us);
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
            ledcWrite(AUDIO_PIN, 35);
#else
            ledcWrite(PWM_CHANNEL, 35);
#endif
            delayMicroseconds(half_period_us);
        }

#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
        ledcWrite(AUDIO_PIN, 128);
#else
        ledcWrite(PWM_CHANNEL, 128);
#endif
        if (was_playing) {
            start();
        }
    }
};

#endif // AUDIO_PLAYER_H
