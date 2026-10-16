import '../../courses/domain/level_type.dart';

/// All tunable game-economy numbers in one place (no magic constants).
///
/// A remote config / A-B test can later provide a different instance.
class GameRules {
  const GameRules({
    required this.maxLives,
    required this.lifeRegenInterval,
    required this.xpByRole,
    required this.defaultLevelXp,
    required this.perfectBonusXp,
    required this.replayXpPercent,
    required this.coinsByRole,
    required this.maxMistakesForThreeStars,
    required this.maxMistakesForTwoStars,
    required this.accountLevelXpStep,
    required this.dailyChallengeXpBonus,
    required this.dailyChallengeCoins,
    required this.streakFreezePrice,
    required this.maxStreakFreezes,
    required this.livesRefillPrice,
    required this.defaultTimedRunDuration,
    required this.timedXpMultiplier,
    required this.timedMaxSpeedBonus,
    required this.timedFirstClearCoins,
  });

  static const GameRules standard = GameRules(
    maxLives: 5,
    lifeRegenInterval: Duration(minutes: 30),
    xpByRole: {
      LevelRole.lesson: 10,
      LevelRole.practice: 10,
      LevelRole.challenge: 20,
      LevelRole.boss: 50,
    },
    defaultLevelXp: 10,
    perfectBonusXp: 5,
    replayXpPercent: 20,
    coinsByRole: {
      LevelRole.lesson: 1,
      LevelRole.practice: 2,
      LevelRole.challenge: 5,
      LevelRole.boss: 15,
    },
    maxMistakesForThreeStars: 0,
    maxMistakesForTwoStars: 1,
    accountLevelXpStep: 100,
    dailyChallengeXpBonus: 25,
    dailyChallengeCoins: 10,
    streakFreezePrice: 50,
    maxStreakFreezes: 2,
    livesRefillPrice: 30,
    defaultTimedRunDuration: Duration(minutes: 10),
    timedXpMultiplier: 2,
    timedMaxSpeedBonus: 100,
    timedFirstClearCoins: 10,
  );

  final int maxLives;
  final Duration lifeRegenInterval;
  final Map<LevelRole, int> xpByRole;
  final int defaultLevelXp;
  final int perfectBonusXp;

  /// XP granted for replaying a completed level, % of base XP.
  final int replayXpPercent;

  /// Coins granted on first completion.
  final Map<LevelRole, int> coinsByRole;
  final int maxMistakesForThreeStars;
  final int maxMistakesForTwoStars;

  /// Level N -> N+1 requires `accountLevelXpStep * N` XP.
  final int accountLevelXpStep;
  final int dailyChallengeXpBonus;
  final int dailyChallengeCoins;
  final int streakFreezePrice;
  final int maxStreakFreezes;
  final int livesRefillPrice;

  /// Timed runs ("На время"): used when a module has no own limit.
  final Duration defaultTimedRunDuration;

  /// Multiplier for XP of a level's first-ever timed completion.
  final int timedXpMultiplier;

  /// Speed bonus for the first clear of a module, scaled by time left.
  final int timedMaxSpeedBonus;
  final int timedFirstClearCoins;
}
