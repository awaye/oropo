import Foundation

/// Manages transcription history with persistence
class HistoryManager {
    private let maxEntries = 10
    private let userDefaultsKey = "transcriptionHistory"
    
    struct HistoryEntry: Codable {
        let text: String
        let timestamp: Date
    }
    
    private var entries: [HistoryEntry] = []
    
    init() {
        loadHistory()
    }
    
    /// Add a new transcription to history
    func addEntry(_ text: String) {
        let entry = HistoryEntry(text: text, timestamp: Date())
        entries.insert(entry, at: 0)
        
        // Keep only max entries
        if entries.count > maxEntries {
            entries = Array(entries.prefix(maxEntries))
        }
        
        saveHistory()
    }
    
    /// Get all history entries
    func getEntries() -> [HistoryEntry] {
        return entries
    }
    
    /// Get formatted entries for menu display
    func getFormattedHistory() -> [(display: String, fullText: String, timestamp: Date)] {
        return entries.map { entry in
            let truncated = entry.text.count > 40 
                ? String(entry.text.prefix(40)) + "..." 
                : entry.text
            return (display: truncated, fullText: entry.text, timestamp: entry.timestamp)
        }
    }
    
    /// Delete entry at index
    func deleteEntry(at index: Int) {
        guard index >= 0 && index < entries.count else { return }
        entries.remove(at: index)
        saveHistory()
    }
    
    /// Clear all history
    func clearHistory() {
        entries.removeAll()
        saveHistory()
    }
    
    // MARK: - Persistence
    
    private func loadHistory() {
        guard let data = UserDefaults.standard.data(forKey: userDefaultsKey),
              let decoded = try? JSONDecoder().decode([HistoryEntry].self, from: data) else {
            return
        }
        entries = decoded
    }
    
    private func saveHistory() {
        guard let encoded = try? JSONEncoder().encode(entries) else { return }
        UserDefaults.standard.set(encoded, forKey: userDefaultsKey)
    }
}
