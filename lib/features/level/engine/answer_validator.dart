import '../../../core/errors/app_exception.dart';
import '../../courses/domain/level_definition.dart';
import '../../courses/domain/level_type.dart';
import '../domain/answer.dart';
import '../domain/validation_outcome.dart';
import 'validators/bug_finder_validator.dart';
import 'validators/code_ordering_validator.dart';
import 'validators/fill_code_validator.dart';
import 'validators/multiple_choice_validator.dart';

/// Checks an answer against a level. One implementation per mechanic.
///
/// Validators are pure: no I/O, no randomness — trivially unit-testable.
/// A future `ExecutionValidator` can delegate to CodeExecutionService.
abstract interface class AnswerValidator {
  ValidationOutcome validate(LevelDefinition level, Answer answer);
}

/// Maps level types to validators. Adding a mechanic = registering here.
class ValidatorRegistry {
  const ValidatorRegistry(this._validators);

  factory ValidatorRegistry.standard() => const ValidatorRegistry({
        LevelType.multipleChoice: MultipleChoiceValidator(),
        LevelType.predictOutput: MultipleChoiceValidator(),
        LevelType.fillCode: FillCodeValidator(),
        LevelType.codeOrdering: CodeOrderingValidator(),
        LevelType.bugFinder: BugFinderValidator(),
      });

  final Map<LevelType, AnswerValidator> _validators;

  bool supports(LevelType type) => _validators.containsKey(type);

  ValidationOutcome validate(LevelDefinition level, Answer answer) {
    final validator = _validators[level.type];
    if (validator == null || !level.isSupported) {
      throw UnsupportedLevelTypeException(
        'No validator for "${level.type.id}" (${level.id})',
      );
    }
    return validator.validate(level, answer);
  }
}

/// Thrown when an answer shape doesn't match the level payload —
/// a programming error in a renderer.
Never answerMismatch(LevelDefinition level, Answer answer) =>
    throw ArgumentError(
      '${answer.runtimeType} is not valid for ${level.type.id} (${level.id})',
    );
