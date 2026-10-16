import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/di/providers.dart';
import '../../progress/presentation/progress_providers.dart';
import '../domain/answer.dart';
import '../domain/initial_answer_factory.dart';
import '../domain/level_result.dart';
import '../domain/level_session.dart';
import '../domain/validation_outcome.dart';
import '../engine/level_engine.dart';
import 'level_ui_state.dart';

typedef LevelArgs = ({String courseId, String levelId, bool isDaily});

final levelControllerProvider = NotifierProvider.autoDispose
    .family<LevelController, LevelUiState, LevelArgs>(LevelController.new);

/// Presentation controller for one level screen. Thin: all rules live in
/// [LevelEngine]; this class maps engine results to [LevelUiState].
class LevelController extends Notifier<LevelUiState> {
  LevelController(this.args);

  final LevelArgs args;

  LevelEngine get _engine => ref.read(levelEngineProvider);

  @override
  LevelUiState build() {
    unawaited(Future.microtask(_start));
    return LevelUiState.loading;
  }

  Future<void> _start() async {
    try {
      final result = await _engine.start(
        courseId: args.courseId,
        levelId: args.levelId,
        mode: args.isDaily ? LevelMode.dailyChallenge : LevelMode.standard,
      );
      if (!ref.mounted) return;
      ref.read(progressRevisionProvider.notifier).bump();
      state = switch (result) {
        LevelStarted(:final session, :final lives) => LevelUiState(
            phase: LevelPhase.playing,
            session: session,
            lives: lives,
            answer: const InitialAnswerFactory().initialFor(
              session.level,
              seed: session.startedAt.millisecondsSinceEpoch,
            ),
          ),
        LevelStartDenied(:final reason, :final lives) => LevelUiState(
            phase: reason == LevelStartDenial.noLives
                ? LevelPhase.outOfLives
                : LevelPhase.denied,
            denial: reason,
            lives: lives,
          ),
      };
    } catch (error) {
      if (!ref.mounted) return;
      state = LevelUiState(phase: LevelPhase.error, errorMessage: '$error');
    }
  }

  void updateAnswer(Answer answer) {
    if (state.isInputLocked) return;
    state = state.copyWith(answer: answer, clearOutcome: true);
  }

  Future<void> submit() async {
    final current = state;
    final session = current.session;
    final answer = current.answer;
    if (!current.canSubmit || session == null || answer == null) return;
    state = current.copyWith(isSubmitting: true);
    try {
      final result = await _engine.submit(session, answer);
      if (!ref.mounted) return;
      ref.read(progressRevisionProvider.notifier).bump();
      final LevelPhase phase;
      if (result.completion != null) {
        phase = LevelPhase.correctAnswer;
      } else if (result.isFailed) {
        phase = LevelPhase.outOfLives;
      } else {
        phase = LevelPhase.wrongAnswer;
      }
      state = current.copyWith(
        phase: phase,
        session: result.session,
        outcome: result.outcome,
        lives: result.lives,
        result: result.completion,
        isSubmitting: false,
      );
    } catch (error) {
      if (!ref.mounted) return;
      state = LevelUiState(phase: LevelPhase.error, errorMessage: '$error');
    }
  }

  /// Closes the wrong-answer feedback and lets the player try again.
  void dismissMistake() {
    if (state.phase != LevelPhase.wrongAnswer) return;
    state = state.copyWith(
      phase: LevelPhase.playing,
      answer: _answerAfterMistake(state.answer, state.outcome),
    );
  }

  /// Moves from the "Correct!" panel to the rewards screen.
  void showRewards() {
    if (state.phase != LevelPhase.correctAnswer) return;
    state = state.copyWith(phase: LevelPhase.completed);
  }

  void showHint() {
    final session = state.session;
    if (session == null || state.isHintVisible) return;
    state = state.copyWith(
      session: _engine.useHint(session),
      isHintVisible: true,
    );
  }

  Future<void> restart() async {
    state = LevelUiState.loading;
    await _start();
  }

  /// Rewarded ad → +1 life, then restart the level.
  Future<bool> watchAdForLife() async {
    final granted = await ref.read(economyServiceProvider).watchAdForLife();
    if (!ref.mounted) return granted;
    ref.read(progressRevisionProvider.notifier).bump();
    if (granted) await restart();
    return granted;
  }

  /// Keeps correct parts, clears wrong blanks so the retry is quick.
  static Answer? _answerAfterMistake(
    Answer? answer,
    ValidationOutcome? outcome,
  ) {
    if (answer is FillCodeAnswer && outcome != null) {
      var next = answer;
      for (final index in outcome.wrongParts) {
        next = next.clear(index);
      }
      return next;
    }
    return answer;
  }
}
