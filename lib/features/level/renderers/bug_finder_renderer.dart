import 'package:flutter/material.dart';

import '../../../core/theme/game_colors.dart';
import '../../../shared/widgets/code_block.dart';
import '../domain/answer.dart';
import 'question_renderer.dart';

class BugFinderRenderer extends QuestionRenderer {
  const BugFinderRenderer();

  @override
  bool get showsLevelCode => false;

  @override
  Widget? buildStage(BuildContext context, QuestionContext question) =>
      BugFinderView(question: question);

  @override
  Widget build(BuildContext context, QuestionContext question) => Text(
        'Нажмите на строку с ошибкой',
        style: Theme.of(context)
            .textTheme
            .bodySmall
            ?.copyWith(color: context.gameColors.textMuted),
      );
}

/// Tap the line(s) containing a bug.
class BugFinderView extends StatelessWidget {
  const BugFinderView({super.key, required this.question});

  final QuestionContext question;

  @override
  Widget build(BuildContext context) {
    final answer = switch (question.answer) {
      final LineSelectionAnswer selection => selection,
      _ => LineSelectionAnswer(const <int>{}),
    };
    final outcome = question.outcome;
    return CodeBlock(
          code: question.level.code ?? '',
          selectedLines: answer.lines,
          errorLines: outcome != null && !outcome.isCorrect
              ? outcome.wrongParts
              : const <int>{},
          successLines: outcome != null && outcome.isCorrect
              ? answer.lines
              : const <int>{},
          onLineTap: question.isLocked
              ? null
              : (line) => question.onChanged(answer.toggle(line)),
        expandable: true,
    );
  }
}
