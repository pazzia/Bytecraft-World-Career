import '../domain/answer.dart';
import '../domain/level_result.dart';
import '../domain/level_session.dart';
import '../domain/mistake_analysis.dart';
import '../domain/validation_outcome.dart';

enum LevelPhase {
  loading,

  /// Player is composing an answer.
  playing,

  /// Answer was wrong; feedback panel is shown.
  wrongAnswer,

  /// Answer was right; feedback with explanation is shown.
  correctAnswer,

  /// Rewards screen.
  completed,

  /// No lives left (at start or mid-level).
  outOfLives,

  /// The timed run's deadline passed.
  timeUp,

  /// Level can't be opened (locked, unsupported, not found).
  denied,
  error,
}

/// Screen state of the level flow (UI state; domain state lives in
/// [LevelSession], persisted state in repositories).
class LevelUiState {
  const LevelUiState({
    required this.phase,
    this.session,
    this.answer,
    this.outcome,
    this.lives,
    this.result,
    this.denial,
    this.errorMessage,
    this.isSubmitting = false,
    this.isHintVisible = false,
    this.mistakeNote,
    this.isSolutionRevealed = false,
  });

  /// After this many mistakes on one level the player may open the solution.
  static const int mistakesBeforeSolution = 3;

  static const LevelUiState loading = LevelUiState(phase: LevelPhase.loading);

  final LevelPhase phase;
  final LevelSession? session;
  final Answer? answer;
  final ValidationOutcome? outcome;
  final LivesSnapshot? lives;
  final LevelResult? result;
  final LevelStartDenial? denial;
  final String? errorMessage;
  final bool isSubmitting;
  final bool isHintVisible;

  /// Short analysis of the last wrong answer.
  final MistakeNote? mistakeNote;

  /// The player gave up and looked at the solution.
  final bool isSolutionRevealed;

  bool get canRevealSolution =>
      !isSolutionRevealed &&
      (session?.mistakes ?? 0) >= mistakesBeforeSolution &&
      session?.level.solution != null;

  bool get canSubmit =>
      phase == LevelPhase.playing &&
      !isSubmitting &&
      (answer?.isComplete ?? false);

  /// Inputs are frozen while feedback is shown or after completion.
  bool get isInputLocked =>
      phase != LevelPhase.playing || isSubmitting;

  LevelUiState copyWith({
    LevelPhase? phase,
    LevelSession? session,
    Answer? answer,
    ValidationOutcome? outcome,
    LivesSnapshot? lives,
    LevelResult? result,
    bool? isSubmitting,
    bool? isHintVisible,
    MistakeNote? mistakeNote,
    bool? isSolutionRevealed,
    bool clearOutcome = false,
    bool clearAnswer = false,
    bool clearMistakeNote = false,
  }) =>
      LevelUiState(
        phase: phase ?? this.phase,
        session: session ?? this.session,
        answer: clearAnswer ? null : answer ?? this.answer,
        outcome: clearOutcome ? null : outcome ?? this.outcome,
        lives: lives ?? this.lives,
        result: result ?? this.result,
        denial: denial,
        errorMessage: errorMessage,
        isSubmitting: isSubmitting ?? this.isSubmitting,
        isHintVisible: isHintVisible ?? this.isHintVisible,
        mistakeNote:
            clearMistakeNote ? null : mistakeNote ?? this.mistakeNote,
        isSolutionRevealed: isSolutionRevealed ?? this.isSolutionRevealed,
      );
}
