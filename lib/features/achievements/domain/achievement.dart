/// What an achievement measures.
enum AchievementMetric {
  levelsCompleted,
  totalXp,
  longestStreak,
  perfectLevels,

  /// Percentage of a course's playable levels completed (needs courseId).
  coursePercent,
}

class Achievement {
  const Achievement({
    required this.id,
    required this.title,
    required this.description,
    required this.icon,
    required this.metric,
    required this.threshold,
    this.courseId,
  });

  final String id;
  final String title;
  final String description;
  final String icon;
  final AchievementMetric metric;
  final int threshold;
  final String? courseId;
}

/// Snapshot of numbers achievements are evaluated against.
class PlayerStats {
  const PlayerStats({
    required this.levelsCompleted,
    required this.totalXp,
    required this.longestStreak,
    required this.perfectLevels,
    this.coursePercent = const {},
  });

  final int levelsCompleted;
  final int totalXp;
  final int longestStreak;
  final int perfectLevels;

  /// courseId -> completion percent (0..100).
  final Map<String, int> coursePercent;

  int valueOf(Achievement achievement) => switch (achievement.metric) {
        AchievementMetric.levelsCompleted => levelsCompleted,
        AchievementMetric.totalXp => totalXp,
        AchievementMetric.longestStreak => longestStreak,
        AchievementMetric.perfectLevels => perfectLevels,
        AchievementMetric.coursePercent =>
          coursePercent[achievement.courseId] ?? 0,
      };
}
