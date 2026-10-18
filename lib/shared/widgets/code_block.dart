import 'dart:math' as math;

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

/// How big code can be so that whole lines fit the board's width.
///
/// The font shrinks from [maxSize] down to [minSize]; lines that still
/// don't fit wrap, and the continuation is indented like the line itself
/// (see [CodeLineText]). Nothing ever scrolls sideways.
class CodeFit {
  const CodeFit._(this.fontSize);

  static const double maxSize = 17;
  static const double minSize = 13;

  /// Width of the line-number column.
  static const double gutterWidth = 28;

  /// A fixed size (for single lines in cards).
  const CodeFit.fixed(this.fontSize);

  final double fontSize;

  double get charWidth => fontSize * AppTypography.codeAdvance;

  /// [columns] — the longest line, in characters.
  factory CodeFit.forWidth(double width, int columns) {
    if (columns <= 0 || !width.isFinite) return const CodeFit._(maxSize);
    final fitting = width / (columns * AppTypography.codeAdvance);
    return CodeFit._(fitting.clamp(minSize, maxSize).floorToDouble());
  }

  static int columnsOf(Iterable<String> lines) =>
      lines.fold(0, (longest, line) => math.max(longest, line.length));
}

/// Leading spaces of a line and the rest.
(int, String) splitIndent(String line) {
  final rest = line.trimLeft();
  return (line.length - rest.length, rest);
}

/// One line of code that wraps with a hanging indent: the continuation
/// starts under the first character after the indentation.
class CodeLineText extends StatelessWidget {
  const CodeLineText({
    super.key,
    required this.indent,
    required this.spans,
    required this.fit,
    required this.color,
  });

  final int indent;
  final List<InlineSpan> spans;
  final CodeFit fit;
  final Color color;

  @override
  Widget build(BuildContext context) => Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(width: indent * fit.charWidth),
          Expanded(
            child: Text.rich(
              TextSpan(children: spans),
              style: AppTypography.code(color: color, size: fit.fontSize),
            ),
          ),
        ],
      );
}

/// The dark "board" every piece of code lives on.
class CodeBoard extends StatelessWidget {
  const CodeBoard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.symmetric(
      vertical: Spacing.lg,
      horizontal: Spacing.md,
    ),
    this.onExpand,
  });

  final Widget child;
  final EdgeInsetsGeometry padding;

  /// Shows an "open full screen" button in the corner.
  final VoidCallback? onExpand;

  @override
  Widget build(BuildContext context) {
    final colors = context.gameColors;
    final board = Container(
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
    if (onExpand == null) return board;
    return Stack(
      children: [
        board,
        Positioned(
          top: 2,
          right: 2,
          child: IconButton(
            key: const ValueKey('code_expand'),
            tooltip: 'Открыть код на весь экран',
            iconSize: 20,
            color: colors.codeLineNumber,
            icon: const Icon(Icons.open_in_full_rounded),
            onPressed: onExpand,
          ),
        ),
      ],
    );
  }
}

/// Readable code with line numbers on the board. The font is fitted to the
/// width so whole lines are visible; very long lines wrap with a hanging
/// indent instead of scrolling sideways.
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
    this.expandable = false,
  });

  final String code;
  final ValueChanged<int>? onLineTap;
  final Set<int> selectedLines;
  final Set<int> errorLines;
  final Set<int> successLines;

  /// Adds a button that opens the code full screen (pinch to zoom).
  final bool expandable;

  static const double _tintAlpha = 0.32;
  static const double _sidePadding = Spacing.md;

  @override
  Widget build(BuildContext context) {
    final colors = context.gameColors;
    final scheme = Theme.of(context).colorScheme;
    final lines = code.split('\n');
    return CodeBoard(
      padding: const EdgeInsets.symmetric(vertical: Spacing.md),
      onExpand: expandable ? () => showCodeViewer(context, code) : null,
      child: LayoutBuilder(
        builder: (context, constraints) {
          final fit = CodeFit.forWidth(
            constraints.maxWidth - CodeFit.gutterWidth - _sidePadding * 2,
            CodeFit.columnsOf(lines),
          );
          return Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              for (var i = 0; i < lines.length; i++)
                _CodeLine(
                  number: i + 1,
                  line: lines[i],
                  fit: fit,
                  colors: colors,
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
          );
        },
      ),
    );
  }
}

class _CodeLine extends StatelessWidget {
  const _CodeLine({
    required this.number,
    required this.line,
    required this.fit,
    required this.colors,
    required this.background,
    required this.selected,
    required this.onTap,
  });

  final int number;
  final String line;
  final CodeFit fit;
  final GameColors colors;
  final Color? background;
  final bool selected;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final (indent, rest) = splitIndent(line);
    final row = Container(
      color: background,
      constraints: BoxConstraints(
        minHeight: onTap == null ? 0 : Spacing.touchTarget,
      ),
      padding: const EdgeInsets.symmetric(horizontal: CodeBlock._sidePadding),
      alignment: Alignment.centerLeft,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: CodeFit.gutterWidth,
            child: Text(
              '$number',
              style: AppTypography.code(
                color: colors.codeLineNumber,
                size: math.min(13, fit.fontSize),
              ).copyWith(height: fit.fontSize * AppTypography.codeLineHeight /
                  math.min(13, fit.fontSize)),
            ),
          ),
          Expanded(
            child: CodeLineText(
              indent: indent,
              spans: highlightPython(rest, colors),
              fit: fit,
              color: colors.codeText,
            ),
          ),
        ],
      ),
    );
    if (onTap == null) return row;
    return Semantics(
      button: true,
      selected: selected,
      label: 'Строка $number',
      child: InkWell(onTap: onTap, child: row),
    );
  }
}

/// Full-screen code: comfortable size, no wrapping, scroll both ways and
/// pinch to zoom. For long programs on a small phone.
Future<void> showCodeViewer(BuildContext context, String code) =>
    Navigator.of(context).push(
      MaterialPageRoute<void>(
        fullscreenDialog: true,
        builder: (context) => _CodeViewerScreen(code: code),
      ),
    );

class _CodeViewerScreen extends StatelessWidget {
  const _CodeViewerScreen({required this.code});

  final String code;

  @override
  Widget build(BuildContext context) {
    final colors = context.gameColors;
    final lines = code.split('\n');
    final numberStyle = AppTypography.code(color: colors.codeLineNumber, size: 13)
        .copyWith(height: 16 * AppTypography.codeLineHeight / 13);
    return Scaffold(
      backgroundColor: colors.board,
      appBar: AppBar(
        backgroundColor: colors.board,
        foregroundColor: colors.codeText,
        title: const Text('Код'),
      ),
      body: InteractiveViewer(
        constrained: false,
        minScale: 0.5,
        maxScale: 3,
        boundaryMargin: const EdgeInsets.all(Spacing.xxl),
        child: Padding(
          padding: const EdgeInsets.all(Spacing.lg),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              for (var i = 0; i < lines.length; i++)
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SizedBox(
                      width: CodeFit.gutterWidth + 4,
                      child: Text('${i + 1}', style: numberStyle),
                    ),
                    Text.rich(
                      TextSpan(children: highlightPython(lines[i], colors)),
                      style: AppTypography.code(color: colors.codeText, size: 16),
                      softWrap: false,
                    ),
                  ],
                ),
            ],
          ),
        ),
      ),
    );
  }
}
