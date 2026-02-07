"""
Voice Typing Assistant - Main Menu Bar Application
A macOS menu bar app for voice-to-text typing
"""

import rumps
import threading
import time
from pynput import keyboard

from audio_recorder import AudioRecorder
from transcription_engine import TranscriptionEngine
from text_injector import TextInjector


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
        
        # Components
        self.recorder = AudioRecorder()
        self.transcriber = TranscriptionEngine()
        self.injector = TextInjector()
        
        # Menu items
        self.status_item = rumps.MenuItem("Status: Idle")
        self.status_item.set_callback(None)  # Not clickable
        
        self.menu = [
            self.status_item,
            None,  # Separator
            rumps.MenuItem("How to Use", callback=self.show_help),
            None,  # Separator
            rumps.MenuItem("Quit", callback=self.quit_app),
        ]
        
        # Start hotkey listener
        self.start_hotkey_listener()
        
        # Pre-load model notification
        self._show_loading = True
        threading.Thread(target=self._preload_model, daemon=True).start()
    
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
        """Start listening for the global hotkey (Right Command)"""
        
        def on_press(key):
            # Check for Right Command key
            if key == keyboard.Key.cmd_r and not self.hotkey_pressed:
                self.hotkey_pressed = True
                self.on_hotkey_press()
        
        def on_release(key):
            if key == keyboard.Key.cmd_r and self.hotkey_pressed:
                self.hotkey_pressed = False
                self.on_hotkey_release()
        
        # Start listener in background
        listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        )
        listener.start()
    
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
        rumps.alert(
            title="How to Use Voice Typing",
            message=(
                "1. Click where you want to type\n\n"
                "2. Press and hold the RIGHT COMMAND key\n\n"
                "3. Speak naturally\n\n"
                "4. Release the key - your text will appear!\n\n"
                "The icon shows:\n"
                "🎤 = Ready\n"
                "🔴 = Recording\n"
                "⏳ = Processing"
            )
        )
    
    def quit_app(self, _):
        """Clean up and quit"""
        self.recorder.cleanup()
        rumps.quit_application()


if __name__ == "__main__":
    print("Starting Voice Typing Assistant...")
    print("Look for the 🎤 icon in your menu bar")
    print("Press Right Command to record, release to transcribe")
    
    app = VoiceTypingApp()
    app.run()
