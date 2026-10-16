import 'package:flutter/material.dart';

abstract final class AppTypography {
  /// Platform monospace fonts; no font assets required.
  static const String _monoFamily = 'monospace';
  static const List<String> _monoFallback = [
    'Menlo',
    'SF Mono',
    'Roboto Mono',
    'Courier New',
    'Courier',
  ];

  static const double codeSize = 16;
  static const double codeLineHeight = 1.5;

  static TextStyle code({Color? color, double size = codeSize}) => TextStyle(
        fontFamily: _monoFamily,
        fontFamilyFallback: _monoFallback,
        fontSize: size,
        height: codeLineHeight,
        color: color,
        fontWeight: FontWeight.w500,
      );

  static TextTheme textTheme(TextTheme base) => base.copyWith(
        displaySmall: base.displaySmall?.copyWith(fontWeight: FontWeight.w800),
        headlineMedium:
            base.headlineMedium?.copyWith(fontWeight: FontWeight.w800),
        headlineSmall: base.headlineSmall?.copyWith(fontWeight: FontWeight.w800),
        titleLarge: base.titleLarge?.copyWith(fontWeight: FontWeight.w700),
        titleMedium: base.titleMedium?.copyWith(fontWeight: FontWeight.w700),
        bodyLarge: base.bodyLarge?.copyWith(fontSize: 17, height: 1.4),
        bodyMedium: base.bodyMedium?.copyWith(fontSize: 15, height: 1.4),
        labelLarge: base.labelLarge?.copyWith(
          fontSize: 16,
          fontWeight: FontWeight.w800,
          letterSpacing: 0.4,
        ),
      );
}
