/// Result of checking an answer.
///
/// [wrongParts] carries type-specific detail for feedback highlighting:
/// blank indexes for fill-code, positions for ordering, line indexes for
/// bug finder, the chosen option for multiple choice, falsely picked options
/// for multi-select, left items for match pairs, output lines for
/// type-output. [missedParts] lists what the player should have picked but
/// didn't (multi-select, bug finder).
class ValidationOutcome {
  const ValidationOutcome._({
    required this.isCorrect,
    required this.wrongParts,
    required this.missedParts,
  });

  static const ValidationOutcome correct = ValidationOutcome._(
    isCorrect: true,
    wrongParts: <int>{},
    missedParts: <int>{},
  );

  factory ValidationOutcome.incorrect([
    Set<int> wrongParts = const <int>{},
    Set<int> missedParts = const <int>{},
  ]) =>
      ValidationOutcome._(
        isCorrect: false,
        wrongParts: Set.unmodifiable(wrongParts),
        missedParts: Set.unmodifiable(missedParts),
      );

  final bool isCorrect;
  final Set<int> wrongParts;
  final Set<int> missedParts;
}
