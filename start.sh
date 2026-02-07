#!/bin/bash

# Voice Typing Assistant - Launcher
# Run this to start the app

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if setup has been run
if [ ! -d "venv" ]; then
    echo "❌ Setup not complete. Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment and run
source venv/bin/activate
echo "🎤 Starting Voice Typing Assistant..."
echo "   Press Right Command to record, release to transcribe"
echo "   Look for the 🎤 icon in your menu bar"
echo ""
python3 app.py
