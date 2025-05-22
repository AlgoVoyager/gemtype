"""
Main application window for GemType.
"""
import logging
import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QSystemTrayIcon,
    QMenu, QAction, QMessageBox, QTabWidget, QStatusBar, QHBoxLayout, QApplication,
    QTextEdit, QGroupBox, QSpacerItem, QSizePolicy, QFrame
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer, QUrl
from PyQt5.QtGui import QIcon, QPixmap, QPalette, QColor, QDesktopServices, QFont

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
        self.setMinimumSize(700, 600) 
        
        # Set application style
        self._apply_theme()
        
        # Show API key warning if not set
        if not config.get("api_key"):
            self._show_api_key_warning()
        
        # Set application icon
        try:
            # Try to load icon from local file
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icons', 'app_icon.jpg')
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
            else:
                # Fallback to resource path
                self.setWindowIcon(QIcon(":/assets/icons/app_icon.jpg"))
        except Exception as e:
            logger.warning(f"Failed to load application icon: {e}")
            # Fallback to system theme icon
            self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
            
        # Show the window on startup
        self.show()
        
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
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icons', 'app_icon.jpg')
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
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
        
        # Add exit button at the bottom
        button_layout = QHBoxLayout()
        
        # Add a spacer to push the exit button to the right
        button_layout.addStretch()
        
        # Create and configure the exit button
        self.exit_button = QPushButton("Stop && Exit")
        # self.exit_button.setFixedWidth(100)
        self.exit_button.clicked.connect(self.quit_application)
        button_layout.addWidget(self.exit_button)
        
        # Add button layout to home layout
        # home_layout.addLayout(button_layout)
        home_layout.setContentsMargins(20, 20, 20, 20)
        home_layout.setSpacing(15)
        
        # Welcome message
        welcome_group = QGroupBox("Welcome to GemType")
        welcome_layout = QVBoxLayout()
        
        welcome_text = QLabel(
            "GemType brings the power of Google's Gemini AI to your fingertips.\n\n<br> "
            " 🖱️ <b>How to use:</b>\n<br>"
            "1. Type and copy your text anywhere\n<br>"
            "2. Press <b>Ctrl+Alt+Space</b> (or your custom hotkey)\n<br>"
            "3. Just wait and the AI will process your input and type the response shortly.\n<br>"
            "💡 <b>Note:</b> GemType will be minimized to system tray icon after you close this window."
        )
        welcome_text.setWordWrap(True)
        welcome_text.setTextFormat(Qt.RichText)
        welcome_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
        welcome_layout.addWidget(welcome_text)
        welcome_group.setLayout(welcome_layout)
        
        # Quick actions group
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout()
        
        # Status indicator
        status_layout = QHBoxLayout()
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("color: #FF4444; font-size: 16px;")
        self.status_label = QLabel("Service: <b>Stopped</b>")
        
        status_layout.addWidget(self.status_indicator)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        # Create start/stop button
        self.start_btn = QPushButton("Start Service")
        self.start_btn.setMinimumHeight(50)
        self.start_btn.clicked.connect(self.toggle_service)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.start_btn)
        
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.setMinimumHeight(50)
        self.settings_btn.clicked.connect(self.show_settings)
        btn_layout.addWidget(self.settings_btn)
        
        actions_layout.addLayout(status_layout)
        actions_layout.addLayout(btn_layout)
        actions_group.setLayout(actions_layout)
        
        # Add widgets to home layout
        home_layout.addWidget(welcome_group)
        home_layout.addWidget(actions_group)
        home_layout.addStretch()
        
        # Create About tab
        self._setup_about_tab()
        
        # Add tabs to main window
        self.tabs.addTab(home_tab, "Home")
        self.tabs.addTab(self.about_tab, "About")
        
        # Add tabs to main layout
        layout.addLayout(header_layout)
        layout.addWidget(self.tabs)
        layout.addLayout(button_layout)
        
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
        from core.hotkey import HotkeyManager
        
        # Initialize hotkey manager with the configured hotkey
        self.hotkey_manager = HotkeyManager(config.get("hotkey", "ctrl+alt+space"))
        self.hotkey_manager.hotkey_triggered.connect(self.on_hotkey_triggered)
        
        # Start the hotkey manager if auto-start is enabled
        if config.get("auto_start", True):
            try:
                self.hotkey_manager.start()
                self.status_indicator.setStyleSheet("color: #4CAF50; font-size: 16px;")
                self.status_label.setText("Service: <b>Running</b>")
                self.start_btn.setText("Stop Service")
            except Exception as e:
                logger.error(f"Failed to start hotkey service: {e}")
                self.status_indicator.setStyleSheet("color: #FF4444; font-size: 16px;")
                self.status_label.setText("Service: <b>Error</b>")
                self.start_btn.setText("Start Service")
        else:
            self.status_indicator.setStyleSheet("color: #FF4444; font-size: 16px;")
            self.status_label.setText("Service: <b>Stopped</b>")
            self.start_btn.setText("Start Service")
    
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
                response = client.generate_response(prompt_text or "send me this msg: copy your text to clipboard and try again.")
                
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
    
    def _setup_about_tab(self):
        """Set up the About tab."""
        self.about_tab = QWidget()
        layout = QVBoxLayout(self.about_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # App info
        info_group = QGroupBox("About GemType")
        info_layout = QVBoxLayout()
        
        # App icon and title
        title_layout = QHBoxLayout()
        try:
            icon_label = QLabel()
            icon_path = os.path.join("assets", "icons", "app_icon.jpg")
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(pixmap)
            title_layout.addWidget(icon_label)
        except:
            pass
            
        title_text = QLabel("<h1>GemType</h1>")
        title_text.setStyleSheet("font-size: 24px; font-weight: bold;")
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        info_layout.addLayout(title_layout)
        
        # Version and description
        version = QLabel("Version 1.0.0")
        description = QLabel(
            "GemType is a lightweight AI assistant that brings the power of Google's Gemini AI "
            "to your fingertips. With a simple hotkey, get AI assistance anywhere on your system."
        )
        description.setWordWrap(True)
        
        # Visit website button
        website_btn = QPushButton("Visit Our Website - Docs")
        website_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://algovoyagers.vercel.app/tools/gemtype")))
        
        # Credits
        credits = QLabel(
            "<b>Credits:</b><br>"
            "• Nishant Dewangan - AlgoVoyager<br>"
            "• PyQt5 for GUI framework<br>"
            "• Google Gemini for AI capabilities<br>"
        )
        credits.setWordWrap(True)
        credits.setOpenExternalLinks(True)
        
        # Add widgets to layout
        info_layout.addWidget(version)
        info_layout.addWidget(description)
        info_layout.addWidget(website_btn, 0, Qt.AlignLeft)
        info_layout.addSpacing(20)
        info_layout.addWidget(credits)
        info_layout.addStretch()
        
        info_group.setLayout(info_layout)
        
        # Add to main layout
        layout.addWidget(info_group)
        layout.addStretch()
        
    def _show_api_key_warning(self):
        """Show a warning if API key is not set."""
        QMessageBox.warning(
            self,
            
            "API Key Required",
            "GemType brings the power of Google's Gemini AI to your fingertips.<br>"
            " 🖱️ <b>How to use:</b> <br>"
            "1. Please set your Google Gemini API key in the Settings to use GemType."
            "You can get an API key from: <br> https://aistudio.google.com/app/apikey<br> <br>"
            "2. Type and copy your text anywhere<br>"
            "3. Press <b>Ctrl+Alt+Space</b> (or your custom hotkey)<br>"
            "4. Just wait and the AI will process your input and type the response shortly.<br>",
            QMessageBox.Ok
        )
        self.show_settings()
        
    def _apply_theme(self, theme_name=None):
        """Apply the selected theme."""
        if theme_name is None:
            theme_name = config.get("theme", "system").lower()
        
        if theme_name == "dark":
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QGroupBox {
                    border: 1px solid #444;
                    border-radius: 5px;
                    margin-top: 10px;
                    padding: 15px;
                    background-color: #333333;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #4a90e2;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #357abd;
                }
                QPushButton:disabled {
                    background-color: #555555;
                }
                QTabWidget::pane {
                    border: 1px solid #444;
                    background: #2b2b2b;
                }
                QTabBar::tab {
                    background: #3c3c3c;
                    color: #ffffff;
                    padding: 8px 16px;
                    border: 1px solid #444;
                    border-bottom: none;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected {
                    background: #2b2b2b;
                    border-bottom: 2px solid #4a90e2;
                }
                QLabel[accessibleName="helpText"] {
                    color: #aaaaaa;
                    font-size: 9pt;
                }
                QTextEdit, QLineEdit, QComboBox {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555;
                    border-radius: 3px;
                    padding: 5px;
                }
                QStatusBar {
                    background: #333333;
                    color: #ffffff;
                }
            """)
        elif theme_name == "light":
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #f5f5f5;
                    color: #333333;
                }
                QGroupBox {
                    border: 1px solid #e0e0e0;
                    border-radius: 5px;
                    margin-top: 10px;
                    padding: 15px;
                    background-color: #ffffff;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                    color: #333333;
                }
                QPushButton {
                    background-color: #4a90e2;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #357abd;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                }
                QTabWidget::pane {
                    border: 1px solid #e0e0e0;
                    background: #ffffff;
                }
                QTabBar::tab {
                    background: #f0f0f0;
                    color: #333333;
                    padding: 8px 16px;
                    border: 1px solid #e0e0e0;
                    border-bottom: none;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected {
                    background: #ffffff;
                    border-bottom: 2px solid #4a90e2;
                }
                QLabel[accessibleName="helpText"] {
                    color: #666666;
                    font-size: 9pt;
                }
                QTextEdit, QLineEdit, QComboBox {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #ddd;
                    border-radius: 3px;
                    padding: 5px;
                }
                QStatusBar {
                    background: #f0f0f0;
                    color: #333333;
                    border-top: 1px solid #e0e0e0;
                }
            """)
            
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
    
    def toggle_service(self):
        """Toggle the hotkey service on/off."""
        if not hasattr(self, 'hotkey_manager') or not self.hotkey_manager:
            return
            
        if self.hotkey_manager.is_running():
            self.hotkey_manager.stop()
            self.status_indicator.setStyleSheet("color: #FF4444; font-size: 16px;")
            self.status_label.setText("Service: <b>Stopped</b>")
            self.start_btn.setText("Start Service")
        else:
            try:
                self.hotkey_manager.start()
                self.status_indicator.setStyleSheet("color: #4CAF50; font-size: 16px;")
                self.status_label.setText("Service: <b>Running</b>")
                self.start_btn.setText("Stop Service")
            except Exception as e:
                logger.error(f"Failed to start hotkey service: {e}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to start hotkey service: {e}"
                )
    
    def quit_application(self):
        """Quit the application."""
        # Clean up resources
        if hasattr(self, 'hotkey_manager') and self.hotkey_manager:
            self.hotkey_manager.stop()
        
        # Close the application
        app = QApplication.instance()
        if app is not None:
            app.quit()
