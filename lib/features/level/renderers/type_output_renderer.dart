import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';
import '../../../core/theme/game_colors.dart';
import '../domain/answer.dart';
import 'question_renderer.dart';

class TypeOutputRenderer extends QuestionRenderer {
  const TypeOutputRenderer();

  @override
  Widget build(BuildContext context, QuestionContext question) =>
      TypeOutputView(
        key: ValueKey('type_output_${question.level.id}'),
        question: question,
      );
}

/// A terminal-like field where the player types the program's output.
/// Phone keyboards' autocorrect, suggestions and smart punctuation are off:
/// they would silently change the answer.
class TypeOutputView extends StatefulWidget {
  const TypeOutputView({super.key, required this.question});

  final QuestionContext question;

  @override
  State<TypeOutputView> createState() => _TypeOutputViewState();
}

class _TypeOutputViewState extends State<TypeOutputView> {
  late final TextEditingController _controller;

  String get _answerText => switch (widget.question.answer) {
        TextAnswer(:final text) => text,
        _ => '',
      };

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: _answerText);
  }

  @override
  void didUpdateWidget(TypeOutputView oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (_controller.text != _answerText) {
      _controller.value = TextEditingValue(
        text: _answerText,
        selection: TextSelection.collapsed(offset: _answerText.length),
      );
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    final outcome = widget.question.outcome;
    final border = outcome == null
        ? game.boardMuted
        : outcome.isCorrect
            ? game.success
            : game.error;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          'Вывод программы',
          style: Theme.of(context)
              .textTheme
              .labelLarge
              ?.copyWith(color: game.textMuted),
        ),
        const SizedBox(height: Spacing.sm),
        Container(
          decoration: BoxDecoration(
            color: game.board,
            borderRadius: AppRadius.lgAll,
            border: Border.all(color: border, width: 2),
          ),
          padding: const EdgeInsets.symmetric(
            horizontal: Spacing.lg,
            vertical: Spacing.sm,
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: const EdgeInsets.only(top: 12, right: Spacing.sm),
                child: Text(
                  '>',
                  style: AppTypography.code(color: game.codeLineNumber),
                ),
              ),
              Expanded(
                child: TextField(
                  key: const ValueKey('type_output_field'),
                  controller: _controller,
                  readOnly: widget.question.isLocked,
                  onChanged: (text) => widget.question.onChanged(TextAnswer(text)),
                  minLines: 2,
                  maxLines: 8,
                  keyboardType: TextInputType.multiline,
                  textCapitalization: TextCapitalization.none,
                  autocorrect: false,
                  enableSuggestions: false,
                  smartQuotesType: SmartQuotesType.disabled,
                  smartDashesType: SmartDashesType.disabled,
                  enableIMEPersonalizedLearning: false,
                  inputFormatters: [
                    FilteringTextInputFormatter.deny(RegExp('\t')),
                  ],
                  cursorColor: game.codeText,
                  style: AppTypography.code(color: game.codeText),
                  decoration: InputDecoration(
                    border: InputBorder.none,
                    enabledBorder: InputBorder.none,
                    focusedBorder: InputBorder.none,
                    filled: false,
                    isDense: true,
                    contentPadding: const EdgeInsets.symmetric(vertical: 12),
                    hintText: 'Что напечатает код?',
                    hintStyle: AppTypography.code(color: game.boardMuted),
                  ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: Spacing.sm),
        Text(
          'Каждый print — с новой строки. Регистр и пробелы внутри строки важны.',
          style: Theme.of(context)
              .textTheme
              .bodySmall
              ?.copyWith(color: game.textMuted),
        ),
      ],
    );
  }
}
