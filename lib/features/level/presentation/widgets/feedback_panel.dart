import 'package:flutter/material.dart';

import '../../../../core/theme/app_spacing.dart';
import '../../../../core/theme/game_colors.dart';
import '../../../../shared/widgets/app_button.dart';

/// Bottom panel with instant feedback after checking an answer.
class FeedbackPanel extends StatelessWidget {
  const FeedbackPanel({
    super.key,
    required this.isCorrect,
    required this.message,
    required this.buttonLabel,
    required this.onPressed,
    this.livesLeft,
  });

  final bool isCorrect;
  final String? message;
  final String buttonLabel;
  final VoidCallback onPressed;
  final int? livesLeft;

  static const double _backgroundAlpha = 0.14;

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    final color = isCorrect ? game.success : game.error;
    final textTheme = Theme.of(context).textTheme;
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: Color.alphaBlend(
          color.withValues(alpha: _backgroundAlpha),
          Theme.of(context).colorScheme.surface,
        ),
        borderRadius: const BorderRadius.vertical(
          top: Radius.circular(AppRadius.xl),
        ),
      ),
      padding: const EdgeInsets.fromLTRB(
        Spacing.page,
        Spacing.xl,
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
                  isCorrect ? Icons.check_circle_rounded : Icons.cancel_rounded,
                  color: color,
                  size: 32,
                ),
                const SizedBox(width: Spacing.sm),
                Expanded(
                  child: Text(
                    isCorrect ? 'Верно!' : 'Не совсем',
                    style: textTheme.headlineSmall?.copyWith(color: color),
                  ),
                ),
                if (!isCorrect && livesLeft != null)
                  Text(
                    '❤️ $livesLeft',
                    style: textTheme.titleMedium?.copyWith(color: game.life),
                  ),
              ],
            ),
            if (message != null && message!.isNotEmpty) ...[
              const SizedBox(height: Spacing.sm),
              Text(message!, style: textTheme.bodyLarge),
            ],
            const SizedBox(height: Spacing.lg),
            AppButton(
              label: buttonLabel,
              variant:
                  isCorrect ? AppButtonVariant.success : AppButtonVariant.danger,
              onPressed: onPressed,
            ),
          ],
        ),
      ),
    );
  }
}
