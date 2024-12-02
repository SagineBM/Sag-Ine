import os
import winshell
from win32com.client import Dispatch

def create_shortcut():
    # Get the path to the executable
    build_dir = os.path.join(os.getcwd(), "build")
    exe_folders = [f for f in os.listdir(build_dir) if f.startswith("exe.")]
    if not exe_folders:
        print("Executable folder not found!")
        return
        
    exe_path = os.path.join(build_dir, exe_folders[0], "Sag Ine.exe")
    if not os.path.exists(exe_path):
        print(f"Executable not found at: {exe_path}")
        return

    # Create shortcut on desktop
    desktop = winshell.desktop()
    path = os.path.join(desktop, "Sag Ine.lnk")
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = exe_path
    shortcut.IconLocation = os.path.join(os.getcwd(), "icons", "sag_ine.ico")
    shortcut.save()
    
    print(f"Shortcut created at: {path}")

if __name__ == "__main__":
    create_shortcut()
