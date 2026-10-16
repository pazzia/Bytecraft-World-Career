import 'package:flutter/material.dart';

import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';
import '../../../core/theme/game_colors.dart';
import '../../../shared/widgets/code_block.dart';
import '../../courses/domain/fill_code_template.dart';
import '../../courses/domain/level_payload.dart';
import '../domain/answer.dart';
import 'question_renderer.dart';

class FillCodeRenderer extends QuestionRenderer {
  const FillCodeRenderer();

  @override
  bool get showsLevelCode => false;

  @override
  Widget build(BuildContext context, QuestionContext question) =>
      FillCodeView(question: question);
}

/// Code with tappable blanks + a bank of large tokens.
/// Tap a token to fill the next empty blank; tap a filled blank to clear it.
class FillCodeView extends StatelessWidget {
  const FillCodeView({super.key, required this.question});

  final QuestionContext question;

  /// Which option chips are already placed (supports duplicate tokens).
  static Set<int> usedOptionIndexes(List<String> options, List<String?> tokens) {
    final remaining = <String, int>{};
    for (final token in tokens) {
      if (token != null) remaining[token] = (remaining[token] ?? 0) + 1;
    }
    final used = <int>{};
    for (var i = 0; i < options.length; i++) {
      final count = remaining[options[i]] ?? 0;
      if (count > 0) {
        used.add(i);
        remaining[options[i]] = count - 1;
      }
    }
    return used;
  }

  InlineSpan _spanFor(
    TemplateSegment segment, {
    required FillCodeAnswer answer,
    required GameColors colors,
    required Set<int> wrong,
    required bool isCorrect,
  }) {
    switch (segment) {
      case TextSegment(:final text):
        return TextSpan(children: highlightPython(text, colors));
      case BlankSegment(:final index):
        return WidgetSpan(
          alignment: PlaceholderAlignment.middle,
          child: _BlankSlot(
            key: ValueKey('blank_$index'),
            token: index < answer.tokens.length ? answer.tokens[index] : null,
            isWrong: wrong.contains(index),
            isCorrect: isCorrect,
            onTap: question.isLocked
                ? null
                : () => question.onChanged(answer.clear(index)),
          ),
        );
    }
  }

  @override
  Widget build(BuildContext context) {
    final payload = question.level.payload as FillCodePayload;
    final answer = switch (question.answer) {
      final FillCodeAnswer fill => fill,
      _ => FillCodeAnswer.empty(payload.blankCount),
    };
    final used = usedOptionIndexes(payload.options, answer.tokens);
    final colors = context.gameColors;
    final wrong = question.outcome?.wrongParts ?? const <int>{};
    final isCorrect = question.outcome?.isCorrect ?? false;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Container(
          decoration: BoxDecoration(
            color: colors.codeBackground,
            borderRadius: AppRadius.lgAll,
          ),
          padding: const EdgeInsets.all(Spacing.lg),
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                for (final line in FillCodeTemplate.lines(payload.template))
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: Spacing.xxs),
                    child: Text.rich(
                      TextSpan(
                        children: [
                          for (final segment in line)
                            _spanFor(
                              segment,
                              answer: answer,
                              colors: colors,
                              wrong: wrong,
                              isCorrect: isCorrect,
                            ),
                        ],
                      ),
                      style: AppTypography.code(color: colors.codeText),
                      softWrap: false,
                    ),
                  ),
              ],
            ),
          ),
        ),
        const SizedBox(height: Spacing.xl),
        Wrap(
          spacing: Spacing.md,
          runSpacing: Spacing.md,
          alignment: WrapAlignment.center,
          children: [
            for (var i = 0; i < payload.options.length; i++)
              TokenChip(
                key: ValueKey('token_$i'),
                label: payload.options[i],
                isUsed: used.contains(i),
                onTap: question.isLocked || used.contains(i) || answer.isComplete
                    ? null
                    : () => question.onChanged(answer.place(payload.options[i])),
              ),
          ],
        ),
      ],
    );
  }
}

class _BlankSlot extends StatelessWidget {
  const _BlankSlot({
    super.key,
    required this.token,
    required this.isWrong,
    required this.isCorrect,
    required this.onTap,
  });

  final String? token;
  final bool isWrong;
  final bool isCorrect;
  final VoidCallback? onTap;

  static const double _minWidth = 56;

  @override
  Widget build(BuildContext context) {
    final colors = context.gameColors;
    final scheme = Theme.of(context).colorScheme;
    final border = isWrong
        ? colors.error
        : isCorrect
            ? colors.success
            : token == null
                ? colors.codeComment
                : scheme.primary;
    return GestureDetector(
      onTap: token == null ? null : onTap,
      child: Container(
        constraints: const BoxConstraints(minWidth: _minWidth),
        margin: const EdgeInsets.symmetric(horizontal: Spacing.xs),
        padding: const EdgeInsets.symmetric(
          horizontal: Spacing.sm,
          vertical: Spacing.xxs,
        ),
        decoration: BoxDecoration(
          color: token == null
              ? Colors.transparent
              : border.withValues(alpha: 0.25),
          borderRadius: AppRadius.smAll,
          border: Border.all(color: border, width: 2),
        ),
        child: Text(
          token ?? ' ',
          textAlign: TextAlign.center,
          style: AppTypography.code(color: colors.codeText),
        ),
      ),
    );
  }
}

/// Large selectable code token.
class TokenChip extends StatelessWidget {
  const TokenChip({
    super.key,
    required this.label,
    required this.isUsed,
    required this.onTap,
  });

  final String label;
  final bool isUsed;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final game = context.gameColors;
    return AnimatedOpacity(
      duration: AppDurations.fast,
      opacity: isUsed ? 0.3 : 1,
      child: Container(
        constraints: const BoxConstraints(
          minHeight: Spacing.touchTarget,
          minWidth: Spacing.touchTarget + Spacing.lg,
        ),
        decoration: BoxDecoration(
          color: scheme.surface,
          borderRadius: AppRadius.mdAll,
          border: Border.all(color: scheme.outline, width: 2),
          boxShadow: AppShadows.edge(isUsed ? game.locked : scheme.outline),
        ),
        child: Material(
          type: MaterialType.transparency,
          child: InkWell(
            borderRadius: AppRadius.mdAll,
            onTap: onTap,
            child: Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: Spacing.lg,
                vertical: Spacing.md,
              ),
              child: Text(
                label,
                textAlign: TextAlign.center,
                style: AppTypography.code(color: scheme.onSurface, size: 18),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
