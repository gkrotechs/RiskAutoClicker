import json
import os

DEFAULT_PRESETS = [
    {
        "id": "minecraft_pvp",
        "name": "Minecraft PvP",
        "desc": "16 CPS • 25% Randomization",
        "cps": 16.0,
        "rate_unit": "Second",
        "rate_mode": "Rate",
        "input_type": "Mouse",
        "mouse_button": "LEFT",
        "duty_cycle": 42.0,
        "speed_randomization": 25.0,
        "hotkey": "Ctrl+Y",
        "trigger_mode": "Toggle"
    },
    {
        "id": "jitter_human",
        "name": "Jitter Click",
        "desc": "14.5 CPS • 45% Randomization",
        "cps": 14.5,
        "rate_unit": "Second",
        "rate_mode": "Rate",
        "input_type": "Mouse",
        "mouse_button": "LEFT",
        "duty_cycle": 50.0,
        "speed_randomization": 45.0,
        "hotkey": "Ctrl+Y",
        "trigger_mode": "Toggle"
    },
    {
        "id": "roblox_auto",
        "name": "Auto Clicker for Roblox",
        "desc": "40 CPS • 15% Randomization",
        "cps": 40.0,
        "rate_unit": "Second",
        "rate_mode": "Rate",
        "input_type": "Mouse",
        "mouse_button": "LEFT",
        "duty_cycle": 45.0,
        "speed_randomization": 15.0,
        "hotkey": "Ctrl+Y",
        "trigger_mode": "Toggle"
    },
    {
        "id": "cookie_clicker",
        "name": "Cookie Clicker",
        "desc": "100 CPS • 35% Randomization",
        "cps": 100.0,
        "rate_unit": "Second",
        "rate_mode": "Rate",
        "input_type": "Mouse",
        "mouse_button": "LEFT",
        "duty_cycle": 45.0,
        "speed_randomization": 35.0,
        "hotkey": "Ctrl+Y",
        "trigger_mode": "Toggle"
    },
    {
        "id": "fastest",
        "name": "Fastest",
        "desc": "500 CPS • Constant",
        "cps": 500.0,
        "rate_unit": "Second",
        "rate_mode": "Rate",
        "input_type": "Mouse",
        "mouse_button": "LEFT",
        "duty_cycle": 50.0,
        "speed_randomization": 0.0,
        "hotkey": "Ctrl+Y",
        "trigger_mode": "Toggle"
    }
]

class PresetManager:
    def __init__(self, config_dir="config"):
        self.config_dir = config_dir
        self.presets_file = os.path.join(config_dir, "presets.json")
        self.presets = []
        self.active_preset_name = None
        self._ensure_dir()
        self.load()

    def _ensure_dir(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir, exist_ok=True)

    def load(self):
        self.presets = list(DEFAULT_PRESETS)
        if os.path.exists(self.presets_file):
            try:
                with open(self.presets_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Keep custom user presets and refresh default ones
                    custom_presets = [p for p in loaded if p.get("id", "").startswith("custom_")]
                    self.presets.extend(custom_presets)
            except Exception as e:
                print(f"Error loading presets: {e}")
        self.save()

    def save(self):
        self._ensure_dir()
        try:
            with open(self.presets_file, 'w', encoding='utf-8') as f:
                json.dump(self.presets, f, indent=2)
        except Exception as e:
            print(f"Error saving presets: {e}")

    def get_presets(self):
        return self.presets

    def add_preset(self, preset_data):
        # Generate simple ID if missing
        if "id" not in preset_data or not preset_data["id"]:
            preset_data["id"] = "custom_" + str(len(self.presets) + 1)
        # Update if exists, else append
        for i, p in enumerate(self.presets):
            if p.get("id") == preset_data["id"] or p.get("name") == preset_data.get("name"):
                self.presets[i] = preset_data
                self.save()
                return preset_data
        self.presets.append(preset_data)
        self.save()
        return preset_data

    def delete_preset(self, preset_id):
        self.presets = [p for p in self.presets if p.get("id") != preset_id]
        self.save()
        return True
