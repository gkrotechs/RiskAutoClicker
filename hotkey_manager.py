import keyboard
import threading
import time

class HotkeyManager:
    def __init__(self, on_trigger=None, on_panic=None):
        self.on_trigger = on_trigger
        self.on_panic = on_panic
        self.current_hotkey = "Ctrl+Y"
        self.panic_hotkey = "F8"
        self.trigger_mode = "Toggle" # Toggle or Hold
        self.is_recording = False
        self._hotkey_hook = None
        self._panic_hook = None
        self._key_down_active = False

    def register_hotkey(self, hotkey_str: str, trigger_mode: str = "Toggle"):
        self.current_hotkey = hotkey_str
        self.trigger_mode = trigger_mode
        self._rebind()

    def register_panic_hotkey(self, panic_str: str):
        self.panic_hotkey = panic_str
        self._rebind()

    def _rebind(self):
        try:
            keyboard.unhook_all()
        except Exception:
            pass

        try:
            # Clean hotkey format e.g. "ctrl+y"
            hk = self.current_hotkey.strip().lower().replace(" ", "")
            if hk:
                if self.trigger_mode == "Toggle":
                    keyboard.add_hotkey(hk, self._handle_toggle, suppress=False)
                else:
                    # Hold mode: start on press, stop on release
                    # Parse base key
                    keyboard.on_press_key(hk, self._handle_press, suppress=False)
                    keyboard.on_release_key(hk, self._handle_release, suppress=False)
        except Exception as e:
            print(f"Error binding main hotkey {self.current_hotkey}: {e}")

        try:
            # Bind panic hotkey (always stops clicker)
            panic = self.panic_hotkey.strip().lower().replace(" ", "")
            if panic:
                keyboard.add_hotkey(panic, self._handle_panic, suppress=False)
        except Exception as e:
            print(f"Error binding panic hotkey {self.panic_hotkey}: {e}")

    def _handle_toggle(self):
        if self.on_trigger and not self.is_recording:
            self.on_trigger("toggle")

    def _handle_press(self, e):
        if self.on_trigger and not self.is_recording and not self._key_down_active:
            self._key_down_active = True
            self.on_trigger("start")

    def _handle_release(self, e):
        if self.on_trigger and not self.is_recording and self._key_down_active:
            self._key_down_active = False
            self.on_trigger("stop")

    def _handle_panic(self):
        if self.on_panic:
            self.on_panic()

    def record_next_hotkey(self, timeout=5.0) -> str:
        """Blocks and records the next key combination pressed."""
        self.is_recording = True
        try:
            combo = keyboard.read_hotkey(suppress=False)
            self.is_recording = False
            # Format nicely, e.g., "Ctrl + Y" or "F6"
            parts = combo.split('+')
            formatted = " + ".join([p.capitalize() for p in parts])
            self._rebind()
            return formatted
        except Exception as e:
            self.is_recording = False
            self._rebind()
            return self.current_hotkey

    def cleanup(self):
        try:
            keyboard.unhook_all()
        except Exception:
            pass
