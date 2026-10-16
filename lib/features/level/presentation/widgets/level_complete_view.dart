import 'package:flutter/material.dart';

import '../../../../core/theme/app_spacing.dart';
import '../../../../core/theme/game_colors.dart';
import '../../../../shared/widgets/app_button.dart';
import '../../../../shared/widgets/app_card.dart';
import '../../../../shared/widgets/app_progress_bar.dart';
import '../../../../shared/widgets/stat_badges.dart';
import '../../../timed_run/presentation/countdown.dart';
import '../../domain/level_result.dart';

/// Rewards screen after a level: stars, XP, coins, streak, course progress.
class LevelCompleteView extends StatelessWidget {
  const LevelCompleteView({
    super.key,
    required this.result,
    required this.onContinue,
    required this.onBackToMap,
  });

  final LevelResult result;

  /// Null when there is no next level (course finished).
  final VoidCallback? onContinue;
  final VoidCallback onBackToMap;

  static const double _starSize = 64;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    final percent = (result.courseProgress * 100).round();
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(Spacing.page),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Expanded(
              child: ListView(
                children: [
                  const SizedBox(height: Spacing.xl),
                  Text(
                    result.isPerfect ? 'Идеально! 💎' : 'Уровень пройден! 🎉',
                    textAlign: TextAlign.center,
                    style: textTheme.headlineMedium,
                  ),
                  const SizedBox(height: Spacing.xl),
                  Center(
                    child: _AnimatedStars(
                      stars: result.stars,
                      size: _starSize,
                    ),
                  ),
                  const SizedBox(height: Spacing.xl),
                  Wrap(
                    alignment: WrapAlignment.center,
                    spacing: Spacing.sm,
                    runSpacing: Spacing.sm,
                    children: [
                      XpBadge(xp: result.xpEarned),
                      if (result.coinsEarned > 0)
                        CoinBadge(coins: result.coinsEarned),
                      StreakBadge(days: result.streak),
                    ],
                  ),
                  if (result.streakExtended) ...[
                    const SizedBox(height: Spacing.md),
                    Text(
                      'Серия продлена: ${result.streak} 🔥',
                      textAlign: TextAlign.center,
                      style: textTheme.titleMedium?.copyWith(color: game.streak),
                    ),
                  ],
                  if (result.leveledUp) ...[
                    const SizedBox(height: Spacing.md),
                    Text(
                      'Новый уровень аккаунта: ${result.accountLevelAfter} ⬆️',
                      textAlign: TextAlign.center,
                      style: textTheme.titleMedium?.copyWith(color: game.xp),
                    ),
                  ],
                  if (result.dailyChallengeCompleted) ...[
                    const SizedBox(height: Spacing.md),
                    Text(
                      'Задача дня выполнена! 🏆',
                      textAlign: TextAlign.center,
                      style: textTheme.titleMedium?.copyWith(color: game.coin),
                    ),
                  ],
                  const SizedBox(height: Spacing.xl),
                  if (result.timedRun != null)
                    _TimedSummary(run: result.timedRun!)
                  else
                  AppCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Прогресс курса: $percent%',
                          style: textTheme.titleMedium,
                        ),
                        const SizedBox(height: Spacing.sm),
                        AppProgressBar(value: result.courseProgress),
                        const SizedBox(height: Spacing.xs),
                        Text(
                          '${result.completedInCourse} из '
                          '${result.playableInCourse} уровней',
                        ),
                      ],
                    ),
                  ),
                  for (final achievement in result.newAchievements) ...[
                    const SizedBox(height: Spacing.md),
                    AppCard(
                      borderColor: game.coin,
                      child: Row(
                        children: [
                          Text(
                            achievement.icon,
                            style: const TextStyle(fontSize: 32),
                          ),
                          const SizedBox(width: Spacing.md),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Достижение: ${achievement.title}',
                                  style: textTheme.titleMedium,
                                ),
                                Text(achievement.description),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: Spacing.md),
            if (onContinue != null) ...[
              AppButton(label: 'Дальше', onPressed: onContinue),
              const SizedBox(height: Spacing.sm),
            ],
            AppButton(
              label: 'К карте',
              variant: AppButtonVariant.secondary,
              onPressed: onBackToMap,
            ),
          ],
        ),
      ),
    );
  }
}

class _TimedSummary extends StatelessWidget {
  const _TimedSummary({required this.run});

  final TimedRunProgress run;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    return AppCard(
      borderColor: game.streak,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (run.moduleCleared) ...[
            Text(
              'Модуль пройден за ${formatClock(run.clearTime!)}',
              style: textTheme.titleMedium,
            ),
            if (run.speedBonus > 0)
              Text('Бонус за скорость: +${run.speedBonus} XP'),
            if (run.bestTime != null)
              Text(
                run.isNewRecord
                    ? 'Новый рекорд!'
                    : 'Рекорд: ${formatClock(run.bestTime!)}',
              ),
          ] else ...[
            Text(
              'Осталось ${formatClock(run.timeLeft)}',
              style: textTheme.titleMedium?.copyWith(color: game.streak),
            ),
            const SizedBox(height: Spacing.sm),
            AppProgressBar(
              value: run.levelsInRun == 0
                  ? 0
                  : run.completedInRun / run.levelsInRun,
              color: game.streak,
            ),
            const SizedBox(height: Spacing.xs),
            Text('${run.completedInRun} из ${run.levelsInRun} уровней'),
          ],
        ],
      ),
    );
  }
}

class _AnimatedStars extends StatelessWidget {
  const _AnimatedStars({required this.stars, required this.size});

  final int stars;
  final double size;

  static const int _maxStars = 3;
  static const Duration _stagger = Duration(milliseconds: 250);

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        for (var i = 0; i < _maxStars; i++)
          TweenAnimationBuilder<double>(
            tween: Tween(begin: 0, end: 1),
            duration: AppDurations.slow + _stagger * i,
            curve: Curves.elasticOut,
            builder: (context, scale, child) =>
                Transform.scale(scale: scale, child: child),
            child: Icon(
              Icons.star_rounded,
              size: i == 1 ? size * 1.25 : size,
              color: i < stars ? game.coin : game.locked,
            ),
          ),
      ],
    );
  }
}
