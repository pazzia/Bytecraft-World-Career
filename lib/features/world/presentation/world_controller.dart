import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/di/providers.dart';
import '../domain/world_challenge.dart';
import '../domain/world_rules.dart';
import '../domain/world_state.dart';
import '../domain/world_hearts.dart';

final worldControllerProvider =
    AsyncNotifierProvider<WorldController, WorldState>(WorldController.new);

class WorldController extends AsyncNotifier<WorldState> {
  @override
  Future<WorldState> build() {
    ref.listen(gameSaveChangesProvider, (_, __) => ref.invalidateSelf());
    return ref.watch(worldRepositoryProvider).load();
  }

  /// Serialize read/modify/persist, including rapid taps and different screens.
  Future<T> _serial<T>(Future<T> Function(WorldState) action) {
    return ref.read(gameSaveStoreProvider).transaction(() async {
      final current = await ref.read(worldRepositoryProvider).load();
      return action(current);
    }).then((result) async {
      if (ref.mounted) {
        final latest = await ref.read(worldRepositoryProvider).load();
        if (jsonEncode(state.value?.toJson()) != jsonEncode(latest.toJson())) {
          state = AsyncData(latest);
        }
      }
      return result;
    });
  }

  Future<void> _set(WorldState next) => ref.read(worldRepositoryProvider).write(next);

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

  Future<void> recordLearningMistake(String moduleId, {String? taskKey, String? topicKey,
    String? sourceCode, String? title}) =>
      _serial((current) async {
        final category = _mistakeCategory(moduleId);
        await _set(
          WorldRules.recordError(current, skillId: topicKey ?? taskKey ?? 'module:$moduleId',
            title: title ?? moduleId, category: category, sourceCode: sourceCode ?? '').copyWith(
            failures: {
              ...current.failures,
              for (final key in {taskKey, topicKey}.whereType<String>())
                key: (current.failures[key] ?? 0) + 1,
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

  Future<bool> upgradeBuilding(String id, {int? expectedLevel}) => _serial((s) async {
    if (expectedLevel != null && s.cityLevels[id] != expectedLevel) return false;
    final next = WorldRules.upgrade(s, id);
    if (identical(s, next)) return false;
    await _set(next);
    return true;
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

  Future<void> refreshHearts() => _serial((s) async {
    final next = WorldHearts.regenerate(s, ref.read(clockProvider).now());
    if (!identical(s, next)) await _set(next);
  });

  Future<void> reviveInfinite() => _serial((s) async {
    final current = WorldHearts.regenerate(s, ref.read(clockProvider).now());
    if (current.gems < 1 || current.hearts >= current.maxHearts) {
      if (!identical(s, current)) await _set(current);
      return;
    }
    await _set(current.copyWith(
      gems: current.gems - 1,
      hearts: current.maxHearts,
      clearHeartRegenAnchor: true,
    ));
  });

  Future<void> dismissMigrationNotice() =>
      _serial((s) async => _set(s.copyWith(showMigrationNotice: false)));

  Future<void> resetWorld() => _serial((s) async => _set(WorldState.initial()));
}
