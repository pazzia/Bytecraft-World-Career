import 'package:flutter/material.dart';

import 'app_colors.dart';

/// Semantic colors of the keycap design that [ColorScheme] doesn't cover.
///
/// "Key" tokens describe the physical keycap: [keyFace] on top, a solid
/// [keyEdge] underneath, [keyBorder] around it.
@immutable
class GameColors extends ThemeExtension<GameColors> {
  const GameColors({
    required this.background,
    required this.textMuted,
    required this.keyFace,
    required this.keyEdge,
    required this.keyBorder,
    required this.track,
    required this.locked,
    required this.lockedIcon,
    required this.primaryEdge,
    required this.primaryTint,
    required this.onPrimary,
    required this.success,
    required this.successEdge,
    required this.successTint,
    required this.successBright,
    required this.error,
    required this.errorEdge,
    required this.errorTint,
    required this.errorBright,
    required this.reward,
    required this.rewardEdge,
    required this.onReward,
    required this.rewardIcon,
    required this.streak,
    required this.streakTint,
    required this.streakText,
    required this.life,
    required this.board,
    required this.boardEdge,
    required this.boardMuted,
    required this.codeText,
    required this.codeKeyword,
    required this.codeBuiltin,
    required this.codeString,
    required this.codeNumber,
    required this.codeComment,
    required this.codeLineNumber,
  });

  static const GameColors light = GameColors(
    background: AppColors.paper,
    textMuted: AppColors.inkSoft,
    keyFace: AppColors.surface,
    keyEdge: AppColors.keyEdge,
    keyBorder: AppColors.line,
    track: AppColors.track,
    locked: AppColors.track,
    lockedIcon: AppColors.lockedIcon,
    primaryEdge: AppColors.blueEdge,
    primaryTint: AppColors.blueTint,
    onPrimary: AppColors.white,
    success: AppColors.green,
    successEdge: AppColors.greenEdge,
    successTint: AppColors.greenTint,
    successBright: AppColors.greenBright,
    error: AppColors.red,
    errorEdge: AppColors.redEdge,
    errorTint: AppColors.redTint,
    errorBright: AppColors.redBright,
    reward: AppColors.yellow,
    rewardEdge: AppColors.yellowEdge,
    onReward: AppColors.ink,
    rewardIcon: AppColors.gold,
    streak: AppColors.ember,
    streakTint: AppColors.emberTint,
    streakText: AppColors.emberText,
    life: AppColors.red,
    board: AppColors.ink,
    boardEdge: AppColors.inkEdge,
    boardMuted: Color(0xFFAFC0D6),
    codeText: AppColors.codeText,
    codeKeyword: AppColors.codeKeyword,
    codeBuiltin: AppColors.codeBuiltin,
    codeString: AppColors.codeString,
    codeNumber: AppColors.codeNumber,
    codeComment: AppColors.codeComment,
    codeLineNumber: AppColors.codeLineNumber,
  );

  static const GameColors dark = GameColors(
    background: AppColors.night,
    textMuted: AppColors.nightMuted,
    keyFace: AppColors.nightKey,
    keyEdge: AppColors.nightDeep,
    keyBorder: AppColors.nightLine,
    track: AppColors.nightDeep,
    locked: AppColors.nightKey,
    lockedIcon: AppColors.nightHandle,
    primaryEdge: AppColors.blueEdge,
    primaryTint: Color(0xFF213A5C),
    onPrimary: AppColors.white,
    success: AppColors.green,
    successEdge: AppColors.greenEdge,
    successTint: Color(0xFF173B33),
    successBright: AppColors.greenBright,
    error: AppColors.red,
    errorEdge: AppColors.redEdge,
    errorTint: Color(0xFF3F2230),
    errorBright: AppColors.redBright,
    reward: AppColors.yellow,
    rewardEdge: AppColors.yellowEdge,
    onReward: AppColors.ink,
    rewardIcon: AppColors.yellow,
    streak: AppColors.ember,
    streakTint: Color(0xFF3A2526),
    streakText: AppColors.emberSoft,
    life: AppColors.redBright,
    board: AppColors.nightDeep,
    boardEdge: Color(0xFF070C14),
    boardMuted: AppColors.nightMuted,
    codeText: AppColors.codeText,
    codeKeyword: AppColors.codeKeyword,
    codeBuiltin: AppColors.codeBuiltin,
    codeString: AppColors.codeString,
    codeNumber: AppColors.codeNumber,
    codeComment: AppColors.codeComment,
    codeLineNumber: AppColors.nightHandle,
  );

  /// Night palette with ember as the action color: the timed mode.
  static const GameColors timed = GameColors(
    background: AppColors.night,
    textMuted: AppColors.nightMuted,
    keyFace: AppColors.nightKey,
    keyEdge: AppColors.nightDeep,
    keyBorder: AppColors.nightLine,
    track: AppColors.nightDeep,
    locked: AppColors.nightKey,
    lockedIcon: AppColors.nightHandle,
    primaryEdge: AppColors.emberEdge,
    primaryTint: Color(0xFF3A2526),
    onPrimary: AppColors.onEmber,
    success: AppColors.green,
    successEdge: AppColors.greenEdge,
    successTint: Color(0xFF173B33),
    successBright: AppColors.greenBright,
    error: AppColors.red,
    errorEdge: AppColors.redEdge,
    errorTint: Color(0xFF3F2230),
    errorBright: AppColors.redBright,
    reward: AppColors.yellow,
    rewardEdge: AppColors.yellowEdge,
    onReward: AppColors.ink,
    rewardIcon: AppColors.yellow,
    streak: AppColors.ember,
    streakTint: Color(0xFF3A2526),
    streakText: AppColors.emberSoft,
    life: AppColors.redBright,
    board: AppColors.nightDeep,
    boardEdge: Color(0xFF070C14),
    boardMuted: AppColors.nightMuted,
    codeText: AppColors.codeText,
    codeKeyword: AppColors.codeKeyword,
    codeBuiltin: AppColors.codeBuiltin,
    codeString: AppColors.codeString,
    codeNumber: AppColors.codeNumber,
    codeComment: AppColors.codeComment,
    codeLineNumber: AppColors.nightHandle,
  );

  final Color background;
  final Color textMuted;
  final Color keyFace;
  final Color keyEdge;
  final Color keyBorder;
  final Color track;
  final Color locked;
  final Color lockedIcon;
  final Color primaryEdge;
  final Color primaryTint;
  final Color onPrimary;
  final Color success;
  final Color successEdge;
  final Color successTint;
  final Color successBright;
  final Color error;
  final Color errorEdge;
  final Color errorTint;
  final Color errorBright;
  final Color reward;
  final Color rewardEdge;
  final Color onReward;
  final Color rewardIcon;
  final Color streak;
  final Color streakTint;
  final Color streakText;
  final Color life;
  final Color board;
  final Color boardEdge;
  final Color boardMuted;
  final Color codeText;
  final Color codeKeyword;
  final Color codeBuiltin;
  final Color codeString;
  final Color codeNumber;
  final Color codeComment;
  final Color codeLineNumber;

  List<Color> get _all => [
        background, textMuted, keyFace, keyEdge, keyBorder, track, locked,
        lockedIcon, primaryEdge, primaryTint, onPrimary, success, successEdge,
        successTint, successBright, error, errorEdge, errorTint, errorBright,
        reward, rewardEdge, onReward, rewardIcon, streak, streakTint,
        streakText, life, board, boardEdge, boardMuted, codeText, codeKeyword,
        codeBuiltin, codeString, codeNumber, codeComment, codeLineNumber,
      ];

  static GameColors _fromList(List<Color> c) => GameColors(
        background: c[0],
        textMuted: c[1],
        keyFace: c[2],
        keyEdge: c[3],
        keyBorder: c[4],
        track: c[5],
        locked: c[6],
        lockedIcon: c[7],
        primaryEdge: c[8],
        primaryTint: c[9],
        onPrimary: c[10],
        success: c[11],
        successEdge: c[12],
        successTint: c[13],
        successBright: c[14],
        error: c[15],
        errorEdge: c[16],
        errorTint: c[17],
        errorBright: c[18],
        reward: c[19],
        rewardEdge: c[20],
        onReward: c[21],
        rewardIcon: c[22],
        streak: c[23],
        streakTint: c[24],
        streakText: c[25],
        life: c[26],
        board: c[27],
        boardEdge: c[28],
        boardMuted: c[29],
        codeText: c[30],
        codeKeyword: c[31],
        codeBuiltin: c[32],
        codeString: c[33],
        codeNumber: c[34],
        codeComment: c[35],
        codeLineNumber: c[36],
      );

  @override
  GameColors copyWith({Color? background, Color? primaryEdge}) {
    final values = _all;
    if (background != null) values[0] = background;
    if (primaryEdge != null) values[8] = primaryEdge;
    return _fromList(values);
  }

  @override
  GameColors lerp(covariant ThemeExtension<GameColors>? other, double t) {
    if (other is! GameColors) return this;
    final a = _all;
    final b = other._all;
    return _fromList([
      for (var i = 0; i < a.length; i++) Color.lerp(a[i], b[i], t)!,
    ]);
  }
}

extension GameColorsContext on BuildContext {
  GameColors get gameColors =>
      Theme.of(this).extension<GameColors>() ?? GameColors.light;
}
