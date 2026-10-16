import 'package:flutter/material.dart';

import '../../../../core/theme/app_spacing.dart';
import '../../../../core/theme/app_typography.dart';
import '../../../../core/theme/game_colors.dart';
import '../../../../shared/widgets/code_block.dart';
import '../../../courses/domain/fill_code_template.dart';
import '../../../courses/domain/level_definition.dart';
import '../../../courses/domain/level_payload.dart';

/// A few lines of a level's code for previews (home card).
///
/// Never reveals an answer: blanks stay empty slots and ordering puzzles
/// show no code at all.
class LevelCodePreview extends StatelessWidget {
  const LevelCodePreview({super.key, required this.level, this.maxLines = 3});

  final LevelDefinition level;
  final int maxLines;

  /// Whether this level has something safe to preview.
  static bool hasPreview(LevelDefinition level) => switch (level.payload) {
        FillCodePayload() => true,
        CodeOrderingPayload() => false,
        _ => level.code != null && level.code!.isNotEmpty,
      };

  @override
  Widget build(BuildContext context) {
    final colors = context.gameColors;
    final style = AppTypography.code(color: colors.codeText);
    final payload = level.payload;
    final List<Widget> lines;
    if (payload is FillCodePayload) {
      lines = [
        for (final line in FillCodeTemplate.lines(payload.template).take(maxLines))
          Text.rich(
            TextSpan(
              children: [
                for (final segment in line)
                  switch (segment) {
                    TextSegment(:final text) =>
                      TextSpan(children: highlightPython(text, colors)),
                    BlankSegment() => WidgetSpan(
                        alignment: PlaceholderAlignment.middle,
                        child: Container(
                          width: 44,
                          height: 24,
                          margin: const EdgeInsets.symmetric(horizontal: 2),
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(7),
                            border: Border.all(color: colors.codeLineNumber, width: 2),
                          ),
                        ),
                      ),
                  },
              ],
            ),
            style: style,
            softWrap: false,
            overflow: TextOverflow.fade,
          ),
      ];
    } else {
      lines = [
        for (final line in level.codeLines.take(maxLines))
          Text.rich(
            TextSpan(children: highlightPython(line, colors)),
            style: style,
            softWrap: false,
            overflow: TextOverflow.fade,
          ),
      ];
    }
    return ExcludeSemantics(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          for (final line in lines)
            Padding(
              padding: const EdgeInsets.only(bottom: Spacing.xxs),
              child: line,
            ),
        ],
      ),
    );
  }
}
