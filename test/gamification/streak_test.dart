import 'package:bytecraft/core/time/calendar_day.dart';
import 'package:bytecraft/features/gamification/domain/streak.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  const policy = StreakPolicy();
  const day1 = CalendarDay(2026, 10, 11);

  test('first activity starts a streak of 1', () {
    final update = policy.registerActivity(const StreakState(), day1);
    expect(update.state.current, 1);
    expect(update.state.longest, 1);
    expect(update.extended, isTrue);
  });

  test('second activity on the same day changes nothing', () {
    final first = policy.registerActivity(const StreakState(), day1).state;
    final again = policy.registerActivity(first, day1);
    expect(again.extended, isFalse);
    expect(again.state.current, 1);
  });

  test('activity on the next day extends the streak', () {
    var state = policy.registerActivity(const StreakState(), day1).state;
    state = policy.registerActivity(state, day1.addDays(1)).state;
    state = policy.registerActivity(state, day1.addDays(2)).state;
    expect(state.current, 3);
    expect(state.longest, 3);
  });

  test('missing a day resets the streak but keeps the record', () {
    var state = policy.registerActivity(const StreakState(), day1).state;
    state = policy.registerActivity(state, day1.addDays(1)).state;
    final update = policy.registerActivity(state, day1.addDays(3));
    expect(update.wasReset, isTrue);
    expect(update.state.current, 1);
    expect(update.state.longest, 2);
  });

  test('a streak freeze covers a missed day and is consumed', () {
    const state = StreakState(current: 5, longest: 5, lastActiveDay: day1, freezes: 1);
    final update = policy.registerActivity(state, day1.addDays(2));
    expect(update.wasReset, isFalse);
    expect(update.freezesUsed, 1);
    expect(update.state.current, 6);
    expect(update.state.freezes, 0);
  });

  test('works across month boundaries and DST dates', () {
    const lastOfMonth = CalendarDay(2026, 10, 31);
    final state = policy.registerActivity(const StreakState(), lastOfMonth).state;
    final next = policy.registerActivity(state, const CalendarDay(2026, 11, 1));
    expect(next.state.current, 2);
    // 2026-10-25 is a DST switch in Europe.
    expect(const CalendarDay(2026, 10, 25).daysUntil(const CalendarDay(2026, 10, 26)), 1);
  });

  group('displayValue', () {
    const state = StreakState(current: 4, longest: 4, lastActiveDay: day1);

    test('shows the streak on the active day and the day after', () {
      expect(policy.displayValue(state, day1), 4);
      expect(policy.displayValue(state, day1.addDays(1)), 4);
    });

    test('shows 0 once the streak is broken', () {
      expect(policy.displayValue(state, day1.addDays(2)), 0);
    });

    test('a freeze keeps the streak visible', () {
      expect(
        policy.displayValue(state.copyWith(freezes: 1), day1.addDays(2)),
        4,
      );
    });
  });

  test('serializes to and from JSON', () {
    const state = StreakState(current: 3, longest: 7, lastActiveDay: day1, freezes: 1);
    final restored = StreakState.fromJson(state.toJson());
    expect(restored.current, 3);
    expect(restored.longest, 7);
    expect(restored.freezes, 1);
    expect(restored.lastActiveDay, day1);
  });
}
