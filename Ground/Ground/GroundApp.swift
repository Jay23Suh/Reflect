import SwiftUI
import CoreText

@main
struct GroundApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate

    init() {
        registerFonts()
    }

    var body: some Scene {
        MenuBarExtra {
            MenuBarView()
                .environmentObject(SupabaseManager.shared)
        } label: {
            Image("GroundIcon")
                .resizable()
                .frame(width: 16, height: 16)
        }
        .menuBarExtraStyle(.menu)
    }

    private func registerFonts() {
        guard let resourcesURL = Bundle.main.resourceURL else { return }
        let enumerator = FileManager.default.enumerator(
            at: resourcesURL,
            includingPropertiesForKeys: nil,
            options: [.skipsHiddenFiles]
        )
        while let url = enumerator?.nextObject() as? URL {
            guard url.pathExtension == "ttf" || url.pathExtension == "otf" else { continue }
            CTFontManagerRegisterFontsForURL(url as CFURL, .process, nil)
        }
    }
}
