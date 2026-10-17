import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/di/providers.dart';
import '../domain/world_state.dart';

final worldControllerProvider =
    AsyncNotifierProvider<WorldController, WorldState>(WorldController.new);

class WorldController extends AsyncNotifier<WorldState> {
  static const _key = 'bytecraft_world_state';
  static const _schema = 1;

  @override
  Future<WorldState> build() async {
    final stored = await ref.watch(documentStoreProvider).read(_key);
    if (stored == null) return WorldState.initial();
    return WorldState.fromJson(stored);
  }

  Future<void> _set(WorldState next) async {
    state = AsyncData(next);
    await ref.read(documentStoreProvider).write(
          _key,
          next.toJson(),
          schemaVersion: _schema,
        );
  }

  Future<WorldState> _current() async => state.value ?? await future;

  Future<void> upgradeBuilding(String id) async {
    final current = await _current();
    final level = current.cityLevels[id] ?? 1;
    final cost = 80 + level * 40;
    if (current.coins < cost) return;
    await _set(
      current.copyWith(
        coins: current.coins - cost,
        worldXp: current.worldXp + 20,
        cityLevels: {...current.cityLevels, id: level + 1},
      ),
    );
  }

  Future<void> advanceExpedition() async {
    final current = await _current();
    if (current.expeditionStep >= 5) return;
    final nextStep = current.expeditionStep + 1;
    await _set(
      current.copyWith(
        expeditionStep: nextStep,
        coins: current.coins + 20,
        worldXp: current.worldXp + 35,
        seasonXp: current.seasonXp + 35,
      ),
    );
  }

  Future<void> claimExpeditionChest() async {
    final current = await _current();
    if (current.expeditionStep < 5 || current.expeditionChestClaimed) return;
    await _set(
      current.copyWith(
        expeditionChestClaimed: true,
        coins: current.coins + 80,
        gems: current.gems + 2,
        worldXp: current.worldXp + 100,
        seasonXp: current.seasonXp + 100,
      ),
    );
  }

  Future<void> attackBoss() async {
    final current = await _current();
    if (current.bossCleared) return;
    final hp = (current.bossHp - 25).clamp(0, 100).toInt();
    final cleared = hp == 0;
    await _set(
      current.copyWith(
        bossHp: hp,
        bossTask: (current.bossTask + 1).clamp(0, 5).toInt(),
        bossCleared: cleared,
        coins: current.coins + (cleared ? 120 : 20),
        worldXp: current.worldXp + (cleared ? 180 : 45),
        seasonXp: current.seasonXp + (cleared ? 180 : 45),
      ),
    );
  }

  Future<void> resetBoss() async {
    final current = await _current();
    await _set(current.copyWith(bossHp: 100, bossTask: 0, bossCleared: false));
  }

  Future<void> submitGhostRun() async {
    final current = await _current();
    final improved = (current.ghostBestSeconds - 17).clamp(125, 999).toInt();
    await _set(
      current.copyWith(
        ghostBestSeconds: improved,
        coins: current.coins + 15,
        worldXp: current.worldXp + 30,
      ),
    );
  }

  Future<void> contributeGuild() async {
    final current = await _current();
    await _set(
      current.copyWith(
        guildContribution: current.guildContribution + 8,
        guildTotal: current.guildTotal + 8,
        worldXp: current.worldXp + 25,
      ),
    );
  }

  Future<void> beatRival() async {
    final current = await _current();
    await _set(
      current.copyWith(
        rivalWins: current.rivalWins + 1,
        coins: current.coins + 25,
        worldXp: current.worldXp + 55,
        seasonXp: current.seasonXp + 55,
      ),
    );
  }

  Future<void> trainMistake(String category) async {
    final current = await _current();
    final old = current.mistakes[category] ?? 0;
    if (old <= 0) return;
    final next = <String, int>{
      ...current.mistakes,
      category: (old - 4).clamp(0, 100).toInt(),
    };
    await _set(
      current.copyWith(
        mistakes: next,
        worldXp: current.worldXp + 30,
        seasonXp: current.seasonXp + 30,
      ),
    );
  }

  Future<void> toggleProjectStep(String id) async {
    final current = await _current();
    final next = <String, bool>{
      ...current.projectSteps,
      id: !(current.projectSteps[id] ?? false),
    };
    await _set(current.copyWith(projectSteps: next));
  }

  Future<void> claimSeasonReward() async {
    final current = await _current();
    final nextLevel = current.seasonLevel + 1;
    await _set(
      current.copyWith(
        seasonLevel: nextLevel,
        seasonXp: 0,
        coins: current.coins + 60,
        gems: current.gems + (nextLevel % 3 == 0 ? 1 : 0),
      ),
    );
  }

  Future<void> solveInfinite() async {
    final current = await _current();
    final nextRun = current.infiniteCurrent + 1;
    await _set(
      current.copyWith(
        infiniteCurrent: nextRun,
        infiniteRecord: nextRun > current.infiniteRecord
            ? nextRun
            : current.infiniteRecord,
        worldXp: current.worldXp + 20 + nextRun,
        seasonXp: current.seasonXp + 20 + nextRun,
        coins: current.coins + 5,
      ),
    );
  }

  Future<void> failInfinite() async {
    final current = await _current();
    if (current.hearts <= 0) return;
    await _set(
      current.copyWith(
        hearts: current.hearts - 1,
        infiniteCurrent: 0,
      ),
    );
  }

  Future<void> reviveInfinite() async {
    final current = await _current();
    if (current.gems < 1) return;
    await _set(current.copyWith(gems: current.gems - 1, hearts: 3));
  }

  Future<void> resetWorld() async {
    await ref.read(documentStoreProvider).delete(_key);
    state = AsyncData(WorldState.initial());
  }
}
