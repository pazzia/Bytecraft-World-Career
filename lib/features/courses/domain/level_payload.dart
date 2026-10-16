/// Type-specific data of a level. Each [LevelType] has its own payload;
/// new mechanics add a new subclass + parser + validator + renderer.
sealed class LevelPayload {
  const LevelPayload();
}

/// Pick one option. Also used for "predict output" style questions.
final class MultipleChoicePayload extends LevelPayload {
  const MultipleChoicePayload({
    required this.options,
    required this.correctIndex,
  });

  final List<String> options;
  final int correctIndex;
}

/// Fill blanks `{{n}}` in [template] with tokens from [options].
final class FillCodePayload extends LevelPayload {
  const FillCodePayload({
    required this.template,
    required this.options,
    required this.answers,
  });

  final String template;
  final List<String> options;

  /// Expected token for blank `n` is `answers[n]`.
  final List<String> answers;

  int get blankCount => answers.length;
}

/// Put code lines in a working order.
final class CodeOrderingPayload extends LevelPayload {
  const CodeOrderingPayload({
    required this.lines,
    this.alternativeOrders = const [],
  });

  /// Lines in the canonical correct order. Line identity = index here.
  final List<String> lines;

  /// Other accepted orders (e.g. independent assignments may be swapped),
  /// expressed as permutations of canonical indexes.
  final List<List<int>> alternativeOrders;
}

/// Tap the line(s) that contain a bug. Lines come from the level code.
final class BugFinderPayload extends LevelPayload {
  const BugFinderPayload({required this.buggyLines});

  /// Zero-based line indexes in `LevelDefinition.code`.
  final Set<int> buggyLines;
}

/// Content this client can't play: unknown type or invalid data.
final class UnsupportedPayload extends LevelPayload {
  const UnsupportedPayload({required this.reason});

  final String reason;
}
