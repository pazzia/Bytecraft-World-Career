import '../../../courses/domain/level_definition.dart';
import '../../../courses/domain/level_payload.dart';
import '../../domain/answer.dart';
import '../../domain/validation_outcome.dart';
import '../answer_validator.dart';

/// Every blank cell must hold the value Python really had there.
class TraceTableValidator implements AnswerValidator {
  const TraceTableValidator();

  @override
  ValidationOutcome validate(LevelDefinition level, Answer answer) {
    final payload = level.payload;
    if (payload is! TraceTablePayload || answer is! AssignmentAnswer) {
      answerMismatch(level, answer);
    }
    final wrong = <int>{
      for (var slot = 0; slot < payload.blanks.length; slot++)
        if (answer.values[slot] != payload.answerFor(slot)) slot,
    };
    return wrong.isEmpty ? ValidationOutcome.correct : ValidationOutcome.incorrect(wrong);
  }
}

/// Every item must be in its group. Wrong parts are item indexes.
class CategorizeValidator implements AnswerValidator {
  const CategorizeValidator();

  @override
  ValidationOutcome validate(LevelDefinition level, Answer answer) {
    final payload = level.payload;
    if (payload is! CategorizePayload || answer is! AssignmentAnswer) {
      answerMismatch(level, answer);
    }
    final wrong = <int>{
      for (var i = 0; i < payload.items.length; i++)
        if (answer.values[i] != '${payload.items[i].category}') i,
    };
    return wrong.isEmpty ? ValidationOutcome.correct : ValidationOutcome.incorrect(wrong);
  }
}

/// The typed line must match a verified fix (spacing and quote style are
/// ignored). The level screen may additionally run an unmatched line in
/// the sandbox and accept it when the program prints the expected output.
class FixLineValidator implements AnswerValidator {
  const FixLineValidator();

  @override
  ValidationOutcome validate(LevelDefinition level, Answer answer) {
    final payload = level.payload;
    if (payload is! FixLinePayload || answer is! TextAnswer) {
      answerMismatch(level, answer);
    }
    final typed = FixLineText.normalize(answer.text);
    final ok = payload.accepted.any((line) => FixLineText.normalize(line) == typed);
    return ok ? ValidationOutcome.correct : ValidationOutcome.incorrect(const {0});
  }
}
