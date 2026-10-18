import '../../courses/domain/course.dart';
import '../../courses/domain/level_definition.dart';
import '../../settings/domain/app_settings.dart';
import 'course_progress.dart';

enum UnlockMode {
  /// Every level requires the previous one (beginners).
  linear,

  /// The first level of every module is open; inside a module it's linear.
  /// Lets experienced players skip what they already know.
  modulesOpen;

  static UnlockMode forExperience(ExperienceLevel? experience) =>
      experience == ExperienceLevel.developer ? modulesOpen : linear;
}

/// Decides which levels are playable. Pure and stateless.
///
/// Levels this client can't play (unsupported types) are transparent:
/// they never block the path.
class UnlockPolicy {
  const UnlockPolicy();

  bool isUnlocked(
    Course course,
    CourseProgress progress,
    String levelId, {
    UnlockMode mode = UnlockMode.linear,
  }) {
    final level = course.levelById(levelId);
    if (level == null || !level.isSupported) return false;
    if (progress.isCompleted(levelId)) return true;
    final previous = _previousPlayable(course, levelId);
    if (previous == null) return true;
    if (mode == UnlockMode.modulesOpen && previous.moduleId != level.moduleId) {
      return true;
    }
    return progress.isCompleted(previous.id);
  }

  /// The level the player should play next ("Continue"), or null when the
  /// whole course is completed.
  LevelDefinition? nextToPlay(
    Course course,
    CourseProgress progress, {
    UnlockMode mode = UnlockMode.linear,
  }) {
    for (final level in course.playableLevels) {
      if (!progress.isCompleted(level.id) &&
          isUnlocked(course, progress, level.id, mode: mode)) {
        return level;
      }
    }
    return null;
  }

  /// Next playable level after [levelId] in course order.
  LevelDefinition? nextAfter(Course course, String levelId) {
    final index = course.indexOf(levelId);
    if (index < 0) return null;
    for (var i = index + 1; i < course.levels.length; i++) {
      if (course.levels[i].isSupported) return course.levels[i];
    }
    return null;
  }

  LevelDefinition? _previousPlayable(Course course, String levelId) {
    final index = course.indexOf(levelId);
    for (var i = index - 1; i >= 0; i--) {
      if (course.levels[i].isSupported) return course.levels[i];
    }
    return null;
  }
}
