# Risk Auto Clicker

A high-performance auto-clicker application with a modern minimalist interface, sub-millisecond low-level clicking precision, and fluid spring physics tab-switching animations.

![Risk Auto Clicker UI](https://raw.githubusercontent.com/gkrotechs/RiskAutoClicker/main/preview.png)

---

## ✨ Highlights & Features

### 🎨 Minimalist UI & Tab Switching Animations
- **Spring-Physics Gliding Indicator**: An animated elastic indicator pill (`cubic-bezier(0.34, 1.56, 0.64, 1)`) glides smoothly between active tabs on the top navigation bar and settings sidebar.
- **Pure Light & Dark Themes**: 100% neutral, high-contrast Light and Dark modes.
- **Dynamic Window Morphing**: Seamless transition between compact bar mode (`585x235`) and settings dashboard (`585x620`).

### ⚡ Low-Level Precision Clicking Engine
- **Windows Multimedia Timer Subsystem**: Utilizes `winmm.dll` `timeBeginPeriod(1)` to bypass Windows default 15.6ms timer quantum, ensuring steady precision up to 1000+ CPS.
- **Direct Win32 `SendInput`**: Lowest possible latency mouse and keyboard event dispatch.
- **Duty Cycle Control**: Adjust the exact ratio of press down vs release time (e.g. 45% press / 55% release).
- **Gaussian Jitter Speed Randomization**: Human-like speed variance (0–100%) to prevent bot detection in games.
- **Targeting Modes**: Cursor tracking or Fixed Screen Coordinate Locking with a built-in 2-second crosshair coordinate picker.
- **Process Filter**: Target specific games/applications (e.g., Minecraft, Roblox, Cookie Clicker) and only click when focused.

### ⌨ Global Hotkeys & Safety
- **Custom Hotkey Recorder**: Default `Ctrl + Y` (or any custom hotkey).
- **Emergency Panic Stop**: Press `F8` to instantly halt all active clicking loops.
- **Trigger Modes**: Toggle (start/stop on press) or Hold (click only while key is depressed).

### 📊 Real-Time Analytics & Presets
- **Usage Statistics**: Tracks lifetime Total Clicks, Total Clicking Time, Average CPU Usage, and Total Clicking Sessions.
- **Built-in Presets**:
  - *Minecraft PvP* (16 CPS, 42% Duty, 25% Jitter)
  - *Jitter Click* (14.5 CPS, 50% Duty, 45% Jitter)
  - *Auto Clicker for Roblox* (40 CPS, 45% Duty, 15% Jitter)
  - *Cookie Clicker* (100 CPS, 45% Duty, 35% Jitter)
  - *Fastest* (500 CPS, 50% Duty)
- **Interactive CPS Test Sandbox**: Built-in clicking test sandbox with live CPS calculation and ripple animations.

---

## 🚀 Quick Start

### Prerequisites
- Windows 10 / 11
- Python 3.10+
- Microsoft Edge WebView2 runtime (pre-installed on Windows 10/11)

### Running Risk Auto Clicker
Double-click `run.bat` or run in terminal:
```powershell
python main.py
```

### Running Unit Tests
```powershell
python -m unittest tests/test_all.py
```
