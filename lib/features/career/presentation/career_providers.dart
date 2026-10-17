import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../progress/presentation/progress_providers.dart';
import '../../settings/presentation/settings_controller.dart';
import '../domain/career_dashboard.dart';

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
