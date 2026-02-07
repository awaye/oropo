"""
Setup script for py2app to create macOS application bundle
"""

from setuptools import setup

APP = ['app.py']
DATA_FILES = []

OPTIONS = {
    'argv_emulation': False,
    'plist': {
        'CFBundleName': 'Voice Typing',
        'CFBundleDisplayName': 'Voice Typing Assistant',
        'CFBundleIdentifier': 'com.voicetyping.assistant',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSUIElement': True,  # Hide from Dock, only menu bar
        'NSMicrophoneUsageDescription': 'Voice Typing needs microphone access to transcribe your speech.',
        'NSAppleEventsUsageDescription': 'Voice Typing needs accessibility access to type text.',
    },
    'packages': [
        'rumps',
        'pynput', 
        'sounddevice',
        'soundfile',
        'numpy',
        'mlx',
        'mlx_whisper',
        'pyperclip',
        'pyautogui',
    ],
    'includes': [
        'audio_recorder',
        'transcription_engine', 
        'text_injector',
    ],
    'iconfile': None,  # Add icon later if needed
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
