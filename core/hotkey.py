"""
Hotkey management for GemType.
Handles global hotkey registration and handling.
"""
import logging
import threading
from typing import Callable, Optional
import keyboard
from PyQt5.QtCore import QObject, pyqtSignal

# Configure logging
logger = logging.getLogger(__name__)

class HotkeyManager(QObject):
    """Manages global hotkey registration and handling."""
    
    # Signal emitted when the hotkey is pressed
    hotkey_triggered = pyqtSignal()
    
    def __init__(self, default_hotkey: str = "ctrl+alt+space"):
        """Initialize the hotkey manager."""
        super().__init__()
        self._hotkey = default_hotkey
        self._hook = None
        self._is_registered = False
        self._lock = threading.Lock()
    
    @property
    def hotkey(self) -> str:
        """Get the current hotkey combination."""
        return self._hotkey
    
    def set_hotkey(self, hotkey: str) -> bool:
        """
        Set a new hotkey combination.
        
        Args:
            hotkey: The new hotkey combination (e.g., 'ctrl+alt+space')
            
        Returns:
            bool: True if the hotkey was set successfully, False otherwise
        """
        if not hotkey:
            logger.error("Cannot set empty hotkey")
            return False
            
        with self._lock:
            # Unregister current hotkey if registered
            if self._is_registered:
                self._unregister()
            
            # Try to register the new hotkey
            old_hotkey = self._hotkey
            self._hotkey = hotkey
            
            if not self._register():
                # Revert to old hotkey if registration fails
                self._hotkey = old_hotkey
                self._register()  # Try to re-register old hotkey
                return False
                
            return True
    
    def _register(self) -> bool:
        """Register the current hotkey."""
        try:
            if self._is_registered:
                return True
                
            logger.info("Registering hotkey: %s", self._hotkey)
            self._hook = keyboard.add_hotkey(
                self._hotkey,
                self._on_hotkey_pressed,
                suppress=True
            )
            self._is_registered = True
            return True
        except Exception as e:
            logger.error("Failed to register hotkey %s: %s", self._hotkey, e)
            return False
    
    def _unregister(self) -> None:
        """Unregister the current hotkey."""
        try:
            if self._hook is not None:
                logger.debug("Unregistering hotkey: %s", self._hotkey)
                keyboard.remove_hotkey(self._hook)
                self._hook = None
            self._is_registered = False
        except Exception as e:
            logger.error("Failed to unregister hotkey: %s", e)
    
    def _on_hotkey_pressed(self) -> None:
        """Handle hotkey press event."""
        logger.debug("Hotkey pressed: %s", self._hotkey)
        self.hotkey_triggered.emit()
    
    def is_running(self) -> bool:
        """Check if the hotkey manager is running.
        
        Returns:
            bool: True if the hotkey manager is running, False otherwise
        """
        with self._lock:
            return self._is_registered
    
    def start(self) -> None:
        """Start the hotkey manager."""
        with self._lock:
            if not self._is_registered:
                self._register()
    
    def stop(self) -> None:
        """Stop the hotkey manager."""
        with self._lock:
            self._unregister()
    
    def __del__(self) -> None:
        """Clean up resources."""
        self.stop()
