/// A local calendar date without time-of-day.
///
/// Day arithmetic is done in UTC on purpose: differences between local
/// midnights can be 23h/25h around DST changes, which breaks `inDays`.
class CalendarDay implements Comparable<CalendarDay> {
  const CalendarDay(this.year, this.month, this.day);

  factory CalendarDay.fromDateTime(DateTime time) =>
      CalendarDay(time.year, time.month, time.day);

  /// Parses `YYYY-MM-DD`. Returns null for malformed input.
  static CalendarDay? tryParse(String? value) {
    if (value == null) return null;
    final parts = value.split('-');
    if (parts.length != 3) return null;
    final year = int.tryParse(parts[0]);
    final month = int.tryParse(parts[1]);
    final day = int.tryParse(parts[2]);
    if (year == null || month == null || day == null) return null;
    return CalendarDay(year, month, day);
  }

  final int year;
  final int month;
  final int day;

  DateTime get _utc => DateTime.utc(year, month, day);

  /// Number of days from this day to [other] (negative if [other] is earlier).
  int daysUntil(CalendarDay other) => other._utc.difference(_utc).inDays;

  CalendarDay addDays(int days) =>
      CalendarDay.fromDateTime(_utc.add(Duration(days: days)));

  /// Stable numeric key, e.g. 20261011. Used for deterministic selection.
  int get numericKey => year * 10000 + month * 100 + day;

  String toIso() => '${year.toString().padLeft(4, '0')}-'
      '${month.toString().padLeft(2, '0')}-'
      '${day.toString().padLeft(2, '0')}';

  @override
  int compareTo(CalendarDay other) => numericKey.compareTo(other.numericKey);

  @override
  bool operator ==(Object other) =>
      other is CalendarDay &&
      other.year == year &&
      other.month == month &&
      other.day == day;

  @override
  int get hashCode => Object.hash(year, month, day);

  @override
  String toString() => toIso();
}
