import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/di/providers.dart';
import '../../../app/router/routes.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';
import '../../../core/theme/game_colors.dart';
import '../../../services/feature_flags/feature_flag_service.dart';
import '../../../shared/widgets/app_button.dart';
import '../../../shared/widgets/app_card.dart';
import '../../../shared/widgets/app_progress_bar.dart';
import '../../../shared/widgets/async_value_view.dart';
import '../../../shared/widgets/code_block.dart';
import '../../../shared/widgets/keycap.dart';
import '../../../shared/widgets/stat_badges.dart';
import '../../daily_challenge/domain/daily_challenge.dart';
import '../../journal/presentation/journal_providers.dart';
import '../../learning_map/domain/learning_map_model.dart';
import '../../learning_map/presentation/learning_map_providers.dart';
import '../../level/domain/level_session.dart';
import '../../level/presentation/widgets/level_code_preview.dart';
import 'home_providers.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final home = ref.watch(homeViewModelProvider);
    final dueReviews = ref.watch(dueReviewCountProvider).value ?? 0;
    final timedEnabled =
        ref.watch(featureFlagsProvider).isEnabled(FeatureFlag.timedRuns);
    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: AsyncValueView<HomeViewModel>(
          value: home,
          onRetry: () => ref.invalidate(homeViewModelProvider),
          data: (vm) => RefreshIndicator(
            onRefresh: () => ref.refresh(homeViewModelProvider.future),
            child: ListView(
              padding: const EdgeInsets.fromLTRB(
                Spacing.page,
                Spacing.xxl,
                Spacing.page,
                Spacing.xxl,
              ),
              children: [
                _Hud(vm: vm),
                const SizedBox(height: Spacing.xl),
                _NextLevelBoard(vm: vm),
                const SizedBox(height: Spacing.xl),
                if (dueReviews > 0) ...[
                  _ReviewTile(
                    count: dueReviews,
                    onTap: () => context.go(Routes.journal),
                  ),
                  const SizedBox(height: Spacing.xl),
                ],
                _CourseProgress(map: vm.map),
                const SizedBox(height: Spacing.xl),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (vm.dailyChallenge != null)
                      Expanded(child: _DailyTile(challenge: vm.dailyChallenge!)),
                    if (vm.dailyChallenge != null && timedEnabled)
                      const SizedBox(width: Spacing.md),
                    if (timedEnabled)
                      Expanded(
                        child: _TimedTile(
                          onTap: () {
                            ref.read(mapModeProvider.notifier).select(MapMode.timed);
                            context.go(Routes.map);
                          },
                        ),
                      ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _Hud extends StatelessWidget {
  const _Hud({required this.vm});

  final HomeViewModel vm;

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    return Row(
      children: [
        StreakBadge(days: vm.streakDays),
        const SizedBox(width: Spacing.lg),
        XpBadge(xp: vm.profile.totalXp),
        const SizedBox(width: Spacing.lg),
        LivesBadge(
          current: vm.lives.current,
          isUnlimited: vm.lives.isUnlimited,
        ),
        const Spacer(),
        Keycap(
          onTap: () => context.go(Routes.profile),
          face: game.board,
          edge: game.boardEdge,
          radius: 12,
          depth: 3,
          width: 44,
          height: 44,
          semanticLabel: 'Профиль',
          child: Text(
            '{}',
            style: AppTypography.code(
              color: game.reward,
              size: 17,
              weight: FontWeight.w700,
            ),
          ),
        ),
      ],
    );
  }
}

/// The hero: the next level on a code board, one tap to continue.
class _NextLevelBoard extends StatelessWidget {
  const _NextLevelBoard({required this.vm});

  final HomeViewModel vm;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    final map = vm.map;
    final next = map.nextLevel;

    if (next == null) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(map.course.title, style: textTheme.labelMedium?.copyWith(color: game.textMuted)),
          const SizedBox(height: Spacing.xs),
          Text('Курс пройден', style: textTheme.headlineLarge),
          const SizedBox(height: Spacing.lg),
          AppButton(
            label: 'Открыть карту',
            onPressed: () => context.go(Routes.map),
          ),
        ],
      );
    }

    final module = map.course.moduleOf(next.id);
    final section = map.sections.firstWhere(
      (section) => section.module.id == module?.id,
      orElse: () => map.sections.first,
    );
    final position =
        section.nodes.indexWhere((node) => node.level.id == next.id) + 1;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          map.course.title,
          style: textTheme.labelMedium?.copyWith(color: game.textMuted),
        ),
        const SizedBox(height: Spacing.xs),
        Text(module?.title ?? next.title, style: textTheme.headlineLarge),
        const SizedBox(height: Spacing.lg),
        CodeBoard(
          padding: const EdgeInsets.all(Spacing.xl),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      'Уровень $position из ${section.total}',
                      style: textTheme.labelMedium?.copyWith(color: game.boardMuted),
                    ),
                  ),
                  Text(
                    '+${vm.nextLevelXp} XP',
                    style: textTheme.labelMedium?.copyWith(
                      color: game.reward,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: Spacing.md),
              if (LevelCodePreview.hasPreview(next)) ...[
                LevelCodePreview(level: next),
                const SizedBox(height: Spacing.md),
              ],
              Text(
                next.title,
                style: textTheme.titleLarge?.copyWith(color: game.codeText),
              ),
              const SizedBox(height: Spacing.lg),
              AppButton(
                label: 'Продолжить',
                icon: Icons.play_arrow_rounded,
                variant: AppButtonVariant.reward,
                onPressed: () => context.push(Routes.level(map.course.id, next.id)),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _CourseProgress extends StatelessWidget {
  const _CourseProgress({required this.map});

  final LearningMapModel map;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    final nextModuleId =
        map.nextLevel == null ? null : map.course.moduleOf(map.nextLevel!.id)?.id;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Expanded(
              child: Text(
                '${map.completed} из ${map.total} ${plural(map.total, 'уровня', 'уровней', 'уровней')}',
                style: textTheme.titleSmall,
              ),
            ),
            Text(
              '${map.stars} ${plural(map.stars, 'звезда', 'звезды', 'звёзд')}',
              style: textTheme.labelMedium?.copyWith(color: game.textMuted),
            ),
          ],
        ),
        const SizedBox(height: Spacing.sm),
        SegmentedProgress(
          semanticLabel: 'Пройдено модулей: '
              '${map.sections.where((s) => s.completed == s.total).length} из ${map.sections.length}',
          segments: [
            for (final section in map.sections)
              section.total > 0 && section.completed == section.total
                  ? SegmentState.done
                  : section.module.id == nextModuleId
                      ? SegmentState.current
                      : SegmentState.todo,
          ],
        ),
      ],
    );
  }
}

class _DailyTile extends StatelessWidget {
  const _DailyTile({required this.challenge});

  final DailyChallenge challenge;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    final done = challenge.isCompleted;
    return AppCard(
      semanticLabel: done ? 'Задача дня выполнена' : 'Задача дня',
      onTap: done
          ? null
          : () => context.push(
                Routes.level(
                  challenge.level.courseId,
                  challenge.level.id,
                  mode: LevelMode.dailyChallenge,
                ),
              ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            done ? Icons.check_circle_rounded : Icons.event_rounded,
            size: 28,
            color: done ? game.success : Theme.of(context).colorScheme.primary,
          ),
          const SizedBox(height: Spacing.md),
          Text('Задача дня', style: textTheme.titleMedium),
          const SizedBox(height: Spacing.xs),
          Text(
            done
                ? 'Выполнено. Новая будет завтра'
                : '+${challenge.bonus.xp} XP и ${challenge.bonus.coins} '
                    '${plural(challenge.bonus.coins, 'монета', 'монеты', 'монет')}',
            style: textTheme.bodySmall?.copyWith(color: game.textMuted),
          ),
        ],
      ),
    );
  }
}

class _TimedTile extends StatelessWidget {
  const _TimedTile({required this.onTap});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    const night = GameColors.timed;
    // In the dark theme the page is already night-coloured: lift the tile.
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final face = isDark ? night.keyFace : night.background;
    return AppCard(
      semanticLabel: 'Режим на время',
      onTap: onTap,
      color: face,
      borderColor: isDark ? night.streak : face,
      edgeColor: isDark ? night.primaryEdge : night.track,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.timer_outlined, size: 28, color: night.streak),
          const SizedBox(height: Spacing.md),
          Text(
            'На время',
            style: textTheme.titleMedium?.copyWith(color: Colors.white),
          ),
          const SizedBox(height: Spacing.xs),
          Text(
            'Модуль на скорость, ×2 XP',
            style: textTheme.bodySmall?.copyWith(color: night.textMuted),
          ),
        ],
      ),
    );
  }
}

class _ReviewTile extends StatelessWidget {
  const _ReviewTile({required this.count, required this.onTap});

  final int count;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    return AppCard(
      onTap: onTap,
      semanticLabel: 'Повторить темы из журнала: $count',
      child: Row(
        children: [
          Icon(Icons.menu_book_rounded, color: game.streak, size: 32),
          const SizedBox(width: Spacing.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Повторение', style: textTheme.titleMedium),
                Text(
                  '$count ${plural(count, 'тема ждёт', 'темы ждут', 'тем ждут')} в журнале',
                  style: textTheme.bodyMedium?.copyWith(color: game.textMuted),
                ),
              ],
            ),
          ),
          Icon(Icons.chevron_right_rounded, color: game.textMuted),
        ],
      ),
    );
  }
}
