import 'package:bytecraft/core/errors/app_exception.dart';
import 'package:bytecraft/features/courses/domain/course.dart';
import 'package:bytecraft/features/courses/domain/level_definition.dart';
import 'package:bytecraft/features/level/domain/answer.dart';
import 'package:bytecraft/features/level/engine/answer_validator.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/test_env.dart';

void main() {
  final Course course = buildTestCourse();
  final validators = ValidatorRegistry.standard();
  LevelDefinition level(String id) => course.levelById(id)!;

  group('MultipleChoiceValidator', () {
    test('accepts the correct option', () {
      expect(validators.validate(level('l1'), const ChoiceAnswer(1)).isCorrect,
          isTrue);
    });

    test('rejects a wrong option and reports it', () {
      final outcome = validators.validate(level('l1'), const ChoiceAnswer(0));
      expect(outcome.isCorrect, isFalse);
      expect(outcome.wrongParts, {0});
    });
  });

  group('FillCodeValidator', () {
    test('accepts the expected token', () {
      final outcome = validators.validate(level('l2'), FillCodeAnswer(['in']));
      expect(outcome.isCorrect, isTrue);
    });

    test('rejects a wrong token and reports the blank', () {
      final outcome = validators.validate(level('l2'), FillCodeAnswer(['of']));
      expect(outcome.isCorrect, isFalse);
      expect(outcome.wrongParts, {0});
    });

    test('treats an empty blank as wrong', () {
      final outcome =
          validators.validate(level('l2'), FillCodeAnswer.empty(1));
      expect(outcome.isCorrect, isFalse);
    });
  });

  group('CodeOrderingValidator', () {
    test('accepts the canonical order', () {
      expect(
        validators.validate(level('l3'), OrderingAnswer([0, 1, 2])).isCorrect,
        isTrue,
      );
    });

    test('accepts an authored alternative order', () {
      expect(
        validators.validate(level('l3'), OrderingAnswer([1, 0, 2])).isCorrect,
        isTrue,
      );
    });

    test('rejects other orders and reports wrong positions', () {
      final outcome = validators.validate(level('l3'), OrderingAnswer([2, 0, 1]));
      expect(outcome.isCorrect, isFalse);
      expect(outcome.wrongParts, {0, 1, 2});
    });
  });

  group('BugFinderValidator', () {
    test('accepts exactly the buggy line', () {
      expect(
        validators.validate(level('l6'), LineSelectionAnswer({1})).isCorrect,
        isTrue,
      );
    });

    test('rejects extra lines and reports false positives', () {
      final outcome =
          validators.validate(level('l6'), LineSelectionAnswer({0, 1}));
      expect(outcome.isCorrect, isFalse);
      expect(outcome.wrongParts, {0});
    });

    test('rejects a missed bug', () {
      expect(
        validators.validate(level('l6'), LineSelectionAnswer({2})).isCorrect,
        isFalse,
      );
    });
  });

  group('ValidatorRegistry', () {
    test('throws for unsupported level types', () {
      expect(
        () => validators.validate(level('l5'), const ChoiceAnswer(0)),
        throwsA(isA<UnsupportedLevelTypeException>()),
      );
    });

    test('throws when the answer shape does not match the level', () {
      expect(
        () => validators.validate(level('l1'), FillCodeAnswer(['in'])),
        throwsArgumentError,
      );
    });
  });
}
