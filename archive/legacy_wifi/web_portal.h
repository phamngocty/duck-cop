#ifndef WEB_PORTAL_H
#define WEB_PORTAL_H

#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>
#include <LittleFS.h>
#include <Update.h>
#include "audio_player.h"
#include "web_portal_data.h"

// Tên mạng WiFi và cổng dịch vụ
#define AP_SSID            "COI-XE-ESP32"
#define DNS_PORT           53
#define HTTP_PORT          80

class WebPortal {
public:
    WebServer server;
    DNSServer dnsServer;
    bool is_active = false;

    WebPortal() : server(HTTP_PORT) {}

    void start() {
        if (is_active) return;
        is_active = true;

        // 1. Khởi động LittleFS nếu chưa mount
        LittleFS.begin(true);

        // 2. Cấu hình WiFi Access Point
        WiFi.persistent(false);
        WiFi.disconnect(true, true);
        WiFi.mode(WIFI_AP);

        IPAddress apIP(192, 168, 4, 1);
        IPAddress netMsk(255, 255, 255, 0);
        WiFi.softAPConfig(apIP, apIP, netMsk);
        WiFi.softAP(AP_SSID);

        // 3. Khởi động DNS Server cho Captive Portal
        dnsServer.setErrorReplyCode(DNSReplyCode::NoError);
        dnsServer.start(DNS_PORT, "*", apIP);

        // CORS Header helper
        auto setCorsHeaders = [this]() {
            server.sendHeader("Access-Control-Allow-Origin", "*");
            server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
            server.sendHeader("Access-Control-Allow-Headers", "*");
        };

        // Phục vụ giao diện Studio HTML nén Gzip (siêu nhẹ, tải trong 100ms)
        server.on("/", HTTP_GET, [this, setCorsHeaders]() {
            setCorsHeaders();
            server.sendHeader("Content-Encoding", "gzip");
            server.sendHeader("Cache-Control", "no-cache");
            server.send_P(200, "text/html; charset=utf-8", (const char*)WEB_PORTAL_HTML_GZ, WEB_PORTAL_HTML_GZ_LEN);
        });

        // OPTIONS cho CORS Pre-flight
        server.on("/api/upload_pcm", HTTP_OPTIONS, [this, setCorsHeaders]() {
            setCorsHeaders();
            server.send(204);
        });
        server.on("/api/select_slot", HTTP_OPTIONS, [this, setCorsHeaders]() {
            setCorsHeaders();
            server.send(204);
        });
        server.on("/api/save_sound", HTTP_OPTIONS, [this, setCorsHeaders]() {
            setCorsHeaders();
            server.send(204);
        });
        server.on("/api/status", HTTP_OPTIONS, [this, setCorsHeaders]() {
            setCorsHeaders();
            server.send(204);
        });

        // API Lấy trạng thái còi xe hiện tại
        server.on("/api/status", HTTP_GET, [this, setCorsHeaders]() {
            setCorsHeaders();
            AudioPlayer& p = AudioPlayer::instance();
            String json = "{";
            json += "\"is_custom\":" + String(p.is_using_littlefs ? "true" : "false") + ",";
            json += "\"slot\":" + String(p.current_slot) + ",";
            json += "\"slot_name\":\"" + String(p.getSlotName(p.current_slot)) + "\",";
            json += "\"sample_rate\":" + String(p.settings.sample_rate) + ",";
            json += "\"volume\":" + String(p.settings.volume) + ",";
            json += "\"loop_mode\":" + String(p.settings.loop_mode) + ",";
            json += "\"loop_pause_ms\":" + String(p.settings.loop_pause_ms) + ",";
            json += "\"pcm_length\":" + String(p.active_pcm_length);
            json += "}";
            server.send(200, "application/json", json);
        });

        // API Chọn slot âm thanh
        server.on("/api/select_slot", HTTP_POST, [this, setCorsHeaders]() {
            setCorsHeaders();
            if (!server.hasArg("slot")) {
                server.send(400, "text/plain", "Missing slot");
                return;
            }
            uint8_t slot = server.arg("slot").toInt();
            if (slot >= SOUND_BANK_COUNT) {
                server.send(400, "text/plain", "Invalid slot");
                return;
            }
            bool ok = AudioPlayer::instance().selectSlot(slot, true);
            if (!ok) {
                server.send(400, "text/plain", "Chua co file am thanh trong LittleFS");
                return;
            }
            server.send(200, "application/json", "{\"success\":true}");
        });

        // API Phát thử tiếng bíp
        server.on("/api/test_beep", HTTP_POST, [this, setCorsHeaders]() {
            setCorsHeaders();
            AudioPlayer::instance().playBeep(2000, 100);
            server.send(200, "application/json", "{\"success\":true}");
        });

        // API Nạp file âm thanh PCM trực tiếp từ Studio vào phân vùng LittleFS
        auto saveAudioHandler = [this, setCorsHeaders]() {
            setCorsHeaders();
            if (!server.hasArg("plain")) {
                server.send(400, "text/plain", "No data");
                return;
            }
            String body = server.arg("plain");
            size_t len = body.length();
            if (len == 0 || len > 2100000) {
                server.send(400, "text/plain", "Payload too large or empty");
                return;
            }

            AudioPlayer& p = AudioPlayer::instance();
            AudioSettings newSet = p.settings;
            if (server.hasHeader("X-Rate")) newSet.sample_rate = server.header("X-Rate").toInt();
            else if (server.hasArg("rate")) newSet.sample_rate = server.arg("rate").toInt();

            File f = LittleFS.open(AUDIO_FILE_PATH, "w");
            if (!f) {
                server.send(500, "text/plain", "Failed to open LittleFS file for writing");
                return;
            }
            f.write((const uint8_t*)body.c_str(), len);
            f.close();

            p.saveSettings(newSet);
            p.selectSlot(5, true);

            server.send(200, "application/json", "{\"success\":true}");
        };

        server.on("/api/save_sound", HTTP_POST, saveAudioHandler);
        server.on("/api/upload_pcm", HTTP_POST, saveAudioHandler);

        // =========================================================================
        // CƠ CHẾ NẠP FIRMWARE TỪ XA QUA WIFI (OTA FIRMWARE UPDATE)
        // =========================================================================
        // Trang cập nhật Firmware HTML độc lập (truy cập: http://192.168.4.1/update)
        server.on("/update", HTTP_GET, [this, setCorsHeaders]() {
            setCorsHeaders();
            const char* otaHtml = 
                "<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
                "<title>OTA Firmware Update - Coi Xe ESP32</title>"
                "<style>body{font-family:sans-serif;background:#050d1a;color:#e6f1ff;display:flex;align-items:center;justify-content:center;height:100vh;margin:0}"
                ".card{background:#0d2242;padding:24px;border-radius:12px;border:1px solid #173766;width:90%;max-width:400px;text-align:center}"
                "h2{color:#00f0aa;margin-top:0}p{font-size:13px;color:#8ba3c7}"
                "input[type=file]{margin:16px 0;width:100%;color:#8ba3c7}"
                "button{background:#00f0aa;color:#050d1a;border:none;padding:12px 20px;border-radius:8px;font-weight:700;width:100%;cursor:pointer;font-size:14px}"
                ".prog{width:100%;background:#08162b;height:12px;border-radius:6px;overflow:hidden;margin:16px 0;display:none}"
                ".bar{width:0%;height:100%;background:#00f0aa;transition:width 0.2s}</style></head><body>"
                "<div class='card'><h2>🚀 Cập Nhật Firmware (OTA)</h2>"
                "<p>Chọn file <b>firmware.bin</b> đã biên dịch từ máy tính / điện thoại để nâng cấp còi xe qua WiFi:</p>"
                "<form id='f' method='POST' action='/api/ota' enctype='multipart/form-data'>"
                "<input type='file' name='update' accept='.bin' id='fi' required>"
                "<div class='prog' id='pr'><div class='bar' id='pb'></div></div>"
                "<button type='submit' id='sub'>BẮT ĐẦU NÂNG CẤP</button></form>"
                "<p id='st' style='margin-top:12px;font-weight:600;'></p></div>"
                "<script>document.getElementById('f').onsubmit=function(e){"
                "e.preventDefault();var fi=document.getElementById('fi').files[0];if(!fi)return;"
                "var fd=new FormData();fd.append('update',fi);var xhr=new XMLHttpRequest();"
                "document.getElementById('pr').style.display='block';document.getElementById('sub').disabled=true;"
                "document.getElementById('st').innerText='Đang tải lên...';"
                "xhr.upload.onprogress=function(e){if(e.lengthComputable){var p=Math.round((e.loaded/e.total)*100);"
                "document.getElementById('pb').style.width=p+'%';document.getElementById('st').innerText='Đang nạp: '+p+'%';}};"
                "xhr.onload=function(){if(xhr.status===200){document.getElementById('st').innerHTML='<span style=\"color:#00f0aa\">✅ THÀNH CÔNG! Đang khởi động lại còi...</span>';"
                "setTimeout(function(){location.href='/';},4000);}else{document.getElementById('st').innerHTML='<span style=\"color:#ff4772\">❌ THẤT BẠI: '+xhr.responseText+'</span>';"
                "document.getElementById('sub').disabled=false;}};"
                "xhr.open('POST','/api/ota');xhr.send(fd);};</script></body></html>";
            server.send(200, "text/html; charset=utf-8", otaHtml);
        });

        // Endpoint xử lý Upload Firmware Streaming Binary vào Flash OTA partition
        server.on("/api/ota", HTTP_POST, [this, setCorsHeaders]() {
            setCorsHeaders();
            server.sendHeader("Connection", "close");
            if (Update.hasError()) {
                server.send(500, "text/plain", "Update Failed!");
            } else {
                server.send(200, "text/plain", "Update Success! Rebooting...");
                delay(300);
                ESP.restart();
            }
        }, [this]() {
            HTTPUpload& upload = server.upload();
            if (upload.status == UPLOAD_FILE_START) {
                // Tắt phát âm thanh để giải phóng CPU và ngắt hardware timer trong lúc flash firmware
                AudioPlayer::instance().stop();

                size_t maxOtaSize = UPDATE_SIZE_UNKNOWN;
                if (!Update.begin(maxOtaSize, U_FLASH)) {
                    Update.printError(Serial);
                }
            } else if (upload.status == UPLOAD_FILE_WRITE) {
                if (Update.write(upload.buf, upload.currentSize) != upload.currentSize) {
                    Update.printError(Serial);
                }
            } else if (upload.status == UPLOAD_FILE_END) {
                if (!Update.end(true)) {
                    Update.printError(Serial);
                }
            } else if (upload.status == UPLOAD_FILE_ABORTED) {
                Update.end();
            }
        });

        // Captive Portal Redirects cho iOS & Android
        server.on("/generate_204", HTTP_GET, [this]() { handleCaptiveRedirect(); });
        server.on("/gen_204", HTTP_GET, [this]() { handleCaptiveRedirect(); });
        server.on("/hotspot-detect.html", HTTP_GET, [this]() { handleCaptiveRedirect(); });
        server.on("/canonical.html", HTTP_GET, [this]() { handleCaptiveRedirect(); });
        server.on("/ncsi.txt", HTTP_GET, [this]() { handleCaptiveRedirect(); });
        server.on("/connecttest.txt", HTTP_GET, [this]() { handleCaptiveRedirect(); });

        server.onNotFound([this]() { handleCaptiveRedirect(); });

        const char* headerkeys[] = {"X-Rate", "X-Vol", "X-Loop", "X-Pause"};
        server.collectHeaders(headerkeys, sizeof(headerkeys) / sizeof(char*));

        server.begin();
    }

    void handleCaptiveRedirect() {
        String host = server.hostHeader();
        if (host.length() > 0 && host.indexOf("192.168.4.1") < 0) {
            server.sendHeader("Location", "http://192.168.4.1/", true);
            server.send(302, "text/plain", "");
        } else {
            server.sendHeader("Content-Encoding", "gzip");
            server.sendHeader("Cache-Control", "no-cache");
            server.send_P(200, "text/html; charset=utf-8", (const char*)WEB_PORTAL_HTML_GZ, WEB_PORTAL_HTML_GZ_LEN);
        }
    }

    void handle() {
        if (!is_active) return;
        dnsServer.processNextRequest();
        server.handleClient();
    }
};

#endif // WEB_PORTAL_H
