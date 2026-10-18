import '../../../../shared/widgets/code_copy.dart';
import '../../../../features/world/presentation/world_controller.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_spacing.dart';
import '../../../../core/theme/game_colors.dart';
import '../../../../shared/widgets/app_button.dart';
import '../../../../shared/widgets/code_block.dart';
import '../../../../shared/widgets/output_board.dart';
import '../../../journal/presentation/journal_providers.dart';
import '../../../journal/presentation/widgets/topic_content.dart';
import '../level_controller.dart';
import '../level_ui_state.dart';

/// Opens the detailed review of the current level.
Future<void> showLevelReview(BuildContext context, LevelArgs args) =>
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      showDragHandle: true,
      builder: (context) => LevelReviewSheet(args: args),
    );

/// Detailed review: what went wrong, the topic with worked examples, the
/// solution (only once the level is solved or the player gave up) and a
/// button to keep the topic in the journal.
class LevelReviewSheet extends ConsumerWidget {
  const LevelReviewSheet({super.key, required this.args});

  final LevelArgs args;

  static final RegExp _errorResult = RegExp(r'^\w*(Error|Exception)\b');

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(levelControllerProvider(args));
    final controller = ref.read(levelControllerProvider(args).notifier);
    final level = state.session?.level;
    if (level == null) return const SizedBox.shrink();
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    final solved = state.phase == LevelPhase.correctAnswer ||
        state.phase == LevelPhase.completed;
    final showSolution = solved || state.isSolutionRevealed;
    final topic =
        ref.watch(topicCatalogProvider).value?.byId(level.topicId);
    final journal = ref.watch(journalProvider).value;
    final saved = level.topicId != null && (journal?.contains(level.topicId!) ?? false);
    final note = state.mistakeNote;
    final solution = level.solution;

    final persisted = ref.watch(worldControllerProvider).value?.failures['lesson:${args.courseId}:${args.levelId}'] ?? 0;
    final errors = state.session?.mistakes ?? 0;
    return CodeCopyScope(wrongAnswers: errors > persisted ? errors : persisted, child: DraggableScrollableSheet(
      expand: false,
      initialChildSize: 0.88,
      minChildSize: 0.4,
      maxChildSize: 0.95,
      builder: (context, scroll) => ListView(
        controller: scroll,
        padding: const EdgeInsets.fromLTRB(
          Spacing.page,
          0,
          Spacing.page,
          Spacing.huge,
        ),
        children: [
          Text('Разбор', style: textTheme.headlineSmall),
          const SizedBox(height: Spacing.xs),
          Text(
            level.title,
            style: textTheme.titleSmall?.copyWith(color: game.textMuted),
          ),
          if (level.topicId != null) ...[
            const SizedBox(height: Spacing.lg),
            // On top: saving the topic is the main action of the review.
            AppButton(
              key: const ValueKey('journal_toggle'),
              label: saved ? 'В журнале · убрать' : 'Сохранить тему в журнал',
              icon: saved ? Icons.bookmark_rounded : Icons.bookmark_add_rounded,
              variant:
                  saved ? AppButtonVariant.secondary : AppButtonVariant.primary,
              onPressed: () => controller.toggleTopicInJournal(save: !saved),
            ),
          ],
          if (note != null && !solved) ...[
            const SizedBox(height: Spacing.xl),
            Text('Что не так', style: textTheme.titleMedium),
            const SizedBox(height: Spacing.sm),
            Text(note.text, style: textTheme.bodyLarge),
            if (note.programResult != null) ...[
              const SizedBox(height: Spacing.sm),
              OutputBoard(
                label: 'С вашим вариантом программа выдаст',
                output: note.programResult!,
                isError: _errorResult.hasMatch(note.programResult!),
              ),
            ],
          ],
          if (showSolution && level.explanation != null) ...[
            const SizedBox(height: Spacing.xl),
            Text('Почему так', style: textTheme.titleMedium),
            const SizedBox(height: Spacing.sm),
            Text(level.explanation!, style: textTheme.bodyLarge),
          ],
          if (solution != null) ...[
            const SizedBox(height: Spacing.xl),
            Text('Решение', style: textTheme.titleMedium),
            const SizedBox(height: Spacing.sm),
            if (showSolution) ...[
              CodeBlock(code: solution.code),
              const SizedBox(height: Spacing.sm),
              OutputBoard(output: solution.output),
            ] else if (state.canRevealSolution)
              AppButton(
                key: const ValueKey('reveal_solution'),
                label: 'Показать решение',
                variant: AppButtonVariant.secondary,
                onPressed: controller.revealSolution,
              )
            else
              Text(
                'Откроется после правильного ответа '
                'или после ${LevelUiState.mistakesBeforeSolution} ошибок.',
                style: textTheme.bodyMedium?.copyWith(color: game.textMuted),
              ),
          ],
          if (topic != null) ...[
            const SizedBox(height: Spacing.xxl),
            Text('Тема', style: textTheme.titleMedium),
            const SizedBox(height: Spacing.sm),
            TopicContent(topic: topic),
          ],
        ],
      ),
    ));
  }
}
