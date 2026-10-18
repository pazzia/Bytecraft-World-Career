import 'dart:math' as math;

import '../../../core/time/calendar_day.dart';

class StreakState {
  const StreakState({
    this.current = 0,
    this.longest = 0,
    this.lastActiveDay,
    this.freezes = 0,
  });

  factory StreakState.fromJson(Map<String, dynamic> json) {
    int read(String key) {
      final value = json[key];
      return value is int ? value : 0;
    }

    final last = json['lastActiveDay'];
    return StreakState(
      current: read('current'),
      longest: read('longest'),
      freezes: read('freezes'),
      lastActiveDay: last is String ? CalendarDay.tryParse(last) : null,
    );
  }

  final int current;
  final int longest;
  final CalendarDay? lastActiveDay;

  /// Streak freezes owned; each one covers one missed day.
  final int freezes;

  StreakState copyWith({int? current, int? longest, int? freezes}) =>
      StreakState(
        current: current ?? this.current,
        longest: longest ?? this.longest,
        lastActiveDay: lastActiveDay,
        freezes: freezes ?? this.freezes,
      );

  Map<String, dynamic> toJson() => {
        'current': current,
        'longest': longest,
        'freezes': freezes,
        if (lastActiveDay != null) 'lastActiveDay': lastActiveDay!.toIso(),
      };
}

class StreakUpdate {
  const StreakUpdate({
    required this.state,
    required this.extended,
    required this.wasReset,
    required this.freezesUsed,
  });

  final StreakState state;

  /// True when today's activity increased the streak.
  final bool extended;
  final bool wasReset;
  final int freezesUsed;
}

/// Daily streak rules. Pure functions of (state, today).
class StreakPolicy {
  const StreakPolicy();

  StreakUpdate registerActivity(StreakState state, CalendarDay today) {
    final last = state.lastActiveDay;
    if (last == null) {
      return _extendTo(state, today, current: 1, wasReset: false, used: 0);
    }
    final gap = last.daysUntil(today);
    if (gap <= 0) {
      // Same day (or clock moved back): nothing changes.
      return StreakUpdate(
        state: state,
        extended: false,
        wasReset: false,
        freezesUsed: 0,
      );
    }
    final missedDays = gap - 1;
    if (missedDays == 0) {
      return _extendTo(
        state,
        today,
        current: state.current + 1,
        wasReset: false,
        used: 0,
      );
    }
    if (missedDays <= state.freezes) {
      return _extendTo(
        state,
        today,
        current: state.current + 1,
        wasReset: false,
        used: missedDays,
      );
    }
    return _extendTo(state, today, current: 1, wasReset: true, used: 0);
  }

  StreakUpdate _extendTo(
    StreakState state,
    CalendarDay today, {
    required int current,
    required bool wasReset,
    required int used,
  }) {
    final next = StreakState(
      current: current,
      longest: math.max(state.longest, current),
      lastActiveDay: today,
      freezes: state.freezes - used,
    );
    return StreakUpdate(
      state: next,
      extended: true,
      wasReset: wasReset,
      freezesUsed: used,
    );
  }

  /// Streak value to show today. A streak is alive while today's activity
  /// could still extend it (yesterday active, or missed days covered by
  /// freezes); otherwise it is shown as 0.
  int displayValue(StreakState state, CalendarDay today) {
    final last = state.lastActiveDay;
    if (last == null) return 0;
    final gap = last.daysUntil(today);
    if (gap <= 1) return state.current;
    return gap - 1 <= state.freezes ? state.current : 0;
  }

  bool isActiveToday(StreakState state, CalendarDay today) =>
      state.lastActiveDay == today;
}
