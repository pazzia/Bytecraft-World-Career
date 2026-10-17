import 'package:flutter/material.dart';

import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';
import '../../../core/theme/game_colors.dart';
import '../../../shared/widgets/keycap.dart';
import '../../courses/domain/level_payload.dart';
import '../domain/answer.dart';
import '../domain/initial_answer_factory.dart';
import 'question_renderer.dart';

class MatchPairsRenderer extends QuestionRenderer {
  const MatchPairsRenderer();

  @override
  Widget build(BuildContext context, QuestionContext question) => MatchPairsView(
        key: ValueKey('match_${question.level.id}'),
        question: question,
      );
}

/// Two columns of keys: tap an item on the left, then its partner on the
/// right. Linked pairs share a colour; tapping a linked left item unlinks it.
class MatchPairsView extends StatefulWidget {
  const MatchPairsView({super.key, required this.question});

  final QuestionContext question;

  @override
  State<MatchPairsView> createState() => _MatchPairsViewState();
}

class _MatchPairsViewState extends State<MatchPairsView> {
  int? _selectedLeft;

  static const List<Color> _pairColors = [
    Color(0xFF2F6DB5),
    Color(0xFF8E44AD),
    Color(0xFFE67E22),
    Color(0xFF16A085),
    Color(0xFFC0392B),
    Color(0xFF7F8C8D),
  ];

  MatchPairsPayload get _payload =>
      widget.question.level.payload as MatchPairsPayload;

  MatchAnswer get _answer => switch (widget.question.answer) {
        final MatchAnswer match => match,
        _ => MatchAnswer.empty(_payload.pairs.length),
      };

  /// Right column order: a stable shuffle that never matches the left.
  late final List<int> _rightOrder = InitialAnswerFactory.shuffledOrder(
    _payload.pairs.length,
    const [],
    widget.question.level.id.hashCode,
  );

  void _tapLeft(int left) {
    if (widget.question.isLocked) return;
    if (_answer.links.containsKey(left)) {
      widget.question.onChanged(_answer.unlinkLeft(left));
      setState(() => _selectedLeft = left);
      return;
    }
    setState(() => _selectedLeft = _selectedLeft == left ? null : left);
  }

  void _tapRight(int right) {
    if (widget.question.isLocked) return;
    final left = _selectedLeft;
    if (left == null) {
      // Tapping a linked right item unlinks it.
      final linked = _answer.leftFor(right);
      if (linked != null) {
        widget.question.onChanged(_answer.unlinkLeft(linked));
      }
      return;
    }
    final next = _answer.link(left, right);
    widget.question.onChanged(next);
    setState(() {
      // Jump to the next unlinked left item.
      _selectedLeft = null;
      for (var i = 0; i < _payload.pairs.length; i++) {
        if (!next.links.containsKey(i)) {
          _selectedLeft = i;
          break;
        }
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final pairs = _payload.pairs;
    final answer = _answer;
    final outcome = widget.question.outcome;
    final game = context.gameColors;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          'Нажмите слева, затем пару справа',
          style: Theme.of(context)
              .textTheme
              .labelLarge
              ?.copyWith(color: game.textMuted),
        ),
        const SizedBox(height: Spacing.md),
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  for (var i = 0; i < pairs.length; i++)
                    Padding(
                      padding: const EdgeInsets.only(bottom: Spacing.md),
                      child: _MatchTile(
                        key: ValueKey('match_left_$i'),
                        label: pairs[i].left,
                        color: answer.links.containsKey(i)
                            ? _pairColors[i % _pairColors.length]
                            : null,
                        selected: _selectedLeft == i,
                        wrong: outcome != null &&
                            !outcome.isCorrect &&
                            outcome.wrongParts.contains(i),
                        correct: outcome?.isCorrect ?? false,
                        onTap: widget.question.isLocked ? null : () => _tapLeft(i),
                      ),
                    ),
                ],
              ),
            ),
            const SizedBox(width: Spacing.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  for (final right in _rightOrder)
                    Padding(
                      padding: const EdgeInsets.only(bottom: Spacing.md),
                      child: Builder(
                        builder: (context) {
                          final left = answer.leftFor(right);
                          return _MatchTile(
                            key: ValueKey('match_right_$right'),
                            label: pairs[right].right,
                            color: left == null
                                ? null
                                : _pairColors[left % _pairColors.length],
                            selected: false,
                            wrong: left != null &&
                                outcome != null &&
                                !outcome.isCorrect &&
                                outcome.wrongParts.contains(left),
                            correct: outcome?.isCorrect ?? false,
                            onTap: widget.question.isLocked
                                ? null
                                : () => _tapRight(right),
                          );
                        },
                      ),
                    ),
                ],
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _MatchTile extends StatelessWidget {
  const _MatchTile({
    super.key,
    required this.label,
    required this.color,
    required this.selected,
    required this.wrong,
    required this.correct,
    required this.onTap,
  });

  final String label;

  /// Pair colour when linked.
  final Color? color;
  final bool selected;
  final bool wrong;
  final bool correct;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final game = context.gameColors;
    final Color face;
    final Color border;
    final Color edge;
    if (wrong) {
      face = game.errorTint;
      border = game.error;
      edge = game.errorEdge;
    } else if (correct) {
      face = game.successTint;
      border = game.success;
      edge = game.successEdge;
    } else if (color != null) {
      face = color!.withValues(alpha: 0.16);
      border = color!;
      edge = color!;
    } else if (selected) {
      face = game.primaryTint;
      border = scheme.primary;
      edge = game.primaryEdge;
    } else {
      face = game.keyFace;
      border = game.keyBorder;
      edge = game.keyEdge;
    }
    return Keycap(
      onTap: onTap,
      face: face,
      edge: edge,
      border: border,
      padding: const EdgeInsets.symmetric(
        horizontal: Spacing.md,
        vertical: Spacing.md,
      ),
      semanticLabel: label,
      selected: selected || color != null,
      child: ConstrainedBox(
        constraints: const BoxConstraints(minHeight: 32),
        child: Center(
          child: Text(
            label,
            textAlign: TextAlign.center,
            style: AppTypography.code(
              color: scheme.onSurface,
              size: 15,
              weight: FontWeight.w700,
            ).copyWith(height: 1.3),
          ),
        ),
      ),
    );
  }
}
