"""
Audio Recorder Module
Captures microphone input and saves to temporary WAV file
Uses sounddevice (no Homebrew dependencies required)
Includes audio level calculation for waveform display
"""

import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile
import threading
import os


class AudioRecorder:
    """Records audio from the microphone using sounddevice"""
    
    def __init__(self):
        self.sample_rate = 16000  # Whisper requires 16kHz
        self.channels = 1  # Mono
        
        self.recording = []
        self.is_recording = False
        self.stream = None
        
        # Audio level callback for waveform
        self.level_callback = None
        self.current_level = 0.0
        
    def set_level_callback(self, callback):
        """Set callback for audio level updates"""
        self.level_callback = callback
        
    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio stream"""
        if self.is_recording:
            self.recording.append(indata.copy())
            
            # Calculate audio level (RMS)
            rms = np.sqrt(np.mean(indata**2))
            # Normalize to 0-1 range (amplify for visibility)
            level = min(1.0, rms * 10)
            self.current_level = level
            
            # Call the level callback if set
            if self.level_callback:
                try:
                    self.level_callback(level)
                except Exception:
                    pass
    
    def start_recording(self):
        """Start recording audio from microphone"""
        if self.is_recording:
            return
        
        self.recording = []
        self.is_recording = True
        self.current_level = 0.0
        
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=self._audio_callback
            )
            self.stream.start()
            
        except Exception as e:
            self.is_recording = False
            raise Exception(f"Could not start recording: {e}")
    
    def stop_recording(self):
        """Stop recording and save to temporary WAV file"""
        if not self.is_recording:
            return None
        
        self.is_recording = False
        self.current_level = 0.0
        
        # Stop stream
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None
        
        # Check if we have any audio
        if not self.recording:
            return None
        
        # Combine all recorded chunks
        audio_data = np.concatenate(self.recording, axis=0)
        
        # Check minimum duration (0.5 seconds)
        duration = len(audio_data) / self.sample_rate
        if duration < 0.5:
            return None
        
        # Save to temporary file
        try:
            temp_file = tempfile.NamedTemporaryFile(
                suffix='.wav',
                delete=False
            )
            temp_path = temp_file.name
            temp_file.close()
            
            sf.write(temp_path, audio_data, self.sample_rate)
            
            return temp_path
            
        except Exception as e:
            print(f"Error saving audio: {e}")
            return None
    
    def cleanup(self):
        """Cleanup audio resources"""
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None


# Test the recorder
if __name__ == "__main__":
    import time
    
    print("Testing Audio Recorder with level display...")
    recorder = AudioRecorder()
    
    # Set up level callback
    def show_level(level):
        bars = int(level * 30)
        print(f"\r[{'█' * bars}{' ' * (30-bars)}] {level:.2f}", end='', flush=True)
    
    recorder.set_level_callback(show_level)
    
    print("Recording for 5 seconds - speak to see the levels!")
    recorder.start_recording()
    time.sleep(5)
    audio_file = recorder.stop_recording()
    print()  # New line
    
    if audio_file:
        print(f"✅ Audio saved to: {audio_file}")
        print(f"   File size: {os.path.getsize(audio_file)} bytes")
    else:
        print("❌ No audio recorded")
    
    recorder.cleanup()
