"""
Configuration Manager Module
Handles user preferences for Oropo voice typing app
Supports custom hotkey combinations
"""

import os
import json
from pynput import keyboard


# Modifier key mappings
MODIFIER_KEYS = {
    keyboard.Key.cmd: "⌘ Command",
    keyboard.Key.cmd_l: "⌘ Command",
    keyboard.Key.cmd_r: "⌘ Command",
    keyboard.Key.ctrl: "⌃ Control",
    keyboard.Key.ctrl_l: "⌃ Control",
    keyboard.Key.ctrl_r: "⌃ Control",
    keyboard.Key.alt: "⌥ Option",
    keyboard.Key.alt_l: "⌥ Option",
    keyboard.Key.alt_r: "⌥ Option",
    keyboard.Key.shift: "⇧ Shift",
    keyboard.Key.shift_l: "⇧ Shift",
    keyboard.Key.shift_r: "⇧ Shift",
}

# Default hotkey presets
HOTKEY_PRESETS = {
    "right_command": {
        "keys": [keyboard.Key.cmd_r],
        "label": "Right Command ⌘"
    },
    "control_option": {
        "keys": [keyboard.Key.ctrl, keyboard.Key.alt],
        "label": "Control + Option"
    },
    "control_shift": {
        "keys": [keyboard.Key.ctrl, keyboard.Key.shift],
        "label": "Control + Shift"
    },
}


class ConfigManager:
    """Manages user configuration with persistent storage"""
    
    def __init__(self):
        self.config_dir = os.path.expanduser("~/.oropo")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self._ensure_directory()
        self.config = self._load_config()
        
        # For custom hotkey recording
        self.recording_hotkey = False
        self.recorded_keys = set()
    
    def _ensure_directory(self):
        """Create config directory if it doesn't exist"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
    
    def _load_config(self):
        """Load config from file or return defaults"""
        default_config = {
            "hotkey_preset": "right_command",
            "custom_hotkey": None,  # List of key names for custom combo
            "model": "mlx-community/whisper-small-mlx"
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
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
    
    def get_hotkey_keys(self):
        """Get the list of keys for the current hotkey"""
        # Check for custom hotkey first
        custom = self.config.get("custom_hotkey")
        if custom:
            return self._parse_custom_keys(custom)
        
        # Fall back to preset
        preset_name = self.config.get("hotkey_preset", "right_command")
        preset = HOTKEY_PRESETS.get(preset_name, HOTKEY_PRESETS["right_command"])
        return preset["keys"]
    
    def get_hotkey_label(self):
        """Get the display label for current hotkey"""
        custom = self.config.get("custom_hotkey")
        if custom:
            return " + ".join(custom)
        
        preset_name = self.config.get("hotkey_preset", "right_command")
        preset = HOTKEY_PRESETS.get(preset_name, HOTKEY_PRESETS["right_command"])
        return preset["label"]
    
    def get_hotkey_name(self):
        """Get the preset name or 'custom'"""
        if self.config.get("custom_hotkey"):
            return "custom"
        return self.config.get("hotkey_preset", "right_command")
    
    def set_hotkey_preset(self, preset_name):
        """Set a preset hotkey"""
        if preset_name in HOTKEY_PRESETS:
            self.config["hotkey_preset"] = preset_name
            self.config["custom_hotkey"] = None
            self._save_config()
            return True
        return False
    
    def set_custom_hotkey(self, key_names):
        """Set a custom hotkey from a list of key names"""
        self.config["custom_hotkey"] = key_names
        self._save_config()
    
    def _parse_custom_keys(self, key_names):
        """Parse key names back to pynput Key objects"""
        key_map = {
            "⌘ Command": keyboard.Key.cmd,
            "⌃ Control": keyboard.Key.ctrl,
            "⌥ Option": keyboard.Key.alt,
            "⇧ Shift": keyboard.Key.shift,
        }
        return [key_map.get(name, keyboard.Key.cmd) for name in key_names if name in key_map]
    
    def get_available_presets(self):
        """Get list of available preset hotkey options"""
        return [(name, info["label"]) for name, info in HOTKEY_PRESETS.items()]
    
    def key_to_label(self, key):
        """Convert a pynput key to a display label"""
        return MODIFIER_KEYS.get(key, str(key))
    
    # Legacy compatibility
    def get_hotkey(self):
        """Legacy method - returns dict with 'key' and 'label'"""
        keys = self.get_hotkey_keys()
        return {
            "key": keys[0] if keys else keyboard.Key.cmd_r,
            "keys": keys,
            "label": self.get_hotkey_label()
        }
    
    def get_available_hotkeys(self):
        """Legacy method - returns preset list"""
        return self.get_available_presets()


# Test
if __name__ == "__main__":
    config = ConfigManager()
    print(f"Current hotkey: {config.get_hotkey_label()}")
    print(f"Available presets:")
    for name, label in config.get_available_presets():
        print(f"  - {name}: {label}")
