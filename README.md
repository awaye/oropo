# 🎤 Voice Typing Assistant for macOS

**Press a key, speak, and your words appear anywhere on your Mac.** Works completely offline using AI transcription on Apple Silicon.

---

## Quick Start (3 Steps)

### Step 1: Install

Open Terminal and run:

```bash
cd /Volumes/Awaye-SSD/AntiGravity/STT
chmod +x setup.sh start.sh
./setup.sh
```

This takes 2-3 minutes and downloads the AI model (~75MB).

---

### Step 2: Grant Permissions

The app needs two macOS permissions:

**Microphone Access:**
1. Open **System Settings** → **Privacy & Security** → **Microphone**
2. Turn ON the toggle for **Terminal**

**Accessibility Access:**
1. Open **System Settings** → **Privacy & Security** → **Accessibility**
2. Click the **+** button
3. Navigate to: **Applications** → **Utilities** → **Terminal**
4. Add it to the list

> ⚠️ If you skip this step, the hotkey won't work!

---

### Step 3: Start the App

```bash
./start.sh
```

Look for the **🎤** icon in your menu bar!

---

## How to Use

1. **Click** where you want to type (any app works!)
2. **Press and hold** the **Right Command** key
3. **Speak** naturally
4. **Release** the key
5. Your text appears in 1-3 seconds ✨

### Menu Bar Icons

| Icon | Meaning |
|------|---------|
| 🎤 | Ready to record |
| 🔴 | Recording... |
| ⏳ | Processing... |

---

## Troubleshooting

### "Nothing happens when I press the key"
- Make sure Terminal has **Accessibility** permission
- Try the **Right** Command key (not Left)
- Check the menu bar for the 🎤 icon

### "Microphone not working"
- Make sure Terminal has **Microphone** permission
- Check your Mac's microphone in System Settings → Sound

### "Text doesn't appear"
- Make sure Terminal has **Accessibility** permission
- Click in a text field before speaking

### To Restart the App
```bash
./start.sh
```

---

## Requirements

- macOS 12 (Monterey) or later
- Apple Silicon Mac (M1, M2, M3, or M4)
- Works completely offline after setup!

---

Made with ❤️ for distraction-free writing
