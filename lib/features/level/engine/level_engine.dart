import '../../../core/errors/app_exception.dart';
import '../../../core/storage/game_save_store.dart';
import '../../../core/utils/id_generator.dart';
import '../../../core/time/calendar_day.dart';
import '../../../core/time/clock.dart';
import '../../../services/analytics/analytics_service.dart';
import '../../../services/feature_flags/feature_flag_service.dart';
import '../../achievements/domain/achievement.dart';
import '../../achievements/domain/achievement_evaluator.dart';
import '../../courses/domain/content_repository.dart';
import '../../courses/domain/course.dart';
import '../../gamification/domain/game_rules.dart';
import '../../gamification/domain/lives.dart';
import '../../gamification/domain/reward.dart';
import '../../gamification/domain/score_calculators.dart';
import '../../gamification/domain/streak.dart';
import '../../progress/domain/course_progress.dart';
import '../../progress/domain/progress_repository.dart';
import '../../progress/domain/unlock_policy.dart';
import '../../progress/domain/user_profile.dart';
import '../../settings/domain/settings_repository.dart';
import '../../timed_run/domain/timed_run.dart';
import '../../timed_run/domain/timed_run_service.dart';
import '../domain/answer.dart';
import '../domain/level_result.dart';
import '../domain/level_session.dart';
import '../domain/validation_outcome.dart';
import 'answer_validator.dart';

/// Orchestrates a level from start to completion.
///
///   start()  -> loads level, checks unlock + lives, records the attempt
///   submit() -> validates, applies lives / XP / stars / streak /
///               achievements, persists progress, unlocks next level
///
/// [LevelMode.timed] levels belong to a timed module run: they are opened in
/// run order instead of by the unlock path, fail when the run's deadline
/// passes, and are rewarded by the timed-run rules.
///
/// UI-agnostic: renderers produce [Answer]s, the engine never touches widgets.
class LevelEngine {
  LevelEngine({
    required ContentRepository content,
    required ProgressRepository progress,
    required SettingsRepository settings,
    required ValidatorRegistry validators,
    required GameRules rules,
    required Clock clock,
    required AnalyticsService analytics,
    required FeatureFlagService flags,
    required TimedRunService timedRuns,
    GameSaveStore? saveStore,
    Future<Reward> Function(Reward, LevelSession, bool)? rewardModifier,
    UnlockPolicy unlockPolicy = const UnlockPolicy(),
    StreakPolicy streakPolicy = const StreakPolicy(),
    AchievementEvaluator achievements = const AchievementEvaluator(),
  })  : _saveStore = saveStore,
        _rewardModifier = rewardModifier,
        _content = content,
        _progress = progress,
        _settings = settings,
        _validators = validators,
        _clock = clock,
        _analytics = analytics,
        _flags = flags,
        _timedRuns = timedRuns,
        _timedPolicy = TimedRunPolicy(rules),
        _rules = rules,
        _unlock = unlockPolicy,
        _streak = streakPolicy,
        _achievements = achievements,
        _lives = LivesPolicy(rules),
        _stars = StarCalculator(rules),
        _rewards = RewardCalculator(rules),
        _accountLevels = AccountLevelCalculator(rules);

  final GameSaveStore? _saveStore;
  final Future<Reward> Function(Reward, LevelSession, bool)? _rewardModifier;
  Future<T> _atomic<T>(Future<T> Function() action) =>
      _saveStore == null ? action() : _saveStore.transaction(action);
  final ContentRepository _content;
  final ProgressRepository _progress;
  final SettingsRepository _settings;
  final ValidatorRegistry _validators;
  final Clock _clock;
  final AnalyticsService _analytics;
  final FeatureFlagService _flags;
  final TimedRunService _timedRuns;
  final TimedRunPolicy _timedPolicy;
  final GameRules _rules;
  final UnlockPolicy _unlock;
  final StreakPolicy _streak;
  final AchievementEvaluator _achievements;
  final LivesPolicy _lives;
  final StarCalculator _stars;
  final RewardCalculator _rewards;
  final AccountLevelCalculator _accountLevels;

  bool _livesActive(UserProfile profile) =>
      _flags.isEnabled(FeatureFlag.lives) && !profile.isPremium;

  LivesSnapshot _livesSnapshot(UserProfile profile, DateTime now, {bool usesLives = true}) =>
      usesLives && _livesActive(profile)
          ? LivesSnapshot.fromState(profile.lives, LivesPolicy(_rules, capacity: profile.lifeCapacity), now)
          : LivesSnapshot.unlimited(profile.lifeCapacity ?? _lives.maxLives);

  Future<UnlockMode> _unlockMode() async =>
      UnlockMode.forExperience((await _settings.load()).experience);

  Future<LevelStartResult> start({
    required String courseId,
    required String levelId,
    LevelMode mode = LevelMode.standard,
  }) => _atomic(() => _start(courseId: courseId, levelId: levelId, mode: mode));

  Future<LevelStartResult> _start({
    required String courseId,
    required String levelId,
    required LevelMode mode,
  }) async {
    final Course course;
    try {
      course = await _content.loadCourse(courseId);
    } on ContentNotFoundException {
      return const LevelStartDenied(LevelStartDenial.notFound);
    }
    final level = course.levelById(levelId);
    if (level == null) return const LevelStartDenied(LevelStartDenial.notFound);
    if (!level.isSupported || !_validators.supports(level.type)) {
      return const LevelStartDenied(LevelStartDenial.unsupported);
    }

    final progress = await _progress.loadCourseProgress(courseId);
    DateTime? deadline;
    DateTime? runStartedAt;
    if (mode == LevelMode.timed) {
      final run = (await _timedRuns.load(courseId)).activeRun;
      if (run == null ||
          run.moduleId != level.moduleId ||
          _timedPolicy.nextLevel(course, run)?.id != levelId) {
        return const LevelStartDenied(LevelStartDenial.noActiveRun);
      }
      deadline = run.deadline;
      runStartedAt = run.startedAt;
    } else {
      final unlockMode = await _unlockMode();
      if (!_unlock.isUnlocked(course, progress, levelId, mode: unlockMode)) {
        return const LevelStartDenied(LevelStartDenial.locked);
      }
    }

    final now = _clock.now();
    final profile = await _progress.loadProfile();
    final previous = progress.levelOf(levelId);
    final usesLives = (mode == LevelMode.standard || mode == LevelMode.dailyChallenge) && !previous.completed;
    final lives = _livesSnapshot(profile, now, usesLives: usesLives);
    if (mode == LevelMode.review && !previous.completed) {
      return const LevelStartDenied(LevelStartDenial.locked);
    }
    if (lives.isEmpty) {
      return LevelStartDenied(LevelStartDenial.noLives, lives: lives);
    }

    await _progress.saveCourseProgress(
      progress.withLevel(
        previous.copyWith(attempts: previous.attempts + 1, lastPlayedAt: now),
      ),
    );

    _analytics.track(
      mode == LevelMode.dailyChallenge
          ? AnalyticsEvent.dailyChallengeStarted
          : AnalyticsEvent.levelStarted,
      {
        'level_id': levelId,
        'type': level.type.id,
        'replay': previous.completed,
        'mode': mode.name,
      },
    );
    return LevelStarted(
      session: LevelSession(
        operationId: RandomIdGenerator().newId(),
        usesLives: usesLives,
        level: level,
        mode: mode,
        startedAt: now,
        deadline: deadline,
        runStartedAt: runStartedAt,
      ),
      lives: lives,
    );
  }

  /// Records hint usage (analytics, future hint limits / AI tutor).
  LevelSession useHint(LevelSession session) {
    _analytics.track(AnalyticsEvent.hintUsed, {'level_id': session.level.id});
    return session.copyWith(hintsUsed: session.hintsUsed + 1);
  }

  Future<SubmissionResult> submit(LevelSession session, Answer answer) => _atomic(() async {
    final receipt = session.operationId == null ? null
        : 'player.receipt.${session.operationId}.${session.submissions}';
    final closed = session.operationId == null ? null : 'player.session.${session.operationId}';
    if (receipt != null && _saveStore != null &&
        (await _saveStore.read(receipt) != null || await _saveStore.read(closed!) != null)) {
      throw const InvalidLevelStateException('Answer already processed');
    }
    final result = await _submit(session, answer);
    if (receipt != null && _saveStore != null) {
      await _saveStore.write(receipt, '1');
      if (result.session.isFinished) await _saveStore.write(closed!, '1');
    }
    return result;
  });

  Future<SubmissionResult> _submit(LevelSession session, Answer answer) async {
    if (session.isFinished) {
      throw const InvalidLevelStateException('Level session already finished');
    }
    final level = session.level;
    if (session.mode == LevelMode.timed && !await _isRunAlive(session)) {
      final profile = await _progress.loadProfile();
      return SubmissionResult(
        session: session.copyWith(isFailed: true),
        outcome: ValidationOutcome.incorrect(),
        lives: _livesSnapshot(profile, _clock.now(), usesLives: session.usesLives),
        timeUp: true,
      );
    }
    final outcome = _validators.validate(level, answer);
    final submitted = session.copyWith(submissions: session.submissions + 1);
    _analytics.track(AnalyticsEvent.answerSubmitted, {
      'level_id': level.id,
      'correct': outcome.isCorrect,
      'attempt': submitted.submissions,
    });

    final now = _clock.now();
    var profile = await _progress.loadProfile();

    if (!outcome.isCorrect) {
      _analytics.track(AnalyticsEvent.wrongAnswer, {'level_id': level.id});
      var failed = false;
      if (session.usesLives && _livesActive(profile)) {
        final lives =
            LivesPolicy(_rules, capacity: profile.lifeCapacity).loseLives(profile.lives, now, amount: level.livesPenalty);
        profile = profile.copyWith(lives: lives, lastActivityAt: now);
        await _progress.saveProfile(profile);
        failed = lives.current <= 0;
      }
      if (failed) {
        _analytics.track(AnalyticsEvent.levelFailed, {'level_id': level.id});
      }
      return SubmissionResult(
        session: submitted.copyWith(
          mistakes: submitted.mistakes + 1,
          isFailed: failed,
        ),
        outcome: outcome,
        lives: _livesSnapshot(profile, now, usesLives: session.usesLives),
      );
    }

    final completion = session.mode == LevelMode.timed
        ? await _completeTimed(submitted, profile, now)
        : await _complete(submitted, profile, now);
    return SubmissionResult(
      session: submitted.copyWith(isCompleted: true),
      outcome: outcome,
      lives: _livesSnapshot(completion.profile, now, usesLives: session.usesLives),
      completion: completion.result,
    );
  }

  Future<({LevelResult result, UserProfile profile})> _complete(
    LevelSession session,
    UserProfile profile,
    DateTime now,
  ) async {
    final level = session.level;
    final course = await _content.loadCourse(level.courseId);
    final mode = await _unlockMode();
    final today = CalendarDay.fromDateTime(now);
    var progress = await _progress.loadCourseProgress(level.courseId);

    final previous = progress.levelOf(level.id);
    final isFirst = !previous.completed;
    final stars = _stars.starsFor(session.mistakes, hintsUsed: session.hintsUsed);
    var reward = _rewards.completionReward(
      level: level,
      mistakes: session.mistakes,
      isFirstCompletion: isFirst,
      hintsUsed: session.hintsUsed,
    );

    final isDaily = session.mode == LevelMode.dailyChallenge &&
        profile.lastDailyChallengeDay != today;
    if (isDaily) reward += _rewards.dailyChallengeBonus;
    if (_rewardModifier != null) reward = await _rewardModifier(reward, session, isFirst);

    final next = _unlock.nextAfter(course, level.id);
    final nextWasUnlocked =
        next != null && _unlock.isUnlocked(course, progress, next.id, mode: mode);

    progress = progress.withLevel(
      previous.copyWith(
        completed: true,
        bestStars: stars > previous.bestStars ? stars : previous.bestStars,
        xpEarned: previous.xpEarned + reward.xp,
        completedAt: previous.completedAt ?? now,
        lastPlayedAt: now,
      ),
    );

    final applied = _applyReward(
      profile,
      reward,
      now,
      course,
      progress,
      isDaily: isDaily,
    );
    profile = applied.profile;
    final streakUpdate = applied.streak;
    final levelBefore = applied.levelBefore;
    final newAchievements = applied.achievements;

    // In the app, progress, wallet and receipt commit in one GameSaveStore write.
    await _progress.saveCourseProgress(progress);
    await _progress.saveProfile(profile);

    _track(level.id, stars, reward, isFirst, streakUpdate, isDaily);

    final newlyUnlocked = next != null &&
            !nextWasUnlocked &&
            _unlock.isUnlocked(course, progress, next.id, mode: mode)
        ? next.id
        : null;

    final result = LevelResult(
      levelId: level.id,
      stars: stars,
      previousBestStars: previous.bestStars,
      xpEarned: reward.xp,
      coinsEarned: reward.coins,
      isFirstCompletion: isFirst,
      streak: profile.streak.current,
      streakExtended: streakUpdate.extended,
      accountLevelBefore: levelBefore,
      accountLevelAfter: _accountLevels.levelFor(profile.totalXp).level,
      completedInCourse: _completedPlayable(course, progress),
      playableInCourse: course.playableLevels.length,
      newAchievements: newAchievements,
      dailyChallengeCompleted: isDaily,
      nextLevelId: next?.id,
      newlyUnlockedLevelId: newlyUnlocked,
    );
    return (result: result, profile: profile);
  }

  /// Whether the run this session belongs to is still running.
  /// Used by the UI when the countdown reaches zero as well.
  Future<bool> isRunAlive(LevelSession session) => _isRunAlive(session);

  Future<bool> _isRunAlive(LevelSession session) async {
    final run = (await _timedRuns.load(session.level.courseId)).activeRun;
    return run != null &&
        run.moduleId == session.level.moduleId &&
        run.deadline == session.deadline &&
        !run.isExpired(_clock.now());
  }

  Future<({LevelResult result, UserProfile profile})> _completeTimed(
    LevelSession session,
    UserProfile profile,
    DateTime now,
  ) async {
    final level = session.level;
    final course = await _content.loadCourse(level.courseId);
    final module = course.moduleById(level.moduleId)!;
    var timed = await _timedRuns.load(level.courseId);
    final active = timed.activeRun;
    if (active == null) {
      throw const InvalidLevelStateException('Timed run ended mid-answer');
    }
    final run = active.withCompleted(level.id);
    final progress = await _progress.loadCourseProgress(level.courseId);

    // Boosted XP only for the first-ever timed completion of a level: an
    // expired run never makes a level "new" again (CodeQuest XP-farm fix).
    final isFirstEver = !timed.everCompletedLevelIds.contains(level.id);
    final stars = _stars.starsFor(session.mistakes, hintsUsed: session.hintsUsed);
    final levelXp = isFirstEver
        ? _rewards.xpFor(
              level: level,
              mistakes: session.mistakes,
              isFirstCompletion: true,
              hintsUsed: session.hintsUsed,
            ) *
            _rules.timedXpMultiplier
        : _rewards.xpFor(
            level: level,
            mistakes: session.mistakes,
            isFirstCompletion: false,
            hintsUsed: session.hintsUsed,
          );

    final cleared = _timedPolicy.isCleared(course, run);
    final isFirstClear = cleared && !timed.hasCleared(module.id);
    var speedBonus = 0;
    var coins = 0;
    Duration? clearTime;
    var bestTimes = timed.bestTimes;
    if (cleared) {
      clearTime = now.difference(run.startedAt);
      speedBonus = _timedPolicy.speedBonus(
        remaining: run.remaining(now),
        total: run.totalDuration,
        isFirstClear: isFirstClear,
      );
      if (isFirstClear) coins = _rules.timedFirstClearCoins;
      final best = bestTimes[module.id];
      if (best == null || clearTime < best) {
        bestTimes = {...bestTimes, module.id: clearTime};
      }
    }
    var reward = Reward(xp: levelXp + speedBonus, coins: coins);
    if (_rewardModifier != null) reward = await _rewardModifier(reward, session, isFirstEver);

    timed = TimedProgress(
      courseId: timed.courseId,
      activeRun: cleared ? null : run,
      everCompletedLevelIds: {...timed.everCompletedLevelIds, level.id},
      bestTimes: bestTimes,
    );
    final applied = _applyReward(profile, reward, now, course, progress);
    await _progress.saveTimedProgress(timed);
    await _progress.saveProfile(applied.profile);

    _track(level.id, stars, reward, isFirstEver, applied.streak, false);
    if (cleared) {
      _analytics.track(AnalyticsEvent.timedRunCompleted, {
        'module_id': module.id,
        'seconds': clearTime!.inSeconds,
        'time_left_percent':
            _timedPolicy.percentLeft(run.remaining(now), run.totalDuration),
        'speed_bonus': speedBonus,
        'first_clear': isFirstClear,
      });
    }

    final result = LevelResult(
      levelId: level.id,
      stars: stars,
      previousBestStars: 0,
      xpEarned: reward.xp,
      coinsEarned: reward.coins,
      isFirstCompletion: isFirstEver,
      streak: applied.profile.streak.current,
      streakExtended: applied.streak.extended,
      accountLevelBefore: applied.levelBefore,
      accountLevelAfter:
          _accountLevels.levelFor(applied.profile.totalXp).level,
      completedInCourse: _completedPlayable(course, progress),
      playableInCourse: course.playableLevels.length,
      newAchievements: applied.achievements,
      dailyChallengeCompleted: false,
      nextLevelId: _timedPolicy.nextLevel(course, run)?.id,
      timedRun: TimedRunProgress(
        moduleId: module.id,
        completedInRun: run.completedLevelIds.length,
        levelsInRun: module.playableLevels.length,
        timeLeft: run.remaining(now),
        moduleCleared: cleared,
        isFirstClear: isFirstClear,
        speedBonus: speedBonus,
        bestTime: bestTimes[module.id],
        clearTime: clearTime,
      ),
    );
    return (result: result, profile: applied.profile);
  }

  /// Applies a reward to the profile: XP, coins, streak, achievements.
  ({
    UserProfile profile,
    StreakUpdate streak,
    int levelBefore,
    List<Achievement> achievements,
  }) _applyReward(
    UserProfile profile,
    Reward reward,
    DateTime now,
    Course course,
    CourseProgress progress, {
    bool isDaily = false,
  }) {
    final today = CalendarDay.fromDateTime(now);
    final streakUpdate = _streak.registerActivity(profile.streak, today);
    final levelBefore = _accountLevels.levelFor(profile.totalXp).level;
    var next = profile.copyWith(
      totalXp: profile.totalXp + reward.xp,
      coins: profile.coins + reward.coins,
      streak: streakUpdate.state,
      lastActivityAt: now,
      lastDailyChallengeDay: isDaily ? today : null,
    );
    final achievements = _achievements.newlyUnlocked(
      _statsFor(next, course, progress),
      next.unlockedAchievements,
    );
    if (achievements.isNotEmpty) {
      next = next.copyWith(
        unlockedAchievements: {
          ...next.unlockedAchievements,
          ...achievements.map((achievement) => achievement.id),
        },
      );
    }
    return (
      profile: next,
      streak: streakUpdate,
      levelBefore: levelBefore,
      achievements: achievements,
    );
  }

  void _track(
    String levelId,
    int stars,
    Reward reward,
    bool isFirst,
    StreakUpdate streak,
    bool isDaily,
  ) {
    _analytics.track(AnalyticsEvent.levelCompleted, {
      'level_id': levelId,
      'stars': stars,
      'xp': reward.xp,
      'first_completion': isFirst,
    });
    if (streak.extended) {
      _analytics.track(
        AnalyticsEvent.streakExtended,
        {'streak': streak.state.current},
      );
    }
    if (isDaily) {
      _analytics.track(
        AnalyticsEvent.dailyChallengeCompleted,
        {'level_id': levelId},
      );
    }
  }

  static int _completedPlayable(Course course, CourseProgress progress) =>
      course.playableLevels
          .where((level) => progress.isCompleted(level.id))
          .length;

  static const int _percent = 100;

  PlayerStats _statsFor(
    UserProfile profile,
    Course course,
    CourseProgress progress,
  ) {
    final playable = course.playableLevels.length;
    final completed = _completedPlayable(course, progress);
    return PlayerStats(
      levelsCompleted: progress.completedCount,
      totalXp: profile.totalXp,
      longestStreak: profile.streak.longest,
      perfectLevels: progress.perfectCount,
      coursePercent: {
        course.id: playable == 0 ? 0 : (completed * _percent) ~/ playable,
      },
    );
  }
}
