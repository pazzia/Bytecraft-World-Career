import '../../world/presentation/repair_screen.dart';
import '../../../app/di/providers.dart';
import '../../playground/presentation/playground_providers.dart';
import '../../projects/presentation/project_providers.dart';
import '../../world/presentation/world_controller.dart';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../progress/presentation/progress_providers.dart';
import '../../settings/presentation/settings_controller.dart';
import '../domain/career_dashboard.dart';

/// A projection of existing course progress. Career never awards currency or
/// creates a second copy of the player's learning records.
final careerDashboardProvider = FutureProvider<CareerDashboard>((ref) async {
  ref.watch(gameSaveChangesProvider);
  final catalog = await ref.watch(repairCatalogProvider.future);
  final mode = await ref.watch(unlockModeProvider.future);
  final world = await ref.watch(worldControllerProvider.future);
  final tasks = await ref.watch(practiceTasksProvider.future);
  final solved = await ref.watch(solvedPracticeProvider.future);
  final project = await ref.watch(calculatorProjectProvider.future);
  final course = await ref.watch(activeCourseProvider.future);
  final progress = await ref.watch(activeCourseProgressProvider.future);
  final settings = await ref.watch(settingsControllerProvider.future);
  return const CareerDashboardCalculator().build(
    catalog: catalog,
    unlockMode: mode,
    projectUnlocked: world.expeditionProgress >= 5,
    tasks: tasks,
    solved: solved,
    project: project,
    repairs: world.repairs.values,
    course: course,
    progress: progress,
    target: CareerTargetId.fromId(settings.careerGoalId),
  );
});
