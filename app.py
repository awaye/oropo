"""
Oropo - Voice Typing Assistant
A macOS menu bar app for voice-to-text typing by Kini AI
"""

import rumps
import threading
import time
from pynput import keyboard

from audio_recorder import AudioRecorder
from transcription_engine import TranscriptionEngine
from text_injector import TextInjector
from stats_manager import StatsManager
from config_manager import ConfigManager, MODIFIER_KEYS
from history_manager import HistoryManager


class VoiceTypingApp(rumps.App):
    """Main menu bar application for voice typing"""
    
    def __init__(self):
        super(VoiceTypingApp, self).__init__(
            "🎤",  # Menu bar icon
            quit_button=None
        )
        
        # State
        self.state = "idle"  # idle, recording, processing
        self.hotkey_pressed = False
        self.listener = None
        self.recording_hotkey = False
        self.recorded_modifiers = set()
        
        # Managers
        self.config = ConfigManager()
        self.stats = StatsManager()
        self.history = HistoryManager()
        
        # Components
        self.recorder = AudioRecorder()
        self.transcriber = TranscriptionEngine()
        self.injector = TextInjector()
        
        # Build menu
        self._build_menu()
        
        # Start hotkey listener
        self.start_hotkey_listener()
        
        # Pre-load model
        self._show_loading = True
        threading.Thread(target=self._preload_model, daemon=True).start()
    
    def _build_menu(self):
        """Build the menu structure like Whryte"""
        # Status item at top
        self.status_item = rumps.MenuItem("Status: Idle")
        self.status_item.set_callback(None)
        
        # Hotkeys submenu with record option
        self.hotkeys_menu = rumps.MenuItem("⌨️ Hotkeys")
        self._build_hotkeys_menu()
        
        # History submenu
        self.history_menu = rumps.MenuItem("🕐 History")
        self._update_history_menu()
        
        # Statistics section - INLINE (not submenu)
        self.stats_header = rumps.MenuItem("─────── STATISTICS ───────")
        self.stats_header.set_callback(None)
        
        self.stats_today = rumps.MenuItem(f"📊 Today's Words                    {self.stats.get_today_words()}")
        self.stats_today.set_callback(None)
        self.stats_total = rumps.MenuItem(f"📄 Total Words                        {self.stats.get_total_words()}")
        self.stats_total.set_callback(None)
        self.stats_time = rumps.MenuItem(f"⏱️ Time Saved                         {self.stats.get_time_saved_minutes()} min")
        self.stats_time.set_callback(None)
        
        # Build full menu
        self.menu = [
            self.status_item,
            None,
            self.hotkeys_menu,
            self.history_menu,
            None,
            self.stats_header,
            self.stats_today,
            self.stats_total,
            self.stats_time,
            None,
            rumps.MenuItem("❓ How to Use", callback=self.show_help),
            None,
            rumps.MenuItem("🔄 Restart", callback=self.restart_app),
            rumps.MenuItem("⏻ Quit", callback=self.quit_app),
        ]
    
    def _build_hotkeys_menu(self):
        """Build hotkeys submenu with presets and custom option"""
        # Clear existing
        if hasattr(self, '_hotkeys_initialized') and self._hotkeys_initialized:
            for key in list(self.hotkeys_menu.keys()):
                del self.hotkeys_menu[key]
        self._hotkeys_initialized = True
        
        current = self.config.get_hotkey_name()
        
        # Current hotkey display
        current_label = rumps.MenuItem(f"Current: {self.config.get_hotkey_label()}")
        current_label.set_callback(None)
        self.hotkeys_menu.add(current_label)
        self.hotkeys_menu.add(None)
        
        # Preset options
        for name, label in self.config.get_available_presets():
            item = rumps.MenuItem(label, callback=lambda _, n=name: self._set_preset_hotkey(n))
            if name == current and current != "custom":
                item.state = 1
            self.hotkeys_menu.add(item)
        
        self.hotkeys_menu.add(None)
        
        # Custom hotkey option
        self.hotkeys_menu.add(rumps.MenuItem("🎯 Record Custom Hotkey...", callback=self._start_record_hotkey))
    
    def _set_preset_hotkey(self, preset_name):
        """Set a preset hotkey"""
        self.config.set_hotkey_preset(preset_name)
        self._build_hotkeys_menu()
        self.start_hotkey_listener()
        rumps.notification("Oropo", "Hotkey Changed", f"Now using: {self.config.get_hotkey_label()}")
    
    def _start_record_hotkey(self, _):
        """Start recording a custom hotkey"""
        self.recording_hotkey = True
        self.recorded_modifiers = set()
        
        rumps.alert(
            title="Record Custom Hotkey",
            message=(
                "Press and hold the modifier keys you want to use as your hotkey.\n\n"
                "Examples:\n"
                "• Control + Option\n"
                "• Command + Shift\n"
                "• Control + Shift\n\n"
                "Press OK, then press your key combination within 5 seconds..."
            )
        )
        
        # Start recording listener
        threading.Thread(target=self._record_hotkey_combo, daemon=True).start()
    
    def _record_hotkey_combo(self):
        """Record the user's key combination"""
        self.recorded_modifiers = set()
        
        def on_press(key):
            if key in MODIFIER_KEYS:
                self.recorded_modifiers.add(key)
        
        def on_release(key):
            pass
        
        # Listen for 5 seconds
        temp_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        temp_listener.start()
        time.sleep(5)
        temp_listener.stop()
        
        self.recording_hotkey = False
        
        if self.recorded_modifiers:
            # Convert to labels
            key_labels = [MODIFIER_KEYS[k] for k in self.recorded_modifiers if k in MODIFIER_KEYS]
            # Remove duplicates (left/right variants)
            unique_labels = list(dict.fromkeys(key_labels))
            
            if unique_labels:
                self.config.set_custom_hotkey(unique_labels)
                self._build_hotkeys_menu()
                self.start_hotkey_listener()
                rumps.notification("Oropo", "Custom Hotkey Set!", " + ".join(unique_labels))
            else:
                rumps.notification("Oropo", "No Keys Detected", "Please try again")
        else:
            rumps.notification("Oropo", "No Keys Detected", "Please try again")
    
    def _update_stats_display(self):
        """Update statistics in menu"""
        self.stats_today.title = f"📊 Today's Words                    {self.stats.get_today_words()}"
        self.stats_total.title = f"📄 Total Words                        {self.stats.get_total_words()}"
        self.stats_time.title = f"⏱️ Time Saved                         {self.stats.get_time_saved_minutes()} min"
    
    def _update_history_menu(self):
        """Update history submenu"""
        if hasattr(self, '_history_initialized') and self._history_initialized:
            for key in list(self.history_menu.keys()):
                del self.history_menu[key]
        self._history_initialized = True
        
        history = self.history.get_formatted_history()
        if not history:
            empty_item = rumps.MenuItem("No history yet")
            empty_item.set_callback(None)
            self.history_menu.add(empty_item)
        else:
            for i, entry in enumerate(history):
                item_menu = rumps.MenuItem(entry["display"])
                
                paste_item = rumps.MenuItem(
                    "📋 Paste at Cursor",
                    callback=lambda _, text=entry["full_text"]: self._paste_history_item(text)
                )
                item_menu.add(paste_item)
                
                copy_item = rumps.MenuItem(
                    "📄 Copy to Clipboard",
                    callback=lambda _, text=entry["full_text"]: self._copy_history_item(text)
                )
                item_menu.add(copy_item)
                
                delete_item = rumps.MenuItem(
                    "🗑️ Delete",
                    callback=lambda _, idx=i: self._delete_history_item(idx)
                )
                item_menu.add(delete_item)
                
                self.history_menu.add(item_menu)
        
        self.history_menu.add(None)
        self.history_menu.add(rumps.MenuItem("Clear All History", callback=self._clear_history))
    
    def _paste_history_item(self, text):
        """Paste a history item at cursor"""
        success = self.injector.paste_text(text)
        if success:
            rumps.notification("Oropo", "Pasted!", text[:30] + "..." if len(text) > 30 else text)
    
    def _copy_history_item(self, text):
        """Copy a history item to clipboard"""
        import pyperclip
        pyperclip.copy(text)
        rumps.notification("Oropo", "Copied!", text[:50] + "..." if len(text) > 50 else text)
    
    def _delete_history_item(self, index):
        """Delete a history item"""
        self.history.delete_entry(index)
        self._update_history_menu()
    
    def _clear_history(self, _):
        """Clear all history"""
        self.history.clear_history()
        self._update_history_menu()
        rumps.notification("Oropo", "History cleared", "")
    
    def _preload_model(self):
        """Pre-load the Whisper model on startup"""
        if self._show_loading:
            self.update_status("Loading model...")
        
        try:
            self.transcriber._ensure_model()
        except Exception:
            pass
        
        self.update_status("Ready")
        self._show_loading = False
    
    def update_status(self, status):
        """Update the status display"""
        self.status_item.title = f"Status: {status}"
        
        if "Recording" in status:
            self.title = "🔴"
        elif "Processing" in status:
            self.title = "⏳"
        else:
            self.title = "🎤"
    
    def start_hotkey_listener(self):
        """Start listening for the configured hotkey"""
        if self.listener:
            try:
                self.listener.stop()
            except Exception:
                pass
        
        hotkey_info = self.config.get_hotkey()
        target_keys = hotkey_info.get("keys", [hotkey_info["key"]])
        self.pressed_keys = set()
        
        def on_press(key):
            if self.recording_hotkey:
                return
            
            self.pressed_keys.add(key)
            
            # Check if all target keys are pressed
            all_pressed = all(
                any(pk == tk or (hasattr(pk, 'name') and hasattr(tk, 'name') and 
                    pk.name.replace('_l', '').replace('_r', '') == tk.name.replace('_l', '').replace('_r', ''))
                    for pk in self.pressed_keys)
                for tk in target_keys
            )
            
            if all_pressed and not self.hotkey_pressed:
                self.hotkey_pressed = True
                self.on_hotkey_press()
        
        def on_release(key):
            if self.recording_hotkey:
                return
            
            self.pressed_keys.discard(key)
            
            # If any target key is released, stop recording
            if self.hotkey_pressed:
                self.hotkey_pressed = False
                self.on_hotkey_release()
        
        self.listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.listener.start()
    
    def on_hotkey_press(self):
        """Called when hotkey is pressed - start recording"""
        if self.state != "idle":
            return
        
        self.state = "recording"
        self.update_status("Recording...")
        
        try:
            self.recorder.start_recording()
        except Exception as e:
            self.update_status(f"Error: {e}")
            self.state = "idle"
    
    def on_hotkey_release(self):
        """Called when hotkey is released - process recording"""
        if self.state != "recording":
            return
        
        self.state = "processing"
        self.update_status("Processing...")
        
        threading.Thread(target=self._process_recording, daemon=True).start()
    
    def _process_recording(self):
        """Process the recording"""
        try:
            audio_file = self.recorder.stop_recording()
            
            if not audio_file:
                self.update_status("No audio")
                time.sleep(1)
                self.update_status("Ready")
                self.state = "idle"
                return
            
            text = self.transcriber.transcribe(audio_file)
            
            if not text:
                self.update_status("No speech")
                time.sleep(1)
                self.update_status("Ready")
                self.state = "idle"
                return
            
            # Record stats and history
            self.stats.record_transcription(text)
            self.history.add_entry(text)
            self._update_stats_display()
            self._update_history_menu()
            
            # Paste text
            success = self.injector.paste_text(text)
            
            if success:
                self.update_status("Done!")
            else:
                self.update_status("Paste failed")
            
            time.sleep(0.5)
            self.update_status("Ready")
            
        except Exception as e:
            self.update_status(f"Error: {str(e)[:20]}")
            time.sleep(2)
            self.update_status("Ready")
        
        finally:
            self.state = "idle"
    
    def show_help(self, _):
        """Show usage instructions"""
        hotkey_label = self.config.get_hotkey_label()
        rumps.alert(
            title="How to Use Oropo",
            message=(
                f"1. Click where you want to type\n\n"
                f"2. Press and hold: {hotkey_label}\n\n"
                f"3. Speak naturally\n\n"
                f"4. Release - your text appears!\n\n"
                f"Icons:\n"
                f"🎤 = Ready\n"
                f"🔴 = Recording\n"
                f"⏳ = Processing"
            )
        )
    
    def restart_app(self, _):
        """Restart the application"""
        import os
        import sys
        os.execv(sys.executable, ['python'] + sys.argv)
    
    def quit_app(self, _):
        """Clean up and quit"""
        if self.listener:
            self.listener.stop()
        self.recorder.cleanup()
        rumps.quit_application()


if __name__ == "__main__":
    print("Starting Oropo Voice Typing...")
    print("Look for the 🎤 icon in your menu bar")
    
    app = VoiceTypingApp()
    app.run()
