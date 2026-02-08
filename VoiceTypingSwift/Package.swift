// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "VoiceTyping",
    platforms: [
        .macOS(.v13)
    ],
    dependencies: [
        .package(url: "https://github.com/argmaxinc/WhisperKit", from: "0.9.0"),
    ],
    targets: [
        .executableTarget(
            name: "VoiceTyping",
            dependencies: [
                .product(name: "WhisperKit", package: "WhisperKit"),
            ],
            path: "Sources",
            resources: [
                .copy("Resources")
            ]
        ),
    ]
)
