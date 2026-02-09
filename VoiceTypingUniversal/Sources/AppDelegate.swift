import Cocoa
import Carbon

/// Main application delegate handling menu bar and hotkey for Universal App
class AppDelegate: NSObject, NSApplicationDelegate {
    
    // MARK: - Properties
    
    private var statusItem: NSStatusItem!
    private var eventMonitor: Any?
    
    // State
    private var isRecording = false
    private var isProcessing = false
    
    // Components
    private let audioRecorder = AudioRecorder()
    private let transcriptionEngine = TranscriptionEngine()
    private let textInjector = TextInjector()
    private let statsManager = StatsManager()
    private let historyManager = HistoryManager()
    
    // Menu items (need references to update them)
    private var statusMenuItem: NSMenuItem!
    private var historyMenuItem: NSMenuItem!
    private var statsTodayItem: NSMenuItem!
    private var statsTotalItem: NSMenuItem!
    private var statsTimeItem: NSMenuItem!
    
    // MARK: - App Lifecycle
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        setupStatusBar()
        setupHotkey()
        
        // Setup transcription engine callbacks
        transcriptionEngine.onStatusChange = { [weak self] status in
            self?.updateStatus(status)
        }
        
        // Initialize engine (will download model if needed)
        Task {
            await transcriptionEngine.initialize()
        }
    }
    
    func applicationWillTerminate(_ notification: Notification) {
        if let monitor = eventMonitor {
            NSEvent.removeMonitor(monitor)
        }
        audioRecorder.cleanup()
    }
    
    // MARK: - Status Bar Setup
    
    private func setupStatusBar() {
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        
        if let button = statusItem.button {
            button.title = "🎤"
        }
        
        statusItem.menu = buildMenu()
    }
    
    private func buildMenu() -> NSMenu {
        let menu = NSMenu()
        
        // Status item
        statusMenuItem = NSMenuItem(title: "Status: Initializing...", action: nil, keyEquivalent: "")
        menu.addItem(statusMenuItem)
        menu.addItem(NSMenuItem.separator())
        
        // History submenu
        historyMenuItem = NSMenuItem(title: "📜 History", action: nil, keyEquivalent: "")
        historyMenuItem.submenu = buildHistoryMenu()
        menu.addItem(historyMenuItem)
        
        menu.addItem(NSMenuItem.separator())
        
        // Statistics header
        let statsHeader = NSMenuItem(title: "───── STATISTICS ─────", action: nil, keyEquivalent: "")
        menu.addItem(statsHeader)
        
        statsTodayItem = NSMenuItem(title: "  Today's Words: \(statsManager.getTodayWords())", action: nil, keyEquivalent: "")
        menu.addItem(statsTodayItem)
        
        statsTotalItem = NSMenuItem(title: "  Total Words: \(statsManager.getTotalWords())", action: nil, keyEquivalent: "")
        menu.addItem(statsTotalItem)
        
        statsTimeItem = NSMenuItem(title: "  Time Saved: \(statsManager.getTimeSavedMinutes()) min", action: nil, keyEquivalent: "")
        menu.addItem(statsTimeItem)
        
        menu.addItem(NSMenuItem.separator())
        
        // Help
        let helpItem = NSMenuItem(title: "❓ How to Use & Setup", action: #selector(showHelp), keyEquivalent: "h")
        helpItem.target = self
        menu.addItem(helpItem)
        
        menu.addItem(NSMenuItem.separator())
        
        // Quit
        let quitItem = NSMenuItem(title: "⏻ Quit", action: #selector(quitApp), keyEquivalent: "q")
        quitItem.target = self
        menu.addItem(quitItem)
        
        return menu
    }
    
    private func buildHistoryMenu() -> NSMenu {
        let submenu = NSMenu()
        
        let history = historyManager.getFormattedHistory()
        
        if history.isEmpty {
            let emptyItem = NSMenuItem(title: "No history yet", action: nil, keyEquivalent: "")
            submenu.addItem(emptyItem)
        } else {
            for (index, entry) in history.enumerated() {
                let item = NSMenuItem(title: entry.display, action: nil, keyEquivalent: "")
                
                // Submenu for each history entry
                let entrySubmenu = NSMenu()
                
                let pasteItem = NSMenuItem(title: "→ Paste at Cursor", action: #selector(pasteHistoryItem(_:)), keyEquivalent: "")
                pasteItem.target = self
                pasteItem.representedObject = entry.fullText
                entrySubmenu.addItem(pasteItem)
                
                let copyItem = NSMenuItem(title: "⎘ Copy to Clipboard", action: #selector(copyHistoryItem(_:)), keyEquivalent: "")
                copyItem.target = self
                copyItem.representedObject = entry.fullText
                entrySubmenu.addItem(copyItem)
                
                let deleteItem = NSMenuItem(title: "✕ Delete", action: #selector(deleteHistoryItem(_:)), keyEquivalent: "")
                deleteItem.target = self
                deleteItem.tag = index
                entrySubmenu.addItem(deleteItem)
                
                item.submenu = entrySubmenu
                submenu.addItem(item)
            }
        }
        
        submenu.addItem(NSMenuItem.separator())
        
        let clearItem = NSMenuItem(title: "Clear All History", action: #selector(clearHistory), keyEquivalent: "")
        clearItem.target = self
        submenu.addItem(clearItem)
        
        return submenu
    }
    
    // MARK: - Hotkey Setup
    
    private func setupHotkey() {
        // Monitor for Right Command key (keyCode 0x36)
        eventMonitor = NSEvent.addGlobalMonitorForEvents(matching: .flagsChanged) { [weak self] event in
            let rightCommandKeyCode: UInt16 = 0x36
            
            if event.keyCode == rightCommandKeyCode {
                if event.modifierFlags.contains(.command) {
                    self?.startRecording()
                } else {
                    self?.stopRecording()
                }
            }
        }
    }
    
    // MARK: - Recording Flow
    
    private func startRecording() {
        guard !isRecording && !isProcessing else { return }
        
        // Check model ready
        guard transcriptionEngine.isModelLoaded else {
            updateStatus("Model not ready")
            return
        }
        
        isRecording = true
        updateStatus("Recording...")
        updateIcon("🔴")
        
        if !audioRecorder.startRecording() {
            updateStatus("Mic access denied")
            updateIcon("🎤")
            isRecording = false
        }
    }
    
    private func stopRecording() {
        guard isRecording else { return }
        
        isRecording = false
        isProcessing = true
        updateStatus("Processing...")
        updateIcon("⏳")
        
        guard let audioURL = audioRecorder.stopRecording() else {
            updateStatus("No audio")
            updateIcon("🎤")
            isProcessing = false
            return
        }
        
        Task {
            await processAudio(url: audioURL)
        }
    }
    
    private func processAudio(url: URL) async {
        do {
            let text = try await transcriptionEngine.transcribe(audioURL: url)
            
            await MainActor.run {
                if text.isEmpty {
                    updateStatus("No speech detected")
                } else {
                    // Record stats and history
                    statsManager.recordTranscription(text)
                    historyManager.addEntry(text)
                    updateStatsDisplay()
                    refreshHistoryMenu()
                    
                    // Paste the text
                    if textInjector.pasteText(text) {
                        updateStatus("Done!")
                    } else {
                        updateStatus("Paste failed")
                    }
                }
                
                // Reset after delay
                DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
                    self.updateStatus("Ready")
                    self.updateIcon("🎤")
                    self.isProcessing = false
                }
            }
        } catch {
            await MainActor.run {
                updateStatus("Error: \(error.localizedDescription)")
                DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                    self.updateStatus("Ready")
                    self.updateIcon("🎤")
                    self.isProcessing = false
                }
            }
        }
    }
    
    // MARK: - UI Updates
    
    private func updateStatus(_ status: String) {
        // Handle download progress in specialized way or general status
        DispatchQueue.main.async {
            self.statusMenuItem?.title = "Status: \(status)"
        }
    }
    
    private func updateIcon(_ icon: String) {
        DispatchQueue.main.async {
            self.statusItem?.button?.title = icon
        }
    }
    
    private func updateStatsDisplay() {
        statsTodayItem?.title = "  Today's Words: \(statsManager.getTodayWords())"
        statsTotalItem?.title = "  Total Words: \(statsManager.getTotalWords())"
        statsTimeItem?.title = "  Time Saved: \(statsManager.getTimeSavedMinutes()) min"
    }
    
    private func refreshHistoryMenu() {
        historyMenuItem?.submenu = buildHistoryMenu()
    }
    
    // MARK: - Menu Actions
    
    @objc private func pasteHistoryItem(_ sender: NSMenuItem) {
        guard let text = sender.representedObject as? String else { return }
        if textInjector.pasteText(text) {
            updateStatus("Pasted!")
            DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
                self.updateStatus("Ready")
            }
        }
    }
    
    @objc private func copyHistoryItem(_ sender: NSMenuItem) {
        guard let text = sender.representedObject as? String else { return }
        textInjector.copyToClipboard(text)
        updateStatus("Copied!")
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            self.updateStatus("Ready")
        }
    }
    
    @objc private func deleteHistoryItem(_ sender: NSMenuItem) {
        historyManager.deleteEntry(at: sender.tag)
        refreshHistoryMenu()
    }
    
    @objc private func clearHistory() {
        historyManager.clearHistory()
        refreshHistoryMenu()
    }
    
    @objc private func showHelp() {
        let alert = NSAlert()
        alert.messageText = "How to Use Voice Typing"
        alert.informativeText = """
        1. Click where you want to type
        2. Press and hold RIGHT COMMAND key
        3. Speak naturally
        4. Release the key
        5. Your text appears!
        
        Initial Setup:
        On first run, the app will download the AI model (~140MB). 
        Please wait for status to show "Ready".
        
        Icons:
        🎤 = Ready
        🔴 = Recording
        ⏳ = Processing
        """
        alert.alertStyle = .informational
        alert.addButton(withTitle: "OK")
        alert.runModal()
    }
    
    @objc private func quitApp() {
        NSApplication.shared.terminate(self)
    }
}
