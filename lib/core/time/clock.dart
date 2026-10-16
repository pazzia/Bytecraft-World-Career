/// Abstraction over the current time so that time-dependent rules
/// (lives regeneration, streaks, daily challenges) are deterministic in tests.
abstract interface class Clock {
  DateTime now();
}

class SystemClock implements Clock {
  const SystemClock();

  @override
  DateTime now() => DateTime.now();
}

/// Manually controlled clock. Useful in tests and debug tooling.
class FixedClock implements Clock {
  FixedClock(this._now);

  DateTime _now;

  @override
  DateTime now() => _now;

  void set(DateTime value) => _now = value;

  void advance(Duration duration) => _now = _now.add(duration);
}
