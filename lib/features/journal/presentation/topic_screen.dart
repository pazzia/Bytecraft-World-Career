import '../../../shared/widgets/code_copy.dart';
import '../../world/presentation/world_controller.dart';
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
  const TopicScreen({super.key, required this.topicId});

  final String topicId;

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

    return Scaffold(
      appBar: AppBar(title: Text(topic?.title ?? 'Тема')),
      body: topic == null
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.fromLTRB(
                Spacing.page,
                Spacing.md,
                Spacing.page,
                Spacing.huge,
              ),
              children: [
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
                    onPressed: () => runJournalAction(
                      ref,
                      (service, courseId) => service.add(courseId, topicId),
                    ),
                  ),
                const SizedBox(height: Spacing.xxl),
                CodeCopyScope(
                  wrongAnswers: ref.watch(worldControllerProvider).value?.failures['topic:${ref.watch(activeCourseIdProvider).value}:$topicId'] ?? 0,
                  child: TopicContent(topic: topic, showTitle: false)),
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
                if (entry != null) ...[
                  const SizedBox(height: Spacing.xxl),
                  AppButton(
                    label: 'Убрать из журнала',
                    variant: AppButtonVariant.quiet,
                    onPressed: () => runJournalAction(
                      ref,
                      (service, courseId) => service.remove(courseId, topicId),
                    ),
                  ),
                ],
                if (topic.examples.isEmpty && all.isEmpty)
                  Text(
                    'Для этой темы пока нет упражнений.',
                    style: textTheme.bodyMedium?.copyWith(color: game.textMuted),
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
