import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/di/providers.dart';
import '../../../app/router/routes.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/theme/game_colors.dart';
import '../../../services/analytics/analytics_service.dart';
import '../../../services/feature_flags/feature_flag_service.dart';
import '../../../shared/widgets/app_button.dart';
import '../../../shared/widgets/app_progress_bar.dart';
import '../../../shared/widgets/async_value_view.dart';
import '../../../shared/widgets/code_block.dart';
import '../../../shared/widgets/keycap.dart';
import '../../../shared/widgets/stat_badges.dart';
import '../../timed_run/domain/timed_run_service.dart';
import '../../timed_run/presentation/countdown.dart';
import '../../timed_run/presentation/time_up_view.dart';
import '../domain/level_result.dart';
import '../domain/level_session.dart';
import '../renderers/question_renderer.dart';
import 'level_controller.dart';
import 'level_position.dart';
import 'level_ui_state.dart';
import 'widgets/feedback_panel.dart';
import 'widgets/level_complete_view.dart';
import 'widgets/out_of_lives_view.dart';

final questionRendererRegistryProvider = Provider<QuestionRendererRegistry>(
  (ref) => QuestionRendererRegistry.standard,
);

/// Hosts any level type. The concrete UI comes from the renderer registry.
/// Timed-run levels use the night palette.
class LevelScreen extends ConsumerWidget {
  const LevelScreen({super.key, required this.args});

  final LevelArgs args;

  bool get _isTimed => args.mode == LevelMode.timed;

  void _exit(BuildContext context) {
    if (context.canPop()) {
      context.pop();
    } else {
      context.go(Routes.map);
    }
  }

  void _openPremium(BuildContext context, WidgetRef ref) {
    ref.read(analyticsProvider).track(
      AnalyticsEvent.premiumScreenOpened,
      {'source': 'out_of_lives'},
    );
    context.push(Routes.premium);
  }

  /// Starts a new run of the same module and opens its first level.
  Future<void> _restartRun(BuildContext context, WidgetRef ref) async {
    final course =
        await ref.read(contentRepositoryProvider).loadCourse(args.courseId);
    final moduleId = course.levelById(args.levelId)?.moduleId;
    if (moduleId == null) return;
    final result =
        await ref.read(timedRunServiceProvider).startRun(args.courseId, moduleId);
    if (!context.mounted) return;
    switch (result) {
      case RunStarted(:final firstLevel) when firstLevel.id == args.levelId:
        // Same route arguments: a replacement route would reuse this
        // screen's (time-up) controller, so restart it in place.
        await ref.read(levelControllerProvider(args).notifier).restart();
      case RunStarted(:final firstLevel):
        context.pushReplacement(
          Routes.level(args.courseId, firstLevel.id, mode: LevelMode.timed),
        );
      case RunDenied():
        context.go(Routes.map);
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final provider = levelControllerProvider(args);
    final state = ref.watch(provider);
    final controller = ref.read(provider.notifier);

    final Widget body = switch (state.phase) {
      LevelPhase.loading => const Center(child: CircularProgressIndicator()),
      LevelPhase.error => ErrorView(
          message: state.errorMessage ?? '',
          onRetry: controller.restart,
        ),
      LevelPhase.denied => _DeniedView(
          reason: state.denial,
          onExit: () => _exit(context),
        ),
      LevelPhase.outOfLives => OutOfLivesView(
          lives: state.lives,
          onExit: () => _exit(context),
          onPremium: () => _openPremium(context, ref),
          onWatchAd: ref.read(featureFlagsProvider).isEnabled(FeatureFlag.ads)
              ? controller.watchAdForLife
              : null,
        ),
      LevelPhase.timeUp => TimeUpView(
          onRestart: () => _restartRun(context, ref),
          onExit: () => context.go(Routes.map),
        ),
      LevelPhase.completed => LevelCompleteView(
          result: state.result!,
          onContinue: state.result!.nextLevelId == null
              ? null
              : () => context.pushReplacement(
                    Routes.level(
                      args.courseId,
                      state.result!.nextLevelId!,
                      mode: _isTimed ? LevelMode.timed : LevelMode.standard,
                    ),
                  ),
          onBackToMap: () => context.go(Routes.map),
        ),
      LevelPhase.playing ||
      LevelPhase.wrongAnswer ||
      LevelPhase.correctAnswer =>
        _PlayingView(
          args: args,
          state: state,
          controller: controller,
          renderers: ref.watch(questionRendererRegistryProvider),
          onClose: () => _exit(context),
        ),
    };

    final scaffold = Scaffold(body: body);
    return _isTimed ? Theme(data: AppTheme.timed, child: scaffold) : scaffold;
  }
}

class _PlayingView extends ConsumerWidget {
  const _PlayingView({
    required this.args,
    required this.state,
    required this.controller,
    required this.renderers,
    required this.onClose,
  });

  final LevelArgs args;
  final LevelUiState state;
  final LevelController controller;
  final QuestionRendererRegistry renderers;
  final VoidCallback onClose;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final session = state.session!;
    final level = session.level;
    final renderer = renderers.resolve(level.type);
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    final lives = state.lives;
    final position =
        ref.watch(levelPositionProvider((args.courseId, args.levelId))).value;
    final deadline = session.deadline;

    return Column(
      children: [
        if (deadline != null)
          _FuseBar(
            startedAt: session.runStartedAt ?? session.startedAt,
            deadline: deadline,
          ),
        SafeArea(
          bottom: false,
          top: deadline == null,
          child: Padding(
            padding: const EdgeInsets.fromLTRB(
              Spacing.sm,
              Spacing.md,
              Spacing.page,
              0,
            ),
            child: Row(
              children: [
                IconButton(
                  tooltip: 'Закрыть уровень',
                  iconSize: 26,
                  color: game.textMuted,
                  icon: const Icon(Icons.close_rounded),
                  onPressed: onClose,
                ),
                const SizedBox(width: Spacing.xs),
                Expanded(
                  child: position == null
                      ? const SizedBox.shrink()
                      : SegmentedProgress(
                          height: 8,
                          semanticLabel:
                              'Уровень ${position.index + 1} из ${position.count}',
                          segments: [
                            for (var i = 0; i < position.count; i++)
                              i < position.index
                                  ? SegmentState.done
                                  : i == position.index
                                      ? SegmentState.current
                                      : SegmentState.todo,
                          ],
                        ),
                ),
                const SizedBox(width: Spacing.md),
                if (deadline != null) ...[
                  CountdownBadge(
                    deadline: deadline,
                    onFinished: controller.onCountdownFinished,
                  ),
                  const SizedBox(width: Spacing.md),
                ],
                if (lives != null)
                  LivesBadge(
                    current: lives.current,
                    isUnlimited: lives.isUnlimited,
                  ),
              ],
            ),
          ),
        ),
        Expanded(
          child: ListView(
            padding: const EdgeInsets.fromLTRB(
              Spacing.page,
              Spacing.lg,
              Spacing.page,
              Spacing.xxl,
            ),
            children: [
              Text(level.prompt, style: textTheme.headlineSmall),
              const SizedBox(height: Spacing.xl),
              if (renderer.showsLevelCode && level.code != null) ...[
                CodeBlock(code: level.code!),
                const SizedBox(height: Spacing.xl),
              ],
              renderer.build(
                context,
                QuestionContext(
                  level: level,
                  answer: state.answer,
                  onChanged: controller.updateAnswer,
                  isLocked: state.isInputLocked,
                  outcome: state.outcome,
                ),
              ),
              if (state.isHintVisible && level.hint != null) ...[
                const SizedBox(height: Spacing.xl),
                _HintCard(text: level.hint!),
              ],
            ],
          ),
        ),
        _BottomBar(state: state, controller: controller),
      ],
    );
  }
}

/// The timed run's fuse: burns down across the top of the screen.
class _FuseBar extends StatelessWidget {
  const _FuseBar({required this.startedAt, required this.deadline});

  final DateTime startedAt;
  final DateTime deadline;

  @override
  Widget build(BuildContext context) => SafeArea(
        bottom: false,
        child: CountdownBuilder(
          deadline: deadline,
          builder: (context, remaining) {
            final total = deadline.difference(startedAt).inMilliseconds;
            final share = total <= 0 ? 0.0 : remaining.inMilliseconds / total;
            return ExcludeSemantics(
              child: AppProgressBar(
                value: share,
                height: 6,
                glow: true,
                color: context.gameColors.streak,
              ),
            );
          },
        ),
      );
}

class _BottomBar extends StatelessWidget {
  const _BottomBar({required this.state, required this.controller});

  final LevelUiState state;
  final LevelController controller;

  @override
  Widget build(BuildContext context) {
    final level = state.session!.level;
    final game = context.gameColors;
    switch (state.phase) {
      case LevelPhase.wrongAnswer:
        return FeedbackPanel(
          isCorrect: false,
          message: level.hint,
          buttonLabel: 'Ещё раз',
          livesLeft: state.lives?.isUnlimited == false
              ? state.lives?.current
              : null,
          onPressed: controller.dismissMistake,
        );
      case LevelPhase.correctAnswer:
        return FeedbackPanel(
          isCorrect: true,
          message: level.explanation,
          buttonLabel: 'Продолжить',
          onPressed: controller.showRewards,
        );
      case LevelPhase.loading:
      case LevelPhase.playing:
      case LevelPhase.completed:
      case LevelPhase.outOfLives:
      case LevelPhase.timeUp:
      case LevelPhase.denied:
      case LevelPhase.error:
        return SafeArea(
          top: false,
          child: Padding(
            padding: const EdgeInsets.fromLTRB(
              Spacing.page,
              Spacing.sm,
              Spacing.page,
              Spacing.lg,
            ),
            child: Row(
              children: [
                if (level.hint != null && !state.isHintVisible) ...[
                  Keycap(
                    onTap: controller.showHint,
                    face: game.keyFace,
                    edge: game.keyEdge,
                    border: game.keyBorder,
                    width: Spacing.keyHeight,
                    height: Spacing.keyHeight,
                    semanticLabel: 'Подсказка',
                    child: Icon(
                      Icons.lightbulb_outline_rounded,
                      color: game.rewardIcon,
                    ),
                  ),
                  const SizedBox(width: Spacing.md),
                ],
                Expanded(
                  child: AppButton(
                    label: 'Проверить',
                    isLoading: state.isSubmitting,
                    onPressed: state.canSubmit ? controller.submit : null,
                  ),
                ),
              ],
            ),
          ),
        );
    }
  }
}

class _HintCard extends StatelessWidget {
  const _HintCard({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    return Container(
      padding: const EdgeInsets.all(Spacing.lg),
      decoration: BoxDecoration(
        color: game.primaryTint,
        borderRadius: AppRadius.lgAll,
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.lightbulb_rounded, color: game.rewardIcon),
          const SizedBox(width: Spacing.md),
          Expanded(
            child: Text(text, style: Theme.of(context).textTheme.bodyLarge),
          ),
        ],
      ),
    );
  }
}

class _DeniedView extends StatelessWidget {
  const _DeniedView({required this.reason, required this.onExit});

  final LevelStartDenial? reason;
  final VoidCallback onExit;

  String get _message => switch (reason) {
        LevelStartDenial.locked => 'Сначала пройдите предыдущие уровни',
        LevelStartDenial.unsupported =>
          'Обновите приложение, чтобы открыть этот уровень',
        LevelStartDenial.notFound => 'Уровень не найден',
        LevelStartDenial.noLives => 'Жизни закончились',
        LevelStartDenial.noActiveRun =>
          'Забег закончился. Начните его заново на карте',
        null => 'Уровень недоступен',
      };

  @override
  Widget build(BuildContext context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(Spacing.page),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Icon(
                Icons.lock_rounded,
                size: 56,
                color: context.gameColors.lockedIcon,
              ),
              const SizedBox(height: Spacing.lg),
              Text(
                _message,
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: Spacing.xxl),
              AppButton(label: 'Назад', onPressed: onExit),
            ],
          ),
        ),
      );
}
