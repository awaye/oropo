#import <Foundation/Foundation.h>

NSBundle* ZipArchive_SWIFTPM_MODULE_BUNDLE() {
    NSURL *bundleURL = [[[NSBundle mainBundle] bundleURL] URLByAppendingPathComponent:@"ZipArchive_ZipArchive.bundle"];

    NSBundle *preferredBundle = [NSBundle bundleWithURL:bundleURL];
    if (preferredBundle == nil) {
      return [NSBundle bundleWithPath:@"/Volumes/Awaye-SSD/AntiGravity/STT/VoiceTypingUniversal/.build/arm64-apple-macosx/release/ZipArchive_ZipArchive.bundle"];
    }

    return preferredBundle;
}