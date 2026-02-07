"""
Transcription Engine Module
Converts audio files to text using MLX-Whisper (Apple Silicon optimized)
"""

import os
import numpy as np
import soundfile as sf
import mlx_whisper


class TranscriptionEngine:
    """Transcribes audio files to text using Whisper"""
    
    def __init__(self, model_name="mlx-community/whisper-tiny"):
        """
        Initialize the transcription engine
        
        Args:
            model_name: HuggingFace model path (downloads automatically on first use)
        """
        self.model_name = model_name
        self._model_loaded = False
        
    def _ensure_model(self):
        """Ensure model is loaded (lazy loading)"""
        if not self._model_loaded:
            self._model_loaded = True
    
    def _load_audio(self, audio_path):
        """Load audio file and convert to format expected by Whisper"""
        try:
            # Read audio file using soundfile (no ffmpeg needed!)
            audio_data, sample_rate = sf.read(audio_path)
            
            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)
            
            # Resample to 16kHz if needed
            if sample_rate != 16000:
                # Simple resampling
                duration = len(audio_data) / sample_rate
                new_length = int(duration * 16000)
                indices = np.linspace(0, len(audio_data) - 1, new_length)
                audio_data = np.interp(indices, np.arange(len(audio_data)), audio_data)
            
            # Convert to float32 and normalize
            audio_data = audio_data.astype(np.float32)
            if audio_data.max() > 1.0:
                audio_data = audio_data / 32768.0  # Normalize int16 to float
                
            return audio_data
            
        except Exception as e:
            print(f"Error loading audio: {e}")
            return None
    
    def transcribe(self, audio_path):
        """
        Transcribe an audio file to text
        
        Args:
            audio_path: Path to the audio file (WAV format, 16kHz)
            
        Returns:
            Transcribed text string, or empty string on failure
        """
        if not audio_path or not os.path.exists(audio_path):
            return ""
        
        try:
            self._ensure_model()
            
            # Load audio using our own loader (no ffmpeg needed)
            audio_data = self._load_audio(audio_path)
            
            if audio_data is None:
                return ""
            
            # Transcribe using MLX-Whisper with numpy array
            result = mlx_whisper.transcribe(
                audio_data,
                path_or_hf_repo=self.model_name,
                language="en",
                word_timestamps=False,
            )
            
            # Extract text from result
            text = result.get("text", "").strip()
            
            # Clean up the audio file after transcription
            try:
                os.remove(audio_path)
            except Exception:
                pass
            
            return text
            
        except Exception as e:
            print(f"Transcription error: {e}")
            # Try to clean up even on error
            try:
                os.remove(audio_path)
            except Exception:
                pass
            return ""


# Test the transcription engine
if __name__ == "__main__":
    print("Testing Transcription Engine...")
    
    engine = TranscriptionEngine()
    
    # Create a test: record and transcribe
    from audio_recorder import AudioRecorder
    import time
    
    recorder = AudioRecorder()
    
    print("\n🎤 Recording for 3 seconds - say something!")
    recorder.start_recording()
    time.sleep(3)
    audio_file = recorder.stop_recording()
    
    if audio_file:
        print("🧠 Transcribing...")
        text = engine.transcribe(audio_file)
        if text:
            print(f"✅ Transcription: {text}")
        else:
            print("❌ No speech detected")
    else:
        print("❌ No audio recorded")
    
    recorder.cleanup()
