import '../../../courses/domain/level_definition.dart';
import '../../../courses/domain/level_payload.dart';
import '../../domain/answer.dart';
import '../../domain/validation_outcome.dart';
import '../answer_validator.dart';

/// Correct only when exactly the correct options are picked.
class MultiSelectValidator implements AnswerValidator {
  const MultiSelectValidator();

  @override
  ValidationOutcome validate(LevelDefinition level, Answer answer) {
    final payload = level.payload;
    if (payload is! MultiSelectPayload || answer is! OptionSetAnswer) {
      answerMismatch(level, answer);
    }
    final falsePicks = answer.options.difference(payload.correctIndexes);
    final missed = payload.correctIndexes.difference(answer.options);
    if (falsePicks.isEmpty && missed.isEmpty) return ValidationOutcome.correct;
    return ValidationOutcome.incorrect(falsePicks, missed);
  }
}
