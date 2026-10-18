import 'package:bytecraft/features/gamification/domain/game_rules.dart';
import 'package:bytecraft/features/gamification/domain/score_calculators.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/test_env.dart';

void main() {
  const rules = GameRules.standard;
  final course = buildTestCourse();
  final lesson = course.levelById('l1')!;
  final boss = course.levelById('l3')!;

  group('StarCalculator', () {
    const stars = StarCalculator(rules);

    test('first try = 3 stars', () => expect(stars.starsFor(0), 3));
    test('one mistake = 2 stars', () => expect(stars.starsFor(1), 2));
    test('more mistakes = 1 star', () {
      expect(stars.starsFor(2), 1);
      expect(stars.starsFor(10), 1);
    });
  });

  group('RewardCalculator', () {
    const rewards = RewardCalculator(rules);

    test('lesson: base XP + perfect bonus on a flawless first completion', () {
      expect(
        rewards.xpFor(level: lesson, mistakes: 0, isFirstCompletion: true),
        10 + 5,
      );
    });

    test('no perfect bonus after a mistake', () {
      expect(
        rewards.xpFor(level: lesson, mistakes: 1, isFirstCompletion: true),
        10,
      );
    });

    test('boss levels give boss XP', () {
      expect(
        rewards.xpFor(level: boss, mistakes: 0, isFirstCompletion: true),
        50 + 5,
      );
    });

    test('replays give a reduced share of base XP and no coins', () {
      expect(
        rewards.xpFor(level: boss, mistakes: 0, isFirstCompletion: false),
        10,
      );
      expect(rewards.coinsFor(level: boss, isFirstCompletion: false), 0);
    });

    test('first completion grants coins by role', () {
      expect(rewards.coinsFor(level: lesson, isFirstCompletion: true), 1);
      expect(rewards.coinsFor(level: boss, isFirstCompletion: true), 15);
    });
  });

  group('AccountLevelCalculator', () {
    const calculator = AccountLevelCalculator(rules);

    test('levels grow with XP (100, then +200, then +300 ...)', () {
      expect(calculator.levelFor(0).level, 1);
      expect(calculator.levelFor(99).level, 1);
      expect(calculator.levelFor(100).level, 2);
      expect(calculator.levelFor(299).level, 2);
      expect(calculator.levelFor(300).level, 3);
    });

    test('reports progress inside the current level', () {
      final level = calculator.levelFor(150);
      expect(level.xpIntoLevel, 50);
      expect(level.xpForNextLevel, 200);
    });
  });
}
