import os
import webbrowser
import threading
import time
import ctypes
from ctypes import wintypes

user32 = ctypes.WinDLL('user32', use_last_error=True)

class ApiBridge:
    def __init__(self, engine, stats, presets, config, hotkeys, window_holder):
        self.engine = engine
        self.stats = stats
        self.presets = presets
        self.config = config
        self.hotkeys = hotkeys
        self._window_holder = window_holder # dictionary holding 'window': webview.Window
        
        # Connect engine callbacks to stats & UI
        self.engine.on_click_callback = self._on_engine_click
        self.engine.on_state_change = self._on_engine_state_change
        self.hotkeys.on_trigger = self._on_hotkey_trigger
        self.hotkeys.on_panic = self._on_hotkey_panic

    def _get_window(self):
        if self._window_holder:
            return self._window_holder.get('window')
        return None

    def _on_engine_click(self, total_clicks):
        pass # UI can poll or receive batch updates to prevent bridge saturating

    def _on_engine_state_change(self, is_running):
        if is_running:
            self.stats.on_session_start()
        else:
            self.stats.on_session_end(self.engine.total_clicks_session)
            self.engine.total_clicks_session = 0

        # Dispatch state change to UI
        win = self._get_window()
        if win:
            try:
                win.evaluate_js(f"window.onStateChanged && window.onStateChanged({str(is_running).lower()})")
            except Exception:
                pass

    def _on_hotkey_trigger(self, action):
        if action == "toggle":
            self.toggle_clicker()
        elif action == "start":
            self.start_clicker()
        elif action == "stop":
            self.stop_clicker()

    def _on_hotkey_panic(self):
        self.stop_clicker()

    # --- API methods callable from JS ---

    def get_initial_state(self):
        return {
            "is_running": self.engine.is_running,
            "engine": {
                "cps": self.engine.cps,
                "rate_unit": self.engine.rate_unit,
                "rate_mode": self.engine.rate_mode,
                "input_type": self.engine.input_type,
                "mouse_button": self.engine.mouse_button,
                "click_type": self.engine.click_type,
                "duty_cycle": self.engine.duty_cycle,
                "speed_randomization": self.engine.speed_randomization,
                "location_mode": self.engine.location_mode,
                "target_x": self.engine.target_x,
                "target_y": self.engine.target_y,
                "target_process_name": self.engine.target_process_name,
                "only_when_focused": self.engine.only_when_focused,
            },
            "hotkey": {
                "current": self.hotkeys.current_hotkey,
                "mode": self.hotkeys.trigger_mode,
                "panic": self.hotkeys.panic_hotkey
            },
            "config": self.config.get_all(),
            "stats": self.stats.get_stats_dict(),
            "presets": self.presets.get_presets(),
            "active_preset": self.presets.active_preset_name
        }

    def update_clicker_config(self, cfg):
        if not isinstance(cfg, dict):
            return False
        if "cps" in cfg:
            try:
                self.engine.cps = float(cfg["cps"])
            except ValueError:
                pass
        if "rate_unit" in cfg:
            self.engine.rate_unit = cfg["rate_unit"]
        if "rate_mode" in cfg:
            self.engine.rate_mode = cfg["rate_mode"]
        if "input_type" in cfg:
            self.engine.input_type = cfg["input_type"]
        if "mouse_button" in cfg:
            self.engine.mouse_button = cfg["mouse_button"]
        if "click_type" in cfg:
            self.engine.click_type = cfg["click_type"]
        if "duty_cycle" in cfg:
            try:
                self.engine.duty_cycle = float(cfg["duty_cycle"])
            except ValueError:
                pass
        if "speed_randomization" in cfg:
            try:
                self.engine.speed_randomization = float(cfg["speed_randomization"])
            except ValueError:
                pass
        if "location_mode" in cfg:
            self.engine.location_mode = cfg["location_mode"]
        if "target_x" in cfg:
            self.engine.target_x = int(cfg["target_x"])
        if "target_y" in cfg:
            self.engine.target_y = int(cfg["target_y"])
        if "target_process_name" in cfg:
            self.engine.target_process_name = cfg["target_process_name"]
        if "only_when_focused" in cfg:
            self.engine.only_when_focused = bool(cfg["only_when_focused"])
            
        return True

    def toggle_clicker(self):
        new_state = self.engine.toggle()
        return new_state

    def start_clicker(self):
        self.engine.start()
        return True

    def stop_clicker(self):
        self.engine.stop()
        return False

    def set_hotkey(self, hotkey_str, trigger_mode="Toggle"):
        self.hotkeys.register_hotkey(hotkey_str, trigger_mode)
        self.config.set("hotkey", hotkey_str)
        self.config.set("trigger_mode", trigger_mode)
        return True

    def record_hotkey(self):
        new_key = self.hotkeys.record_next_hotkey()
        self.config.set("hotkey", new_key)
        return new_key

    def set_panic_hotkey(self, panic_str):
        self.hotkeys.register_panic_hotkey(panic_str)
        self.config.set("panic_hotkey", panic_str)
        return True

    def get_presets(self):
        return self.presets.get_presets()

    def apply_preset(self, preset_id):
        all_presets = self.presets.get_presets()
        for p in all_presets:
            if p.get("id") == preset_id:
                self.presets.active_preset_name = p.get("name")
                self.engine.cps = float(p.get("cps", 100))
                self.engine.rate_unit = p.get("rate_unit", "Second")
                self.engine.rate_mode = p.get("rate_mode", "Rate")
                self.engine.input_type = p.get("input_type", "Mouse")
                self.engine.mouse_button = p.get("mouse_button", "LEFT")
                self.engine.duty_cycle = float(p.get("duty_cycle", 45))
                self.engine.speed_randomization = float(p.get("speed_randomization", 35))
                if "hotkey" in p:
                    self.set_hotkey(p["hotkey"], p.get("trigger_mode", "Toggle"))
                return p
        return None

    def save_preset(self, preset_data):
        return self.presets.add_preset(preset_data)

    def delete_preset(self, preset_id):
        return self.presets.delete_preset(preset_id)

    def get_processes(self):
        from .process_manager import ProcessManager
        return ProcessManager.get_window_processes()

    def get_stats(self):
        return self.stats.get_stats_dict()

    def reset_stats(self):
        self.stats.reset_stats()
        return self.stats.get_stats_dict()

    def update_config(self, key, value):
        self.config.set(key, value)
        win = self._get_window()
        if key == "always_on_top" and win:
            win.on_top = bool(value)
        return True

    def set_always_on_top(self, enabled):
        self.config.set("always_on_top", enabled)
        win = self._get_window()
        if win:
            win.on_top = bool(enabled)
        return enabled

    def get_cursor_position(self):
        class POINT(ctypes.Structure):
            _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]
        pt = POINT()
        user32.GetCursorPos(ctypes.byref(pt))
        return {"x": pt.x, "y": pt.y}

    def pick_coordinate_mode(self):
        """Wait 2 seconds then grab cursor position."""
        time.sleep(2.0)
        return self.get_cursor_position()

    def resize_window(self, width, height):
        win = self._get_window()
        if win:
            try:
                win.resize(int(width), int(height))
            except Exception as e:
                print(f"Error resizing window: {e}")
        return True

    def minimize_window(self):
        win = self._get_window()
        if win:
            win.minimize()
        return True

    def close_window(self):
        win = self._get_window()
        if win:
            win.destroy()
        return True

    def open_external_url(self, url):
        webbrowser.open(url)
        return True

    def check_for_updates(self):
        """Check for updates."""
        current_version = "v1.0.0"
        return {
            "is_latest": True,
            "current_version": current_version,
            "latest_version": current_version,
            "release_url": "https://github.com/gkrotechs/RiskAutoClicker/releases"
        }
