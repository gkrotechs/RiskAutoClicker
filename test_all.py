import unittest
import time
import os
import shutil
from backend.clicker_engine import ClickerEngine
from backend.stats_manager import StatsManager
from backend.preset_manager import PresetManager
from backend.config_manager import ConfigManager
from backend.hotkey_manager import HotkeyManager
from backend.process_manager import ProcessManager

class TestPrismAutoClicker(unittest.TestCase):
    def setUp(self):
        self.test_config_dir = "tests_tmp_config"
        if os.path.exists(self.test_config_dir):
            shutil.rmtree(self.test_config_dir, ignore_errors=True)

    def tearDown(self):
        if os.path.exists(self.test_config_dir):
            shutil.rmtree(self.test_config_dir, ignore_errors=True)

    def test_engine_interval_calculation(self):
        engine = ClickerEngine()
        engine.cps = 100
        engine.rate_unit = "Second"
        engine.rate_mode = "Rate"
        interval = engine.get_actual_interval()
        self.assertAlmostEqual(interval, 0.01, places=4)

        engine.rate_unit = "Minute"
        engine.cps = 60
        interval_min = engine.get_actual_interval()
        self.assertAlmostEqual(interval_min, 1.0, places=4)

        engine.rate_mode = "Interval"
        engine.cps = 50 # 50 ms
        interval_ms = engine.get_actual_interval()
        self.assertAlmostEqual(interval_ms, 0.05, places=4)
        engine.cleanup()

    def test_stats_manager(self):
        stats = StatsManager(config_dir=self.test_config_dir)
        self.assertEqual(stats.total_clicks, 0)
        self.assertEqual(stats.total_sessions, 0)
        
        stats.on_session_start()
        self.assertEqual(stats.total_sessions, 1)
        time.sleep(0.05)
        stats.on_session_end(clicks_in_session=50)
        
        self.assertEqual(stats.total_clicks, 50)
        self.assertGreater(stats.total_duration_sec, 0.04)
        
        formatted = stats.format_duration(145)
        self.assertEqual(formatted, "2m 25s")

    def test_presets_manager(self):
        presets_mgr = PresetManager(config_dir=self.test_config_dir)
        presets = presets_mgr.get_presets()
        self.assertGreaterEqual(len(presets), 4)

        # Test adding custom preset
        custom = {
            "id": "custom_test",
            "name": "Custom Test 120 CPS",
            "cps": 120,
            "rate_unit": "Second",
            "duty_cycle": 45,
            "speed_randomization": 10
        }
        presets_mgr.add_preset(custom)
        found = any(p["id"] == "custom_test" for p in presets_mgr.get_presets())
        self.assertTrue(found)

        # Delete preset
        presets_mgr.delete_preset("custom_test")
        found_after = any(p["id"] == "custom_test" for p in presets_mgr.get_presets())
        self.assertFalse(found_after)

    def test_config_manager(self):
        cfg = ConfigManager(config_dir=self.test_config_dir)
        self.assertEqual(cfg.get("version"), "v1.0.0")
        cfg.set("accent_color", "#ff0000")
        self.assertEqual(cfg.get("accent_color"), "#ff0000")

    def test_process_manager(self):
        windows = ProcessManager.get_window_processes()
        self.assertIsInstance(windows, list)

if __name__ == "__main__":
    unittest.main()
