import AVFoundation
import Foundation

/// Handles audio recording from the microphone
class AudioRecorder {
    private var audioRecorder: AVAudioRecorder?
    private var audioURL: URL?
    private var permissionGranted = false
    
    init() {
        checkPermission()
    }
    
    /// Check and request microphone permission
    func checkPermission() {
        switch AVCaptureDevice.authorizationStatus(for: .audio) {
        case .authorized:
            permissionGranted = true
        case .notDetermined:
            AVCaptureDevice.requestAccess(for: .audio) { [weak self] granted in
                self?.permissionGranted = granted
            }
        case .denied, .restricted:
            permissionGranted = false
        @unknown default:
            permissionGranted = false
        }
    }
    
    /// Start recording audio
    func startRecording() -> Bool {
        guard permissionGranted else {
            print("Microphone permission not granted")
            return false
        }
        
        // Create temp file for recording
        let tempDir = FileManager.default.temporaryDirectory
        let filename = "voice_recording_\(Date().timeIntervalSince1970).wav"
        audioURL = tempDir.appendingPathComponent(filename)
        
        guard let url = audioURL else { return false }
        
        // Audio settings for Whisper compatibility
        let settings: [String: Any] = [
            AVFormatIDKey: Int(kAudioFormatLinearPCM),
            AVSampleRateKey: 16000.0,
            AVNumberOfChannelsKey: 1,
            AVLinearPCMBitDepthKey: 16,
            AVLinearPCMIsFloatKey: false,
            AVLinearPCMIsBigEndianKey: false
        ]
        
        do {
            audioRecorder = try AVAudioRecorder(url: url, settings: settings)
            audioRecorder?.record()
            return true
        } catch {
            print("Failed to start recording: \(error)")
            return false
        }
    }
    
    /// Stop recording and return the audio file URL
    func stopRecording() -> URL? {
        audioRecorder?.stop()
        audioRecorder = nil
        
        // Verify file exists and has content
        if let url = audioURL,
           FileManager.default.fileExists(atPath: url.path) {
            return url
        }
        
        return nil
    }
    
    /// Clean up any temporary files
    func cleanup() {
        if let url = audioURL {
            try? FileManager.default.removeItem(at: url)
        }
        audioRecorder?.stop()
        audioRecorder = nil
        audioURL = nil
    }
}
