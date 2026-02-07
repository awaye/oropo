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
from config_manager import ConfigManager, HOTKEY_OPTIONS
from history_manager import HistoryManager


class VoiceTypingApp(rumps.App):
    """Main menu bar application for voice typing"""
    
    def __init__(self):
        super(VoiceTypingApp, self).__init__(
            "🎤",  # Menu bar icon
            quit_button=None  # We'll add our own
        )
        
        # State
        self.state = "idle"  # idle, recording, processing
        self.hotkey_pressed = False
        self.listener = None
        
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
        
        # Pre-load model notification
        self._show_loading = True
        threading.Thread(target=self._preload_model, daemon=True).start()
    
    def _build_menu(self):
        """Build the menu structure"""
        # Status item
        self.status_item = rumps.MenuItem("Status: Idle")
        self.status_item.set_callback(None)
        
        # Statistics items
        self.stats_today = rumps.MenuItem(f"Today's Words: {self.stats.get_today_words()}")
        self.stats_today.set_callback(None)
        self.stats_total = rumps.MenuItem(f"Total Words: {self.stats.get_total_words()}")
        self.stats_total.set_callback(None)
        self.stats_time = rumps.MenuItem(f"Time Saved: {self.stats.get_time_saved_minutes()} min")
        self.stats_time.set_callback(None)
        
        # Hotkeys submenu
        self.hotkeys_menu = rumps.MenuItem("Hotkeys")
        current_hotkey = self.config.get_hotkey_name()
        for name, label in self.config.get_available_hotkeys():
            item = rumps.MenuItem(label, callback=lambda _, n=name: self._set_hotkey(n))
            if name == current_hotkey:
                item.state = 1  # Checkmark
            self.hotkeys_menu.add(item)
        
        # History submenu
        self.history_menu = rumps.MenuItem("History")
        self._update_history_menu()
        
        # Build full menu
        self.menu = [
            self.status_item,
            None,  # Separator
            ("Statistics", [self.stats_today, self.stats_total, self.stats_time]),
            self.hotkeys_menu,
            self.history_menu,
            None,  # Separator
            rumps.MenuItem("How to Use", callback=self.show_help),
            None,  # Separator
            rumps.MenuItem("Quit", callback=self.quit_app),
        ]
    
    def _update_stats_display(self):
        """Update statistics in menu"""
        self.stats_today.title = f"Today's Words: {self.stats.get_today_words()}"
        self.stats_total.title = f"Total Words: {self.stats.get_total_words()}"
        self.stats_time.title = f"Time Saved: {self.stats.get_time_saved_minutes()} min"
    
    def _update_history_menu(self):
        """Update history submenu"""
        # Only clear if menu has been initialized
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
            for entry in history[:10]:  # Show last 10 in menu
                item = rumps.MenuItem(
                    entry["display"],
                    callback=lambda _, text=entry["full_text"]: self._copy_history_item(text)
                )
                self.history_menu.add(item)
            
            if len(history) > 10:
                self.history_menu.add(None)  # Separator
                more_item = rumps.MenuItem(f"({len(history)} total entries)")
                more_item.set_callback(None)
                self.history_menu.add(more_item)
        
        self.history_menu.add(None)  # Separator
        self.history_menu.add(rumps.MenuItem("Clear History", callback=self._clear_history))
    
    def _copy_history_item(self, text):
        """Copy a history item to clipboard"""
        import pyperclip
        pyperclip.copy(text)
        rumps.notification("Oropo", "Copied to clipboard", text[:50] + "..." if len(text) > 50 else text)
    
    def _clear_history(self, _):
        """Clear all history"""
        self.history.clear_history()
        self._update_history_menu()
        rumps.notification("Oropo", "History cleared", "")
    
    def _set_hotkey(self, hotkey_name):
        """Set new hotkey and restart listener"""
        self.config.set_hotkey(hotkey_name)
        
        # Update menu checkmarks
        for item in self.hotkeys_menu.values():
            if hasattr(item, 'title'):
                hotkey_info = HOTKEY_OPTIONS.get(hotkey_name, {})
                item.state = 1 if item.title == hotkey_info.get("label") else 0
        
        # Restart listener with new hotkey
        self.start_hotkey_listener()
        
        hotkey_label = HOTKEY_OPTIONS[hotkey_name]["label"]
        rumps.notification("Oropo", "Hotkey changed", f"Now using: {hotkey_label}")
    
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
        
        # Update icon based on state
        if "Recording" in status:
            self.title = "🔴"  # Red circle when recording
        elif "Processing" in status:
            self.title = "⏳"  # Hourglass when processing
        else:
            self.title = "🎤"  # Microphone when idle
    
    def start_hotkey_listener(self):
        """Start listening for the configured hotkey"""
        # Stop existing listener if any
        if self.listener:
            try:
                self.listener.stop()
            except Exception:
                pass
        
        hotkey_config = self.config.get_hotkey()
        target_key = hotkey_config["key"]
        
        def on_press(key):
            if key == target_key and not self.hotkey_pressed:
                self.hotkey_pressed = True
                self.on_hotkey_press()
        
        def on_release(key):
            if key == target_key and self.hotkey_pressed:
                self.hotkey_pressed = False
                self.on_hotkey_release()
        
        # Start listener in background
        self.listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        )
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
        
        # Process in background thread
        threading.Thread(target=self._process_recording, daemon=True).start()
    
    def _process_recording(self):
        """Process the recording (runs in background thread)"""
        try:
            # Stop recording and get audio file
            audio_file = self.recorder.stop_recording()
            
            if not audio_file:
                self.update_status("No audio detected")
                time.sleep(1)
                self.update_status("Ready")
                self.state = "idle"
                return
            
            # Transcribe
            text = self.transcriber.transcribe(audio_file)
            
            if not text:
                self.update_status("No speech detected")
                time.sleep(1)
                self.update_status("Ready")
                self.state = "idle"
                return
            
            # Record stats and history
            self.stats.record_transcription(text)
            self.history.add_entry(text)
            self._update_stats_display()
            self._update_history_menu()
            
            # Inject text at cursor
            success = self.injector.paste_text(text)
            
            if success:
                self.update_status("Done!")
            else:
                self.update_status("Paste failed")
            
            time.sleep(0.5)
            self.update_status("Ready")
            
        except Exception as e:
            self.update_status(f"Error: {str(e)[:30]}")
            time.sleep(2)
            self.update_status("Ready")
        
        finally:
            self.state = "idle"
    
    def show_help(self, _):
        """Show usage instructions"""
        hotkey_label = self.config.get_hotkey()["label"]
        rumps.alert(
            title="How to Use Oropo",
            message=(
                f"1. Click where you want to type\n\n"
                f"2. Press and hold {hotkey_label}\n\n"
                f"3. Speak naturally\n\n"
                f"4. Release the key - your text will appear!\n\n"
                f"The icon shows:\n"
                f"🎤 = Ready\n"
                f"🔴 = Recording\n"
                f"⏳ = Processing"
            )
        )
    
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
