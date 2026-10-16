import 'package:flutter/material.dart';

/// Raw palette. Widgets should prefer `Theme.of(context).colorScheme`
/// and `context.gameColors` over these constants.
abstract final class AppColors {
  static const Color violet = Color(0xFF6C4CF5);
  static const Color violetDeep = Color(0xFF4B2FD1);
  static const Color mint = Color(0xFF14B88F);
  static const Color sky = Color(0xFF3D8BFF);
  static const Color flame = Color(0xFFFF7A1A);
  static const Color gold = Color(0xFFF5B400);
  static const Color coral = Color(0xFFF0506E);
  static const Color heart = Color(0xFFFF4D6D);
  static const Color green = Color(0xFF22C55E);

  static const Color lightBackground = Color(0xFFF6F5FB);
  static const Color lightSurface = Color(0xFFFFFFFF);
  static const Color lightOutline = Color(0xFFE2DFEE);
  static const Color lightLocked = Color(0xFFC9C6D6);

  static const Color darkBackground = Color(0xFF12111A);
  static const Color darkSurface = Color(0xFF1C1B27);
  static const Color darkOutline = Color(0xFF2E2C3E);
  static const Color darkLocked = Color(0xFF3A3850);

  static const Color codeBackgroundLight = Color(0xFF1F1D2E);
  static const Color codeBackgroundDark = Color(0xFF0B0A12);
  static const Color codeText = Color(0xFFECEAF7);
  static const Color codeKeyword = Color(0xFFC792EA);
  static const Color codeString = Color(0xFFC3E88D);
  static const Color codeNumber = Color(0xFFF78C6C);
  static const Color codeComment = Color(0xFF7F7A99);
  static const Color codeBuiltin = Color(0xFF82AAFF);

  static const Color white = Color(0xFFFFFFFF);
}
