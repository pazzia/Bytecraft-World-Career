import 'package:flutter/material.dart';

import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';
import '../../../core/theme/game_colors.dart';
import '../../../shared/widgets/code_block.dart';
import '../../courses/domain/level_payload.dart';
import '../domain/answer.dart';
import 'question_renderer.dart';

class CodeOrderingRenderer extends QuestionRenderer {
  const CodeOrderingRenderer();

  @override
  bool get showsLevelCode => false;

  @override
  Widget build(BuildContext context, QuestionContext question) =>
      CodeOrderingView(question: question);
}

/// Drag & drop reordering of code lines.
///
/// Implemented with Draggable/DragTarget (not ReorderableListView) so the
/// whole card is the handle, it works inside the screen's scroll view and
/// doesn't depend on framework-version-specific reorder callbacks.
class CodeOrderingView extends StatelessWidget {
  const CodeOrderingView({super.key, required this.question});

  final QuestionContext question;

  static const Duration _dragDelay = Duration(milliseconds: 120);

  @override
  Widget build(BuildContext context) {
    final payload = question.level.payload as CodeOrderingPayload;
    final answer = switch (question.answer) {
      final OrderingAnswer ordering => ordering,
      _ => OrderingAnswer(List<int>.generate(payload.lines.length, (i) => i)),
    };
    final wrong = question.outcome?.wrongParts ?? const <int>{};
    final isCorrect = question.outcome?.isCorrect ?? false;

    return LayoutBuilder(
      builder: (context, constraints) => Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          for (var position = 0; position < answer.order.length; position++)
            Padding(
              padding: const EdgeInsets.only(bottom: Spacing.sm),
              child: _DropSlot(
                key: ValueKey('slot_${answer.order[position]}'),
                position: position,
                width: constraints.maxWidth,
                text: payload.lines[answer.order[position]],
                isWrong: wrong.contains(position),
                isCorrect: isCorrect,
                isLocked: question.isLocked,
                dragDelay: _dragDelay,
                onMove: (from, to) => question.onChanged(answer.move(from, to)),
              ),
            ),
        ],
      ),
    );
  }
}

class _DropSlot extends StatelessWidget {
  const _DropSlot({
    super.key,
    required this.position,
    required this.width,
    required this.text,
    required this.isWrong,
    required this.isCorrect,
    required this.isLocked,
    required this.dragDelay,
    required this.onMove,
  });

  final int position;
  final double width;
  final String text;
  final bool isWrong;
  final bool isCorrect;
  final bool isLocked;
  final Duration dragDelay;
  final void Function(int from, int to) onMove;

  @override
  Widget build(BuildContext context) {
    final card = _LineCard(
      text: text,
      isWrong: isWrong,
      isCorrect: isCorrect,
      isLocked: isLocked,
    );
    if (isLocked) return card;
    return DragTarget<int>(
      onWillAcceptWithDetails: (details) => details.data != position,
      onAcceptWithDetails: (details) => onMove(details.data, position),
      builder: (context, candidates, rejected) => LongPressDraggable<int>(
        data: position,
        delay: dragDelay,
        axis: Axis.vertical,
        feedback: Material(
          color: Colors.transparent,
          child: SizedBox(
            width: width,
            child: _LineCard(
              text: text,
              isWrong: false,
              isCorrect: false,
              isLocked: false,
              isLifted: true,
            ),
          ),
        ),
        childWhenDragging: Opacity(opacity: 0.25, child: card),
        child: candidates.isEmpty
            ? card
            : _LineCard(
                text: text,
                isWrong: false,
                isCorrect: false,
                isLocked: false,
                isDropTarget: true,
              ),
      ),
    );
  }
}

class _LineCard extends StatelessWidget {
  const _LineCard({
    required this.text,
    required this.isWrong,
    required this.isCorrect,
    required this.isLocked,
    this.isLifted = false,
    this.isDropTarget = false,
  });

  final String text;
  final bool isWrong;
  final bool isCorrect;
  final bool isLocked;
  final bool isLifted;
  final bool isDropTarget;

  @override
  Widget build(BuildContext context) {
    final colors = context.gameColors;
    final scheme = Theme.of(context).colorScheme;
    final border = isWrong
        ? colors.error
        : isCorrect
            ? colors.success
            : isDropTarget || isLifted
                ? scheme.primary
                : colors.codeBackground;
    return AnimatedContainer(
      duration: AppDurations.fast,
      constraints: const BoxConstraints(minHeight: Spacing.touchTarget),
      decoration: BoxDecoration(
        color: colors.codeBackground,
        borderRadius: AppRadius.mdAll,
        border: Border.all(color: border, width: 2),
        boxShadow: isLifted ? AppShadows.raised : null,
      ),
      padding: const EdgeInsets.symmetric(horizontal: Spacing.md),
      child: Row(
        children: [
          Expanded(
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Text.rich(
                TextSpan(children: highlightPython(text, colors)),
                style: AppTypography.code(color: colors.codeText),
                softWrap: false,
              ),
            ),
          ),
          if (!isLocked)
            Icon(Icons.drag_indicator_rounded, color: colors.codeComment),
        ],
      ),
    );
  }
}
