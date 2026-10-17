import 'package:flutter/material.dart';

import '../../../../core/theme/app_spacing.dart';
import '../../../../core/theme/game_colors.dart';
import '../../../../shared/widgets/code_block.dart';
import '../../../../shared/widgets/output_board.dart';
import '../../domain/topic.dart';

/// The reference card of a topic: explanation, worked examples with their
/// real output, typical mistakes.
class TopicContent extends StatelessWidget {
  const TopicContent({super.key, required this.topic, this.showTitle = true});

  final Topic topic;
  final bool showTitle;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    final paragraphs = topic.body
        .split(RegExp(r'\n\s*\n'))
        .map((paragraph) => paragraph.trim())
        .where((paragraph) => paragraph.isNotEmpty);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (showTitle) ...[
          Text(topic.title, style: textTheme.titleLarge),
          const SizedBox(height: Spacing.sm),
        ],
        Container(
          padding: const EdgeInsets.all(Spacing.md),
          decoration: BoxDecoration(
            color: game.primaryTint,
            borderRadius: AppRadius.lgAll,
          ),
          child: Text(
            topic.summary,
            style: textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.w600),
          ),
        ),
        for (final paragraph in paragraphs) ...[
          const SizedBox(height: Spacing.md),
          Text(paragraph, style: textTheme.bodyLarge),
        ],
        for (var i = 0; i < topic.examples.length; i++) ...[
          const SizedBox(height: Spacing.xl),
          Text(
            topic.examples.length == 1 ? 'Пример' : 'Пример ${i + 1}',
            style: textTheme.titleSmall,
          ),
          if (topic.examples[i].note != null) ...[
            const SizedBox(height: Spacing.xs),
            Text(
              topic.examples[i].note!,
              style: textTheme.bodyMedium?.copyWith(color: game.textMuted),
            ),
          ],
          const SizedBox(height: Spacing.sm),
          CodeBlock(code: topic.examples[i].code),
          const SizedBox(height: Spacing.sm),
          OutputBoard(output: topic.examples[i].output),
        ],
        if (topic.pitfalls.isNotEmpty) ...[
          const SizedBox(height: Spacing.xl),
          Text('Частые ошибки', style: textTheme.titleSmall),
          const SizedBox(height: Spacing.sm),
          for (final pitfall in topic.pitfalls)
            Padding(
              padding: const EdgeInsets.only(bottom: Spacing.sm),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: const EdgeInsets.only(top: 2),
                    child: Icon(
                      Icons.warning_amber_rounded,
                      size: 20,
                      color: game.streak,
                    ),
                  ),
                  const SizedBox(width: Spacing.sm),
                  Expanded(child: Text(pitfall, style: textTheme.bodyMedium)),
                ],
              ),
            ),
        ],
      ],
    );
  }
}
