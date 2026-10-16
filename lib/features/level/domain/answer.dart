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
