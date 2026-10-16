import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../../core/theme/app_spacing.dart';
import '../../../../core/theme/game_colors.dart';
import '../../../../shared/widgets/app_button.dart';
import '../../../../shared/widgets/app_progress_bar.dart';
import '../../../../shared/widgets/stat_badges.dart';
import '../../../achievements/presentation/achievement_visuals.dart';
import '../../../timed_run/presentation/countdown.dart';
import '../../domain/level_result.dart';

/// Rewards screen: star keys, what was earned, where the player is now.
class LevelCompleteView extends StatefulWidget {
  const LevelCompleteView({
    super.key,
    required this.result,
    required this.onContinue,
    required this.onBackToMap,
  });

  final LevelResult result;

  /// Null when there is no next level.
  final VoidCallback? onContinue;
  final VoidCallback onBackToMap;

  @override
  State<LevelCompleteView> createState() => _LevelCompleteViewState();
}

class _LevelCompleteViewState extends State<LevelCompleteView> {
  @override
  void initState() {
    super.initState();
    HapticFeedback.mediumImpact();
  }

  String get _headline {
    final result = widget.result;
    final timed = result.timedRun;
    if (timed != null && timed.moduleCleared) return 'Модуль пройден';
    return result.isPerfect ? 'С первой попытки' : 'Уровень пройден';
  }

  @override
  Widget build(BuildContext context) {
    final result = widget.result;
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    return Column(
      children: [
        Container(
          width: double.infinity,
          decoration: BoxDecoration(
            color: game.board,
            borderRadius: const BorderRadius.vertical(
              bottom: Radius.circular(36),
            ),
          ),
          child: SafeArea(
            bottom: false,
            child: Padding(
              padding: const EdgeInsets.fromLTRB(
                Spacing.page,
                Spacing.huge,
                Spacing.page,
                Spacing.xxxl,
              ),
              child: Column(
                children: [
                  _StarKeys(stars: result.stars),
                  const SizedBox(height: Spacing.xl),
                  Text(
                    _headline,
                    textAlign: TextAlign.center,
                    style: textTheme.headlineLarge?.copyWith(color: Colors.white),
                  ),
                ],
              ),
            ),
          ),
        ),
        Expanded(
          child: ListView(
            padding: const EdgeInsets.fromLTRB(
              Spacing.page,
              Spacing.xxl,
              Spacing.page,
              Spacing.lg,
            ),
            children: [
              _EarnedRow(result: result),
              if (result.streakExtended) ...[
                const SizedBox(height: Spacing.md),
                _Banner(
                  icon: Icons.local_fire_department_rounded,
                  iconColor: game.streak,
                  color: game.streakTint,
                  textColor: game.streakText,
                  text: 'Серия продлена: ${result.streak} '
                      '${plural(result.streak, 'день', 'дня', 'дней')} подряд',
                ),
              ],
              if (result.leveledUp) ...[
                const SizedBox(height: Spacing.md),
                _Banner(
                  icon: Icons.arrow_circle_up_rounded,
                  iconColor: Theme.of(context).colorScheme.primary,
                  color: game.primaryTint,
                  text: 'Новый уровень аккаунта: ${result.accountLevelAfter}',
                ),
              ],
              if (result.dailyChallengeCompleted) ...[
                const SizedBox(height: Spacing.md),
                _Banner(
                  icon: Icons.event_available_rounded,
                  iconColor: game.success,
                  color: game.successTint,
                  text: 'Задача дня выполнена',
                ),
              ],
              for (final achievement in result.newAchievements) ...[
                const SizedBox(height: Spacing.md),
                Row(
                  children: [
                    AchievementBadge(
                      achievement: achievement,
                      unlocked: true,
                      size: 48,
                    ),
                    const SizedBox(width: Spacing.md),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Новое достижение: ${achievement.title}',
                            style: textTheme.titleSmall,
                          ),
                          Text(
                            achievement.description,
                            style: textTheme.bodySmall
                                ?.copyWith(color: game.textMuted),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
              const SizedBox(height: Spacing.xl),
              if (result.timedRun != null)
                _TimedSummary(run: result.timedRun!)
              else
                _CourseSummary(result: result),
            ],
          ),
        ),
        SafeArea(
          top: false,
          child: Padding(
            padding: const EdgeInsets.fromLTRB(
              Spacing.page,
              Spacing.sm,
              Spacing.page,
              Spacing.lg,
            ),
            child: Column(
              children: [
                if (widget.onContinue != null) ...[
                  AppButton(
                    label: result.timedRun != null
                        ? 'Следующий уровень забега'
                        : 'Следующий уровень',
                    onPressed: widget.onContinue,
                  ),
                  const SizedBox(height: Spacing.xs),
                ],
                AppButton(
                  label: 'К карте',
                  variant: widget.onContinue == null
                      ? AppButtonVariant.primary
                      : AppButtonVariant.quiet,
                  onPressed: widget.onBackToMap,
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

/// Three star keys pop in one after another (static with reduced motion).
class _StarKeys extends StatelessWidget {
  const _StarKeys({required this.stars});

  final int stars;

  static const Duration _stagger = Duration(milliseconds: 180);

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    final reduceMotion = MediaQuery.maybeDisableAnimationsOf(context) ?? false;
    Widget key(int i, double size) {
      final earned = i < stars;
      final box = Container(
        width: size,
        height: size,
        margin: const EdgeInsets.symmetric(horizontal: 5),
        decoration: BoxDecoration(
          color: earned ? game.reward : game.boardEdge,
          borderRadius: BorderRadius.circular(size * 0.28),
          boxShadow: earned ? AppShadows.edge(game.rewardEdge, depth: 5) : null,
        ),
        child: Icon(
          Icons.star_rounded,
          size: size * 0.6,
          color: earned ? game.onReward : game.boardMuted.withValues(alpha: 0.4),
        ),
      );
      if (reduceMotion) return box;
      return TweenAnimationBuilder<double>(
        tween: Tween(begin: 0, end: 1),
        duration: AppDurations.slow + _stagger * i,
        curve: Interval(
          (_stagger * i).inMilliseconds /
              (AppDurations.slow + _stagger * i).inMilliseconds,
          1,
          curve: Curves.elasticOut,
        ),
        builder: (context, t, child) => Transform.scale(scale: t, child: child),
        child: box,
      );
    }

    return Semantics(
      label: '$stars из 3 звёзд',
      excludeSemantics: true,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          key(0, 72),
          Padding(
            padding: const EdgeInsets.only(bottom: Spacing.md),
            child: key(1, 92),
          ),
          key(2, 72),
        ],
      ),
    );
  }
}

class _EarnedRow extends StatelessWidget {
  const _EarnedRow({required this.result});

  final LevelResult result;

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    final textTheme = Theme.of(context).textTheme;
    Widget cell(IconData icon, Color color, String value, String label) =>
        Expanded(
          child: Semantics(
            label: '$value $label',
            excludeSemantics: true,
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: Spacing.md),
              child: Column(
                children: [
                  Icon(icon, color: color),
                  const SizedBox(height: Spacing.xs),
                  Text(value, style: textTheme.titleLarge),
                  Text(
                    label,
                    style: textTheme.bodySmall?.copyWith(color: game.textMuted),
                  ),
                ],
              ),
            ),
          ),
        );
    Widget divider() => Container(width: 2, height: 56, color: game.keyBorder);
    return Container(
      margin: const EdgeInsets.only(bottom: 4),
      decoration: BoxDecoration(
        color: game.keyFace,
        borderRadius: AppRadius.xlAll,
        border: Border.all(color: game.keyBorder, width: 2),
        boxShadow: AppShadows.edge(game.keyEdge),
      ),
      child: Row(
        children: [
          cell(Icons.bolt_rounded, game.rewardIcon, '+${result.xpEarned}', 'опыта'),
          divider(),
          cell(
            Icons.toll_rounded,
            game.rewardIcon,
            '+${result.coinsEarned}',
            plural(result.coinsEarned, 'монета', 'монеты', 'монет'),
          ),
          divider(),
          cell(
            Icons.local_fire_department_rounded,
            game.streak,
            '${result.streak}',
            '${plural(result.streak, 'день', 'дня', 'дней')} подряд',
          ),
        ],
      ),
    );
  }
}

class _Banner extends StatelessWidget {
  const _Banner({
    required this.icon,
    required this.iconColor,
    required this.color,
    required this.text,
    this.textColor,
  });

  final IconData icon;
  final Color iconColor;
  final Color color;
  final Color? textColor;
  final String text;

  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.symmetric(
          horizontal: Spacing.lg,
          vertical: Spacing.md,
        ),
        decoration: BoxDecoration(color: color, borderRadius: AppRadius.lgAll),
        child: Row(
          children: [
            Icon(icon, color: iconColor),
            const SizedBox(width: Spacing.md),
            Expanded(
              child: Text(
                text,
                style: Theme.of(context)
                    .textTheme
                    .titleSmall
                    ?.copyWith(color: textColor),
              ),
            ),
          ],
        ),
      );
}

class _CourseSummary extends StatelessWidget {
  const _CourseSummary({required this.result});

  final LevelResult result;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Expanded(child: Text('Прогресс курса', style: textTheme.titleSmall)),
            Text(
              '${result.completedInCourse} из ${result.playableInCourse}',
              style: textTheme.labelMedium?.copyWith(color: game.textMuted),
            ),
          ],
        ),
        const SizedBox(height: Spacing.sm),
        AppProgressBar(value: result.courseProgress, color: game.success),
      ],
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
    if (run.moduleCleared) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Время: ${formatClock(run.clearTime!)}',
            style: textTheme.titleLarge,
          ),
          const SizedBox(height: Spacing.xs),
          if (run.speedBonus > 0)
            Text(
              'Бонус за скорость: +${run.speedBonus} XP',
              style: textTheme.bodyLarge?.copyWith(color: game.streakText),
            ),
          if (run.bestTime != null)
            Text(
              run.isNewRecord
                  ? 'Это ваш рекорд'
                  : 'Рекорд: ${formatClock(run.bestTime!)}',
              style: textTheme.bodyLarge?.copyWith(color: game.textMuted),
            ),
        ],
      );
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Expanded(
              child: Text(
                'Осталось ${formatClock(run.timeLeft)}',
                style: textTheme.titleLarge?.copyWith(color: game.streakText),
              ),
            ),
            Text(
              '${run.completedInRun} из ${run.levelsInRun}',
              style: textTheme.labelMedium?.copyWith(color: game.textMuted),
            ),
          ],
        ),
        const SizedBox(height: Spacing.sm),
        AppProgressBar(
          value: run.levelsInRun == 0 ? 0 : run.completedInRun / run.levelsInRun,
          color: game.streak,
        ),
      ],
    );
  }
}
