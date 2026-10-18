import 'package:flutter/material.dart';

/// Onest for the interface, JetBrains Mono for code. Both are bundled in
/// assets/fonts (OFL) so text renders the same offline.
abstract final class AppTypography {
  static const String uiFamily = 'Onest';
  static const String codeFamily = 'JetBrainsMono';
  static const List<String> _codeFallback = ['monospace'];

  static const double codeSize = 18;
  static const double codeLineHeight = 1.5;

  /// JetBrains Mono draws `>=`, `==`, `->` as single glyphs (≥, ═, →).
  /// A learner must see the characters they type, so ligatures are off.
  static const List<FontFeature> codeFeatures = [
    FontFeature.disable('calt'),
    FontFeature.disable('liga'),
  ];

  /// Advance width of one JetBrains Mono character, in ems.
  static const double codeAdvance = 0.6;

  static TextStyle code({
    Color? color,
    double size = codeSize,
    FontWeight weight = FontWeight.w500,
  }) =>
      TextStyle(
        fontFamily: codeFamily,
        fontFamilyFallback: _codeFallback,
        fontSize: size,
        height: codeLineHeight,
        color: color,
        fontWeight: weight,
        fontFeatures: codeFeatures,
      );

  /// Type scale (px): 30 / 26 / 24 / 20 / 17 / 15 / 13.
  static TextTheme textTheme(TextTheme base, Color text) {
    TextStyle? style(TextStyle? s, double size, FontWeight weight,
            {double height = 1.25, double spacing = 0}) =>
        s?.copyWith(
          fontFamily: uiFamily,
          fontSize: size,
          fontWeight: weight,
          height: height,
          letterSpacing: spacing,
          color: text,
        );
    return base.copyWith(
      displaySmall: style(base.displaySmall, 34, FontWeight.w800, spacing: -0.6),
      headlineLarge:
          style(base.headlineLarge, 30, FontWeight.w800, height: 1.15, spacing: -0.6),
      headlineMedium:
          style(base.headlineMedium, 26, FontWeight.w800, height: 1.15, spacing: -0.5),
      headlineSmall: style(base.headlineSmall, 24, FontWeight.w800, spacing: -0.3),
      titleLarge: style(base.titleLarge, 20, FontWeight.w700),
      titleMedium: style(base.titleMedium, 17, FontWeight.w700),
      titleSmall: style(base.titleSmall, 15, FontWeight.w700),
      bodyLarge: style(base.bodyLarge, 17, FontWeight.w400, height: 1.45),
      bodyMedium: style(base.bodyMedium, 15, FontWeight.w400, height: 1.45),
      bodySmall: style(base.bodySmall, 13, FontWeight.w500, height: 1.35),
      labelLarge: style(base.labelLarge, 17, FontWeight.w800),
      labelMedium: style(base.labelMedium, 14, FontWeight.w600),
      labelSmall: style(base.labelSmall, 12, FontWeight.w600),
    );
  }
}
