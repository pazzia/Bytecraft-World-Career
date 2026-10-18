import '../../../core/time/calendar_day.dart';
import '../../courses/domain/content_repository.dart';
import '../../gamification/domain/game_rules.dart';
import '../../gamification/domain/score_calculators.dart';
import '../../progress/domain/progress_repository.dart';
import '../../progress/domain/unlock_policy.dart';
import '../../settings/domain/settings_repository.dart';
import '../domain/daily_challenge.dart';

/// Deterministically picks one of the player's unlocked levels per day,
/// so the challenge is stable across app restarts and works offline.
class LocalDailyChallengeService implements DailyChallengeService {
  LocalDailyChallengeService({
    required ContentRepository content,
    required ProgressRepository progress,
    required SettingsRepository settings,
    required GameRules rules,
    UnlockPolicy unlockPolicy = const UnlockPolicy(),
  })  : _content = content,
        _progress = progress,
        _settings = settings,
        _rewards = RewardCalculator(rules),
        _unlock = unlockPolicy;

  final ContentRepository _content;
  final ProgressRepository _progress;
  final SettingsRepository _settings;
  final RewardCalculator _rewards;
  final UnlockPolicy _unlock;

  /// Large odd multiplier spreads consecutive days over the level list.
  static const int _dayHashMultiplier = 2654435761;

  @override
  Future<DailyChallenge?> challengeFor(
    CalendarDay day,
    String courseId,
  ) async {
    final course = await _content.loadCourse(courseId);
    final progress = await _progress.loadCourseProgress(courseId);
    final settings = await _settings.load();
    final mode = UnlockMode.forExperience(settings.experience);
    final candidates = course.playableLevels
        .where(
          (level) =>
              _unlock.isUnlocked(course, progress, level.id, mode: mode),
        )
        .toList();
    if (candidates.isEmpty) return null;
    final index = (day.numericKey * _dayHashMultiplier).abs() % candidates.length;
    final profile = await _progress.loadProfile();
    return DailyChallenge(
      day: day,
      level: candidates[index],
      bonus: _rewards.dailyChallengeBonus,
      isCompleted: profile.lastDailyChallengeDay == day,
    );
  }
}
