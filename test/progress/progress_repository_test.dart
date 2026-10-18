import 'package:bytecraft/core/storage/json_document_store.dart';
import 'package:bytecraft/core/storage/key_value_store.dart';
import 'package:bytecraft/core/storage/storage_keys.dart';
import 'package:bytecraft/core/time/clock.dart';
import 'package:bytecraft/features/gamification/domain/game_rules.dart';
import 'package:bytecraft/features/progress/data/local_progress_repository.dart';
import 'package:bytecraft/features/progress/domain/level_progress.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/test_env.dart';

void main() {
  late InMemoryKeyValueStore store;
  late LocalProgressRepository repository;

  LocalProgressRepository build() => LocalProgressRepository(
        documents: JsonDocumentStore(store),
        clock: FixedClock(DateTime(2026, 10, 11)),
        rules: GameRules.standard,
        ids: FixedIdGenerator(),
      );

  setUp(() {
    store = InMemoryKeyValueStore();
    repository = build();
  });

  test('creates the profile once and persists it', () async {
    final profile = await repository.loadProfile();
    expect(profile.userId, 'user-1');
    expect(profile.lives.current, GameRules.standard.maxLives);
    expect(store.snapshot.containsKey(StorageKeys.profile), isTrue);
    await repository.saveProfile(profile.copyWith(totalXp: 42, coins: 3));
    final reloaded = await build().loadProfile();
    expect(reloaded.totalXp, 42);
    expect(reloaded.coins, 3);
  });

  test('round-trips course progress', () async {
    final progress = await repository.loadCourseProgress(testCourseId);
    await repository.saveCourseProgress(
      progress.withLevel(
        const LevelProgress(levelId: 'l1', completed: true, bestStars: 2),
      ),
    );
    final reloaded = await build().loadCourseProgress(testCourseId);
    expect(reloaded.isCompleted('l1'), isTrue);
    expect(reloaded.levelOf('l1').bestStars, 2);
    expect(reloaded.lastLevelId, 'l1');
  });

  test('marks data dirty for cloud sync on every write', () async {
    await repository.loadProfile();
    expect(store.snapshot.containsKey(StorageKeys.syncDirty), isTrue);
  });

  test('corrupted documents fall back to defaults', () async {
    await store.write(StorageKeys.profile, '{not json');
    await store.write(StorageKeys.courseProgress(testCourseId), '[]');
    expect((await repository.loadProfile()).totalXp, 0);
    expect(
      (await repository.loadCourseProgress(testCourseId)).completedCount,
      0,
    );
  });

  test('resetAll wipes player data only', () async {
    await repository.loadProfile();
    await store.write(StorageKeys.settings, '{}');
    await repository.resetAll();
    expect(store.snapshot.containsKey(StorageKeys.profile), isFalse);
    expect(store.snapshot.containsKey(StorageKeys.settings), isTrue);
  });
}
