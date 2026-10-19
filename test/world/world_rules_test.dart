import 'package:bytecraft/features/world/domain/world_challenge.dart';
import 'package:bytecraft/features/world/domain/world_rules.dart';
import 'package:bytecraft/features/world/domain/world_state.dart';
import 'package:flutter_test/flutter_test.dart';

final now = DateTime(2026, 10, 18, 13);
WorldState solve(WorldState s, WorldMode mode, {String category = 'Условия'}) {
  final q = WorldChallenges.at(s, mode, category: category);
  final result = WorldRules.submit(
    s,
    mode,
    q.id,
    q.answer,
    now,
    category: category,
    elapsedSeconds: 20,
  );
  expect(result.correct, isTrue, reason: result.message);
  return result.state;
}

void main() {
  test('new player has no invented progress, errors, streak or records', () {
    final s = WorldState.initial();
    expect(
      s.coins +
          s.worldXp +
          s.guildTotal +
          s.infiniteRecord +
          s.ghostBestSeconds +
          s.streak,
      0,
    );
    expect(s.completedProjectSteps, 0);
    expect(s.mistakes.values.every((v) => v == 0), isTrue);
  });
  test('direct submissions cannot bypass locked story or side modes', () {
    final s = WorldState.initial();
    for (final mode in [
      WorldMode.project,
      WorldMode.boss,
      WorldMode.guild,
      WorldMode.rival,
      WorldMode.ghost,
    ]) {
      final q = WorldChallenges.at(s, mode);
      final r = WorldRules.submit(
        s,
        mode,
        q.id,
        q.answer,
        now,
        elapsedSeconds: 20,
      );
      expect(r.correct, isFalse);
      expect(r.state, same(s));
    }
  });
  test('empty and incorrect answers never advance or reward', () {
    final s = WorldState.initial();
    final q = WorldChallenges.at(s, WorldMode.expedition);
    for (final input in ['', '  ', 'выполнено', '0', 'None']) {
      final r = WorldRules.submit(s, WorldMode.expedition, q.id, input, now);
      expect(r.correct, isFalse);
      expect(r.state.expeditionStep, 0);
      expect(r.state.coins + r.state.worldXp, 0);
    }
    final wrong = WorldRules.submit(
      s,
      WorldMode.expedition,
      q.id,
      'wrong',
      now,
    );
    expect(wrong.state.mistakes[q.category], 1);
    final retry = solve(wrong.state, WorldMode.expedition);
    expect(retry.worldXp, 17);
    expect(retry.expeditionStep, 1);
  });
  test(
    'story gates require verified code, world questions cannot be replayed',
    () {
      var s = WorldState.initial();
      expect(WorldChallenges.locked(s, WorldMode.project), isNotNull);
      expect(WorldChallenges.locked(s, WorldMode.boss), isNotNull);
      final codes = <String>{};
      for (var i = 0; i < 5; i++) {
        final q = WorldChallenges.at(s, WorldMode.expedition);
        codes.add(q.code);
        final before = s;
        s = solve(s, WorldMode.expedition);
        final replay = WorldRules.submit(
          s,
          WorldMode.expedition,
          q.id,
          q.answer,
          now,
        );
        expect(identical(replay.state, s), isTrue);
        expect(s.worldXp, greaterThan(before.worldXp));
      }
      expect(WorldChallenges.locked(s, WorldMode.project), isNull);
      final legacy = WorldChallenges.at(s, WorldMode.project);
      expect(WorldRules.submit(s, WorldMode.project, legacy.id, legacy.answer, now).correct, isFalse);
      s = s.copyWith(projectSteps: {for (final id in WorldState.projectIds) id: true});
      expect(WorldChallenges.locked(s, WorldMode.boss), isNotNull);
      // The ProjectService tests exercise the code verification that sets this proof.
      s = s.copyWith(hasVerifiedProject: true);
      expect(s.projectUnlocked, isTrue);
      expect(WorldChallenges.locked(s, WorldMode.boss), isNull);
      for (var i = 0; i < 4; i++) {
        codes.add(WorldChallenges.at(s, WorldMode.boss).code);
        s = solve(s, WorldMode.boss);
        expect(s.bossHp, 100 - (i + 1) * 25);
      }
      expect(codes.length, 9);
      expect(s.bossCleared, isTrue);
      final q = WorldChallenges.at(s, WorldMode.boss);
      expect(
        WorldRules.submit(s, WorldMode.boss, q.id, q.answer, now).state,
        same(s),
      );
    },
  );
  test('infinite failure resets series, consumes life, preserves record and blocks zero lives', () {
    var s = solve(
      solve(WorldState.initial(), WorldMode.infinite),
      WorldMode.infinite,
    );
    final q = WorldChallenges.at(s, WorldMode.infinite);
    for (var i = 0; i < 3; i++) {
      s = WorldRules.submit(s, WorldMode.infinite, q.id, 'wrong', now).state;
    }
    expect(s.hearts, 0);
    expect(s.infiniteCurrent, 0);
    expect(s.infiniteRecord, 2);
    expect(
      WorldRules.submit(s, WorldMode.infinite, q.id, q.answer, now).state,
      same(s),
    );
  });
  test(
    'all repeatable modes change code and reject blank/wrong/stale answers',
    () {
      for (final mode in [
        WorldMode.infinite,
        WorldMode.guild,
        WorldMode.rival,
        WorldMode.ghost,
        WorldMode.training,
      ]) {
        var s = WorldState.initial().copyWith(expeditionStep: 2);
        final codes = <String>{};
        for (var n = 0; n < (mode == WorldMode.training ? 20 : 40); n++) {
          final q = WorldChallenges.at(s, mode);
          codes.add(q.code);
          final blank = WorldRules.submit(s, mode, q.id, '', now);
          expect(blank.correct, isFalse);
          expect(blank.state, same(s));
          s = solve(s, mode);
          expect(
            WorldRules.submit(
              s,
              mode,
              q.id,
              q.answer,
              now,
              elapsedSeconds: 20,
            ).state,
            same(s),
          );
        }
        expect(codes.length, mode == WorldMode.training ? 20 : 40, reason: mode.name);
      }
    },
  );
  test('ordinary training retains gaps until independent proof, real times are required', () {
    var s = WorldState.initial().copyWith(
      expeditionStep: 2,
      mistakes: {'Циклы': 2, 'Условия': 3},
    );
    s = solve(s, WorldMode.training, category: 'Циклы');
    expect(s.mistakes['Циклы'], 2); // A solved lesson is not independent proof.
    expect(s.mistakes['Условия'], 3);
    final q = WorldChallenges.at(s, WorldMode.ghost);
    expect(
      WorldRules.submit(s, WorldMode.ghost, q.id, q.answer, now).correct,
      isFalse,
    );
    s = solve(s, WorldMode.ghost);
    expect(s.ghostBestSeconds, 20);
  });
  test('season threshold checked in domain and overflow preserved', () {
    final initial = WorldState.initial();
    expect(WorldRules.claimSeason(initial), same(initial));
    var s = WorldRules.claimSeason(initial.copyWith(seasonXp: 2450));
    expect(s.seasonXp, 1450);
    expect(s.seasonLevel, 2);
    s = WorldRules.claimSeason(s);
    expect(s.seasonXp, 450);
    expect(s.gems, 4);
    expect(WorldRules.claimSeason(s), same(s));
  });
  test(
    'building purchases require XP and coins and change reward/life mechanics',
    () {
      final initial = WorldState.initial().copyWith(coins: 1000);
      expect(WorldRules.upgrade(initial, 'office'), same(initial));
      var s = initial.copyWith(worldXp: 200);
      s = WorldRules.upgrade(s, 'office');
      expect(s.coins, 880);
      expect(s.cityLevels['office'], 2);
      expect(WorldRules.upgrade(s, 'unknown'), same(s));
      s = WorldRules.upgrade(s, 'servers');
      expect(s.maxHearts, 4);
      expect(s.hearts, 4);
      final result = solve(s, WorldMode.infinite);
      expect(result.coins - s.coins, 6);
    },
  );
  test('guild goal earns bonus once and actually finishes', () {
    var s = WorldState.initial().copyWith(expeditionStep: 2, guildTotal: 159);
    s = solve(s, WorldMode.guild);
    expect(s.guildTotal, 160);
    expect(s.worldXp, 180);
    expect(WorldChallenges.finished(s, WorldMode.guild), isTrue);
    final q = WorldChallenges.at(s, WorldMode.guild);
    expect(
      WorldRules.submit(s, WorldMode.guild, q.id, q.answer, now).state,
      same(s),
    );
  });
  test('streak is one increment per calendar day and resets after a gap', () {
    var s = WorldRules.active(WorldState.initial(), now);
    expect(s.streak, 1);
    s = WorldRules.active(s, now);
    expect(s.streak, 1);
    s = WorldRules.active(s, now.add(const Duration(days: 1)));
    expect(s.streak, 2);
    s = WorldRules.active(s, now.add(const Duration(days: 4)));
    expect(s.streak, 1);
  });
}
