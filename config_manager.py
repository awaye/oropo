"""
Configuration Manager Module
Handles user preferences for Oropo voice typing app
"""

import os
import json
from pynput import keyboard


# Available hotkey options
HOTKEY_OPTIONS = {
    "right_command": {"key": keyboard.Key.cmd_r, "label": "Right Command ⌘"},
    "left_command": {"key": keyboard.Key.cmd_l, "label": "Left Command ⌘"},
    "right_option": {"key": keyboard.Key.alt_r, "label": "Right Option ⌥"},
    "left_option": {"key": keyboard.Key.alt_l, "label": "Left Option ⌥"},
    "right_control": {"key": keyboard.Key.ctrl_r, "label": "Right Control ⌃"},
    "fn": {"key": keyboard.Key.f13, "label": "F13 Key"},
}


class ConfigManager:
    """Manages user configuration with persistent storage"""
    
    def __init__(self):
        self.config_dir = os.path.expanduser("~/.oropo")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self._ensure_directory()
        self.config = self._load_config()
    
    def _ensure_directory(self):
        """Create config directory if it doesn't exist"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
    
    def _load_config(self):
        """Load config from file or return defaults"""
        default_config = {
            "hotkey": "right_command",
            "model": "mlx-community/whisper-small-mlx"
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults for any missing keys
                    return {**default_config, **loaded}
        except Exception:
            pass
        
        return default_config
    
    def _save_config(self):
        """Save config to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass
    
    def get_hotkey(self):
        """Get the configured hotkey"""
        hotkey_name = self.config.get("hotkey", "right_command")
        return HOTKEY_OPTIONS.get(hotkey_name, HOTKEY_OPTIONS["right_command"])
    
    def get_hotkey_name(self):
        """Get the hotkey setting name"""
        return self.config.get("hotkey", "right_command")
    
    def set_hotkey(self, hotkey_name):
        """Set the hotkey"""
        if hotkey_name in HOTKEY_OPTIONS:
            self.config["hotkey"] = hotkey_name
            self._save_config()
            return True
        return False
    
    def get_available_hotkeys(self):
        """Get list of available hotkey options"""
        return [(name, info["label"]) for name, info in HOTKEY_OPTIONS.items()]


# Test
if __name__ == "__main__":
    config = ConfigManager()
    print(f"Current hotkey: {config.get_hotkey()['label']}")
    print(f"Available hotkeys:")
    for name, label in config.get_available_hotkeys():
        print(f"  - {name}: {label}")
