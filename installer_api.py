import os
import sys
import time
import shutil
import subprocess
import winreg

class InstallerApi:
    def __init__(self, window_holder=None):
        self.window_holder = window_holder or {}
        self.default_install_dir = os.path.join(
            os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
            "Programs",
            "RiskAutoClicker"
        )

    def _get_window(self):
        return self.window_holder.get("window")

    def get_defaults(self):
        return {
            "default_path": self.default_install_dir,
            "desktop_shortcut": True,
            "start_menu_shortcut": True,
            "launch_on_finish": True,
            "app_version": "v1.0.0"
        }

    def browse_folder(self):
        win = self._get_window()
        chosen = None
        if win:
            try:
                import webview
                res = win.create_file_dialog(webview.FOLDER_DIALOG)
                if res and len(res) > 0:
                    chosen = res[0]
            except Exception:
                pass
        
        if not chosen:
            try:
                import tkinter as tk
                from tkinter import filedialog
                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                chosen = filedialog.askdirectory(initialdir=self.default_install_dir)
                root.destroy()
            except Exception:
                pass

        if chosen:
            chosen = os.path.normpath(chosen)
            if not chosen.lower().endswith("riskautoclicker"):
                chosen = os.path.join(chosen, "RiskAutoClicker")
            return chosen
        return ""

    def create_shortcut(self, target_exe, shortcut_path, work_dir=""):
        try:
            if not work_dir:
                work_dir = os.path.dirname(target_exe)
            
            shortcut_dir = os.path.dirname(shortcut_path)
            if not os.path.exists(shortcut_dir):
                os.makedirs(shortcut_dir, exist_ok=True)

            ps_cmd = (
                f'$WshShell = New-Object -ComObject WScript.Shell; '
                f'$Shortcut = $WshShell.CreateShortcut("{shortcut_path}"); '
                f'$Shortcut.TargetPath = "{target_exe}"; '
                f'$Shortcut.IconLocation = "{target_exe},0"; '
                f'$Shortcut.WorkingDirectory = "{work_dir}"; '
                f'$Shortcut.Save()'
            )
            
            flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd],
                capture_output=True,
                creationflags=flags,
                check=True
            )
            return True
        except Exception as e:
            print(f"Error creating shortcut {shortcut_path}: {e}")
            return False

    def register_in_windows(self, target_dir, target_exe):
        try:
            # Create uninstaller scripts inside target directory
            uninstaller_ps1 = os.path.join(target_dir, "uninstall.ps1")
            uninstaller_bat = os.path.join(target_dir, "uninstall.bat")

            ps1_content = f'''param([switch]$Quiet)
if (-not $Quiet) {{
    $ans = [System.Windows.Forms.MessageBox]::Show("Are you sure you want to uninstall Risk Auto Clicker?", "Risk Auto Clicker Uninstall", [System.Windows.Forms.MessageBoxButtons]::YesNo, [System.Windows.Forms.MessageBoxIcon]::Question)
    if ($ans -ne [System.Windows.Forms.DialogResult]::Yes) {{ exit }}
}}

# Stop any running process
Get-Process -Name "RiskAutoClicker" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# Remove shortcuts
$desktopLnk = [System.IO.Path]::Combine([System.Environment]::GetFolderPath("Desktop"), "Risk Auto Clicker.lnk")
if (Test-Path $desktopLnk) {{ Remove-Item -Force $desktopLnk -ErrorAction SilentlyContinue }}

$startMenuLnk = [System.IO.Path]::Combine([System.Environment]::GetFolderPath("ApplicationData"), "Microsoft\\Windows\\Start Menu\\Programs\\Risk Auto Clicker.lnk")
if (Test-Path $startMenuLnk) {{ Remove-Item -Force $startMenuLnk -ErrorAction SilentlyContinue }}

# Remove Registry Key
Remove-Item -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\RiskAutoClicker" -Recurse -Force -ErrorAction SilentlyContinue

# Schedule removal of folder
Start-Process cmd.exe -ArgumentList '/c timeout /t 1 & rmdir /s /q "{target_dir}"' -WindowStyle Hidden
if (-not $Quiet) {{
    [System.Windows.Forms.MessageBox]::Show("Risk Auto Clicker has been removed from your PC.", "Uninstalled", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
}}
'''
            with open(uninstaller_ps1, "w", encoding="utf-8") as f:
                f.write(ps1_content)

            bat_content = '@echo off\r\npowershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0uninstall.ps1"\r\n'
            with open(uninstaller_bat, "w", encoding="utf-8") as f:
                f.write(bat_content)

            # Write Windows Uninstall Registry Key
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\RiskAutoClicker"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "Risk Auto Clicker")
                winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "1.0.0")
                winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "gkrotech")
                winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, target_dir)
                winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, f"{target_exe},0")
                winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'"{uninstaller_bat}"')
                winreg.SetValueEx(key, "QuietUninstallString", 0, winreg.REG_SZ, f'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{uninstaller_ps1}" -Quiet')
                winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "EstimatedSize", 0, winreg.REG_DWORD, 45000)
                winreg.SetValueEx(key, "URLInfoAbout", 0, winreg.REG_SZ, "https://github.com/gkrotechs")

            return True
        except Exception as e:
            print(f"Error registering in Windows: {e}")
            return False

    def start_install(self, options):
        target_dir = options.get("target_dir") or self.default_install_dir
        create_desktop = options.get("create_desktop", True)
        create_start_menu = options.get("create_start_menu", True)
        launch_now = options.get("launch_now", True)

        try:
            target_dir = os.path.normpath(target_dir)
            os.makedirs(target_dir, exist_ok=True)

            source_exe = None
            if getattr(sys, 'frozen', False):
                base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
                embedded_exe = os.path.join(base_dir, "RiskAutoClicker.exe")
                if os.path.exists(embedded_exe):
                    source_exe = embedded_exe
            
            if not source_exe:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                parent_dist = os.path.join(os.path.dirname(current_dir), "dist", "RiskAutoClicker.exe")
                local_dist = os.path.join(current_dir, "dist", "RiskAutoClicker.exe")
                if os.path.exists(parent_dist):
                    source_exe = parent_dist
                elif os.path.exists(local_dist):
                    source_exe = local_dist

            target_exe = os.path.join(target_dir, "RiskAutoClicker.exe")

            if source_exe and os.path.exists(source_exe):
                shutil.copy2(source_exe, target_exe)

            # Copy icon asset if present
            base_search = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            for possible_ico in [
                os.path.join(base_search, "app.ico"),
                os.path.join(base_search, "installer_frontend", "assets", "app.ico"),
                os.path.join(os.path.dirname(base_search), "frontend", "assets", "app.ico")
            ]:
                if os.path.exists(possible_ico):
                    try:
                        shutil.copy2(possible_ico, os.path.join(target_dir, "app.ico"))
                        break
                    except Exception:
                        pass

            # Prepare default config folder
            target_config = os.path.join(target_dir, "config")
            os.makedirs(target_config, exist_ok=True)
            
            # Create shortcuts with explicit icon binding
            if create_desktop:
                desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
                desktop_shortcut = os.path.join(desktop_dir, "Risk Auto Clicker.lnk")
                self.create_shortcut(target_exe, desktop_shortcut, target_dir)

            if create_start_menu:
                appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
                start_menu_dir = os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs")
                start_shortcut = os.path.join(start_menu_dir, "Risk Auto Clicker.lnk")
                self.create_shortcut(target_exe, start_shortcut, target_dir)

            # Register in Windows Add/Remove Programs
            self.register_in_windows(target_dir, target_exe)

            # Refresh Windows Shell
            try:
                import ctypes
                ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)
            except Exception:
                pass

            time.sleep(0.5)

            if launch_now and os.path.exists(target_exe):
                subprocess.Popen([target_exe], cwd=target_dir, close_fds=True)
                time.sleep(0.3)
                self.close_window()

            return {
                "success": True,
                "target_dir": target_dir,
                "target_exe": target_exe
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def launch_app(self, target_dir=None):
        if not target_dir:
            target_dir = self.default_install_dir
        target_exe = os.path.join(target_dir, "RiskAutoClicker.exe")
        if os.path.exists(target_exe):
            subprocess.Popen([target_exe], cwd=target_dir, close_fds=True)
            self.close_window()
            return True
        return False

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
