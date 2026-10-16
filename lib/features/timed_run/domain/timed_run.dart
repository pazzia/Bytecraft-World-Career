import 'dart:math' as math;

import '../../courses/domain/course.dart';
import '../../courses/domain/level_definition.dart';
import '../../gamification/domain/game_rules.dart';
import '../../progress/domain/course_progress.dart';
import '../../progress/domain/unlock_policy.dart';

/// An in-progress timed run of one module ("На время").
///
/// The clock starts when the player presses "Start" — not after the first
/// solved level — so every level of the module is played against time.
class TimedRun {
  TimedRun({
    required this.moduleId,
    required this.startedAt,
    required this.deadline,
    List<String> completedLevelIds = const [],
  }) : completedLevelIds = List.unmodifiable(completedLevelIds);

  factory TimedRun.fromJson(Map<String, dynamic> json) {
    final completed = json['completed'];
    return TimedRun(
      moduleId: json['moduleId'] as String,
      startedAt: DateTime.parse(json['startedAt'] as String),
      deadline: DateTime.parse(json['deadline'] as String),
      completedLevelIds:
          completed is List ? completed.whereType<String>().toList() : const [],
    );
  }

  final String moduleId;
  final DateTime startedAt;
  final DateTime deadline;
  final List<String> completedLevelIds;

  Duration get totalDuration => deadline.difference(startedAt);

  bool isExpired(DateTime now) => !now.isBefore(deadline);

  Duration remaining(DateTime now) {
    final left = deadline.difference(now);
    return left.isNegative ? Duration.zero : left;
  }

  TimedRun withCompleted(String levelId) => TimedRun(
        moduleId: moduleId,
        startedAt: startedAt,
        deadline: deadline,
        completedLevelIds: [...completedLevelIds, levelId],
      );

  Map<String, dynamic> toJson() => {
        'moduleId': moduleId,
        'startedAt': startedAt.toIso8601String(),
        'deadline': deadline.toIso8601String(),
        'completed': completedLevelIds,
      };
}

/// Persisted timed-run state for one course.
///
/// [everCompletedLevelIds] and [bestTimes] are permanent: an expired or
/// abandoned run never removes them. That is what prevents re-farming the
/// boosted first-completion XP and the speed bonus.
class TimedProgress {
  TimedProgress({
    required this.courseId,
    this.activeRun,
    Set<String> everCompletedLevelIds = const <String>{},
    Map<String, Duration> bestTimes = const {},
  })  : everCompletedLevelIds = Set.unmodifiable(everCompletedLevelIds),
        bestTimes = Map.unmodifiable(bestTimes);

  factory TimedProgress.fromJson(Map<String, dynamic> json) {
    final run = json['activeRun'];
    final ever = json['everCompleted'];
    final best = json['bestTimesMs'];
    return TimedProgress(
      courseId: json['courseId'] as String,
      activeRun: run is Map<String, dynamic> ? TimedRun.fromJson(run) : null,
      everCompletedLevelIds:
          ever is List ? ever.whereType<String>().toSet() : const <String>{},
      bestTimes: {
        if (best is Map<String, dynamic>)
          for (final entry in best.entries)
            if (entry.value is int)
              entry.key: Duration(milliseconds: entry.value as int),
      },
    );
  }

  final String courseId;
  final TimedRun? activeRun;
  final Set<String> everCompletedLevelIds;

  /// moduleId -> best clear time. Presence = module cleared at least once.
  final Map<String, Duration> bestTimes;

  bool hasCleared(String moduleId) => bestTimes.containsKey(moduleId);

  TimedProgress copyWith({
    TimedRun? activeRun,
    bool clearRun = false,
    Set<String>? everCompletedLevelIds,
    Map<String, Duration>? bestTimes,
  }) =>
      TimedProgress(
        courseId: courseId,
        activeRun: clearRun ? null : activeRun ?? this.activeRun,
        everCompletedLevelIds:
            everCompletedLevelIds ?? this.everCompletedLevelIds,
        bestTimes: bestTimes ?? this.bestTimes,
      );

  Map<String, dynamic> toJson() => {
        'courseId': courseId,
        if (activeRun != null) 'activeRun': activeRun!.toJson(),
        'everCompleted': everCompletedLevelIds.toList()..sort(),
        'bestTimesMs': {
          for (final entry in bestTimes.entries)
            entry.key: entry.value.inMilliseconds,
        },
      };
}

enum TimedModuleAvailability {
  /// Finish the module in normal mode first.
  locked,
  available,
}

/// Pure rules of timed runs.
class TimedRunPolicy {
  const TimedRunPolicy(this.rules);

  static const int _percent = 100;

  final GameRules rules;

  Duration durationFor(CourseModule module) =>
      module.timedRunDuration ?? rules.defaultTimedRunDuration;

  /// A module can be raced once the player finished it in normal mode
  /// (or skips ahead as an experienced developer). Timed runs are for
  /// consolidating knowledge, not for learning new material under stress.
  TimedModuleAvailability availability(
    CourseModule module,
    CourseProgress progress, {
    UnlockMode mode = UnlockMode.linear,
  }) {
    if (module.playableLevels.isEmpty) return TimedModuleAvailability.locked;
    if (mode == UnlockMode.modulesOpen) return TimedModuleAvailability.available;
    final finished =
        module.playableLevels.every((level) => progress.isCompleted(level.id));
    return finished
        ? TimedModuleAvailability.available
        : TimedModuleAvailability.locked;
  }

  TimedRun startRun(CourseModule module, DateTime now) => TimedRun(
        moduleId: module.id,
        startedAt: now,
        deadline: now.add(durationFor(module)),
      );

  /// Levels are played in module order within a run.
  LevelDefinition? nextLevel(Course course, TimedRun run) {
    final module = course.moduleById(run.moduleId);
    if (module == null) return null;
    for (final level in module.playableLevels) {
      if (!run.completedLevelIds.contains(level.id)) return level;
    }
    return null;
  }

  bool isCleared(Course course, TimedRun run) =>
      nextLevel(course, run) == null;

  /// Drops the active run if its time is up.
  TimedProgress expire(TimedProgress progress, DateTime now) {
    final run = progress.activeRun;
    if (run == null || !run.isExpired(now)) return progress;
    return progress.copyWith(clearRun: true);
  }

  /// Bonus for time left, only on the first-ever clear of a module.
  int speedBonus({
    required Duration remaining,
    required Duration total,
    required bool isFirstClear,
  }) {
    if (!isFirstClear || total <= Duration.zero) return 0;
    final share = remaining.inMilliseconds / total.inMilliseconds;
    final bonus = (rules.timedMaxSpeedBonus * share).round();
    return math.max(0, math.min(rules.timedMaxSpeedBonus, bonus));
  }

  /// Converts a percentage of time left to a whole number (for analytics).
  int percentLeft(Duration remaining, Duration total) => total <= Duration.zero
      ? 0
      : (remaining.inMilliseconds * _percent) ~/ total.inMilliseconds;
}
