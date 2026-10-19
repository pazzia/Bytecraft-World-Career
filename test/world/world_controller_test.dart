import 'dart:convert';

import 'package:bytecraft/app/di/providers.dart';
import 'package:bytecraft/core/storage/key_value_store.dart';
import 'package:bytecraft/core/storage/game_save_store.dart';
import 'package:bytecraft/features/world/domain/world_challenge.dart';
import 'package:bytecraft/features/world/domain/world_state.dart';
import 'package:bytecraft/features/world/presentation/world_controller.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('duplicate purchase at the displayed price upgrades only once', () async {
    final initial = WorldState.initial().copyWith(coins: 1000, worldXp: 800);
    final store = InMemoryKeyValueStore({'bytecraft_world_state':
      jsonEncode({...initial.toJson(), 'schemaVersion': 2})});
    final c = ProviderContainer(overrides: [keyValueStoreProvider.overrideWithValue(store)]);
    addTearDown(c.dispose);
    await c.read(worldControllerProvider.future);
    final results = await Future.wait(List.generate(10, (_) =>
      c.read(worldControllerProvider.notifier).upgradeBuilding('office', expectedLevel: 1)));
    expect(results.where((purchased) => purchased).length, 1);
    final saved = await c.read(worldRepositoryProvider).load();
    expect(saved.cityLevels['office'], 2);
    expect(saved.coins, 880);
  });
  test('new curriculum resets only old DNA cursors and keeps earned game progress', () async {
    final old = WorldState.initial().copyWith(coins: 91, worldXp: 150, expeditionStep: 3,
      trainingCurriculumVersion: 1,
      solved: {'training:Условия': 73, 'expedition': 3},
      failures: {'training:Условия:73': 2, 'expedition:3': 3});
    final store = InMemoryKeyValueStore({'bytecraft_world_state': jsonEncode({...old.toJson(), 'schemaVersion': 2})});
    final c = ProviderContainer(overrides: [keyValueStoreProvider.overrideWithValue(store)]);
    addTearDown(c.dispose);
    final s = await c.read(worldControllerProvider.future);
    expect(s.trainingCurriculumVersion, DnaCurriculum.revision);
    expect(s.solved, {'expedition': 3});
    expect(s.failures, {'expedition:3': 3});
    expect(s.coins, 91);
    expect(s.worldXp, 150);
    expect(s.expeditionStep, 3);
  });
  test('course error gates persist independently for level and reference topic', () async {
    final store = InMemoryKeyValueStore();
    final c = ProviderContainer(overrides: [keyValueStoreProvider.overrideWithValue(store)]);
    addTearDown(c.dispose);
    await c.read(worldControllerProvider.future);
    for (var n = 0; n < 3; n++) {
      await c.read(worldControllerProvider.notifier).recordLearningMistake('types',
        taskKey: 'lesson:python:types_1', topicKey: 'topic:python:types');
    }
    final restored = ProviderContainer(overrides: [keyValueStoreProvider.overrideWithValue(store)]);
    addTearDown(restored.dispose);
    final s = await restored.read(worldControllerProvider.future);
    expect(s.failures['lesson:python:types_1'], 3);
    expect(s.failures['topic:python:types'], 3);
    expect(s.failures['lesson:python:types_2'], isNull);
  });
  test('rapid duplicate submissions reward once and survive restart', () async {
    final store = InMemoryKeyValueStore();
    final c = ProviderContainer(
      overrides: [keyValueStoreProvider.overrideWithValue(store)],
    );
    addTearDown(c.dispose);
    final s = await c.read(worldControllerProvider.future);
    final q = WorldChallenges.at(s, WorldMode.expedition);
    final results = await Future.wait(
      List.generate(
        12,
        (_) => c
            .read(worldControllerProvider.notifier)
            .submitChallenge(WorldMode.expedition, q.id, q.answer),
      ),
    );
    expect(results.where((r) => r.correct).length, 1);
    expect(c.read(worldControllerProvider).value!.coins, 20);
    final restored = ProviderContainer(
      overrides: [keyValueStoreProvider.overrideWithValue(store)],
    );
    addTearDown(restored.dispose);
    final loaded = await restored.read(worldControllerProvider.future);
    expect(loaded.expeditionStep, 1);
    expect(loaded.coins, 20);
    expect(loaded.solved['expedition'], 1);
  });
  test('chest and season cannot be claimed early or duplicated, revive requires zero lives', () async {
    final store = InMemoryKeyValueStore();
    final c = ProviderContainer(
      overrides: [keyValueStoreProvider.overrideWithValue(store)],
    );
    addTearDown(c.dispose);
    await c.read(worldControllerProvider.future);
    final controller = c.read(worldControllerProvider.notifier);
    await controller.claimExpeditionChest();
    await controller.claimSeasonReward();
    await controller.reviveInfinite();
    expect(c.read(worldControllerProvider).value!.coins, 0);
    expect(c.read(worldControllerProvider).value!.gems, 3);
    for (var i = 0; i < 5; i++) {
      final s = c.read(worldControllerProvider).value!;
      final q = WorldChallenges.at(s, WorldMode.expedition);
      await controller.submitChallenge(WorldMode.expedition, q.id, q.answer);
    }
    await Future.wait(
      List.generate(10, (_) => controller.claimExpeditionChest()),
    );
    final done = c.read(worldControllerProvider).value!;
    expect(done.expeditionChestClaimed, isTrue);
    expect(done.coins, 180);
    expect(done.gems, 5);
    expect(done.worldXp, 275);
  });
  test('legacy unvalidated quest flags reset once, purchased city and course remain', () async {
    final store = InMemoryKeyValueStore({
      'bytecraft_world_state': jsonEncode({
        'schemaVersion': 1,
        'coins': 1300,
        'gems': 15,
        'expeditionStep': 5,
        'bossCleared': true,
        'worldXp': 900,
        'projectSteps': {'basic': true},
        'cityLevels': {
          'office': 2,
          'python': 3,
          'rnd': 1,
          'servers': 2,
          'team': 2,
        },
      }),
      'course:python': 'keep',
    });
    final c = ProviderContainer(
      overrides: [keyValueStoreProvider.overrideWithValue(store)],
    );
    addTearDown(c.dispose);
    final s = await c.read(worldControllerProvider.future);
    expect(s.expeditionStep, 0);
    expect(s.bossCleared, isFalse);
    expect(s.worldXp, 0);
    expect(s.coins, 1300);
    expect(s.cityLevels['python'], 3);
    expect(await store.read('course:python'), 'keep');
    expect(
      jsonDecode((await GameSaveStore(store).read('bytecraft_world_state'))!)['schemaVersion'],
      2,
    );
  });
  test('failed storage write gives no visible completion or reward and permits retry', () async {
    final store = _FailingStore();
    final c = ProviderContainer(
      overrides: [keyValueStoreProvider.overrideWithValue(store)],
    );
    addTearDown(c.dispose);
    final s = await c.read(worldControllerProvider.future);
    final q = WorldChallenges.at(s, WorldMode.expedition);
    final controller = c.read(worldControllerProvider.notifier);
    await expectLater(
      controller.submitChallenge(WorldMode.expedition, q.id, q.answer),
      throwsStateError,
    );
    expect(c.read(worldControllerProvider).value!.expeditionStep, 0);
    store.fail = false;
    final result = await controller.submitChallenge(
      WorldMode.expedition,
      q.id,
      q.answer,
    );
    expect(result.correct, isTrue);
    expect(c.read(worldControllerProvider).value!.expeditionStep, 1);
  });
}

class _FailingStore extends InMemoryKeyValueStore {
  bool fail = true;
  @override
  Future<void> write(String key, String value) async {
    if (fail) throw StateError('disk full');
    await super.write(key, value);
  }
}
