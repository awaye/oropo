#!/bin/bash

# Voice Typing Swift - Build Script
# Builds the native macOS app bundle

set -e

echo "================================================"
echo "  Voice Typing Swift - Build"
echo "================================================"
echo ""

cd "$(dirname "$0")"

echo "📦 Resolving dependencies..."
swift package resolve

echo ""
echo "🔨 Building release version..."
echo "   (This may take a few minutes on first build)"
swift build -c release

echo ""
echo "📁 Creating app bundle..."

APP_NAME="Voice Typing.app"
BUILD_DIR=".build/release"
APP_DIR="$APP_NAME/Contents"

rm -rf "$APP_NAME"
mkdir -p "$APP_DIR/MacOS"
mkdir -p "$APP_DIR/Resources"

# Copy executable
cp "$BUILD_DIR/VoiceTyping" "$APP_DIR/MacOS/VoiceTyping"

# Copy Info.plist
cp "Sources/Info.plist" "$APP_DIR/Info.plist"

# Copy Resources if they exist
if [ -d "Sources/Resources" ]; then
    cp -R "Sources/Resources/"* "$APP_DIR/Resources/" 2>/dev/null || true
fi

# Remove quarantine attribute
xattr -cr "$APP_NAME" 2>/dev/null || true

echo ""
echo "✅ Build complete!"
echo ""
echo "Your app is at: $(pwd)/$APP_NAME"
echo ""
echo "To install:"
echo "  1. Drag '$APP_NAME' to your Applications folder"
echo "  2. Double-click to launch"
echo "  3. Grant Microphone and Accessibility permissions when prompted"
echo ""
echo "To add to Login Items (auto-start on boot):"
echo "  System Settings → General → Login Items → Add '$APP_NAME'"
echo ""
