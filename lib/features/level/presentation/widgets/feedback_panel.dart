import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../../core/theme/app_spacing.dart';
import '../../../../core/theme/game_colors.dart';
import '../../../../shared/widgets/app_button.dart';
import '../../../../shared/widgets/output_board.dart';
import '../../../../shared/widgets/stat_badges.dart';

/// Bottom sheet with instant feedback after checking an answer.
class FeedbackPanel extends StatefulWidget {
  const FeedbackPanel({
    super.key,
    required this.isCorrect,
    required this.message,
    required this.buttonLabel,
    required this.onPressed,
    this.livesLeft,
    this.programResult,
    this.hint,
    this.onDetails,
  });

  final bool isCorrect;

  /// Short analysis of the mistake, or the explanation after a right answer.
  final String? message;
  final String buttonLabel;
  final VoidCallback onPressed;
  final int? livesLeft;

  /// What the program does with the player's version (fill-code).
  final String? programResult;

  /// Hint shown under a mistake.
  final String? hint;

  /// Opens the detailed review ("Разбор").
  final VoidCallback? onDetails;

  static final RegExp _errorResult = RegExp(r'^\w*(Error|Exception)\b');

  @override
  State<FeedbackPanel> createState() => _FeedbackPanelState();
}

class _FeedbackPanelState extends State<FeedbackPanel> {
  @override
  void initState() {
    super.initState();
    if (widget.isCorrect) {
      HapticFeedback.lightImpact();
    } else {
      HapticFeedback.heavyImpact();
    }
  }

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    final textTheme = Theme.of(context).textTheme;
    final accent = widget.isCorrect ? game.success : game.error;
    final accentText = widget.isCorrect ? game.successEdge : game.errorEdge;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final titleColor = isDark
        ? (widget.isCorrect ? game.successBright : game.errorBright)
        : accentText;
    final lives = widget.livesLeft;
    return Semantics(
      liveRegion: true,
      container: true,
      child: Container(
        width: double.infinity,
        decoration: BoxDecoration(
          color: widget.isCorrect ? game.successTint : game.errorTint,
          borderRadius: const BorderRadius.vertical(
            top: Radius.circular(AppRadius.sheet),
          ),
        ),
        padding: const EdgeInsets.fromLTRB(
          Spacing.page,
          Spacing.xxl,
          Spacing.page,
          Spacing.lg,
        ),
        child: SafeArea(
          top: false,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    widget.isCorrect
                        ? Icons.check_circle_rounded
                        : Icons.cancel_rounded,
                    color: accent,
                    size: 32,
                  ),
                  const SizedBox(width: Spacing.sm),
                  Expanded(
                    child: Text(
                      widget.isCorrect ? 'Верно!' : 'Не то',
                      style: textTheme.headlineSmall?.copyWith(color: titleColor),
                    ),
                  ),
                  if (!widget.isCorrect && lives != null)
                    Text(
                      'осталось $lives ${plural(lives, 'жизнь', 'жизни', 'жизней')}',
                      style: textTheme.titleSmall?.copyWith(color: titleColor),
                    ),
                ],
              ),
              if (widget.message != null && widget.message!.isNotEmpty) ...[
                const SizedBox(height: Spacing.sm),
                Text(widget.message!, style: textTheme.bodyLarge),
              ],
              if (widget.programResult != null) ...[
                const SizedBox(height: Spacing.sm),
                OutputBoard(
                  label: 'С вашим вариантом программа выдаст',
                  output: widget.programResult!,
                  isError: FeedbackPanel._errorResult.hasMatch(widget.programResult!),
                ),
              ],
              if (widget.hint != null && widget.hint!.isNotEmpty) ...[
                const SizedBox(height: Spacing.sm),
                Text(
                  'Подсказка: ${widget.hint}',
                  style: textTheme.bodyMedium?.copyWith(color: game.textMuted),
                ),
              ],
              const SizedBox(height: Spacing.lg),
              Row(
                children: [
                  if (widget.onDetails != null) ...[
                    Expanded(
                      flex: 2,
                      child: AppButton(
                        key: const ValueKey('review_button'),
                        label: 'Разбор',
                        variant: AppButtonVariant.secondary,
                        onPressed: widget.onDetails,
                      ),
                    ),
                    const SizedBox(width: Spacing.md),
                  ],
                  Expanded(
                    flex: 3,
                    child: AppButton(
                      label: widget.buttonLabel,
                      variant: widget.isCorrect
                          ? AppButtonVariant.success
                          : AppButtonVariant.danger,
                      onPressed: widget.onPressed,
                    ),
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
