import ctypes
from ctypes import wintypes
import psutil

user32 = ctypes.WinDLL('user32', use_last_error=True)

class ProcessManager:
    @staticmethod
    def get_window_processes():
        """Enumerate top-level visible windows with non-empty titles."""
        windows = []
        
        def enum_windows_proc(hwnd, lParam):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buff, length + 1)
                    title = buff.value
                    
                    pid = wintypes.DWORD()
                    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                    
                    try:
                        proc = psutil.Process(pid.value)
                        proc_name = proc.name()
                        
                        # Filter out common shell/invisible helper windows
                        if title and proc_name and title not in ["Program Manager", "Default IME", "MSCTFIME UI"]:
                            windows.append({
                                "hwnd": hwnd,
                                "pid": pid.value,
                                "name": proc_name,
                                "title": title
                            })
                    except Exception:
                        pass
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows(WNDENUMPROC(enum_windows_proc), 0)
        
        # Deduplicate and sort by title
        seen = set()
        unique_windows = []
        for w in windows:
            key = (w["name"], w["title"])
            if key not in seen:
                seen.add(key)
                unique_windows.append(w)
                
        return unique_windows
