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
    this.optionFeedback = const [],
  });

  final List<String> options;
  final int correctIndex;

  /// Why each option is wrong (same order as [options]); empty strings or a
  /// shorter list mean "no specific feedback".
  final List<String> optionFeedback;

  String? feedbackFor(int index) => _feedbackAt(optionFeedback, index);
}

/// Pick every correct option.
final class MultiSelectPayload extends LevelPayload {
  const MultiSelectPayload({
    required this.options,
    required this.correctIndexes,
    this.optionFeedback = const [],
  });

  final List<String> options;
  final Set<int> correctIndexes;
  final List<String> optionFeedback;

  String? feedbackFor(int index) => _feedbackAt(optionFeedback, index);
}

/// Fill blanks `{{n}}` in [template] with tokens from [options].
final class FillCodePayload extends LevelPayload {
  const FillCodePayload({
    required this.template,
    required this.options,
    required this.answers,
    this.variantResults = const {},
  });

  final String template;
  final List<String> options;

  /// Expected token for blank `n` is `answers[n]`.
  final List<String> answers;

  /// What the program does with a given combination of tokens, computed by
  /// running it in real Python when the content was built. Keyed by
  /// [variantKey]; e.g. "NameError: name 'x' is not defined" or "7".
  final Map<String, String> variantResults;

  int get blankCount => answers.length;

  static const String keySeparator = '\u0001';

  static String variantKey(List<String?> tokens) =>
      tokens.map((token) => token ?? '').join(keySeparator);
}

/// Type exactly what the program prints.
final class TypeOutputPayload extends LevelPayload {
  const TypeOutputPayload({required this.expectedOutput});

  /// Program output (stdout) without the final newline.
  final String expectedOutput;
}

/// Connect every left item with its right item.
final class MatchPairsPayload extends LevelPayload {
  MatchPairsPayload({required List<MatchPair> pairs})
      : pairs = List.unmodifiable(pairs);

  /// In the canonical order: `pairs[i].left` belongs to `pairs[i].right`.
  final List<MatchPair> pairs;
}

class MatchPair {
  const MatchPair(this.left, this.right);

  final String left;
  final String right;
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

String? _feedbackAt(List<String> feedback, int index) {
  if (index < 0 || index >= feedback.length) return null;
  final text = feedback[index].trim();
  return text.isEmpty ? null : text;
}
