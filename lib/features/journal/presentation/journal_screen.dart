import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/di/providers.dart';
import '../../../app/router/routes.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/game_colors.dart';
import '../../../shared/widgets/app_card.dart';
import '../../../shared/widgets/async_value_view.dart';
import '../../../shared/widgets/stat_badges.dart';
import '../../progress/presentation/progress_providers.dart';
import '../domain/journal.dart';
import '../domain/topic.dart';
import 'journal_providers.dart';

class JournalViewModel {
  const JournalViewModel({
    required this.journal,
    required this.catalog,
    required this.reachedModules,
    required this.moduleTitles,
    required this.now,
  });

  final Journal journal;
  final TopicCatalog catalog;
  final Set<String> reachedModules;

  /// Module id -> title, in course order.
  final Map<String, String> moduleTitles;
  final DateTime now;
}

final journalViewModelProvider = FutureProvider<JournalViewModel>((ref) async {
  final course = await ref.watch(activeCourseProvider.future);
  return JournalViewModel(
    journal: await ref.watch(journalProvider.future),
    catalog: await ref.watch(topicCatalogProvider.future),
    reachedModules: await ref.watch(reachedModuleIdsProvider.future),
    moduleTitles: {for (final module in course.modules) module.id: module.title},
    now: ref.watch(clockProvider).now(),
  );
});

/// The journal tab: saved topics with spaced review, suggestions from
/// mistakes and the reference of every topic reached so far.
class JournalScreen extends ConsumerWidget {
  const JournalScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final vm = ref.watch(journalViewModelProvider);
    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: AsyncValueView<JournalViewModel>(
          value: vm,
          onRetry: () => ref.invalidate(journalViewModelProvider),
          data: (vm) => _JournalBody(vm: vm),
        ),
      ),
    );
  }
}

class _JournalBody extends ConsumerWidget {
  const _JournalBody({required this.vm});

  final JournalViewModel vm;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    final journal = vm.journal;
    final entries = journal.entries.values
        .where((entry) => vm.catalog.byId(entry.topicId) != null)
        .toList()
      ..sort((a, b) => b.addedAt.compareTo(a.addedAt));
    final due = journal
        .due(vm.now)
        .where((entry) => vm.catalog.byId(entry.topicId) != null)
        .toList();
    final suggested = journal
        .suggestedTopicIds()
        .where((id) => vm.catalog.byId(id) != null)
        .take(5)
        .toList();

    void open(String topicId) => context.push(Routes.topic(topicId));

    return ListView(
      padding: const EdgeInsets.fromLTRB(
        Spacing.page,
        Spacing.xxl,
        Spacing.page,
        Spacing.huge,
      ),
      children: [
        Text('Журнал', style: textTheme.headlineMedium),
        const SizedBox(height: Spacing.xs),
        Text(
          entries.isEmpty
              ? 'Сохраняйте темы из разбора ошибок — они вернутся на повторение.'
              : '${entries.length} ${plural(entries.length, 'тема', 'темы', 'тем')} · '
                  'к повторению: ${due.length}',
          style: textTheme.bodyMedium?.copyWith(color: game.textMuted),
        ),
        if (due.isNotEmpty) ...[
          const SectionTitle('Повторить сегодня'),
          for (final entry in due)
            Padding(
              padding: const EdgeInsets.only(bottom: Spacing.md),
              child: _EntryCard(
                topic: vm.catalog.byId(entry.topicId)!,
                entry: entry,
                highlight: true,
                onTap: () => open(entry.topicId),
              ),
            ),
        ],
        if (suggested.isNotEmpty) ...[
          const SectionTitle('Стоит повторить'),
          for (final id in suggested)
            Padding(
              padding: const EdgeInsets.only(bottom: Spacing.md),
              child: _SuggestionCard(
                topic: vm.catalog.byId(id)!,
                mistakes: journal.mistakes[id]?.length ?? 0,
                onOpen: () => open(id),
                onAdd: () => runJournalAction(
                  ref,
                  (service, courseId) => service.add(courseId, id),
                ),
              ),
            ),
        ],
        if (entries.isNotEmpty) ...[
          const SectionTitle('Мои темы'),
          for (final entry in entries)
            Padding(
              padding: const EdgeInsets.only(bottom: Spacing.md),
              child: _EntryCard(
                topic: vm.catalog.byId(entry.topicId)!,
                entry: entry,
                onTap: () => open(entry.topicId),
              ),
            ),
        ],
        const SectionTitle('Справочник'),
        for (final moduleId in vm.moduleTitles.keys)
          if (vm.reachedModules.contains(moduleId) &&
              vm.catalog.forModule(moduleId).isNotEmpty)
            _ModuleTopics(
              title: vm.moduleTitles[moduleId]!,
              topics: vm.catalog.forModule(moduleId),
              saved: journal.entries.keys.toSet(),
              onOpen: open,
            ),
        if (vm.moduleTitles.keys.any((id) => !vm.reachedModules.contains(id)))
          Padding(
            padding: const EdgeInsets.only(top: Spacing.sm),
            child: Text(
              'Темы следующих модулей откроются, когда вы до них дойдёте.',
              style: textTheme.bodySmall?.copyWith(color: game.textMuted),
            ),
          ),
      ],
    );
  }
}

/// Five dots: how far the topic has climbed the review boxes.
class ReviewDots extends StatelessWidget {
  const ReviewDots({super.key, required this.box});

  final int box;

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    const total = ReviewScheduler.intervalDays.length;
    return Semantics(
      label: 'Освоено на $box из $total',
      excludeSemantics: true,
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          for (var i = 0; i < total; i++)
            Container(
              width: 10,
              height: 10,
              margin: const EdgeInsets.only(right: 4),
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: i < box ? game.success : game.track,
              ),
            ),
        ],
      ),
    );
  }
}

class _EntryCard extends StatelessWidget {
  const _EntryCard({
    required this.topic,
    required this.entry,
    required this.onTap,
    this.highlight = false,
  });

  final Topic topic;
  final JournalEntry entry;
  final VoidCallback onTap;
  final bool highlight;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    final mistakes = entry.mistakeLevelIds.length;
    return AppCard(
      onTap: onTap,
      borderColor: highlight ? Theme.of(context).colorScheme.primary : null,
      semanticLabel: topic.title,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(child: Text(topic.title, style: textTheme.titleMedium)),
              if (entry.isMastered)
                Icon(Icons.verified_rounded, color: game.success)
              else
                ReviewDots(box: entry.box),
            ],
          ),
          const SizedBox(height: Spacing.xs),
          Text(
            topic.summary,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: textTheme.bodyMedium?.copyWith(color: game.textMuted),
          ),
          if (mistakes > 0) ...[
            const SizedBox(height: Spacing.xs),
            Text(
              'Ошибок в уровнях: $mistakes',
              style: textTheme.labelMedium?.copyWith(color: game.error),
            ),
          ],
        ],
      ),
    );
  }
}

class _SuggestionCard extends StatelessWidget {
  const _SuggestionCard({
    required this.topic,
    required this.mistakes,
    required this.onOpen,
    required this.onAdd,
  });

  final Topic topic;
  final int mistakes;
  final VoidCallback onOpen;
  final VoidCallback onAdd;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    return AppCard(
      onTap: onOpen,
      semanticLabel: topic.title,
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(topic.title, style: textTheme.titleMedium),
                const SizedBox(height: Spacing.xs),
                Text(
                  'Ошибок: $mistakes',
                  style: textTheme.labelMedium?.copyWith(color: game.error),
                ),
              ],
            ),
          ),
          IconButton(
            tooltip: 'Сохранить в журнал',
            icon: Icon(
              Icons.bookmark_add_rounded,
              color: Theme.of(context).colorScheme.primary,
            ),
            onPressed: onAdd,
          ),
        ],
      ),
    );
  }
}

class _ModuleTopics extends StatelessWidget {
  const _ModuleTopics({
    required this.title,
    required this.topics,
    required this.saved,
    required this.onOpen,
  });

  final String title;
  final List<Topic> topics;
  final Set<String> saved;
  final ValueChanged<String> onOpen;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    return Padding(
      padding: const EdgeInsets.only(bottom: Spacing.lg),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            title,
            style: textTheme.labelLarge?.copyWith(color: game.textMuted),
          ),
          const SizedBox(height: Spacing.xs),
          for (final topic in topics)
            InkWell(
              onTap: () => onOpen(topic.id),
              borderRadius: AppRadius.mdAll,
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: Spacing.sm),
                child: Row(
                  children: [
                    Icon(
                      saved.contains(topic.id)
                          ? Icons.bookmark_rounded
                          : Icons.article_outlined,
                      size: 20,
                      color: saved.contains(topic.id)
                          ? Theme.of(context).colorScheme.primary
                          : game.textMuted,
                    ),
                    const SizedBox(width: Spacing.md),
                    Expanded(
                      child: Text(topic.title, style: textTheme.bodyLarge),
                    ),
                    Icon(Icons.chevron_right_rounded, color: game.textMuted),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}
