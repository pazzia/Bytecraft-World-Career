import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/di/providers.dart';
import '../../../app/router/routes.dart';
import '../../../core/config/build_info.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';
import '../../../core/theme/game_colors.dart';
import '../../../services/analytics/analytics_service.dart';
import '../../../shared/widgets/app_button.dart';
import '../../../shared/widgets/app_card.dart';
import '../../../shared/widgets/app_progress_bar.dart';
import '../../../shared/widgets/async_value_view.dart';
import '../../../shared/widgets/segmented_switch.dart';
import '../../../shared/widgets/stat_badges.dart';
import '../../achievements/domain/achievement_catalog.dart';
import '../../achievements/presentation/achievement_visuals.dart';
import '../../gamification/domain/score_calculators.dart';
import '../../progress/domain/course_progress.dart';
import '../../progress/domain/user_profile.dart';
import '../../progress/presentation/progress_providers.dart';
import '../../settings/domain/app_settings.dart';
import '../../settings/presentation/settings_controller.dart';

class ProfileViewModel {
  const ProfileViewModel({
    required this.profile,
    required this.level,
    required this.progress,
  });

  final UserProfile profile;
  final AccountLevel level;
  final CourseProgress progress;
}

final profileViewModelProvider = FutureProvider<ProfileViewModel>((ref) async {
  return ProfileViewModel(
    profile: await ref.watch(profileProvider.future),
    level: await ref.watch(accountLevelProvider.future),
    progress: await ref.watch(activeCourseProgressProvider.future),
  );
});

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  Future<void> _confirmReset(BuildContext context, WidgetRef ref) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Сбросить прогресс?'),
        content: const Text(
          'Опыт, звёзды, серия, монеты и пройденные уровни удалятся. '
          'Отменить это нельзя.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Отмена'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Сбросить прогресс'),
          ),
        ],
      ),
    );
    if (confirmed != true) return;
    await ref.read(progressRepositoryProvider).resetAll();
    ref.read(progressRevisionProvider.notifier).bump();
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final vm = ref.watch(profileViewModelProvider);
    final theme = ref.watch(
      settingsControllerProvider.select(
        (value) => value.value?.theme ?? ThemePreference.system,
      ),
    );
    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: AsyncValueView<ProfileViewModel>(
          value: vm,
          onRetry: () => ref.invalidate(profileViewModelProvider),
          data: (vm) {
            final unlocked = vm.profile.unlockedAchievements;
            final unlockedCount = AchievementCatalog.all
                .where((achievement) => unlocked.contains(achievement.id))
                .length;
            return ListView(
              padding: const EdgeInsets.fromLTRB(
                Spacing.page,
                Spacing.xxl,
                Spacing.page,
                Spacing.huge,
              ),
              children: [
                _Header(vm: vm),
                const SizedBox(height: Spacing.xl),
                _StatsBlock(vm: vm),
                SectionTitle(
                  'Достижения',
                  trailing: '$unlockedCount из ${AchievementCatalog.all.length}',
                ),
                GridView.count(
                  crossAxisCount: 3,
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  mainAxisSpacing: Spacing.md,
                  crossAxisSpacing: Spacing.sm,
                  childAspectRatio: 0.82,
                  children: [
                    for (final achievement in AchievementCatalog.all)
                      Semantics(
                        label: '${achievement.title}: '
                            '${unlocked.contains(achievement.id) ? 'получено' : achievement.description}',
                        excludeSemantics: true,
                        child: Column(
                          children: [
                            AchievementBadge(
                              achievement: achievement,
                              unlocked: unlocked.contains(achievement.id),
                            ),
                            const SizedBox(height: Spacing.xs),
                            Text(
                              achievement.title,
                              textAlign: TextAlign.center,
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                              style: Theme.of(context).textTheme.labelMedium?.copyWith(
                                    color: unlocked.contains(achievement.id)
                                        ? null
                                        : context.gameColors.textMuted,
                                  ),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
                const SectionTitle('Тема'),
                SegmentedSwitch<ThemePreference>(
                  semanticLabel: 'Тема оформления',
                  selected: theme,
                  onChanged: ref.read(settingsControllerProvider.notifier).setTheme,
                  options: const [
                    SegmentOption(ThemePreference.system, 'Авто'),
                    SegmentOption(ThemePreference.light, 'Светлая'),
                    SegmentOption(ThemePreference.dark, 'Тёмная'),
                  ],
                ),
                const SizedBox(height: Spacing.xxl),
                _LinkRow(
                  icon: Icons.storefront_rounded,
                  label: 'Магазин',
                  onTap: () => context.push(Routes.shop),
                ),
                const SizedBox(height: Spacing.md),
                _LinkRow(
                  icon: Icons.workspace_premium_rounded,
                  label: vm.profile.isPremium ? 'Premium активен' : 'Premium',
                  onTap: () {
                    ref.read(analyticsProvider).track(
                      AnalyticsEvent.premiumScreenOpened,
                      {'source': 'profile'},
                    );
                    context.push(Routes.premium);
                  },
                ),
                const SizedBox(height: Spacing.xl),
                AppButton(
                  label: 'Сбросить прогресс',
                  variant: AppButtonVariant.quiet,
                  onPressed: () => _confirmReset(context, ref),
                ),
                const SizedBox(height: Spacing.lg),
                Text(
                  'Bytecraft ${BuildInfo.label}',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.labelMedium?.copyWith(
                        color: context.gameColors.textMuted,
                      ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}

class _Header extends StatelessWidget {
  const _Header({required this.vm});

  final ProfileViewModel vm;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    final level = vm.level;
    return Row(
      children: [
        Container(
          width: 72,
          height: 72,
          margin: const EdgeInsets.only(bottom: 5),
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: game.board,
            borderRadius: BorderRadius.circular(22),
            boxShadow: AppShadows.edge(game.boardEdge, depth: 5),
          ),
          child: Text(
            '{}',
            style: AppTypography.code(
              color: game.reward,
              size: 26,
              weight: FontWeight.w700,
            ),
          ),
        ),
        const SizedBox(width: Spacing.lg),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(vm.profile.displayName, style: textTheme.headlineSmall),
              const SizedBox(height: Spacing.xs),
              Row(
                children: [
                  Expanded(
                    child: Text(
                      'Уровень ${level.level}'
                      '${vm.profile.isPremium ? ', Premium' : ''}',
                      style: textTheme.titleSmall,
                    ),
                  ),
                  Text(
                    '${level.xpIntoLevel} из ${level.xpForNextLevel} XP',
                    style: textTheme.labelMedium?.copyWith(color: game.textMuted),
                  ),
                ],
              ),
              const SizedBox(height: Spacing.sm),
              AppProgressBar(value: level.progress, height: 8),
            ],
          ),
        ),
      ],
    );
  }
}

class _StatsBlock extends StatelessWidget {
  const _StatsBlock({required this.vm});

  final ProfileViewModel vm;

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    final textTheme = Theme.of(context).textTheme;
    final stats = [
      ('${vm.profile.totalXp}', 'опыта всего'),
      ('${vm.profile.streak.longest}', 'лучшая серия'),
      (
        '${vm.progress.completedCount}',
        '${plural(vm.progress.completedCount, 'уровень', 'уровня', 'уровней')} пройдено'
      ),
      (
        '${vm.progress.totalStars}',
        plural(vm.progress.totalStars, 'звезда', 'звезды', 'звёзд')
      ),
      ('${vm.progress.perfectCount}', 'без ошибок'),
      (
        '${vm.profile.coins}',
        plural(vm.profile.coins, 'монета', 'монеты', 'монет')
      ),
    ];
    Widget cell(int i) => Semantics(
          label: '${stats[i].$1} ${stats[i].$2}',
          excludeSemantics: true,
          child: Container(
            padding: const EdgeInsets.all(Spacing.md),
            decoration: BoxDecoration(
              border: Border(
                left: i % 3 == 0
                    ? BorderSide.none
                    : BorderSide(color: game.keyBorder, width: 2),
                top: i < 3
                    ? BorderSide.none
                    : BorderSide(color: game.keyBorder, width: 2),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(stats[i].$1, style: textTheme.headlineSmall),
                Text(
                  stats[i].$2,
                  maxLines: 2,
                  style: textTheme.bodySmall?.copyWith(color: game.textMuted),
                ),
              ],
            ),
          ),
        );
    return Container(
      margin: const EdgeInsets.only(bottom: 4),
      decoration: BoxDecoration(
        color: game.keyFace,
        borderRadius: AppRadius.xlAll,
        border: Border.all(color: game.keyBorder, width: 2),
        boxShadow: AppShadows.edge(game.keyEdge),
      ),
      child: Column(
        children: [
          for (var row = 0; row < 2; row++)
            IntrinsicHeight(
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  for (var col = 0; col < 3; col++)
                    Expanded(child: cell(row * 3 + col)),
                ],
              ),
            ),
        ],
      ),
    );
  }
}

class _LinkRow extends StatelessWidget {
  const _LinkRow({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => AppCard(
        onTap: onTap,
        semanticLabel: label,
        padding: const EdgeInsets.symmetric(
          horizontal: Spacing.lg,
          vertical: Spacing.md,
        ),
        child: Row(
          children: [
            Icon(icon, color: Theme.of(context).colorScheme.primary),
            const SizedBox(width: Spacing.md),
            Expanded(
              child: Text(label, style: Theme.of(context).textTheme.titleMedium),
            ),
            Icon(Icons.chevron_right_rounded, color: context.gameColors.textMuted),
          ],
        ),
      );
}
