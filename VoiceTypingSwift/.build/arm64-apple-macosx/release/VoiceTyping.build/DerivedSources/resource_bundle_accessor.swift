import Foundation

extension Foundation.Bundle {
    static let module: Bundle = {
        let mainPath = Bundle.main.bundleURL.appendingPathComponent("VoiceTyping_VoiceTyping.bundle").path
        let buildPath = "/Volumes/Awaye-SSD/AntiGravity/STT/VoiceTypingSwift/.build/arm64-apple-macosx/release/VoiceTyping_VoiceTyping.bundle"

        let preferredBundle = Bundle(path: mainPath)

        guard let bundle = preferredBundle ?? Bundle(path: buildPath) else {
            // Users can write a function called fatalError themselves, we should be resilient against that.
            Swift.fatalError("could not load resource bundle: from \(mainPath) or \(buildPath)")
        }

        return bundle
    }()
}