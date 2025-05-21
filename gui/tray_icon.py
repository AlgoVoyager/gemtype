"""
System tray icon for GemType.
"""
import logging
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QPixmap
import os
# Configure logging
logger = logging.getLogger(__name__)

class TrayIcon(QSystemTrayIcon):
    """System tray icon with menu for GemType."""
    
    # Signals
    show_main_window_signal = pyqtSignal()
    quit_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the tray icon."""
        # Create a default icon if needed
        try:
            icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icons', 'tray_icon.png')
            if os.path.exists(icon_path):
                icon = QIcon(icon_path)
            else:
                raise FileNotFoundError
        except:
            # Create a simple icon as fallback
            pixmap = QPixmap(64, 64)
            pixmap.fill("#4285f4")
            icon = QIcon(pixmap)
        
        super().__init__(icon, parent)
        
        # Set up the tray icon
        self.setToolTip("GemType - AI Assistant")
        
        # Create the menu
        self.menu = QMenu()
        
        # Create actions
        self.show_action = QAction("Show", self)
        self.show_action.triggered.connect(self.show_main_window_signal.emit)
        
        self.settings_action = QAction("Settings", self)
        self.settings_action.triggered.connect(self.show_settings)
        
        self.quit_action = QAction("Quit", self)
        self.quit_action.triggered.connect(self.quit_application)
        
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
    
    def on_tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_main_window_signal.emit()
    
    def show_settings(self):
        """Show the settings dialog."""
        # This will be connected to the main window's settings dialog
        self.show_main_window_signal.emit()
        # The main window will handle showing the settings dialog
    
    def quit_application(self):
        """Quit the application."""
        logger.info("Quit requested from tray icon")
        self.quit_signal.emit()
