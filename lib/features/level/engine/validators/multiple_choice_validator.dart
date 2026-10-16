import '../../../courses/domain/level_definition.dart';
import '../../../courses/domain/level_payload.dart';
import '../../domain/answer.dart';
import '../../domain/validation_outcome.dart';
import '../answer_validator.dart';

class MultipleChoiceValidator implements AnswerValidator {
  const MultipleChoiceValidator();

  @override
  ValidationOutcome validate(LevelDefinition level, Answer answer) {
    final payload = level.payload;
    if (payload is! MultipleChoicePayload || answer is! ChoiceAnswer) {
      answerMismatch(level, answer);
    }
    return answer.optionIndex == payload.correctIndex
        ? ValidationOutcome.correct
        : ValidationOutcome.incorrect({answer.optionIndex});
  }
}
