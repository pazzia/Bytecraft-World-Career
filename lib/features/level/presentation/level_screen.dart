import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/di/providers.dart';
import '../../../app/router/routes.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../services/analytics/analytics_service.dart';
import '../../../services/feature_flags/feature_flag_service.dart';
import '../../../shared/widgets/app_button.dart';
import '../../../shared/widgets/async_value_view.dart';
import '../../../shared/widgets/code_block.dart';
import '../../../shared/widgets/stat_badges.dart';
import '../../courses/domain/level_type.dart';
import '../domain/level_result.dart';
import '../renderers/question_renderer.dart';
import 'level_controller.dart';
import 'level_ui_state.dart';
import 'widgets/feedback_panel.dart';
import 'widgets/level_complete_view.dart';
import 'widgets/out_of_lives_view.dart';

final questionRendererRegistryProvider = Provider<QuestionRendererRegistry>(
  (ref) => QuestionRendererRegistry.standard,
);

/// Hosts any level type. The concrete UI comes from the renderer registry.
class LevelScreen extends ConsumerWidget {
  const LevelScreen({super.key, required this.args});

  final LevelArgs args;

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
      LevelPhase.completed => LevelCompleteView(
          result: state.result!,
          onContinue: state.result!.nextLevelId == null
              ? null
              : () => context.pushReplacement(
                    Routes.level(args.courseId, state.result!.nextLevelId!),
                  ),
          onBackToMap: () => context.go(Routes.map),
        ),
      LevelPhase.playing ||
      LevelPhase.wrongAnswer ||
      LevelPhase.correctAnswer =>
        _PlayingView(
          state: state,
          controller: controller,
          renderers: ref.watch(questionRendererRegistryProvider),
          onClose: () => _exit(context),
        ),
    };

    return Scaffold(body: body);
  }
}

class _PlayingView extends StatelessWidget {
  const _PlayingView({
    required this.state,
    required this.controller,
    required this.renderers,
    required this.onClose,
  });

  final LevelUiState state;
  final LevelController controller;
  final QuestionRendererRegistry renderers;
  final VoidCallback onClose;

  @override
  Widget build(BuildContext context) {
    final session = state.session!;
    final level = session.level;
    final renderer = renderers.resolve(level.type);
    final textTheme = Theme.of(context).textTheme;
    final lives = state.lives;

    return Column(
      children: [
        SafeArea(
          bottom: false,
          child: Padding(
            padding: const EdgeInsets.fromLTRB(
              Spacing.sm,
              Spacing.sm,
              Spacing.page,
              0,
            ),
            child: Row(
              children: [
                IconButton(
                  tooltip: 'Закрыть',
                  icon: const Icon(Icons.close_rounded),
                  onPressed: onClose,
                ),
                Expanded(
                  child: Text(
                    level.title,
                    style: textTheme.titleMedium,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                if (level.role == LevelRole.boss)
                  const Padding(
                    padding: EdgeInsets.only(right: Spacing.sm),
                    child: Text('👑', style: TextStyle(fontSize: 20)),
                  ),
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
            padding: const EdgeInsets.all(Spacing.page),
            children: [
              Text(level.prompt, style: textTheme.titleLarge),
              const SizedBox(height: Spacing.lg),
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
                const SizedBox(height: Spacing.lg),
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

class _BottomBar extends StatelessWidget {
  const _BottomBar({required this.state, required this.controller});

  final LevelUiState state;
  final LevelController controller;

  @override
  Widget build(BuildContext context) {
    final level = state.session!.level;
    switch (state.phase) {
      case LevelPhase.wrongAnswer:
        return FeedbackPanel(
          isCorrect: false,
          message: level.hint,
          buttonLabel: 'Попробовать ещё',
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
                  SizedBox(
                    width: Spacing.touchTarget,
                    height: Spacing.touchTarget,
                    child: IconButton.filledTonal(
                      tooltip: 'Подсказка',
                      icon: const Icon(Icons.lightbulb_outline_rounded),
                      onPressed: controller.showHint,
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
    final scheme = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.all(Spacing.lg),
      decoration: BoxDecoration(
        color: scheme.secondary.withValues(alpha: 0.12),
        borderRadius: AppRadius.lgAll,
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('💡', style: TextStyle(fontSize: 22)),
          const SizedBox(width: Spacing.md),
          Expanded(child: Text(text)),
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
        LevelStartDenial.locked => 'Сначала пройдите предыдущие уровни 🔒',
        LevelStartDenial.unsupported =>
          'Обновите приложение, чтобы открыть этот уровень',
        LevelStartDenial.notFound => 'Уровень не найден',
        LevelStartDenial.noLives => 'Жизни закончились',
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
              Text(
                _message,
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: Spacing.xl),
              AppButton(label: 'Назад', onPressed: onExit),
            ],
          ),
        ),
      );
}
