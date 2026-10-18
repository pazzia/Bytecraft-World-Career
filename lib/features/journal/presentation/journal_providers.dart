import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/di/providers.dart';
import '../../courses/domain/level_definition.dart';
import '../../learning_map/presentation/learning_map_providers.dart';
import '../../progress/presentation/progress_providers.dart';
import '../domain/journal.dart';
import '../domain/journal_service.dart';
import '../domain/topic.dart';

final topicCatalogProvider = FutureProvider<TopicCatalog>((ref) async {
  final courseId = await ref.watch(activeCourseIdProvider.future);
  return ref.watch(topicRepositoryProvider).load(courseId);
});

final glossaryProvider = FutureProvider<Glossary>((ref) async {
  final courseId = await ref.watch(activeCourseIdProvider.future);
  return ref.watch(topicRepositoryProvider).loadGlossary(courseId);
});

/// The active course's journal; recomputed after every player-state write.
final journalProvider = FutureProvider<Journal>((ref) async {
  ref.watch(progressRevisionProvider);
  final courseId = await ref.watch(activeCourseIdProvider.future);
  return ref.watch(journalServiceProvider).load(courseId);
});

/// Number of saved topics due for review (tab badge, home card).
final dueReviewCountProvider = FutureProvider<int>((ref) async {
  final journal = await ref.watch(journalProvider.future);
  return journal.due(ref.watch(clockProvider).now()).length;
});

/// Runs a journal write for the active course and refreshes read models.
Future<void> runJournalAction(
  WidgetRef ref,
  Future<void> Function(JournalService service, String courseId) action,
) async {
  final courseId = await ref.read(activeCourseIdProvider.future);
  await action(ref.read(journalServiceProvider), courseId);
  ref.read(progressRevisionProvider.notifier).bump();
}

/// Levels of a topic the player can open now, in course order.
final playableTopicLevelsProvider =
    FutureProvider.family<List<LevelDefinition>, String>((ref, topicId) async {
  final map = await ref.watch(learningMapProvider.future);
  return [
    for (final section in map.sections)
      for (final node in section.nodes)
        if (node.isPlayable && node.level.topicId == topicId) node.level,
  ];
});

/// All levels of a topic (open or not), in course order.
final topicLevelsProvider =
    FutureProvider.family<List<LevelDefinition>, String>((ref, topicId) async {
  final course = await ref.watch(activeCourseProvider.future);
  return course.playableLevels
      .where((level) => level.topicId == topicId)
      .toList();
});

/// Modules the player has reached (at least one level open): their topics
/// are listed in the reference.
final reachedModuleIdsProvider = FutureProvider<Set<String>>((ref) async {
  final map = await ref.watch(learningMapProvider.future);
  return {
    for (final section in map.sections)
      if (section.nodes.any((node) => node.isPlayable)) section.module.id,
  };
});

/// Picks the level for the next review of a topic: a level the player got
/// wrong first (newest mistake first), then the others in turn.
LevelDefinition? pickReviewLevel(
  JournalEntry entry,
  List<LevelDefinition> playable,
) {
  if (playable.isEmpty) return null;
  final byId = {for (final level in playable) level.id: level};
  for (final id in entry.mistakeLevelIds.reversed) {
    final level = byId[id];
    if (level != null && entry.reviews % 2 == 0) return level;
  }
  return playable[entry.reviews % playable.length];
}
