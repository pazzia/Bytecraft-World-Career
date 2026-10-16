import '../../../courses/domain/level_definition.dart';
import '../../../courses/domain/level_payload.dart';
import '../../domain/answer.dart';
import '../../domain/validation_outcome.dart';
import '../answer_validator.dart';

class FillCodeValidator implements AnswerValidator {
  const FillCodeValidator();

  @override
  ValidationOutcome validate(LevelDefinition level, Answer answer) {
    final payload = level.payload;
    if (payload is! FillCodePayload || answer is! FillCodeAnswer) {
      answerMismatch(level, answer);
    }
    final wrong = <int>{};
    for (var i = 0; i < payload.blankCount; i++) {
      final token = i < answer.tokens.length ? answer.tokens[i] : null;
      if (token == null || token.trim() != payload.answers[i].trim()) {
        wrong.add(i);
      }
    }
    return wrong.isEmpty
        ? ValidationOutcome.correct
        : ValidationOutcome.incorrect(wrong);
  }
}
