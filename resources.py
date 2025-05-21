"""
Resource management for GemType.
This module handles all application resources like icons and images.
"""
from PyQt5.QtCore import QDir, QFile
from PyQt5.QtGui import QIcon, QPixmap
import os
import sys

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

class Icons:
    """Static class to hold application icons."""
    
    # Icon paths
    _icon_paths = {
        'app_icon': 'assets/icons/app_icon.png',
        'tray_icon': 'assets/icons/tray_icon.png',
        'settings': 'assets/icons/settings.png',
        'exit': 'assets/icons/exit.png',
        'status_active': 'assets/icons/status_active.png',
        'status_inactive': 'assets/icons/status_inactive.png',
    }
    
    # Cache for loaded icons
    _icons = {}
    
    @classmethod
    def get_icon(cls, icon_name):
        """Get an icon by name."""
        if icon_name not in cls._icons:
            if icon_name in cls._icon_paths:
                icon_path = resource_path(cls._icon_paths[icon_name])
                if os.path.exists(icon_path):
                    cls._icons[icon_name] = QIcon(icon_path)
                else:
                    # Return a default icon if the file doesn't exist
                    print(f"Icon not found: {icon_path}")
                    return QIcon()
            else:
                raise ValueError(f"Unknown icon name: {icon_name}")
        
        return cls._icons[icon_name]
    
    @classmethod
    def get_pixmap(cls, icon_name, size=32):
        """Get a pixmap by name and size."""
        icon = cls.get_icon(icon_name)
        if not icon.isNull():
            return icon.pixmap(size, size)
        return QPixmap(size, size)
