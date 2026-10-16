import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

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

/// Drag & drop reordering of code lines, each line a dark key.
///
/// Implemented with Draggable/DragTarget (not ReorderableListView) so the
/// whole key is the handle, it works inside the screen's scroll view and
/// doesn't depend on framework-version-specific reorder callbacks.
/// Screen readers get "move up / move down" actions instead of dragging.
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
              padding: const EdgeInsets.only(bottom: Spacing.md),
              child: _DropSlot(
                key: ValueKey('slot_${answer.order[position]}'),
                position: position,
                count: answer.order.length,
                width: constraints.maxWidth,
                text: payload.lines[answer.order[position]],
                isWrong: wrong.contains(position),
                isCorrect: isCorrect,
                isLocked: question.isLocked,
                dragDelay: _dragDelay,
                onMove: (from, to) => question.onChanged(answer.move(from, to)),
              ),
            ),
          if (!question.isLocked)
            Text(
              'Удерживайте строку и перетащите её на нужное место',
              style: Theme.of(context)
                  .textTheme
                  .bodySmall
                  ?.copyWith(color: context.gameColors.textMuted),
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
    required this.count,
    required this.width,
    required this.text,
    required this.isWrong,
    required this.isCorrect,
    required this.isLocked,
    required this.dragDelay,
    required this.onMove,
  });

  final int position;
  final int count;
  final double width;
  final String text;
  final bool isWrong;
  final bool isCorrect;
  final bool isLocked;
  final Duration dragDelay;
  final void Function(int from, int to) onMove;

  @override
  Widget build(BuildContext context) {
    final card = _LineKey(
      text: text,
      state: isWrong
          ? _LineState.wrong
          : isCorrect
              ? _LineState.correct
              : _LineState.idle,
      showHandle: !isLocked,
    );
    if (isLocked) return card;
    return Semantics(
      label: 'Строка ${position + 1} из $count: $text',
      customSemanticsActions: {
        if (position > 0)
          const CustomSemanticsAction(label: 'Поднять выше'): () =>
              onMove(position, position - 1),
        if (position < count - 1)
          const CustomSemanticsAction(label: 'Опустить ниже'): () =>
              onMove(position, position + 1),
      },
      child: DragTarget<int>(
        onWillAcceptWithDetails: (details) => details.data != position,
        onAcceptWithDetails: (details) {
          HapticFeedback.selectionClick();
          onMove(details.data, position);
        },
        builder: (context, candidates, rejected) => LongPressDraggable<int>(
          data: position,
          delay: dragDelay,
          axis: Axis.vertical,
          hapticFeedbackOnStart: true,
          feedback: Material(
            color: Colors.transparent,
            child: SizedBox(
              width: width,
              child: Transform.rotate(
                angle: -0.025,
                child: _LineKey(
                  text: text,
                  state: _LineState.lifted,
                  showHandle: true,
                ),
              ),
            ),
          ),
          childWhenDragging: const _Socket(height: 58),
          child: candidates.isEmpty
              ? card
              : _LineKey(
                  text: text,
                  state: _LineState.dropTarget,
                  showHandle: true,
                ),
        ),
      ),
    );
  }
}

enum _LineState { idle, lifted, dropTarget, wrong, correct }

class _Socket extends StatelessWidget {
  const _Socket({required this.height});

  final double height;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Container(
      height: height,
      margin: const EdgeInsets.only(bottom: 4),
      decoration: BoxDecoration(
        color: scheme.primary.withValues(alpha: 0.08),
        borderRadius: AppRadius.mdAll,
        border: Border.all(color: scheme.primary, width: 2),
      ),
    );
  }
}

class _LineKey extends StatelessWidget {
  const _LineKey({
    required this.text,
    required this.state,
    required this.showHandle,
  });

  final String text;
  final _LineState state;
  final bool showHandle;

  @override
  Widget build(BuildContext context) {
    final colors = context.gameColors;
    final scheme = Theme.of(context).colorScheme;
    final border = switch (state) {
      _LineState.wrong => colors.error,
      _LineState.correct => colors.success,
      _LineState.lifted || _LineState.dropTarget => scheme.primary,
      _LineState.idle => colors.board,
    };
    return Container(
      constraints: const BoxConstraints(minHeight: 58),
      margin: const EdgeInsets.only(bottom: 4),
      decoration: BoxDecoration(
        color: state == _LineState.lifted
            ? Color.lerp(colors.board, Colors.white, 0.1)
            : colors.board,
        borderRadius: AppRadius.mdAll,
        border: Border.all(color: border, width: 2),
        boxShadow: [
          BoxShadow(color: colors.boardEdge, offset: const Offset(0, 4)),
          if (state == _LineState.lifted) ...const [
            BoxShadow(
              color: Color(0x66000000),
              blurRadius: 28,
              offset: Offset(0, 14),
            ),
          ],
        ],
      ),
      padding: const EdgeInsets.only(left: Spacing.lg, right: Spacing.md),
      child: Row(
        children: [
          Expanded(
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Text.rich(
                TextSpan(children: highlightPython(text, colors)),
                style: AppTypography.code(color: colors.codeText, size: 17),
                softWrap: false,
              ),
            ),
          ),
          if (showHandle)
            Icon(
              Icons.drag_indicator_rounded,
              color: state == _LineState.lifted
                  ? scheme.primary
                  : colors.codeLineNumber,
            ),
        ],
      ),
    );
  }
}
