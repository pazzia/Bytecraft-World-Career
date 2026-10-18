import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';

import '../../../../core/theme/app_spacing.dart';
import '../../../../core/theme/app_typography.dart';
import '../../../../core/theme/game_colors.dart';
import '../../../../shared/widgets/code_block.dart';
import '../../domain/topic.dart';

/// Called when a link in a topic is tapped: `target` is a topic id or
/// `g:key`; `term` is the glossary key the link was made for (if any).
typedef TopicLinkHandler = void Function(String target, String? term);

// ------------------------------------------------------------------ parsing

sealed class TopicBlock {
  const TopicBlock();
}

class ParagraphBlock extends TopicBlock {
  const ParagraphBlock(this.text);
  final String text;
}

class HeadingBlock extends TopicBlock {
  const HeadingBlock(this.text);
  final String text;
}

class ListBlock extends TopicBlock {
  const ListBlock(this.items, {required this.numbered});
  final List<String> items;
  final bool numbered;
}

class TableBlock extends TopicBlock {
  const TableBlock(this.header, this.rows);
  final List<String> header;
  final List<List<String>> rows;
}

class SyntaxBlock extends TopicBlock {
  const SyntaxBlock(this.code);
  final String code;
}

/// Topic markup -> blocks (see tool/content/topic_markup.py). Text without
/// markup is just paragraphs, so older content still renders.
abstract final class TopicMarkup {
  static final RegExp _numbered = RegExp(r'^\d+\. ');
  static final RegExp _rule = RegExp(r'^\|(\s*:?-{3,}:?\s*\|)+$');

  static List<TopicBlock> parse(String body) {
    final lines = body.split('\n');
    final blocks = <TopicBlock>[];
    var i = 0;
    while (i < lines.length) {
      final line = lines[i].trimRight();
      if (line.trim().isEmpty) {
        i++;
        continue;
      }
      if (line.trim().startsWith('```')) {
        final code = <String>[];
        i++;
        while (i < lines.length && lines[i].trim() != '```') {
          code.add(lines[i]);
          i++;
        }
        i++;
        blocks.add(SyntaxBlock(code.join('\n')));
        continue;
      }
      if (line.startsWith('## ')) {
        blocks.add(HeadingBlock(line.substring(3).trim()));
        i++;
        continue;
      }
      final isBullet = line.startsWith('- ');
      final isNumbered = _numbered.hasMatch(line);
      if (isBullet || isNumbered) {
        final items = <String>[];
        while (i < lines.length && lines[i].trim().isNotEmpty) {
          final current = lines[i].trim();
          if (current.startsWith('- ') && isBullet) {
            items.add(current.substring(2));
          } else if (isNumbered && _numbered.hasMatch(current)) {
            items.add(current.replaceFirst(_numbered, ''));
          } else if (items.isNotEmpty && !current.startsWith('## ') && !current.startsWith('|')) {
            items[items.length - 1] = '${items.last} $current';
          } else {
            break;
          }
          i++;
        }
        blocks.add(ListBlock(items, numbered: isNumbered));
        continue;
      }
      if (line.startsWith('|')) {
        final rows = <List<String>>[];
        while (i < lines.length && lines[i].trim().startsWith('|')) {
          final row = lines[i].trim();
          if (!_rule.hasMatch(row.replaceAll(' ', ''))) {
            final cells = row.substring(1, row.endsWith('|') ? row.length - 1 : row.length).split('|');
            rows.add([for (final cell in cells) cell.trim()]);
          }
          i++;
        }
        if (rows.isNotEmpty) blocks.add(TableBlock(rows.first, rows.skip(1).toList()));
        continue;
      }
      final paragraph = <String>[];
      while (i < lines.length && lines[i].trim().isNotEmpty) {
        final current = lines[i].trim();
        if (paragraph.isNotEmpty &&
            (current.startsWith('- ') ||
                current.startsWith('## ') ||
                current.startsWith('|') ||
                current.startsWith('```') ||
                _numbered.hasMatch(current))) {
          break;
        }
        paragraph.add(current);
        i++;
      }
      blocks.add(ParagraphBlock(paragraph.join(' ')));
    }
    return blocks;
  }
}

sealed class InlinePart {
  const InlinePart();
}

class TextPart extends InlinePart {
  const TextPart(this.text, {this.bold = false});
  final String text;
  final bool bold;
}

class CodePart extends InlinePart {
  const CodePart(this.code);
  final String code;
}

class LinkPart extends InlinePart {
  const LinkPart(this.target, this.label, this.term);
  final String target;

  /// The visible text (may contain `code`).
  final String label;
  final String? term;
}

abstract final class InlineMarkup {
  static final RegExp _token = RegExp(r'\[\[([^\]|]+)\|([^\]|]+)(?:\|([^\]|]+))?\]\]|`([^`]+)`|\*\*([^*]+)\*\*');

  static List<InlinePart> parse(String text) {
    final parts = <InlinePart>[];
    var last = 0;
    for (final match in _token.allMatches(text)) {
      if (match.start > last) parts.add(TextPart(text.substring(last, match.start)));
      if (match.group(1) != null) {
        parts.add(LinkPart(match.group(1)!, match.group(2)!, match.group(3)));
      } else if (match.group(4) != null) {
        parts.add(CodePart(match.group(4)!));
      } else {
        parts.add(TextPart(match.group(5)!, bold: true));
      }
      last = match.end;
    }
    if (last < text.length) parts.add(TextPart(text.substring(last)));
    return parts;
  }
}

// -------------------------------------------------------------------- views

/// Rich text of one line of topic markup: code chips, bold, links.
class MarkupText extends StatefulWidget {
  const MarkupText(this.text, {super.key, this.style, this.onLink});

  final String text;
  final TextStyle? style;
  final TopicLinkHandler? onLink;

  @override
  State<MarkupText> createState() => _MarkupTextState();
}

class _MarkupTextState extends State<MarkupText> {
  final List<TapGestureRecognizer> _recognizers = [];

  void _clearRecognizers() {
    for (final recognizer in _recognizers) {
      recognizer.dispose();
    }
    _recognizers.clear();
  }

  @override
  void dispose() {
    _clearRecognizers();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    _clearRecognizers();
    final game = context.gameColors;
    final scheme = Theme.of(context).colorScheme;
    final base = widget.style ?? Theme.of(context).textTheme.bodyLarge!;
    final codeStyle = AppTypography.code(
      color: scheme.onSurface,
      size: (base.fontSize ?? 17) * 0.88,
      weight: FontWeight.w500,
    ).copyWith(backgroundColor: game.track.withValues(alpha: 0.7), height: 1.2);

    List<InlineSpan> spansOf(String text, {TapGestureRecognizer? link}) {
      final spans = <InlineSpan>[];
      for (final part in InlineMarkup.parse(text)) {
        switch (part) {
          case TextPart(:final text, :final bold):
            spans.add(TextSpan(
              text: text,
              recognizer: link,
              style: link == null
                  ? (bold ? const TextStyle(fontWeight: FontWeight.w700) : null)
                  : TextStyle(
                      color: scheme.primary,
                      fontWeight: bold ? FontWeight.w700 : FontWeight.w600,
                      decoration: TextDecoration.underline,
                      decorationColor: scheme.primary,
                    ),
            ));
          case CodePart(:final code):
            // Thin spaces keep the code background off the neighbours.
            spans.add(TextSpan(
              text: ' $code ',
              recognizer: link,
              style: link == null
                  ? codeStyle
                  : codeStyle.copyWith(
                      color: scheme.primary,
                      decoration: TextDecoration.underline,
                      decorationColor: scheme.primary,
                      decorationThickness: 1.5,
                    ),
            ));
          case LinkPart(:final target, :final label, :final term):
            final recognizer = TapGestureRecognizer()
              ..onTap = () => widget.onLink?.call(target, term);
            _recognizers.add(recognizer);
            spans.addAll(spansOf(label, link: widget.onLink == null ? null : recognizer));
        }
      }
      return spans;
    }

    return Semantics(
      container: true,
      child: Text.rich(TextSpan(style: base, children: spansOf(widget.text))),
    );
  }
}

/// The body of a topic: sections, lists, tables, syntax boards.
class TopicBody extends StatelessWidget {
  const TopicBody({super.key, required this.body, this.onLink});

  final String body;
  final TopicLinkHandler? onLink;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    final paragraph = textTheme.bodyLarge!.copyWith(height: 1.5);
    final children = <Widget>[];
    for (final block in TopicMarkup.parse(body)) {
      switch (block) {
        case HeadingBlock(:final text):
          children.add(Padding(
            padding: const EdgeInsets.only(top: 28, bottom: Spacing.sm),
            child: MarkupText(text, style: textTheme.titleMedium, onLink: onLink),
          ));
        case ParagraphBlock(:final text):
          children.add(Padding(
            padding: const EdgeInsets.only(top: Spacing.md),
            child: MarkupText(text, style: paragraph, onLink: onLink),
          ));
        case ListBlock(:final items, :final numbered):
          children.add(Padding(
            padding: const EdgeInsets.only(top: Spacing.md),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                for (var i = 0; i < items.length; i++)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 6),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        SizedBox(
                          width: numbered ? 28 : 18,
                          child: numbered
                              ? Text('${i + 1}.', style: AppTypography.code(color: game.textMuted, size: 15).copyWith(height: 1.7))
                              : Padding(
                                  padding: const EdgeInsets.only(top: 10, right: 6),
                                  child: Container(
                                    width: 6,
                                    height: 6,
                                    decoration: BoxDecoration(color: game.textMuted, shape: BoxShape.circle),
                                  ),
                                ),
                        ),
                        Expanded(child: MarkupText(items[i], style: paragraph, onLink: onLink)),
                      ],
                    ),
                  ),
              ],
            ),
          ));
        case TableBlock(:final header, :final rows):
          children.add(Padding(
            padding: const EdgeInsets.only(top: Spacing.md),
            child: _MarkupTable(header: header, rows: rows, onLink: onLink),
          ));
        case SyntaxBlock(:final code):
          children.add(Padding(
            padding: const EdgeInsets.only(top: Spacing.md),
            child: SyntaxBoard(code: code),
          ));
      }
    }
    return Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: children);
  }
}

class _MarkupTable extends StatelessWidget {
  const _MarkupTable({required this.header, required this.rows, this.onLink});

  final List<String> header;
  final List<List<String>> rows;
  final TopicLinkHandler? onLink;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    final cell = textTheme.bodyMedium!.copyWith(height: 1.35);
    final head = textTheme.labelMedium!.copyWith(color: game.textMuted);
    Widget pad(Widget child) => Padding(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
          child: child,
        );
    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        borderRadius: AppRadius.mdAll,
        border: Border.all(color: game.track),
      ),
      clipBehavior: Clip.antiAlias,
      child: Table(
        border: TableBorder(horizontalInside: BorderSide(color: game.track)),
        defaultVerticalAlignment: TableCellVerticalAlignment.middle,
        children: [
          TableRow(children: [for (final h in header) pad(MarkupText(h, style: head, onLink: onLink))]),
          for (final row in rows)
            TableRow(children: [
              for (var c = 0; c < header.length; c++)
                pad(MarkupText(c < row.length ? row[c] : '', style: cell, onLink: onLink)),
            ]),
        ],
      ),
    );
  }
}

/// General form of a construct: Python is highlighted, Cyrillic words are
/// the places the reader fills in (shown muted and underlined).
class SyntaxBoard extends StatelessWidget {
  const SyntaxBoard({super.key, required this.code});

  final String code;

  static final RegExp _placeholder = RegExp(r'[А-Яа-яЁё][А-Яа-яЁё0-9_]*');

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    final scheme = Theme.of(context).colorScheme;
    final style = AppTypography.code(color: scheme.onSurface, size: 15).copyWith(height: 1.45);
    final placeholder = TextStyle(
      color: game.textMuted,
      fontWeight: FontWeight.w400,
      decoration: TextDecoration.underline,
      decorationStyle: TextDecorationStyle.dotted,
      decorationColor: game.textMuted,
    );
    List<InlineSpan> line(String text) {
      final spans = <InlineSpan>[];
      var last = 0;
      for (final match in _placeholder.allMatches(text)) {
        if (match.start > last) spans.add(TextSpan(text: text.substring(last, match.start)));
        spans.add(TextSpan(text: match.group(0), style: placeholder));
        last = match.end;
      }
      if (last < text.length) spans.add(TextSpan(text: text.substring(last)));
      return spans;
    }

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: game.primaryTint,
        borderRadius: AppRadius.mdAll,
      ),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Text.rich(
          TextSpan(
            style: style,
            children: [
              for (final (index, text) in code.split('\n').indexed) ...[
                if (index > 0) const TextSpan(text: '\n'),
                ...line(text),
              ],
            ],
          ),
          softWrap: false,
        ),
      ),
    );
  }
}

/// A worked example: its code and the real output on one board, titled by
/// the example's note. No line numbers: here code is read, not pointed at.
class ExampleBoard extends StatelessWidget {
  const ExampleBoard({super.key, required this.code, required this.output});

  final String code;
  final String output;

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    final out = output.endsWith('\n') ? output.substring(0, output.length - 1) : output;
    return CodeBoard(
      padding: EdgeInsets.zero,
      onExpand: () => showCodeViewer(context, code),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final lines = code.split('\n');
          final fitted = CodeFit.forWidth(constraints.maxWidth - 2 * Spacing.lg, CodeFit.columnsOf(lines));
          final fit = CodeFit.fixed(fitted.fontSize > 15 ? 15 : fitted.fontSize);
          return Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(Spacing.lg, Spacing.lg, 40, Spacing.md),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    for (final line in lines)
                      Builder(builder: (context) {
                        final (indent, rest) = splitIndent(line);
                        return CodeLineText(
                          indent: indent,
                          spans: highlightPython(rest, game),
                          fit: fit,
                          color: game.codeText,
                        );
                      }),
                  ],
                ),
              ),
              Container(
                color: Colors.black.withValues(alpha: 0.18),
                padding: const EdgeInsets.fromLTRB(Spacing.lg, Spacing.sm, Spacing.lg, Spacing.lg),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Вывод', style: AppTypography.code(color: game.codeLineNumber, size: 12, weight: FontWeight.w700)),
                    const SizedBox(height: 2),
                    Text(
                      out.isEmpty ? '(ничего не печатает)' : out,
                      style: AppTypography.code(color: game.codeText, size: fit.fontSize).copyWith(height: 1.45),
                    ),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

/// «Так нельзя / так можно»: two code strips with the explanation above.
class PitfallView extends StatelessWidget {
  const PitfallView({super.key, required this.pitfall, this.onLink});

  final TopicPitfall pitfall;
  final TopicLinkHandler? onLink;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    Widget strip(String label, String code, Color color, Color tint) => Container(
          decoration: BoxDecoration(
            color: tint,
            border: Border(left: BorderSide(color: color, width: 3)),
          ),
          padding: const EdgeInsets.fromLTRB(Spacing.md, Spacing.sm, Spacing.md, Spacing.sm),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(label, style: textTheme.labelSmall?.copyWith(color: color)),
              const SizedBox(height: 2),
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Text(
                  code,
                  softWrap: false,
                  style: AppTypography.code(color: Theme.of(context).colorScheme.onSurface, size: 15)
                      .copyWith(height: 1.4),
                ),
              ),
            ],
          ),
        );
    return Padding(
      padding: const EdgeInsets.only(bottom: Spacing.lg),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          MarkupText(pitfall.why, style: textTheme.bodyMedium!.copyWith(height: 1.45), onLink: onLink),
          if (pitfall.hasCode) ...[
            const SizedBox(height: Spacing.sm),
            strip('Так нельзя', pitfall.bad!, game.error, game.errorTint),
            const SizedBox(height: Spacing.xs),
            strip('Так можно', pitfall.good!, game.success, game.successTint),
          ],
        ],
      ),
    );
  }
}
