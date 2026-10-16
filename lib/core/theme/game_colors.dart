import 'package:flutter/material.dart';

import 'app_colors.dart';

/// Game-specific semantic colors not covered by [ColorScheme].
@immutable
class GameColors extends ThemeExtension<GameColors> {
  const GameColors({
    required this.success,
    required this.error,
    required this.streak,
    required this.xp,
    required this.coin,
    required this.life,
    required this.locked,
    required this.codeBackground,
    required this.codeText,
    required this.codeKeyword,
    required this.codeString,
    required this.codeNumber,
    required this.codeComment,
    required this.codeBuiltin,
  });

  static const GameColors light = GameColors(
    success: AppColors.green,
    error: AppColors.coral,
    streak: AppColors.flame,
    xp: AppColors.sky,
    coin: AppColors.gold,
    life: AppColors.heart,
    locked: AppColors.lightLocked,
    codeBackground: AppColors.codeBackgroundLight,
    codeText: AppColors.codeText,
    codeKeyword: AppColors.codeKeyword,
    codeString: AppColors.codeString,
    codeNumber: AppColors.codeNumber,
    codeComment: AppColors.codeComment,
    codeBuiltin: AppColors.codeBuiltin,
  );

  static const GameColors dark = GameColors(
    success: AppColors.green,
    error: AppColors.coral,
    streak: AppColors.flame,
    xp: AppColors.sky,
    coin: AppColors.gold,
    life: AppColors.heart,
    locked: AppColors.darkLocked,
    codeBackground: AppColors.codeBackgroundDark,
    codeText: AppColors.codeText,
    codeKeyword: AppColors.codeKeyword,
    codeString: AppColors.codeString,
    codeNumber: AppColors.codeNumber,
    codeComment: AppColors.codeComment,
    codeBuiltin: AppColors.codeBuiltin,
  );

  final Color success;
  final Color error;
  final Color streak;
  final Color xp;
  final Color coin;
  final Color life;
  final Color locked;
  final Color codeBackground;
  final Color codeText;
  final Color codeKeyword;
  final Color codeString;
  final Color codeNumber;
  final Color codeComment;
  final Color codeBuiltin;

  @override
  GameColors copyWith({
    Color? success,
    Color? error,
    Color? streak,
    Color? xp,
    Color? coin,
    Color? life,
    Color? locked,
    Color? codeBackground,
    Color? codeText,
    Color? codeKeyword,
    Color? codeString,
    Color? codeNumber,
    Color? codeComment,
    Color? codeBuiltin,
  }) =>
      GameColors(
        success: success ?? this.success,
        error: error ?? this.error,
        streak: streak ?? this.streak,
        xp: xp ?? this.xp,
        coin: coin ?? this.coin,
        life: life ?? this.life,
        locked: locked ?? this.locked,
        codeBackground: codeBackground ?? this.codeBackground,
        codeText: codeText ?? this.codeText,
        codeKeyword: codeKeyword ?? this.codeKeyword,
        codeString: codeString ?? this.codeString,
        codeNumber: codeNumber ?? this.codeNumber,
        codeComment: codeComment ?? this.codeComment,
        codeBuiltin: codeBuiltin ?? this.codeBuiltin,
      );

  @override
  GameColors lerp(covariant ThemeExtension<GameColors>? other, double t) {
    if (other is! GameColors) return this;
    Color mix(Color a, Color b) => Color.lerp(a, b, t)!;
    return GameColors(
      success: mix(success, other.success),
      error: mix(error, other.error),
      streak: mix(streak, other.streak),
      xp: mix(xp, other.xp),
      coin: mix(coin, other.coin),
      life: mix(life, other.life),
      locked: mix(locked, other.locked),
      codeBackground: mix(codeBackground, other.codeBackground),
      codeText: mix(codeText, other.codeText),
      codeKeyword: mix(codeKeyword, other.codeKeyword),
      codeString: mix(codeString, other.codeString),
      codeNumber: mix(codeNumber, other.codeNumber),
      codeComment: mix(codeComment, other.codeComment),
      codeBuiltin: mix(codeBuiltin, other.codeBuiltin),
    );
  }
}

extension GameColorsContext on BuildContext {
  GameColors get gameColors =>
      Theme.of(this).extension<GameColors>() ?? GameColors.light;
}
