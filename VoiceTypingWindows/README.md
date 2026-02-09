# Voice Typing for Windows

A lightweight, offline voice typing application for Windows.

## Features
- **Offline**: Uses `faster-whisper` (runs locally).
- **Optimized**: Tuned for standard CPUs (INT8 quantization).
- **System Tray**: Runs quietly in the background.
- **Global Hotkey**: Hold **Right Ctrl** to record.

## How to Build (Cloud)
**You do not need a Windows computer to build this.**
1. Push this code to the `windows-version` branch on GitHub.
2. Go to the **Actions** tab in your GitHub repository.
3. Click on the most recent workflow run ("Build Windows App").
4. Scroll down to **Artifacts** and download `VoiceTyping-Windows`.
5. Inside is the `VoiceTyping.exe`.

## How to Build (Local)
If you have a Windows computer with Python installed:
1. Run `build.bat`.
2. The executable will appear in the `dist` folder.

## Usage
1. Run `VoiceTyping.exe`.
2. Look for the microphone icon in your System Tray (bottom right).
3. **Hold Right Ctrl** to record.
4. Release to transcribe and type.
