#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

def main():
    # Hide console window if not running in debug mode
    if getattr(sys, 'frozen', False):  # Running as compiled
        import ctypes
        kernel32 = ctypes.WinDLL('kernel32')
        hwnd = kernel32.GetConsoleWindow()
        if hwnd != 0:
            user32 = ctypes.WinDLL('user32')
            user32.ShowWindow(hwnd, 0)  # Hide console window
    
    from gui.main_window import MainWindow
    from PyQt5.QtWidgets import QApplication
    
    # Set application attributes
    app = QApplication(sys.argv)
    app.setApplicationName("GemType")
    app.setApplicationDisplayName("GemType - AI Assistant")
    app.setQuitOnLastWindowClosed(False)  # Keep running in system tray
    
    # Create and show main window
    window = MainWindow()
    
    # Start the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
