import '../../../core/storage/game_save_store.dart';
import '../../../core/storage/json_document_store.dart';
import '../../../core/time/clock.dart';
import '../domain/world_state.dart';
import '../domain/world_hearts.dart';
import '../domain/world_challenge.dart';

class WorldRepository {
  WorldRepository(this.documents, this.clock, this.save);
  static const key = 'bytecraft_world_state';
  static const schema = 2;
  final JsonDocumentStore documents;
  final Clock clock;
  final GameSaveStore save;

  Future<WorldState> load() => save.transaction(_load);
  Future<WorldState> _load() async {
    final store = documents;
    final stored = await store.read(key);
    if (stored == null) {
      final legacy = await store.read('player.profile');
      if (legacy == null) return WorldState.initial();
      final lives = legacy['lives'] as Map<String, dynamic>?;
      final streak = legacy['streak'] as Map<String, dynamic>?;
      final count = (lives?['current'] as num?)?.toInt() ?? 3;
      final capacity = count.clamp(3, 7);
      return WorldState.initial().copyWith(
        coins: (legacy['coins'] as num?)?.toInt() ?? 0,
        worldXp: (legacy['totalXp'] as num?)?.toInt() ?? 0,
        cityLevels: {...WorldState.initial().cityLevels, 'servers': capacity - 2},
        hearts: count.clamp(0, capacity),
        heartRegenAnchor: DateTime.tryParse('${lives?['regenAnchor']}'),
        streak: (streak?['current'] as num?)?.toInt() ?? 0,
        lastActiveDay: streak?['lastActiveDay'] as String? ?? '',
      );
    }
    if (stored['schemaVersion'] == schema) {
      final loaded = WorldState.fromJson(stored);
      final current = WorldHearts.regenerate(loaded, clock.now());
      if (!identical(loaded, current)) {
        await store.write(key, current.toJson(), schemaVersion: schema);
      }
      if (current.trainingCurriculumVersion >= DnaCurriculum.revision) return current;
      final migrated = current.copyWith(
        trainingCurriculumVersion: DnaCurriculum.revision,
        solved: Map.fromEntries(current.solved.entries.where((e) => !e.key.startsWith('training:'))),
        failures: Map.fromEntries(current.failures.entries.where((e) => !e.key.startsWith('training:'))),
      );
      await store.write(key, migrated.toJson(), schemaVersion: schema);
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
    await store.write(key, migrated.toJson(), schemaVersion: schema);
    return migrated;
  }

  Future<void> write(WorldState state) => documents.write(
    key, state.toJson(), schemaVersion: schema);
}
