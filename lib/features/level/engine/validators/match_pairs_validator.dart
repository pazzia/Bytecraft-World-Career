import '../../../courses/domain/level_definition.dart';
import '../../../courses/domain/level_payload.dart';
import '../../domain/answer.dart';
import '../../domain/validation_outcome.dart';
import '../answer_validator.dart';

/// Every left item must be linked to the right item of the same pair.
/// Wrong parts are the left items linked wrongly or not at all.
class MatchPairsValidator implements AnswerValidator {
  const MatchPairsValidator();

  @override
  ValidationOutcome validate(LevelDefinition level, Answer answer) {
    final payload = level.payload;
    if (payload is! MatchPairsPayload || answer is! MatchAnswer) {
      answerMismatch(level, answer);
    }
    final wrong = <int>{
      for (var i = 0; i < payload.pairs.length; i++)
        if (answer.links[i] != i) i,
    };
    return wrong.isEmpty
        ? ValidationOutcome.correct
        : ValidationOutcome.incorrect(wrong);
  }
}
