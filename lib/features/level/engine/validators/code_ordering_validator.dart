import '../../../courses/domain/level_definition.dart';
import '../../../courses/domain/level_payload.dart';
import '../../domain/answer.dart';
import '../../domain/validation_outcome.dart';
import '../answer_validator.dart';

/// Accepts the canonical order or any authored alternative order.
/// Wrong positions are reported against the canonical order.
class CodeOrderingValidator implements AnswerValidator {
  const CodeOrderingValidator();

  @override
  ValidationOutcome validate(LevelDefinition level, Answer answer) {
    final payload = level.payload;
    if (payload is! CodeOrderingPayload || answer is! OrderingAnswer) {
      answerMismatch(level, answer);
    }
    final canonical = List<int>.generate(payload.lines.length, (i) => i);
    final accepted = [canonical, ...payload.alternativeOrders];
    if (accepted.any((order) => _equals(order, answer.order))) {
      return ValidationOutcome.correct;
    }
    final wrongPositions = <int>{};
    for (var i = 0; i < canonical.length; i++) {
      if (i >= answer.order.length || answer.order[i] != canonical[i]) {
        wrongPositions.add(i);
      }
    }
    return ValidationOutcome.incorrect(wrongPositions);
  }

  static bool _equals(List<int> a, List<int> b) {
    if (a.length != b.length) return false;
    for (var i = 0; i < a.length; i++) {
      if (a[i] != b[i]) return false;
    }
    return true;
  }
}
