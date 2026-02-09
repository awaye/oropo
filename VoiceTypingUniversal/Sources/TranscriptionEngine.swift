import Foundation
import SwiftWhisper

/// Handles audio transcription using SwiftWhisper (whisper.cpp)
/// Supports both Intel (Accelerate) and Apple Silicon (Metal)
class TranscriptionEngine {
    private var whisper: Whisper?
    private var isLoading = false
    private var modelLoaded = false
    private var downloadTask: URLSessionDownloadTask?
    
    // Model configuration
    private let modelName = "ggml-base.en.bin"
    // Using a reliable mirror for whisper.cpp models
    private let modelURL = URL(string: "https://huggingface.co/gherid/whisper.cpp/resolve/main/ggml-base.en.bin")!
    
    var onProgress: ((Double) -> Void)?
    var onStatusChange: ((String) -> Void)?
    
    /// Check if model is loaded
    var isModelLoaded: Bool {
        return modelLoaded
    }
    
    /// Initialize and load/download model
    func initialize() async {
        if isModelFilePresent() {
            loadModel()
        } else {
            await downloadModel()
        }
    }
    
    /// Transcribe audio file to text
    func transcribe(audioURL: URL) async throws -> String {
        guard let whisper = whisper, modelLoaded else {
            throw TranscriptionError.modelNotLoaded
        }
        
        // SwiftWhisper transcribe(audioFrames:) expects [Float]
        // We need to read the WAV file and convert to Float array
        guard let audioFrames = readAudioFile(url: audioURL) else {
            throw TranscriptionError.audioReadFailed
        }
        
        return try await withCheckedThrowingContinuation { continuation in
            Task {
                do {
                    let segments = try await whisper.transcribe(audioFrames: audioFrames)
                    let text = segments.map { $0.text }.joined(separator: " ").trimmingCharacters(in: .whitespacesAndNewlines)
                    
                    // Clean up temp audio file
                    try? FileManager.default.removeItem(at: audioURL)
                    
                    continuation.resume(returning: text)
                } catch {
                     continuation.resume(throwing: TranscriptionError.transcriptionFailed(error.localizedDescription))
                }
            }
        }
    }
    
    // MARK: - Model Management
    
    private func getModelPath() -> URL {
        let appSupport = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first!
        let appDir = appSupport.appendingPathComponent("VoiceTyping")
        return appDir.appendingPathComponent("models").appendingPathComponent(modelName)
    }
    
    private func isModelFilePresent() -> Bool {
        return FileManager.default.fileExists(atPath: getModelPath().path)
    }
    
    private func loadModel() {
        let path = getModelPath()
        onStatusChange?("Loading model...")
        
        let whisper = Whisper(fromFileURL: path)
        self.whisper = whisper
        modelLoaded = true
        onStatusChange?("Ready")
        onProgress?(1.0)
    }
    
    private func downloadModel() async {
        onStatusChange?("Downloading model...")
        isLoading = true
        
        // Create directory
        let modelPath = getModelPath()
        try? FileManager.default.createDirectory(at: modelPath.deletingLastPathComponent(), withIntermediateDirectories: true)
        
        do {
            let (tempURL, _) = try await URLSession.shared.download(from: modelURL)
            
            // Move file to destination
            if FileManager.default.fileExists(atPath: modelPath.path) {
                try FileManager.default.removeItem(at: modelPath)
            }
            try FileManager.default.moveItem(at: tempURL, to: modelPath)
            
            // Load it
            loadModel()
        } catch {
            onStatusChange?("Download failed: \(error.localizedDescription)")
            print("Download error: \(error)")
        }
        
        isLoading = false
    }
    
    // MARK: - Audio Helper
    
    private func readAudioFile(url: URL) -> [Float]? {
        // Read WAV file header to find data chunk
        // This is a simplified reader suitable for the specific format we record in (16kHz 16-bit mono)
        
        guard let data = try? Data(contentsOf: url) else { return nil }
        
        // Skip header (usually 44 bytes for WAV)
        // A robust implementation would parse the header, but for our specific recorder settings 44 is standard
        let headerSize = 44
        guard data.count > headerSize else { return nil }
        
        let pcmData = data.subdata(in: headerSize..<data.count)
        
        // Convert Int16 data to Float [-1.0, 1.0]
        var floats = [Float]()
        floats.reserveCapacity(pcmData.count / 2)
        
        pcmData.withUnsafeBytes { buffer in
            let int16Buffer = buffer.bindMemory(to: Int16.self)
            for int16 in int16Buffer {
                floats.append(Float(int16) / 32768.0)
            }
        }
        
        return floats
    }
}

enum TranscriptionError: Error, LocalizedError {
    case modelNotLoaded
    case audioReadFailed
    case transcriptionFailed(String)
    
    var errorDescription: String? {
        switch self {
        case .modelNotLoaded:
            return "Whisper model not loaded"
        case .audioReadFailed:
            return "Could not read audio file"
        case .transcriptionFailed(let reason):
            return "Transcription failed: \(reason)"
        }
    }
}
