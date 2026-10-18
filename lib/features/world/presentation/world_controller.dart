import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/di/providers.dart';
import '../domain/world_challenge.dart';
import '../domain/world_rules.dart';
import '../domain/world_state.dart';

final worldControllerProvider =
    AsyncNotifierProvider<WorldController, WorldState>(WorldController.new);

class WorldController extends AsyncNotifier<WorldState> {
  static const _key = 'bytecraft_world_state';
  static const _schema = 2;
  Future<void> _pending = Future.value();

  @override
  Future<WorldState> build() async {
    final store = ref.watch(documentStoreProvider);
    final stored = await store.read(_key);
    if (stored == null) return WorldState.initial();
    if (stored['schemaVersion'] == _schema) {
      final current = WorldState.fromJson(stored);
      if (current.trainingCurriculumVersion >= DnaCurriculum.revision) return current;
      final migrated = current.copyWith(
        trainingCurriculumVersion: DnaCurriculum.revision,
        solved: Map.fromEntries(current.solved.entries.where((e) => !e.key.startsWith('training:'))),
        failures: Map.fromEntries(current.failures.entries.where((e) => !e.key.startsWith('training:'))),
      );
      await store.write(_key, migrated.toJson(), schemaVersion: _schema);
      return migrated;
    }
    // v1 contained demo progress and unvalidated click rewards. Keep currency
    // and purchased buildings, but require evidence for quests and records.
    final old = WorldState.fromJson(stored);
    final migrated = WorldState.initial().copyWith(
      showMigrationNotice: true,
      coins: old.coins,
      gems: old.gems,
      cityLevels: {
        for (final id in WorldState.initial().cityLevels.keys)
          id: (old.cityLevels[id] ?? 1).clamp(1, 5),
      },
      hearts: 2 + (old.cityLevels['servers'] ?? 1).clamp(1, 5),
    );
    await store.write(_key, migrated.toJson(), schemaVersion: _schema);
    return migrated;
  }

  /// Serialize read/modify/persist, including rapid taps and different screens.
  Future<T> _serial<T>(Future<T> Function(WorldState) action) {
    final result = Completer<T>();
    _pending = _pending.then((_) async {
      try {
        final current = state.value ?? await future;
        result.complete(await action(current));
      } catch (error, stack) {
        result.completeError(error, stack);
      }
    });
    return result.future;
  }

  Future<void> _set(WorldState next) async {
    // A failed disk write must not leave an earned reward visible in memory.
    await ref
        .read(documentStoreProvider)
        .write(_key, next.toJson(), schemaVersion: _schema);
    state = AsyncData(next);
  }

  Future<WorldSubmission> submitChallenge(
    WorldMode mode,
    String id,
    String answer, {
    String category = 'Условия',
    int? elapsedSeconds,
  }) => _serial((current) async {
    final result = WorldRules.submit(
      current,
      mode,
      id,
      answer,
      ref.read(clockProvider).now(),
      category: category,
      elapsedSeconds: elapsedSeconds,
    );
    if (!identical(result.state, current)) await _set(result.state);
    return result;
  });

  Future<void> recordLessonCompleted({
    required String moduleId,
    required String levelId,
    required int mistakes,
  }) => _serial((current) async {
    final key = 'lesson:$levelId';
    if (current.solved.containsKey(key)) {
      final active = WorldRules.active(current, ref.read(clockProvider).now());
      if (!identical(active, current)) await _set(active);
      return;
    }
    final next = WorldRules.active(
      WorldRules.reward(
        current,
        mistakes == 0 ? 36 : 24,
        mistakes == 0 ? 12 : 8,
        clean: mistakes == 0,
      ),
      ref.read(clockProvider).now(),
    );
    await _set(next.copyWith(solved: {...next.solved, key: 1}));
  });

  Future<void> recordLearningMistake(String moduleId, {String? taskKey, String? topicKey}) =>
      _serial((current) async {
        final category = _mistakeCategory(moduleId);
        await _set(
          current.copyWith(
            failures: {
              ...current.failures,
              for (final key in {taskKey, topicKey}.whereType<String>())
                key: (current.failures[key] ?? 0) + 1,
            },
            mistakes: {
              ...current.mistakes,
              category: (current.mistakes[category] ?? 0) + 1,
            },
          ),
        );
      });

  String _mistakeCategory(String moduleId) {
    if ({'conditions', 'exceptions', 'testing'}.contains(moduleId))
      return 'Условия';
    if ({
      'loops',
      'loops_control',
      'comprehensions',
      'generators',
      'async',
      'concurrency',
    }.contains(moduleId))
      return 'Циклы';
    if ({
      'lists',
      'tuples_sets',
      'dicts',
      'strings',
      'files',
      'textdata',
    }.contains(moduleId))
      return 'Индексы';
    if ({
      'variables',
      'types',
      'operators',
      'io',
      'dataclasses',
      'typing',
      'classes',
      'inheritance',
      'dunder',
      'properties',
    }.contains(moduleId))
      return 'Типы данных';
    return 'Функции';
  }

  Future<void> upgradeBuilding(String id) => _serial((s) async {
    final next = WorldRules.upgrade(s, id);
    if (!identical(s, next)) await _set(next);
  });

  Future<void> claimExpeditionChest() => _serial((s) async {
    if (s.expeditionStep < 5 || s.expeditionChestClaimed) return;
    await _set(
      s.copyWith(
        expeditionChestClaimed: true,
        coins: s.coins + 80,
        gems: s.gems + 2,
        worldXp: s.worldXp + 100,
        seasonXp: s.seasonXp + 100,
      ),
    );
  });

  Future<void> claimSeasonReward() => _serial((s) async {
    final next = WorldRules.claimSeason(s);
    if (!identical(s, next)) await _set(next);
  });

  Future<void> reviveInfinite() => _serial((s) async {
    if (s.gems < 1 || s.hearts > 0) return;
    await _set(s.copyWith(gems: s.gems - 1, hearts: s.maxHearts));
  });

  Future<void> dismissMigrationNotice() =>
      _serial((s) async => _set(s.copyWith(showMigrationNotice: false)));

  Future<void> resetWorld() => _serial((s) async => _set(WorldState.initial()));
}
