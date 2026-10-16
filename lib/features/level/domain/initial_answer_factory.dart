import 'dart:math';

import '../../courses/domain/level_definition.dart';
import '../../courses/domain/level_payload.dart';
import 'answer.dart';

/// Builds the starting (draft) answer for a level.
///
/// Keeps rules like "ordering puzzles never start already solved" out of
/// the widgets.
class InitialAnswerFactory {
  const InitialAnswerFactory();

  Answer? initialFor(LevelDefinition level, {int seed = 0}) =>
      switch (level.payload) {
        MultipleChoicePayload() => null,
        FillCodePayload(:final blankCount) => FillCodeAnswer.empty(blankCount),
        CodeOrderingPayload(:final lines, :final alternativeOrders) =>
          OrderingAnswer(shuffledOrder(lines.length, alternativeOrders, seed)),
        BugFinderPayload() => null,
        UnsupportedPayload() => null,
      };

  /// Deterministic shuffle that differs from every accepted order.
  static List<int> shuffledOrder(
    int length,
    List<List<int>> acceptedAlternatives,
    int seed,
  ) {
    final identity = List<int>.generate(length, (i) => i);
    if (length < 2) return identity;
    final accepted = [identity, ...acceptedAlternatives];
    final random = Random(seed);
    const maxAttempts = 32;
    for (var attempt = 0; attempt < maxAttempts; attempt++) {
      final candidate = [...identity]..shuffle(random);
      if (!accepted.any((order) => _same(order, candidate))) return candidate;
    }
    // Fallback: rotate by one — never equal to identity for length >= 2.
    return [...identity.skip(1), identity.first];
  }

  static bool _same(List<int> a, List<int> b) {
    if (a.length != b.length) return false;
    for (var i = 0; i < a.length; i++) {
      if (a[i] != b[i]) return false;
    }
    return true;
  }
}
