// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "VoiceTyping",
    platforms: [
        .macOS(.v13)
    ],
    dependencies: [
        // SwiftWhisper (whisper.cpp wrapper) for Universal support
        .package(url: "https://github.com/exPHAT/SwiftWhisper.git", from: "1.0.0"),
        // ZipArchive for unzipping downloaded models if needed
        .package(url: "https://github.com/ZipArchive/ZipArchive.git", from: "2.5.5")
    ],
    targets: [
        .executableTarget(
            name: "VoiceTyping",
            dependencies: [
                .product(name: "SwiftWhisper", package: "SwiftWhisper"),
                .product(name: "ZipArchive", package: "ZipArchive")
            ],
            path: "Sources",
            resources: [
                .copy("Resources")
            ]
        ),
    ]
)
