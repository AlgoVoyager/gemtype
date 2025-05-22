"""
Settings dialog for GemType.
"""
import logging
from core.config import config
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QComboBox, QGroupBox, QDialogButtonBox,
    QFileDialog, QMessageBox, QTabWidget, QWidget, QSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence, QIntValidator
from PyQt5.QtWidgets import QStyle
from core.config import config

# Configure logging
logger = logging.getLogger(__name__)

class SettingsDialog(QDialog):
    """Settings dialog for GemType."""
    
    # Signal emitted when settings are saved
    settings_saved = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the settings dialog."""
        super().__init__(parent)
        
        self.setWindowTitle("Settings")
        self.setMinimumSize(600, 550)
        
        # Initialize config
        self.config = config
        
        # Store original settings to detect changes
        self.original_settings = {
            "api_key": config.get("api_key", ""),
            "hotkey": config.get("hotkey", "ctrl+alt+space"),
            "model": config.get("model", "gemini-2.5-flash-preview-05-20"),
            "auto_start": config.get("auto_start", True),
            "show_notifications": config.get("show_notifications", True),
            "theme": config.get("theme", "light"),
        }
        
        # Initialize UI
        self._init_ui()
        self._apply_theme(self.original_settings["theme"])
    
        # Load current settings
        self._load_settings()
    
    def _init_ui(self):
        # Set application icon
        try:
            # Try to load icon from local file
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icons', 'app_icon.jpg')
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
            else:
                # Fallback to resource path
                self.setWindowIcon(QIcon(":/assets/icons/app_icon.ico"))
        except Exception as e:
            logger.warning(f"Failed to load application icon: {e}")
            # Fallback to system theme icon
            self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))

        """Initialize the user interface."""
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # Create tabs
        self.tabs = QTabWidget()
        
        # ===== API Tab =====
        api_tab = QWidget()
        api_layout = QVBoxLayout(api_tab)
        api_layout.setContentsMargins(20, 20, 20, 20)
        api_layout.setSpacing(15)
        
        # API Settings Group
        api_group = QGroupBox("API Settings")
        api_form_layout = QFormLayout(api_group)
        api_form_layout.setContentsMargins(15, 25, 15, 15)
        api_form_layout.setSpacing(10)
        
        # API Key
        api_key_layout = QHBoxLayout()
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.textChanged.connect(self.on_settings_changed)
        
        self.api_key_btn = QPushButton("Show")
        self.api_key_btn.setCheckable(True)
        self.api_key_btn.toggled.connect(self.toggle_api_key_visibility)
        
        api_key_layout.addWidget(self.api_key_edit)
        api_key_layout.addWidget(self.api_key_btn)
        
        api_key_label = QLabel()
        api_key_label.setText("<b>API Key:</b><br><span style='font-size: 9pt; color: #666;'>Enter your API key</span>")
        api_key_label.setTextFormat(Qt.RichText)
        api_form_layout.addRow(api_key_label, api_key_layout)
        
        # Model selection
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "gemini-2.5-flash-preview-05-20",
            "gemini-2.5-flash-preview-04-17",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b",
            "gemma-3-27b-it",
            "gemini-2.5-pro-preview-05-06",
            "gemini-1.5-pro",
            ])
        self.model_combo.currentTextChanged.connect(self.on_settings_changed)
        
        model_label = QLabel("<b>Model:</b>")
        model_label.setTextFormat(Qt.RichText)
        api_form_layout.addRow(model_label, self.model_combo)
        
        # Add API group to API tab
        api_layout.addWidget(api_group)
        api_layout.addStretch()

        # info group
        info_group = QGroupBox("Info")
        info_layout = QVBoxLayout()
        
        info_text = QLabel(
            "API Key is required to use the service.\n<br> "
            "You can switch to different API models<br>"
            "Which most of listed models here offers Free Tier<br>"
            "Each Model can have own features and capabilities<br>"
            "As well as different pricing and RPM (Requests Per Minute) limits<br>"
            "You can find more information about the models in Docs below."
        )
        info_text.setWordWrap(True)
        info_text.setTextFormat(Qt.RichText)
        info_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
        info_layout.addWidget(info_text)

        website_btn = QPushButton("Google AI for Developers - Docs")
        website_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://ai.google.dev/gemini-api/docs/rate-limits#free-tier")))
        info_layout.addWidget(website_btn, 0, Qt.AlignLeft)
        
        info_group.setLayout(info_layout)
        
        # Add info group to API tab
        api_layout.addWidget(info_group)
        api_layout.addStretch()
        
        # ===== Hotkey Tab =====
        hotkey_tab = QWidget()
        hotkey_layout = QVBoxLayout(hotkey_tab)
        hotkey_layout.setContentsMargins(20, 20, 20, 20)
        hotkey_layout.setSpacing(15)
        
        # Hotkey settings
        hotkey_group = QGroupBox("Hotkey Settings")
        hotkey_form = QFormLayout(hotkey_group)
        hotkey_form.setContentsMargins(15, 25, 15, 15)
        hotkey_form.setSpacing(10)
        
        self.hotkey_edit = QLineEdit()
        self.hotkey_edit.setReadOnly(True)
        self.hotkey_edit.setPlaceholderText("Press a key combination...")
        self.hotkey_edit.keyPressEvent = self.on_hotkey_press
        self.hotkey_edit.setToolTip("Press the key combination you want to use")
        
        self.reset_hotkey_btn = QPushButton("Reset")
        self.reset_hotkey_btn.clicked.connect(self.reset_hotkey)
        
        hotkey_btn_layout = QHBoxLayout()
        hotkey_btn_layout.addWidget(self.hotkey_edit)
        hotkey_btn_layout.addWidget(self.reset_hotkey_btn)
        
        hotkey_label = QLabel()
        hotkey_label.setText("<b>Hotkey:</b><br><span style='font-size: 9pt; color: #666;'>Press the key combination you want to use</span>")
        hotkey_label.setTextFormat(Qt.RichText)
        hotkey_form.addRow(hotkey_label, hotkey_btn_layout)
        
        hotkey_layout.addWidget(hotkey_group)
        hotkey_layout.addStretch()
        
        # ===== Application Tab =====
        app_tab = QWidget()
        app_layout = QVBoxLayout(app_tab)
        app_layout.setContentsMargins(20, 20, 20, 20)
        app_layout.setSpacing(15)
        
        # Application Settings Group
        app_group = QGroupBox("Application Settings")
        app_form_layout = QFormLayout(app_group)
        app_form_layout.setContentsMargins(15, 25, 15, 15)
        app_form_layout.setSpacing(10)
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Light", "Dark"])
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        
        theme_label = QLabel("<b>Theme:</b>")
        theme_label.setTextFormat(Qt.RichText)
        app_form_layout.addRow(theme_label, self.theme_combo)
        
        # Auto-start option
        self.auto_start_cb = QCheckBox("Start GemType when I log in")
        self.auto_start_cb.stateChanged.connect(self.on_settings_changed)
        
        # Notifications option
        self.notifications_cb = QCheckBox("Show notifications")
        self.notifications_cb.stateChanged.connect(self.on_settings_changed)
        
        # Add widgets to form layout
        app_form_layout.addRow(self.auto_start_cb)
        app_form_layout.addRow(self.notifications_cb)
        
        # Add app group to app tab
        app_layout.addWidget(app_group)
        app_layout.addStretch()
        
        # ===== Add Tabs =====
        self.tabs.addTab(api_tab, "API")
        self.tabs.addTab(hotkey_tab, "Hotkey")
        self.tabs.addTab(app_tab, "Application")
        
        # Add main layout
        main_layout.addWidget(self.tabs)
        
        # Create button box
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel | QDialogButtonBox.RestoreDefaults
        )
        self.button_box.accepted.connect(self.save_settings)
        self.button_box.rejected.connect(self.reject)
        self.button_box.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self.restore_defaults)
        
        # Disable save button initially (no changes yet)
        self.button_box.button(QDialogButtonBox.Save).setEnabled(False)
        
        # Add button box to main layout
        main_layout.addWidget(self.button_box)
        
        # Apply styles
        self._apply_theme()
    
    def _apply_theme(self, theme_name=None):
        """Apply the selected theme."""
        if theme_name is None:
            theme_name = config.get("theme", "light").lower()  # Default to light theme
            
        if theme_name == "dark":
            # Dark theme with #0C1226 as base
            self.setStyleSheet("""
                /* Base colors */
                QMainWindow, QWidget, QDialog {
                    background-color: #0C1226;
                    color: #e0e0e0;
                }
                
                /* Buttons */
                QPushButton {
                    background-color: #d1a300;
                    color: #000000;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e6b400;
                }
                QPushButton:pressed {
                    background-color: #cc9f00;
                }
                
                /* Tabs */
                QTabWidget::pane {
                    border: 1px solid #1a237e;
                    border-radius: 4px;
                    background: #0a0f1f;
                    margin-top: 10px;
                }
                QTabBar::tab {
                    background: #1a237e;
                    color: #a0a0b0;
                    border: 1px solid #1a237e;
                    padding: 8px 16px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background: #0C1226;
                    color: #ffffff;
                    border-bottom: 2px solid #ffc800;
                }
                
                /* Group Boxes */
                QGroupBox {
                    border: 1px solid #1a237e;
                    border-radius: 4px;
                    margin-top: 10px;
                    padding: 15px;
                    background: #0a0f1f;
                }
                QGroupBox::title {
                    color: #ffffff;
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
                
                /* Input Fields */
                QLineEdit, QTextEdit, QComboBox {
                    background-color: #0a0f1f;
                    color: #e0e0e0;
                    border: 1px solid #1a237e;
                    border-radius: 3px;
                    padding: 5px;
                }
                
                /* Labels */
                QLabel {
                    color: #e0e0e0;
                }
                QLabel[accessibleName="helpText"] {
                    color: #a0a0b0;
                    font-size: 9pt;
                }
                
                /* Status Bar */
                QStatusBar {
                    background: #0a0f1f;
                    color: #e0e0e0;
                    border-top: 1px solid #1a237e;
                }
            """)
        else:
            # Light theme (default)
            self.setStyleSheet("""
                /* Base colors */
                QMainWindow, QWidget, QDialog {
                    background-color: #f0f0f0;
                    color: #333333;
                }
                
                /* Buttons */
                QPushButton {
                    background-color: #ffd749;
                    color: #000000;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e6b400;
                }
                QPushButton:pressed {
                    background-color: #cc9f00;
                }
                
                /* Tabs */
                QTabWidget::pane {
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    background: white;
                    margin-top: 10px;
                }
                QTabBar::tab {
                    background: #e0e0e0;
                    color: #666666;
                    border: 1px solid #e0e0e0;
                    padding: 8px 16px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background: white;
                    color: #333333;
                    border-bottom: 2px solid #ffc800;
                }
                
                /* Group Boxes */
                QGroupBox {
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    margin-top: 10px;
                    padding: 15px;
                    background:  #f0f0f0;
                }
                QGroupBox::title {
                    color: #333333;
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
                
                /* Input Fields */
                QLineEdit, QTextEdit, QComboBox {
                    background-color: white;
                    color: #333333;
                    border: 1px solid #e0e0e0;
                    border-radius: 3px;
                    padding: 5px;
                }
                
                /* Labels */
                QLabel {
                    color: #333333;
                }
                QLabel[accessibleName="helpText"] {
                    color: #666666;
                    font-size: 9pt;
                }
                
                /* Status Bar */
                QStatusBar {
                    background: #fefefe;
                    color: #333333;
                    border-top: 1px solid #e0e0e0;
                }
            """)  
    def _load_settings(self):
        """Load current settings into the UI."""
        # API Settings
        self.api_key_edit.setText(self.original_settings["api_key"])
        
        # Set model
        model_index = self.model_combo.findText(self.original_settings["model"])
        if model_index >= 0:
            self.model_combo.setCurrentIndex(model_index)
        
        # Hotkey
        self.hotkey_edit.setText(self.original_settings["hotkey"])
        
        # Application settings
        theme = self.original_settings["theme"].capitalize()
        theme_index = self.theme_combo.findText(theme)
        if theme_index >= 0:
            self.theme_combo.setCurrentIndex(theme_index)
            # Apply the theme immediately when loading settings
            if hasattr(self.parent(), '_apply_theme'):
                self.parent()._apply_theme(theme.lower())
                
        self.auto_start_cb.setChecked(self.original_settings["auto_start"])
        self.notifications_cb.setChecked(self.original_settings["show_notifications"])
        
    def on_theme_changed(self, theme_name):
        """Handle theme changes in the settings dialog."""
        # Apply theme to settings dialog
        self._apply_theme(theme_name.lower())
        
        # Apply theme to main window if it exists
        if hasattr(self.parent(), '_apply_theme'):
            self.parent()._apply_theme(theme_name.lower())
        
        # Mark settings as changed
        self.on_settings_changed()
    
    def on_settings_changed(self):
        """Handle settings changes."""
        # Enable/disable save button based on changes
        current_settings = self._get_current_settings()
        has_changes = any(
            current_settings[key] != self.original_settings[key]
            for key in self.original_settings
        )
        
        self.button_box.button(QDialogButtonBox.Save).setEnabled(has_changes)
    
    def _get_current_settings(self):
        """Get current settings from the UI."""
        return {
            "api_key": self.api_key_edit.text(),
            "hotkey": self.hotkey_edit.text(),
            "model": self.model_combo.currentText(),
            "auto_start": self.auto_start_cb.isChecked(),
            "show_notifications": self.notifications_cb.isChecked(),
            "theme": self.theme_combo.currentText().lower(),
        }
    
    def toggle_api_key_visibility(self, checked):
        """Toggle API key visibility."""
        if checked:
            self.api_key_edit.setEchoMode(QLineEdit.Normal)
        else:
            self.api_key_edit.setEchoMode(QLineEdit.Password)
    
    def on_hotkey_press(self, event):
        """Handle hotkey press event."""
        # Ignore modifier keys
        if event.key() in (Qt.Key_Control, Qt.Key_Alt, Qt.Key_Shift, Qt.Key_Meta):
            return
        
        # Get the key sequence
        key_sequence = []
        
        if event.modifiers() & Qt.ControlModifier:
            key_sequence.append("Ctrl")
        if event.modifiers() & Qt.AltModifier:
            key_sequence.append("Alt")
        if event.modifiers() & Qt.ShiftModifier:
            key_sequence.append("Shift")
        if event.modifiers() & Qt.MetaModifier:
            key_sequence.append("Meta")
        
        # Add the actual key
        key = QKeySequence(event.key()).toString()
        if key and key not in ["Ctrl", "Alt", "Shift", "Meta"]:
            key_sequence.append(key)
        
        # Update the hotkey display
        if len(key_sequence) > 0:
            hotkey = "+".join(key_sequence).lower()
            self.hotkey_edit.setText(hotkey)
            self.on_settings_changed()
    
    def reset_hotkey(self):
        """Reset hotkey to default."""
        default_hotkey = "ctrl+alt+space"
        self.hotkey_edit.setText(default_hotkey)
        self.on_settings_changed()
    
    def restore_defaults(self):
        """Restore all settings to default values."""
        reply = QMessageBox.question(
            self,
            "Restore Defaults",
            "Are you sure you want to restore all settings to their default values?\n"
            "This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Reset to default values
            self.original_settings = {
                "api_key": "",
                "hotkey": "ctrl+alt+space",
                "model": "gemini-2.5-flash-preview-05-20",
                "auto_start": True,
                "show_notifications": True,
                "theme": "system",
            }
            
            # Update UI
            self._load_settings()
            self.on_settings_changed()
    
    def save_settings(self):
        """Save settings to config."""
        current_settings = self._get_current_settings()
        
        # Validate API key if it's being set
        if current_settings["api_key"] and len(current_settings["api_key"]) < 20:  # Simple validation
            QMessageBox.warning(
                self,
                "Invalid API Key",
                "Please enter a valid Gemini API key.",
                QMessageBox.Ok
            )
            return
        
        # Validate hotkey
        if not current_settings["hotkey"]:
            QMessageBox.warning(
                self,
                "Invalid Hotkey",
                "Please set a valid hotkey combination.",
                QMessageBox.Ok
            )
            return
        
        # Save settings
        for key, value in current_settings.items():
            config.set(key, value)
        
        # Update original settings
        self.original_settings = current_settings
        
        # Disable save button
        self.button_box.button(QDialogButtonBox.Save).setEnabled(False)
        
        # Emit signal that settings were saved
        self.settings_saved.emit()
        
        # Show success message
        QMessageBox.information(
            self,
            "Settings Saved",
            "Your settings have been saved successfully.",
            QMessageBox.Ok
        )
        
        # Close the dialog if it was opened modally
        if self.isModal():
            self.accept()
