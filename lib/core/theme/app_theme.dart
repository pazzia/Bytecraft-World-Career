import 'package:flutter/material.dart';

import 'app_colors.dart';
import 'app_spacing.dart';
import 'app_typography.dart';
import 'game_colors.dart';

abstract final class AppTheme {
  static ThemeData get light => _build(
        brightness: Brightness.light,
        primary: AppColors.blue,
        surface: AppColors.surface,
        text: AppColors.ink,
        outline: AppColors.line,
        game: GameColors.light,
      );

  static ThemeData get dark => _build(
        brightness: Brightness.dark,
        primary: AppColors.blue,
        surface: AppColors.nightSurface,
        text: AppColors.nightText,
        outline: AppColors.nightLine,
        game: GameColors.dark,
      );

  /// The "На время" mode: night palette with ember actions, independent of
  /// the system theme so the mode always feels like a different place.
  static ThemeData get timed => _build(
        brightness: Brightness.dark,
        primary: AppColors.ember,
        surface: AppColors.nightSurface,
        text: AppColors.nightText,
        outline: AppColors.nightLine,
        game: GameColors.timed,
      );

  static ThemeData _build({
    required Brightness brightness,
    required Color primary,
    required Color surface,
    required Color text,
    required Color outline,
    required GameColors game,
  }) {
    final scheme = ColorScheme.fromSeed(
      seedColor: AppColors.blue,
      brightness: brightness,
    ).copyWith(
      primary: primary,
      onPrimary: game.onPrimary,
      secondary: AppColors.green,
      onSecondary: AppColors.white,
      error: AppColors.red,
      surface: surface,
      onSurface: text,
      outline: outline,
      outlineVariant: outline,
    );
    final base = ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      brightness: brightness,
      fontFamily: AppTypography.uiFamily,
    );
    final textTheme = AppTypography.textTheme(base.textTheme, text);
    return base.copyWith(
      scaffoldBackgroundColor: game.background,
      textTheme: textTheme,
      extensions: [game],
      iconTheme: IconThemeData(color: text),
      appBarTheme: AppBarTheme(
        backgroundColor: game.background,
        foregroundColor: text,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: false,
        titleTextStyle: textTheme.titleLarge,
      ),
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        backgroundColor: AppColors.ink,
        contentTextStyle: textTheme.bodyMedium?.copyWith(color: AppColors.white),
        shape: const RoundedRectangleBorder(borderRadius: AppRadius.mdAll),
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: surface,
        shape: const RoundedRectangleBorder(borderRadius: AppRadius.xlAll),
      ),
      dividerTheme: DividerThemeData(color: outline, thickness: 1),
      progressIndicatorTheme: ProgressIndicatorThemeData(color: primary),
    );
  }
}
