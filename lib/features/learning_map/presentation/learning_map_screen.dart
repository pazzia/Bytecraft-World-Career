import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/di/providers.dart';
import '../../../app/router/routes.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/game_colors.dart';
import '../../../services/feature_flags/feature_flag_service.dart';
import '../../../shared/widgets/async_value_view.dart';
import '../../../shared/widgets/segmented_switch.dart';
import '../../progress/presentation/progress_providers.dart';
import '../../timed_run/presentation/timed_runs_view.dart';
import '../domain/learning_map_model.dart';
import 'learning_map_providers.dart';
import 'widgets/map_node.dart';

class LearningMapScreen extends ConsumerWidget {
  const LearningMapScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final timedEnabled =
        ref.watch(featureFlagsProvider).isEnabled(FeatureFlag.timedRuns);
    final mode = timedEnabled ? ref.watch(mapModeProvider) : MapMode.learn;
    final course = ref.watch(activeCourseProvider).value;
    final textTheme = Theme.of(context).textTheme;
    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(
                Spacing.page,
                Spacing.xxl,
                Spacing.page,
                Spacing.md,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(course?.title ?? '', style: textTheme.headlineMedium),
                  if (timedEnabled) ...[
                    const SizedBox(height: Spacing.md),
                    SegmentedSwitch<MapMode>(
                      semanticLabel: 'Режим карты',
                      selected: mode,
                      onChanged: ref.read(mapModeProvider.notifier).select,
                      options: const [
                        SegmentOption(MapMode.learn, 'Обучение'),
                        SegmentOption(MapMode.timed, 'На время'),
                      ],
                    ),
                  ],
                ],
              ),
            ),
            Expanded(
              child: mode == MapMode.timed
                  ? const TimedRunsView()
                  : const _LearnPath(),
            ),
          ],
        ),
      ),
    );
  }
}

class _LearnPath extends ConsumerStatefulWidget {
  const _LearnPath();

  @override
  ConsumerState<_LearnPath> createState() => _LearnPathState();
}

class _LearnPathState extends ConsumerState<_LearnPath> {
  final GlobalKey _currentKey = GlobalKey();
  bool _scrolledToCurrent = false;

  void _open(LearningMapModel model, MapNode node) {
    if (!node.isPlayable) {
      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(
          const SnackBar(content: Text('Сначала пройдите предыдущие уровни')),
        );
      return;
    }
    context.push(Routes.level(model.course.id, node.level.id));
  }

  /// Opens the map at the player's current level, not at the top.
  void _scrollToCurrentOnce() {
    if (_scrolledToCurrent) return;
    _scrolledToCurrent = true;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final target = _currentKey.currentContext;
      if (target != null && target.mounted) {
        Scrollable.ensureVisible(target, alignment: 0.3);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final map = ref.watch(learningMapProvider);
    return AsyncValueView<LearningMapModel>(
      value: map,
      onRetry: () => ref.invalidate(learningMapProvider),
      data: (model) {
        _scrollToCurrentOnce();
        return ListView(
          padding: const EdgeInsets.fromLTRB(
            Spacing.page,
            0,
            Spacing.page,
            Spacing.huge,
          ),
          children: [
            for (final section in model.sections) ...[
              _ModuleHeader(section: section),
              for (final node in section.nodes)
                MapNodeTile(
                  key: node.state == MapNodeState.current
                      ? _currentKey
                      : ValueKey(node.level.id),
                  node: node,
                  onTap: () => _open(model, node),
                ),
            ],
          ],
        );
      },
    );
  }
}

class _ModuleHeader extends StatelessWidget {
  const _ModuleHeader({required this.section});

  final MapSection section;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    final done = section.total > 0 && section.completed == section.total;
    return Semantics(
      header: true,
      child: Padding(
        padding: const EdgeInsets.only(top: Spacing.xl, bottom: Spacing.sm),
        child: Row(
          children: [
            Text(
              section.module.title,
              style: textTheme.titleMedium?.copyWith(
                fontSize: 18,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(width: Spacing.md),
            Expanded(child: Container(height: 2, color: game.keyBorder)),
            const SizedBox(width: Spacing.md),
            Text(
              '${section.completed} из ${section.total}',
              style: textTheme.labelMedium?.copyWith(
                color: done ? game.success : game.textMuted,
                fontWeight: FontWeight.w700,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
