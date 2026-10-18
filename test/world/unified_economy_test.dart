import 'dart:convert';

import 'package:bytecraft/app/di/providers.dart';
import 'package:bytecraft/core/storage/game_save_store.dart';
import 'package:bytecraft/core/storage/key_value_store.dart';
import 'package:bytecraft/core/time/clock.dart';
import 'package:bytecraft/features/level/domain/answer.dart';
import 'package:bytecraft/features/level/domain/level_result.dart';
import 'package:bytecraft/features/world/domain/world_challenge.dart';
import 'package:bytecraft/features/world/domain/world_state.dart';
import 'package:bytecraft/features/world/presentation/world_controller.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/test_env.dart';

void main() {
  final now = DateTime(2026, 10, 19, 12);
  ProviderContainer container(KeyValueStore store, {FixedClock? clock}) => ProviderContainer(overrides: [
    keyValueStoreProvider.overrideWithValue(store),
    clockProvider.overrideWithValue(clock ?? FixedClock(now)),
    contentRepositoryProvider.overrideWithValue(FakeContentRepository(buildTestCourse())),
  ]);

  test('World wallet wins migration; Career-only wallet imports without addition', () async {
    for (final hasWorld in [false, true]) {
      final source = InMemoryKeyValueStore({
        'player.profile': jsonEncode({
          'userId': 'legacy', 'coins': 70, 'totalXp': 150,
          'lives': {'current': 4}, 'schemaVersion': 1,
        }),
        if (hasWorld) 'bytecraft_world_state': jsonEncode({
          ...WorldState.initial().copyWith(coins: 300, worldXp: 800).toJson(),
          'schemaVersion': 2,
        }),
      });
      final c = container(source);
      final profile = await c.read(progressRepositoryProvider).loadProfile();
      expect(profile.coins, hasWorld ? 300 : 70);
      expect(profile.totalXp, hasWorld ? 800 : 150);
      c.dispose();
      final restarted = container(source);
      addTearDown(restarted.dispose);
      final again = await restarted.read(progressRepositoryProvider).loadProfile();
      expect(again.coins, profile.coins);
      expect(again.totalXp, profile.totalXp);
      expect(again.lives.current, hasWorld ? 3 : 4);
    }
  });

  test('one course reward is visible in World and profile, duplicate submission is rejected', () async {
    final source = InMemoryKeyValueStore();
    final c = container(source);
    addTearDown(c.dispose);
    final engine = c.read(levelEngineProvider);
    final start = await engine.start(courseId: 'test', levelId: 'l1');
    final session = (start as LevelStarted).session;
    final results = await Future.wait(List.generate(8, (_) async {
      try { return await engine.submit(session, const ChoiceAnswer(1)); }
      catch (_) { return null; }
    }));
    expect(results.where((r) => r != null).length, 1);
    final result = results.whereType<SubmissionResult>().single.completion!;
    final profile = await c.read(progressRepositoryProvider).loadProfile();
    final world = await c.read(worldRepositoryProvider).load();
    expect(profile.totalXp, result.xpEarned);
    expect(profile.coins, result.coinsEarned);
    expect(world.worldXp, profile.totalXp);
    expect(world.coins, profile.coins);
    expect(world.seasonXp, result.xpEarned);
    final restarted = container(source);
    addTearDown(restarted.dispose);
    expect((await restarted.read(progressRepositoryProvider).loadProfile()).coins, profile.coins);
    expect((await restarted.read(progressRepositoryProvider).loadCourseProgress('test')).isCompleted('l1'), isTrue);
  });

  test('course error, infinite run, paid refill and offline regeneration use one life pool', () async {
    final source = InMemoryKeyValueStore();
    final clock = FixedClock(now);
    final c = container(source, clock: clock);
    addTearDown(c.dispose);
    final engine = c.read(levelEngineProvider);
    final session = (await engine.start(courseId: 'test', levelId: 'l1') as LevelStarted).session;
    await engine.submit(session, const ChoiceAnswer(0));
    expect((await c.read(worldRepositoryProvider).load()).hearts, 2);
    final controller = c.read(worldControllerProvider.notifier);
    final world = await c.read(worldRepositoryProvider).load();
    final task = WorldChallenges.at(world, WorldMode.infinite);
    await controller.submitChallenge(WorldMode.infinite, task.id, 'wrong');
    expect((await c.read(progressRepositoryProvider).loadProfile()).lives.current, 1);
    clock.advance(const Duration(minutes: 30));
    expect((await c.read(progressRepositoryProvider).loadProfile()).lives.current, 2);
    await Future.wait(List.generate(8, (_) => controller.reviveInfinite()));
    expect((await c.read(progressRepositoryProvider).loadProfile()).lives.current, 3);
    expect((await c.read(worldRepositoryProvider).load()).gems, 2);
  });

  test('failed completion commits neither progress nor reward, retry succeeds exactly once', () async {
    final source = _Disk();
    final c = container(source);
    addTearDown(c.dispose);
    final engine = c.read(levelEngineProvider);
    final session = (await engine.start(courseId: 'test', levelId: 'l1') as LevelStarted).session;
    source.fail = true;
    await expectLater(engine.submit(session, const ChoiceAnswer(1)), throwsStateError);
    source.fail = false;
    expect((await c.read(progressRepositoryProvider).loadCourseProgress('test')).isCompleted('l1'), isFalse);
    expect((await c.read(progressRepositoryProvider).loadProfile()).totalXp, 0);
    await engine.submit(session, const ChoiceAnswer(1));
    expect((await c.read(progressRepositoryProvider).loadProfile()).totalXp, 15);
    await expectLater(engine.submit(session, const ChoiceAnswer(1)), throwsA(anything));
    expect((await c.read(progressRepositoryProvider).loadProfile()).totalXp, 15);
    expect(await GameSaveStore(source).read('player.course.test'), isNotNull);
  });
}

class _Disk extends InMemoryKeyValueStore {
  bool fail = false;
  @override
  Future<void> write(String key, String value) async {
    if (fail) throw StateError('disk full');
    await super.write(key, value);
  }
}
