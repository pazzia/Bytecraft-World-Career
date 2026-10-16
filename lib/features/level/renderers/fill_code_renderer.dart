import 'package:flutter/material.dart';

import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';
import '../../../core/theme/game_colors.dart';
import '../../../shared/widgets/code_block.dart';
import '../../../shared/widgets/keycap.dart';
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

/// Code on the board with slots + a bank of token keys.
/// Tap a key to drop it into the next empty slot; tap a slot to take the
/// key back out.
class FillCodeView extends StatelessWidget {
  const FillCodeView({super.key, required this.question});

  final QuestionContext question;

  /// Which option keys are already placed (supports duplicate tokens).
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
            index: index,
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
    final lines = FillCodeTemplate.lines(payload.template);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        CodeBoard(
          padding: const EdgeInsets.all(Spacing.lg),
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                for (var i = 0; i < lines.length; i++)
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: Spacing.xs),
                    child: Row(
                      children: [
                        SizedBox(
                          width: 26,
                          child: Text(
                            '${i + 1}',
                            style: AppTypography.code(
                              color: colors.codeLineNumber,
                              size: 13,
                            ),
                          ),
                        ),
                        Text.rich(
                          TextSpan(
                            children: [
                              for (final segment in lines[i])
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
                      ],
                    ),
                  ),
              ],
            ),
          ),
        ),
        const SizedBox(height: Spacing.xxl),
        _TokenGrid(
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

class _TokenGrid extends StatelessWidget {
  const _TokenGrid({required this.children});

  final List<Widget> children;

  @override
  Widget build(BuildContext context) => Column(
        children: [
          for (var row = 0; row < children.length; row += 2)
            Padding(
              padding: const EdgeInsets.only(bottom: Spacing.md),
              child: Row(
                children: [
                  Expanded(child: children[row]),
                  const SizedBox(width: Spacing.md),
                  Expanded(
                    child: row + 1 < children.length
                        ? children[row + 1]
                        : const SizedBox.shrink(),
                  ),
                ],
              ),
            ),
        ],
      );
}

class _BlankSlot extends StatelessWidget {
  const _BlankSlot({
    super.key,
    required this.index,
    required this.token,
    required this.isWrong,
    required this.isCorrect,
    required this.onTap,
  });

  final int index;
  final String? token;
  final bool isWrong;
  final bool isCorrect;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final colors = context.gameColors;
    final slotStyle = AppTypography.code(
      color: colors.onReward,
      size: 18,
      weight: FontWeight.w700,
    ).copyWith(height: 1.2);
    if (token == null) {
      return Semantics(
        label: 'Пропуск ${index + 1}, пустой',
        child: Container(
          constraints: const BoxConstraints(minWidth: 60, minHeight: 34),
          margin: const EdgeInsets.symmetric(horizontal: Spacing.xs),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(9),
            border: Border.all(color: colors.codeLineNumber, width: 2),
          ),
        ),
      );
    }
    final (Color face, Color edge, Color text) = isWrong
        ? (colors.errorBright, colors.errorEdge, Colors.white)
        : isCorrect
            ? (colors.successBright, colors.successEdge, Colors.white)
            : (colors.reward, colors.rewardEdge, colors.onReward);
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: Spacing.xs),
      child: Keycap(
        onTap: onTap,
        face: face,
        edge: edge,
        radius: 9,
        depth: 3,
        padding: const EdgeInsets.symmetric(
          horizontal: Spacing.md,
          vertical: Spacing.xs,
        ),
        semanticLabel: 'Пропуск ${index + 1}: $token. Нажмите, чтобы убрать',
        child: Text(token!, style: slotStyle.copyWith(color: text)),
      ),
    );
  }
}

/// A large selectable code token key.
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
    final text = Text(
      label,
      textAlign: TextAlign.center,
      style: AppTypography.code(
        color: isUsed ? game.lockedIcon : scheme.onSurface,
        size: 20,
        weight: FontWeight.w700,
      ).copyWith(height: 1.2),
    );
    if (isUsed) {
      // An empty socket where the key was.
      return Semantics(
        label: '$label, уже в коде',
        excludeSemantics: true,
        child: Container(
          height: 60,
          margin: const EdgeInsets.only(bottom: 4),
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: game.track,
            borderRadius: AppRadius.lgAll,
          ),
          child: text,
        ),
      );
    }
    return Keycap(
      onTap: onTap,
      face: game.keyFace,
      edge: game.keyEdge,
      border: game.keyBorder,
      height: 64,
      semanticLabel: label,
      child: text,
    );
  }
}
