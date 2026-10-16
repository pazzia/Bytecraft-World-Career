import 'level_progress.dart';

/// Player progress inside one course.
///
/// Aggregates (completed count, stars, XP) are derived from per-level
/// records instead of being stored separately, so they can't go out of sync.
class CourseProgress {
  CourseProgress({
    required this.courseId,
    Map<String, LevelProgress> levels = const {},
    this.lastLevelId,
  }) : levels = Map.unmodifiable(levels);

  factory CourseProgress.fromJson(Map<String, dynamic> json) {
    final rawLevels = json['levels'];
    final levels = <String, LevelProgress>{};
    if (rawLevels is List) {
      for (final entry in rawLevels) {
        if (entry is Map<String, dynamic> && entry['levelId'] is String) {
          final progress = LevelProgress.fromJson(entry);
          levels[progress.levelId] = progress;
        }
      }
    }
    final last = json['lastLevelId'];
    return CourseProgress(
      courseId: json['courseId'] as String,
      levels: levels,
      lastLevelId: last is String ? last : null,
    );
  }

  final String courseId;
  final Map<String, LevelProgress> levels;
  final String? lastLevelId;

  LevelProgress levelOf(String levelId) =>
      levels[levelId] ?? LevelProgress(levelId: levelId);

  bool isCompleted(String levelId) => levels[levelId]?.completed ?? false;

  Iterable<LevelProgress> get _completed =>
      levels.values.where((level) => level.completed);

  int get completedCount => _completed.length;

  int get totalStars =>
      _completed.fold(0, (sum, level) => sum + level.bestStars);

  int get totalXp => levels.values.fold(0, (sum, level) => sum + level.xpEarned);

  int get perfectCount => _completed.where((level) => level.isPerfect).length;

  CourseProgress withLevel(LevelProgress progress) => CourseProgress(
        courseId: courseId,
        levels: {...levels, progress.levelId: progress},
        lastLevelId: progress.levelId,
      );

  Map<String, dynamic> toJson() => {
        'courseId': courseId,
        if (lastLevelId != null) 'lastLevelId': lastLevelId,
        'levels': levels.values.map((level) => level.toJson()).toList(),
      };
}
