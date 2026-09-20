import os
import sys
import webview
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("gkrotech.riskautoclicker.setup.1.0")
except Exception:
    pass

from installer_api import InstallerApi

def main():
    if getattr(sys, 'frozen', False):
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    frontend_dir = os.path.join(base_dir, "installer_frontend")
    html_path = os.path.join(frontend_dir, "index.html")

    window_holder = {}
    api = InstallerApi(window_holder)

    window = webview.create_window(
        title="Risk Auto Clicker Setup",
        url=f"file:///{html_path.replace(os.sep, '/')}",
        js_api=api,
        width=560,
        height=410,
        resizable=False,
        frameless=True,
        easy_drag=False,
        background_color="#ffffff"
    )

    window_holder["window"] = window
    webview.start(debug=False, gui='edgechromium')

if __name__ == "__main__":
    main()
