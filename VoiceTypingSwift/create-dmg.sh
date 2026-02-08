#!/bin/bash

# Voice Typing Swift - Create DMG Script
# Creates a distributable DMG installer

set -e

echo "================================================"
echo "  Voice Typing Swift - Create DMG"
echo "================================================"
echo ""

cd "$(dirname "$0")"

APP_NAME="Voice Typing.app"
DMG_NAME="Voice Typing.dmg"
VOLUME_NAME="Voice Typing"

# First, build the app if not already built
if [ ! -d "$APP_NAME" ]; then
    echo "📦 App not found, building first..."
    ./build.sh
fi

echo ""
echo "📀 Creating DMG..."

# Remove old DMG if exists
rm -f "$DMG_NAME"

# Create a temporary folder for DMG contents
TEMP_DMG_DIR=$(mktemp -d)
cp -R "$APP_NAME" "$TEMP_DMG_DIR/"

# Create symlink to Applications folder
ln -s /Applications "$TEMP_DMG_DIR/Applications"

# Create the DMG
hdiutil create -volname "$VOLUME_NAME" \
    -srcfolder "$TEMP_DMG_DIR" \
    -ov -format UDZO \
    "$DMG_NAME"

# Clean up
rm -rf "$TEMP_DMG_DIR"

# Remove quarantine attribute
xattr -cr "$DMG_NAME" 2>/dev/null || true

echo ""
echo "✅ DMG created successfully!"
echo ""
echo "Your installer is at: $(pwd)/$DMG_NAME"
echo ""
echo "To install on any Mac:"
echo "  1. Double-click '$DMG_NAME' to mount"
echo "  2. Drag 'Voice Typing' to the Applications folder"
echo "  3. Eject the disk image"
echo "  4. Launch from Applications"
echo ""
