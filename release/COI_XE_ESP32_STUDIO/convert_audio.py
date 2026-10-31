#!/usr/bin/env python3
"""
===============================================================================
AUDIO STUDIO WEB SERVER & CONVERTER FOR ESP32-C3 SPEED FX HORN
===============================================================================
- Giao diện trực quan đồ họa sóng âm (Waveform Visualizer)
- Cắt tỉa (Trim start/end), điều chỉnh tốc độ, chuẩn hóa âm lượng (Normalize)
- Đóng gói 5 Slot âm thanh thành sound_bank.bin và nạp thẳng qua USB
- 100% ĐỘC LẬP: Không phụ thuộc mã nguồn C++, an toàn cung cấp cho khách hàng!
===============================================================================
"""

import sys
import os
import wave
import struct
import math
import json
import webbrowser
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Đảm bảo console Windows in tiếng Việt UTF-8 mượt mà
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DIR = os.path.join(SCRIPT_DIR, "sounds_sample")
INPUT_DIR = os.path.join(SCRIPT_DIR, "sounds_input")
HTML_PATH = os.path.join(SCRIPT_DIR, "index.html")
OUTPUT_BIN = os.path.join(SCRIPT_DIR, "sound_bank.bin")

os.makedirs(SAMPLE_DIR, exist_ok=True)
os.makedirs(INPUT_DIR, exist_ok=True)

# Import bộ nạp sound_bank
try:
    import build_sound_bank
except ImportError:
    sys.path.insert(0, SCRIPT_DIR)
    import build_sound_bank

def write_wav(file_path, pcm_bytes, sample_rate=16000):
    """Ghi dữ liệu 8-bit PCM ra file WAV chuẩn mono"""
    with wave.open(file_path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(1)
        w.setframerate(sample_rate)
        w.writeframes(bytes(pcm_bytes))

class AudioStudioHandler(BaseHTTPRequestHandler):
    """HTTP Server phục vụ Web GUI và các tác vụ nạp âm thanh"""

    def log_message(self, format, *args):
        sys.stdout.write(f"[Studio Web] {args[0]} {args[1]}\n")

    def _send_json_response(self, status_code, payload):
        response_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(response_bytes)
        try:
            self.wfile.flush()
        except Exception:
            pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path in ["/", "/index.html"]:
            target_html = HTML_PATH
            if not os.path.exists(target_html):
                alt_html = os.path.join(SCRIPT_DIR, "Audio_Studio.html")
                if os.path.exists(alt_html):
                    target_html = alt_html
                else:
                    self.send_error(404, "Audio_Studio.html not found")
                    return
            with open(target_html, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        elif path == "/esptool-bundle.js":
            bundle_path = os.path.join(SCRIPT_DIR, "esptool-bundle.js")
            if not os.path.exists(bundle_path):
                self.send_error(404, "esptool-bundle.js not found")
                return
            with open(bundle_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
            return

        elif path == "/api/audio_file":
            filename = query.get("name", [""])[0]
            if not filename:
                self.send_error(400, "Missing filename")
                return

            clean_name = os.path.basename(filename)
            # Tìm file trong sounds_sample hoặc sounds_input
            file_path = os.path.join(INPUT_DIR, clean_name)
            if not os.path.exists(file_path):
                file_path = os.path.join(SAMPLE_DIR, clean_name)

            if not os.path.exists(file_path):
                self.send_error(404, f"File {clean_name} not found")
                return

            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = "audio/wav"

            with open(file_path, "rb") as f:
                content = f.read()

            self.send_response(200)
            self.send_header("Content-Type", mime_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
            return

        elif path == "/api/list_slots":
            slots_data = []
            for i in range(20):
                fpath, name = build_sound_bank.find_slot_file(i)
                slots_data.append({
                    "slot": i,
                    "name": name,
                    "filename": os.path.basename(fpath) if fpath else "",
                    "is_custom": (fpath is not None and "sounds_input" in fpath)
                })
            self._send_json_response(200, {"success": True, "slots": slots_data})
            return

        else:
            self.send_error(404, "Endpoint not found")

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/save_slot":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)
                data = json.loads(body.decode("utf-8"))

                slot_idx = int(data.get("slot", 0))
                if slot_idx < 0 or slot_idx >= 20:
                    self._send_json_response(400, {"success": False, "error": "Slot index must be 0-19"})
                    return

                pcm_data = data.get("pcm", [])
                sample_rate = int(data.get("sample_rate", 16000))

                if not pcm_data:
                    self._send_json_response(400, {"success": False, "error": "No PCM data provided"})
                    return

                target_wav = os.path.join(INPUT_DIR, f"slot{slot_idx}.wav")
                write_wav(target_wav, pcm_data, sample_rate)

                # Tự động cập nhật gói sound_bank.bin
                build_sound_bank.build_sound_bank_binary(OUTPUT_BIN)

                self._send_json_response(200, {
                    "success": True,
                    "slot": slot_idx,
                    "length": len(pcm_data),
                    "sample_rate": sample_rate,
                    "message": f"Đã lưu thành công vào Slot {slot_idx} và cập nhật sound_bank.bin!"
                })
            except Exception as e:
                self._send_json_response(500, {"success": False, "error": str(e)})

        elif parsed.path == "/api/flash":
            try:
                success = build_sound_bank.flash_to_esp32(OUTPUT_BIN)
                if success:
                    self._send_json_response(200, {"success": True, "message": "Nạp còi xe thành công!"})
                else:
                    self._send_json_response(500, {"success": False, "error": "Nạp còi xe thất bại. Vui lòng kiểm tra cáp cắm USB."})
            except Exception as e:
                self._send_json_response(500, {"success": False, "error": str(e)})

        else:
            self.send_error(404, "Endpoint not found")

def start_gui_server(port=8765):
    """Mở máy chủ local và tự động bật trình duyệt"""
    import socket

    for p in range(port, port + 20):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", p))
                port = p
                break
        except OSError:
            continue

    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, AudioStudioHandler)
    url = f"http://127.0.0.1:{port}"

    print("=" * 65)
    print("🦆 CÒI XE ESP32-C3 - GIAO DIỆN TÙY CHỈNH ÂM THANH (AUDIO STUDIO)")
    print("=" * 65)
    print(f"[+] Máy chủ đang chạy tại: {url}")
    print("[+] Tự động mở trình duyệt web...")
    print("[+] Nhấn Ctrl+C trong cửa sổ này để dừng máy chủ khi hoàn tất.")
    print("=" * 65)

    webbrowser.open(url)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Đã đóng Audio Studio. Chúc bạn một ngày tốt lành!")
        httpd.server_close()

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--build":
        build_sound_bank.build_sound_bank_binary(OUTPUT_BIN)
    elif len(sys.argv) > 1 and sys.argv[1] == "--flash":
        build_sound_bank.build_sound_bank_binary(OUTPUT_BIN)
        build_sound_bank.flash_to_esp32(OUTPUT_BIN)
    else:
        start_gui_server()

if __name__ == "__main__":
    main()
