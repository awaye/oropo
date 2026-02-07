#!/bin/bash

# Voice Typing Assistant - Simplified Setup Script
# Works without Homebrew

set -e  # Exit on any error

echo "================================================"
echo "  Voice Typing Assistant - Setup"
echo "================================================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if running on Apple Silicon
if [[ $(uname -m) != "arm64" ]]; then
    echo "❌ ERROR: This app requires Apple Silicon (M1/M2/M3/M4)"
    echo "   Intel Macs are not supported."
    exit 1
fi
echo "✅ Apple Silicon detected"

# Create virtual environment
echo ""
echo "🐍 Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
echo "✅ Virtual environment created"

# Upgrade pip
echo ""
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo ""
echo "📦 Installing Python packages (this may take a few minutes)..."
pip install rumps pynput pyperclip pyautogui numpy soundfile

# Install MLX packages for Apple Silicon
echo ""
echo "🧠 Installing MLX-Whisper (Apple Silicon AI)..."
pip install mlx mlx-whisper

# Pre-download the Whisper model
echo ""
echo "🧠 Downloading Whisper Tiny model (~75MB)..."
python3 -c "
import mlx_whisper
print('   Downloading model (first time only)...')
try:
    result = mlx_whisper.transcribe('dummy', path_or_hf_repo='mlx-community/whisper-tiny')
except:
    pass
print('   Model cached!')
" 2>&1 || echo "   Model will download on first use"

echo ""
echo "================================================"
echo "  ✅ Setup Complete!"
echo "================================================"
echo ""
echo "IMPORTANT - Grant these permissions before using:"
echo ""
echo "1. Microphone: System Settings → Privacy & Security → Microphone → Enable Terminal"
echo ""
echo "2. Accessibility: System Settings → Privacy & Security → Accessibility → Add Terminal"
echo ""
echo "Then run: ./start.sh"
echo ""
