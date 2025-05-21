"""
Settings dialog for GemType.
"""
import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QComboBox, QGroupBox, QDialogButtonBox,
    QFileDialog, QMessageBox, QTabWidget, QWidget, QSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence, QIntValidator

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
        
        self.setWindowTitle("GemType Settings")
        self.setMinimumSize(600, 500)
        
        # Store original settings to detect changes
        self.original_settings = {
            "api_key": config.get("api_key", ""),
            "hotkey": config.get("hotkey", "ctrl+alt+space"),
            "model": config.get("model", "gemini-2.5-flash-preview-05-20"),
            "auto_start": config.get("auto_start", True),
            "show_notifications": config.get("show_notifications", True),
            "theme": config.get("theme", "system"),
        }
        
        # Initialize UI
        self._init_ui()
        
        # Load current settings
        self._load_settings()
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # API Settings Tab
        api_tab = QWidget()
        api_layout = QVBoxLayout(api_tab)
        
        # API Key Group
        api_key_group = QGroupBox("API Settings")
        api_key_layout = QFormLayout()
        
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.textChanged.connect(self.on_settings_changed)
        
        self.show_api_key_cb = QCheckBox("Show API Key")
        self.show_api_key_cb.toggled.connect(self.toggle_api_key_visibility)
        
        api_key_layout.addRow("API Key:", self.api_key_edit)
        api_key_layout.addRow("", self.show_api_key_cb)
        
        # Model selection
        self.model_combo = QComboBox()
        self.model_combo.addItems(["gemini-2.5-flash-preview-05-20", "gemini-1.5-pro"])
        self.model_combo.currentTextChanged.connect(self.on_settings_changed)
        
        api_key_layout.addRow("Model:", self.model_combo)
        
        api_key_group.setLayout(api_key_layout)
        
        # Add API group to API tab
        api_layout.addWidget(api_key_group)
        api_layout.addStretch()
        
        # Hotkey Tab
        hotkey_tab = QWidget()
        hotkey_layout = QVBoxLayout(hotkey_tab)
        
        # Hotkey Group
        hotkey_group = QGroupBox("Hotkey Settings")
        hotkey_form_layout = QFormLayout()
        
        self.hotkey_edit = QLineEdit()
        self.hotkey_edit.setReadOnly(True)
        self.hotkey_edit.setPlaceholderText("Press a key combination...")
        self.hotkey_edit.keyPressEvent = self.on_hotkey_press
        self.hotkey_edit.setToolTip("Press the key combination you want to use")
        
        self.reset_hotkey_btn = QPushButton("Reset to Default")
        self.reset_hotkey_btn.clicked.connect(self.reset_hotkey)
        
        hotkey_btn_layout = QHBoxLayout()
        hotkey_btn_layout.addWidget(self.hotkey_edit)
        hotkey_btn_layout.addWidget(self.reset_hotkey_btn)
        
        hotkey_form_layout.addRow("Hotkey:", hotkey_btn_layout)
        hotkey_group.setLayout(hotkey_form_layout)
        
        # Add hotkey group to hotkey tab
        hotkey_layout.addWidget(hotkey_group)
        hotkey_layout.addStretch()
        
        # Application Tab
        app_tab = QWidget()
        app_layout = QVBoxLayout(app_tab)
        
        # Application Settings Group
        app_group = QGroupBox("Application Settings")
        app_form_layout = QFormLayout()
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["system", "light", "dark"])
        self.theme_combo.currentTextChanged.connect(self.on_settings_changed)
        
        # Auto-start option
        self.auto_start_cb = QCheckBox("Start GemType when I log in")
        self.auto_start_cb.stateChanged.connect(self.on_settings_changed)
        
        # Notifications option
        self.notifications_cb = QCheckBox("Show notifications")
        self.notifications_cb.stateChanged.connect(self.on_settings_changed)
        
        # Add widgets to form layout
        app_form_layout.addRow("Theme:", self.theme_combo)
        app_form_layout.addRow(self.auto_start_cb)
        app_form_layout.addRow(self.notifications_cb)
        
        app_group.setLayout(app_form_layout)
        
        # Add app group to app tab
        app_layout.addWidget(app_group)
        app_layout.addStretch()
        
        # Add tabs to tab widget
        self.tabs.addTab(api_tab, "API")
        self.tabs.addTab(hotkey_tab, "Hotkey")
        self.tabs.addTab(app_tab, "Application")
        
        # Create button box
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel | QDialogButtonBox.RestoreDefaults
        )
        self.button_box.accepted.connect(self.save_settings)
        self.button_box.rejected.connect(self.reject)
        self.button_box.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self.restore_defaults)
        
        # Add widgets to main layout
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(self.button_box)
        
        # Apply styles
        self._apply_styles()
    
    def _apply_styles(self):
        """Apply custom styles to the dialog."""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QGroupBox {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLineEdit, QComboBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                min-width: 200px;
            }
            QPushButton {
                padding: 5px 10px;
                background-color: #4285f4;
                color: white;
                border: none;
                border-radius: 3px;
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
        theme_index = self.theme_combo.findText(self.original_settings["theme"])
        if theme_index >= 0:
            self.theme_combo.setCurrentIndex(theme_index)
        
        self.auto_start_cb.setChecked(self.original_settings["auto_start"])
        self.notifications_cb.setChecked(self.original_settings["show_notifications"])
    
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
            "theme": self.theme_combo.currentText(),
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
