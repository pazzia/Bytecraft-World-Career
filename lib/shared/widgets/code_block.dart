import 'package:flutter/material.dart';

import '../../core/theme/app_spacing.dart';
import '../../core/theme/app_typography.dart';
import '../../core/theme/game_colors.dart';
import '../utils/python_highlighter.dart';

/// Builds highlighted spans for one line of Python.
List<TextSpan> highlightPython(String line, GameColors colors) =>
    PythonHighlighter.tokenize(line).map((token) {
      final color = switch (token.kind) {
        CodeTokenKind.keyword => colors.codeKeyword,
        CodeTokenKind.builtin => colors.codeBuiltin,
        CodeTokenKind.string => colors.codeString,
        CodeTokenKind.number => colors.codeNumber,
        CodeTokenKind.comment => colors.codeComment,
        CodeTokenKind.plain => colors.codeText,
      };
      return TextSpan(text: token.text, style: TextStyle(color: color));
    }).toList();

/// Large, readable code with line numbers. Long lines scroll horizontally
/// instead of wrapping, so indentation stays meaningful.
///
/// With [onLineTap] lines become tappable (bug finder).
class CodeBlock extends StatelessWidget {
  const CodeBlock({
    super.key,
    required this.code,
    this.onLineTap,
    this.selectedLines = const <int>{},
    this.errorLines = const <int>{},
    this.successLines = const <int>{},
  });

  final String code;
  final ValueChanged<int>? onLineTap;
  final Set<int> selectedLines;
  final Set<int> errorLines;
  final Set<int> successLines;

  static const double _selectionAlpha = 0.28;
  static const double _gutterWidth = 28;

  @override
  Widget build(BuildContext context) {
    final colors = context.gameColors;
    final scheme = Theme.of(context).colorScheme;
    final lines = code.split('\n');
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: colors.codeBackground,
        borderRadius: AppRadius.lgAll,
      ),
      padding: const EdgeInsets.symmetric(vertical: Spacing.md),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            for (var i = 0; i < lines.length; i++)
              _CodeLine(
                number: i + 1,
                spans: highlightPython(lines[i], colors),
                gutterWidth: _gutterWidth,
                numberColor: colors.codeComment,
                background: errorLines.contains(i)
                    ? colors.error.withValues(alpha: _selectionAlpha)
                    : successLines.contains(i)
                        ? colors.success.withValues(alpha: _selectionAlpha)
                        : selectedLines.contains(i)
                            ? scheme.primary.withValues(alpha: _selectionAlpha)
                            : null,
                onTap: onLineTap == null ? null : () => onLineTap!(i),
              ),
          ],
        ),
      ),
    );
  }
}

class _CodeLine extends StatelessWidget {
  const _CodeLine({
    required this.number,
    required this.spans,
    required this.gutterWidth,
    required this.numberColor,
    required this.background,
    required this.onTap,
  });

  final int number;
  final List<TextSpan> spans;
  final double gutterWidth;
  final Color numberColor;
  final Color? background;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final line = Container(
      color: background,
      constraints: BoxConstraints(
        minHeight: onTap == null ? 0 : Spacing.touchTarget - Spacing.sm,
      ),
      padding: const EdgeInsets.symmetric(horizontal: Spacing.md),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          SizedBox(
            width: gutterWidth,
            child: Text(
              '$number',
              style: AppTypography.code(color: numberColor, size: 13),
            ),
          ),
          Text.rich(
            TextSpan(children: spans),
            style: AppTypography.code(),
            softWrap: false,
          ),
        ],
      ),
    );
    if (onTap == null) return line;
    return InkWell(onTap: onTap, child: line);
  }
}
