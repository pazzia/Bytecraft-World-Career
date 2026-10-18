/// Player's answer. One subtype per interaction shape; several level types
/// may share a shape (e.g. multiple choice and predict output).
sealed class Answer {
  const Answer();

  /// Whether the answer can be submitted (all blanks filled, etc.).
  bool get isComplete;
}

final class ChoiceAnswer extends Answer {
  const ChoiceAnswer(this.optionIndex);

  final int optionIndex;

  @override
  bool get isComplete => true;

  @override
  bool operator ==(Object other) =>
      other is ChoiceAnswer && other.optionIndex == optionIndex;

  @override
  int get hashCode => optionIndex.hashCode;
}

final class FillCodeAnswer extends Answer {
  FillCodeAnswer(List<String?> tokens) : tokens = List.unmodifiable(tokens);

  factory FillCodeAnswer.empty(int blanks) =>
      FillCodeAnswer(List<String?>.filled(blanks, null));

  /// Token chosen for each blank, null when the blank is empty.
  final List<String?> tokens;

  @override
  bool get isComplete => tokens.every((token) => token != null);

  /// Places [token] into the first empty blank (no-op when all are filled).
  FillCodeAnswer place(String token) {
    final index = tokens.indexOf(null);
    if (index < 0) return this;
    final next = [...tokens];
    next[index] = token;
    return FillCodeAnswer(next);
  }

  FillCodeAnswer clear(int blankIndex) {
    if (blankIndex < 0 || blankIndex >= tokens.length) return this;
    final next = [...tokens];
    next[blankIndex] = null;
    return FillCodeAnswer(next);
  }
}

final class OrderingAnswer extends Answer {
  OrderingAnswer(List<int> order) : order = List.unmodifiable(order);

  /// Canonical line indexes in the order the player arranged them.
  final List<int> order;

  @override
  bool get isComplete => order.isNotEmpty;

  /// Moves the item at [from] so that it ends up at position [to].
  OrderingAnswer move(int from, int to) {
    if (from == to ||
        from < 0 ||
        to < 0 ||
        from >= order.length ||
        to >= order.length) {
      return this;
    }
    final next = [...order];
    final item = next.removeAt(from);
    next.insert(to, item);
    return OrderingAnswer(next);
  }
}

final class LineSelectionAnswer extends Answer {
  LineSelectionAnswer(Set<int> lines) : lines = Set.unmodifiable(lines);

  final Set<int> lines;

  @override
  bool get isComplete => lines.isNotEmpty;

  LineSelectionAnswer toggle(int line) => LineSelectionAnswer(
        lines.contains(line) ? ({...lines}..remove(line)) : {...lines, line},
      );
}

/// Free text typed by the player (type-output levels).
final class TextAnswer extends Answer {
  const TextAnswer(this.text);

  final String text;

  @override
  bool get isComplete => text.trim().isNotEmpty;
}

/// Several options picked at once (multi-select levels).
final class OptionSetAnswer extends Answer {
  OptionSetAnswer(Set<int> options) : options = Set.unmodifiable(options);

  final Set<int> options;

  @override
  bool get isComplete => options.isNotEmpty;

  OptionSetAnswer toggle(int option) => OptionSetAnswer(
        options.contains(option)
            ? ({...options}..remove(option))
            : {...options, option},
      );
}

/// Pairs made by the player: left item index -> right item index (both in
/// the canonical pair order of the level).
final class MatchAnswer extends Answer {
  MatchAnswer(Map<int, int> links, {required this.pairCount})
      : links = Map.unmodifiable(links);

  factory MatchAnswer.empty(int pairCount) =>
      MatchAnswer(const {}, pairCount: pairCount);

  final Map<int, int> links;
  final int pairCount;

  @override
  bool get isComplete => links.length == pairCount;

  /// Links [left] to [right]; whatever either of them was linked to before
  /// is unlinked.
  MatchAnswer link(int left, int right) {
    final next = {...links}..removeWhere((key, value) => value == right);
    next[left] = right;
    return MatchAnswer(next, pairCount: pairCount);
  }

  MatchAnswer unlinkLeft(int left) =>
      MatchAnswer({...links}..remove(left), pairCount: pairCount);

  int? leftFor(int right) {
    for (final entry in links.entries) {
      if (entry.value == right) return entry.key;
    }
    return null;
  }
}

/// Values put into numbered slots: cells of a trace table, groups of a
/// categorize level (the value is the group index as text).
final class AssignmentAnswer extends Answer {
  AssignmentAnswer(Map<int, String> values, {required this.slotCount})
      : values = Map.unmodifiable(values);

  factory AssignmentAnswer.empty(int slotCount) =>
      AssignmentAnswer(const {}, slotCount: slotCount);

  final Map<int, String> values;
  final int slotCount;

  @override
  bool get isComplete => values.length == slotCount;

  AssignmentAnswer assign(int slot, String value) =>
      AssignmentAnswer({...values, slot: value}, slotCount: slotCount);

  AssignmentAnswer clear(int slot) =>
      AssignmentAnswer({...values}..remove(slot), slotCount: slotCount);

  /// First slot without a value, or null when all are filled.
  int? get firstEmpty {
    for (var slot = 0; slot < slotCount; slot++) {
      if (!values.containsKey(slot)) return slot;
    }
    return null;
  }
}
