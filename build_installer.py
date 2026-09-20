import os
import subprocess
import sys

def build_setup():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(root_dir, "app.ico")
    dist_exe = os.path.join(root_dir, "dist", "RiskAutoClicker.exe")

    print("Building RiskAutoClicker.exe with icon...")
    app_cmd = [
        "pyinstaller",
        "--noconsole",
        "--onefile",
        f"--icon={icon_path}",
        "--add-data", "frontend;frontend",
        "--add-data", f"{icon_path};.",
        "--name", "RiskAutoClicker",
        "--clean",
        "-y",
        "main.py"
    ]
    subprocess.run(app_cmd, check=True)

    print("Building RiskAutoClicker_Setup.exe with icon...")
    setup_cmd = [
        "pyinstaller",
        "--noconsole",
        "--onefile",
        f"--icon={icon_path}",
        "--add-data", f"{os.path.join('installer', 'installer_frontend')};installer_frontend",
        "--add-data", f"{os.path.join('dist', 'RiskAutoClicker.exe')};.",
        "--add-data", f"{icon_path};.",
        "--name", "RiskAutoClicker_Setup",
        "--clean",
        "-y",
        os.path.join("installer", "installer_main.py")
    ]
    subprocess.run(setup_cmd, check=True)

    # Refresh Windows Explorer Icon Cache
    try:
        import ctypes
        ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None) # SHCNE_ASSOCCHANGED
    except Exception:
        pass

    print("Setup installer built successfully: dist/RiskAutoClicker_Setup.exe")

if __name__ == "__main__":
    build_setup()
