"""
History Manager Module
Saves and retrieves transcription history for Oropo voice typing app
"""

import os
import json
from datetime import datetime


class HistoryManager:
    """Manages transcription history with persistent storage"""
    
    MAX_ENTRIES = 10  # Keep last 10 transcriptions
    
    def __init__(self):
        self.history_dir = os.path.expanduser("~/.oropo")
        self.history_file = os.path.join(self.history_dir, "history.json")
        self._ensure_directory()
        self.history = self._load_history()
    
    def _ensure_directory(self):
        """Create directory if it doesn't exist"""
        if not os.path.exists(self.history_dir):
            os.makedirs(self.history_dir)
    
    def _load_history(self):
        """Load history from file or return empty list"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return []
    
    def _save_history(self):
        """Save history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception:
            pass
    
    def add_entry(self, text):
        """Add a transcription to history"""
        if not text or not text.strip():
            return
        
        entry = {
            "text": text.strip(),
            "timestamp": datetime.now().isoformat(),
            "word_count": len(text.split())
        }
        
        # Add to beginning (newest first)
        self.history.insert(0, entry)
        
        # Keep only last MAX_ENTRIES
        if len(self.history) > self.MAX_ENTRIES:
            self.history = self.history[:self.MAX_ENTRIES]
        
        self._save_history()
    
    def get_history(self):
        """Get all history entries"""
        return self.history
    
    def get_formatted_history(self):
        """Get history formatted for display"""
        formatted = []
        for entry in self.history:
            timestamp = datetime.fromisoformat(entry["timestamp"])
            time_str = timestamp.strftime("%I:%M %p")
            date_str = timestamp.strftime("%b %d")
            
            # Truncate long text for menu display
            text = entry["text"]
            if len(text) > 50:
                text = text[:47] + "..."
            
            formatted.append({
                "display": f"{time_str} - {text}",
                "full_text": entry["text"],
                "date": date_str,
                "time": time_str
            })
        return formatted
    
    def clear_history(self):
        """Clear all history"""
        self.history = []
        self._save_history()
    
    def delete_entry(self, index):
        """Delete a specific history entry by index"""
        if 0 <= index < len(self.history):
            del self.history[index]
            self._save_history()
            return True
        return False


# Test
if __name__ == "__main__":
    history = HistoryManager()
    
    # Add test entries
    history.add_entry("This is a test transcription.")
    history.add_entry("Another test entry here.")
    
    print("History entries:")
    for entry in history.get_formatted_history():
        print(f"  {entry['display']}")
