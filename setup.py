from cx_Freeze import setup, Executable
import sys

build_exe_options = {
    "packages": [
        "customtkinter", 
        "tkinter",
        "requests",
        "bs4",
        "PIL",
        "json",
        "threading",
        "webbrowser",
        "docx",
        "pandas",
        "PyPDF2",
        "openai",
        "google.generativeai",
        "httplib2",
        "socks",
        "win32gui",
        "google.api_core",
        "google.auth",
    ],
    "includes": ["_socket"],
    "include_files": [
        "icons/",
        "sag_ine_config.json"
    ]
}

base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name="Sag Ine",
    version="1.0",
    description="AI Assistant with Multiple Providers",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "ai_assistant_gui.py",
            base=base,
            icon="icons/sag_ine.ico",
            target_name="Sag Ine.exe"
        )
    ]
)
