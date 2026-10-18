import 'package:flutter/material.dart';

import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';
import '../../../core/theme/game_colors.dart';
import '../../../shared/widgets/keycap.dart';
import '../../courses/domain/level_payload.dart';
import '../domain/answer.dart';
import 'question_renderer.dart';

class MultipleChoiceRenderer extends QuestionRenderer {
  const MultipleChoiceRenderer();

  @override
  Widget build(BuildContext context, QuestionContext question) =>
      MultipleChoiceView(question: question);
}

/// Answer keys: a 2-column grid for short options (values, operators),
/// a column for longer ones.
class MultipleChoiceView extends StatelessWidget {
  const MultipleChoiceView({super.key, required this.question});

  final QuestionContext question;

  static const int _shortOptionLength = 10;

  @override
  Widget build(BuildContext context) {
    final payload = question.level.payload as MultipleChoicePayload;
    final selected = switch (question.answer) {
      ChoiceAnswer(:final optionIndex) => optionIndex,
      _ => null,
    };
    final outcome = question.outcome;
    final tiles = [
      for (var i = 0; i < payload.options.length; i++)
        OptionTile(
          key: ValueKey('option_$i'),
          label: payload.options[i],
          isSelected: selected == i,
          status: selected == i && outcome != null
              ? (outcome.isCorrect ? OptionStatus.correct : OptionStatus.wrong)
              : OptionStatus.neutral,
          onTap: question.isLocked
              ? null
              : () => question.onChanged(ChoiceAnswer(i)),
        ),
    ];
    final short =
        payload.options.every((option) => option.length <= _shortOptionLength);
    if (!short) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          for (final tile in tiles)
            Padding(
              padding: const EdgeInsets.only(bottom: Spacing.md),
              child: tile,
            ),
        ],
      );
    }
    return Column(
      children: [
        for (var row = 0; row < tiles.length; row += 2)
          Padding(
            padding: const EdgeInsets.only(bottom: Spacing.md),
            child: Row(
              children: [
                Expanded(child: tiles[row]),
                const SizedBox(width: Spacing.md),
                Expanded(
                  child: row + 1 < tiles.length
                      ? tiles[row + 1]
                      : const SizedBox.shrink(),
                ),
              ],
            ),
          ),
      ],
    );
  }
}

enum OptionStatus { neutral, correct, wrong }

/// One answer key.
class OptionTile extends StatelessWidget {
  const OptionTile({
    super.key,
    required this.label,
    required this.isSelected,
    required this.status,
    required this.onTap,
  });

  final String label;
  final bool isSelected;
  final OptionStatus status;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final game = context.gameColors;
    final (Color face, Color edge, Color border, Color text) = switch (status) {
      OptionStatus.correct =>
        (game.successTint, game.successEdge, game.success, game.successEdge),
      OptionStatus.wrong =>
        (game.errorTint, game.errorEdge, game.error, game.errorEdge),
      OptionStatus.neutral => isSelected
          ? (game.primaryTint, game.primaryEdge, scheme.primary, scheme.onSurface)
          : (game.keyFace, game.keyEdge, game.keyBorder, scheme.onSurface),
    };
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final labelColor = isDark && status != OptionStatus.neutral
        ? (status == OptionStatus.correct ? game.successBright : game.errorBright)
        : text;
    return Keycap(
      onTap: onTap,
      face: face,
      edge: edge,
      border: border,
      padding: const EdgeInsets.symmetric(
        horizontal: Spacing.lg,
        vertical: Spacing.md,
      ),
      semanticLabel: label,
      selected: isSelected,
      child: ConstrainedBox(
        constraints: const BoxConstraints(minHeight: 36),
        child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          if (status == OptionStatus.wrong) ...[
            Icon(Icons.close_rounded, size: 20, color: labelColor),
            const SizedBox(width: Spacing.sm),
          ],
          if (status == OptionStatus.correct) ...[
            Icon(Icons.check_rounded, size: 20, color: labelColor),
            const SizedBox(width: Spacing.sm),
          ],
          Flexible(
            child: Text(
              label,
              textAlign: TextAlign.center,
              style: AppTypography.code(
                color: labelColor,
                size: 19,
                weight: FontWeight.w700,
              ).copyWith(height: 1.25),
            ),
          ),
        ],
        ),
      ),
    );
  }
}
