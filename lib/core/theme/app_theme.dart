import 'package:flutter/material.dart';

import 'app_colors.dart';
import 'app_spacing.dart';
import 'app_typography.dart';
import 'game_colors.dart';

abstract final class AppTheme {
  static ThemeData get light => _build(
        brightness: Brightness.light,
        background: AppColors.lightBackground,
        surface: AppColors.lightSurface,
        outline: AppColors.lightOutline,
        game: GameColors.light,
      );

  static ThemeData get dark => _build(
        brightness: Brightness.dark,
        background: AppColors.darkBackground,
        surface: AppColors.darkSurface,
        outline: AppColors.darkOutline,
        game: GameColors.dark,
      );

  static ThemeData _build({
    required Brightness brightness,
    required Color background,
    required Color surface,
    required Color outline,
    required GameColors game,
  }) {
    final scheme = ColorScheme.fromSeed(
      seedColor: AppColors.violet,
      brightness: brightness,
    ).copyWith(
      primary: AppColors.violet,
      onPrimary: AppColors.white,
      secondary: AppColors.mint,
      onSecondary: AppColors.white,
      error: AppColors.coral,
      surface: surface,
      outline: outline,
      outlineVariant: outline,
    );
    final base = ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      brightness: brightness,
    );
    return base.copyWith(
      scaffoldBackgroundColor: background,
      textTheme: AppTypography.textTheme(base.textTheme),
      extensions: [game],
      appBarTheme: AppBarTheme(
        backgroundColor: background,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        centerTitle: false,
        titleTextStyle: AppTypography.textTheme(base.textTheme)
            .titleLarge
            ?.copyWith(color: scheme.onSurface),
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: surface,
        indicatorColor: AppColors.violet.withValues(alpha: 0.16),
        height: 68,
      ),
      snackBarTheme: const SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: AppRadius.mdAll),
      ),
      dividerTheme: DividerThemeData(color: outline, thickness: 1),
    );
  }
}
