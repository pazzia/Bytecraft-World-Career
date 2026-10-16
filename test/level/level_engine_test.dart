import 'package:bytecraft/core/errors/app_exception.dart';
import 'package:bytecraft/core/storage/key_value_store.dart';
import 'package:bytecraft/features/level/domain/answer.dart';
import 'package:bytecraft/features/level/domain/level_result.dart';
import 'package:bytecraft/features/level/domain/level_session.dart';
import 'package:bytecraft/features/gamification/domain/lives.dart';
import 'package:bytecraft/services/analytics/analytics_service.dart';
import 'package:bytecraft/services/feature_flags/feature_flag_service.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/test_env.dart';

void main() {
  late TestEnv env;

  setUp(() => env = TestEnv());

  group('start', () {
    test('first level starts and records an attempt', () async {
      final result = await env.start('l1');
      expect(result, isA<LevelStarted>());
      final progress = await env.progress.loadCourseProgress(testCourseId);
      expect(progress.levelOf('l1').attempts, 1);
      expect(env.analytics.names, contains(AnalyticsEvent.levelStarted));
    });

    test('locked level is denied', () async {
      final result = await env.start('l2');
      expect(result, isA<LevelStartDenied>());
      expect((result as LevelStartDenied).reason, LevelStartDenial.locked);
    });

    test('unknown and unsupported levels are denied', () async {
      expect(
        ((await env.start('nope')) as LevelStartDenied).reason,
        LevelStartDenial.notFound,
      );
      expect(
        ((await env.start('l5')) as LevelStartDenied).reason,
        LevelStartDenial.unsupported,
      );
    });
  });

  group('correct answer', () {
    test('completes the level with XP, stars, coins, streak', () async {
      final session = await env.startOk('l1');
      final result = await env.engine.submit(session, const ChoiceAnswer(1));

      expect(result.outcome.isCorrect, isTrue);
      expect(result.session.isCompleted, isTrue);
      final completion = result.completion!;
      expect(completion.stars, 3);
      expect(completion.xpEarned, 15);
      expect(completion.coinsEarned, 1);
      expect(completion.isFirstCompletion, isTrue);
      expect(completion.streak, 1);
      expect(completion.streakExtended, isTrue);
      expect(completion.nextLevelId, 'l2');
      expect(completion.newlyUnlockedLevelId, 'l2');

      final profile = await env.progress.loadProfile();
      expect(profile.totalXp, 15);
      expect(profile.coins, 1);
      expect(profile.lives.current, env.rules.maxLives);
      expect(profile.streak.current, 1);
      expect(profile.unlockedAchievements, containsAll(['first_code', 'perfect_level']));

      final progress = await env.progress.loadCourseProgress(testCourseId);
      expect(progress.isCompleted('l1'), isTrue);
      expect(progress.levelOf('l1').bestStars, 3);
      expect(env.analytics.names, contains(AnalyticsEvent.levelCompleted));
    });

    test('next level becomes playable', () async {
      final session = await env.startOk('l1');
      await env.engine.submit(session, const ChoiceAnswer(1));
      expect(await env.start('l2'), isA<LevelStarted>());
    });
  });

  group('wrong answer', () {
    test('costs a life and lowers the stars', () async {
      var session = await env.startOk('l1');
      final wrong = await env.engine.submit(session, const ChoiceAnswer(0));
      expect(wrong.outcome.isCorrect, isFalse);
      expect(wrong.completion, isNull);
      expect(wrong.lives.current, env.rules.maxLives - 1);
      expect(wrong.session.mistakes, 1);
      expect(env.analytics.names, contains(AnalyticsEvent.wrongAnswer));

      session = wrong.session;
      final right = await env.engine.submit(session, const ChoiceAnswer(1));
      expect(right.completion!.stars, 2);
      expect(right.completion!.xpEarned, 10, reason: 'no perfect bonus');

      final profile = await env.progress.loadProfile();
      expect(profile.lives.current, env.rules.maxLives - 1);
    });

    test('losing the last life fails the level and blocks new starts', () async {
      final profile = await env.progress.loadProfile();
      await env.progress.saveProfile(
        profile.copyWith(lives: const LivesState(current: 1)),
      );
      final session = await env.startOk('l1');
      final result = await env.engine.submit(session, const ChoiceAnswer(0));
      expect(result.isFailed, isTrue);
      expect(result.lives.isEmpty, isTrue);
      expect(env.analytics.names, contains(AnalyticsEvent.levelFailed));

      final denied = await env.start('l1');
      expect((denied as LevelStartDenied).reason, LevelStartDenial.noLives);

      env.clock.advance(env.rules.lifeRegenInterval);
      expect(await env.start('l1'), isA<LevelStarted>());
    });

    test('premium players do not lose lives', () async {
      final profile = await env.progress.loadProfile();
      await env.progress.saveProfile(profile.copyWith(isPremium: true));
      final session = await env.startOk('l1');
      final result = await env.engine.submit(session, const ChoiceAnswer(0));
      expect(result.lives.isUnlimited, isTrue);
      expect((await env.progress.loadProfile()).lives.current, env.rules.maxLives);
    });

    test('lives can be disabled by feature flag', () async {
      env = TestEnv(flags: {FeatureFlag.lives: false});
      final session = await env.startOk('l1');
      final result = await env.engine.submit(session, const ChoiceAnswer(0));
      expect(result.lives.isUnlimited, isTrue);
      expect((await env.progress.loadProfile()).lives.current, env.rules.maxLives);
    });
  });

  group('replay', () {
    test('gives reduced XP, no coins, keeps best stars', () async {
      var session = await env.startOk('l1');
      await env.engine.submit(session, const ChoiceAnswer(1));

      session = await env.startOk('l1');
      final wrong = await env.engine.submit(session, const ChoiceAnswer(0));
      final replay = await env.engine.submit(wrong.session, const ChoiceAnswer(1));

      final completion = replay.completion!;
      expect(completion.isFirstCompletion, isFalse);
      expect(completion.xpEarned, 2);
      expect(completion.coinsEarned, 0);
      expect(completion.stars, 2);
      expect(completion.newlyUnlockedLevelId, isNull);

      final progress = await env.progress.loadCourseProgress(testCourseId);
      expect(progress.levelOf('l1').bestStars, 3);
      expect(progress.levelOf('l1').xpEarned, 17);
      expect(progress.levelOf('l1').attempts, 2);
      expect((await env.progress.loadProfile()).totalXp, 17);
    });
  });

  test('finished sessions reject further answers', () async {
    final session = await env.startOk('l1');
    final result = await env.engine.submit(session, const ChoiceAnswer(1));
    await expectLater(
      env.engine.submit(result.session, const ChoiceAnswer(1)),
      throwsA(isA<InvalidLevelStateException>()),
    );
  });

  test('daily challenge bonus is granted once per day', () async {
    var session = await env.startOk('l1', mode: LevelMode.dailyChallenge);
    final first = await env.engine.submit(session, const ChoiceAnswer(1));
    expect(first.completion!.dailyChallengeCompleted, isTrue);
    expect(
      first.completion!.xpEarned,
      15 + env.rules.dailyChallengeXpBonus,
    );
    expect(first.completion!.coinsEarned, 1 + env.rules.dailyChallengeCoins);

    session = await env.startOk('l1', mode: LevelMode.dailyChallenge);
    final second = await env.engine.submit(session, const ChoiceAnswer(1));
    expect(second.completion!.dailyChallengeCompleted, isFalse);
    expect(second.completion!.xpEarned, 2);
  });

  test('streak grows on consecutive days', () async {
    var session = await env.startOk('l1');
    await env.engine.submit(session, const ChoiceAnswer(1));
    env.clock.advance(const Duration(days: 1));
    session = await env.startOk('l2');
    final result = await env.engine.submit(session, FillCodeAnswer(['in']));
    expect(result.completion!.streak, 2);
  });

  test('progress survives an app restart (new engine, same storage)', () async {
    final store = InMemoryKeyValueStore();
    final first = TestEnv(store: store);
    final session = await first.startOk('l1');
    await first.engine.submit(session, const ChoiceAnswer(1));

    final restarted = TestEnv(store: store);
    final profile = await restarted.progress.loadProfile();
    expect(profile.userId, 'user-1');
    expect(profile.totalXp, 15);
    expect(await restarted.start('l2'), isA<LevelStarted>());
  });

  test('boss completion unlocks the next module', () async {
    for (final (id, answer) in [
      ('l1', const ChoiceAnswer(1)),
      ('l2', FillCodeAnswer(['in'])),
      ('l3', OrderingAnswer([1, 0, 2])),
    ]) {
      final session = await env.startOk(id);
      await env.engine.submit(session, answer);
    }
    expect(await env.start('l4'), isA<LevelStarted>());
    final profile = await env.progress.loadProfile();
    expect(profile.totalXp, 15 + 15 + 55);
  });
}
