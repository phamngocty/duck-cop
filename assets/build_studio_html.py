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
OUTPUT_DOCS = os.path.join(SCRIPT_DIR, "..", "docs", "index.html")

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
      grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
      gap: 12px;
    }

    .btn-slot-action {
      background: #0d2242;
      border: 1px solid var(--border-color);
      color: var(--text-primary);
      padding: 5px 12px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      transition: all 0.2s ease;
    }

    .btn-slot-action:hover:not(:disabled) {
      transform: translateY(-1px);
    }

    .btn-slot-action.btn-add-slot {
      background: rgba(0, 240, 170, 0.12);
      border-color: rgba(0, 240, 170, 0.4);
      color: var(--accent-neon);
    }

    .btn-slot-action.btn-add-slot:hover {
      background: rgba(0, 240, 170, 0.25);
      border-color: var(--accent-neon);
      box-shadow: 0 0 10px var(--accent-neon-glow);
    }

    .btn-slot-action.btn-del-slot {
      background: rgba(255, 71, 114, 0.1);
      border-color: rgba(255, 71, 114, 0.35);
      color: var(--accent-danger);
    }

    .btn-slot-action.btn-del-slot:hover:not(:disabled) {
      background: rgba(255, 71, 114, 0.25);
      border-color: var(--accent-danger);
      box-shadow: 0 0 10px rgba(255, 71, 114, 0.4);
    }

    .btn-slot-action:disabled {
      opacity: 0.35;
      cursor: not-allowed;
      transform: none !important;
      box-shadow: none !important;
    }

    .slot-add-card {
      background: rgba(14, 39, 75, 0.3);
      border: 2px dashed rgba(0, 210, 255, 0.35);
      border-radius: 12px;
      padding: 14px;
      cursor: pointer;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 6px;
      min-height: 82px;
      color: var(--accent-cyan);
      font-weight: 700;
      font-size: 13px;
      transition: all 0.2s ease;
    }

    .slot-add-card:hover {
      background: rgba(14, 39, 75, 0.7);
      border-color: var(--accent-neon);
      color: var(--accent-neon);
      transform: translateY(-2px);
      box-shadow: 0 4px 16px rgba(0, 240, 170, 0.25);
    }

    .btn-tab-del {
      background: transparent;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      font-size: 12px;
      padding: 1px 4px;
      border-radius: 4px;
      line-height: 1;
      font-weight: 800;
      transition: all 0.15s ease;
    }

    .btn-tab-del:hover {
      background: rgba(255, 71, 114, 0.25);
      color: var(--accent-danger);
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
      background: rgba(3, 7, 16, 0.72);
      border-right: 2px solid var(--accent-cyan);
    }

    .trim-dimmer-right {
      position: absolute;
      top: 0;
      bottom: 0;
      right: 0;
      background: rgba(3, 7, 16, 0.72);
      border-left: 2px solid #ff4772;
    }

    .trim-handle {
      position: absolute;
      top: 0;
      bottom: 0;
      width: 28px;
      cursor: ew-resize;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      z-index: 10;
      user-select: none;
    }

    .trim-handle-left {
      right: -14px;
    }

    .trim-handle-right {
      left: -14px;
    }

    .trim-handle-line {
      width: 3px;
      height: 100%;
      border-radius: 2px;
    }
    .trim-handle-left .trim-handle-line {
      background: var(--accent-cyan);
      box-shadow: 0 0 8px var(--accent-cyan);
    }
    .trim-handle-right .trim-handle-line {
      background: #ff4772;
      box-shadow: 0 0 8px #ff4772;
    }

    .trim-handle-badge {
      position: absolute;
      top: 8px;
      font-size: 10px;
      font-weight: 800;
      padding: 3px 6px;
      border-radius: 4px;
      letter-spacing: 0.5px;
      white-space: nowrap;
      pointer-events: none;
    }
    .trim-handle-left .trim-handle-badge {
      background: rgba(0, 210, 255, 0.95);
      color: #030712;
      box-shadow: 0 2px 6px rgba(0, 210, 255, 0.5);
    }
    .trim-handle-right .trim-handle-badge {
      background: rgba(255, 71, 114, 0.95);
      color: #ffffff;
      box-shadow: 0 2px 6px rgba(255, 71, 114, 0.5);
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

    /* Modal Flash Web Serial */
    .flash-info-row {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
    }

    @media (max-width: 600px) {
      .flash-info-row { grid-template-columns: 1fr; }
    }

    .flash-chip-badge {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      padding: 10px 12px;
      border-radius: 8px;
      font-size: 12px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .flash-chip-badge span { color: var(--text-muted); font-size: 11px; }
    .flash-chip-badge strong { color: var(--accent-neon); font-family: 'JetBrains Mono', monospace; font-size: 13px; }

    .flash-select {
      background: #07172c;
      color: var(--accent-cyan);
      border: 1px solid var(--border-color);
      border-radius: 6px;
      padding: 4px 6px;
      font-size: 11px;
      font-family: 'JetBrains Mono', monospace;
      font-weight: 600;
    }

    .flash-progress-wrapper {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 12px 14px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .flash-progress-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .flash-progress-track {
      width: 100%;
      height: 12px;
      background: #040913;
      border-radius: 6px;
      overflow: hidden;
      position: relative;
      box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);
    }

    .flash-progress-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--accent-cyan) 0%, var(--accent-neon) 100%);
      box-shadow: 0 0 10px var(--accent-neon-glow);
      transition: width 0.15s ease-out;
    }

    .flash-terminal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 12px;
      color: var(--text-secondary);
      font-weight: 600;
    }

    .btn-clear-term {
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-size: 11px;
      cursor: pointer;
      text-decoration: underline;
    }

    .btn-clear-term:hover { color: var(--text-primary); }

    .flash-terminal {
      background: #030811;
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 12px 14px;
      height: 170px;
      overflow-y: auto;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11.5px;
      line-height: 1.5;
      display: flex;
      flex-direction: column;
      gap: 4px;
      user-select: text;
    }

    .term-line { word-break: break-all; }
    .term-line.info { color: #5bc0de; }
    .term-line.success { color: #00f0aa; font-weight: 600; }
    .term-line.warn { color: #ffb834; font-weight: 600; }
    .term-line.error { color: #ff4772; font-weight: 600; }
    .term-line.muted { color: #577196; }

    .flash-alert-box {
      padding: 12px 16px;
      border-radius: 10px;
      font-size: 12.5px;
      line-height: 1.5;
    }

    .flash-alert-box.success {
      background: rgba(0, 240, 170, 0.12);
      border: 1px solid var(--accent-neon);
      color: #f0f6fc;
    }

    .flash-alert-box.error {
      background: rgba(255, 71, 114, 0.12);
      border: 1px solid var(--accent-danger);
      color: #f0f6fc;
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

    /* ESP32-C3 Flash Memory Gauge */
    .flash-meter-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 14px 18px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    }

    .flash-meter-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 10px;
    }

    .flash-meter-title {
      font-size: 13px;
      font-weight: 700;
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: 8px;
      letter-spacing: 0.3px;
    }

    .flash-meter-stats {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 12px;
      color: var(--text-secondary);
    }

    .flash-meter-stats strong {
      color: var(--accent-neon);
      font-family: 'JetBrains Mono', monospace;
    }

    .badge-free {
      background: rgba(0, 240, 170, 0.12);
      color: var(--accent-neon);
      border: 1px solid rgba(0, 240, 170, 0.4);
      font-size: 11px;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 6px;
      font-family: 'JetBrains Mono', monospace;
    }

    .flash-meter-track {
      width: 100%;
      height: 8px;
      background: #040913;
      border: 1px solid rgba(22, 54, 100, 0.6);
      border-radius: 999px;
      overflow: hidden;
      position: relative;
    }

    .flash-meter-fill {
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, #00d2ff 0%, #00f0aa 100%);
      border-radius: 999px;
      transition: width 0.3s ease, background 0.3s ease;
      box-shadow: 0 0 10px rgba(0, 240, 170, 0.5);
    }

    .flash-meter-slots {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }

    .flash-slot-pill {
      font-size: 11px;
      font-family: 'JetBrains Mono', monospace;
      background: rgba(12, 32, 61, 0.7);
      border: 1px solid rgba(22, 54, 100, 0.8);
      color: var(--text-secondary);
      padding: 2px 8px;
      border-radius: 4px;
      transition: all 0.2s ease;
    }

    .flash-slot-pill.active-slot-pill {
      border-color: var(--accent-neon);
      color: var(--accent-neon);
      background: rgba(0, 240, 170, 0.12);
      font-weight: 700;
    }

    .flash-slot-pill.header-pill {
      color: var(--text-muted);
    }

    /* Cutting Toolbar */
    .cutting-toolbar {
      display: flex;
      flex-direction: column;
      gap: 10px;
      padding: 12px 16px;
      background: rgba(4, 9, 19, 0.85);
      border-top: 1px solid var(--border-color);
      border-bottom: 1px solid var(--border-color);
    }

    .cutting-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      flex-wrap: wrap;
    }

    .cutting-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }

    .btn-cut {
      background: var(--bg-surface);
      color: var(--text-primary);
      border: 1px solid var(--border-color);
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .btn-cut:disabled {
      opacity: 0.4;
      cursor: not-allowed;
      transform: none !important;
      box-shadow: none !important;
    }

    .btn-cut:not(:disabled):hover {
      background: var(--bg-surface-hover);
      border-color: #2b558f;
      transform: translateY(-1px);
    }

    /* 2 Nút Cắt Đoạn Âm Thanh Chính Siêu Nổi Bật */
    .btn-cut-keep {
      background: linear-gradient(135deg, rgba(0, 240, 170, 0.22) 0%, rgba(0, 210, 255, 0.22) 100%);
      border: 1px solid var(--accent-neon);
      color: #00f0aa;
      font-weight: 700;
      padding: 8px 15px;
      font-size: 13px;
    }

    .btn-cut-head {
      background: linear-gradient(135deg, rgba(0, 210, 255, 0.18) 0%, rgba(59, 130, 246, 0.18) 100%);
      border: 1px solid var(--accent-cyan);
      color: var(--accent-cyan);
      font-weight: 700;
      padding: 8px 14px;
      font-size: 13px;
    }
    .btn-cut-head:not(:disabled):hover {
      background: linear-gradient(135deg, rgba(0, 210, 255, 0.32) 0%, rgba(59, 130, 246, 0.32) 100%);
      box-shadow: 0 0 14px rgba(0, 210, 255, 0.45);
      transform: translateY(-1px);
    }

    .btn-cut-tail {
      background: linear-gradient(135deg, rgba(255, 138, 76, 0.2) 0%, rgba(255, 71, 114, 0.2) 100%);
      border: 1px solid #ff8a4c;
      color: #ff9f68;
      font-weight: 700;
      padding: 8px 14px;
      font-size: 13px;
    }
    .btn-cut-tail:not(:disabled):hover {
      background: linear-gradient(135deg, rgba(255, 138, 76, 0.35) 0%, rgba(255, 71, 114, 0.35) 100%);
      box-shadow: 0 0 14px rgba(255, 138, 76, 0.45);
      transform: translateY(-1px);
    }

    .btn-cut-keep:not(:disabled):hover {
      background: linear-gradient(135deg, rgba(0, 240, 170, 0.35) 0%, rgba(0, 210, 255, 0.35) 100%);
      box-shadow: 0 0 16px rgba(0, 240, 170, 0.5);
      transform: translateY(-1px);
    }

    .btn-cut-delete {
      background: linear-gradient(135deg, rgba(255, 71, 114, 0.22) 0%, rgba(255, 184, 52, 0.22) 100%);
      border: 1px solid var(--accent-danger);
      color: #ff6b8b;
      font-weight: 700;
      padding: 8px 15px;
      font-size: 13px;
    }

    .btn-cut-delete:not(:disabled):hover {
      background: linear-gradient(135deg, rgba(255, 71, 114, 0.35) 0%, rgba(255, 184, 52, 0.35) 100%);
      box-shadow: 0 0 16px rgba(255, 71, 114, 0.5);
      transform: translateY(-1px);
    }

    .btn-preview-sub {
      background: rgba(0, 210, 255, 0.12);
      border-color: var(--accent-cyan);
      color: var(--accent-cyan);
    }

    .btn-preview-sub:not(:disabled):hover {
      background: rgba(0, 210, 255, 0.25);
      box-shadow: 0 0 12px rgba(0, 210, 255, 0.4);
    }

    .trim-inputs-group {
      display: flex;
      align-items: center;
      gap: 14px;
      flex-wrap: wrap;
    }

    .trim-input-item {
      display: flex;
      align-items: center;
      gap: 5px;
    }

    .trim-input-label {
      font-size: 11px;
      font-weight: 700;
      color: var(--text-muted);
      letter-spacing: 0.5px;
    }

    .btn-step {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      color: var(--text-primary);
      width: 24px;
      height: 24px;
      border-radius: 4px;
      font-weight: 700;
      font-size: 13px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.15s ease;
    }

    .btn-step:hover {
      border-color: var(--accent-cyan);
      color: var(--accent-cyan);
      background: var(--bg-surface-hover);
    }

    .trim-number-input {
      width: 60px;
      background: #030710;
      border: 1px solid var(--border-color);
      border-radius: 4px;
      color: var(--accent-neon);
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      font-weight: 600;
      padding: 3px 4px;
      text-align: center;
      outline: none;
    }

    .trim-number-input:focus {
      border-color: var(--accent-neon);
      box-shadow: 0 0 6px var(--accent-neon-glow);
    }

    .trim-unit {
      font-size: 11px;
      color: var(--text-muted);
      font-family: 'JetBrains Mono', monospace;
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
      <button class="btn-action btn-flash" onclick="openFlashModal()">
        <span>⚡</span> Nạp Còi Xe (Web Serial)
      </button>
    </div>
  </header>

  <main>
    <!-- ESP32-C3 Flash Memory Gauge -->
    <div class="flash-meter-card" id="flashMeterCard">
      <div class="flash-meter-header">
        <div class="flash-meter-title">
          <span>📊</span> BỘ NHỚ FLASH ESP32-C3 (Phân vùng 0x1E0000: 2,112 KB)
        </div>
        <div class="flash-meter-stats">
          <span id="flashUsedText">Đã dùng: <strong>0.0 KB</strong> / 2,112 KB (0.0%)</span>
          <span class="badge-free" id="flashFreeText">Trống: 2,112 KB</span>
        </div>
      </div>
      <div class="flash-meter-track">
        <div class="flash-meter-fill" id="flashMeterFill" style="width: 0%;"></div>
      </div>
      <div class="flash-meter-slots" id="flashMeterSlots">
        <span class="flash-slot-pill header-pill">Header: 0.5 KB</span>
        <span class="flash-slot-pill">Slot 0: --</span>
        <span class="flash-slot-pill">Slot 1: --</span>
        <span class="flash-slot-pill">Slot 2: --</span>
        <span class="flash-slot-pill">Slot 3: --</span>
        <span class="flash-slot-pill">Slot 4: --</span>
      </div>
    </div>

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
          <button class="btn-slot-action btn-add-slot" onclick="addNewSlot()" title="Thêm slot âm thanh mới vào danh sách (Tối đa 20 Slot)">
            <span>➕</span> Thêm Slot
          </button>
          <button class="btn-slot-action btn-del-slot" id="btnDelSlot" onclick="deleteCurrentSlot()" title="Xóa slot âm thanh này khỏi danh sách">
            <span>🗑️</span> Xóa Slot
          </button>
        </div>

        <div class="editor-tools">
          <input type="file" id="fileInput" accept="audio/*,.mp3,.wav,.ogg,.m4a" style="display:none" onchange="handleFileSelected(event)">
          <button class="btn-tool preset" onclick="openPresetModal()">
            <span>✨</span> Chọn mẫu có sẵn
          </button>
          <button class="btn-tool" onclick="document.getElementById('fileInput').click()">
            <span>📁</span> Đổi bằng file MP3/WAV
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
        <div class="trim-dimmer-left" id="trimDimmerLeft" style="width: 0px;">
          <div class="trim-handle trim-handle-left" title="Kéo để chỉnh mốc BẮT ĐẦU (hoặc click vào waveform)">
            <div class="trim-handle-line"></div>
            <div class="trim-handle-badge">◀ BẮT ĐẦU</div>
          </div>
        </div>
        <div class="trim-dimmer-right" id="trimDimmerRight" style="width: 0px;">
          <div class="trim-handle trim-handle-right" title="Kéo để chỉnh mốc KẾT THÚC (hoặc click vào waveform)">
            <div class="trim-handle-line"></div>
            <div class="trim-handle-badge">KẾT THÚC ▶</div>
          </div>
        </div>
      </div>

      <!-- Cutting Tools Toolbar -->
      <div class="cutting-toolbar" id="cuttingToolbar">
        <!-- Hàng 1: Các Nút Cắt Đoạn Chính, Nghe Thử & Ghép Nối -->
        <div class="cutting-row">
          <div class="cutting-actions">
            <button class="btn-cut btn-cut-head" onclick="deleteHead()" title="Cắt bỏ toàn bộ phần âm thanh từ đầu (0s) đến mốc BẮT ĐẦU">
              <span>✂️</span> <strong>Cắt Bỏ Đoạn Đầu</strong>
            </button>
            <button class="btn-cut btn-cut-tail" onclick="deleteTail()" title="Cắt bỏ toàn bộ phần âm thanh từ mốc KẾT THÚC đến hết file">
              <span>✂️</span> <strong>Cắt Bỏ Đoạn Đuôi</strong>
            </button>
            <button class="btn-cut btn-cut-keep" onclick="cropToSelection()" title="Lấy riêng đoạn trong vùng chọn, xóa bỏ cả phần đầu và phần đuôi">
              <span>✂️</span> <strong>Cắt Giữ Đoạn Chọn</strong>
            </button>
            <button class="btn-cut btn-cut-delete" onclick="deleteSelectionAndMerge()" title="Cắt bỏ đoạn ở giữa đang chọn, tự động ghép đoạn trước và đoạn sau lại làm một">
              <span>✂️</span> <strong>Cắt Bỏ Đoạn Giữa & Ghép Lại</strong>
            </button>
            <button class="btn-cut btn-preview-sub" onclick="playSelectionOnly()" title="Chỉ phát thử đoạn đang được chọn">
              <span>▶️</span> Nghe Đoạn Chọn
            </button>
            <button class="btn-cut btn-preview-sub" onclick="previewCutAndMerge()" title="Nghe thử xem nếu cắt bỏ đoạn giữa thì 2 đầu ghép lại nghe ra sao trước khi bấm cắt">
              <span>⏩</span> Nghe Thử Sau Ghép
            </button>
          </div>

          <div class="cutting-actions">
            <input type="file" id="appendFileInput" accept="audio/*,.mp3,.wav,.ogg,.m4a" style="display:none" onchange="handleAppendFile(event)">
            <button class="btn-cut" onclick="document.getElementById('appendFileInput').click()" title="Chọn thêm 1 file âm thanh để ghép nối tiếp vào đuôi">
              <span>➕</span> Ghép Thêm File
            </button>
            <button class="btn-cut" onclick="duplicateCurrentSound()" title="Nhân đôi tiếng còi này kèm khoảng nghỉ 80ms ở giữa để tạo tiếng còi đôi (quạc-quạc)">
              <span>🔁</span> Tạo Còi Đôi
            </button>
          </div>
        </div>

        <!-- Hàng 2: Lịch Sử Hoàn Tác, Fade/Lặng & Vi Chỉnh Bằng Số -->
        <div class="cutting-row">
          <div class="cutting-actions">
            <button class="btn-cut" id="btnUndo" onclick="undoLastAction()" title="Hoàn tác thao tác vừa thực hiện (Ctrl+Z)" disabled>
              <span>↩️</span> Hoàn Tác
            </button>
            <button class="btn-cut" id="btnRedo" onclick="redoLastAction()" title="Làm lại thao tác vừa hoàn tác (Ctrl+Y)" disabled>
              <span>↪️</span> Làm Lại
            </button>
            <button class="btn-cut" onclick="restoreOriginalAudio()" title="Khôi phục lại hoàn toàn âm thanh gốc ban đầu khi vừa nạp file">
              <span>🔄</span> Khôi Phục Gốc
            </button>
            <button class="btn-cut" onclick="autoTrimSilence()" title="Tự động phát hiện và cắt bỏ khoảng lặng ở đầu và đuôi">
              <span>✂️</span> Cắt Khoảng Lặng
            </button>
            <button class="btn-cut" onclick="applyFade('in')" title="Làm nhỏ dần từ 0 lên ở đầu (chống bụp loa)">
              <span>📈</span> Fade In
            </button>
            <button class="btn-cut" onclick="applyFade('out')" title="Làm nhỏ dần về 0 ở đuôi (chống bụp loa)">
              <span>📉</span> Fade Out
            </button>
          </div>

          <!-- Precise Time Fine-Tuning -->
          <div class="trim-inputs-group">
            <div class="trim-input-item">
              <span class="trim-input-label">BẮT ĐẦU:</span>
              <button class="btn-step" onclick="adjustTrimTime('start', -0.05)" title="Lùi 0.05s">-</button>
              <input type="number" id="trimStartInput" class="trim-number-input" step="0.01" min="0" value="0.00" onchange="onTrimInputChange('start', this.value)">
              <span class="trim-unit">s</span>
              <button class="btn-step" onclick="adjustTrimTime('start', 0.05)" title="Tiến 0.05s">+</button>
            </div>

            <div class="trim-input-item">
              <span class="trim-input-label">KẾT THÚC:</span>
              <button class="btn-step" onclick="adjustTrimTime('end', -0.05)" title="Lùi 0.05s">-</button>
              <input type="number" id="trimEndInput" class="trim-number-input" step="0.01" min="0" value="0.00" onchange="onTrimInputChange('end', this.value)">
              <span class="trim-unit">s</span>
              <button class="btn-step" onclick="adjustTrimTime('end', 0.05)" title="Tiến 0.05s">+</button>
            </div>
          </div>
        </div>
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
          <li>Mỗi lần nhấn nhả, còi nhảy sang tiếng tiếp theo (0 → 1 → 2 → 3) và phát thử ngay tiếng mới.</li>
          <li>Còi tự động lưu nhớ vĩnh viễn vào NVS & RTC SRAM (tắt chìa khóa bật lại vẫn nhớ đúng tiếng).</li>
        </ol>
      </div>

      <div class="info-card">
        <div class="info-title"><span>⚡</span> Nạp Âm Thanh Trực Tiếp 1-Click (Web Serial)</div>
        <ol class="info-list">
          <li><strong>Bước 1:</strong> Chọn tiếng mẫu hoặc nạp file MP3/WAV, kéo thanh <strong>Âm Lượng (100% - 250%)</strong> hoặc cắt đoạn ưng ý.</li>
          <li><strong>Bước 2:</strong> Cắm cáp USB Type-C từ còi xe vào máy tính.</li>
          <li><strong>Bước 3:</strong> Bấm nút <code>⚡ Nạp Còi Xe (Web Serial)</code> ở góc trên, chọn cổng COM và nạp trực tiếp trong 3 giây (không cần tải file!).</li>
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

  <!-- Modal Web Serial Flash -->
  <div class="modal-backdrop" id="flashModal">
    <div class="modal-card" style="max-width: 660px;">
      <div class="modal-header">
        <div class="modal-title"><span>⚡</span> Nạp Âm Thanh Trực Tiếp Vào Còi Xe (Web Serial)</div>
        <button class="btn-close" onclick="closeFlashModal()">&times;</button>
      </div>
      <div class="modal-body" style="display: flex; flex-direction: column; gap: 14px;">
        <!-- Config & Status Badges -->
        <div class="flash-info-row">
          <div class="flash-chip-badge"><span>🎯 Vi điều khiển:</span> <strong>ESP32-C3</strong></div>
          <div class="flash-chip-badge"><span>📍 Phân vùng:</span> <strong>0x1E0000</strong></div>
          <div class="flash-chip-badge">
            <span>⚡ Tốc độ:</span>
            <select id="flashBaudSelect" class="flash-select">
              <option value="460800" selected>460,800 baud (Chuẩn)</option>
              <option value="115200">115,200 baud (Ổn định)</option>
              <option value="921600">921,600 baud (Cực nhanh)</option>
            </select>
          </div>
        </div>

        <!-- Connection / Action Button -->
        <div style="display: flex; gap: 12px; align-items: center;">
          <button id="btnStartFlash" class="btn-action btn-flash" style="flex: 1; padding: 13px 20px; font-size: 14px; justify-content: center;" onclick="startWebSerialFlash()">
            <span>🔌</span> Chọn Cổng COM & Nạp Ngay
          </button>
        </div>

        <!-- Progress Bar -->
        <div class="flash-progress-wrapper" id="flashProgressWrapper" style="display: none;">
          <div class="flash-progress-header">
            <span id="flashStatusText" style="font-size: 13px; font-weight: 700; color: var(--accent-neon);">Đang nạp...</span>
            <span id="flashPercentText" style="font-size: 13px; font-weight: 700; font-family: 'JetBrains Mono', monospace;">0%</span>
          </div>
          <div class="flash-progress-track">
            <div class="flash-progress-fill" id="flashProgressFill" style="width: 0%;"></div>
          </div>
        </div>

        <!-- Console Log Terminal -->
        <div class="flash-terminal-header">
          <span>📜 Nhật ký nạp Serial</span>
          <button class="btn-clear-term" onclick="clearFlashTerminal()">Xóa log</button>
        </div>
        <div class="flash-terminal" id="flashTerminal">
          <div class="term-line info">[*] Sẵn sàng nạp trực tiếp vào phân vùng 0x1E0000 qua Web Serial.</div>
          <div class="term-line muted">[*] Cắm cáp USB Type-C từ còi xe vào máy tính, sau đó bấm 'Chọn Cổng COM & Nạp Ngay'.</div>
        </div>

        <div id="flashAlertBox" class="flash-alert-box" style="display: none;"></div>
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
      { key: "sample_vit_that.wav", name: "Vịt Quạc Thật 100% (Real Duck Quack)", desc: "Bản thu âm vịt tự nhiên thật 100%, tiếng cạp đanh giòn, khàn tự nhiên, rất tiếu lâm." },
      { key: "sample_de_cuu.wav", name: "Dê / Cừu Be-e-e (Goat / Sheep Bleat)", desc: "Tiếng be-e-e hài hước cực bựa, giúp người đi đường phì cười và nhường đường vui vẻ." },
      { key: "sample_ga_gay.wav", name: "Gà Trống Gáy (Rooster Crow)", desc: "Tiếng gà gáy o-o-o đanh giòn vang xa, tạo nét cá tính độc lạ, không gây bực mình." },
      { key: "sample_cho_sua.wav", name: "Chó Sủa Đanh (Guard Dog Barking)", desc: "Hai tiếng gâu gâu dứt khoát, độ cảnh báo cực cao, phản xạ nhanh tức thì." },
      { key: "sample_meme_wow.wav", name: "Anime WOW Meme (Tiếng WOW Hài Hước)", desc: "Âm thanh cảm thán WOW huyền thoại, siêu hài hước và thân thiện." }
    ];

    // Cấu trúc 4 Slot chính của thiết bị
    const slots = [
      { name: "Vit Coi Xe Chuan (Duck 2)", pcm: null, sampleRate: 22050, buffer: null, originalBuffer: null, trimStart: 0, trimEnd: 0, volume: 100 },
      { name: "Vit Keu Don (Duck 1)", pcm: null, sampleRate: 22050, buffer: null, originalBuffer: null, trimStart: 0, trimEnd: 0, volume: 100 },
      { name: "Vit Coi Doi (Double Quack)", pcm: null, sampleRate: 22050, buffer: null, originalBuffer: null, trimStart: 0, trimEnd: 0, volume: 100 },
      { name: "Bo Rong (Cow Mooing)", pcm: null, sampleRate: 22050, buffer: null, originalBuffer: null, trimStart: 0, trimEnd: 0, volume: 100 }
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
        div.onclick = (e) => {
          if (e.target.closest('.btn-tab-del')) return;
          selectSlot(i);
        };

        const dur = s.buffer ? `${s.buffer.duration.toFixed(2)}s` : '--';
        const sizeKb = s.pcm ? `${(s.pcm.length / 1024).toFixed(1)} KB` : '--';
        const delBtnHtml = slots.length > 1 
          ? `<button class="btn-tab-del" onclick="deleteSlotAt(${i})" title="Xóa Slot ${i}">✕</button>` 
          : '';

        div.innerHTML = `
          <div class="slot-header">
            <span class="slot-index">SLOT ${i}</span>
            <div style="display:flex;align-items:center;gap:6px;">
              <span class="slot-detail">${dur} • ${sizeKb}</span>
              ${delBtnHtml}
            </div>
          </div>
          <div class="slot-name" id="slotNameText${i}">${s.name}</div>
        `;
        container.appendChild(div);
      });

      // Nút thêm slot dạng card ở cuối danh sách
      if (slots.length < 20) {
        const addCard = document.createElement('div');
        addCard.className = 'slot-add-card';
        addCard.onclick = addNewSlot;
        addCard.title = 'Thêm slot âm thanh mới (Tối đa 20 Slot)';
        addCard.innerHTML = `
          <span style="font-size:22px;line-height:1;">➕</span>
          <span>Thêm Slot Mới</span>
        `;
        container.appendChild(addCard);
      }

      const btnDel = document.getElementById('btnDelSlot');
      if (btnDel) {
        btnDel.disabled = (slots.length <= 1);
      }
    }

    function selectSlot(idx) {
      if (idx < 0 || idx >= slots.length) idx = 0;
      stopPlayback();
      currentSlotIdx = idx;
      for (let i = 0; i < slots.length; i++) {
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

      // Đặt lại tốc độ phát mặc định là 1.0x
      playSpeed = 1.0;
      document.querySelectorAll('.btn-speed').forEach(b => {
        b.classList.toggle('active', b.textContent.trim() === '1.0x');
      });

      drawWaveform();
      updateTimeDisplay();
      updateTrimDimmer();
      updateTrimInputs();
      updateFlashUsageUI();
      updateUndoRedoUI();
    }

    function addNewSlot() {
      if (slots.length >= 20) {
        showToast("⚠️ Đã đạt giới hạn tối đa 20 Slot âm thanh!");
        return;
      }
      const newIdx = slots.length;
      const presetInfo = PRESET_CATALOG[newIdx % PRESET_CATALOG.length];
      const presetKey = presetInfo.key;
      const presetName = presetInfo.name;

      const newSlot = {
        name: `Slot ${newIdx}: ${presetName}`,
        pcm: null,
        sampleRate: 22050,
        buffer: null,
        originalBuffer: null,
        trimStart: 0,
        trimEnd: 0,
        volume: 100,
        undoStack: [],
        redoStack: []
      };

      slots.push(newSlot);

      if (EMBEDDED_PRESETS[presetKey]) {
        try {
          const ab = base64ToArrayBuffer(EMBEDDED_PRESETS[presetKey]);
          getAudioContext().decodeAudioData(ab.slice(0)).then(buf => {
            newSlot.buffer = buf;
            newSlot.originalBuffer = buf;
            newSlot.trimStart = 0;
            newSlot.trimEnd = buf.duration;
            ensureSlotPCM(newIdx);
            if (currentSlotIdx === newIdx) {
              selectSlot(newIdx);
            }
            renderSlotsUI();
            updateFlashUsageUI();
          }).catch(e => {
            console.error(e);
          });
        } catch(e){}
      }

      renderSlotsUI();
      selectSlot(newIdx);
      updateFlashUsageUI();
      showToast(`➕ Đã thêm Slot ${newIdx}!`);
    }

    function deleteCurrentSlot() {
      deleteSlotAt(currentSlotIdx);
    }

    function deleteSlotAt(idx) {
      if (slots.length <= 1) {
        showToast("⚠️ Phải giữ ít nhất 1 Slot âm thanh!");
        return;
      }

      const slotName = slots[idx] ? slots[idx].name : `Slot ${idx}`;
      if (!confirm(`Bạn có chắc muốn xóa '${slotName}' (Slot ${idx}) không?`)) {
        return;
      }

      stopPlayback();
      slots.splice(idx, 1);

      if (currentSlotIdx >= slots.length) {
        currentSlotIdx = slots.length - 1;
      } else if (currentSlotIdx > idx) {
        currentSlotIdx--;
      }

      renderSlotsUI();
      selectSlot(currentSlotIdx);
      updateFlashUsageUI();
      showToast(`🗑️ Đã xóa Slot ${idx}!`);
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
        "slot3_bo_rong.wav"
      ];

      for (let i = 0; i < defaultKeys.length; i++) {
        const k = defaultKeys[i];
        if (EMBEDDED_PRESETS[k]) {
          try {
            const ab = base64ToArrayBuffer(EMBEDDED_PRESETS[k]);
            const buf = await getAudioContext().decodeAudioData(ab);
            slots[i].buffer = buf;
            slots[i].originalBuffer = buf;
            slots[i].trimStart = 0;
            slots[i].trimEnd = buf.duration;
            slots[i].volume = 100;
            ensureSlotPCM(i);
          } catch (e) {
            console.error("Lỗi giải mã audio slot " + i, e);
          }
        }
      }

      renderSlotsUI();
      selectSlot(0);
      updateFlashUsageUI();
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

      const dur = currentBuffer.duration;

      // Thước đo thời gian & Lưới chia giây (Time Grid & Rulers)
      const tickInterval = dur <= 0.6 ? 0.05 : (dur <= 1.5 ? 0.1 : (dur <= 3.0 ? 0.25 : 0.5));
      ctx.font = '9px "JetBrains Mono", monospace';
      ctx.textAlign = 'center';

      for (let t = tickInterval; t < dur; t += tickInterval) {
        const tx = (t / dur) * w;
        ctx.fillStyle = 'rgba(255, 255, 255, 0.06)';
        ctx.fillRect(tx, 0, 1, h);
        ctx.fillStyle = 'rgba(145, 168, 201, 0.45)';
        ctx.fillText(`${t.toFixed(2)}s`, tx, 12);
      }

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
      const pct = Math.max(0, Math.min(1, clickX / rect.width));
      const dur = currentBuffer.duration;
      const clickTime = pct * dur;

      const startX = (trimStart / dur) * rect.width;
      const endX = (trimEnd / dur) * rect.width;

      // 1. Kiểm tra nếu bấm gần tay cầm nào (bán kính 24px)
      if (Math.abs(clickX - startX) <= 24) {
        isDraggingTrim = 'left';
      } else if (Math.abs(clickX - endX) <= 24) {
        isDraggingTrim = 'right';
      }
      // 2. Nếu bấm ra ngoài vùng chọn (vùng dimmer trái - đoạn đầu)
      else if (clickX < startX) {
        trimStart = Math.min(clickTime, trimEnd - 0.05);
        isDraggingTrim = 'left';
      }
      // 3. Nếu bấm ra ngoài vùng chọn (vùng dimmer phải - đoạn đuôi)
      else if (clickX > endX) {
        trimEnd = Math.max(clickTime, trimStart + 0.05);
        isDraggingTrim = 'right';
      }
      // 4. Nếu bấm vào giữa vùng chọn: tự động bắt mốc gần nhất
      else {
        const distToStart = Math.abs(clickX - startX);
        const distToEnd = Math.abs(clickX - endX);
        if (distToStart <= distToEnd) {
          trimStart = Math.min(clickTime, trimEnd - 0.05);
          isDraggingTrim = 'left';
        } else {
          trimEnd = Math.max(clickTime, trimStart + 0.05);
          isDraggingTrim = 'right';
        }
      }
      slots[currentSlotIdx].trimStart = trimStart;
      slots[currentSlotIdx].trimEnd = trimEnd;
      updateTrimDimmer();
      updateTimeDisplay();
      updateTrimInputs();
    });

    window.addEventListener('mousemove', (e) => {
      if (!isDraggingTrim || !currentBuffer) return;
      const rect = canvasEl.getBoundingClientRect();
      const clickX = Math.max(0, Math.min(rect.width, e.clientX - rect.left));
      const pct = clickX / rect.width;
      const time = pct * currentBuffer.duration;

      if (isDraggingTrim === 'left') {
        trimStart = Math.max(0, Math.min(time, trimEnd - 0.05));
      } else if (isDraggingTrim === 'right') {
        trimEnd = Math.min(currentBuffer.duration, Math.max(time, trimStart + 0.05));
      }
      slots[currentSlotIdx].trimStart = trimStart;
      slots[currentSlotIdx].trimEnd = trimEnd;
      updateTrimDimmer();
      updateTimeDisplay();
      updateTrimInputs();
    });

    window.addEventListener('mouseup', () => {
      if (isDraggingTrim) {
        isDraggingTrim = null;
        recalculatePCM();
        updateTrimInputs();
        updateFlashUsageUI();
      }
    });

    // === CÔNG CỤ CẮT ÂM THANH CƠ BẢN (BASIC AUDIO CUTTING TOOLS) ===

    function updateTrimInputs() {
      const startEl = document.getElementById('trimStartInput');
      const endEl = document.getElementById('trimEndInput');
      if (startEl) startEl.value = trimStart.toFixed(2);
      if (endEl) endEl.value = trimEnd.toFixed(2);
    }

    function adjustTrimTime(handle, delta) {
      if (!currentBuffer) return;
      const dur = currentBuffer.duration;
      if (handle === 'start') {
        trimStart = Math.max(0, Math.min(trimEnd - 0.05, trimStart + delta));
      } else if (handle === 'end') {
        trimEnd = Math.max(trimStart + 0.05, Math.min(dur, trimEnd + delta));
      }
      slots[currentSlotIdx].trimStart = trimStart;
      slots[currentSlotIdx].trimEnd = trimEnd;
      updateTrimDimmer();
      updateTimeDisplay();
      updateTrimInputs();
      recalculatePCM();
      updateFlashUsageUI();
    }

    function onTrimInputChange(handle, val) {
      if (!currentBuffer) return;
      val = parseFloat(val);
      if (isNaN(val)) return;
      const dur = currentBuffer.duration;
      if (handle === 'start') {
        trimStart = Math.max(0, Math.min(trimEnd - 0.05, val));
      } else if (handle === 'end') {
        trimEnd = Math.max(trimStart + 0.05, Math.min(dur, val));
      }
      slots[currentSlotIdx].trimStart = trimStart;
      slots[currentSlotIdx].trimEnd = trimEnd;
      updateTrimDimmer();
      updateTimeDisplay();
      updateTrimInputs();
      recalculatePCM();
      updateFlashUsageUI();
    }

    // === CÔNG CỤ XỬ LÝ ÂM THANH HOÀN CHỈNH (COMPLETE AUDIO EDITING SUITE) ===

    function cloneAudioBuffer(buf) {
      if (!buf) return null;
      const actx = getAudioContext();
      const copy = actx.createBuffer(buf.numberOfChannels, buf.length, buf.sampleRate);
      for (let ch = 0; ch < buf.numberOfChannels; ch++) {
        copy.getChannelData(ch).set(buf.getChannelData(ch));
      }
      return copy;
    }

    // 0. Quản lý lịch sử Hoàn tác (Undo / Redo)
    function pushSlotHistory(actionName) {
      const s = slots[currentSlotIdx];
      if (!s) return;
      if (!s.undoStack) s.undoStack = [];
      s.undoStack.push({
        action: actionName,
        buffer: cloneAudioBuffer(s.buffer),
        trimStart: s.trimStart,
        trimEnd: s.trimEnd
      });
      if (s.undoStack.length > 20) s.undoStack.shift();
      s.redoStack = [];
      updateUndoRedoUI();
    }

    function updateUndoRedoUI() {
      const s = slots[currentSlotIdx];
      const btnUndo = document.getElementById('btnUndo');
      const btnRedo = document.getElementById('btnRedo');
      if (btnUndo) btnUndo.disabled = !(s && s.undoStack && s.undoStack.length > 0);
      if (btnRedo) btnRedo.disabled = !(s && s.redoStack && s.redoStack.length > 0);
    }

    function undoLastAction() {
      const s = slots[currentSlotIdx];
      if (!s || !s.undoStack || s.undoStack.length === 0) return;
      stopPlayback();
      if (!s.redoStack) s.redoStack = [];
      s.redoStack.push({
        action: 'Hiện tại',
        buffer: cloneAudioBuffer(s.buffer),
        trimStart: s.trimStart,
        trimEnd: s.trimEnd
      });
      const prev = s.undoStack.pop();
      s.buffer = prev.buffer;
      currentBuffer = prev.buffer;
      s.trimStart = prev.trimStart;
      s.trimEnd = prev.trimEnd;
      trimStart = prev.trimStart;
      trimEnd = prev.trimEnd;
      drawWaveform();
      updateTimeDisplay();
      updateTrimDimmer();
      updateTrimInputs();
      recalculatePCM();
      updateFlashUsageUI();
      updateUndoRedoUI();
      showToast(`↩️ Đã hoàn tác: ${prev.action}`);
    }

    function redoLastAction() {
      const s = slots[currentSlotIdx];
      if (!s || !s.redoStack || s.redoStack.length === 0) return;
      stopPlayback();
      if (!s.undoStack) s.undoStack = [];
      s.undoStack.push({
        action: 'Trước redo',
        buffer: cloneAudioBuffer(s.buffer),
        trimStart: s.trimStart,
        trimEnd: s.trimEnd
      });
      const next = s.redoStack.pop();
      s.buffer = next.buffer;
      currentBuffer = next.buffer;
      s.trimStart = next.trimStart;
      s.trimEnd = next.trimEnd;
      trimStart = next.trimStart;
      trimEnd = next.trimEnd;
      drawWaveform();
      updateTimeDisplay();
      updateTrimDimmer();
      updateTrimInputs();
      recalculatePCM();
      updateFlashUsageUI();
      updateUndoRedoUI();
      showToast(`↪️ Đã làm lại thao tác!`);
    }

    // 1. Cắt bỏ đoạn đầu (Delete Head: từ 0 đến mốc BẮT ĐẦU)
    function deleteHead() {
      if (!currentBuffer) return;
      const actx = getAudioContext();
      const rate = currentBuffer.sampleRate;
      const startSample = Math.floor(trimStart * rate);
      const remainSamples = currentBuffer.length - startSample;

      if (remainSamples < 10) {
        showToast("⚠️ Âm thanh còn lại quá ngắn!");
        return;
      }
      if (startSample <= 10) {
        showToast("ℹ️ Mốc BẮT ĐẦU đã ở 0s, không có đoạn đầu để cắt!");
        return;
      }

      pushSlotHistory("Cắt bỏ đoạn đầu");
      if (!slots[currentSlotIdx].originalBuffer) {
        slots[currentSlotIdx].originalBuffer = cloneAudioBuffer(currentBuffer);
      }

      const newBuffer = actx.createBuffer(
        currentBuffer.numberOfChannels,
        remainSamples,
        rate
      );

      // Micro fade in 5ms ở đầu để chống bụp loa
      const fadeSamples = Math.min(80, Math.floor(remainSamples / 4));
      for (let ch = 0; ch < currentBuffer.numberOfChannels; ch++) {
        const src = currentBuffer.getChannelData(ch);
        const dst = newBuffer.getChannelData(ch);
        dst.set(src.subarray(startSample));
        for (let i = 0; i < fadeSamples; i++) {
          const factor = i / fadeSamples;
          dst[i] *= factor;
        }
      }

      slots[currentSlotIdx].buffer = newBuffer;
      currentBuffer = newBuffer;
      const removedTime = trimStart;
      trimStart = 0;
      trimEnd = Math.max(0.05, trimEnd - removedTime);
      slots[currentSlotIdx].trimStart = trimStart;
      slots[currentSlotIdx].trimEnd = trimEnd;

      drawWaveform();
      updateTimeDisplay();
      updateTrimDimmer();
      updateTrimInputs();
      recalculatePCM();
      updateFlashUsageUI();
      showToast(`✂️ Đã cắt bỏ đoạn đầu (còn lại ${newBuffer.duration.toFixed(2)}s)!`);
    }

    // 2. Cắt bỏ đoạn đuôi (Delete Tail: từ mốc KẾT THÚC đến hết file)
    function deleteTail() {
      if (!currentBuffer) return;
      const actx = getAudioContext();
      const rate = currentBuffer.sampleRate;
      const endSample = Math.floor(trimEnd * rate);

      if (endSample < 10) {
        showToast("⚠️ Vị trí kết thúc quá ngắn!");
        return;
      }
      if (endSample >= currentBuffer.length - 10) {
        showToast("ℹ️ Mốc KẾT THÚC đã ở cuối file, không có đoạn đuôi để cắt!");
        return;
      }

      pushSlotHistory("Cắt bỏ đoạn đuôi");
      if (!slots[currentSlotIdx].originalBuffer) {
        slots[currentSlotIdx].originalBuffer = cloneAudioBuffer(currentBuffer);
      }

      const newBuffer = actx.createBuffer(
        currentBuffer.numberOfChannels,
        endSample,
        rate
      );

      // Micro fade out 5ms ở đuôi để chống bụp loa
      const fadeSamples = Math.min(80, Math.floor(endSample / 4));
      for (let ch = 0; ch < currentBuffer.numberOfChannels; ch++) {
        const src = currentBuffer.getChannelData(ch);
        const dst = newBuffer.getChannelData(ch);
        dst.set(src.subarray(0, endSample));
        for (let i = 0; i < fadeSamples; i++) {
          const idx = endSample - fadeSamples + i;
          const factor = 1 - (i / fadeSamples);
          dst[idx] *= factor;
        }
      }

      slots[currentSlotIdx].buffer = newBuffer;
      currentBuffer = newBuffer;
      trimStart = Math.min(trimStart, newBuffer.duration);
      trimEnd = newBuffer.duration;
      slots[currentSlotIdx].trimStart = trimStart;
      slots[currentSlotIdx].trimEnd = trimEnd;

      drawWaveform();
      updateTimeDisplay();
      updateTrimDimmer();
      updateTrimInputs();
      recalculatePCM();
      updateFlashUsageUI();
      showToast(`✂️ Đã cắt bỏ đoạn đuôi (còn lại ${newBuffer.duration.toFixed(2)}s)!`);
    }

    // 3. Cắt giữ đoạn chọn (Crop to Selection)
    function cropToSelection() {
      if (!currentBuffer) return;
      const actx = getAudioContext();
      const rate = currentBuffer.sampleRate;
      const startSample = Math.floor(trimStart * rate);
      const endSample = Math.floor(trimEnd * rate);
      const numSamples = Math.max(1, endSample - startSample);

      if (numSamples <= 10) {
        showToast("⚠️ Vùng chọn quá ngắn để cắt!");
        return;
      }

      pushSlotHistory("Cắt giữ đoạn chọn");
      if (!slots[currentSlotIdx].originalBuffer) {
        slots[currentSlotIdx].originalBuffer = cloneAudioBuffer(currentBuffer);
      }

      const newBuffer = actx.createBuffer(
        currentBuffer.numberOfChannels,
        numSamples,
        rate
      );

      for (let ch = 0; ch < currentBuffer.numberOfChannels; ch++) {
        const srcData = currentBuffer.getChannelData(ch);
        const dstData = newBuffer.getChannelData(ch);
        dstData.set(srcData.subarray(startSample, endSample));
      }

      slots[currentSlotIdx].buffer = newBuffer;
      currentBuffer = newBuffer;
      trimStart = 0;
      trimEnd = newBuffer.duration;
      slots[currentSlotIdx].trimStart = 0;
      slots[currentSlotIdx].trimEnd = newBuffer.duration;

      drawWaveform();
      updateTimeDisplay();
      updateTrimDimmer();
      updateTrimInputs();
      recalculatePCM();
      updateFlashUsageUI();
      showToast(`✂️ Đã cắt giữ vùng chọn (${newBuffer.duration.toFixed(2)}s)!`);
    }

    // 2. Cắt bỏ đoạn giữa & ghép lại (Delete Selection and Merge with 5ms micro-crossfade)
    function deleteSelectionAndMerge() {
      if (!currentBuffer) return;
      const actx = getAudioContext();
      const rate = currentBuffer.sampleRate;
      const startSample = Math.floor(trimStart * rate);
      const endSample = Math.floor(trimEnd * rate);
      const totalSamples = currentBuffer.length;
      const leftSamples = startSample;
      const rightSamples = totalSamples - endSample;

      if (leftSamples + rightSamples <= 10) {
        showToast("⚠️ Không thể xóa toàn bộ âm thanh!");
        return;
      }

      pushSlotHistory("Cắt bỏ đoạn giữa & ghép lại");
      if (!slots[currentSlotIdx].originalBuffer) {
        slots[currentSlotIdx].originalBuffer = cloneAudioBuffer(currentBuffer);
      }

      // Micro-crossfade 5ms (80 mẫu ở 16kHz) để ghép cực mượt không bị tiếng bụp loa/click
      const fadeSamples = Math.min(80, Math.floor(leftSamples / 2), Math.floor(rightSamples / 2));
      const keepSamples = leftSamples + rightSamples - fadeSamples;

      const newBuffer = actx.createBuffer(
        currentBuffer.numberOfChannels,
        keepSamples,
        rate
      );

      for (let ch = 0; ch < currentBuffer.numberOfChannels; ch++) {
        const srcData = currentBuffer.getChannelData(ch);
        const dstData = newBuffer.getChannelData(ch);

        // Sao chép phần bên trái trước vùng crossfade
        if (leftSamples - fadeSamples > 0) {
          dstData.set(srcData.subarray(0, leftSamples - fadeSamples), 0);
        }

        // Crossfade mượt mà tại điểm nối
        for (let i = 0; i < fadeSamples; i++) {
          const wOut = 1.0 - (i / fadeSamples);
          const wIn = i / fadeSamples;
          const sL = srcData[leftSamples - fadeSamples + i];
          const sR = srcData[endSample + i];
          dstData[leftSamples - fadeSamples + i] = (sL * wOut) + (sR * wIn);
        }

        // Sao chép phần bên phải sau vùng crossfade
        if (rightSamples - fadeSamples > 0) {
          dstData.set(srcData.subarray(endSample + fadeSamples, totalSamples), leftSamples);
        }
      }

      slots[currentSlotIdx].buffer = newBuffer;
      currentBuffer = newBuffer;
      trimStart = 0;
      trimEnd = newBuffer.duration;
      slots[currentSlotIdx].trimStart = 0;
      slots[currentSlotIdx].trimEnd = newBuffer.duration;

      drawWaveform();
      updateTimeDisplay();
      updateTrimDimmer();
      updateTrimInputs();
      recalculatePCM();
      updateFlashUsageUI();
      showToast(`✂️ Đã cắt bỏ đoạn giữa và ghép 2 đầu (${newBuffer.duration.toFixed(2)}s)!`);
    }

    // 3. Phát riêng đoạn chọn (Play Selection Only)
    function playSelectionOnly() {
      if (!currentBuffer) return;
      stopPlayback();
      const actx = getAudioContext();
      const src = actx.createBufferSource();
      src.buffer = currentBuffer;
      src.playbackRate.value = playSpeed;

      const gain = actx.createGain();
      const vol = (slots[currentSlotIdx].volume || 100) / 100.0;
      gain.gain.value = vol;

      src.connect(gain);
      gain.connect(actx.destination);

      const selDur = Math.max(0.01, trimEnd - trimStart);
      src.start(0, trimStart, selDur);
      isPlaying = true;
      currentSource = src;
      currentGainNode = gain;

      const playIcon = document.getElementById('playIcon');
      if (playIcon) playIcon.textContent = '⏹';

      src.onended = () => {
        stopPlayback();
      };
      showToast("▶️ Đang phát riêng đoạn chọn...");
    }

    // 4. Nghe thử sau khi ghép (Preview Cut & Merge ảo mà không sửa buffer)
    function previewCutAndMerge() {
      if (!currentBuffer) return;
      const rate = currentBuffer.sampleRate;
      const startSample = Math.floor(trimStart * rate);
      const endSample = Math.floor(trimEnd * rate);
      const totalSamples = currentBuffer.length;
      const leftSamples = startSample;
      const rightSamples = totalSamples - endSample;

      if (leftSamples + rightSamples <= 10) {
        showToast("⚠️ Âm thanh còn lại quá ngắn để nghe thử!");
        return;
      }

      stopPlayback();
      const actx = getAudioContext();
      const fadeSamples = Math.min(80, Math.floor(leftSamples / 2), Math.floor(rightSamples / 2));
      const newLength = leftSamples + rightSamples - fadeSamples;
      const previewBuf = actx.createBuffer(currentBuffer.numberOfChannels, newLength, rate);

      for (let ch = 0; ch < currentBuffer.numberOfChannels; ch++) {
        const src = currentBuffer.getChannelData(ch);
        const dst = previewBuf.getChannelData(ch);
        if (leftSamples - fadeSamples > 0) {
          dst.set(src.subarray(0, leftSamples - fadeSamples), 0);
        }
        for (let i = 0; i < fadeSamples; i++) {
          const wOut = 1.0 - (i / fadeSamples);
          const wIn = i / fadeSamples;
          const sL = src[leftSamples - fadeSamples + i];
          const sR = src[endSample + i];
          dst[leftSamples - fadeSamples + i] = (sL * wOut) + (sR * wIn);
        }
        if (rightSamples - fadeSamples > 0) {
          dst.set(src.subarray(endSample + fadeSamples, totalSamples), leftSamples);
        }
      }

      const srcNode = actx.createBufferSource();
      srcNode.buffer = previewBuf;
      srcNode.playbackRate.value = playSpeed;

      const gain = actx.createGain();
      const vol = (slots[currentSlotIdx].volume || 100) / 100.0;
      gain.gain.value = vol;

      srcNode.connect(gain);
      gain.connect(actx.destination);

      srcNode.start(0);
      isPlaying = true;
      currentSource = srcNode;
      currentGainNode = gain;

      const playIcon = document.getElementById('playIcon');
      if (playIcon) playIcon.textContent = '⏹';

      srcNode.onended = () => {
        stopPlayback();
      };
      showToast(`⏩ Đang nghe thử sau ghép (${previewBuf.duration.toFixed(2)}s)...`);
    }

    // 5. Nhân đôi tiếng còi kèm khoảng nghỉ (Tạo còi đôi)
    function duplicateCurrentSound() {
      if (!currentBuffer) return;
      pushSlotHistory("Tạo còi đôi");
      if (!slots[currentSlotIdx].originalBuffer) {
        slots[currentSlotIdx].originalBuffer = cloneAudioBuffer(currentBuffer);
      }

      const actx = getAudioContext();
      const rate = currentBuffer.sampleRate;
      const gapSamples = Math.floor(rate * 0.08); // 80ms nghỉ tự nhiên giữa 2 nhịp
      const len1 = currentBuffer.length;
      const newLen = len1 * 2 + gapSamples;

      const newBuffer = actx.createBuffer(currentBuffer.numberOfChannels, newLen, rate);
      for (let ch = 0; ch < currentBuffer.numberOfChannels; ch++) {
        const src = currentBuffer.getChannelData(ch);
        const dst = newBuffer.getChannelData(ch);
        dst.set(src, 0);
        dst.set(src, len1 + gapSamples);
      }

      slots[currentSlotIdx].buffer = newBuffer;
      currentBuffer = newBuffer;
      trimStart = 0;
      trimEnd = newBuffer.duration;
      slots[currentSlotIdx].trimStart = 0;
      slots[currentSlotIdx].trimEnd = newBuffer.duration;

      drawWaveform();
      updateTimeDisplay();
      updateTrimDimmer();
      updateTrimInputs();
      recalculatePCM();
      updateFlashUsageUI();
      showToast(`🔁 Đã tạo tiếng còi đôi (${newBuffer.duration.toFixed(2)}s)!`);
    }

    // 6. Ghép thêm file âm thanh nối tiếp vào đuôi
    async function handleAppendFile(e) {
      const file = e.target.files && e.target.files[0];
      if (!file) return;

      try {
        const ab = await file.arrayBuffer();
        const actx = getAudioContext();
        const appendBuf = await actx.decodeAudioData(ab);

        if (!currentBuffer) {
          slots[currentSlotIdx].buffer = appendBuf;
          slots[currentSlotIdx].originalBuffer = appendBuf;
          slots[currentSlotIdx].trimStart = 0;
          slots[currentSlotIdx].trimEnd = appendBuf.duration;
          slots[currentSlotIdx].name = file.name.replace(/\.[^/.]+$/, "");
          currentBuffer = appendBuf;
        } else {
          pushSlotHistory("Ghép thêm file");
          const rate = currentBuffer.sampleRate;
          let resampledAppend = appendBuf;
          if (appendBuf.sampleRate !== rate) {
            const numDst = Math.round(appendBuf.duration * rate);
            resampledAppend = actx.createBuffer(1, numDst, rate);
            const srcCh = appendBuf.getChannelData(0);
            const dstCh = resampledAppend.getChannelData(0);
            const step = (srcCh.length - 1) / Math.max(1, numDst - 1);
            for (let i = 0; i < numDst; i++) {
              const pos = i * step;
              const idx = Math.floor(pos);
              const frac = pos - idx;
              dstCh[i] = srcCh[idx] * (1 - frac) + (srcCh[Math.min(srcCh.length - 1, idx + 1)] || 0) * frac;
            }
          }

          const gapSamples = Math.floor(rate * 0.04); // 40ms khoảng đệm
          const totalLen = currentBuffer.length + gapSamples + resampledAppend.length;
          const mergedBuf = actx.createBuffer(1, totalLen, rate);
          const dst = mergedBuf.getChannelData(0);

          dst.set(currentBuffer.getChannelData(0), 0);
          dst.set(resampledAppend.getChannelData(0), currentBuffer.length + gapSamples);

          slots[currentSlotIdx].buffer = mergedBuf;
          currentBuffer = mergedBuf;
          trimStart = 0;
          trimEnd = mergedBuf.duration;
          slots[currentSlotIdx].trimStart = 0;
          slots[currentSlotIdx].trimEnd = mergedBuf.duration;
        }

        drawWaveform();
        updateTimeDisplay();
        updateTrimDimmer();
        updateTrimInputs();
        recalculatePCM();
        updateFlashUsageUI();
        showToast(`➕ Đã ghép nối tiếp file '${file.name}' vào đuôi!`);
      } catch (err) {
        alert("Lỗi khi ghép file âm thanh: " + err.message);
      }
      e.target.value = '';
    }

    // 7. Khôi phục âm thanh ban đầu (Reset / Undo to original)
    function restoreOriginalAudio() {
      if (!slots[currentSlotIdx]) return;
      if (slots[currentSlotIdx].originalBuffer) {
        pushSlotHistory("Khôi phục bản gốc");
        currentBuffer = cloneAudioBuffer(slots[currentSlotIdx].originalBuffer);
        slots[currentSlotIdx].buffer = currentBuffer;
        trimStart = 0;
        trimEnd = currentBuffer.duration;
        slots[currentSlotIdx].trimStart = 0;
        slots[currentSlotIdx].trimEnd = currentBuffer.duration;
        drawWaveform();
        updateTimeDisplay();
        updateTrimDimmer();
        updateTrimInputs();
        recalculatePCM();
        updateFlashUsageUI();
        showToast("🔄 Đã khôi phục lại âm thanh gốc ban đầu!");
      } else if (currentBuffer) {
        trimStart = 0;
        trimEnd = currentBuffer.duration;
        slots[currentSlotIdx].trimStart = 0;
        slots[currentSlotIdx].trimEnd = currentBuffer.duration;
        updateTrimDimmer();
        updateTimeDisplay();
        updateTrimInputs();
        recalculatePCM();
        updateFlashUsageUI();
        showToast("🔄 Đã mở rộng vùng chọn toàn bộ âm thanh!");
      }
    }

    // 8. Làm mượt đầu và đuôi (Fade In / Fade Out)
    function applyFade(direction) {
      if (!currentBuffer) return;
      pushSlotHistory(direction === 'in' ? "Fade In" : "Fade Out");
      const ch = currentBuffer.getChannelData(0);
      const rate = currentBuffer.sampleRate;
      const fadeDuration = 0.04; // 40ms mượt mà
      const fadeSamples = Math.min(Math.floor(rate * fadeDuration), Math.floor(ch.length / 2));

      if (!slots[currentSlotIdx].originalBuffer) {
        slots[currentSlotIdx].originalBuffer = cloneAudioBuffer(currentBuffer);
      }

      if (direction === 'in') {
        for (let i = 0; i < fadeSamples; i++) {
          const factor = i / fadeSamples;
          ch[i] *= factor;
        }
        showToast("📈 Đã áp dụng Fade In (Làm mượt đầu âm thanh)!");
      } else if (direction === 'out') {
        const startIdx = ch.length - fadeSamples;
        for (let i = 0; i < fadeSamples; i++) {
          const factor = 1.0 - (i / fadeSamples);
          ch[startIdx + i] *= factor;
        }
        showToast("📉 Đã áp dụng Fade Out (Làm mượt đuôi âm thanh)!");
      }

      drawWaveform();
      recalculatePCM();
      updateFlashUsageUI();
    }

    // === ĐO DUNG LƯỢNG BỘ NHỚ FLASH ESP32-C3 (FLASH STORAGE METER) ===
    function updateFlashUsageUI() {
      const TOTAL_FLASH_BYTES = 2162688; // 2,112 KB (0x210000 bytes trong partitions_4mb.csv)
      const headerBytes = slots.length <= 11 ? 512 : 1024;
      let totalPcmBytes = 0;
      const slotSizes = [];

      for (let i = 0; i < slots.length; i++) {
        const sLen = slots[i] && slots[i].pcm ? slots[i].pcm.length : 0;
        slotSizes.push(sLen);
        totalPcmBytes += sLen;
      }

      const totalUsedBytes = headerBytes + totalPcmBytes;
      const usedKb = (totalUsedBytes / 1024).toFixed(1);
      const freeKb = Math.max(0, (TOTAL_FLASH_BYTES - totalUsedBytes) / 1024).toFixed(1);
      const pct = Math.min(100, (totalUsedBytes / TOTAL_FLASH_BYTES) * 100).toFixed(1);

      const fillEl = document.getElementById('flashMeterFill');
      if (fillEl) {
        fillEl.style.width = `${Math.max(1, pct)}%`;
        if (parseFloat(pct) > 90) {
          fillEl.style.background = 'linear-gradient(90deg, #ffb834 0%, #ff4772 100%)';
        } else {
          fillEl.style.background = 'linear-gradient(90deg, #00d2ff 0%, #00f0aa 100%)';
        }
      }

      const usedEl = document.getElementById('flashUsedText');
      if (usedEl) {
        usedEl.innerHTML = `Đã dùng: <strong>${usedKb} KB</strong> / 2,112 KB (${pct}%) • <strong>${slots.length} Slots</strong>`;
      }

      const freeEl = document.getElementById('flashFreeText');
      if (freeEl) {
        freeEl.textContent = `Trống: ${freeKb} KB`;
      }

      const slotsEl = document.getElementById('flashMeterSlots');
      if (slotsEl) {
        let html = `<span class="flash-slot-pill header-pill">Header: ${(headerBytes / 1024).toFixed(1)} KB</span>`;
        for (let i = 0; i < slots.length; i++) {
          const kb = (slotSizes[i] / 1024).toFixed(1);
          const isCur = i === currentSlotIdx ? 'active-slot-pill' : '';
          html += `<span class="flash-slot-pill ${isCur}">Slot ${i}: ${kb} KB</span>`;
        }
        slotsEl.innerHTML = html;
      }
    }

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
      updateTrimInputs();
      recalculatePCM();
      updateFlashUsageUI();
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
        updateFlashUsageUI();
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

      const targetRate = 22050;
      const targetLen = Math.floor(numSamples * (targetRate / rate));
      const pcm = new Uint8Array(220 + targetLen);

      pcm.fill(128, 0, 220); // 10ms đệm 0x80 chống bụp loa ở 22050Hz

      // Nhân hệ số Volume đã chỉnh
      const volFactor = (slots[currentSlotIdx].volume || 100) / 100.0;
      const ratio = numSamples / targetLen;

      for (let i = 0; i < targetLen; i++) {
        const srcIdx = startSample + Math.floor(i * ratio);
        const s = ch[Math.min(srcIdx, ch.length - 1)] * volFactor;
        // Chặn cận mềm [0, 255]
        pcm[220 + i] = Math.max(0, Math.min(255, Math.round((s * 127) + 128)));
      }

      slots[currentSlotIdx].pcm = pcm;
      slots[currentSlotIdx].sampleRate = targetRate;
      renderSlotsUI();
      updateFlashUsageUI();
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
        slots[currentSlotIdx].originalBuffer = decoded;
        slots[currentSlotIdx].trimStart = 0;
        slots[currentSlotIdx].trimEnd = decoded.duration;
        slots[currentSlotIdx].name = file.name.replace(/\.[^/.]+$/, "");
        slots[currentSlotIdx].volume = 100;

        selectSlot(currentSlotIdx);
        autoTrimSilence();
        normalizeVolume();
        updateTrimInputs();
        updateFlashUsageUI();
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
      slots[currentSlotIdx].originalBuffer = buf;
      slots[currentSlotIdx].trimStart = 0;
      slots[currentSlotIdx].trimEnd = buf.duration;
      slots[currentSlotIdx].name = name;
      slots[currentSlotIdx].volume = 100;

      selectSlot(currentSlotIdx);
      recalculatePCM();
      updateTrimInputs();
      updateFlashUsageUI();
      showToast(`🎉 Đã gán '${name}' vào Slot ${currentSlotIdx}!`);
    }

    function ensureSlotPCM(idx) {
      const s = slots[idx];
      if (!s || !s.buffer) return;
      const ch = s.buffer.getChannelData(0);
      const rate = s.buffer.sampleRate;
      const startSample = Math.floor((s.trimStart || 0) * rate);
      const endSample = Math.floor((s.trimEnd || s.buffer.duration) * rate);
      const numSamples = Math.max(1, endSample - startSample);

      const targetRate = 22050;
      const targetLen = Math.floor(numSamples * (targetRate / rate));
      const pcm = new Uint8Array(220 + targetLen);
      pcm.fill(128, 0, 220); // 10ms DC 128 chống bụp loa ở 22050Hz

      const volFactor = (s.volume || 100) / 100.0;
      const ratio = numSamples / targetLen;

      for (let i = 0; i < targetLen; i++) {
        const srcIdx = startSample + Math.floor(i * ratio);
        const val = ch[Math.min(srcIdx, ch.length - 1)] * volFactor;
        pcm[220 + i] = Math.max(0, Math.min(255, Math.round((val * 127) + 128)));
      }
      s.pcm = pcm;
      s.sampleRate = targetRate;
    }

    // Đóng gói danh sách Slot âm thanh thành Uint8Array hoàn chỉnh
    function generateSoundBankBuffer() {
      const headerSize = slots.length <= 11 ? 512 : 1024;
      let totalPcmLen = 0;
      for (let i = 0; i < slots.length; i++) {
        if (!slots[i].pcm || slots[i].pcm.length === 0) {
          ensureSlotPCM(i);
        }
        totalPcmLen += (slots[i].pcm ? slots[i].pcm.length : 0);
      }

      const buffer = new Uint8Array(headerSize + totalPcmLen);
      const view = new DataView(buffer.buffer);

      view.setUint32(0, 0x4B435544, true); // Magic 'DUCK'
      view.setUint16(4, 1, true);          // Version 1
      view.setUint16(6, slots.length, true); // Số lượng slot thực tế

      let currOffset = headerSize;
      for (let i = 0; i < slots.length; i++) {
        const s = slots[i];
        const slotHeadOffset = 8 + i * 44;
        const pcmLen = s.pcm ? s.pcm.length : 0;

        view.setUint32(slotHeadOffset, currOffset, true);
        view.setUint32(slotHeadOffset + 4, pcmLen, true);
        view.setUint16(slotHeadOffset + 8, s.sampleRate || 22050, true);
        view.setUint16(slotHeadOffset + 10, 0, true);

        const nameBytes = new TextEncoder().encode((s.name || `Slot ${i}`).slice(0, 31));
        buffer.set(nameBytes, slotHeadOffset + 12);

        if (s.pcm && pcmLen > 0) {
          buffer.set(s.pcm, currOffset);
        }
        currOffset += pcmLen;
      }
      return buffer;
    }

    // Xuất gói nhị phân sound_bank.bin
    function exportSoundBankBin() {
      const buffer = generateSoundBankBuffer();
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

    // Web Serial ESP32-C3 Flasher Logic
    let isFlashing = false;
    let esptoolModule = null;

    async function loadEsptool() {
      if (esptoolModule) return esptoolModule;
      try {
        esptoolModule = await import('./esptool-bundle.js');
        return esptoolModule;
      } catch (e1) {
        try {
          esptoolModule = await import('https://unpkg.com/esptool-js@0.5.4/bundle.js');
          return esptoolModule;
        } catch (e2) {
          throw new Error("Không thể tải thư viện nạp esptool-js (kiểm tra file esptool-bundle.js hoặc mạng)");
        }
      }
    }

    function openFlashModal() {
      const modal = document.getElementById('flashModal');
      modal.classList.add('open');

      const alertBox = document.getElementById('flashAlertBox');
      alertBox.style.display = 'none';

      if (!('serial' in navigator)) {
        alertBox.className = 'flash-alert-box error';
        alertBox.style.display = 'block';
        alertBox.innerHTML = `
          <strong>⚠️ Trình duyệt chưa bật tính năng mở cổng COM (Web Serial)!</strong><br>
          - Bạn đang mở trực tiếp file qua giao thức <code>file://</code> (cần mở qua <code>http://localhost:8765</code> để cấp quyền cổng COM).<br>
          👉 <strong>Cách 1:</strong> Nhấp đúp file <code>nap_tieng_coi.bat</code> trong thư mục để tự động mở qua <code>http://localhost:8765</code>.<br>
          👉 <strong>Cách 2:</strong> Mở bản Online tại GitHub Pages (HTTPS) để nạp 1-click không cần cài Python.<br>
          👉 <strong>Cách 3:</strong> Bấm nút <code>📦 Xuất sound_bank.bin</code> ở trên để tải file và dùng nạp truyền thống.
        `;
        document.getElementById('btnStartFlash').disabled = true;
      } else {
        document.getElementById('btnStartFlash').disabled = false;
      }
    }

    function closeFlashModal() {
      if (isFlashing) {
        if (!confirm("Quá trình nạp đang diễn ra. Bạn có chắc chắn muốn đóng?")) return;
      }
      document.getElementById('flashModal').classList.remove('open');
    }

    function logFlash(text, type = 'info') {
      const term = document.getElementById('flashTerminal');
      const line = document.createElement('div');
      line.className = `term-line ${type}`;
      line.textContent = text;
      term.appendChild(line);
      term.scrollTop = term.scrollHeight;
    }

    function clearFlashTerminal() {
      document.getElementById('flashTerminal').innerHTML = '';
    }

    function updateFlashUI(state, percent = 0, detail = '') {
      const progressWrapper = document.getElementById('flashProgressWrapper');
      const progressFill = document.getElementById('flashProgressFill');
      const statusText = document.getElementById('flashStatusText');
      const percentText = document.getElementById('flashPercentText');
      const btnStart = document.getElementById('btnStartFlash');

      if (state === 'idle') {
        progressWrapper.style.display = 'none';
        btnStart.disabled = false;
        btnStart.innerHTML = '<span>🔌</span> Chọn Cổng COM & Nạp Ngay';
      } else if (state === 'flashing') {
        progressWrapper.style.display = 'block';
        btnStart.disabled = true;
        btnStart.innerHTML = '<span>⏳</span> Đang nạp...';
        progressFill.style.width = `${percent}%`;
        statusText.textContent = detail || 'Đang ghi dữ liệu...';
        percentText.textContent = `${percent}%`;
      } else if (state === 'success') {
        progressWrapper.style.display = 'block';
        btnStart.disabled = false;
        btnStart.innerHTML = '<span>🎉</span> Nạp Thành Công! Bấm để nạp lại';
        progressFill.style.width = '100%';
        statusText.textContent = '🎉 NẠP THÀNH CÔNG 100%!';
        percentText.textContent = '100%';
      } else if (state === 'error') {
        btnStart.disabled = false;
        btnStart.innerHTML = '<span>🔄</span> Thử Nạp Lại';
        statusText.textContent = '❌ Nạp thất bại!';
      }
    }

    async function startWebSerialFlash() {
      if (isFlashing) return;

      const alertBox = document.getElementById('flashAlertBox');
      alertBox.style.display = 'none';

      if (!('serial' in navigator)) {
        openFlashModal();
        return;
      }

      let port = null;
      let transport = null;

      try {
        isFlashing = true;
        updateFlashUI('flashing', 0, 'Đang đóng gói âm thanh...');
        logFlash('--------------------------------------------------', 'muted');
        logFlash('[*] Đang đóng gói dữ liệu 5 slot âm thanh...', 'info');

        const buffer = generateSoundBankBuffer();
        const kbSize = (buffer.length / 1024).toFixed(1);
        logFlash(`[+] Gói sound_bank.bin đã tạo xong: ${buffer.length} bytes (~${kbSize} KB)`, 'success');

        logFlash('[*] Đang khởi tạo module Web Serial Flasher...', 'info');
        const esptool = await loadEsptool();

        logFlash('[*] Vui lòng chọn cổng COM của còi xe trong hộp thoại trình duyệt...', 'warn');
        port = await navigator.serial.requestPort();

        const baudrate = parseInt(document.getElementById('flashBaudSelect').value) || 460800;
        logFlash(`[*] Đã chọn cổng COM! Đang kết nối ở tốc độ ${baudrate} baud...`, 'info');

        transport = new esptool.Transport(port);

        const terminalObj = {
          clean: () => {},
          writeLine: (data) => {
            const cleanStr = String(data).trim();
            if (cleanStr) logFlash(cleanStr, 'muted');
          },
          write: (data) => {
            const cleanStr = String(data).trim();
            if (cleanStr) logFlash(cleanStr, 'muted');
          }
        };

        const esploader = new esptool.ESPLoader({
          transport: transport,
          baudrate: baudrate,
          terminal: terminalObj,
          romBaudrate: 115200
        });

        logFlash('[*] Đang bắt tay và nhận diện vi điều khiển...', 'info');
        updateFlashUI('flashing', 10, 'Đang kết nối ESP32...');

        const chipDesc = await esploader.main("default_reset");
        logFlash(`[+] Nhận diện thành công: ${chipDesc}`, 'success');

        updateFlashUI('flashing', 25, 'Đang ghi dữ liệu vào Flash 0x1E0000...');
        logFlash(`[*] Bắt đầu nạp ${kbSize} KB vào phân vùng 0x1E0000...`, 'info');

        // Chuyển Uint8Array sang binary string cho esptool-js
        const bstr = esploader.ui8ToBstr(buffer);

        await esploader.writeFlash({
          fileArray: [{ data: bstr, address: 0x1E0000 }],
          flashSize: 'keep',
          flashMode: 'keep',
          flashFreq: 'keep',
          eraseAll: false,
          compress: true,
          reportProgress: (fileIndex, written, total) => {
            const pct = Math.floor((written / total) * 100);
            const writtenKb = (written / 1024).toFixed(1);
            const totalKb = (total / 1024).toFixed(1);
            updateFlashUI('flashing', pct, `Đang nạp: ${writtenKb}/${totalKb} KB (${pct}%)`);
          }
        });

        logFlash('[+] Đã ghi xong 100% dữ liệu vào Flash 0x1E0000!', 'success');
        updateFlashUI('flashing', 95, 'Đang khởi động lại còi xe...');

        logFlash('[*] Đang Hard Reset vi điều khiển còi xe...', 'info');
        try {
          await esploader.hardReset();
        } catch (rstErr) {
          try {
            await transport.setDTR(false);
            await new Promise(r => setTimeout(r, 100));
            await transport.setDTR(true);
          } catch(e){}
        }

        try {
          await transport.disconnect();
        } catch(e){}

        updateFlashUI('success', 100);
        logFlash('🎉 NẠP THÀNH CÔNG 100%! Còi xe đã sẵn sàng!', 'success');
        logFlash('👉 Bạn có thể rút cáp USB, bật khóa xe và bấm còi trải nghiệm ngay!', 'success');
        showToast("🎉 NẠP ÂM THANH THÀNH CÔNG VÀO CÒI XE!", 6000);

        alertBox.className = 'flash-alert-box success';
        alertBox.style.display = 'block';
        alertBox.innerHTML = `
          <strong>🎉 NẠP THÀNH CÔNG 100%!</strong><br>
          Phân vùng âm thanh <code>0x1E0000</code> đã được nạp dữ liệu mới nhất.<br>
          Bạn có thể tắt mở khóa xe máy hoặc nhấn nút còi để nghe thử ngay!
        `;

      } catch (err) {
        console.error("Flash error:", err);
        updateFlashUI('error');

        if (err.name === 'NotFoundError' || err.message.includes('No port selected')) {
          logFlash('[-] Người dùng đã hủy chọn cổng COM.', 'warn');
        } else {
          logFlash(`[-] Lỗi trong quá trình nạp: ${err.message}`, 'error');
          alertBox.className = 'flash-alert-box error';
          alertBox.style.display = 'block';
          alertBox.innerHTML = `
            <strong>[-] Nạp thất bại: ${err.message}</strong><br>
            <em>Gợi ý khắc phục:</em><br>
            1. Đảm bảo cáp USB Type-C cắm chắc chắn và có hỗ trợ truyền dữ liệu (data).<br>
            2. Nếu cổng COM đang bị phần mềm khác (Serial Monitor, v.v.) chiếm dụng, hãy tắt chúng trước.<br>
            3. Nhấn giữ nút BOOT trên mạch còi rồi cắm cáp lại để thử lại.<br>
            4. Hoặc bạn có thể xuất file <code>sound_bank.bin</code> và nạp bằng file .bat truyền thống.
          `;
        }

        if (transport) {
          try { await transport.disconnect(); } catch(e){}
        }
      } finally {
        isFlashing = false;
      }
    }

    function handleFlashClick() {
      openFlashModal();
    }

    window.addEventListener('DOMContentLoaded', () => {
      initSlotsAudio();
      window.addEventListener('resize', drawWaveform);
    });

    window.addEventListener('keydown', (e) => {
      // Undo: Ctrl+Z
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z' && !e.shiftKey) {
        if (e.target.tagName !== 'INPUT') {
          e.preventDefault();
          undoLastAction();
        }
      }
      // Redo: Ctrl+Y hoặc Ctrl+Shift+Z
      if (((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'y') ||
          ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'z')) {
        if (e.target.tagName !== 'INPUT') {
          e.preventDefault();
          redoLastAction();
        }
      }
      if (e.code === 'Space' && e.target.tagName !== 'INPUT') {
        e.preventDefault();
        togglePlay();
      }
      if (e.code === 'Escape') {
        closePresetModal();
        closeFlashModal();
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

if os.path.exists(os.path.dirname(OUTPUT_DOCS)):
    with open(OUTPUT_DOCS, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"Created {OUTPUT_DOCS} ({os.path.getsize(OUTPUT_DOCS):,} bytes)")

    # Copy esptool-bundle.js to docs/ for GitHub Pages
    src_bundle = os.path.join(SCRIPT_DIR, "..", "tools", "esptool-bundle.js")
    dst_bundle = os.path.join(SCRIPT_DIR, "..", "docs", "esptool-bundle.js")
    if os.path.exists(src_bundle):
        import shutil
        shutil.copy2(src_bundle, dst_bundle)
        print(f"Copied {src_bundle} to {dst_bundle}")
