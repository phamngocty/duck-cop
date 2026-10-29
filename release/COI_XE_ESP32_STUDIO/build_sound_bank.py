#!/usr/bin/env python3
"""
===============================================================================
ESP32-C3 SOUND BANK BUILDER & FLASHER TOOL (DÀNH CHO KHÁCH HÀNG & NHÀ SẢN XUẤT)
===============================================================================
- Chức năng:
  1. Tự động chuyển đổi các file âm thanh WAV trong thư mục `sounds_input/`
     thành gói nhị phân độc lập `sound_bank.bin`.
  2. Nạp trực tiếp gói âm thanh `sound_bank.bin` vào phân vùng Flash 0x1E0000 của ESP32-C3.
  3. TUYỆT ĐỐI BẢO MẬT: Không chứa mã nguồn C++, không lộ thuật toán còi xe!
===============================================================================
"""

import os
import sys
import glob
import wave
import struct
import math
import argparse
import subprocess

# Đảm bảo in tiếng Việt trên mọi máy tính Windows không bị lỗi font / charmap
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DIR = os.path.join(SCRIPT_DIR, "sounds_sample")
INPUT_DIR = os.path.join(SCRIPT_DIR, "sounds_input")
OUTPUT_BIN = os.path.join(SCRIPT_DIR, "sound_bank.bin")

FLASH_OFFSET = "0x1E0000"
MAGIC = 0x4B435544  # 'D','U','C','K' in little-endian
VERSION = 1
MAX_SLOTS = 20
TARGET_SAMPLE_RATE = 22050
ANTI_POP_PADDING_SAMPLES = 220  # 10ms of 0x80 (DC 128) at 22050Hz

DEFAULT_SLOT_NAMES = [
    "Slot 0: Vit Coi Xe Chuan (Duck 2)",
    "Slot 1: Vit Keu Don (Duck 1)",
    "Slot 2: Vit Coi Doi (Double Quack)",
    "Slot 3: Bo Rong (Cow Mooing)"
]

def load_wav_pcm(wav_path, target_rate=TARGET_SAMPLE_RATE, add_padding=True):
    """Đọc file WAV, chuẩn hóa về 8-bit unsigned PCM ở tần số target_rate"""
    with wave.open(wav_path, 'rb') as w:
        nchannels, sampwidth, framerate, nframes = w.getparams()[:4]
        raw = w.readframes(nframes)

    # 1. Giải mã mẫu sang float [-1.0, 1.0]
    if sampwidth == 1:
        samples = [(b - 128) / 128.0 for b in raw]
    elif sampwidth == 2:
        samples = [s[0] / 32768.0 for s in struct.iter_unpack('<h', raw)]
    elif sampwidth == 3:
        # 24-bit PCM
        samples = []
        for i in range(0, len(raw), 3):
            val = int.from_bytes(raw[i:i+3], byteorder='little', signed=True)
            samples.append(val / 8388608.0)
    else:
        raise ValueError(f"Không hỗ trợ định dạng âm thanh {sampwidth * 8}-bit trong file: {wav_path}")

    # Gộp stereo về mono nếu cần
    if nchannels > 1:
        samples = [sum(samples[i:i+nchannels]) / float(nchannels) for i in range(0, len(samples), nchannels)]

    # 2. Resample tuyến tính về tần số mục tiêu (mặc định 16000Hz)
    if framerate != target_rate:
        ratio = framerate / float(target_rate)
        num_out = int(len(samples) / ratio)
        resampled = []
        for i in range(num_out):
            src = i * ratio
            low = int(src)
            high = min(low + 1, len(samples) - 1)
            frac = src - low
            val = (1.0 - frac) * samples[low] + frac * samples[high]
            resampled.append(val)
        samples = resampled

    # 3. Khuếch đại tối đa (Normalize Peak lên 98% để kêu to nhất)
    mx = max(abs(s) for s in samples) if samples else 1.0
    scale = 0.98 / mx if mx > 0.05 else 1.0
    pcm = [max(0, min(255, int(round((s * scale * 127.0) + 128.0)))) for s in samples]

    # 4. Cắt tỉa khoảng lặng (silence trim)
    start = 0
    while start < len(pcm) and abs(pcm[start] - 128) < 4:
        start += 1
    end = len(pcm) - 1
    while end > start and abs(pcm[end] - 128) < 4:
        end -= 1

    trimmed = pcm[start:end+1] if end >= start else pcm

    # 5. Chèn đệm 10ms DC 128 chống bụp loa
    if add_padding:
        trimmed = [128] * ANTI_POP_PADDING_SAMPLES + trimmed

    return trimmed, target_rate

def find_slot_file(slot_idx):
    """Tìm file cho slot: Ưu tiên sounds_input/slotX.* -> sounds_sample/slotX_*"""
    def_name = DEFAULT_SLOT_NAMES[slot_idx] if slot_idx < len(DEFAULT_SLOT_NAMES) else f"Slot {slot_idx}"
    # 1. Tìm trong sounds_input
    for ext in ['.wav', '.WAV']:
        p = os.path.join(INPUT_DIR, f"slot{slot_idx}{ext}")
        if os.path.exists(p):
            return p, f"Custom Slot {slot_idx} ({os.path.basename(p)})"

    # Tìm bất kỳ file nào có tiền tố slotX trong sounds_input
    matches = glob.glob(os.path.join(INPUT_DIR, f"slot{slot_idx}*.*"))
    if matches:
        return matches[0], f"Custom Slot {slot_idx} ({os.path.basename(matches[0])})"

    # 2. Dự phòng trong sounds_sample
    sample_matches = glob.glob(os.path.join(SAMPLE_DIR, f"slot{slot_idx}*.*"))
    if sample_matches:
        return sample_matches[0], def_name

    return None, def_name

def build_sound_bank_binary(output_path=OUTPUT_BIN):
    """Tạo file sound_bank.bin chuẩn định dạng nhị phân Flash"""
    print("\n" + "=" * 65)
    print("[*] DANG KHOI TAO GOI AM THANH SOUND_BANK.BIN CHO ESP32-C3")
    print("=" * 65)

    import re
    slot_indices = set(range(4))
    for f in glob.glob(os.path.join(INPUT_DIR, "slot*.*")):
        base = os.path.basename(f)
        m = re.match(r'slot(\d+)', base, re.I)
        if m:
            slot_indices.add(int(m.group(1)))

    num_slots = min(MAX_SLOTS, max(slot_indices) + 1 if slot_indices else 4)
    header_size = 512 if num_slots <= 11 else 1024
    header_buf = bytearray(header_size)
    struct.pack_into('<IHH', header_buf, 0, MAGIC, VERSION, num_slots)

    curr_offset = header_size
    pcm_chunks = []
    slot_info_list = []

    for idx in range(num_slots):
        file_path, display_name = find_slot_file(idx)
        if file_path and os.path.exists(file_path):
            try:
                pcm_data, rate = load_wav_pcm(file_path, TARGET_SAMPLE_RATE)
                print(f"[+] Slot {idx}: '{display_name}' <- {os.path.basename(file_path)}")
                print(f"    Dung lượng: {len(pcm_data):,} bytes ({len(pcm_data)/rate:.2f}s @ {rate}Hz)")
            except Exception as e:
                print(f"[!] Lỗi đọc file {file_path}: {e}. Sử dụng âm mẫu dự phòng.")
                pcm_data = [128] * 1600
                rate = 16000
        else:
            print(f"[-] Slot {idx}: Không tìm thấy file. Dùng âm đệm 0x80.")
            pcm_data = [128] * 1600
            rate = 16000

        length = len(pcm_data)
        name_bytes = display_name.encode('utf-8')[:31].ljust(32, b'\x00')
        slot_offset = 8 + idx * 44

        # Ghi metadata vào header
        struct.pack_into('<IIHH32s', header_buf, slot_offset, curr_offset, length, rate, 0, name_bytes)

        pcm_chunks.append(bytes(pcm_data))
        slot_info_list.append((display_name, curr_offset, length, rate))
        curr_offset += length

    final_bin = bytes(header_buf) + b''.join(pcm_chunks)

    with open(output_path, "wb") as f:
        f.write(final_bin)

    print("-" * 65)
    print(f"[OK] TAO THANH CONG: {output_path}")
    print(f"[+] Tong dung luong goi am thanh: {len(final_bin):,} bytes (~{len(final_bin)/1024:.1f} KB)")
    print(f"[+] Phan vung Flash muc tieu: {FLASH_OFFSET}")
    print("=" * 65)
    return output_path

def find_esptool():
    """Tìm đường dẫn esptool trên máy tính"""
    # 0. Ưu tiên esptool.exe đi kèm ngay trong thư mục tools (100% độc lập, không cần Python)
    local_tool = os.path.join(SCRIPT_DIR, "esptool.exe")
    if os.path.exists(local_tool):
        return local_tool

    # 1. Thử gọi trực tiếp từ PATH
    for cmd in ["esptool.exe", "esptool", "esptool.py"]:
        try:
            res = subprocess.run([cmd, "version"], capture_output=True, text=True)
            if res.returncode == 0:
                return cmd
        except Exception:
            pass

    # 2. Tìm trong PlatformIO penv
    pio_py = os.path.expanduser("~/.platformio/penv/Scripts/python.exe")
    pio_esptool = os.path.expanduser("~/.platformio/packages/tool-esptoolpy/esptool.py")
    if os.path.exists(pio_py) and os.path.exists(pio_esptool):
        return f'"{pio_py}" "{pio_esptool}"'

    # 3. Tìm trong Python Scripts
    python_dir = os.path.dirname(sys.executable)
    cand = os.path.join(python_dir, "Scripts", "esptool.exe")
    if os.path.exists(cand):
        return cand

    return None

def flash_to_esp32(bin_path=OUTPUT_BIN, port=None):
    """Nạp file binary vào phân vùng Flash 0x1E0000 của ESP32-C3"""
    if not os.path.exists(bin_path):
        print(f"[-] Không tìm thấy file {bin_path}! Đang tạo lại...")
        build_sound_bank_binary(bin_path)

    esptool = find_esptool()
    if not esptool:
        print("\n[!] Không tìm thấy công cụ esptool trên máy!")
        print("    Vui lòng cài đặt bằng lệnh: pip install esptool")
        print("    Hoặc mở file Audio_Studio.html trên trình duyệt Chrome để nạp qua Web Serial.")
        return False

    cmd = [esptool, "--chip", "esp32c3"]
    if port:
        cmd.extend(["--port", port])
    cmd.extend(["--baud", "460800", "write_flash", FLASH_OFFSET, bin_path])

    print("\n" + "=" * 65)
    print(f"[*] DANG NAP GOI AM THANH VAO COI XE QUA CONG USB...")
    print(f"   Lenh thuc thi: {' '.join(cmd)}")
    print("=" * 65)

    try:
        res = subprocess.run(cmd)
        if res.returncode == 0:
            print("\n" + "=" * 65)
            print("[SUCCESS] NAP AM THANH THANH CONG VAO COI XE!")
            print("   Ban co the rut cap USB, bat khoa xe va trai nghiem ngay tieng coi moi!")
            print("=" * 65)
            return True
        else:
            print(f"\n[-] Quá trình nạp thất bại với mã lỗi: {res.returncode}")
            return False
    except Exception as e:
        print(f"[-] Lỗi khi gọi esptool: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="ESP32-C3 Sound Bank Builder & Flasher")
    parser.add_argument("--build", action="store_true", help="Chỉ tạo file sound_bank.bin")
    parser.add_argument("--flash", action="store_true", help="Nạp sound_bank.bin vào ESP32-C3")
    parser.add_argument("--port", type=str, default=None, help="Cổng COM (ví dụ: COM3)")
    parser.add_argument("--output", type=str, default=OUTPUT_BIN, help="Đường dẫn file .bin xuất ra")

    args = parser.parse_args()

    if args.flash:
        build_sound_bank_binary(args.output)
        flash_to_esp32(args.output, args.port)
    else:
        build_sound_bank_binary(args.output)
        print("\n💡 GỢI Ý:")
        print("  - Để nạp vào còi xe, cắm cáp Type-C và chạy lệnh: python build_sound_bank.py --flash")
        print("  - Hoặc mở file Audio_Studio.html trên trình duyệt Chrome để nạp bằng giao diện đồ họa.")

if __name__ == "__main__":
    main()
