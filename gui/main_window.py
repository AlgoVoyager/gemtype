"""
Main application window for GemType.
"""
import logging
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QSystemTrayIcon,
    QMenu, QAction, QMessageBox, QTabWidget, QStatusBar, QHBoxLayout, QApplication
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QPalette, QColor

from core.config import config
from core.hotkey import HotkeyManager
from .tray_icon import TrayIcon
from .settings_dialog import SettingsDialog

# Configure logging
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main application window for GemType."""
    
    # Signal emitted when the window is closed (but app may still run in tray)
    window_closed = pyqtSignal()
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        # Initialize components
        self.tray_icon = None
        self.hotkey_manager = None
        self.settings_dialog = None
        
        # Set up the UI
        self._init_ui()
        
        # Set up the system tray
        self._init_tray_icon()
        
        # Set up hotkey manager
        self._init_hotkey_manager()
        
        # Show a welcome message
        self.show_welcome_message()
    
    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("GemType - AI Assistant")
        self.setMinimumSize(600, 400)
        
        # Set application icon
        try:
            # Try to load icon from resources
            self.setWindowIcon(QIcon(":/icons/app_icon.png"))
        except:
            # Fallback to system theme icon
            self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        # App icon and title
        icon_label = QLabel()
        try:
            pixmap = QPixmap(":/icons/app_icon.png").scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        except:
            pass
            
        title_label = QLabel("GemType")
        title_font = title_label.font()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Create tabs
        self.tabs = QTabWidget()
        
        # Home tab
        home_tab = QWidget()
        home_layout = QVBoxLayout(home_tab)
        
        # Status section
        status_group = QWidget()
        status_layout = QVBoxLayout(status_group)
        
        self.status_icon = QLabel()
        self.status_icon.setAlignment(Qt.AlignCenter)
        self.status_label = QLabel("Status: Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        status_layout.addWidget(self.status_icon)
        status_layout.addWidget(self.status_label)
        
        # Quick actions
        actions_group = QWidget()
        actions_layout = QVBoxLayout(actions_group)
        
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.clicked.connect(self.show_settings)
        
        self.quick_action_btn = QPushButton("Quick Action")
        self.quick_action_btn.clicked.connect(self.perform_quick_action)
        
        actions_layout.addWidget(self.settings_btn)
        actions_layout.addWidget(self.quick_action_btn)
        actions_layout.addStretch()
        
        # Add widgets to home layout
        home_layout.addWidget(status_group)
        home_layout.addWidget(actions_group)
        home_layout.addStretch()
        
        # Add tabs
        self.tabs.addTab(home_tab, "Home")
        
        # Add tabs to main layout
        layout.addLayout(header_layout)
        layout.addWidget(self.tabs)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Apply styles
        self._apply_styles()
    
    def _init_tray_icon(self):
        """Initialize the system tray icon."""
        self.tray_icon = TrayIcon(self)
        self.tray_icon.show()
        self.tray_icon.show_main_window_signal.connect(self.show_normal)
        self.tray_icon.quit_signal.connect(self.quit_application)
    
    def _init_hotkey_manager(self):
        """Initialize the hotkey manager."""
        self.hotkey_manager = HotkeyManager(config.get("hotkey", "ctrl+alt+space"))
        self.hotkey_manager.hotkey_triggered.connect(self.on_hotkey_triggered)
        self.hotkey_manager.start()
    
    def _apply_styles(self):
        """Apply custom styles to the application."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
            QPushButton:pressed {
                background-color: #2a56c6;
            }
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background: white;
                margin-top: 10px;
            }
            QTabBar::tab {
                background: #e0e0e0;
                border: 1px solid #ccc;
                padding: 8px 16px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 2px solid #4285f4;
            }
        """)
    
    def show_welcome_message(self):
        """Show a welcome message on first run."""
        if config.get("first_run", True):
            QMessageBox.information(
                self,
                "Welcome to GemType",
                "GemType is running in your system tray.\n\n"
                "• Use the system tray icon to access the app\n"
                "• Press Ctrl+Alt+Space to trigger the AI assistant\n"
                "• Right-click the tray icon to access settings"
            )
            config.set("first_run", False)
    
    def show_settings(self):
        """Show the settings dialog."""
        if not self.settings_dialog:
            self.settings_dialog = SettingsDialog(self)
            self.settings_dialog.settings_saved.connect(self.on_settings_saved)
        
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()
    
    def on_settings_saved(self):
        """Handle settings saved event."""
        # Update hotkey if changed
        if self.hotkey_manager:
            self.hotkey_manager.set_hotkey(config.get("hotkey", "ctrl+alt+space"))
        
        # Update status
        self.statusBar().showMessage("Settings saved", 3000)
    
    def on_hotkey_triggered(self):
        """Handle hotkey press event."""
        try:
            logger.info("Hotkey triggered, processing...")
            
            # Get selected text (if any)
            import pyperclip
            original_clipboard = pyperclip.paste()
            
            try:
                # Simulate Ctrl+C to copy selected text
                pyperclip.copy('')  # Clear clipboard first
                import pyautogui
                pyautogui.hotkey('ctrl', 'c')
                
                # Small delay to ensure clipboard is updated
                import time
                time.sleep(0.2)
                
                # Get the selected text
                prompt_text = pyperclip.paste().strip()
                logger.info(f"Selected text: {prompt_text[:100]}...")  # Log first 100 chars
                
                if not prompt_text:
                    logger.info("No text selected, will use empty prompt")
                
                # Generate response
                from core.gemini import GeminiClient
                client = GeminiClient(config.get("api_key"), config.get("model"))
                response = client.generate_response(prompt_text or "Hello, how can I help?")
                
                if response.startswith("❌"):
                    logger.error(f"Error generating response: {response}")
                    if config.get("show_notifications", True):
                        self.tray_icon.showMessage(
                            "GemType Error",
                            "Failed to generate response. Check logs for details.",
                            QSystemTrayIcon.Critical
                        )
                    return
                
                logger.info("Response generated, pasting...")
                
                # Type the response
                pyperclip.copy(response)
                pyautogui.hotkey('ctrl', 'v')
                
                # Small delay to ensure paste completes
                time.sleep(0.2)
                
                # Restore original clipboard
                pyperclip.copy(original_clipboard)
                
                logger.info("Response pasted successfully")
                
                if config.get("show_notifications", True):
                    self.tray_icon.showMessage(
                        "GemType",
                        "Response generated and pasted",
                        QSystemTrayIcon.Information,
                        2000
                    )
                    
            except Exception as e:
                logger.error(f"Error in hotkey handler: {e}", exc_info=True)
                if config.get("show_notifications", True):
                    self.tray_icon.showMessage(
                        "GemType Error",
                        f"Error: {str(e)}",
                        QSystemTrayIcon.Critical
                    )
                # Restore clipboard on error
                pyperclip.copy(original_clipboard)
                
        except Exception as e:
            logger.critical(f"Critical error in hotkey handler: {e}", exc_info=True)

    # def on_hotkey_triggered(self):
        """Handle hotkey trigger event."""
        # Show a notification
        if self.tray_icon and config.get("show_notifications", True):
            self.tray_icon.showMessage(
                "GemType",
                "Hotkey pressed! Processing your request...",
                QSystemTrayIcon.Information,
                2000
            )
        
        # TODO: Implement the actual hotkey action
        self.statusBar().showMessage("Hotkey pressed!", 3000)
    
    def perform_quick_action(self):
        """Perform a quick action (placeholder for now)."""
        QMessageBox.information(self, "Quick Action", "This is a placeholder for a quick action.")
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.tray_icon and self.tray_icon.isVisible():
            # Hide instead of closing if we have a tray icon
            self.hide()
            event.ignore()
            
            # Show a message that the app is still running
            if config.get("show_notifications", True):
                self.tray_icon.showMessage(
                    "GemType",
                    "GemType is still running in the system tray.",
                    QSystemTrayIcon.Information,
                    2000
                )
        else:
            # No tray icon, quit the application
            self.quit_application()
    
    def show_normal(self):
        """Show the window normally."""
        self.show()
        self.activateWindow()
        self.raise_()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
    
    def quit_application(self):
        """Quit the application."""
        # Clean up resources
        if self.hotkey_manager:
            self.hotkey_manager.stop()
        
        # Close the application
        app = QApplication.instance()
        if app is not None:
            app.quit()
