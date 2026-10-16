import '../../../core/time/calendar_day.dart';
import '../../courses/domain/level_definition.dart';
import '../../gamification/domain/reward.dart';

class DailyChallenge {
  const DailyChallenge({
    required this.day,
    required this.level,
    required this.bonus,
    required this.isCompleted,
  });

  final CalendarDay day;
  final LevelDefinition level;

  /// Extra reward on top of the regular level reward.
  final Reward bonus;
  final bool isCompleted;
}

/// Provides today's challenge. Local implementation picks from bundled
/// content; a backend implementation can serve curated challenges.
abstract interface class DailyChallengeService {
  Future<DailyChallenge?> challengeFor(CalendarDay day, String courseId);
}
