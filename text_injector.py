"""
Text Injector Module
Pastes transcribed text at the current cursor position in any application
"""

import time
import pyperclip
import pyautogui


class TextInjector:
    """Injects text at the cursor position using clipboard paste"""
    
    def __init__(self):
        # Configure pyautogui for macOS
        pyautogui.PAUSE = 0.05  # Small delay between actions
        pyautogui.FAILSAFE = True
    
    def paste_text(self, text):
        """
        Paste text at the current cursor position
        
        Uses clipboard + Cmd+V for universal compatibility across all apps
        
        Args:
            text: The text to paste
            
        Returns:
            True if successful, False otherwise
        """
        if not text or not text.strip():
            return False
        
        try:
            # Save current clipboard contents
            try:
                original_clipboard = pyperclip.paste()
            except Exception:
                original_clipboard = ""
            
            # Copy new text to clipboard
            pyperclip.copy(text)
            
            # IMPORTANT: Wait for user to fully release their hotkey
            # This prevents the "V" appearing when Command is still held
            time.sleep(0.15)
            
            # Simulate Cmd+V to paste
            pyautogui.hotkey('command', 'v')
            
            # Wait for paste to complete
            time.sleep(0.1)
            
            # Restore original clipboard after a short delay
            # (in case user wants to paste again immediately)
            def restore_clipboard():
                time.sleep(0.5)
                try:
                    pyperclip.copy(original_clipboard)
                except Exception:
                    pass
            
            # Restore in background to not block
            import threading
            threading.Thread(target=restore_clipboard, daemon=True).start()
            
            return True
            
        except Exception as e:
            print(f"Text injection error: {e}")
            return False


# Test the text injector
if __name__ == "__main__":
    print("Testing Text Injector...")
    print("In 3 seconds, text will be pasted at your cursor position")
    print("Click somewhere to type first!")
    
    time.sleep(3)
    
    injector = TextInjector()
    success = injector.paste_text("Hello from Voice Typing Assistant! 🎤")
    
    if success:
        print("✅ Text injection successful!")
    else:
        print("❌ Text injection failed")
