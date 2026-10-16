import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/di/providers.dart';

/// Where a level sits inside its module: for the segmented top bar.
class LevelPosition {
  const LevelPosition({required this.index, required this.count});

  /// Zero-based index among the module's playable levels.
  final int index;
  final int count;
}

final levelPositionProvider =
    FutureProvider.family<LevelPosition?, (String, String)>((ref, key) async {
  final (courseId, levelId) = key;
  final course = await ref.watch(contentRepositoryProvider).loadCourse(courseId);
  final module = course.moduleOf(levelId);
  if (module == null) return null;
  final playable = module.playableLevels;
  final index = playable.indexWhere((level) => level.id == levelId);
  if (index < 0) return null;
  return LevelPosition(index: index, count: playable.length);
});
