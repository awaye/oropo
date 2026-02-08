import Foundation
import WhisperKit

/// Handles audio transcription using WhisperKit
class TranscriptionEngine {
    private var whisperKit: WhisperKit?
    private var isLoading = false
    private var modelLoaded = false
    
    /// Load the Whisper model
    func loadModel() async throws {
        guard !modelLoaded && !isLoading else { return }
        
        isLoading = true
        defer { isLoading = false }
        
        // Use base model for good balance of speed and accuracy
        whisperKit = try await WhisperKit(model: "base")
        modelLoaded = true
    }
    
    /// Check if model is loaded
    var isModelLoaded: Bool {
        return modelLoaded
    }
    
    /// Transcribe audio file to text
    func transcribe(audioURL: URL) async throws -> String {
        // Ensure model is loaded
        if !modelLoaded {
            try await loadModel()
        }
        
        guard let whisperKit = whisperKit else {
            throw TranscriptionError.modelNotLoaded
        }
        
        // Transcribe the audio
        let results = try await whisperKit.transcribe(audioPath: audioURL.path)
        
        // Combine all segments
        let text = results
            .map { $0.text }
            .joined(separator: " ")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        
        // Clean up temp audio file
        try? FileManager.default.removeItem(at: audioURL)
        
        return text
    }
}

enum TranscriptionError: Error, LocalizedError {
    case modelNotLoaded
    case transcriptionFailed(String)
    
    var errorDescription: String? {
        switch self {
        case .modelNotLoaded:
            return "Whisper model not loaded"
        case .transcriptionFailed(let reason):
            return "Transcription failed: \(reason)"
        }
    }
}
