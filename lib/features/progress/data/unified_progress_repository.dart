import 'dart:math' as math;

import '../../../core/storage/game_save_store.dart';
import '../../../core/storage/json_document_store.dart';
import '../../../core/storage/storage_keys.dart';
import '../../../core/time/calendar_day.dart';
import '../../../core/time/clock.dart';
import '../../../core/utils/id_generator.dart';
import '../../gamification/domain/game_rules.dart';
import '../../gamification/domain/lives.dart';
import '../../gamification/domain/streak.dart';
import '../../world/data/world_repository.dart';
import '../domain/user_profile.dart';
import 'local_progress_repository.dart';

/// Profile metadata and course records share the same atomic save as World.
/// The wallet lives only in World; the profile exposes a read projection.
class UnifiedProgressRepository extends LocalProgressRepository {
  UnifiedProgressRepository({
    required this.documents,
    required this.save,
    required this.world,
    required this.clock,
    required this.rules,
    required this.ids,
  }) : super(documents: documents, clock: clock, rules: rules, ids: ids);

  final JsonDocumentStore documents;
  final GameSaveStore save;
  final WorldRepository world;
  final Clock clock;
  final GameRules rules;
  final IdGenerator ids;

  @override
  Future<UserProfile> loadProfile() => save.transaction(() async {
    final json = await documents.read(StorageKeys.profile);
    if (json == null && await documents.raw.read(StorageKeys.profile) != null) {
      throw StateError('Corrupt player profile');
    }
    if (json != null && json['schemaVersion'] != StorageKeys.profileSchema) {
      throw StateError('Unsupported player profile version');
    }
    final metadata = json != null && json['userId'] is String
        ? UserProfile.fromJson(json, rules)
        : UserProfile.create(userId: ids.newId(), now: clock.now(), rules: rules);
    final wallet = await world.load();
    if (json == null || json.containsKey('totalXp') || json.containsKey('coins')) {
      // Freeze the chosen wallet before retiring the old profile balances.
      // Existing World wins; Career-only installs import their old profile.
      await world.write(wallet);
      await _saveMetadata(metadata);
    }
    return metadata.copyWith(
      totalXp: wallet.worldXp,
      coins: wallet.coins,
      lifeCapacity: wallet.maxHearts,
      lives: LivesState(current: wallet.hearts, regenAnchor: wallet.heartRegenAnchor),
      streak: StreakState(
        current: wallet.streak,
        longest: math.max(metadata.streak.longest, wallet.streak),
        lastActiveDay: CalendarDay.tryParse(wallet.lastActiveDay),
        freezes: metadata.streak.freezes,
      ),
    );
  });

  Future<void> _saveMetadata(UserProfile profile) {
    final json = profile.toJson()
      ..remove('coins')
      ..remove('totalXp')
      ..remove('lives');
    return documents.write(StorageKeys.profile, json, schemaVersion: StorageKeys.profileSchema);
  }

  @override
  Future<void> saveProfile(UserProfile profile) => save.transaction(() async {
    final wallet = await world.load();
    final gainedXp = math.max(0, profile.totalXp - wallet.worldXp);
    await world.write(wallet.copyWith(
      worldXp: profile.totalXp,
      coins: profile.coins,
      seasonXp: wallet.seasonXp + gainedXp,
      hearts: profile.lives.current.clamp(0, wallet.maxHearts),
      heartRegenAnchor: profile.lives.regenAnchor,
      clearHeartRegenAnchor: profile.lives.regenAnchor == null,
      streak: profile.streak.current,
      lastActiveDay: profile.streak.lastActiveDay?.toIso() ?? wallet.lastActiveDay,
    ));
    await _saveMetadata(profile);
    await documents.raw.write(StorageKeys.syncDirty, clock.now().toIso8601String());
  });

  @override
  Future<void> resetAll() => save.transaction(() async {
    await super.resetAll();
    await documents.delete(WorldRepository.key);
    // Do not resurrect a legacy wallet on next launch.
    await world.write(await world.load());
  });
}
