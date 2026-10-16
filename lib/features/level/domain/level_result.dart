import '../../achievements/domain/achievement.dart';
import '../../gamification/domain/lives.dart';
import 'level_session.dart';
import 'validation_outcome.dart';

/// Outcome of a successfully completed level.
class LevelResult {
  const LevelResult({
    required this.levelId,
    required this.stars,
    required this.previousBestStars,
    required this.xpEarned,
    required this.coinsEarned,
    required this.isFirstCompletion,
    required this.streak,
    required this.streakExtended,
    required this.accountLevelBefore,
    required this.accountLevelAfter,
    required this.completedInCourse,
    required this.playableInCourse,
    required this.newAchievements,
    required this.dailyChallengeCompleted,
    this.nextLevelId,
    this.newlyUnlockedLevelId,
  });

  final String levelId;
  final int stars;
  final int previousBestStars;
  final int xpEarned;
  final int coinsEarned;
  final bool isFirstCompletion;

  /// Streak value after this completion.
  final int streak;
  final bool streakExtended;
  final int accountLevelBefore;
  final int accountLevelAfter;
  final int completedInCourse;
  final int playableInCourse;
  final List<Achievement> newAchievements;
  final bool dailyChallengeCompleted;

  /// Level that follows in course order (may already be completed).
  final String? nextLevelId;

  /// Set when this completion unlocked a previously locked level.
  final String? newlyUnlockedLevelId;

  bool get isPerfect => stars >= 3;
  bool get leveledUp => accountLevelAfter > accountLevelBefore;
  double get courseProgress =>
      playableInCourse == 0 ? 0 : completedInCourse / playableInCourse;
}

/// Why a level can't be started.
enum LevelStartDenial { notFound, locked, unsupported, noLives }

sealed class LevelStartResult {
  const LevelStartResult();
}

final class LevelStarted extends LevelStartResult {
  const LevelStarted({required this.session, required this.lives});

  final LevelSession session;
  final LivesSnapshot lives;
}

final class LevelStartDenied extends LevelStartResult {
  const LevelStartDenied(this.reason, {this.lives});

  final LevelStartDenial reason;
  final LivesSnapshot? lives;
}

/// Lives as seen by the player at a moment in time.
class LivesSnapshot {
  const LivesSnapshot({
    required this.current,
    required this.max,
    required this.isUnlimited,
    this.nextLifeIn,
  });

  factory LivesSnapshot.unlimited(int max) =>
      LivesSnapshot(current: max, max: max, isUnlimited: true);

  factory LivesSnapshot.fromState(
    LivesState state,
    LivesPolicy policy,
    DateTime now,
  ) {
    final current = policy.regenerate(state, now);
    return LivesSnapshot(
      current: current.current,
      max: policy.maxLives,
      isUnlimited: false,
      nextLifeIn: policy.timeToNextLife(state, now),
    );
  }

  final int current;
  final int max;
  final bool isUnlimited;
  final Duration? nextLifeIn;

  bool get isEmpty => !isUnlimited && current <= 0;
}

/// Outcome of one answer submission.
class SubmissionResult {
  const SubmissionResult({
    required this.session,
    required this.outcome,
    required this.lives,
    this.completion,
  });

  final LevelSession session;
  final ValidationOutcome outcome;
  final LivesSnapshot lives;

  /// Non-null when the answer completed the level.
  final LevelResult? completion;

  bool get isFailed => session.isFailed;
}
