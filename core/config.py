"""
Configuration management for GemType.
Handles loading, saving, and validating application settings.
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    """Manages application configuration with persistence."""
    
    # Default configuration values
    DEFAULTS = {
        "api_key": "",
        "hotkey": "ctrl+alt+space",
        "model": "gemini-2.5-flash-preview-05-20",
        "auto_start": True,
        "show_notifications": True,
        "theme": "system",  # 'light', 'dark', or 'system'
        "first_run": True  # Add this line
    }
    
    def __init__(self):
        """Initialize configuration with default values and load from file if exists."""
        self.config_path = self._get_config_path()
        self._data = self.DEFAULTS.copy()
        self._load()
    
    def _get_config_path(self) -> Path:
        """Get the path to the config file."""
        config_dir = Path.home() / ".config" / "gemtype"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.json"
    
    def _load(self) -> None:
        """Load configuration from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    loaded = json.load(f)
                    self._data.update(loaded)
                    logger.info("Configuration loaded from %s", self.config_path)
            else:
                self._save()  # Create default config file
        except Exception as e:
            logger.error("Error loading config: %s", e, exc_info=True)
    
    def _save(self) -> None:
        """Save current configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self._data, f, indent=2)
            logger.debug("Configuration saved to %s", self.config_path)
        except Exception as e:
            logger.error("Error saving config: %s", e, exc_info=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._data.get(key, default)
    
    def set(self, key: str, value: Any, save: bool = True) -> None:
        """Set a configuration value."""
        if key in self._data:
            self._data[key] = value
            if save:
                self._save()
        else:
            logger.warning("Attempted to set unknown config key: %s", key)
    
    def update(self, updates: Dict[str, Any], save: bool = True) -> None:
        """Update multiple configuration values at once."""
        for key, value in updates.items():
            if key in self._data:
                self._data[key] = value
            else:
                logger.warning("Attempted to set unknown config key: %s", key)
        if save and updates:
            self._save()
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self._data = self.DEFAULTS.copy()
        self._save()
        logger.info("Configuration reset to defaults")

# Global configuration instance
config = Config()
