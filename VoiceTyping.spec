# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Voice Typing Assistant

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'rumps',
        'pynput',
        'pynput.keyboard',
        'pynput.keyboard._darwin',
        'sounddevice',
        'soundfile',
        'numpy',
        'mlx',
        'mlx.core',
        'mlx_whisper',
        'pyperclip',
        'pyautogui',
        'AppKit',
        'objc',
        'Foundation',
        'audio_recorder',
        'transcription_engine',
        'text_injector',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VoiceTyping',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VoiceTyping',
)

app = BUNDLE(
    coll,
    name='Voice Typing.app',
    icon=None,
    bundle_identifier='com.voicetyping.assistant',
    info_plist={
        'CFBundleName': 'Voice Typing',
        'CFBundleDisplayName': 'Voice Typing Assistant',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSUIElement': True,
        'NSMicrophoneUsageDescription': 'Voice Typing needs microphone access to transcribe your speech.',
        'NSAppleEventsUsageDescription': 'Voice Typing needs accessibility access to type text.',
        'LSMinimumSystemVersion': '12.0',
    },
)
