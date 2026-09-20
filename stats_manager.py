import json
import os
import time
import psutil

class StatsManager:
    def __init__(self, config_dir="config"):
        self.config_dir = config_dir
        self.stats_file = os.path.join(config_dir, "stats.json")
        self.total_clicks = 0
        self.total_duration_sec = 0.0
        self.total_sessions = 0
        self.session_start_time = None
        self.session_click_count = 0
        
        self._ensure_dir()
        self.load()

    def _ensure_dir(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir, exist_ok=True)

    def load(self):
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.total_clicks = data.get("total_clicks", 0)
                    self.total_duration_sec = data.get("total_duration_sec", 0.0)
                    self.total_sessions = data.get("total_sessions", 0)
            except Exception as e:
                print(f"Error loading stats: {e}")

    def save(self):
        self._ensure_dir()
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "total_clicks": self.total_clicks,
                    "total_duration_sec": self.total_duration_sec,
                    "total_sessions": self.total_sessions
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving stats: {e}")

    def on_session_start(self):
        self.session_start_time = time.time()
        self.session_click_count = 0
        self.total_sessions += 1
        self.save()

    def on_session_end(self, clicks_in_session: int):
        if self.session_start_time:
            duration = time.time() - self.session_start_time
            self.total_duration_sec += duration
            self.session_start_time = None
        self.total_clicks += clicks_in_session
        self.save()

    def record_click(self, count: int = 1):
        self.total_clicks += count

    def reset_stats(self):
        self.total_clicks = 0
        self.total_duration_sec = 0.0
        self.total_sessions = 0
        self.save()

    def get_cpu_usage(self) -> float:
        try:
            return round(psutil.cpu_percent(interval=None), 1)
        except Exception:
            return 1.2

    def format_duration(self, seconds: float) -> str:
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"

    def get_stats_dict(self):
        # Calculate live session duration if currently running
        cur_duration = self.total_duration_sec
        if self.session_start_time:
            cur_duration += (time.time() - self.session_start_time)
            
        return {
            "total_clicks": f"{self.total_clicks:,}",
            "raw_total_clicks": self.total_clicks,
            "total_duration": self.format_duration(cur_duration),
            "raw_total_duration": cur_duration,
            "cpu_usage": f"{self.get_cpu_usage()}%",
            "total_sessions": self.total_sessions
        }
