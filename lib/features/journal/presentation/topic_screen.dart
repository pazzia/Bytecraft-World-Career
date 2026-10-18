import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/di/providers.dart';
import '../../../app/router/routes.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/game_colors.dart';
import '../../../shared/widgets/app_button.dart';
import '../../../shared/widgets/app_card.dart';
import '../../courses/domain/level_definition.dart';
import '../../level/domain/level_session.dart';
import '../../progress/presentation/progress_providers.dart';
import '../domain/journal.dart';
import 'journal_providers.dart';
import 'journal_screen.dart';
import 'widgets/topic_content.dart';

/// A topic from the journal or the reference: the explanation with
/// examples, review state and practice levels.
class TopicScreen extends ConsumerWidget {
  const TopicScreen({super.key, required this.topicId, this.fromTopicId});

  final String topicId;

  /// The topic the reader came from by a link: shows «‹ К теме X».
  final String? fromTopicId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final topic = ref.watch(topicCatalogProvider).value?.byId(topicId);
    final journal = ref.watch(journalProvider).value;
    final entry = journal?.entries[topicId];
    final playable = ref.watch(playableTopicLevelsProvider(topicId)).value ??
        const <LevelDefinition>[];
    final all = ref.watch(topicLevelsProvider(topicId)).value ??
        const <LevelDefinition>[];
    final progress = ref.watch(activeCourseProgressProvider).value;
    final mistakes = journal?.mistakes[topicId] ?? const <String>[];
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    final now = ref.watch(clockProvider).now();

    void startReview() {
      final level = entry == null ? null : pickReviewLevel(entry, playable);
      if (level == null) return;
      context.push(
        Routes.level(level.courseId, level.id, mode: LevelMode.review),
      );
    }

    final saved = entry != null;
    final fromTopic = fromTopicId == null
        ? null
        : ref.watch(topicCatalogProvider).value?.byId(fromTopicId!);

    return Scaffold(
      appBar: AppBar(
        title: Text(topic?.title ?? 'Тема', maxLines: 1, overflow: TextOverflow.ellipsis),
        actions: [
          if (topic != null)
            IconButton(
              key: const ValueKey('topic_bookmark'),
              tooltip: saved ? 'Убрать из журнала' : 'Сохранить в журнал',
              icon: Icon(saved ? Icons.bookmark_rounded : Icons.bookmark_add_outlined),
              color: saved ? Theme.of(context).colorScheme.primary : null,
              onPressed: () => runJournalAction(
                ref,
                (service, courseId) => saved
                    ? service.remove(courseId, topicId)
                    : service.add(courseId, topicId),
              ),
            ),
        ],
      ),
      body: topic == null
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                if (fromTopic != null)
                  Material(
                    color: game.primaryTint,
                    child: InkWell(
                      key: const ValueKey('topic_back_link'),
                      onTap: () => context.canPop()
                          ? context.pop()
                          : context.go(Routes.topic(fromTopic.id)),
                      child: Padding(
                        padding: const EdgeInsets.symmetric(
                          horizontal: Spacing.page,
                          vertical: Spacing.md,
                        ),
                        child: Row(
                          children: [
                            Icon(Icons.arrow_back_rounded, size: 18, color: Theme.of(context).colorScheme.primary),
                            const SizedBox(width: Spacing.sm),
                            Expanded(
                              child: Text(
                                'К теме «${fromTopic.title}»',
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: textTheme.labelLarge?.copyWith(
                                  color: Theme.of(context).colorScheme.primary,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                Expanded(
                  child: ListView(
                    key: PageStorageKey('topic_$topicId'),
                    padding: const EdgeInsets.fromLTRB(
                      Spacing.page,
                      Spacing.lg,
                      Spacing.page,
                      Spacing.huge,
                    ),
                    children: [
                      TopicContent(topic: topic),
                      if (all.isNotEmpty) ...[
                        const SectionTitle('Практика по теме'),
                        for (final level in all)
                          _PracticeRow(
                            level: level,
                            isOpen: playable.any((open) => open.id == level.id),
                            isDone: progress?.isCompleted(level.id) ?? false,
                            hadMistake: mistakes.contains(level.id),
                            onTap: () => context.push(
                              Routes.level(
                                level.courseId,
                                level.id,
                                mode: entry == null
                                    ? LevelMode.standard
                                    : LevelMode.review,
                              ),
                            ),
                          ),
                      ],
                      const SizedBox(height: Spacing.xxl),
                      if (entry != null)
                        _ReviewCard(
                          entry: entry,
                          now: now,
                          canPractice: playable.isNotEmpty,
                          onReview: startReview,
                          onSelfCheck: (remembered) => runJournalAction(
                            ref,
                            (service, courseId) => service.recordReview(
                              courseId,
                              topicId,
                              remembered: remembered,
                            ),
                          ),
                        )
                      else
                        AppButton(
                          key: const ValueKey('topic_save'),
                          label: 'Сохранить в журнал',
                          icon: Icons.bookmark_add_rounded,
                          variant: AppButtonVariant.secondary,
                          onPressed: () => runJournalAction(
                            ref,
                            (service, courseId) => service.add(courseId, topicId),
                          ),
                        ),
                      if (entry != null) ...[
                        const SizedBox(height: Spacing.lg),
                        AppButton(
                          label: 'Убрать из журнала',
                          variant: AppButtonVariant.quiet,
                          onPressed: () => runJournalAction(
                            ref,
                            (service, courseId) => service.remove(courseId, topicId),
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ],
            ),
    );
  }
}

class _ReviewCard extends StatelessWidget {
  const _ReviewCard({
    required this.entry,
    required this.now,
    required this.canPractice,
    required this.onReview,
    required this.onSelfCheck,
  });

  final JournalEntry entry;
  final DateTime now;
  final bool canPractice;
  final VoidCallback onReview;
  final ValueChanged<bool> onSelfCheck;

  String _due() {
    if (entry.isDue(now)) return 'Пора повторить';
    final days = entry.dueAt.difference(now).inHours ~/ 24 + 1;
    return days <= 1 ? 'Следующее повторение — завтра' : 'Следующее повторение через $days дн.';
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Icon(Icons.bookmark_rounded, color: Theme.of(context).colorScheme.primary),
              const SizedBox(width: Spacing.sm),
              Expanded(child: Text('В журнале', style: textTheme.titleMedium)),
              ReviewDots(box: entry.box),
            ],
          ),
          const SizedBox(height: Spacing.xs),
          Text(
            entry.isMastered ? 'Тема освоена. ${_due()}' : _due(),
            style: textTheme.bodyMedium?.copyWith(color: game.textMuted),
          ),
          const SizedBox(height: Spacing.lg),
          if (canPractice)
            AppButton(
              key: const ValueKey('topic_review'),
              label: 'Повторить: решить задачу',
              icon: Icons.replay_rounded,
              onPressed: onReview,
            )
          else ...[
            Text(
              'Прочитайте тему и честно ответьте: помните её?',
              style: textTheme.bodyMedium,
            ),
            const SizedBox(height: Spacing.md),
            Row(
              children: [
                Expanded(
                  child: AppButton(
                    label: 'Повторить ещё',
                    variant: AppButtonVariant.secondary,
                    onPressed: () => onSelfCheck(false),
                  ),
                ),
                const SizedBox(width: Spacing.md),
                Expanded(
                  child: AppButton(
                    label: 'Помню',
                    variant: AppButtonVariant.success,
                    onPressed: () => onSelfCheck(true),
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }
}

class _PracticeRow extends StatelessWidget {
  const _PracticeRow({
    required this.level,
    required this.isOpen,
    required this.isDone,
    required this.hadMistake,
    required this.onTap,
  });

  final LevelDefinition level;
  final bool isOpen;
  final bool isDone;
  final bool hadMistake;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    final icon = !isOpen
        ? Icons.lock_rounded
        : isDone
            ? Icons.check_circle_rounded
            : Icons.play_circle_rounded;
    final color = !isOpen
        ? game.lockedIcon
        : isDone
            ? game.success
            : Theme.of(context).colorScheme.primary;
    return InkWell(
      onTap: isOpen ? onTap : null,
      borderRadius: AppRadius.mdAll,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: Spacing.sm),
        child: Row(
          children: [
            Icon(icon, color: color),
            const SizedBox(width: Spacing.md),
            Expanded(
              child: Text(
                level.title,
                style: textTheme.bodyLarge?.copyWith(
                  color: isOpen ? null : game.textMuted,
                ),
              ),
            ),
            if (hadMistake)
              Text(
                'была ошибка',
                style: textTheme.labelMedium?.copyWith(color: game.error),
              ),
          ],
        ),
      ),
    );
  }
}
