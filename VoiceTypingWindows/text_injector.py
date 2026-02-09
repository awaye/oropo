"""
Text Injector Module (Windows)
Pastes text using Ctrl+V
"""

import time
import pyperclip
import keyboard # Windows-friendly keyboard usage if needed, or pyautogui

# We'll use pyautogui for hotkeys as it's cross-platform standard for this
import pyautogui

class TextInjector:
    """Injects text at the cursor position using clipboard paste"""
    
    def __init__(self):
        pyautogui.PAUSE = 0.05
        pyautogui.FAILSAFE = True
    
    def paste_text(self, text):
        """Paste text using Clipboard + Ctrl+V"""
        if not text or not text.strip():
            return False
            
        try:
            # 1. Save clipboard (optional, sometimes flaky on Windows, skipping for robustness)
            # original = pyperclip.paste()
            
            # 2. Put text on clipboard
            pyperclip.copy(text)
            
            # 3. Wait a tiny bit for clipboard update
            time.sleep(0.1)
            
            # 4. Press Ctrl+V
            # Using pyautogui to simulate
            pyautogui.hotkey('ctrl', 'v')
            
            return True
            
        except Exception as e:
            print(f"Injection error: {e}")
            return False
