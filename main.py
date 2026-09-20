import os
import sys
import webview
import ctypes

# Windows DPI awareness & Taskbar AppUserModelID
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2) # Per-monitor DPI aware
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("gkrotech.riskautoclicker.app.1.0")
except Exception:
    pass

from backend.clicker_engine import ClickerEngine
from backend.stats_manager import StatsManager
from backend.preset_manager import PresetManager
from backend.config_manager import ConfigManager
from backend.hotkey_manager import HotkeyManager
from backend.api_bridge import ApiBridge

def main():
    # Base directory paths (handles frozen .exe and regular script execution)
    if getattr(sys, 'frozen', False):
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        config_dir = os.path.join(os.path.dirname(sys.executable), "config")
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_dir = os.path.join(base_dir, "config")

    frontend_dir = os.path.join(base_dir, "frontend")
    html_path = os.path.join(frontend_dir, "index.html")

    # Initialize Core Subsystems
    engine = ClickerEngine()
    stats = StatsManager(config_dir=config_dir)
    presets = PresetManager(config_dir=config_dir)
    config = ConfigManager(config_dir=config_dir)
    hotkeys = HotkeyManager()

    window_holder = {}
    bridge = ApiBridge(engine, stats, presets, config, hotkeys, window_holder)

    # Initial Hotkey registration from saved config
    saved_hotkey = config.get("hotkey", "Ctrl + Y")
    saved_mode = config.get("trigger_mode", "Toggle")
    saved_panic = config.get("panic_hotkey", "F8")
    hotkeys.register_hotkey(saved_hotkey, saved_mode)
    hotkeys.register_panic_hotkey(saved_panic)

    theme_setting = config.get("theme", "light")
    if theme_setting == "dark":
        bg_color = "#121215"
    elif theme_setting == "blue":
        bg_color = "#eaf2f9"
    else:
        bg_color = "#ffffff"

    # Create PyWebView Window (Frameless, draggable, Edge Chromium WebView2 engine)
    window = webview.create_window(
        title="Risk Auto Clicker",
        url=f"file:///{html_path.replace(os.sep, '/')}",
        js_api=bridge,
        width=585,
        height=235,
        resizable=True,
        frameless=True,
        easy_drag=False,
        on_top=config.get("always_on_top", False),
        background_color=bg_color
    )
    window_holder['window'] = window

    try:
        # Start PyWebView GUI Event Loop
        webview.start(debug=False, gui='edgechromium')
    finally:
        # Graceful cleanup on window close
        engine.cleanup()
        hotkeys.cleanup()
        stats.save()

if __name__ == "__main__":
    main()
