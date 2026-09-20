import json
import os

DEFAULT_CONFIG = {
    "version": "v1.0.0",
    "theme": "light", # "light", "dark", "blue"
    "accent_color": "#18181b",
    "window_opacity": 0.96,
    "blur_effect": True,
    "always_on_top": False,
    "show_notifications": True,
    "auto_start": False,
    "hotkey": "Ctrl + Y",
    "trigger_mode": "Toggle",
    "panic_hotkey": "F8",
    "stop_on_mouse_move": False,
    "click_limit_enabled": False,
    "click_limit": 1000,
    "active_preset": "default"
}

class ConfigManager:
    def __init__(self, config_dir="config"):
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "settings.json")
        self.config = dict(DEFAULT_CONFIG)
        self._ensure_dir()
        self.load()

    def _ensure_dir(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir, exist_ok=True)

    def load(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.config.update(loaded)
                    self.config["version"] = "v1.0.0"
                    self.save()
                    return
            except Exception as e:
                print(f"Error loading config: {e}")
        self.save()

    def save(self):
        self._ensure_dir()
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save()

    def get_all(self):
        return self.config

    def reset(self):
        self.config = dict(DEFAULT_CONFIG)
        self.save()
        return self.config
