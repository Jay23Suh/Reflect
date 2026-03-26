import SwiftUI

// MARK: - Colors
extension Color {
    init(hex: String) {
        let h = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: h).scanHexInt64(&int)
        let r = Double((int >> 16) & 0xFF) / 255
        let g = Double((int >> 8) & 0xFF) / 255
        let b = Double(int & 0xFF) / 255
        self.init(red: r, green: g, blue: b)
    }

    // Brand palette
    static let rPink     = Color(hex: "#FFA6C9")
    static let rMint     = Color(hex: "#76D7C4")
    static let rLavender = Color(hex: "#C39BD3")
    static let rBlue     = Color(hex: "#005499")
    static let rOrange   = Color(hex: "#F7971D")
    static let rVoid     = Color(hex: "#0A0B16")

    // Semantic — light
    static let rBgLight      = Color(hex: "#fceef5")
    static let rTextLight     = Color(hex: "#005499")
    static let rMutedLight    = Color(hex: "#005499").opacity(0.45)
    static let rCardLight     = Color.white.opacity(0.52)
    static let rBorderLight   = Color(hex: "#C39BD3").opacity(0.35)
    static let rInputLight    = Color.white.opacity(0.7)

    // Semantic — dark
    static let rBgDark       = Color(hex: "#0A0B16")
    static let rTextDark      = Color(hex: "#FFA6C9")
    static let rMutedDark     = Color(hex: "#76D7C4").opacity(0.5)
    static let rCardDark      = Color(hex: "#005499").opacity(0.22)
    static let rBorderDark    = Color(hex: "#76D7C4").opacity(0.18)
    static let rInputDark     = Color(hex: "#005499").opacity(0.2)
}

// MARK: - Adaptive color helpers
struct RColor {
    static func text(_ scheme: ColorScheme) -> Color {
        scheme == .dark ? .rTextDark : .rTextLight
    }
    static func muted(_ scheme: ColorScheme) -> Color {
        scheme == .dark ? .rMutedDark : .rMutedLight
    }
    static func card(_ scheme: ColorScheme) -> Color {
        scheme == .dark ? .rCardDark : .rCardLight
    }
    static func border(_ scheme: ColorScheme) -> Color {
        scheme == .dark ? .rBorderDark : .rBorderLight
    }
    static func input(_ scheme: ColorScheme) -> Color {
        scheme == .dark ? .rInputDark : .rInputLight
    }
    static func soft(_ scheme: ColorScheme) -> Color {
        scheme == .dark ? Color(hex: "#76D7C4").opacity(0.85) : Color(hex: "#005499").opacity(0.75)
    }
}

// MARK: - Fonts
// Requires: CormorantGaramond-Regular.ttf, CormorantGaramond-Italic.ttf,
//           CormorantGaramond-SemiBold.ttf, Quicksand-Regular.ttf,
//           Quicksand-Medium.ttf, Quicksand-SemiBold.ttf, SpaceMono-Regular.ttf
// Add these files to the Xcode project and register in Info.plist under
// "Fonts provided by application"
struct RFont {
    static func header(_ size: CGFloat, italic: Bool = false) -> Font {
        italic
            ? .custom("CormorantGaramond-Italic", size: size)
            : .custom("CormorantGaramond-SemiBold", size: size)
    }
    static func body(_ size: CGFloat) -> Font {
        .custom("Quicksand-Medium", size: size)
    }
    static func mono(_ size: CGFloat) -> Font {
        .custom("SpaceMono-Regular", size: size)
    }
}

// MARK: - Gradient Background
// MARK: - Particle Field

private struct Particle: Identifiable {
    let id = UUID()
    let x: CGFloat        // 0–1 normalized
    let startY: CGFloat   // 0–1 normalized
    let size: CGFloat
    let duration: Double
    let delay: Double
    let opacity: Double
}

struct ParticleField: View {
    @Environment(\.colorScheme) var scheme
    private let particles: [Particle] = (0..<80).map { _ in
        Particle(
            x:        CGFloat.random(in: 0...1),
            startY:   CGFloat.random(in: 0...1),
            size:     CGFloat.random(in: 2.0...5.0),
            duration: Double.random(in: 8...20),
            delay:    Double.random(in: 0...10),
            opacity:  Double.random(in: 0.3...0.75)
        )
    }

    var body: some View {
        GeometryReader { geo in
            ForEach(particles) { p in
                ParticleDot(particle: p, size: geo.size, dark: scheme == .dark)
            }
        }
    }
}

private struct ParticleDot: View {
    let particle: Particle
    let size: CGSize
    let dark: Bool
    @State private var drifted = false

    var body: some View {
        Circle()
            .fill(Color.white.opacity(particle.opacity))
            .frame(width: particle.size, height: particle.size)
            .position(
                x: particle.x * size.width,
                y: drifted
                    ? (particle.startY * size.height) - 60
                    : (particle.startY * size.height) + 20
            )
            .opacity(drifted ? 0 : particle.opacity)
            .onAppear {
                withAnimation(
                    .easeInOut(duration: particle.duration)
                    .repeatForever(autoreverses: false)
                    .delay(particle.delay)
                ) { drifted = true }
            }
    }
}

// MARK: - Background

struct GroundBackground: View {
    @Environment(\.colorScheme) var scheme
    @State private var p1 = false
    @State private var p2 = false
    @State private var p3 = false
    @State private var p4 = false

    var body: some View {
        ZStack {
            scheme == .dark ? Color.rVoid : Color.rBgLight
            GeometryReader { geo in
                let w = geo.size.width
                ZStack {
                    if scheme == .dark {
                        RadialGradient(colors: [Color.rPink.opacity(0.45), .clear],
                                       center: UnitPoint(x: p1 ? 0.25 : 0.10, y: p1 ? 0.22 : 0.12),
                                       startRadius: 0, endRadius: w * 0.5)
                        RadialGradient(colors: [Color.rMint.opacity(0.38), .clear],
                                       center: UnitPoint(x: p2 ? 0.78 : 0.88, y: p2 ? 0.18 : 0.06),
                                       startRadius: 0, endRadius: w * 0.45)
                        RadialGradient(colors: [Color.rLavender.opacity(0.35), .clear],
                                       center: UnitPoint(x: p3 ? 0.55 : 0.68, y: p3 ? 0.72 : 0.84),
                                       startRadius: 0, endRadius: w * 0.5)
                        RadialGradient(colors: [Color.rBlue.opacity(0.25), .clear],
                                       center: UnitPoint(x: p4 ? 0.42 : 0.55, y: p4 ? 0.42 : 0.55),
                                       startRadius: 0, endRadius: w * 0.6)
                    } else {
                        RadialGradient(colors: [Color.rPink.opacity(0.55), .clear],
                                       center: UnitPoint(x: p1 ? 0.25 : 0.10, y: p1 ? 0.22 : 0.12),
                                       startRadius: 0, endRadius: w * 0.55)
                        RadialGradient(colors: [Color.rMint.opacity(0.45), .clear],
                                       center: UnitPoint(x: p2 ? 0.78 : 0.88, y: p2 ? 0.18 : 0.06),
                                       startRadius: 0, endRadius: w * 0.5)
                        RadialGradient(colors: [Color.rLavender.opacity(0.40), .clear],
                                       center: UnitPoint(x: p3 ? 0.60 : 0.72, y: p3 ? 0.78 : 0.88),
                                       startRadius: 0, endRadius: w * 0.55)
                        RadialGradient(colors: [Color.rPink.opacity(0.35), .clear],
                                       center: UnitPoint(x: p4 ? 0.12 : 0.02, y: p4 ? 0.72 : 0.84),
                                       startRadius: 0, endRadius: w * 0.5)
                    }
                }
                .frame(width: w, height: geo.size.height)
            }
            ParticleField()
        }
        .ignoresSafeArea()
        .onAppear {
            withAnimation(.easeInOut(duration: 9).repeatForever(autoreverses: true))  { p1 = true }
            withAnimation(.easeInOut(duration: 12).repeatForever(autoreverses: true).delay(1.5)) { p2 = true }
            withAnimation(.easeInOut(duration: 10).repeatForever(autoreverses: true).delay(3.0)) { p3 = true }
            withAnimation(.easeInOut(duration: 14).repeatForever(autoreverses: true).delay(0.8)) { p4 = true }
        }
    }
}

// MARK: - Glass Card
struct GlassCard<Content: View>: View {
    @Environment(\.colorScheme) var scheme
    let content: Content
    init(@ViewBuilder content: () -> Content) { self.content = content() }

    var body: some View {
        content
            .background(
                RoundedRectangle(cornerRadius: 20)
                    .fill(.ultraThinMaterial)
                    .overlay(
                        RoundedRectangle(cornerRadius: 20)
                            .fill(RColor.card(scheme))
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: 20)
                            .stroke(RColor.border(scheme), lineWidth: 1)
                    )
                    .shadow(color: Color.black.opacity(scheme == .dark ? 0.4 : 0.08),
                            radius: 24, x: 0, y: 8)
            )
    }
}

// MARK: - Button Styles
struct OrangeButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(RFont.body(15).weight(.semibold))
            .foregroundColor(.white)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .background(
                RoundedRectangle(cornerRadius: 10)
                    .fill(Color.rOrange.opacity(configuration.isPressed ? 0.8 : 1))
                    .shadow(color: Color.rOrange.opacity(0.35), radius: 8, x: 0, y: 4)
            )
    }
}

struct SkipButtonStyle: ButtonStyle {
    @Environment(\.colorScheme) var scheme
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(RFont.body(13))
            .foregroundColor(RColor.muted(scheme))
            .padding(.horizontal, 20)
            .padding(.vertical, 9)
            .background(
                RoundedRectangle(cornerRadius: 10)
                    .fill(RColor.input(scheme).opacity(configuration.isPressed ? 0.5 : 1))
                    .overlay(RoundedRectangle(cornerRadius: 10).stroke(RColor.border(scheme), lineWidth: 1))
            )
    }
}

struct SaveButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(RFont.body(13).weight(.semibold))
            .foregroundColor(.white)
            .padding(.horizontal, 20)
            .padding(.vertical, 9)
            .background(
                RoundedRectangle(cornerRadius: 10)
                    .fill(Color.rOrange.opacity(configuration.isPressed ? 0.8 : 1))
                    .shadow(color: Color.rOrange.opacity(0.35), radius: 6, x: 0, y: 3)
            )
    }
}
