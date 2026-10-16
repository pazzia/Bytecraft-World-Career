import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/di/providers.dart';
import '../../../app/router/routes.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/game_colors.dart';
import '../../../services/analytics/analytics_service.dart';
import '../../../shared/widgets/app_button.dart';
import '../../../shared/widgets/app_card.dart';
import '../../../shared/widgets/app_progress_bar.dart';
import '../../../shared/widgets/async_value_view.dart';
import '../../../shared/widgets/stat_badges.dart';
import '../../daily_challenge/domain/daily_challenge.dart';
import 'home_providers.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final home = ref.watch(homeViewModelProvider);
    return Scaffold(
      body: SafeArea(
        child: AsyncValueView<HomeViewModel>(
          value: home,
          onRetry: () => ref.invalidate(homeViewModelProvider),
          data: (vm) => RefreshIndicator(
            onRefresh: () => ref.refresh(homeViewModelProvider.future),
            child: ListView(
              padding: const EdgeInsets.all(Spacing.page),
              children: [
                _Header(vm: vm),
                const SizedBox(height: Spacing.xl),
                _ContinueCard(vm: vm),
                if (vm.dailyChallenge != null) ...[
                  const SizedBox(height: Spacing.lg),
                  _DailyChallengeCard(challenge: vm.dailyChallenge!),
                ],
                const SectionTitle('Магазин'),
                Row(
                  children: [
                    Expanded(
                      child: _Tile(
                        glyph: '🛒',
                        title: 'Магазин',
                        onTap: () => context.push(Routes.shop),
                      ),
                    ),
                    const SizedBox(width: Spacing.md),
                    Expanded(
                      child: _Tile(
                        glyph: '⭐',
                        title: 'Premium',
                        onTap: () {
                          ref.read(analyticsProvider).track(
                            AnalyticsEvent.premiumScreenOpened,
                            {'source': 'home'},
                          );
                          context.push(Routes.premium);
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

class _Header extends StatelessWidget {
  const _Header({required this.vm});

  final HomeViewModel vm;

  @override
  Widget build(BuildContext context) => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            vm.isStreakActiveToday
                ? 'Отличная работа сегодня!'
                : 'Пора кодить 👾',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: Spacing.md),
          Wrap(
            spacing: Spacing.sm,
            runSpacing: Spacing.sm,
            children: [
              StreakBadge(days: vm.streakDays),
              XpBadge(xp: vm.profile.totalXp),
              LivesBadge(
                current: vm.lives.current,
                isUnlimited: vm.lives.isUnlimited,
              ),
              CoinBadge(coins: vm.profile.coins),
            ],
          ),
        ],
      );
}

class _ContinueCard extends StatelessWidget {
  const _ContinueCard({required this.vm});

  final HomeViewModel vm;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final map = vm.map;
    final next = map.nextLevel;
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Текущий курс', style: textTheme.labelMedium),
          const SizedBox(height: Spacing.xs),
          Text(map.course.title, style: textTheme.titleLarge),
          const SizedBox(height: Spacing.md),
          AppProgressBar(value: map.progress),
          const SizedBox(height: Spacing.xs),
          Text('${map.completed} из ${map.total} уровней · ⭐ ${map.stars}'),
          const SizedBox(height: Spacing.lg),
          if (next != null) ...[
            Text('Дальше: ${next.title}', style: textTheme.bodyMedium),
            const SizedBox(height: Spacing.sm),
            AppButton(
              label: 'Продолжить',
              icon: Icons.play_arrow_rounded,
              onPressed: () =>
                  context.push(Routes.level(map.course.id, next.id)),
            ),
          ] else
            AppButton(
              label: 'Курс пройден! К карте',
              variant: AppButtonVariant.success,
              onPressed: () => context.go(Routes.map),
            ),
        ],
      ),
    );
  }
}

class _DailyChallengeCard extends StatelessWidget {
  const _DailyChallengeCard({required this.challenge});

  final DailyChallenge challenge;

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    final textTheme = Theme.of(context).textTheme;
    return AppCard(
      borderColor: game.coin,
      onTap: challenge.isCompleted
          ? null
          : () => context.push(
                Routes.level(
                  challenge.level.courseId,
                  challenge.level.id,
                  daily: true,
                ),
              ),
      child: Row(
        children: [
          const Text('🏆', style: TextStyle(fontSize: 36)),
          const SizedBox(width: Spacing.lg),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Задача дня', style: textTheme.titleMedium),
                Text(
                  challenge.isCompleted
                      ? 'Выполнено — возвращайтесь завтра'
                      : '${challenge.level.title} · '
                          '+${challenge.bonus.xp} XP, '
                          '+${challenge.bonus.coins} 🪙',
                ),
              ],
            ),
          ),
          if (challenge.isCompleted)
            Icon(Icons.check_circle_rounded, color: game.success)
          else
            const Icon(Icons.chevron_right_rounded),
        ],
      ),
    );
  }
}

class _Tile extends StatelessWidget {
  const _Tile({required this.glyph, required this.title, required this.onTap});

  final String glyph;
  final String title;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => AppCard(
        onTap: onTap,
        child: Column(
          children: [
            Text(glyph, style: const TextStyle(fontSize: 28)),
            const SizedBox(height: Spacing.xs),
            Text(title, style: Theme.of(context).textTheme.titleSmall),
          ],
        ),
      );
}
