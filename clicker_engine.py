import ctypes
from ctypes import wintypes
import time
import threading
import random
import psutil

# Setup high-resolution multimedia timer in Windows (1ms resolution instead of default 15.6ms)
try:
    winmm = ctypes.WinDLL('winmm')
    winmm.timeBeginPeriod(1)
except Exception:
    pass

user32 = ctypes.WinDLL('user32', use_last_error=True)

# Low-level SendInput structures
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_ABSOLUTE = 0x8000

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_SCANCODE = 0x0008

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    )

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    )

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    )

class _INPUT_UNION(ctypes.Union):
    _fields_ = (
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    )

class INPUT(ctypes.Structure):
    _fields_ = (
        ("type", wintypes.DWORD),
        ("union", _INPUT_UNION),
    )

def send_mouse_event(flags: int, dx: int = 0, dy: int = 0, mouse_data: int = 0):
    """Sends low-level mouse event using SendInput."""
    inp = INPUT()
    inp.type = INPUT_MOUSE
    inp.union.mi.dx = dx
    inp.union.mi.dy = dy
    inp.union.mi.mouseData = mouse_data
    inp.union.mi.dwFlags = flags
    inp.union.mi.time = 0
    inp.union.mi.dwExtraInfo = 0
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

def send_key_event(vk_code: int, is_up: bool = False):
    """Sends low-level keyboard event using SendInput."""
    flags = KEYEVENTF_KEYUP if is_up else 0
    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    inp.union.ki.wVk = vk_code
    inp.union.ki.wScan = 0
    inp.union.ki.dwFlags = flags
    inp.union.ki.time = 0
    inp.union.ki.dwExtraInfo = 0
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

class ClickerEngine:
    def __init__(self):
        self.is_running = False
        self._thread = None
        self._stop_event = threading.Event()
        
        # Configuration
        self.cps = 100.0  # Clicks per second
        self.rate_unit = "Second"  # Second, Millisecond, Minute, Hour
        self.rate_mode = "Rate"    # Rate (CPS) vs Interval (ms)
        self.input_type = "Mouse"  # Mouse vs Keyboard
        self.mouse_button = "LEFT" # LEFT, MIDDLE, RIGHT
        self.click_type = "Single" # Single, Double, Hold, Triple
        self.duty_cycle = 45.0     # Percentage of period holding the button down (e.g. 45%)
        self.speed_randomization = 35.0  # Randomization percentage (0-100%)
        self.key_to_press = 0x20  # Virtual key code (default Space: 0x20)
        
        # Target location
        self.location_mode = "Cursor" # Cursor or Fixed
        self.target_x = 0
        self.target_y = 0
        
        # Process targeting
        self.target_process_name = None  # None = any, or "javaw.exe", etc.
        self.only_when_focused = False
        
        # Callbacks & Statistics
        self.on_click_callback = None
        self.on_state_change = None
        self.total_clicks_session = 0
        self.start_time = None
        self.total_run_duration = 0.0

    def get_actual_interval(self) -> float:
        """Calculate the target period between clicks in seconds."""
        if self.rate_mode == "Interval":
            # self.cps stores interval in milliseconds in this mode
            base_interval = max(0.0005, self.cps / 1000.0)
        else:
            # Rate mode: clicks per unit
            if self.rate_unit == "Millisecond":
                clicks_per_sec = self.cps * 1000.0
            elif self.rate_unit == "Minute":
                clicks_per_sec = self.cps / 60.0
            elif self.rate_unit == "Hour":
                clicks_per_sec = self.cps / 3600.0
            else: # Second
                clicks_per_sec = self.cps
            
            clicks_per_sec = max(0.01, clicks_per_sec)
            base_interval = 1.0 / clicks_per_sec
            
        return base_interval

    def _should_click_process(self) -> bool:
        """Check if target process conditions are met."""
        if not self.target_process_name or not self.only_when_focused:
            return True
        try:
            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return False
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            proc = psutil.Process(pid.value)
            return proc.name().lower() == self.target_process_name.lower()
        except Exception:
            return True

    def _click_down(self):
        if self.input_type == "Mouse":
            if self.mouse_button == "LEFT":
                send_mouse_event(MOUSEEVENTF_LEFTDOWN)
            elif self.mouse_button == "RIGHT":
                send_mouse_event(MOUSEEVENTF_RIGHTDOWN)
            elif self.mouse_button == "MIDDLE":
                send_mouse_event(MOUSEEVENTF_MIDDLEDOWN)
        else:
            send_key_event(self.key_to_press, is_up=False)

    def _click_up(self):
        if self.input_type == "Mouse":
            if self.mouse_button == "LEFT":
                send_mouse_event(MOUSEEVENTF_LEFTUP)
            elif self.mouse_button == "RIGHT":
                send_mouse_event(MOUSEEVENTF_RIGHTUP)
            elif self.mouse_button == "MIDDLE":
                send_mouse_event(MOUSEEVENTF_MIDDLEUP)
        else:
            send_key_event(self.key_to_press, is_up=True)

    def _execute_click_cycle(self, down_duration: float, up_duration: float):
        """Execute a down-up cycle with precise sleep / busy-wait."""
        if self.location_mode == "Fixed":
            user32.SetCursorPos(int(self.target_x), int(self.target_y))
            
        self._click_down()
        self._precise_sleep(down_duration)
        self._click_up()
        
        self.total_clicks_session += 1
        if self.on_click_callback:
            try:
                self.on_click_callback(self.total_clicks_session)
            except Exception:
                pass
                
        self._precise_sleep(up_duration)

    def _precise_sleep(self, seconds: float):
        """High-resolution hybrid sleep using time.perf_counter()."""
        if seconds <= 0:
            return
        deadline = time.perf_counter() + seconds
        if seconds > 0.002:
            time.sleep(seconds - 0.0015)
        while time.perf_counter() < deadline:
            if self._stop_event.is_set():
                break

    def _run_loop(self):
        while not self._stop_event.is_set():
            if not self._should_click_process():
                time.sleep(0.05)
                continue
                
            base_interval = self.get_actual_interval()
            
            if self.speed_randomization > 0:
                jitter_factor = (self.speed_randomization / 100.0)
                variation = random.gauss(0, jitter_factor * 0.35)
                interval = base_interval * (1.0 + variation)
                interval = max(0.0005, interval)
            else:
                interval = base_interval
                
            duty = max(5.0, min(95.0, self.duty_cycle)) / 100.0
            down_duration = interval * duty
            up_duration = interval * (1.0 - duty)
            
            down_duration = max(0.0002, down_duration)
            up_duration = max(0.0002, up_duration)
            
            self._execute_click_cycle(down_duration, up_duration)

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self._stop_event.clear()
        self.start_time = time.time()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        if self.on_state_change:
            self.on_state_change(True)

    def stop(self):
        if not self.is_running:
            return
        self.is_running = False
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=0.5)
            self._thread = None
        self._click_up()
        if self.start_time:
            self.total_run_duration += (time.time() - self.start_time)
            self.start_time = None
        if self.on_state_change:
            self.on_state_change(False)

    def toggle(self):
        if self.is_running:
            self.stop()
        else:
            self.start()
        return self.is_running

    def cleanup(self):
        self.stop()
        try:
            winmm.timeEndPeriod(1)
        except Exception:
            pass
