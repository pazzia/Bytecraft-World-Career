import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/di/providers.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/game_colors.dart';
import '../../../shared/widgets/app_card.dart';
import '../../../shared/widgets/app_progress_bar.dart';
import '../../../shared/widgets/async_value_view.dart';
import '../../achievements/domain/achievement_catalog.dart';
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
        content: const Text('XP, звёзды, серия и пройденные уровни удалятся.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Отмена'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Сбросить'),
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
      appBar: AppBar(title: const Text('Профиль')),
      body: AsyncValueView<ProfileViewModel>(
        value: vm,
        onRetry: () => ref.invalidate(profileViewModelProvider),
        data: (vm) => ListView(
          padding: const EdgeInsets.all(Spacing.page),
          children: [
            _LevelCard(vm: vm),
            const SectionTitle('Статистика'),
            _StatsGrid(vm: vm),
            const SectionTitle('Достижения'),
            for (final achievement in AchievementCatalog.all)
              Padding(
                padding: const EdgeInsets.only(bottom: Spacing.sm),
                child: Opacity(
                  opacity: vm.profile.unlockedAchievements
                          .contains(achievement.id)
                      ? 1
                      : 0.4,
                  child: AppCard(
                    padding: const EdgeInsets.all(Spacing.md),
                    child: Row(
                      children: [
                        Text(
                          achievement.icon,
                          style: const TextStyle(fontSize: 28),
                        ),
                        const SizedBox(width: Spacing.md),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                achievement.title,
                                style: Theme.of(context).textTheme.titleSmall,
                              ),
                              Text(achievement.description),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            const SectionTitle('Тема'),
            SegmentedButton<ThemePreference>(
              segments: const [
                ButtonSegment(
                  value: ThemePreference.system,
                  label: Text('Авто'),
                ),
                ButtonSegment(
                  value: ThemePreference.light,
                  label: Text('Светлая'),
                ),
                ButtonSegment(
                  value: ThemePreference.dark,
                  label: Text('Тёмная'),
                ),
              ],
              selected: {theme},
              onSelectionChanged: (selection) => ref
                  .read(settingsControllerProvider.notifier)
                  .setTheme(selection.first),
            ),
            const SizedBox(height: Spacing.xl),
            TextButton(
              onPressed: () => _confirmReset(context, ref),
              child: const Text('Сбросить прогресс'),
            ),
          ],
        ),
      ),
    );
  }
}

class _LevelCard extends StatelessWidget {
  const _LevelCard({required this.vm});

  final ProfileViewModel vm;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;
    final profile = vm.profile;
    return AppCard(
      child: Row(
        children: [
          CircleAvatar(
            radius: 32,
            backgroundColor: scheme.primary,
            child: const Text('🤖', style: TextStyle(fontSize: 30)),
          ),
          const SizedBox(width: Spacing.lg),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(profile.displayName, style: textTheme.titleLarge),
                Text(
                  'Уровень ${vm.level.level}'
                  '${profile.isPremium ? ' · Premium ⭐' : ''}',
                ),
                const SizedBox(height: Spacing.sm),
                AppProgressBar(
                  value: vm.level.progress,
                  height: 10,
                  color: context.gameColors.xp,
                ),
                const SizedBox(height: Spacing.xs),
                Text(
                  '${vm.level.xpIntoLevel} / ${vm.level.xpForNextLevel} XP',
                  style: textTheme.bodySmall,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _StatsGrid extends StatelessWidget {
  const _StatsGrid({required this.vm});

  final ProfileViewModel vm;

  @override
  Widget build(BuildContext context) {
    final stats = [
      ('⚡', '${vm.profile.totalXp}', 'Всего XP'),
      ('🔥', '${vm.profile.streak.longest}', 'Лучшая серия'),
      ('✅', '${vm.progress.completedCount}', 'Уровней'),
      ('⭐', '${vm.progress.totalStars}', 'Звёзд'),
      ('💎', '${vm.progress.perfectCount}', 'Идеальных'),
      ('🪙', '${vm.profile.coins}', 'Монет'),
    ];
    return GridView.count(
      crossAxisCount: 3,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      mainAxisSpacing: Spacing.sm,
      crossAxisSpacing: Spacing.sm,
      childAspectRatio: 0.95,
      children: [
        for (final (glyph, value, label) in stats)
          AppCard(
            padding: const EdgeInsets.all(Spacing.sm),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(glyph, style: const TextStyle(fontSize: 22)),
                Text(value, style: Theme.of(context).textTheme.titleLarge),
                Text(
                  label,
                  style: Theme.of(context).textTheme.bodySmall,
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
      ],
    );
  }
}
