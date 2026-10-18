import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../progress/presentation/progress_providers.dart';
import '../../settings/presentation/settings_controller.dart';
import '../domain/career_dashboard.dart';

/// A projection of existing course progress. Career never awards currency or
/// creates a second copy of the player's learning records.
final careerDashboardProvider = FutureProvider<CareerDashboard>((ref) async {
  final course = await ref.watch(activeCourseProvider.future);
  final progress = await ref.watch(activeCourseProgressProvider.future);
  final settings = await ref.watch(settingsControllerProvider.future);
  return const CareerDashboardCalculator().build(
    course: course,
    progress: progress,
    target: CareerTargetId.fromId(settings.careerGoalId),
  );
});
