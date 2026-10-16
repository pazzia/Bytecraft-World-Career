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

/// The dark "board" every piece of code lives on.
class CodeBoard extends StatelessWidget {
  const CodeBoard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.symmetric(
      vertical: Spacing.lg,
      horizontal: Spacing.md,
    ),
  });

  final Widget child;
  final EdgeInsetsGeometry padding;

  @override
  Widget build(BuildContext context) {
    final colors = context.gameColors;
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 6),
      padding: padding,
      decoration: BoxDecoration(
        color: colors.board,
        borderRadius: AppRadius.boardAll,
        boxShadow: AppShadows.edge(colors.boardEdge, depth: 6),
      ),
      child: child,
    );
  }
}

/// Large, readable code with line numbers on the board. Long lines scroll
/// horizontally instead of wrapping, so indentation stays meaningful.
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

  static const double _gutterWidth = 26;
  static const double _tintAlpha = 0.32;

  @override
  Widget build(BuildContext context) {
    final colors = context.gameColors;
    final scheme = Theme.of(context).colorScheme;
    final lines = code.split('\n');
    return CodeBoard(
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
                numberColor: colors.codeLineNumber,
                background: errorLines.contains(i)
                    ? colors.error.withValues(alpha: _tintAlpha)
                    : successLines.contains(i)
                        ? colors.success.withValues(alpha: _tintAlpha)
                        : selectedLines.contains(i)
                            ? scheme.primary.withValues(alpha: _tintAlpha)
                            : null,
                selected: selectedLines.contains(i),
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
    required this.selected,
    required this.onTap,
  });

  final int number;
  final List<TextSpan> spans;
  final double gutterWidth;
  final Color numberColor;
  final Color? background;
  final bool selected;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final line = Container(
      color: background,
      constraints: BoxConstraints(
        minHeight: onTap == null ? 0 : Spacing.touchTarget,
        minWidth: MediaQuery.sizeOf(context).width - Spacing.page * 2,
      ),
      padding: const EdgeInsets.symmetric(horizontal: Spacing.lg),
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
    return Semantics(
      button: true,
      selected: selected,
      label: 'Строка $number',
      child: InkWell(onTap: onTap, child: line),
    );
  }
}
