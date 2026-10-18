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
/// Trace table: the program runs step by step; the player fills the
/// values the variables have after the marked lines.
final class TraceTablePayload extends LevelPayload {
  TraceTablePayload({
    required List<String> columns,
    required List<TraceRow> rows,
    required List<TraceCell> blanks,
    required List<String> bank,
  })  : columns = List.unmodifiable(columns),
        rows = List.unmodifiable(rows),
        blanks = List.unmodifiable(blanks),
        bank = List.unmodifiable(bank);

  /// Variable names (table header).
  final List<String> columns;

  /// One row per step: values as Python shows them (repr), after [TraceRow.line].
  final List<TraceRow> rows;

  /// Cells the player fills, in answer-slot order.
  final List<TraceCell> blanks;

  /// Values to choose from (all right answers plus look-alikes).
  final List<String> bank;

  String answerFor(int slot) {
    final cell = blanks[slot];
    return rows[cell.row].values[cell.column];
  }

  /// Slot of a cell, or null when the cell is given.
  int? slotOf(int row, int column) {
    for (var i = 0; i < blanks.length; i++) {
      if (blanks[i].row == row && blanks[i].column == column) return i;
    }
    return null;
  }
}

class TraceRow {
  TraceRow({required this.line, required List<String> values})
      : values = List.unmodifiable(values);

  /// 1-based line number of the program after which the values are taken.
  final int line;
  final List<String> values;
}

class TraceCell {
  const TraceCell(this.row, this.column);

  final int row;
  final int column;
}

/// Sort items into groups ("mutable / immutable", "true / false"...).
final class CategorizePayload extends LevelPayload {
  CategorizePayload({required List<String> categories, required List<CategorizeItem> items})
      : categories = List.unmodifiable(categories),
        items = List.unmodifiable(items);

  final List<String> categories;
  final List<CategorizeItem> items;
}

class CategorizeItem {
  const CategorizeItem({
    required this.text,
    required this.category,
    this.isCode = false,
    this.feedback,
  });

  final String text;

  /// Index into [CategorizePayload.categories].
  final int category;

  /// Show as code (monospace) rather than a sentence.
  final bool isCode;

  /// Why this item belongs to its group (shown after a mistake).
  final String? feedback;
}

/// The bug's line is known; the player types the corrected line.
final class FixLinePayload extends LevelPayload {
  FixLinePayload({
    required this.line,
    required List<String> accepted,
    required this.expectedOutput,
  }) : accepted = List.unmodifiable(accepted);

  /// 0-based index of the broken line in `level.code`.
  final int line;

  /// Corrected lines verified by running them (compared after
  /// [FixLineText.normalize]).
  final List<String> accepted;

  /// What the corrected program prints.
  final String expectedOutput;
}

/// Lenient comparison of typed code: spacing and quote style don't matter.
abstract final class FixLineText {
  static String normalize(String line) {
    final buffer = StringBuffer();
    String? quote;
    final text = line.trim().replaceAll('\u2019', "'").replaceAll('\u2018', "'")
        .replaceAll('\u201c', '"').replaceAll('\u201d', '"').replaceAll('\u00ab', '"')
        .replaceAll('\u00bb', '"');
    for (var i = 0; i < text.length; i++) {
      final char = text[i];
      if (quote != null) {
        buffer.write(char == quote ? '"' : char);
        if (char == quote) quote = null;
        continue;
      }
      if (char == '"' || char == "'") {
        quote = char;
        buffer.write('"');
        continue;
      }
      if (char == ' ' || char == '\t') continue;
      buffer.write(char);
    }
    return buffer.toString();
  }

  /// Indentation of [line] (to keep the typed line inside its block).
  static String indentOf(String line) => line.substring(0, line.length - line.trimLeft().length);
}

final class UnsupportedPayload extends LevelPayload {
  const UnsupportedPayload({required this.reason});

  final String reason;
}

String? _feedbackAt(List<String> feedback, int index) {
  if (index < 0 || index >= feedback.length) return null;
  final text = feedback[index].trim();
  return text.isEmpty ? null : text;
}
