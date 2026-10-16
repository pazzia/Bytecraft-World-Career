import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/di/providers.dart';
import '../../../app/router/routes.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/game_colors.dart';
import '../../../shared/widgets/app_button.dart';
import '../../../shared/widgets/app_card.dart';
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
        padding: const EdgeInsets.all(Spacing.page),
        children: [
          Text(
            'Пройдите модуль целиком, пока не вышло время. Первый забег '
            'даёт ×2 опыта и бонус за скорость.',
            style: Theme.of(context).textTheme.bodyMedium,
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
    final locked = card.availability == TimedModuleAvailability.locked;
    final run = card.activeRun;
    final details = [
      formatClock(card.duration),
      '${card.module.playableLevels.length} уровней',
      if (card.bestTime != null) 'рекорд ${formatClock(card.bestTime!)}',
    ].join(', ');

    return Opacity(
      opacity: locked ? 0.55 : 1,
      child: AppCard(
        borderColor: run != null ? game.streak : null,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Text(card.module.icon, style: const TextStyle(fontSize: 28)),
                const SizedBox(width: Spacing.md),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(card.module.title, style: textTheme.titleMedium),
                      Text(details, style: textTheme.bodySmall),
                    ],
                  ),
                ),
                if (run != null)
                  CountdownBadge(deadline: run.deadline, onFinished: onExpired),
              ],
            ),
            const SizedBox(height: Spacing.md),
            if (locked)
              Text(
                'Откроется, когда пройдёте модуль в обучении',
                style: textTheme.bodySmall,
              )
            else if (run != null)
              AppButton(
                label: 'Продолжить забег',
                variant: AppButtonVariant.danger,
                onPressed: onResume,
              )
            else
              AppButton(
                label: card.bestTime == null ? 'Старт' : 'Улучшить время',
                icon: Icons.timer_outlined,
                onPressed: onStart,
              ),
          ],
        ),
      ),
    );
  }
}
