import 'world_state.dart';

/// A persisted anchor preserves partial progress and works while the app is closed.
abstract final class WorldHearts {
  static const interval = Duration(minutes: 30);

  static WorldState regenerate(WorldState s, DateTime now) {
    final hearts = s.hearts.clamp(0, s.maxHearts);
    if (hearts == s.maxHearts) {
      if (s.hearts == hearts && s.heartRegenAnchor == null) return s;
      return s.copyWith(hearts: hearts, clearHeartRegenAnchor: true);
    }
    final anchor = s.heartRegenAnchor;
    if (anchor == null || now.isBefore(anchor)) {
      return s.copyWith(hearts: hearts, heartRegenAnchor: now);
    }
    final gained = now.difference(anchor).inMilliseconds ~/ interval.inMilliseconds;
    if (gained == 0 && hearts == s.hearts) return s;
    final next = (hearts + gained).clamp(0, s.maxHearts);
    return s.copyWith(
      hearts: next,
      heartRegenAnchor: anchor.add(interval * gained),
      clearHeartRegenAnchor: next == s.maxHearts,
    );
  }

  static WorldState lose(WorldState s, DateTime now) {
    final current = regenerate(s, now);
    if (current.hearts == 0) return current;
    return current.copyWith(
      hearts: current.hearts - 1,
      heartRegenAnchor: current.heartRegenAnchor ?? now,
    );
  }

  static Duration? nextIn(WorldState s, DateTime now) {
    final current = regenerate(s, now);
    if (current.hearts == current.maxHearts) return null;
    return interval - now.difference(current.heartRegenAnchor!);
  }

  static String countdown(Duration duration) {
    final seconds = (duration.inMilliseconds / 1000).ceil().clamp(0, 999999);
    return '${seconds ~/ 60}:${(seconds % 60).toString().padLeft(2, '0')}';
  }
}
