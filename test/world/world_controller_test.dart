import 'dart:convert';

import 'package:bytecraft/app/di/providers.dart';
import 'package:bytecraft/core/storage/key_value_store.dart';
import 'package:bytecraft/features/world/domain/world_challenge.dart';
import 'package:bytecraft/features/world/presentation/world_controller.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
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
  test('course replay cannot farm world rewards', () async {
    final c = ProviderContainer(
      overrides: [
        keyValueStoreProvider.overrideWithValue(InMemoryKeyValueStore()),
      ],
    );
    addTearDown(c.dispose);
    await c.read(worldControllerProvider.future);
    final controller = c.read(worldControllerProvider.notifier);
    for (var i = 0; i < 3; i++) {
      await controller.recordLessonCompleted(
        moduleId: 'types',
        levelId: 'python:types_1',
        mistakes: 0,
      );
    }
    expect(c.read(worldControllerProvider).value!.worldXp, 36);
    await controller.recordLessonCompleted(
      moduleId: 'types',
      levelId: 'python:types_2',
      mistakes: 1,
    );
    expect(c.read(worldControllerProvider).value!.worldXp, 60);
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
      jsonDecode((await store.read('bytecraft_world_state'))!)['schemaVersion'],
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
