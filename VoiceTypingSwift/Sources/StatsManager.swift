import Foundation

/// Manages transcription statistics with persistence
class StatsManager {
    private let todayWordsKey = "todayWords"
    private let todayDateKey = "todayDate"
    private let totalWordsKey = "totalWords"
    
    init() {
        checkDateRollover()
    }
    
    /// Record a transcription and update stats
    func recordTranscription(_ text: String) {
        checkDateRollover()
        
        let wordCount = text.split(separator: " ").count
        
        // Update today's count
        let todayWords = UserDefaults.standard.integer(forKey: todayWordsKey)
        UserDefaults.standard.set(todayWords + wordCount, forKey: todayWordsKey)
        
        // Update total count
        let totalWords = UserDefaults.standard.integer(forKey: totalWordsKey)
        UserDefaults.standard.set(totalWords + wordCount, forKey: totalWordsKey)
    }
    
    /// Get today's word count
    func getTodayWords() -> Int {
        checkDateRollover()
        return UserDefaults.standard.integer(forKey: todayWordsKey)
    }
    
    /// Get total word count
    func getTotalWords() -> Int {
        return UserDefaults.standard.integer(forKey: totalWordsKey)
    }
    
    /// Get estimated time saved in minutes (assumes 40 WPM typing speed)
    func getTimeSavedMinutes() -> Int {
        let totalWords = getTotalWords()
        return totalWords / 40  // Average typing speed
    }
    
    // MARK: - Private
    
    private func checkDateRollover() {
        let today = dateString(from: Date())
        let storedDate = UserDefaults.standard.string(forKey: todayDateKey) ?? ""
        
        if today != storedDate {
            // New day - reset today's count
            UserDefaults.standard.set(0, forKey: todayWordsKey)
            UserDefaults.standard.set(today, forKey: todayDateKey)
        }
    }
    
    private func dateString(from date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter.string(from: date)
    }
}
