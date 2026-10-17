import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/di/providers.dart';
import '../../progress/presentation/progress_providers.dart';
import '../../settings/presentation/settings_controller.dart';
import '../domain/career_dashboard.dart';
import '../domain/github_portfolio.dart';

final githubPortfolioProvider = FutureProvider<GitHubPortfolio>((ref) async {
  final settings = await ref.watch(settingsControllerProvider.future);
  final username = settings.githubUsername.trim();
  if (username.isEmpty) return GitHubPortfolio.disconnected();
  return ref.watch(githubPortfolioRepositoryProvider).load(username);
});

final careerDashboardProvider = FutureProvider<CareerDashboard>((ref) async {
  final course = await ref.watch(activeCourseProvider.future);
  final progress = await ref.watch(activeCourseProgressProvider.future);
  final settings = await ref.watch(settingsControllerProvider.future);
  final portfolio =
      ref.watch(githubPortfolioProvider).value ?? GitHubPortfolio.disconnected();
  return const CareerDashboardCalculator().build(
    course: course,
    progress: progress,
    target: CareerTargetId.fromId(settings.careerGoalId),
    portfolio: portfolio,
  );
});
