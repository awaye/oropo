@echo off
echo Voice Typing Windows Builder
echo ============================
echo.
echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller
echo.
echo Building EXE...
pyinstaller --onefile --noconsole --name "VoiceTyping" --hidden-import=faster_whisper --hidden-import=pystray main.py
echo.
echo Build complete! Check the 'dist' folder.
pause
