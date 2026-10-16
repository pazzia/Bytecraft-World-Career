import '../../courses/domain/level_definition.dart';
import 'game_rules.dart';
import 'reward.dart';

/// Stars for a completed level from the number of mistakes made.
class StarCalculator {
  const StarCalculator(this.rules);

  static const int maxStars = 3;

  final GameRules rules;

  int starsFor(int mistakes) {
    if (mistakes <= rules.maxMistakesForThreeStars) return maxStars;
    if (mistakes <= rules.maxMistakesForTwoStars) return maxStars - 1;
    return 1;
  }
}

/// XP and coin rewards for completing a level.
class RewardCalculator {
  const RewardCalculator(this.rules);

  static const int _percent = 100;

  final GameRules rules;

  int baseXp(LevelDefinition level) =>
      level.xpOverride ?? rules.xpByRole[level.role] ?? rules.defaultLevelXp;

  int xpFor({
    required LevelDefinition level,
    required int mistakes,
    required bool isFirstCompletion,
  }) {
    final base = baseXp(level);
    if (!isFirstCompletion) {
      return (base * rules.replayXpPercent / _percent).round();
    }
    final isPerfect = mistakes <= rules.maxMistakesForThreeStars;
    return base + (isPerfect ? rules.perfectBonusXp : 0);
  }

  int coinsFor({
    required LevelDefinition level,
    required bool isFirstCompletion,
  }) =>
      isFirstCompletion ? rules.coinsByRole[level.role] ?? 0 : 0;

  Reward completionReward({
    required LevelDefinition level,
    required int mistakes,
    required bool isFirstCompletion,
  }) =>
      Reward(
        xp: xpFor(
          level: level,
          mistakes: mistakes,
          isFirstCompletion: isFirstCompletion,
        ),
        coins: coinsFor(level: level, isFirstCompletion: isFirstCompletion),
      );

  Reward get dailyChallengeBonus => Reward(
        xp: rules.dailyChallengeXpBonus,
        coins: rules.dailyChallengeCoins,
      );
}

/// Account level derived from total XP (never stored, so it can't drift).
class AccountLevel {
  const AccountLevel({
    required this.level,
    required this.xpIntoLevel,
    required this.xpForNextLevel,
  });

  final int level;
  final int xpIntoLevel;
  final int xpForNextLevel;

  double get progress => xpForNextLevel == 0 ? 0 : xpIntoLevel / xpForNextLevel;
}

class AccountLevelCalculator {
  const AccountLevelCalculator(this.rules);

  final GameRules rules;

  AccountLevel levelFor(int totalXp) {
    var level = 1;
    var remaining = totalXp < 0 ? 0 : totalXp;
    while (remaining >= rules.accountLevelXpStep * level) {
      remaining -= rules.accountLevelXpStep * level;
      level++;
    }
    return AccountLevel(
      level: level,
      xpIntoLevel: remaining,
      xpForNextLevel: rules.accountLevelXpStep * level,
    );
  }
}
