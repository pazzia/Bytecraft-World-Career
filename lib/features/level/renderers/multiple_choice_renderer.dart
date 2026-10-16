import 'package:flutter/material.dart';

import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';
import '../../../core/theme/game_colors.dart';
import '../../courses/domain/level_payload.dart';
import '../domain/answer.dart';
import 'question_renderer.dart';

class MultipleChoiceRenderer extends QuestionRenderer {
  const MultipleChoiceRenderer();

  @override
  Widget build(BuildContext context, QuestionContext question) =>
      MultipleChoiceView(question: question);
}

class MultipleChoiceView extends StatelessWidget {
  const MultipleChoiceView({super.key, required this.question});

  final QuestionContext question;

  @override
  Widget build(BuildContext context) {
    final payload = question.level.payload as MultipleChoicePayload;
    final selected = switch (question.answer) {
      ChoiceAnswer(:final optionIndex) => optionIndex,
      _ => null,
    };
    final outcome = question.outcome;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        for (var i = 0; i < payload.options.length; i++)
          Padding(
            padding: const EdgeInsets.only(bottom: Spacing.md),
            child: OptionTile(
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
          ),
      ],
    );
  }
}

enum OptionStatus { neutral, correct, wrong }

/// Large, thumb-friendly answer button.
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

  static const double _fillAlpha = 0.12;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final game = context.gameColors;
    final accent = switch (status) {
      OptionStatus.correct => game.success,
      OptionStatus.wrong => game.error,
      OptionStatus.neutral => isSelected ? scheme.primary : scheme.outline,
    };
    return AnimatedContainer(
      duration: AppDurations.fast,
      constraints: const BoxConstraints(minHeight: Spacing.touchTarget + 4),
      decoration: BoxDecoration(
        color: isSelected
            ? accent.withValues(alpha: _fillAlpha)
            : scheme.surface,
        borderRadius: AppRadius.lgAll,
        border: Border.all(color: accent, width: 2),
        boxShadow: AppShadows.edge(accent),
      ),
      child: Material(
        type: MaterialType.transparency,
        child: InkWell(
          borderRadius: AppRadius.lgAll,
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.symmetric(
              horizontal: Spacing.lg,
              vertical: Spacing.md,
            ),
            child: Align(
              alignment: Alignment.centerLeft,
              child: Text(
                label,
                style: AppTypography.code(color: scheme.onSurface),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
