import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/di/providers.dart';
import '../../../app/router/routes.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/game_colors.dart';
import '../../../shared/widgets/app_button.dart';
import '../../../shared/widgets/app_progress_bar.dart';
import '../../../shared/widgets/stat_badges.dart';
import '../../../shared/widgets/async_value_view.dart';
import '../../courses/domain/course.dart';
import '../../level/domain/level_session.dart';
import '../../progress/presentation/progress_providers.dart';
import '../domain/timed_run.dart';
import '../domain/timed_run_service.dart';
import 'countdown.dart';

class TimedModuleCardModel {
  const TimedModuleCardModel({
    required this.module,
    required this.availability,
    required this.duration,
    this.bestTime,
    this.activeRun,
  });

  final CourseModule module;
  final TimedModuleAvailability availability;
  final Duration duration;
  final Duration? bestTime;

  /// Set when the player's active run is in this module.
  final TimedRun? activeRun;
}

class TimedOverview {
  const TimedOverview({required this.course, required this.modules});

  final Course course;
  final List<TimedModuleCardModel> modules;

  TimedRun? get activeRun {
    for (final module in modules) {
      if (module.activeRun != null) return module.activeRun;
    }
    return null;
  }
}

final timedOverviewProvider = FutureProvider<TimedOverview>((ref) async {
  ref.watch(progressRevisionProvider);
  final course = await ref.watch(activeCourseProvider.future);
  final progress = await ref.watch(activeCourseProgressProvider.future);
  final mode = await ref.watch(unlockModeProvider.future);
  final timed = await ref.watch(timedRunServiceProvider).load(course.id);
  final policy = ref.watch(timedRunPolicyProvider);
  return TimedOverview(
    course: course,
    modules: [
      for (final module in course.modules)
        if (module.playableLevels.isNotEmpty)
          TimedModuleCardModel(
            module: module,
            availability: policy.availability(module, progress, mode: mode),
            duration: policy.durationFor(module),
            bestTime: timed.bestTimes[module.id],
            activeRun: timed.activeRun?.moduleId == module.id
                ? timed.activeRun
                : null,
          ),
    ],
  );
});

/// "На время" tab of the map: one card per module.
class TimedRunsView extends ConsumerWidget {
  const TimedRunsView({super.key});

  Future<void> _start(
    BuildContext context,
    WidgetRef ref,
    TimedOverview overview,
    CourseModule module,
  ) async {
    final active = overview.activeRun;
    if (active != null && active.moduleId != module.id) {
      final confirmed = await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Начать новый забег?'),
          content: const Text('Текущий забег будет прерван.'),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: const Text('Отмена'),
            ),
            TextButton(
              onPressed: () => Navigator.of(context).pop(true),
              child: const Text('Начать'),
            ),
          ],
        ),
      );
      if (confirmed != true) return;
    }
    final result = await ref
        .read(timedRunServiceProvider)
        .startRun(overview.course.id, module.id);
    ref.read(progressRevisionProvider.notifier).bump();
    if (!context.mounted) return;
    switch (result) {
      case RunStarted(:final firstLevel):
        await context.push(
          Routes.level(
            overview.course.id,
            firstLevel.id,
            mode: LevelMode.timed,
          ),
        );
      case RunDenied():
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Сначала пройдите модуль в обучении')),
        );
    }
  }

  Future<void> _resume(
    BuildContext context,
    WidgetRef ref,
    TimedOverview overview,
    CourseModule module,
  ) async {
    final next = await ref
        .read(timedRunServiceProvider)
        .resume(overview.course.id, module.id);
    ref.read(progressRevisionProvider.notifier).bump();
    if (!context.mounted || next == null) return;
    await context.push(
      Routes.level(overview.course.id, next.id, mode: LevelMode.timed),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final overview = ref.watch(timedOverviewProvider);
    return AsyncValueView<TimedOverview>(
      value: overview,
      onRetry: () => ref.invalidate(timedOverviewProvider),
      data: (overview) => ListView(
        padding: const EdgeInsets.fromLTRB(
          Spacing.page,
          0,
          Spacing.page,
          Spacing.huge,
        ),
        children: [
          Text(
            'Пройдите модуль целиком, пока не вышло время. Первый забег '
            'даёт ×2 опыта и бонус за скорость.',
            style: Theme.of(context)
                .textTheme
                .bodyMedium
                ?.copyWith(color: context.gameColors.textMuted),
          ),
          const SizedBox(height: Spacing.lg),
          for (final card in overview.modules)
            Padding(
              padding: const EdgeInsets.only(bottom: Spacing.md),
              child: _ModuleCard(
                card: card,
                onStart: () => _start(context, ref, overview, card.module),
                onResume: () => _resume(context, ref, overview, card.module),
                onExpired: () => ref.invalidate(timedOverviewProvider),
              ),
            ),
        ],
      ),
    );
  }
}

class _ModuleCard extends StatelessWidget {
  const _ModuleCard({
    required this.card,
    required this.onStart,
    required this.onResume,
    required this.onExpired,
  });

  final TimedModuleCardModel card;
  final VoidCallback onStart;
  final VoidCallback onResume;
  final VoidCallback onExpired;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    final scheme = Theme.of(context).colorScheme;
    final locked = card.availability == TimedModuleAvailability.locked;
    final run = card.activeRun;
    final levels = card.module.playableLevels.length;
    final details = [
      '${formatClock(card.duration)} на $levels ${plural(levels, 'уровень', 'уровня', 'уровней')}',
      if (card.bestTime != null) 'рекорд ${formatClock(card.bestTime!)}',
    ].join(', ');

    if (locked) {
      return Container(
        padding: const EdgeInsets.all(Spacing.lg),
        decoration: BoxDecoration(
          borderRadius: AppRadius.xlAll,
          border: Border.all(color: game.keyBorder, width: 2),
        ),
        child: Row(
          children: [
            Icon(Icons.lock_rounded, color: game.lockedIcon),
            const SizedBox(width: Spacing.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    card.module.title,
                    style: textTheme.titleMedium?.copyWith(color: game.textMuted),
                  ),
                  Text(
                    'Откроется, когда пройдёте модуль в обучении',
                    style: textTheme.bodySmall?.copyWith(color: game.textMuted),
                  ),
                ],
              ),
            ),
          ],
        ),
      );
    }

    if (run != null) {
      return Container(
        padding: const EdgeInsets.all(Spacing.lg),
        margin: const EdgeInsets.only(bottom: 4),
        decoration: BoxDecoration(
          color: game.keyFace,
          borderRadius: AppRadius.xlAll,
          border: Border.all(color: scheme.primary, width: 2),
          boxShadow: AppShadows.edge(game.primaryEdge),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(card.module.title, style: textTheme.titleMedium),
                      Text(
                        'Забег идёт: ${run.completedLevelIds.length} из $levels',
                        style: textTheme.bodySmall
                            ?.copyWith(color: game.textMuted),
                      ),
                    ],
                  ),
                ),
                CountdownBadge(
                  deadline: run.deadline,
                  onFinished: onExpired,
                  size: 26,
                ),
              ],
            ),
            const SizedBox(height: Spacing.md),
            CountdownBuilder(
              deadline: run.deadline,
              builder: (context, remaining) => ExcludeSemantics(
                child: AppProgressBar(
                  value: run.totalDuration.inMilliseconds == 0
                      ? 0
                      : remaining.inMilliseconds /
                          run.totalDuration.inMilliseconds,
                  height: 8,
                  glow: true,
                  color: game.streak,
                ),
              ),
            ),
            const SizedBox(height: Spacing.lg),
            AppButton(label: 'Продолжить забег', onPressed: onResume),
          ],
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.all(Spacing.lg),
      decoration: BoxDecoration(
        color: game.keyFace,
        borderRadius: AppRadius.xlAll,
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(card.module.title, style: textTheme.titleMedium),
                Text(
                  details,
                  style: textTheme.bodySmall?.copyWith(color: game.textMuted),
                ),
              ],
            ),
          ),
          const SizedBox(width: Spacing.md),
          AppButton(
            label: card.bestTime == null ? 'Старт' : 'Улучшить',
            icon: card.bestTime == null ? Icons.timer_outlined : null,
            expand: false,
            variant: card.bestTime == null
                ? AppButtonVariant.primary
                : AppButtonVariant.secondary,
            onPressed: onStart,
          ),
        ],
      ),
    );
  }
}
