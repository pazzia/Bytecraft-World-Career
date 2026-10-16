/// Result of checking an answer.
///
/// [wrongParts] carries type-specific detail for feedback highlighting:
/// blank indexes for fill-code, positions for ordering, line indexes for
/// bug finder, the chosen option for multiple choice.
class ValidationOutcome {
  const ValidationOutcome._({required this.isCorrect, required this.wrongParts});

  static const ValidationOutcome correct =
      ValidationOutcome._(isCorrect: true, wrongParts: <int>{});

  factory ValidationOutcome.incorrect([Set<int> wrongParts = const <int>{}]) =>
      ValidationOutcome._(
        isCorrect: false,
        wrongParts: Set.unmodifiable(wrongParts),
      );

  final bool isCorrect;
  final Set<int> wrongParts;
}
