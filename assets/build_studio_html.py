#!/usr/bin/env python3
"""
Tự động biên dịch Audio_Studio.html với thư viện âm thanh nhúng sẵn Base64 và thanh điều chỉnh âm lượng
"""
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRESETS_JSON = os.path.join(SCRIPT_DIR, "presets_b64.json")
OUTPUT_TOOLS = os.path.join(SCRIPT_DIR, "..", "tools", "Audio_Studio.html")
OUTPUT_RELEASE = os.path.join(SCRIPT_DIR, "..", "release", "COI_XE_ESP32_STUDIO", "Audio_Studio.html")

with open(PRESETS_JSON, "r", encoding="utf-8") as f:
    presets_b64 = json.load(f)

html_template = r'''<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>ESP32-C3 Speed FX Audio Studio - Quản Lý Âm Thanh Còi Xe</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-darkest: #040913;
      --bg-editor: #071426;
      --bg-surface: #0c203d;
      --bg-surface-hover: #132e58;
      --border-color: #163664;
      --border-highlight: #00f0aa;
      --accent-neon: #00f0aa;
      --accent-neon-glow: rgba(0, 240, 170, 0.4);
      --accent-cyan: #00d2ff;
      --accent-cyan-glow: rgba(0, 210, 255, 0.35);
      --accent-danger: #ff4772;
      --accent-warning: #ffb834;
      --text-primary: #f0f6fc;
      --text-secondary: #91a8c9;
      --text-muted: #577196;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background: radial-gradient(circle at 50% 0%, #0d254c 0%, var(--bg-darkest) 75%);
      color: var(--text-primary);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      user-select: none;
      padding-bottom: 50px;
    }

    header {
      background: rgba(12, 32, 61, 0.92);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border-color);
      padding: 14px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
      position: sticky;
      top: 0;
      z-index: 100;
      box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .brand-icon {
      font-size: 32px;
      filter: drop-shadow(0 0 12px rgba(0, 240, 170, 0.6));
      animation: float-duck 3s ease-in-out infinite;
    }

    @keyframes float-duck {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-3px); }
    }

    .brand h1 {
      font-size: 19px;
      font-weight: 800;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 10px;
      letter-spacing: -0.3px;
    }

    .badge {
      background: rgba(0, 240, 170, 0.15);
      color: var(--accent-neon);
      border: 1px solid var(--accent-neon);
      font-size: 11px;
      font-weight: 700;
      padding: 3px 10px;
      border-radius: 999px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .badge-sub {
      background: rgba(0, 210, 255, 0.15);
      color: var(--accent-cyan);
      border: 1px solid var(--accent-cyan);
      font-size: 11px;
      font-weight: 600;
      padding: 3px 8px;
      border-radius: 6px;
      font-family: 'JetBrains Mono', monospace;
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .btn-action {
      background: linear-gradient(135deg, #103463 0%, #174b8f 100%);
      color: #fff;
      border: 1px solid #2866b8;
      padding: 9px 18px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .btn-action:hover {
      background: linear-gradient(135deg, #164684 0%, #2062ba 100%);
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(0, 150, 255, 0.3);
    }

    .btn-flash {
      background: linear-gradient(135deg, #00b884 0%, var(--accent-neon) 100%);
      color: #031326;
      border: none;
      font-weight: 700;
      box-shadow: 0 4px 14px var(--accent-neon-glow);
    }

    .btn-flash:hover {
      background: linear-gradient(135deg, #00d296 0%, #34ffd0 100%);
      box-shadow: 0 6px 20px rgba(0, 240, 170, 0.6);
      transform: translateY(-2px);
    }

    main {
      max-width: 1240px;
      width: 100%;
      margin: 24px auto 0;
      padding: 0 20px;
      display: flex;
      flex-direction: column;
      gap: 22px;
    }

    /* Slots bar */
    .slots-container {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 12px;
    }

    @media (max-width: 900px) {
      .slots-container {
        grid-template-columns: repeat(2, 1fr);
      }
      .slots-container > div:last-child {
        grid-column: span 2;
      }
    }

    @media (max-width: 540px) {
      .slots-container {
        grid-template-columns: 1fr;
      }
      .slots-container > div:last-child {
        grid-column: span 1;
      }
    }

    .slot-tab {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 14px 16px;
      cursor: pointer;
      display: flex;
      flex-direction: column;
      gap: 6px;
      position: relative;
      overflow: hidden;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .slot-tab:hover {
      background: var(--bg-surface-hover);
      border-color: #2b558f;
      transform: translateY(-2px);
    }

    .slot-tab.active {
      background: linear-gradient(135deg, #0e274b 0%, #15386b 100%);
      border-color: var(--accent-neon);
      box-shadow: 0 0 0 1px var(--accent-neon), 0 8px 24px rgba(0, 240, 170, 0.2);
    }

    .slot-tab.active::before {
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: var(--accent-neon);
      box-shadow: 0 0 8px var(--accent-neon);
    }

    .slot-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .slot-index {
      font-size: 11px;
      font-family: 'JetBrains Mono', monospace;
      font-weight: 800;
      color: var(--accent-neon);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .slot-name {
      font-size: 13px;
      font-weight: 700;
      color: #fff;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .slot-detail {
      font-size: 11px;
      color: var(--text-muted);
      font-family: 'JetBrains Mono', monospace;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    /* Waveform Editor Card */
    .editor-card {
      background: var(--bg-editor);
      border: 1px solid var(--border-color);
      border-radius: 18px;
      box-shadow: 0 18px 40px rgba(0, 0, 0, 0.5);
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }

    .editor-topbar {
      padding: 14px 22px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid rgba(22, 54, 100, 0.7);
      background: rgba(7, 20, 38, 0.7);
      flex-wrap: wrap;
      gap: 14px;
    }

    .editor-slot-label {
      font-size: 15px;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .slot-title-input {
      background: #040d1a;
      border: 1px solid var(--border-color);
      border-radius: 6px;
      color: #fff;
      font-family: inherit;
      font-size: 14px;
      font-weight: 600;
      padding: 5px 12px;
      outline: none;
      transition: border-color 0.2s;
      width: 220px;
    }

    .slot-title-input:focus {
      border-color: var(--accent-cyan);
    }

    .editor-tools {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }

    .btn-tool {
      background: #0d2242;
      border: 1px solid #1a3c6e;
      color: var(--text-secondary);
      padding: 7px 14px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }

    .btn-tool:hover {
      background: #143566;
      color: #fff;
      border-color: #2b558f;
    }

    .btn-tool.preset {
      background: linear-gradient(135deg, rgba(0, 210, 255, 0.15) 0%, rgba(0, 240, 170, 0.15) 100%);
      color: var(--accent-neon);
      border-color: var(--accent-neon);
    }

    .btn-tool.preset:hover {
      background: linear-gradient(135deg, rgba(0, 210, 255, 0.25) 0%, rgba(0, 240, 170, 0.25) 100%);
      box-shadow: 0 0 14px var(--accent-neon-glow);
    }

    /* Waveform Canvas Area */
    .canvas-container {
      position: relative;
      width: 100%;
      height: 240px;
      background: #030710;
      overflow: hidden;
    }

    canvas {
      width: 100%;
      height: 100%;
      display: block;
      cursor: crosshair;
    }

    .trim-dimmer-left {
      position: absolute;
      top: 0;
      bottom: 0;
      left: 0;
      background: rgba(3, 7, 16, 0.7);
      border-right: 2px solid var(--accent-danger);
    }

    .trim-dimmer-right {
      position: absolute;
      top: 0;
      bottom: 0;
      right: 0;
      background: rgba(3, 7, 16, 0.7);
      border-left: 2px solid var(--accent-danger);
    }

    .playhead-line {
      position: absolute;
      top: 0;
      bottom: 0;
      width: 2px;
      background: #ffffff;
      box-shadow: 0 0 8px #ffffff;
      pointer-events: none;
      display: none;
      z-index: 5;
    }

    .editor-controls {
      padding: 14px 22px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-top: 1px solid rgba(22, 54, 100, 0.7);
      background: rgba(7, 20, 38, 0.9);
      flex-wrap: wrap;
      gap: 14px;
    }

    .playback-group {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .btn-play {
      background: linear-gradient(135deg, var(--accent-neon) 0%, #00b884 100%);
      color: #04101d;
      border: none;
      width: 46px;
      height: 46px;
      border-radius: 50%;
      font-size: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      box-shadow: 0 4px 14px var(--accent-neon-glow);
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .btn-play:hover {
      transform: scale(1.08);
      box-shadow: 0 6px 20px rgba(0, 240, 170, 0.6);
    }

    .time-box {
      font-family: 'JetBrains Mono', monospace;
      font-size: 13px;
      color: var(--accent-neon);
      background: #040d1a;
      padding: 9px 16px;
      border-radius: 8px;
      border: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .time-label {
      color: var(--text-muted);
      font-size: 11px;
    }

    /* Volume Slider Group */
    .volume-group {
      display: flex;
      align-items: center;
      gap: 10px;
      background: #040d1a;
      padding: 7px 14px;
      border-radius: 8px;
      border: 1px solid var(--border-color);
    }

    .vol-slider {
      -webkit-appearance: none;
      appearance: none;
      width: 110px;
      height: 6px;
      border-radius: 3px;
      background: #143566;
      outline: none;
      cursor: pointer;
    }

    .vol-slider::-webkit-slider-thumb {
      -webkit-appearance: none;
      appearance: none;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: var(--accent-neon);
      cursor: pointer;
      box-shadow: 0 0 8px var(--accent-neon-glow);
      transition: transform 0.15s;
    }

    .vol-slider::-webkit-slider-thumb:hover {
      transform: scale(1.2);
    }

    .vol-badge {
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      font-weight: 700;
      color: var(--accent-neon);
      min-width: 44px;
      text-align: right;
    }

    .btn-boost {
      background: linear-gradient(135deg, #ff9500 0%, #ff4772 100%);
      color: #fff;
      border: none;
      padding: 4px 10px;
      border-radius: 5px;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.2s;
    }

    .btn-boost:hover {
      filter: brightness(1.2);
      transform: translateY(-1px);
    }

    .speed-group {
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .btn-speed {
      background: #0d2242;
      border: 1px solid var(--border-color);
      color: var(--text-secondary);
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s;
    }

    .btn-speed.active {
      border-color: var(--accent-neon);
      color: var(--accent-neon);
      background: rgba(0, 240, 170, 0.15);
    }

    /* Modal Preset Library */
    .modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(2, 6, 14, 0.82);
      backdrop-filter: blur(8px);
      z-index: 1000;
      display: flex;
      align-items: center;
      justify-content: center;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.25s ease;
      padding: 20px;
    }

    .modal-backdrop.open {
      opacity: 1;
      pointer-events: auto;
    }

    .modal-card {
      background: var(--bg-editor);
      border: 1px solid var(--border-color);
      border-radius: 20px;
      max-width: 840px;
      width: 100%;
      max-height: 85vh;
      display: flex;
      flex-direction: column;
      box-shadow: 0 24px 60px rgba(0, 0, 0, 0.7);
      overflow: hidden;
      transform: translateY(20px);
      transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .modal-backdrop.open .modal-card {
      transform: translateY(0);
    }

    .modal-header {
      padding: 18px 24px;
      background: rgba(12, 32, 61, 0.8);
      border-bottom: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .modal-title {
      font-size: 17px;
      font-weight: 800;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .btn-close {
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-size: 22px;
      cursor: pointer;
      line-height: 1;
    }

    .btn-close:hover { color: #fff; }

    .modal-body {
      padding: 20px 24px;
      overflow-y: auto;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
      gap: 14px;
    }

    .preset-item {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      transition: all 0.2s;
    }

    .preset-item:hover {
      background: var(--bg-surface-hover);
      border-color: var(--accent-cyan);
      transform: translateY(-2px);
    }

    .preset-title {
      font-size: 14px;
      font-weight: 700;
      color: #fff;
    }

    .preset-desc {
      font-size: 11px;
      color: var(--text-secondary);
      line-height: 1.4;
      flex: 1;
    }

    .preset-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-top: 4px;
    }

    .btn-preset-play {
      background: #143566;
      border: 1px solid #285596;
      color: #fff;
      padding: 6px 10px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .btn-preset-play:hover {
      background: #1c4b8f;
      color: var(--accent-neon);
    }

    .btn-preset-select {
      background: linear-gradient(135deg, #00b884 0%, var(--accent-neon) 100%);
      color: #031326;
      border: none;
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      flex: 1;
      text-align: center;
    }

    .btn-preset-select:hover {
      filter: brightness(1.1);
    }

    /* Instructions & Info Cards */
    .info-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }

    @media (max-width: 768px) {
      .info-grid { grid-template-columns: 1fr; }
    }

    .info-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 14px;
      padding: 18px 22px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .info-title {
      font-size: 15px;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .info-list {
      list-style-position: inside;
      font-size: 13px;
      color: var(--text-secondary);
      line-height: 1.6;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .info-list strong { color: var(--text-primary); }

    /* Toast Notification */
    .toast {
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: rgba(12, 32, 61, 0.95);
      border: 1px solid var(--accent-neon);
      box-shadow: 0 8px 30px var(--accent-neon-glow);
      color: #fff;
      padding: 12px 20px;
      border-radius: 10px;
      font-size: 13px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 10px;
      transform: translateY(100px);
      opacity: 0;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      z-index: 2000;
      backdrop-filter: blur(10px);
    }

    .toast.show {
      transform: translateY(0);
      opacity: 1;
    }
  </style>
</head>
<body>

  <header>
    <div class="brand">
      <div class="brand-icon">🦆</div>
      <div>
        <h1>ESP32-C3 SPEED FX STUDIO <span class="badge">Standalone 100%</span></h1>
      </div>
    </div>

    <div class="header-actions">
      <span class="badge-sub">Flash: 0x1E0000</span>
      <button class="btn-action" onclick="openPresetModal()">
        <span>🎵</span> Thư Viện Mẫu (9+)
      </button>
      <button class="btn-action" onclick="exportSoundBankBin()">
        <span>📦</span> Xuất sound_bank.bin
      </button>
      <button class="btn-action btn-flash" onclick="handleFlashClick()">
        <span>⚡</span> Nạp Còi Xe (USB)
      </button>
    </div>
  </header>

  <main>
    <!-- 5 Slot Cards -->
    <div class="slots-container" id="slotsContainer">
      <!-- Generated via JS -->
    </div>

    <!-- Waveform Editor -->
    <div class="editor-card">
      <div class="editor-topbar">
        <div class="editor-slot-label">
          <span id="currentSlotBadge" class="badge">SLOT 0</span>
          <input type="text" id="slotTitleInput" class="slot-title-input" value="Vit Coi Xe Chuan (Duck 2)" onchange="updateCurrentSlotName(this.value)">
        </div>

        <div class="editor-tools">
          <input type="file" id="fileInput" accept="audio/*,.mp3,.wav,.ogg,.m4a" style="display:none" onchange="handleFileSelected(event)">
          <button class="btn-tool preset" onclick="openPresetModal()">
            <span>✨</span> Chọn mẫu có sẵn
          </button>
          <button class="btn-tool" onclick="document.getElementById('fileInput').click()">
            <span>📁</span> Đổi bằng file MP3/WAV
          </button>
          <button class="btn-tool" onclick="autoTrimSilence()">
            <span>✂️</span> Cắt khoảng lặng
          </button>
          <button class="btn-tool" onclick="normalizeVolume()">
            <span>🔊</span> Chuẩn hóa Peak 98%
          </button>
          <button class="btn-tool" onclick="downloadCurrentSlotWav()">
            <span>💾</span> Xuất WAV Slot này
          </button>
        </div>
      </div>

      <!-- Canvas Waveform -->
      <div class="canvas-container" id="canvasContainer">
        <canvas id="waveCanvas"></canvas>
        <div class="playhead-line" id="playhead"></div>
        <div class="trim-dimmer-left" id="trimDimmerLeft" style="width: 0px;"></div>
        <div class="trim-dimmer-right" id="trimDimmerRight" style="width: 0px;"></div>
      </div>

      <!-- Editor Controls -->
      <div class="editor-controls">
        <div class="playback-group">
          <button class="btn-play" id="btnPlay" onclick="togglePlay()" title="Nghe thử (Spacebar)">
            <span id="playIcon">▶</span>
          </button>
          <div class="time-box">
            <span class="time-label">VỊ TRÍ:</span>
            <span id="timeBox">00:00.00 / 00:00.00</span>
          </div>
        </div>

        <!-- Volume Slider Control -->
        <div class="volume-group">
          <span style="font-size:12px; color:var(--text-muted); font-weight:600;">🔊 ÂM LƯỢNG:</span>
          <input type="range" id="volSlider" class="vol-slider" min="10" max="250" value="100" step="5" oninput="setVolume(this.value)" title="Kéo để chỉnh âm lượng phát và xuất ra còi">
          <span id="volBadge" class="vol-badge">100%</span>
          <button class="btn-boost" onclick="boostVolume()" title="Kích âm lượng lên 150%">🚀 150%</button>
        </div>

        <div class="speed-group">
          <span style="font-size:12px; color:var(--text-muted); font-weight:600;">TỐC ĐỘ:</span>
          <button class="btn-speed" onclick="setSpeed(0.75, this)">0.75x</button>
          <button class="btn-speed active" onclick="setSpeed(1.0, this)">1.0x</button>
          <button class="btn-speed" onclick="setSpeed(1.25, this)">1.25x</button>
          <button class="btn-speed" onclick="setSpeed(1.5, this)">1.5x</button>
        </div>
      </div>
    </div>

    <!-- Instruction Info Cards -->
    <div class="info-grid">
      <div class="info-card">
        <div class="info-title"><span>🏍️</span> Cách Đổi Tiếng Trực Tiếp Trên Xe Máy</div>
        <ol class="info-list">
          <li><strong>Bật chìa khóa xe:</strong> Còi phát ngay lập tức tiếng bạn đã chọn lần trước (không trễ 1 mili-giây).</li>
          <li><strong>Đổi tiếng nhanh:</strong> Nhấn nhả nút phụ trên tay lái (nối vào GPIO1) hoặc nút BOOT trên mạch.</li>
          <li>Mỗi lần nhấn nhả, còi nhảy sang tiếng tiếp theo (0 → 1 → 2 → 3 → 4) và phát thử ngay tiếng mới.</li>
          <li>Còi tự động lưu nhớ vĩnh viễn vào NVS & RTC SRAM (tắt chìa khóa bật lại vẫn nhớ đúng tiếng).</li>
        </ol>
      </div>

      <div class="info-card">
        <div class="info-title"><span>⚡</span> 2 Bước Nạp Âm Thanh Mới Vào Còi Xe</div>
        <ol class="info-list">
          <li><strong>Bước 1:</strong> Chọn tiếng, kéo thanh <strong>Âm Lượng (100% - 250%)</strong> hoặc cắt đoạn ưng ý, sau đó bấm <code>Xuất sound_bank.bin</code>.</li>
          <li><strong>Bước 2:</strong> Cắm cáp USB Type-C từ còi xe vào máy tính và nhấp đúp file <code>nap_tieng_coi.bat</code> để nạp trong 3 giây.</li>
          <li><strong>Bảo mật 100%:</strong> Quá trình nạp chỉ ghi đè phân vùng dữ liệu âm thanh <code>0x1E0000</code>, tuyệt đối không chạm vào hay làm lộ mã nguồn vi điều khiển.</li>
        </ol>
      </div>
    </div>
  </main>

  <!-- Modal Preset Library -->
  <div class="modal-backdrop" id="presetModal">
    <div class="modal-card">
      <div class="modal-header">
        <div class="modal-title"><span>🎵</span> Thư Viện Âm Mẫu Có Sẵn Cho Còi Xe</div>
        <button class="btn-close" onclick="closePresetModal()">&times;</button>
      </div>
      <div class="modal-body" id="presetListContainer">
        <!-- Rendered via JS -->
      </div>
    </div>
  </div>

  <div class="toast" id="toast">Thông báo</div>

  <script>
    // Dữ liệu Base64 nhúng sẵn 100% của toàn bộ âm thanh
    const EMBEDDED_PRESETS = ''' + json.dumps(presets_b64) + r''';

    const PRESET_CATALOG = [
      { key: "slot0_vit_chuan.wav", name: "Vịt Còi Xe Chuẩn (Duck 2)", desc: "Âm vịt còi chuẩn to đanh, giòn dứt khoát, âm lượng cực đại, đã tinh chỉnh triệt tiêu đỉnh sụt áp." },
      { key: "slot1_vit_don.wav", name: "Vịt Kêu Đơn (Duck 1)", desc: "Tiếng quạc đanh giòn, 1 nhịp nhanh gọn, phù hợp cảnh báo người đi đường lịch sự." },
      { key: "slot2_coi_doi.wav", name: "Vịt Còi Đôi (Double Quack)", desc: "Hai nhịp quạc-quạc nối tiếp, âm vang rõ nét, phong cách độc đáo." },
      { key: "slot3_bo_rong.wav", name: "Bò Rống (Cow Mooing)", desc: "Tiếng bò rống trầm ấm, vang xa, gây chú ý mạnh trên đường phố." },
      { key: "slot4_canh_sat.wav", name: "Còi Cảnh Sát (Police Siren)", desc: "Âm hú còi tuần tra báo động dồn dập, nổi bật giữa đám đông." },
      { key: "sample_coi_bim_bim.wav", name: "Còi Xe Máy Bim Bim", desc: "Hợp âm kép còi xe máy kinh điển đanh thép, độ nhạy cao." },
      { key: "sample_tau_hoa.wav", name: "Còi Tàu Hỏa (Train Horn)", desc: "Hợp âm kèn tàu hỏa ba bè hùng dũng, trầm hùng, âm vang cực xa." },
      { key: "sample_laser_blaster.wav", name: "Súng Laser Không Gian", desc: "Tiếng súng viễn tưởng Sci-Fi vui nhộn, âm thanh tần số cao đanh giòn." },
      { key: "sample_vit_cuoi.wav", name: "Vịt Donald Cười", desc: "Tràng cười quác quác ngộ nghĩnh, tạo cảm giác thân thiện, hóm hỉnh." }
    ];

    // Cấu trúc 5 Slot chính của thiết bị
    const slots = [
      { name: "Vit Coi Xe Chuan (Duck 2)", pcm: null, sampleRate: 16000, buffer: null, trimStart: 0, trimEnd: 0, volume: 100 },
      { name: "Vit Keu Don (Duck 1)", pcm: null, sampleRate: 16000, buffer: null, trimStart: 0, trimEnd: 0, volume: 100 },
      { name: "Vit Coi Doi (Double Quack)", pcm: null, sampleRate: 16000, buffer: null, trimStart: 0, trimEnd: 0, volume: 100 },
      { name: "Bo Rong (Cow Mooing)", pcm: null, sampleRate: 16000, buffer: null, trimStart: 0, trimEnd: 0, volume: 100 },
      { name: "Coi Canh Sat (Police Siren)", pcm: null, sampleRate: 16000, buffer: null, trimStart: 0, trimEnd: 0, volume: 100 }
    ];

    let currentSlotIdx = 0;
    let audioCtx = null;
    let currentBuffer = null;
    let currentSource = null;
    let currentGainNode = null;
    let isPlaying = false;
    let playStartTime = 0;
    let playStartOffset = 0;
    let playSpeed = 1.0;
    let animFrameId = null;

    let trimStart = 0;
    let trimEnd = 1;
    let isDraggingTrim = null;

    function getAudioContext() {
      if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      }
      if (audioCtx.state === 'suspended') {
        audioCtx.resume();
      }
      return audioCtx;
    }

    function showToast(msg, duration = 3000) {
      const t = document.getElementById('toast');
      t.textContent = msg;
      t.classList.add('show');
      setTimeout(() => t.classList.remove('show'), duration);
    }

    function base64ToArrayBuffer(base64) {
      const binaryString = window.atob(base64);
      const len = binaryString.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      return bytes.buffer;
    }

    function renderSlotsUI() {
      const container = document.getElementById('slotsContainer');
      container.innerHTML = '';
      slots.forEach((s, i) => {
        const div = document.createElement('div');
        div.className = `slot-tab ${i === currentSlotIdx ? 'active' : ''}`;
        div.id = `slotTab${i}`;
        div.onclick = () => selectSlot(i);

        const dur = s.buffer ? `${s.buffer.duration.toFixed(2)}s` : '--';
        const vol = s.volume ? `${s.volume}%` : '100%';
        div.innerHTML = `
          <div class="slot-header">
            <span class="slot-index">SLOT ${i}</span>
            <span class="slot-detail">${dur} • ${vol}</span>
          </div>
          <div class="slot-name" id="slotNameText${i}">${s.name}</div>
        `;
        container.appendChild(div);
      });
    }

    function selectSlot(idx) {
      stopPlayback();
      currentSlotIdx = idx;
      for (let i = 0; i < 5; i++) {
        const el = document.getElementById(`slotTab${i}`);
        if (el) el.classList.toggle('active', i === idx);
      }
      document.getElementById('currentSlotBadge').textContent = `SLOT ${idx}`;
      document.getElementById('slotTitleInput').value = slots[idx].name;

      currentBuffer = slots[idx].buffer;
      trimStart = slots[idx].trimStart || 0;
      trimEnd = slots[idx].trimEnd || (currentBuffer ? currentBuffer.duration : 1);

      // Cập nhật thanh Volume
      const vol = slots[idx].volume || 100;
      document.getElementById('volSlider').value = vol;
      document.getElementById('volBadge').textContent = `${vol}%`;

      drawWaveform();
      updateTimeDisplay();
      updateTrimDimmer();
    }

    function updateCurrentSlotName(newName) {
      newName = newName.trim();
      if (!newName) newName = `Slot ${currentSlotIdx}`;
      slots[currentSlotIdx].name = newName;
      document.getElementById(`slotNameText${currentSlotIdx}`).textContent = newName;
    }

    // Xử lý điều chỉnh âm lượng
    function setVolume(val) {
      val = parseInt(val);
      slots[currentSlotIdx].volume = val;
      document.getElementById('volBadge').textContent = `${val}%`;

      // Cập nhật GainNode nếu đang phát trực tiếp
      if (currentGainNode) {
        currentGainNode.gain.value = val / 100.0;
      }

      recalculatePCM();
      renderSlotsUI();
    }

    function boostVolume() {
      setVolume(150);
      document.getElementById('volSlider').value = 150;
      showToast("🚀 Đã kích âm lượng lên 150%!");
    }

    async function initSlotsAudio() {
      const defaultKeys = [
        "slot0_vit_chuan.wav",
        "slot1_vit_don.wav",
        "slot2_coi_doi.wav",
        "slot3_bo_rong.wav",
        "slot4_canh_sat.wav"
      ];

      for (let i = 0; i < 5; i++) {
        const k = defaultKeys[i];
        if (EMBEDDED_PRESETS[k]) {
          try {
            const ab = base64ToArrayBuffer(EMBEDDED_PRESETS[k]);
            const buf = await getAudioContext().decodeAudioData(ab);
            slots[i].buffer = buf;
            slots[i].trimStart = 0;
            slots[i].trimEnd = buf.duration;
            slots[i].volume = 100;
            slots[i].pcm = bufferToPCM8(buf);
          } catch (e) {
            console.error("Lỗi giải mã audio slot " + i, e);
          }
        }
      }

      renderSlotsUI();
      selectSlot(0);
    }

    // Playback Engine với Volume Gain Node
    function togglePlay() {
      if (isPlaying) {
        stopPlayback();
      } else {
        startPlayback();
      }
    }

    function startPlayback() {
      if (!currentBuffer) return;
      stopPlayback();

      const actx = getAudioContext();
      currentSource = actx.createBufferSource();
      currentSource.buffer = currentBuffer;
      currentSource.playbackRate.value = playSpeed;

      // Tạo Gain Node điều chỉnh âm lượng
      currentGainNode = actx.createGain();
      const currentVol = (slots[currentSlotIdx].volume || 100) / 100.0;
      currentGainNode.gain.value = currentVol;

      currentSource.connect(currentGainNode);
      currentGainNode.connect(actx.destination);

      const offset = trimStart;
      const duration = Math.max(0.01, trimEnd - trimStart);

      playStartTime = actx.currentTime;
      playStartOffset = offset;

      currentSource.start(0, offset, duration);
      isPlaying = true;
      document.getElementById('playIcon').textContent = '⏹';

      currentSource.onended = () => {
        stopPlayback();
      };

      trackPlayhead();
    }

    function stopPlayback() {
      if (currentSource) {
        try { currentSource.stop(); } catch (e) {}
        currentSource = null;
      }
      currentGainNode = null;
      isPlaying = false;
      document.getElementById('playIcon').textContent = '▶';
      document.getElementById('playhead').style.display = 'none';
      if (animFrameId) cancelAnimationFrame(animFrameId);
    }

    function trackPlayhead() {
      if (!isPlaying || !currentBuffer) return;
      const actx = getAudioContext();
      const elapsed = (actx.currentTime - playStartTime) * playSpeed;
      const currentPos = playStartOffset + elapsed;

      const dur = currentBuffer.duration;
      const pct = Math.max(0, Math.min(1, currentPos / dur));

      const playheadEl = document.getElementById('playhead');
      playheadEl.style.display = 'block';
      playheadEl.style.left = `${pct * 100}%`;

      updateTimeDisplay(currentPos);

      if (currentPos < trimEnd) {
        animFrameId = requestAnimationFrame(trackPlayhead);
      } else {
        stopPlayback();
      }
    }

    function setSpeed(spd, btn) {
      playSpeed = spd;
      document.querySelectorAll('.btn-speed').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      if (isPlaying) {
        startPlayback();
      }
    }

    function updateTimeDisplay(curTime = trimStart) {
      if (!currentBuffer) return;
      const totalDur = currentBuffer.duration;
      const selDur = Math.max(0, trimEnd - trimStart);
      document.getElementById('timeBox').textContent = 
        `${formatTime(curTime)} / ${formatTime(totalDur)} (Cắt: ${selDur.toFixed(2)}s)`;
    }

    function formatTime(sec) {
      const m = Math.floor(sec / 60);
      const s = Math.floor(sec % 60);
      const cs = Math.floor((sec % 1) * 100);
      return `${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}.${String(cs).padStart(2,'0')}`;
    }

    function drawWaveform() {
      const canvas = document.getElementById('waveCanvas');
      const ctx = canvas.getContext('2d');
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);

      const w = rect.width;
      const h = rect.height;

      ctx.fillStyle = '#030710';
      ctx.fillRect(0, 0, w, h);

      if (!currentBuffer) return;

      const ch = currentBuffer.getChannelData(0);
      const step = Math.ceil(ch.length / w);
      const amp = h / 2;

      ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
      ctx.beginPath();
      ctx.moveTo(0, amp);
      ctx.lineTo(w, amp);
      ctx.stroke();

      const gradient = ctx.createLinearGradient(0, 0, 0, h);
      gradient.addColorStop(0, '#00d2ff');
      gradient.addColorStop(0.5, '#00f0aa');
      gradient.addColorStop(1, '#00d2ff');

      ctx.fillStyle = gradient;

      for (let x = 0; x < w; x++) {
        let min = 1.0;
        let max = -1.0;
        for (let j = 0; j < step; j++) {
          const val = ch[x * step + j] || 0;
          if (val < min) min = val;
          if (val > max) max = val;
        }
        const barH = Math.max(2, (max - min) * amp * 0.95);
        ctx.fillRect(x, amp - barH / 2, 1.2, barH);
      }
    }

    function updateTrimDimmer() {
      if (!currentBuffer) return;
      const dur = currentBuffer.duration;
      const leftPct = (trimStart / dur) * 100;
      const rightPct = (1 - (trimEnd / dur)) * 100;

      document.getElementById('trimDimmerLeft').style.width = `${leftPct}%`;
      document.getElementById('trimDimmerRight').style.width = `${rightPct}%`;
    }

    const canvasEl = document.getElementById('canvasContainer');
    canvasEl.addEventListener('mousedown', (e) => {
      if (!currentBuffer) return;
      const rect = canvasEl.getBoundingClientRect();
      const clickX = e.clientX - rect.left;
      const pct = clickX / rect.width;
      const dur = currentBuffer.duration;
      const clickTime = pct * dur;

      const startX = (trimStart / dur) * rect.width;
      const endX = (trimEnd / dur) * rect.width;

      if (Math.abs(clickX - startX) < 18) {
        isDraggingTrim = 'left';
      } else if (Math.abs(clickX - endX) < 18) {
        isDraggingTrim = 'right';
      } else {
        trimStart = Math.min(clickTime, trimEnd - 0.05);
        isDraggingTrim = 'left';
      }
      updateTrimDimmer();
      updateTimeDisplay();
    });

    window.addEventListener('mousemove', (e) => {
      if (!isDraggingTrim || !currentBuffer) return;
      const rect = canvasEl.getBoundingClientRect();
      const clickX = Math.max(0, Math.min(rect.width, e.clientX - rect.left));
      const pct = clickX / rect.width;
      const time = pct * currentBuffer.duration;

      if (isDraggingTrim === 'left') {
        trimStart = Math.min(time, trimEnd - 0.05);
      } else if (isDraggingTrim === 'right') {
        trimEnd = Math.max(time, trimStart + 0.05);
      }
      slots[currentSlotIdx].trimStart = trimStart;
      slots[currentSlotIdx].trimEnd = trimEnd;
      updateTrimDimmer();
      updateTimeDisplay();
    });

    window.addEventListener('mouseup', () => {
      if (isDraggingTrim) {
        isDraggingTrim = null;
        recalculatePCM();
      }
    });

    function autoTrimSilence() {
      if (!currentBuffer) return;
      const ch = currentBuffer.getChannelData(0);
      const len = ch.length;
      let startIdx = 0;
      let endIdx = len - 1;

      while (startIdx < len && Math.abs(ch[startIdx]) < 0.02) {
        startIdx++;
      }
      while (endIdx > startIdx && Math.abs(ch[endIdx]) < 0.02) {
        endIdx--;
      }

      trimStart = (startIdx / len) * currentBuffer.duration;
      trimEnd = (endIdx / len) * currentBuffer.duration;
      slots[currentSlotIdx].trimStart = trimStart;
      slots[currentSlotIdx].trimEnd = trimEnd;

      updateTrimDimmer();
      updateTimeDisplay();
      recalculatePCM();
      showToast("✂️ Đã tự động cắt sạch khoảng lặng đầu & cuối!");
    }

    function normalizeVolume() {
      if (!currentBuffer) return;
      const ch = currentBuffer.getChannelData(0);
      let mx = 0;
      for (let i = 0; i < ch.length; i++) {
        const a = Math.abs(ch[i]);
        if (a > mx) mx = a;
      }
      if (mx > 0.01) {
        const factor = 0.98 / mx;
        for (let i = 0; i < ch.length; i++) {
          ch[i] = Math.max(-1.0, Math.min(1.0, ch[i] * factor));
        }
        drawWaveform();
        recalculatePCM();
        showToast("🔊 Đã chuẩn hóa âm lượng đạt đỉnh 98%!");
      }
    }

    // Tính toán lại mảng PCM 8-bit có nhân hệ số Volume
    function recalculatePCM() {
      if (!currentBuffer) return;
      const ch = currentBuffer.getChannelData(0);
      const rate = currentBuffer.sampleRate;
      const startSample = Math.floor(trimStart * rate);
      const endSample = Math.floor(trimEnd * rate);
      const numSamples = Math.max(1, endSample - startSample);

      const targetRate = 16000;
      const targetLen = Math.floor(numSamples * (targetRate / rate));
      const pcm = new Uint8Array(160 + targetLen);

      pcm.fill(128, 0, 160); // 10ms đệm 0x80 chống bụp loa

      // Nhân hệ số Volume đã chỉnh
      const volFactor = (slots[currentSlotIdx].volume || 100) / 100.0;
      const ratio = numSamples / targetLen;

      for (let i = 0; i < targetLen; i++) {
        const srcIdx = startSample + Math.floor(i * ratio);
        const s = ch[Math.min(srcIdx, ch.length - 1)] * volFactor;
        // Chặn cận mềm [0, 255]
        pcm[160 + i] = Math.max(0, Math.min(255, Math.round((s * 127) + 128)));
      }

      slots[currentSlotIdx].pcm = pcm;
      slots[currentSlotIdx].sampleRate = targetRate;
      renderSlotsUI();
    }

    function bufferToPCM8(buf) {
      const ch = buf.getChannelData(0);
      const pcm = new Uint8Array(ch.length);
      for (let i = 0; i < ch.length; i++) {
        pcm[i] = Math.max(0, Math.min(255, Math.round((ch[i] * 127) + 128)));
      }
      return pcm;
    }

    async function handleFileSelected(e) {
      const file = e.target.files[0];
      if (!file) return;

      try {
        const ab = await file.arrayBuffer();
        const decoded = await getAudioContext().decodeAudioData(ab);

        slots[currentSlotIdx].buffer = decoded;
        slots[currentSlotIdx].trimStart = 0;
        slots[currentSlotIdx].trimEnd = decoded.duration;
        slots[currentSlotIdx].name = file.name.replace(/\.[^/.]+$/, "");
        slots[currentSlotIdx].volume = 100;

        selectSlot(currentSlotIdx);
        autoTrimSilence();
        normalizeVolume();
        showToast(`✅ Đã nạp '${file.name}' vào Slot ${currentSlotIdx}!`);
      } catch (err) {
        alert("Lỗi giải mã file âm thanh: " + err.message);
      }
      e.target.value = '';
    }

    function openPresetModal() {
      const container = document.getElementById('presetListContainer');
      container.innerHTML = '';

      PRESET_CATALOG.forEach(p => {
        const item = document.createElement('div');
        item.className = 'preset-item';
        item.innerHTML = `
          <div class="preset-title">${p.name}</div>
          <div class="preset-desc">${p.desc}</div>
          <div class="preset-actions">
            <button class="btn-preset-play" onclick="previewPreset('${p.key}')">▶ Nghe thử</button>
            <button class="btn-preset-select" onclick="applyPresetToCurrentSlot('${p.key}', '${p.name}')">✅ Chọn vào Slot ${currentSlotIdx}</button>
          </div>
        `;
        container.appendChild(item);
      });

      document.getElementById('presetModal').classList.add('open');
    }

    function closePresetModal() {
      document.getElementById('presetModal').classList.remove('open');
      stopPlayback();
    }

    let previewSource = null;
    async function previewPreset(key) {
      stopPlayback();
      if (previewSource) {
        try { previewSource.stop(); } catch(e){}
      }
      if (!EMBEDDED_PRESETS[key]) return;
      const ab = base64ToArrayBuffer(EMBEDDED_PRESETS[key]);
      const buf = await getAudioContext().decodeAudioData(ab);
      const actx = getAudioContext();
      previewSource = actx.createBufferSource();
      previewSource.buffer = buf;
      previewSource.connect(actx.destination);
      previewSource.start();
    }

    async function applyPresetToCurrentSlot(key, name) {
      closePresetModal();
      if (!EMBEDDED_PRESETS[key]) return;

      const ab = base64ToArrayBuffer(EMBEDDED_PRESETS[key]);
      const buf = await getAudioContext().decodeAudioData(ab);

      slots[currentSlotIdx].buffer = buf;
      slots[currentSlotIdx].trimStart = 0;
      slots[currentSlotIdx].trimEnd = buf.duration;
      slots[currentSlotIdx].name = name;
      slots[currentSlotIdx].volume = 100;

      selectSlot(currentSlotIdx);
      recalculatePCM();
      showToast(`🎉 Đã gán '${name}' vào Slot ${currentSlotIdx}!`);
    }

    // Xuất gói nhị phân sound_bank.bin
    function exportSoundBankBin() {
      let totalPcmLen = 0;
      for (let i = 0; i < 5; i++) {
        if (!slots[i].pcm) {
          recalculatePCM();
        }
        totalPcmLen += slots[i].pcm.length;
      }

      const buffer = new Uint8Array(512 + totalPcmLen);
      const view = new DataView(buffer.buffer);

      view.setUint32(0, 0x4B435544, true); // Magic 'DUCK'
      view.setUint16(4, 1, true);          // Version 1
      view.setUint16(6, 5, true);          // 5 Slots

      let currOffset = 512;
      for (let i = 0; i < 5; i++) {
        const s = slots[i];
        const slotHeadOffset = 8 + i * 44;
        const pcmLen = s.pcm.length;

        view.setUint32(slotHeadOffset, currOffset, true);
        view.setUint32(slotHeadOffset + 4, pcmLen, true);
        view.setUint16(slotHeadOffset + 8, s.sampleRate, true);
        view.setUint16(slotHeadOffset + 10, 0, true);

        const nameBytes = new TextEncoder().encode(s.name.slice(0, 31));
        buffer.set(nameBytes, slotHeadOffset + 12);

        buffer.set(s.pcm, currOffset);
        currOffset += pcmLen;
      }

      const blob = new Blob([buffer], { type: 'application/octet-stream' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'sound_bank.bin';
      a.click();
      showToast(`📦 Đã xuất gói sound_bank.bin (${(buffer.length/1024).toFixed(1)} KB)!`);
    }

    function downloadCurrentSlotWav() {
      const s = slots[currentSlotIdx];
      if (!s.pcm) recalculatePCM();

      const pcmBytes = s.pcm;
      const sampleRate = s.sampleRate;
      const header = new ArrayBuffer(44);
      const view = new DataView(header);
      const writeStr = (off, str) => { for (let i = 0; i < str.length; i++) view.setUint8(off + i, str.charCodeAt(i)); };

      writeStr(0, 'RIFF');
      view.setUint32(4, 36 + pcmBytes.length, true);
      writeStr(8, 'WAVE');
      writeStr(12, 'fmt ');
      view.setUint32(16, 16, true);
      view.setUint16(20, 1, true); // PCM
      view.setUint16(22, 1, true); // Mono
      view.setUint32(24, sampleRate, true);
      view.setUint32(28, sampleRate, true);
      view.setUint16(32, 1, true);
      view.setUint16(34, 8, true);
      writeStr(36, 'data');
      view.setUint32(40, pcmBytes.length, true);

      const blob = new Blob([header, pcmBytes], { type: 'audio/wav' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `slot${currentSlotIdx}_${s.name.replace(/\s+/g, '_')}.wav`;
      a.click();
      showToast(`🎵 Đã xuất file WAV cho Slot ${currentSlotIdx}!`);
    }

    async function handleFlashClick() {
      showToast("⏳ Đang chuẩn bị nạp âm thanh vào còi xe qua USB...");
      try {
        const resp = await fetch('/api/flash', { method: 'POST' });
        const res = await resp.json();
        if (resp.ok && res.success) {
          showToast("🎉 NẠP ÂM THANH THÀNH CÔNG VÀO CÒI XE!", 5000);
          return;
        }
      } catch (e) {}

      exportSoundBankBin();
      setTimeout(() => {
        alert("👉 HƯỚNG DẪN NẠP VÀO CÒI XE:\n\n1. File 'sound_bank.bin' vừa được tải về máy của bạn.\n2. Hãy cắm cáp USB Type-C từ còi xe vào máy tính.\n3. Nhấp đúp chuột vào file 'nap_tieng_coi.bat' trong thư mục để tự động nạp trong 3 giây!");
      }, 400);
    }

    window.addEventListener('DOMContentLoaded', () => {
      initSlotsAudio();
      window.addEventListener('resize', drawWaveform);
    });

    window.addEventListener('keydown', (e) => {
      if (e.code === 'Space' && e.target.tagName !== 'INPUT') {
        e.preventDefault();
        togglePlay();
      }
      if (e.code === 'Escape') {
        closePresetModal();
      }
    });
  </script>
</body>
</html>
'''

os.makedirs(os.path.dirname(OUTPUT_TOOLS), exist_ok=True)
with open(OUTPUT_TOOLS, "w", encoding="utf-8") as f:
    f.write(html_template)
print(f"Created {OUTPUT_TOOLS} ({os.path.getsize(OUTPUT_TOOLS):,} bytes)")

if os.path.exists(os.path.dirname(OUTPUT_RELEASE)):
    with open(OUTPUT_RELEASE, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"Created {OUTPUT_RELEASE} ({os.path.getsize(OUTPUT_RELEASE):,} bytes)")
