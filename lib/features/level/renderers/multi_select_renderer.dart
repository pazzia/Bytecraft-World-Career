import 'package:flutter/material.dart';

import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';
import '../../../core/theme/game_colors.dart';
import '../../../shared/widgets/keycap.dart';
import '../../courses/domain/level_payload.dart';
import '../domain/answer.dart';
import 'question_renderer.dart';

class MultiSelectRenderer extends QuestionRenderer {
  const MultiSelectRenderer();

  @override
  Widget build(BuildContext context, QuestionContext question) =>
      MultiSelectView(question: question);
}

/// Checkbox keys: pick every correct option.
class MultiSelectView extends StatelessWidget {
  const MultiSelectView({super.key, required this.question});

  final QuestionContext question;

  @override
  Widget build(BuildContext context) {
    final payload = question.level.payload as MultiSelectPayload;
    final answer = switch (question.answer) {
      final OptionSetAnswer set => set,
      _ => OptionSetAnswer(const <int>{}),
    };
    final outcome = question.outcome;
    final game = context.gameColors;
    final count = payload.correctIndexes.length;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          'Верных вариантов: $count',
          style: Theme.of(context)
              .textTheme
              .labelLarge
              ?.copyWith(color: game.textMuted),
        ),
        const SizedBox(height: Spacing.md),
        for (var i = 0; i < payload.options.length; i++)
          Padding(
            padding: const EdgeInsets.only(bottom: Spacing.md),
            child: _CheckTile(
              key: ValueKey('multi_option_$i'),
              label: payload.options[i],
              checked: answer.options.contains(i),
              status: outcome == null || !answer.options.contains(i)
                  ? _Status.neutral
                  : outcome.isCorrect
                      ? _Status.correct
                      : outcome.wrongParts.contains(i)
                          ? _Status.wrong
                          : _Status.neutral,
              onTap: question.isLocked
                  ? null
                  : () => question.onChanged(answer.toggle(i)),
            ),
          ),
      ],
    );
  }
}

enum _Status { neutral, correct, wrong }

class _CheckTile extends StatelessWidget {
  const _CheckTile({
    super.key,
    required this.label,
    required this.checked,
    required this.status,
    required this.onTap,
  });

  final String label;
  final bool checked;
  final _Status status;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final game = context.gameColors;
    final (Color face, Color edge, Color border, Color text) = switch (status) {
      _Status.correct =>
        (game.successTint, game.successEdge, game.success, game.successEdge),
      _Status.wrong =>
        (game.errorTint, game.errorEdge, game.error, game.errorEdge),
      _Status.neutral => checked
          ? (game.primaryTint, game.primaryEdge, scheme.primary, scheme.onSurface)
          : (game.keyFace, game.keyEdge, game.keyBorder, scheme.onSurface),
    };
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final labelColor = isDark && status != _Status.neutral
        ? (status == _Status.correct ? game.successBright : game.errorBright)
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
      selected: checked,
      child: Row(
        children: [
          Icon(
            checked
                ? Icons.check_box_rounded
                : Icons.check_box_outline_blank_rounded,
            color: checked ? (status == _Status.neutral ? scheme.primary : labelColor) : game.textMuted,
          ),
          const SizedBox(width: Spacing.md),
          Expanded(
            child: Text(
              label,
              style: AppTypography.code(
                color: labelColor,
                size: 17,
                weight: FontWeight.w700,
              ).copyWith(height: 1.3),
            ),
          ),
        ],
      ),
    );
  }
}
