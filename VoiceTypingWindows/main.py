"""
Oropo Voice Typing (Windows)
System Tray Application
"""

import os
import sys
import threading
import time
import queue
from PIL import Image, ImageDraw
import pystray
from pynput import keyboard

# Local imports
from audio_recorder import AudioRecorder
from transcription_engine import TranscriptionEngine
from text_injector import TextInjector
from stats_manager import StatsManager
from history_manager import HistoryManager
from config_manager import ConfigManager

class VoiceTypingWindowsApp:
    def __init__(self):
        self.state = "idle" # idle, recording, processing
        
        # Components
        self.recorder = AudioRecorder()
        self.transcriber = TranscriptionEngine() # loads faster-whisper
        self.injector = TextInjector()
        self.stats = StatsManager()
        self.history = HistoryManager()
        self.config = ConfigManager()
        
        # Hotkey state
        self.hotkey_listener = None
        self.pressed_keys = set()
        
        # Icon
        self.icon = None
        self.menu_items = []
        
        # Preload model in thread
        threading.Thread(target=self._preload_model, daemon=True).start()

    def _create_image(self, color="white"):
        # Generate an icon image
        width = 64
        height = 64
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0)) # transparent bg
        draw = ImageDraw.Draw(image)
        
        # Draw a microphone-ish shape
        # Body
        draw.rectangle((width//2-10, 10, width//2+10, 40), fill=color)
        # Cup
        draw.arc((width//2-20, 30, width//2+20, 50), 0, 180, fill=color, width=4)
        # Stand
        draw.line((width//2, 50, width//2, 60), fill=color, width=4)
        draw.line((width//2-15, 60, width//2+15, 60), fill=color, width=4)
        
        return image

    def _preload_model(self):
        try:
            self.transcriber._ensure_model()
            self._update_icon_state() 
        except Exception as e:
            print(f"Model load error: {e}")

    def _update_icon_state(self):
        if not self.icon: return
        
        if self.state == "recording":
            self.icon.icon = self._create_image("red")
            self.icon.title = "Recording... Release to Transcribe"
        elif self.state == "processing":
            self.icon.icon = self._create_image("yellow")
            self.icon.title = "Processing..."
        else:
            self.icon.icon = self._create_image("white")
            self.icon.title = "Voice Typing: Ready (Right Ctrl)"

    def _build_menu(self):
        return pystray.Menu(
            pystray.MenuItem("Status: " + self.state.capitalize(), lambda i, item: None, enabled=False),
            pystray.MenuItem("History (Last 5)", lambda i, item: None, enabled=False),
             pystray.Menu.SEPARATOR,
            *self._get_history_items(),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Statistics", lambda i, item: None, enabled=False),
            pystray.MenuItem(lambda item: f"  Today: {self.stats.get_today_words()}", lambda i, item: None, enabled=False),
            pystray.MenuItem(lambda item: f"  Total: {self.stats.get_total_words()}", lambda i, item: None, enabled=False),
             pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self.on_quit)
        )

    def _get_history_items(self):
        history = self.history.get_formatted_history()
        items = []
        if not history:
             items.append(pystray.MenuItem("  (No history)", lambda i, item: None, enabled=False))
        else:
            # Show last 5
            for entry in history[:5]:
                text = entry['display']
                full_text = entry['full_text']
                
                def on_click(icon, item, t=full_text):
                     self.injector.paste_text(t)
                
                items.append(pystray.MenuItem(f"  {text}", on_click))
        return items

    def _refresh_menu(self):
        if self.icon:
            self.icon.menu = self._build_menu()

    # Hotkey Handling (Right Control by default)
    def start_hotkey_listener(self):
        # We use pynput.keyboard
        # Target: Right Control (common for PTT)
        
        def on_press(key):
            try:
                if key == keyboard.Key.ctrl_r:
                    if self.state == "idle":
                        self.start_recording()
            except AttributeError:
                pass
        
        def on_release(key):
            try:
                if key == keyboard.Key.ctrl_r:
                    if self.state == "recording":
                        self.stop_recording()
            except AttributeError:
                pass

        self.hotkey_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.hotkey_listener.start()

    def start_recording(self):
        self.state = "recording"
        self._update_icon_state()
        self._refresh_menu()
        
        try:
            self.recorder.start_recording()
        except:
            self.state = "idle"
            self._update_icon_state()
            self._refresh_menu()

    def stop_recording(self):
        self.state = "processing"
        self._update_icon_state()
        self._refresh_menu()
        
        # Process in thread
        threading.Thread(target=self._process_audio, daemon=True).start()

    def _process_audio(self):
        try:
            audio_file = self.recorder.stop_recording()
            if not audio_file:
                self.state = "idle"
                self._update_icon_state()
                self._refresh_menu()
                return

            text = self.transcriber.transcribe(audio_file)
            
            if text:
                self.stats.record_transcription(text)
                self.history.add_entry(text)
                
                success = self.injector.paste_text(text)
                if not success:
                    print("Paste failed")
            
        except Exception as e:
            print(f"Processing error: {e}")
        finally:
            self.state = "idle"
            self._update_icon_state()
            self._refresh_menu()

    def on_quit(self, icon, item):
        self.icon.stop()
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        sys.exit(0)

    def run(self):
        self.start_hotkey_listener()
        
        self.icon = pystray.Icon("Voice Typing", self._create_image("white"), "Voice Typing", self._build_menu())
        self.icon.run()

if __name__ == "__main__":
    app = VoiceTypingWindowsApp()
    app.run()
