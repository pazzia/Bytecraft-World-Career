import 'package:flutter/material.dart';

import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/game_colors.dart';
import '../../../shared/widgets/app_button.dart';

class TimeUpView extends StatelessWidget {
  const TimeUpView({
    super.key,
    required this.onRestart,
    required this.onExit,
  });

  final VoidCallback onRestart;
  final VoidCallback onExit;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(Spacing.page),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Spacer(),
            Icon(Icons.timer_off_outlined, size: 72, color: game.streak),
            const SizedBox(height: Spacing.lg),
            Text(
              'Время вышло',
              textAlign: TextAlign.center,
              style: textTheme.headlineSmall,
            ),
            const SizedBox(height: Spacing.sm),
            Text(
              'Забег не засчитан. Опыт за уже пройденные уровни остаётся у вас.',
              textAlign: TextAlign.center,
              style: textTheme.bodyLarge?.copyWith(color: game.textMuted),
            ),
            const Spacer(),
            AppButton(label: 'Начать заново', onPressed: onRestart),
            const SizedBox(height: Spacing.xs),
            AppButton(
              label: 'К карте',
              variant: AppButtonVariant.quiet,
              onPressed: onExit,
            ),
          ],
        ),
      ),
    );
  }
}
