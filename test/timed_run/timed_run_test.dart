import 'package:bytecraft/features/gamification/domain/game_rules.dart';
import 'package:bytecraft/features/level/domain/answer.dart';
import 'package:bytecraft/features/level/domain/level_result.dart';
import 'package:bytecraft/features/level/domain/level_session.dart';
import 'package:bytecraft/features/settings/domain/app_settings.dart';
import 'package:bytecraft/features/timed_run/domain/timed_run.dart';
import 'package:bytecraft/features/timed_run/domain/timed_run_service.dart';
import 'package:bytecraft/services/analytics/analytics_service.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/test_env.dart';

/// Correct answers for the "basics" module of the test course.
final Map<String, Answer> basicsAnswers = {
  'l1': const ChoiceAnswer(1),
  'l2': FillCodeAnswer(['in']),
  'l3': OrderingAnswer([0, 1, 2]),
};

const Duration step = Duration(seconds: 20);

Future<void> finishBasicsNormally(TestEnv env) async {
  for (final entry in basicsAnswers.entries) {
    final session = await env.startOk(entry.key);
    await env.engine.submit(session, entry.value);
  }
}

/// Plays the whole timed run, advancing the clock by [step] per level.
Future<List<LevelResult>> playRun(TestEnv env) async {
  final results = <LevelResult>[];
  for (final entry in basicsAnswers.entries) {
    final session = await env.startOk(entry.key, mode: LevelMode.timed);
    env.clock.advance(step);
    final result = await env.engine.submit(session, entry.value);
    results.add(result.completion!);
  }
  return results;
}

Future<int> xp(TestEnv env) async => (await env.progress.loadProfile()).totalXp;

void main() {
  const rules = GameRules.standard;
  late TestEnv env;

  setUp(() => env = TestEnv());

  group('availability', () {
    test('a module is locked until finished in normal mode', () async {
      final result = await env.timedRuns.startRun(testCourseId, 'basics');
      expect((result as RunDenied).reason, RunDenial.locked);
    });

    test('experienced developers can race any module', () async {
      await env.settings.save(
        AppSettings.initial(testCourseId)
            .copyWith(experience: ExperienceLevel.developer),
      );
      expect(
        await env.timedRuns.startRun(testCourseId, 'basics'),
        isA<RunStarted>(),
      );
    });
  });

  group('starting levels', () {
    setUp(() => finishBasicsNormally(env));

    test('timed levels need an active run', () async {
      final denied = await env.start('l1', mode: LevelMode.timed);
      expect((denied as LevelStartDenied).reason, LevelStartDenial.noActiveRun);
    });

    test('levels are played in module order', () async {
      await env.timedRuns.startRun(testCourseId, 'basics');
      final skipped = await env.start('l2', mode: LevelMode.timed);
      expect(skipped, isA<LevelStartDenied>());
      expect(await env.start('l1', mode: LevelMode.timed), isA<LevelStarted>());
    });

    test('the clock starts when the run starts, not after level 1', () async {
      final started =
          await env.timedRuns.startRun(testCourseId, 'basics') as RunStarted;
      expect(started.run.startedAt, env.clock.now());
      expect(started.run.totalDuration, const Duration(seconds: 300));
      env.clock.advance(const Duration(seconds: 301));
      final denied = await env.start('l1', mode: LevelMode.timed);
      expect((denied as LevelStartDenied).reason, LevelStartDenial.noActiveRun);
      expect(env.analytics.names, contains(AnalyticsEvent.timedRunFailed));
    });
  });

  group('playing a run', () {
    setUp(() => finishBasicsNormally(env));

    test('answer after the deadline = time up, no XP, no lost life', () async {
      await env.timedRuns.startRun(testCourseId, 'basics');
      final session = await env.startOk('l1', mode: LevelMode.timed);
      final xpBefore = await xp(env);
      env.clock.advance(const Duration(minutes: 6));

      final result = await env.engine.submit(session, const ChoiceAnswer(1));
      expect(result.timeUp, isTrue);
      expect(result.session.isFailed, isTrue);
      expect(result.completion, isNull);
      expect(await xp(env), xpBefore);
      final profile = await env.progress.loadProfile();
      expect(profile.lives.current, rules.maxLives);
      final timed = await env.progress.loadTimedProgress(testCourseId);
      expect(timed.activeRun, isNull);
    });

    test('first clear: doubled XP, speed bonus, coins, best time', () async {
      await env.timedRuns.startRun(testCourseId, 'basics');
      final xpBefore = await xp(env);
      final coinsBefore = (await env.progress.loadProfile()).coins;

      final results = await playRun(env);

      expect(results[0].xpEarned, 15 * 2);
      expect(results[1].xpEarned, 15 * 2);
      expect(results[0].nextLevelId, 'l2');
      expect(results[0].timedRun!.moduleCleared, isFalse);

      final last = results.last;
      final run = last.timedRun!;
      expect(run.moduleCleared, isTrue);
      expect(run.isFirstClear, isTrue);
      expect(run.clearTime, step * 3);
      expect(run.bestTime, step * 3);
      // 240 of 300 seconds left -> 80% of the max bonus.
      expect(run.speedBonus, 80);
      expect(last.xpEarned, 55 * 2 + 80);
      expect(last.coinsEarned, rules.timedFirstClearCoins);
      expect(last.nextLevelId, isNull);

      expect(await xp(env), xpBefore + 30 + 30 + 110 + 80);
      expect(
        (await env.progress.loadProfile()).coins,
        coinsBefore + rules.timedFirstClearCoins,
      );
      final timed = await env.progress.loadTimedProgress(testCourseId);
      expect(timed.activeRun, isNull);
      expect(timed.hasCleared('basics'), isTrue);
      expect(env.analytics.names, contains(AnalyticsEvent.timedRunCompleted));
    });

    test('mistakes reduce timed XP', () async {
      await env.timedRuns.startRun(testCourseId, 'basics');
      final session = await env.startOk('l1', mode: LevelMode.timed);
      final wrong = await env.engine.submit(session, const ChoiceAnswer(0));
      final right =
          await env.engine.submit(wrong.session, const ChoiceAnswer(1));
      expect(right.completion!.stars, 2);
      expect(right.completion!.xpEarned, 10 * 2);
    });

    test('replaying a cleared module gives replay XP only, no bonus', () async {
      await env.timedRuns.startRun(testCourseId, 'basics');
      await playRun(env);

      await env.timedRuns.startRun(testCourseId, 'basics');
      final xpBefore = await xp(env);
      final results = await playRun(env);

      expect(results.map((result) => result.xpEarned), [2, 2, 10]);
      expect(results.last.timedRun!.speedBonus, 0);
      expect(results.last.timedRun!.isFirstClear, isFalse);
      expect(results.last.coinsEarned, 0);
      expect(await xp(env), xpBefore + 14);
    });

    test('regression: an expired run cannot be re-farmed', () async {
      // CodeQuest bug: expiry removed completed levels, so they paid ×2 again.
      await env.timedRuns.startRun(testCourseId, 'basics');
      final session = await env.startOk('l1', mode: LevelMode.timed);
      final first = await env.engine.submit(session, const ChoiceAnswer(1));
      expect(first.completion!.xpEarned, 30);

      env.clock.advance(const Duration(minutes: 10));
      await env.timedRuns.startRun(testCourseId, 'basics');
      final again = await env.startOk('l1', mode: LevelMode.timed);
      final second = await env.engine.submit(again, const ChoiceAnswer(1));
      expect(second.completion!.xpEarned, 2);
    });

    test('a slower clear keeps the best time', () async {
      await env.timedRuns.startRun(testCourseId, 'basics');
      await playRun(env);
      await env.timedRuns.startRun(testCourseId, 'basics');
      env.clock.advance(const Duration(seconds: 30));
      final results = await playRun(env);
      expect(results.last.timedRun!.clearTime, step * 3 + const Duration(seconds: 30));
      expect(results.last.timedRun!.bestTime, step * 3);
      expect(results.last.timedRun!.isNewRecord, isFalse);
    });

    test('starting another run abandons the current one', () async {
      await env.timedRuns.startRun(testCourseId, 'basics');
      await env.timedRuns.startRun(testCourseId, 'basics');
      final failures = env.analytics.events
          .where((event) => event.$1 == AnalyticsEvent.timedRunFailed);
      expect(failures.single.$2['reason'], 'abandoned');
    });
  });

  group('TimedRunPolicy', () {
    const policy = TimedRunPolicy(rules);

    test('speed bonus scales with time left and is capped', () {
      expect(
        policy.speedBonus(
          remaining: const Duration(minutes: 5),
          total: const Duration(minutes: 5),
          isFirstClear: true,
        ),
        rules.timedMaxSpeedBonus,
      );
      expect(
        policy.speedBonus(
          remaining: Duration.zero,
          total: const Duration(minutes: 5),
          isFirstClear: true,
        ),
        0,
      );
      expect(
        policy.speedBonus(
          remaining: const Duration(minutes: 4),
          total: const Duration(minutes: 5),
          isFirstClear: false,
        ),
        0,
      );
    });

    test('modules without their own limit use the default', () {
      final module = buildTestCourse().moduleById('advanced')!;
      expect(policy.durationFor(module), rules.defaultTimedRunDuration);
    });

    test('TimedProgress survives a JSON round trip', () {
      final now = DateTime(2026, 10, 16, 20);
      final progress = TimedProgress(
        courseId: testCourseId,
        activeRun: TimedRun(
          moduleId: 'basics',
          startedAt: now,
          deadline: now.add(const Duration(minutes: 5)),
          completedLevelIds: const ['l1'],
        ),
        everCompletedLevelIds: const {'l1', 'l2'},
        bestTimes: const {'basics': Duration(seconds: 61)},
      );
      final restored = TimedProgress.fromJson(progress.toJson());
      expect(restored.activeRun!.completedLevelIds, ['l1']);
      expect(restored.activeRun!.deadline, now.add(const Duration(minutes: 5)));
      expect(restored.everCompletedLevelIds, {'l1', 'l2'});
      expect(restored.bestTimes['basics'], const Duration(seconds: 61));
    });
  });
}
