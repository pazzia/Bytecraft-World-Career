import '../../../courses/domain/level_definition.dart';
import '../../../courses/domain/level_payload.dart';
import '../../domain/answer.dart';
import '../../domain/validation_outcome.dart';
import '../answer_validator.dart';

/// Correct when the selected lines are exactly the buggy lines.
class BugFinderValidator implements AnswerValidator {
  const BugFinderValidator();

  @override
  ValidationOutcome validate(LevelDefinition level, Answer answer) {
    final payload = level.payload;
    if (payload is! BugFinderPayload || answer is! LineSelectionAnswer) {
      answerMismatch(level, answer);
    }
    final falsePositives = answer.lines.difference(payload.buggyLines);
    final missed = payload.buggyLines.difference(answer.lines);
    if (falsePositives.isEmpty && missed.isEmpty) {
      return ValidationOutcome.correct;
    }
    return ValidationOutcome.incorrect(falsePositives, missed);
  }
}
