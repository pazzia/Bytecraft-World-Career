import 'dart:math' as math;

import 'game_rules.dart';

/// Persisted lives state.
///
/// [regenAnchor] is the moment from which the next life is counted;
/// null when lives are full. Current lives are always derived lazily via
/// [LivesPolicy.regenerate] — no background timers needed.
class LivesState {
  const LivesState({required this.current, this.regenAnchor});

  factory LivesState.full(GameRules rules) =>
      LivesState(current: rules.maxLives);

  factory LivesState.fromJson(Map<String, dynamic> json, GameRules rules) {
    final current = json['current'];
    final anchor = json['regenAnchor'];
    return LivesState(
      current: current is int ? current : rules.maxLives,
      regenAnchor: anchor is String ? DateTime.tryParse(anchor) : null,
    );
  }

  final int current;
  final DateTime? regenAnchor;

  Map<String, dynamic> toJson() => {
        'current': current,
        if (regenAnchor != null) 'regenAnchor': regenAnchor!.toIso8601String(),
      };

  @override
  bool operator ==(Object other) =>
      other is LivesState &&
      other.current == current &&
      other.regenAnchor == regenAnchor;

  @override
  int get hashCode => Object.hash(current, regenAnchor);

  @override
  String toString() => 'LivesState($current, anchor: $regenAnchor)';
}

class LivesPolicy {
  const LivesPolicy(this.rules, {this.capacity});

  final int? capacity;

  final GameRules rules;

  int get maxLives => capacity ?? rules.maxLives;

  /// Applies time-based regeneration up to [GameRules.maxLives].
  LivesState regenerate(LivesState state, DateTime now) {
    if (state.current >= maxLives) return LivesState(current: maxLives);
    final anchor = state.regenAnchor ?? now;
    final elapsed = now.difference(anchor);
    if (elapsed.isNegative) {
      // Device clock moved backwards: restart the timer, never grant lives.
      return LivesState(current: state.current, regenAnchor: now);
    }
    final interval = rules.lifeRegenInterval;
    final gained = elapsed.inMicroseconds ~/ interval.inMicroseconds;
    if (gained == 0) {
      return LivesState(current: state.current, regenAnchor: anchor);
    }
    final next = math.min(maxLives, state.current + gained);
    if (next >= maxLives) return LivesState(current: maxLives);
    return LivesState(current: next, regenAnchor: anchor.add(interval * gained));
  }

  LivesState loseLives(LivesState state, DateTime now, {int amount = 1}) {
    final current = regenerate(state, now);
    final next = math.max(0, current.current - amount);
    return LivesState(current: next, regenAnchor: current.regenAnchor ?? now);
  }

  LivesState addLives(LivesState state, DateTime now, {int amount = 1}) {
    final current = regenerate(state, now);
    final next = math.min(maxLives, current.current + amount);
    if (next >= maxLives) return LivesState(current: maxLives);
    return LivesState(current: next, regenAnchor: current.regenAnchor);
  }

  bool canPlay(LivesState state, DateTime now) =>
      regenerate(state, now).current > 0;

  /// Time until the next life, or null when lives are full.
  Duration? timeToNextLife(LivesState state, DateTime now) {
    final current = regenerate(state, now);
    final anchor = current.regenAnchor;
    if (current.current >= maxLives || anchor == null) return null;
    return anchor.add(rules.lifeRegenInterval).difference(now);
  }
}
