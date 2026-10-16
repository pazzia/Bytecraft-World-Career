import 'package:flutter/material.dart';

/// Raw palette of the "keycap" design (see docs/DESIGN.md).
///
/// Widgets use semantic tokens from `context.gameColors` and the
/// [ColorScheme]; these constants only feed the theme definitions.
abstract final class AppColors {
  // Day palette.
  static const Color paper = Color(0xFFEEF2F7);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color ink = Color(0xFF1B2838);
  static const Color inkEdge = Color(0xFF0D1520);
  static const Color inkSoft = Color(0xFF5B6B7F);
  static const Color line = Color(0xFFD5DDE8);
  static const Color lineSoft = Color(0xFFE6EBF2);
  static const Color keyEdge = Color(0xFFC3CEDC);
  static const Color track = Color(0xFFDCE3ED);
  static const Color lockedIcon = Color(0xFF7D8CA0);

  // Python blue: primary actions, current level.
  static const Color blue = Color(0xFF2F6DB5);
  static const Color blueEdge = Color(0xFF1F4E86);
  static const Color blueTint = Color(0xFFE6EFFA);
  static const Color blueRing = Color(0xFFC7DAF2);

  // Python yellow: rewards only.
  static const Color yellow = Color(0xFFFFD43B);
  static const Color yellowEdge = Color(0xFFC99B00);
  static const Color gold = Color(0xFFE0A800);

  static const Color green = Color(0xFF188A5D);
  static const Color greenEdge = Color(0xFF116A47);
  static const Color greenTint = Color(0xFFDDF3E8);
  static const Color greenBright = Color(0xFF2BB57A);

  static const Color red = Color(0xFFD23C42);
  static const Color redEdge = Color(0xFF9E272C);
  static const Color redTint = Color(0xFFFBE3E4);
  static const Color redBright = Color(0xFFE25B60);

  // Ember: streaks and the timed mode.
  static const Color ember = Color(0xFFFF5B1F);
  static const Color emberEdge = Color(0xFFB83A0B);
  static const Color emberSoft = Color(0xFFFF8A57);
  static const Color emberTint = Color(0xFFFFF1E9);
  static const Color emberText = Color(0xFF8A2E07);
  static const Color onEmber = Color(0xFF1B0A02);

  // Night palette: dark theme and the timed mode.
  static const Color night = Color(0xFF142033);
  static const Color nightSurface = Color(0xFF1C2B42);
  static const Color nightDeep = Color(0xFF0D1726);
  static const Color nightKey = Color(0xFF22344F);
  static const Color nightKeyLifted = Color(0xFF2F4566);
  static const Color nightLine = Color(0xFF2E3F59);
  static const Color nightText = Color(0xFFF1F5FA);
  static const Color nightMuted = Color(0xFFA9B8CC);
  static const Color nightHandle = Color(0xFF5E7392);

  // Code board.
  static const Color codeText = Color(0xFFE8EEF6);
  static const Color codeKeyword = Color(0xFFC792EA);
  static const Color codeBuiltin = Color(0xFF82AAFF);
  static const Color codeString = Color(0xFFC3E88D);
  static const Color codeNumber = Color(0xFFF78C6C);
  static const Color codeComment = Color(0xFF8796AB);
  static const Color codeLineNumber = Color(0xFF5B6B7F);

  static const Color white = Color(0xFFFFFFFF);
}
