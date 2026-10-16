import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../progress/presentation/progress_providers.dart';
import '../domain/learning_map_model.dart';

final learningMapProvider = FutureProvider<LearningMapModel>((ref) async {
  final course = await ref.watch(activeCourseProvider.future);
  final progress = await ref.watch(activeCourseProgressProvider.future);
  final mode = await ref.watch(unlockModeProvider.future);
  return const LearningMapBuilder().build(course, progress, mode: mode);
});

enum MapMode { learn, timed }

/// Which tab of the map is shown. Lives in memory: the map opens on
/// "Обучение" after a restart, which is the safe default.
final mapModeProvider = NotifierProvider<MapModeController, MapMode>(
  MapModeController.new,
);

class MapModeController extends Notifier<MapMode> {
  @override
  MapMode build() => MapMode.learn;

  void select(MapMode mode) => state = mode;
}
