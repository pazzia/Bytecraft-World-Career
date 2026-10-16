import '../../../core/errors/app_exception.dart';
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
import '../domain/answer.dart';
import '../domain/level_result.dart';
import '../domain/level_session.dart';
import 'answer_validator.dart';

/// Orchestrates a level from start to completion.
///
///   start()  -> loads level, checks unlock + lives, records the attempt
///   submit() -> validates, applies lives / XP / stars / streak /
///               achievements, persists progress, unlocks next level
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
    UnlockPolicy unlockPolicy = const UnlockPolicy(),
    StreakPolicy streakPolicy = const StreakPolicy(),
    AchievementEvaluator achievements = const AchievementEvaluator(),
  })  : _content = content,
        _progress = progress,
        _settings = settings,
        _validators = validators,
        _clock = clock,
        _analytics = analytics,
        _flags = flags,
        _unlock = unlockPolicy,
        _streak = streakPolicy,
        _achievements = achievements,
        _lives = LivesPolicy(rules),
        _stars = StarCalculator(rules),
        _rewards = RewardCalculator(rules),
        _accountLevels = AccountLevelCalculator(rules);

  final ContentRepository _content;
  final ProgressRepository _progress;
  final SettingsRepository _settings;
  final ValidatorRegistry _validators;
  final Clock _clock;
  final AnalyticsService _analytics;
  final FeatureFlagService _flags;
  final UnlockPolicy _unlock;
  final StreakPolicy _streak;
  final AchievementEvaluator _achievements;
  final LivesPolicy _lives;
  final StarCalculator _stars;
  final RewardCalculator _rewards;
  final AccountLevelCalculator _accountLevels;

  bool _livesActive(UserProfile profile) =>
      _flags.isEnabled(FeatureFlag.lives) && !profile.isPremium;

  LivesSnapshot _livesSnapshot(UserProfile profile, DateTime now) =>
      _livesActive(profile)
          ? LivesSnapshot.fromState(profile.lives, _lives, now)
          : LivesSnapshot.unlimited(_lives.maxLives);

  Future<UnlockMode> _unlockMode() async =>
      UnlockMode.forExperience((await _settings.load()).experience);

  Future<LevelStartResult> start({
    required String courseId,
    required String levelId,
    LevelMode mode = LevelMode.standard,
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
    final unlockMode = await _unlockMode();
    if (!_unlock.isUnlocked(course, progress, levelId, mode: unlockMode)) {
      return const LevelStartDenied(LevelStartDenial.locked);
    }

    final now = _clock.now();
    final profile = await _progress.loadProfile();
    final lives = _livesSnapshot(profile, now);
    if (lives.isEmpty) {
      return LevelStartDenied(LevelStartDenial.noLives, lives: lives);
    }

    final previous = progress.levelOf(levelId);
    await _progress.saveCourseProgress(
      progress.withLevel(
        previous.copyWith(attempts: previous.attempts + 1, lastPlayedAt: now),
      ),
    );

    _analytics.track(
      mode == LevelMode.dailyChallenge
          ? AnalyticsEvent.dailyChallengeStarted
          : AnalyticsEvent.levelStarted,
      {'level_id': levelId, 'type': level.type.id, 'replay': previous.completed},
    );
    return LevelStarted(
      session: LevelSession(level: level, mode: mode, startedAt: now),
      lives: lives,
    );
  }

  /// Records hint usage (analytics, future hint limits / AI tutor).
  LevelSession useHint(LevelSession session) {
    _analytics.track(AnalyticsEvent.hintUsed, {'level_id': session.level.id});
    return session.copyWith(hintsUsed: session.hintsUsed + 1);
  }

  Future<SubmissionResult> submit(LevelSession session, Answer answer) async {
    if (session.isFinished) {
      throw const InvalidLevelStateException('Level session already finished');
    }
    final level = session.level;
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
      if (_livesActive(profile)) {
        final lives =
            _lives.loseLives(profile.lives, now, amount: level.livesPenalty);
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
        lives: _livesSnapshot(profile, now),
      );
    }

    final completion = await _complete(submitted, profile, now);
    return SubmissionResult(
      session: submitted.copyWith(isCompleted: true),
      outcome: outcome,
      lives: _livesSnapshot(completion.profile, now),
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
    final stars = _stars.starsFor(session.mistakes);
    var reward = _rewards.completionReward(
      level: level,
      mistakes: session.mistakes,
      isFirstCompletion: isFirst,
    );

    final isDaily = session.mode == LevelMode.dailyChallenge &&
        profile.lastDailyChallengeDay != today;
    if (isDaily) reward += _rewards.dailyChallengeBonus;

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

    final streakUpdate = _streak.registerActivity(profile.streak, today);
    final levelBefore = _accountLevels.levelFor(profile.totalXp).level;
    profile = profile.copyWith(
      totalXp: profile.totalXp + reward.xp,
      coins: profile.coins + reward.coins,
      streak: streakUpdate.state,
      lastActivityAt: now,
      lastDailyChallengeDay: isDaily ? today : null,
    );

    final newAchievements = _achievements.newlyUnlocked(
      _statsFor(profile, course, progress),
      profile.unlockedAchievements,
    );
    if (newAchievements.isNotEmpty) {
      profile = profile.copyWith(
        unlockedAchievements: {
          ...profile.unlockedAchievements,
          ...newAchievements.map((achievement) => achievement.id),
        },
      );
    }

    // Course progress first: a crash between writes can only lose the
    // reward, never the completion itself.
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
