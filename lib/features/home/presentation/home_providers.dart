import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/di/providers.dart';
import '../../../core/time/calendar_day.dart';
import '../../../services/feature_flags/feature_flag_service.dart';
import '../../daily_challenge/domain/daily_challenge.dart';
import '../../gamification/domain/score_calculators.dart';
import '../../gamification/domain/streak.dart';
import '../../learning_map/domain/learning_map_model.dart';
import '../../learning_map/presentation/learning_map_providers.dart';
import '../../level/domain/level_result.dart';
import '../../progress/domain/user_profile.dart';
import '../../progress/presentation/progress_providers.dart';

final dailyChallengeProvider = FutureProvider<DailyChallenge?>((ref) async {
  ref.watch(progressRevisionProvider);
  if (!ref.watch(featureFlagsProvider).isEnabled(FeatureFlag.dailyChallenge)) {
    return null;
  }
  final courseId = await ref.watch(activeCourseIdProvider.future);
  final today = CalendarDay.fromDateTime(ref.watch(clockProvider).now());
  return ref
      .watch(dailyChallengeServiceProvider)
      .challengeFor(today, courseId);
});

class HomeViewModel {
  const HomeViewModel({
    required this.profile,
    required this.streakDays,
    required this.isStreakActiveToday,
    required this.lives,
    required this.map,
    required this.dailyChallenge,
    required this.nextLevelXp,
  });

  final UserProfile profile;
  final int streakDays;
  final bool isStreakActiveToday;
  final LivesSnapshot lives;
  final LearningMapModel map;
  final DailyChallenge? dailyChallenge;

  /// XP for a flawless first completion of the next level.
  final int nextLevelXp;
}

final homeViewModelProvider = FutureProvider<HomeViewModel>((ref) async {
  final profile = await ref.watch(profileProvider.future);
  final lives = await ref.watch(livesProvider.future);
  final map = await ref.watch(learningMapProvider.future);
  final daily = await ref.watch(dailyChallengeProvider.future);
  final today = CalendarDay.fromDateTime(ref.watch(clockProvider).now());
  const streakPolicy = StreakPolicy();
  final next = map.nextLevel;
  final rewards = RewardCalculator(ref.watch(gameRulesProvider));
  return HomeViewModel(
    nextLevelXp: next == null
        ? 0
        : rewards.xpFor(level: next, mistakes: 0, isFirstCompletion: true),
    profile: profile,
    streakDays: streakPolicy.displayValue(profile.streak, today),
    isStreakActiveToday: streakPolicy.isActiveToday(profile.streak, today),
    lives: lives,
    map: map,
    dailyChallenge: daily,
  );
});
