"""
Transcription Engine Module (Windows/Faster-Whisper)
Uses faster-whisper (CTranslate2) for efficient CPU/GPU inference.
"""

import os
import time
from faster_whisper import WhisperModel

class TranscriptionEngine:
    """Transcribes audio files to text using Faster-Whisper"""
    
    def __init__(self, model_size="base", device="cpu", compute_type="int8"):
        """
        Initialize the transcription engine
        
        Args:
            model_size: "tiny", "base", "small", "medium", "large-v3"
            device: "cpu" or "cuda" (for NVIDIA GPUs)
            compute_type: "int8" (CPU), "float16" (GPU)
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None
        
        # Auto-detect CUDA
        try:
            import torch
            if torch.cuda.is_available():
                self.device = "cuda"
                self.compute_type = "float16"
                print("🚀 NVIDIA GPU detected! Using CUDA/float16")
        except ImportError:
            pass # torch might not be installed if we only installed faster-whisper standalone
            
    def _ensure_model(self):
        """Ensure model is loaded (lazy loading)"""
        if self.model is None:
            print(f"Loading {self.model_size} model on {self.device}...")
            # This triggers download if not cached
            self.model = WhisperModel(
                self.model_size, 
                device=self.device, 
                compute_type=self.compute_type,
                cpu_threads=4 # Optimize for mainstream CPUs
            )
            print("Model loaded!")
    
    def transcribe(self, audio_path):
        """
        Transcribe an audio file to text
        
        Args:
            audio_path: Path to the audio file (WAV)
            
        Returns:
            Transcribed text string, or empty string on failure
        """
        if not audio_path or not os.path.exists(audio_path):
            return ""
        
        try:
            self._ensure_model()
            
            # Run transcription
            segments, info = self.model.transcribe(
                audio_path, 
                beam_size=5,
                word_timestamps=False
            )
            
            # Collect text segments
            text_segments = []
            for segment in segments:
                text_segments.append(segment.text)
                
            full_text = " ".join(text_segments).strip()
            
            # Clean up the audio file
            try:
                os.remove(audio_path)
            except Exception:
                pass
            
            return full_text
            
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""

# Test
if __name__ == "__main__":
    print("Initializing engine...")
    engine = TranscriptionEngine()
    print("Ready. (Run this file directly to test model loading)")
