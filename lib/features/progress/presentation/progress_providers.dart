import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/di/providers.dart';
import '../../../services/feature_flags/feature_flag_service.dart';
import '../../courses/domain/course.dart';
import '../../gamification/domain/lives.dart';
import '../../gamification/domain/score_calculators.dart';
import '../../level/domain/level_result.dart';
import '../../settings/presentation/settings_controller.dart';
import '../domain/course_progress.dart';
import '../domain/unlock_policy.dart';
import '../domain/user_profile.dart';

/// Bumped after any write to player state; read models depend on it and
/// recompute. Keeps persistence (repositories) and UI state decoupled.
final progressRevisionProvider =
    NotifierProvider<ProgressRevision, int>(ProgressRevision.new);

class ProgressRevision extends Notifier<int> {
  @override
  int build() => 0;

  void bump() => state++;
}

final profileProvider = FutureProvider<UserProfile>((ref) {
  ref.watch(progressRevisionProvider);
  return ref.watch(progressRepositoryProvider).loadProfile();
});

final activeCourseIdProvider = FutureProvider<String>((ref) async {
  final settings = await ref.watch(settingsControllerProvider.future);
  return settings.activeCourseId;
});

final activeCourseProvider = FutureProvider<Course>((ref) async {
  final courseId = await ref.watch(activeCourseIdProvider.future);
  return ref.watch(contentRepositoryProvider).loadCourse(courseId);
});

final activeCourseProgressProvider = FutureProvider<CourseProgress>((ref) async {
  ref.watch(progressRevisionProvider);
  final courseId = await ref.watch(activeCourseIdProvider.future);
  return ref.watch(progressRepositoryProvider).loadCourseProgress(courseId);
});

final unlockModeProvider = FutureProvider<UnlockMode>((ref) async {
  final settings = await ref.watch(settingsControllerProvider.future);
  return UnlockMode.forExperience(settings.experience);
});

final livesProvider = FutureProvider<LivesSnapshot>((ref) async {
  final profile = await ref.watch(profileProvider.future);
  final rules = ref.watch(gameRulesProvider);
  final flags = ref.watch(featureFlagsProvider);
  if (!flags.isEnabled(FeatureFlag.lives) || profile.isPremium) {
    return LivesSnapshot.unlimited(rules.maxLives);
  }
  return LivesSnapshot.fromState(
    profile.lives,
    LivesPolicy(rules),
    ref.watch(clockProvider).now(),
  );
});

final accountLevelProvider = FutureProvider<AccountLevel>((ref) async {
  final profile = await ref.watch(profileProvider.future);
  return AccountLevelCalculator(ref.watch(gameRulesProvider))
      .levelFor(profile.totalXp);
});
