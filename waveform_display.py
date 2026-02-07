"""
Waveform Display Module
Creates a floating window at the bottom of the screen showing audio waveform
"""

import threading
import numpy as np
from AppKit import (
    NSApplication, NSWindow, NSView, NSColor, NSBezierPath,
    NSWindowStyleMaskBorderless, NSFloatingWindowLevel,
    NSScreen, NSBackingStoreBuffered, NSApplicationActivationPolicyAccessory
)
from PyObjCTools import AppHelper
import objc


class WaveformView(NSView):
    """Custom view that draws audio waveform"""
    
    def initWithFrame_(self, frame):
        self = objc.super(WaveformView, self).initWithFrame_(frame)
        if self:
            self.audio_levels = [0.0] * 50  # Buffer of audio levels
            self.is_recording = False
        return self
    
    def drawRect_(self, rect):
        """Draw the waveform"""
        # Background - dark with slight transparency
        NSColor.colorWithCalibratedRed_green_blue_alpha_(0.1, 0.1, 0.15, 0.95).setFill()
        NSBezierPath.fillRect_(rect)
        
        if not self.is_recording:
            return
        
        # Draw waveform bars
        bar_count = len(self.audio_levels)
        bar_width = rect.size.width / bar_count
        max_height = rect.size.height - 10
        
        for i, level in enumerate(self.audio_levels):
            # Calculate bar height with some animation effect
            height = max(4, level * max_height)
            
            x = i * bar_width + 2
            y = (rect.size.height - height) / 2
            
            # Color gradient from cyan to purple based on level
            r = 0.2 + level * 0.5
            g = 0.8 - level * 0.3
            b = 1.0
            NSColor.colorWithCalibratedRed_green_blue_alpha_(r, g, b, 0.9).setFill()
            
            # Draw rounded bar
            bar_rect = ((x, y), (bar_width - 4, height))
            path = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(bar_rect, 2, 2)
            path.fill()
    
    def update_levels(self, new_level):
        """Update audio levels and redraw"""
        # Shift levels and add new one
        self.audio_levels = self.audio_levels[1:] + [new_level]
        self.setNeedsDisplay_(True)
    
    def set_recording(self, is_recording):
        """Set recording state"""
        self.is_recording = is_recording
        if not is_recording:
            self.audio_levels = [0.0] * 50
        self.setNeedsDisplay_(True)


class WaveformWindow:
    """Floating waveform window at bottom of screen"""
    
    def __init__(self):
        self.window = None
        self.waveform_view = None
        self.is_visible = False
        self._setup_done = False
        
    def setup(self):
        """Setup the window (must be called from main thread)"""
        if self._setup_done:
            return
            
        # Get screen dimensions
        screen = NSScreen.mainScreen()
        screen_frame = screen.frame()
        
        # Window size - thin bar at bottom
        window_width = screen_frame.size.width * 0.6
        window_height = 60
        x = (screen_frame.size.width - window_width) / 2
        y = 30  # 30 pixels from bottom
        
        # Create window
        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            ((x, y), (window_width, window_height)),
            NSWindowStyleMaskBorderless,
            NSBackingStoreBuffered,
            False
        )
        
        # Configure window
        self.window.setLevel_(NSFloatingWindowLevel)
        self.window.setOpaque_(False)
        self.window.setBackgroundColor_(NSColor.clearColor())
        self.window.setHasShadow_(True)
        self.window.setCollectionBehavior_(1 << 0)  # Can join all spaces
        
        # Create waveform view
        content_frame = ((0, 0), (window_width, window_height))
        self.waveform_view = WaveformView.alloc().initWithFrame_(content_frame)
        self.window.setContentView_(self.waveform_view)
        
        self._setup_done = True
    
    def show(self):
        """Show the waveform window"""
        if not self._setup_done:
            self.setup()
        
        if self.window and not self.is_visible:
            self.waveform_view.set_recording(True)
            self.window.orderFront_(None)
            self.is_visible = True
    
    def hide(self):
        """Hide the waveform window"""
        if self.window and self.is_visible:
            self.waveform_view.set_recording(False)
            self.window.orderOut_(None)
            self.is_visible = False
    
    def update(self, audio_level):
        """Update waveform with new audio level (0.0 to 1.0)"""
        if self.waveform_view and self.is_visible:
            self.waveform_view.update_levels(audio_level)


# Singleton instance
_waveform_window = None

def get_waveform_window():
    """Get or create the waveform window singleton"""
    global _waveform_window
    if _waveform_window is None:
        _waveform_window = WaveformWindow()
    return _waveform_window
