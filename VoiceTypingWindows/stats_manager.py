"""
Statistics Manager Module
Tracks usage statistics for Oropo voice typing app
"""

import os
import json
from datetime import datetime, date


class StatsManager:
    """Manages usage statistics with persistent storage"""
    
    def __init__(self):
        self.stats_dir = os.path.expanduser("~/.oropo")
        self.stats_file = os.path.join(self.stats_dir, "stats.json")
        self._ensure_directory()
        self.stats = self._load_stats()
    
    def _ensure_directory(self):
        """Create config directory if it doesn't exist"""
        if not os.path.exists(self.stats_dir):
            os.makedirs(self.stats_dir)
    
    def _load_stats(self):
        """Load stats from file or return defaults"""
        default_stats = {
            "total_words": 0,
            "total_characters": 0,
            "total_transcriptions": 0,
            "daily_stats": {}
        }
        
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        
        return default_stats
    
    def _save_stats(self):
        """Save stats to file"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception:
            pass
    
    def record_transcription(self, text):
        """Record a transcription's statistics"""
        if not text:
            return
        
        words = len(text.split())
        chars = len(text)
        today = date.today().isoformat()
        
        # Update totals
        self.stats["total_words"] += words
        self.stats["total_characters"] += chars
        self.stats["total_transcriptions"] += 1
        
        # Update daily stats
        if today not in self.stats["daily_stats"]:
            self.stats["daily_stats"][today] = {"words": 0, "chars": 0, "count": 0}
        
        self.stats["daily_stats"][today]["words"] += words
        self.stats["daily_stats"][today]["chars"] += chars
        self.stats["daily_stats"][today]["count"] += 1
        
        self._save_stats()
    
    def get_today_words(self):
        """Get word count for today"""
        today = date.today().isoformat()
        return self.stats.get("daily_stats", {}).get(today, {}).get("words", 0)
    
    def get_total_words(self):
        """Get total word count"""
        return self.stats.get("total_words", 0)
    
    def get_time_saved_minutes(self):
        """Estimate time saved (assumes 3x faster than typing)"""
        # Average typing speed: 40 words/minute
        # Speaking speed: ~150 words/minute
        # Time saved = words / 40 - words / 150 ≈ words / 55
        total_words = self.get_total_words()
        return round(total_words / 55, 1)


# Test
if __name__ == "__main__":
    stats = StatsManager()
    print(f"Today's words: {stats.get_today_words()}")
    print(f"Total words: {stats.get_total_words()}")
    print(f"Time saved: {stats.get_time_saved_minutes()} min")
    
    # Test recording
    stats.record_transcription("This is a test transcription with some words.")
    print(f"After test - Today's words: {stats.get_today_words()}")
