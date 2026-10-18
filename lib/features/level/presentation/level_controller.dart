import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/di/providers.dart';
import '../../progress/presentation/progress_providers.dart';
import '../../world/presentation/world_controller.dart';
import '../domain/answer.dart';
import '../domain/initial_answer_factory.dart';
import '../domain/level_result.dart';
import '../domain/level_session.dart';
import '../domain/mistake_analysis.dart';
import '../domain/validation_outcome.dart';
import '../engine/level_engine.dart';
import 'level_ui_state.dart';

typedef LevelArgs = ({String courseId, String levelId, LevelMode mode});

final levelControllerProvider = NotifierProvider.autoDispose
    .family<LevelController, LevelUiState, LevelArgs>(LevelController.new);

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
        mode: args.mode,
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
          phase: switch (reason) {
            LevelStartDenial.noLives => LevelPhase.outOfLives,
            LevelStartDenial.noActiveRun => LevelPhase.timeUp,
            _ => LevelPhase.denied,
          },
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
      if (result.timeUp) {
        phase = LevelPhase.timeUp;
      } else if (result.completion != null) {
        phase = LevelPhase.correctAnswer;
      } else if (result.isFailed) {
        phase = LevelPhase.outOfLives;
      } else {
        phase = LevelPhase.wrongAnswer;
      }
      final wrong = !result.outcome.isCorrect && !result.timeUp;
      state = current.copyWith(
        phase: phase,
        session: result.session,
        outcome: result.outcome,
        lives: result.lives,
        result: result.completion,
        isSubmitting: false,
        mistakeNote: wrong
            ? const MistakeAnalyzer().analyze(
                session.level,
                answer,
                result.outcome,
              )
            : null,
        clearMistakeNote: !wrong,
      );
      if (wrong) {
        await _recordMistake(session);
        await _recordWorldMistake(session);
      } else if (result.completion != null) {
        if (session.mode != LevelMode.review) {
          await _rewardWorldForLesson(result.session);
        } else {
          await _recordReview(
            session,
            remembered: result.session.mistakes == 0,
          );
        }
      }
    } catch (error) {
      if (!ref.mounted) return;
      state = LevelUiState(phase: LevelPhase.error, errorMessage: '$error');
    }
  }

  Future<void> _rewardWorldForLesson(LevelSession session) async {
    try {
      await ref
          .read(worldControllerProvider.notifier)
          .recordLessonCompleted(
            moduleId: session.level.moduleId,
            levelId: '${session.level.courseId}:${session.level.id}',
            mistakes: session.mistakes,
          );
    } catch (_) {
      // The meta-game is additive: learning must never fail because of it.
    }
  }

  Future<void> _recordWorldMistake(LevelSession session) async {
    try {
      await ref
          .read(worldControllerProvider.notifier)
          .recordLearningMistake(session.level.moduleId,
            taskKey: 'lesson:${session.level.courseId}:${session.level.id}',
            topicKey: session.level.topicId == null ? null : 'topic:${session.level.courseId}:${session.level.topicId}');
    } catch (_) {
      // Best effort for the same reason as the journal.
    }
  }

  Future<void> onCountdownFinished() async {
    final session = state.session;
    if (session == null || session.mode != LevelMode.timed) return;
    if (state.phase != LevelPhase.playing &&
        state.phase != LevelPhase.wrongAnswer) {
      return;
    }
    final alive = await _engine.isRunAlive(session);
    if (!ref.mounted || alive) return;
    ref.read(progressRevisionProvider.notifier).bump();
    state = state.copyWith(phase: LevelPhase.timeUp);
  }

  Future<void> _recordMistake(LevelSession session) async {
    final topicId = session.level.topicId;
    if (topicId == null) return;
    try {
      await ref
          .read(journalServiceProvider)
          .recordMistake(args.courseId, topicId, session.level.id);
    } catch (_) {
      return;
    }
    if (!ref.mounted) return;
    ref.read(progressRevisionProvider.notifier).bump();
  }

  Future<void> _recordReview(
    LevelSession session, {
    required bool remembered,
  }) async {
    final topicId = session.level.topicId;
    if (topicId == null) return;
    try {
      await ref
          .read(journalServiceProvider)
          .recordReview(args.courseId, topicId, remembered: remembered);
    } catch (_) {
      return;
    }
    if (!ref.mounted) return;
    ref.read(progressRevisionProvider.notifier).bump();
  }

  Future<void> toggleTopicInJournal({required bool save}) async {
    final level = state.session?.level;
    final topicId = level?.topicId;
    if (level == null || topicId == null) return;
    final journal = ref.read(journalServiceProvider);
    if (save) {
      await journal.add(args.courseId, topicId, levelId: level.id);
    } else {
      await journal.remove(args.courseId, topicId);
    }
    if (!ref.mounted) return;
    ref.read(progressRevisionProvider.notifier).bump();
  }

  Future<void> revealSolution() async {
    if (!state.canRevealSolution) return;
    state = state.copyWith(isSolutionRevealed: true);
    await toggleTopicInJournal(save: true);
  }

  void dismissMistake() {
    if (state.phase != LevelPhase.wrongAnswer) return;
    final next = answerAfterMistake(state.answer, state.outcome);
    state = state.copyWith(
      phase: LevelPhase.playing,
      answer: next,
      clearAnswer: next == null,
    );
  }

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

  Future<bool> watchAdForLife() async {
    final granted = await ref.read(economyServiceProvider).watchAdForLife();
    if (!ref.mounted) return granted;
    ref.read(progressRevisionProvider.notifier).bump();
    if (granted) await restart();
    return granted;
  }

  static Answer? answerAfterMistake(
    Answer? answer,
    ValidationOutcome? outcome,
  ) {
    if (outcome == null) return answer;
    switch (answer) {
      case final FillCodeAnswer fill:
        var next = fill;
        for (final index in outcome.wrongParts) {
          next = next.clear(index);
        }
        return next;
      case ChoiceAnswer():
        return null;
      case LineSelectionAnswer(:final lines):
        final kept = lines.difference(outcome.wrongParts);
        return kept.isEmpty ? null : LineSelectionAnswer(kept);
      case OptionSetAnswer(:final options):
        final kept = options.difference(outcome.wrongParts);
        return kept.isEmpty ? null : OptionSetAnswer(kept);
      case MatchAnswer(:final links, :final pairCount):
        return MatchAnswer({
          for (final entry in links.entries)
            if (!outcome.wrongParts.contains(entry.key)) entry.key: entry.value,
        }, pairCount: pairCount);
      case TextAnswer():
      case OrderingAnswer():
      case null:
        return answer;
    }
  }
}
