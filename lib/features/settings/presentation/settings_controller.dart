import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/di/providers.dart';
import '../../../services/analytics/analytics_service.dart';
import '../domain/app_settings.dart';

final settingsControllerProvider =
    AsyncNotifierProvider<SettingsController, AppSettings>(
  SettingsController.new,
);

class SettingsController extends AsyncNotifier<AppSettings> {
  @override
  Future<AppSettings> build() => ref.watch(settingsRepositoryProvider).load();

  Future<void> _update(AppSettings Function(AppSettings current) change) async {
    final next = await ref.read(gameSaveStoreProvider).transaction(() async {
      final repository = ref.read(settingsRepositoryProvider);
      final current = await repository.load();
      final next = change(current);
      await repository.save(next);
      return next;
    });
    if (ref.mounted) state = AsyncData(next);
  }

  Future<void> completeOnboarding({
    required ExperienceLevel experience,
    required String courseId,
  }) async {
    await _update(
      (current) => current.copyWith(
        onboardingCompleted: true,
        experience: experience,
        activeCourseId: courseId,
      ),
    );
    final analytics = ref.read(analyticsProvider);
    analytics.track(
      AnalyticsEvent.onboardingComplete,
      {'experience': experience.id},
    );
    analytics.track(AnalyticsEvent.courseStarted, {'course_id': courseId});
  }

  Future<void> setTheme(ThemePreference theme) =>
      _update((current) => current.copyWith(theme: theme));

  Future<void> setActiveCourse(String courseId) =>
      _update((current) => current.copyWith(activeCourseId: courseId));

  Future<void> setCareerGoal(String goalId) =>
      _update((current) => current.copyWith(careerGoalId: goalId));

  Future<void> setGitHubUsername(String username) {
    final clean = username.trim().replaceFirst(RegExp(r'^@'), '');
    return _update((current) => current.copyWith(githubUsername: clean));
  }
}
