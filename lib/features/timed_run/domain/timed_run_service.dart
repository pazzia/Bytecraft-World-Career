import '../../../core/time/clock.dart';
import '../../../services/analytics/analytics_service.dart';
import '../../courses/domain/content_repository.dart';
import '../../courses/domain/level_definition.dart';
import '../../progress/domain/progress_repository.dart';
import '../../progress/domain/unlock_policy.dart';
import '../../settings/domain/settings_repository.dart';
import 'timed_run.dart';

sealed class StartRunResult {
  const StartRunResult();
}

final class RunStarted extends StartRunResult {
  const RunStarted({required this.run, required this.firstLevel});

  final TimedRun run;
  final LevelDefinition firstLevel;
}

enum RunDenial { moduleNotFound, locked }

final class RunDenied extends StartRunResult {
  const RunDenied(this.reason);

  final RunDenial reason;
}

/// Starts, resumes and abandons timed runs. Level play itself goes through
/// LevelEngine in [LevelMode.timed].
class TimedRunService {
  TimedRunService({
    required ContentRepository content,
    required ProgressRepository progress,
    required SettingsRepository settings,
    required TimedRunPolicy policy,
    required Clock clock,
    required AnalyticsService analytics,
  })  : _content = content,
        _progress = progress,
        _settings = settings,
        _policy = policy,
        _clock = clock,
        _analytics = analytics;

  final ContentRepository _content;
  final ProgressRepository _progress;
  final SettingsRepository _settings;
  final TimedRunPolicy _policy;
  final Clock _clock;
  final AnalyticsService _analytics;

  /// Current state with an overdue run already dropped (and persisted).
  Future<TimedProgress> load(String courseId) async {
    final stored = await _progress.loadTimedProgress(courseId);
    final run = stored.activeRun;
    final current = _policy.expire(stored, _clock.now());
    if (run != null && current.activeRun == null) {
      await _progress.saveTimedProgress(current);
      _analytics.track(AnalyticsEvent.timedRunFailed, {
        'module_id': run.moduleId,
        'reason': 'time_up',
        'completed': run.completedLevelIds.length,
      });
    }
    return current;
  }

  /// Starts a fresh run for [moduleId]. Any other active run is abandoned.
  Future<StartRunResult> startRun(String courseId, String moduleId) async {
    final course = await _content.loadCourse(courseId);
    final module = course.moduleById(moduleId);
    if (module == null) return const RunDenied(RunDenial.moduleNotFound);
    final courseProgress = await _progress.loadCourseProgress(courseId);
    final mode =
        UnlockMode.forExperience((await _settings.load()).experience);
    if (_policy.availability(module, courseProgress, mode: mode) !=
        TimedModuleAvailability.available) {
      return const RunDenied(RunDenial.locked);
    }
    final timed = await load(courseId);
    final previous = timed.activeRun;
    if (previous != null) {
      _analytics.track(AnalyticsEvent.timedRunFailed, {
        'module_id': previous.moduleId,
        'reason': 'abandoned',
        'completed': previous.completedLevelIds.length,
      });
    }
    final run = _policy.startRun(module, _clock.now());
    await _progress.saveTimedProgress(timed.copyWith(activeRun: run));
    _analytics.track(AnalyticsEvent.timedRunStarted, {
      'module_id': moduleId,
      'seconds': run.totalDuration.inSeconds,
    });
    return RunStarted(run: run, firstLevel: module.playableLevels.first);
  }

  /// Next level of the active run in [moduleId], or null if none.
  Future<LevelDefinition?> resume(String courseId, String moduleId) async {
    final timed = await load(courseId);
    final run = timed.activeRun;
    if (run == null || run.moduleId != moduleId) return null;
    return _policy.nextLevel(await _content.loadCourse(courseId), run);
  }

  Future<void> abandon(String courseId) async {
    final timed = await load(courseId);
    final run = timed.activeRun;
    if (run == null) return;
    await _progress.saveTimedProgress(timed.copyWith(clearRun: true));
    _analytics.track(AnalyticsEvent.timedRunFailed, {
      'module_id': run.moduleId,
      'reason': 'abandoned',
      'completed': run.completedLevelIds.length,
    });
  }
}
