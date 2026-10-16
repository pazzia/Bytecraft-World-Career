import 'package:bytecraft/features/gamification/domain/game_rules.dart';
import 'package:bytecraft/features/gamification/domain/lives.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  const rules = GameRules.standard;
  const policy = LivesPolicy(rules);
  final t0 = DateTime(2026, 10, 11, 12);
  final regen = rules.lifeRegenInterval;

  test('losing a life from full starts the regeneration timer', () {
    final state = policy.loseLives(LivesState.full(rules), t0);
    expect(state.current, rules.maxLives - 1);
    expect(state.regenAnchor, t0);
  });

  test('never goes below zero', () {
    final state = policy.loseLives(const LivesState(current: 1), t0, amount: 3);
    expect(state.current, 0);
    expect(policy.canPlay(state, t0), isFalse);
  });

  test('regenerates one life per interval and keeps the remainder', () {
    final state = LivesState(current: 1, regenAnchor: t0);
    final later = t0.add(regen * 2 + const Duration(minutes: 5));
    final regenerated = policy.regenerate(state, later);
    expect(regenerated.current, 3);
    expect(regenerated.regenAnchor, t0.add(regen * 2));
  });

  test('caps at max and clears the timer', () {
    final state = LivesState(current: 4, regenAnchor: t0);
    final regenerated = policy.regenerate(state, t0.add(regen * 10));
    expect(regenerated, LivesState(current: rules.maxLives));
  });

  test('does not grant lives when the clock moves backwards', () {
    final state = LivesState(current: 2, regenAnchor: t0);
    final earlier = t0.subtract(const Duration(hours: 5));
    expect(policy.regenerate(state, earlier).current, 2);
  });

  test('empty lives become playable again after the interval', () {
    final state = LivesState(current: 0, regenAnchor: t0);
    expect(policy.canPlay(state, t0), isFalse);
    expect(policy.canPlay(state, t0.add(regen)), isTrue);
  });

  test('reports time to the next life', () {
    final state = LivesState(current: 2, regenAnchor: t0);
    expect(
      policy.timeToNextLife(state, t0.add(const Duration(minutes: 10))),
      regen - const Duration(minutes: 10),
    );
    expect(policy.timeToNextLife(LivesState.full(rules), t0), isNull);
  });

  test('addLives (rewarded ad) is capped at max', () {
    expect(policy.addLives(const LivesState(current: 0), t0).current, 1);
    expect(
      policy.addLives(LivesState.full(rules), t0).current,
      rules.maxLives,
    );
  });

  test('serializes to and from JSON', () {
    final state = LivesState(current: 3, regenAnchor: t0);
    expect(LivesState.fromJson(state.toJson(), rules), state);
  });
}
