import Cocoa

/// Handles text injection via clipboard and simulated Cmd+V
class TextInjector {
    
    /// Paste text at the current cursor position
    /// - Returns: true if successful
    func pasteText(_ text: String) -> Bool {
        let pasteboard = NSPasteboard.general
        
        // Save current clipboard contents
        let oldContents = pasteboard.string(forType: .string)
        
        // Set new text to clipboard
        pasteboard.clearContents()
        pasteboard.setString(text, forType: .string)
        
        // Small delay to ensure clipboard is ready
        usleep(50000)  // 50ms
        
        // Simulate Cmd+V
        let success = simulatePaste()
        
        // Restore original clipboard after a delay
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            if let old = oldContents {
                pasteboard.clearContents()
                pasteboard.setString(old, forType: .string)
            }
        }
        
        return success
    }
    
    /// Copy text to clipboard without pasting
    func copyToClipboard(_ text: String) {
        let pasteboard = NSPasteboard.general
        pasteboard.clearContents()
        pasteboard.setString(text, forType: .string)
    }
    
    // MARK: - Private
    
    private func simulatePaste() -> Bool {
        // Create event source
        guard let source = CGEventSource(stateID: .hidSystemState) else {
            return false
        }
        
        // V key = 0x09
        let vKeyCode: CGKeyCode = 0x09
        
        // Create key down event with Command modifier
        guard let keyDown = CGEvent(keyboardEventSource: source, virtualKey: vKeyCode, keyDown: true) else {
            return false
        }
        keyDown.flags = .maskCommand
        
        // Create key up event
        guard let keyUp = CGEvent(keyboardEventSource: source, virtualKey: vKeyCode, keyDown: false) else {
            return false
        }
        keyUp.flags = .maskCommand
        
        // Post events
        keyDown.post(tap: .cghidEventTap)
        keyUp.post(tap: .cghidEventTap)
        
        return true
    }
}
