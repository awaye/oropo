#!/bin/bash

# Voice Typing Assistant - Easy Install Script
# This creates a clickable app that runs the Python version

echo "================================================"
echo "  Voice Typing Assistant - Creating App Shortcut"
echo "================================================"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create a simple AppleScript app that launches the Python version
APP_NAME="Voice Typing.app"
APP_PATH="$HOME/Applications/$APP_NAME"

# Create Applications folder if needed
mkdir -p "$HOME/Applications"

# Remove old version if exists
rm -rf "$APP_PATH"

# Create the app bundle
mkdir -p "$APP_PATH/Contents/MacOS"
mkdir -p "$APP_PATH/Contents/Resources"

# Create the launcher script
cat > "$APP_PATH/Contents/MacOS/Voice Typing" << 'LAUNCHER'
#!/bin/bash
cd /Volumes/Awaye-SSD/AntiGravity/STT
source venv/bin/activate
python3 app.py
LAUNCHER

chmod +x "$APP_PATH/Contents/MacOS/Voice Typing"

# Create Info.plist
cat > "$APP_PATH/Contents/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Voice Typing</string>
    <key>CFBundleIdentifier</key>
    <string>com.voicetyping.assistant</string>
    <key>CFBundleName</key>
    <string>Voice Typing</string>
    <key>CFBundleDisplayName</key>
    <string>Voice Typing</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>LSUIElement</key>
    <true/>
    <key>NSMicrophoneUsageDescription</key>
    <string>Voice Typing needs microphone access to transcribe your speech.</string>
</dict>
</plist>
PLIST

echo "✅ App created at: $APP_PATH"
echo ""
echo "You can now:"
echo "1. Find 'Voice Typing' in ~/Applications"
echo "2. Drag it to your Dock for easy access"
echo "3. Double-click to launch anytime!"
echo ""
echo "Remember to grant permissions:"
echo "- System Settings → Privacy → Microphone → Enable Terminal"
echo "- System Settings → Privacy → Accessibility → Add Terminal"
echo ""

# Open the Applications folder
open "$HOME/Applications"
