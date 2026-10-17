import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';
import '../../../core/theme/game_colors.dart';

/// Keeps Python indentation while typing on a phone: Enter repeats the
/// previous line's indent (one level deeper after a colon).
class PythonIndentFormatter extends TextInputFormatter {
  const PythonIndentFormatter();

  static const String indentUnit = '    ';

  @override
  TextEditingValue formatEditUpdate(
    TextEditingValue oldValue,
    TextEditingValue newValue,
  ) {
    final oldSelection = oldValue.selection;
    final newSelection = newValue.selection;
    if (!oldSelection.isValid ||
        !newSelection.isCollapsed ||
        newValue.text.length != oldValue.text.length + 1 -
            (oldSelection.end - oldSelection.start)) {
      return newValue;
    }
    final cursor = newSelection.baseOffset;
    if (cursor <= 0 || newValue.text[cursor - 1] != '\n') return newValue;
    final before = newValue.text.substring(0, cursor - 1);
    final lineStart = before.lastIndexOf('\n') + 1;
    final line = before.substring(lineStart);
    final indent = RegExp(r'^[ ]*').stringMatch(line) ?? '';
    final extra = line.trimRight().endsWith(':') ? indentUnit : '';
    final insert = indent + extra;
    if (insert.isEmpty) return newValue;
    final text = newValue.text.substring(0, cursor) +
        insert +
        newValue.text.substring(cursor);
    return TextEditingValue(
      text: text,
      selection: TextSelection.collapsed(offset: cursor + insert.length),
    );
  }
}

/// Multi-line Python editor on the dark board, with a row of symbol keys
/// that are awkward to reach on a phone keyboard.
class CodeEditor extends StatelessWidget {
  const CodeEditor({
    super.key,
    required this.controller,
    this.focusNode,
    this.onChanged,
    this.minLines = 10,
  });

  final TextEditingController controller;
  final FocusNode? focusNode;
  final ValueChanged<String>? onChanged;
  final int minLines;

  static const List<(String, String)> _keys = [
    ('⇥', PythonIndentFormatter.indentUnit),
    (':', ':'),
    ('(', '('),
    (')', ')'),
    ('[', '['),
    (']', ']'),
    ('{', '{'),
    ('}', '}'),
    ('"', '"'),
    ("'", "'"),
    ('=', '='),
    ('_', '_'),
    ('#', '#'),
    ('<', '<'),
    ('>', '>'),
    ('+', '+'),
    ('-', '-'),
    ('*', '*'),
    ('/', '/'),
    ('%', '%'),
    (',', ','),
    ('.', '.'),
  ];

  void _insert(String text) {
    final value = controller.value;
    final selection = value.selection.isValid
        ? value.selection
        : TextSelection.collapsed(offset: value.text.length);
    final updated = value.text.replaceRange(selection.start, selection.end, text);
    controller.value = TextEditingValue(
      text: updated,
      selection: TextSelection.collapsed(offset: selection.start + text.length),
    );
    onChanged?.call(updated);
  }

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Container(
          decoration: BoxDecoration(
            color: game.board,
            borderRadius: AppRadius.lgAll,
          ),
          padding: const EdgeInsets.symmetric(
            horizontal: Spacing.md,
            vertical: Spacing.xs,
          ),
          child: TextField(
            key: const ValueKey('code_editor'),
            controller: controller,
            focusNode: focusNode,
            onChanged: onChanged,
            minLines: minLines,
            maxLines: null,
            keyboardType: TextInputType.multiline,
            textCapitalization: TextCapitalization.none,
            autocorrect: false,
            enableSuggestions: false,
            smartQuotesType: SmartQuotesType.disabled,
            smartDashesType: SmartDashesType.disabled,
            enableIMEPersonalizedLearning: false,
            inputFormatters: const [PythonIndentFormatter()],
            cursorColor: game.codeText,
            style: AppTypography.code(color: game.codeText, size: 15),
            decoration: const InputDecoration(
              border: InputBorder.none,
              enabledBorder: InputBorder.none,
              focusedBorder: InputBorder.none,
              filled: false,
              isDense: true,
              contentPadding: EdgeInsets.symmetric(vertical: Spacing.md),
            ),
          ),
        ),
        const SizedBox(height: Spacing.sm),
        SizedBox(
          height: 40,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: _keys.length,
            separatorBuilder: (context, index) => const SizedBox(width: 6),
            itemBuilder: (context, index) {
              final (label, text) = _keys[index];
              return Material(
                color: game.keyFace,
                shape: RoundedRectangleBorder(
                  borderRadius: AppRadius.smAll,
                  side: BorderSide(color: game.keyBorder),
                ),
                child: InkWell(
                  borderRadius: AppRadius.smAll,
                  onTap: () => _insert(text),
                  child: SizedBox(
                    width: 40,
                    child: Center(
                      child: Text(
                        label,
                        style: AppTypography.code(size: 17, weight: FontWeight.w700),
                      ),
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}
