import 'package:flutter/material.dart';

import '../../core/theme/app_spacing.dart';
import '../../core/theme/app_typography.dart';
import '../../core/theme/game_colors.dart';

/// What a program printed: a terminal-like strip under a code block.
class OutputBoard extends StatelessWidget {
  const OutputBoard({
    super.key,
    required this.output,
    this.label = 'Вывод',
    this.isError = false,
  });

  final String output;
  final String label;
  final bool isError;

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    final text = output.endsWith('\n')
        ? output.substring(0, output.length - 1)
        : output;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(Spacing.md),
      decoration: BoxDecoration(
        color: game.board,
        borderRadius: AppRadius.lgAll,
        border: Border.all(
          color: isError ? game.error : game.boardMuted,
          width: 1.5,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: AppTypography.code(
              color: isError ? game.errorBright : game.codeLineNumber,
              size: 12,
              weight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: Spacing.xs),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Text(
              text.isEmpty ? '(ничего не выводит)' : text,
              softWrap: false,
              style: AppTypography.code(
                color: isError ? game.errorBright : game.codeText,
                size: 15,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
