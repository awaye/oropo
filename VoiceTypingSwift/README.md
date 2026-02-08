# Voice Typing Swift Version

A native macOS menu bar app for voice-to-text typing using WhisperKit (Apple Silicon optimized).

## Features

- 🎤 **Menu bar presence** with status updates
- ⌨️ **Right Command hotkey** - hold to record, release to transcribe
- 🧠 **WhisperKit transcription** - offline, Apple Silicon optimized
- 📋 **Auto-paste** - text appears at your cursor
- 📜 **History** - last 10 transcriptions saved
- 📊 **Statistics** - track words typed and time saved

## Requirements

- macOS 13.0 or later
- Apple Silicon Mac (M1/M2/M3/M4)
- Xcode Command Line Tools (for building)

## Installation

### Option 1: Use the DMG (Recommended)

1. Double-click `Voice Typing.dmg`
2. Drag `Voice Typing` to Applications
3. Launch from Applications
4. Grant Microphone and Accessibility permissions when prompted

### Option 2: Build from Source

```bash
cd VoiceTypingSwift
./build.sh
```

Then follow the instructions printed at the end.

## Usage

1. Look for 🎤 in your menu bar
2. Click where you want to type
3. Press and hold **Right Command** key
4. Speak naturally
5. Release the key
6. Your text appears!

## Icons

| Icon | Status |
|------|--------|
| 🎤 | Ready |
| 🔴 | Recording |
| ⏳ | Processing |

## Permissions Required

On first launch, grant:
- **Microphone** access (for recording)
- **Accessibility** access (for text injection)

## Auto-Start on Login

To have Voice Typing start when your Mac boots:

1. Open **System Settings**
2. Go to **General → Login Items**
3. Click **+** and add **Voice Typing.app**

## Menu Options

- **Status** - Current app state
- **History** - View/paste/copy/delete recent transcriptions
- **Statistics** - Today's words, total words, time saved
- **How to Use** - Quick help
- **Quit** - Exit the app

## Building the DMG

To create a distributable DMG:

```bash
./create-dmg.sh
```

## Project Structure

```
VoiceTypingSwift/
├── Package.swift           # Swift Package dependencies
├── Sources/
│   ├── main.swift          # App entry point
│   ├── AppDelegate.swift   # Menu bar & hotkey handling
│   ├── AudioRecorder.swift # Microphone capture
│   ├── TranscriptionEngine.swift # WhisperKit wrapper
│   ├── TextInjector.swift  # Clipboard + paste
│   ├── StatsManager.swift  # Usage statistics
│   ├── HistoryManager.swift # Recent transcriptions
│   └── Info.plist          # App permissions
├── build.sh                # Build to .app
└── create-dmg.sh           # Package as DMG
```
