import 'package:flutter/material.dart';

import '../../../../core/theme/app_spacing.dart';
import '../../../../core/theme/game_colors.dart';
import '../../../../shared/widgets/app_button.dart';
import '../../domain/level_result.dart';

class OutOfLivesView extends StatelessWidget {
  const OutOfLivesView({
    super.key,
    required this.lives,
    required this.onExit,
    required this.onPremium,
    this.onWatchAd,
  });

  final LivesSnapshot? lives;
  final VoidCallback onExit;
  final VoidCallback onPremium;

  /// Null when rewarded ads are disabled by feature flag.
  final VoidCallback? onWatchAd;

  String _nextLifeText() {
    final wait = lives?.nextLifeIn;
    if (wait == null) return 'Жизни восстанавливаются со временем.';
    final minutes = wait.inMinutes + 1;
    return 'Новая жизнь появится примерно через $minutes мин.';
  }

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
            Icon(Icons.heart_broken_rounded, size: 72, color: game.life),
            const SizedBox(height: Spacing.lg),
            Text(
              'Жизни закончились',
              textAlign: TextAlign.center,
              style: textTheme.headlineSmall,
            ),
            const SizedBox(height: Spacing.sm),
            Text(
              _nextLifeText(),
              textAlign: TextAlign.center,
              style: textTheme.bodyLarge?.copyWith(color: game.textMuted),
            ),
            const Spacer(),
            if (onWatchAd != null) ...[
              AppButton(
                label: 'Посмотреть рекламу: +1 жизнь',
                icon: Icons.play_circle_fill_rounded,
                onPressed: onWatchAd,
              ),
              const SizedBox(height: Spacing.sm),
            ],
            AppButton(
              label: 'Premium: бесконечные жизни',
              variant: AppButtonVariant.reward,
              onPressed: onPremium,
            ),
            const SizedBox(height: Spacing.xs),
            AppButton(
              label: 'Выйти',
              variant: AppButtonVariant.quiet,
              onPressed: onExit,
            ),
          ],
        ),
      ),
    );
  }
}
