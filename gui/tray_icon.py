"""
System tray icon for GemType.
"""
import os
import sys
import logging
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import pyqtSignal, QObject, Qt
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QFont

logger = logging.getLogger(__name__)

class TrayIcon(QSystemTrayIcon):
    """System tray icon for the application."""
    
    show_main_window_signal = pyqtSignal()
    quit_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the tray icon."""
        super().__init__()
        
        # Initialize icon paths
        self.icon_paths = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icons', 'app_icon.ico'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icons', 'tray_icon.jpg'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icons', 'app_icon.png')
        ]
        
        # Add path for PyInstaller bundle
        if getattr(sys, '_MEIPASS', None):
            base_path = sys._MEIPASS
            self.icon_paths.extend([
                os.path.join(base_path, 'assets', 'icons', 'app_icon.ico'),
                os.path.join(base_path, 'assets', 'icons', 'tray_icon.jpg'),
                os.path.join(base_path, 'assets', 'icons', 'app_icon.png')
            ])
        
        # Try to load icon from available paths
        icon = self._load_icon()
        
        # Initialize system tray
        self.setIcon(icon)
        self.setToolTip("GemType - AI Assistant")
        
        # Create the menu
        self.menu = QMenu()
        
        # Add actions
        self.show_action = QAction("Show", self)
        self.show_action.triggered.connect(self.show_main_window_signal.emit)
        
        self.settings_action = QAction("Settings", self)
        self.settings_action.triggered.connect(self.show_settings)
        
        self.quit_action = QAction("Quit", self)
        self.quit_action.triggered.connect(self.quit_signal.emit)
        
        # Add actions to menu
        self.menu.addAction(self.show_action)
        self.menu.addSeparator()
        self.menu.addAction(self.settings_action)
        self.menu.addSeparator()
        self.menu.addAction(self.quit_action)
        
        # Set the context menu
        self.setContextMenu(self.menu)
        
        # Connect signals
        self.activated.connect(self.on_tray_activated)
        
        logger.info("Tray icon initialized")
    
    def _load_icon(self):
        """Try to load icon from available paths."""
        for icon_path in self.icon_paths:
            if os.path.exists(icon_path):
                try:
                    return QIcon(icon_path)
                except Exception as e:
                    logger.warning(f"Failed to load icon from {icon_path}: {e}")
        
        # If no icon found, create a default one
        logger.warning("No valid icon found, using fallback")
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.white)  # Fill with white background
        
        # Draw a simple icon
        painter = QPainter(pixmap)
        painter.setPen(Qt.blue)
        painter.setFont(QFont('Arial', 30))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "G")
        painter.end()
        
        return QIcon(pixmap)
    
    def on_tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_main_window_signal.emit()
    
    def show_settings(self):
        """Show settings dialog."""
        # This will be handled by the main window
        pass
    
    def quit_application(self):
        """Quit the application."""
        logger.info("Quit requested from tray icon")
        self.quit_signal.emit()
