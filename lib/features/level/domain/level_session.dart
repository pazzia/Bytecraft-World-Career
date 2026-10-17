import '../../courses/domain/level_definition.dart';

enum LevelMode {
  standard,
  dailyChallenge,

  /// Part of a timed module run ("На время").
  timed,

  /// Reviewing a journal topic: plays like a replay, the result moves the
  /// topic between review boxes.
  review,
}

/// In-memory state of one play-through. Immutable: the engine returns an
/// updated copy after every submission.
class LevelSession {
  const LevelSession({
    required this.level,
    required this.mode,
    required this.startedAt,
    this.mistakes = 0,
    this.submissions = 0,
    this.hintsUsed = 0,
    this.isCompleted = false,
    this.isFailed = false,
    this.deadline,
    this.runStartedAt,
  });

  final LevelDefinition level;
  final LevelMode mode;
  final DateTime startedAt;
  final int mistakes;
  final int submissions;
  final int hintsUsed;
  final bool isCompleted;
  final bool isFailed;

  /// Run deadline for [LevelMode.timed] sessions.
  final DateTime? deadline;

  /// When the timed run began (the fuse is measured from it).
  final DateTime? runStartedAt;

  bool get isFinished => isCompleted || isFailed;

  LevelSession copyWith({
    int? mistakes,
    int? submissions,
    int? hintsUsed,
    bool? isCompleted,
    bool? isFailed,
  }) =>
      LevelSession(
        level: level,
        mode: mode,
        startedAt: startedAt,
        mistakes: mistakes ?? this.mistakes,
        submissions: submissions ?? this.submissions,
        hintsUsed: hintsUsed ?? this.hintsUsed,
        isCompleted: isCompleted ?? this.isCompleted,
        isFailed: isFailed ?? this.isFailed,
        deadline: deadline,
        runStartedAt: runStartedAt,
      );
}
