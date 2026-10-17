import 'package:bytecraft/core/utils/json_reader.dart';
import 'package:bytecraft/features/courses/data/content_parser.dart';
import 'package:bytecraft/features/courses/domain/level_definition.dart';
import 'package:bytecraft/features/courses/domain/level_payload.dart';
import 'package:bytecraft/features/level/domain/answer.dart';
import 'package:bytecraft/features/level/domain/initial_answer_factory.dart';
import 'package:bytecraft/features/level/domain/mistake_analysis.dart';
import 'package:bytecraft/features/level/domain/validation_outcome.dart';
import 'package:bytecraft/features/level/engine/answer_validator.dart';
import 'package:bytecraft/features/level/engine/validators/type_output_validator.dart';
import 'package:bytecraft/features/level/presentation/level_controller.dart';
import 'package:flutter_test/flutter_test.dart';

LevelDefinition parse(Map<String, dynamic> json) =>
    ContentParser().parseLevel(JsonReader(json), 'c', 'm');

final LevelDefinition multiLevel = parse({
  'id': 'multi',
  'type': 'multi_select',
  'title': 'Multi',
  'prompt': 'pick',
  'topic': 't1',
  'payload': {
    'options': ['a', 'b', 'c', 'd'],
    'correctIndexes': [0, 2],
    'optionFeedback': ['', 'b is wrong because', '', ''],
  },
});

final LevelDefinition matchLevel = parse({
  'id': 'match',
  'type': 'match_pairs',
  'title': 'Match',
  'prompt': 'pairs',
  'payload': {
    'pairs': [
      {'left': '1 + 1', 'right': '2'},
      {'left': '2 * 3', 'right': '6'},
      {'left': '10 // 3', 'right': '3'},
    ],
  },
});

final LevelDefinition typedLevel = parse({
  'id': 'typed',
  'type': 'type_output',
  'title': 'Typed',
  'prompt': 'type',
  'code': 'print("ёж", [1, 2])\nprint("ok")',
  'payload': {'expectedOutput': 'ёж [1, 2]\nok'},
  'solution': {'code': 'print(1)', 'output': '1\n'},
});

final LevelDefinition fillLevel = parse({
  'id': 'fill',
  'type': 'fill_code',
  'title': 'Fill',
  'prompt': 'fill',
  'payload': {
    'template': 'x = {{0}}\nprint(x {{1}} 1)',
    'options': ['5', '"5"', '+', '-'],
    'answers': ['5', '+'],
    'variantResults': {
      '"5"\u0001+': 'TypeError: can only concatenate str (not "int") to str',
      '5\u0001-': '4',
    },
  },
});

void main() {
  final validators = ValidatorRegistry.standard();

  group('parsing', () {
    test('new level types parse into their payloads', () {
      expect(multiLevel.payload, isA<MultiSelectPayload>());
      expect(matchLevel.payload, isA<MatchPairsPayload>());
      expect(typedLevel.payload, isA<TypeOutputPayload>());
      expect(typedLevel.solution!.output, '1\n');
      expect(multiLevel.topicId, 't1');
    });

    test('match pairs must be unique, otherwise the level is unsupported', () {
      final broken = parse({
        'id': 'bad',
        'type': 'match_pairs',
        'title': 'x',
        'prompt': 'x',
        'payload': {
          'pairs': [
            {'left': 'a', 'right': '1'},
            {'left': 'b', 'right': '1'},
          ],
        },
      });
      expect(broken.payload, isA<UnsupportedPayload>());
    });
  });

  group('validators', () {
    test('multi select needs exactly the correct set', () {
      expect(validators.validate(multiLevel, OptionSetAnswer({0, 2})).isCorrect, isTrue);
      final extra = validators.validate(multiLevel, OptionSetAnswer({0, 1, 2}));
      expect(extra.isCorrect, isFalse);
      expect(extra.wrongParts, {1});
      final missing = validators.validate(multiLevel, OptionSetAnswer({0}));
      expect(missing.wrongParts, isEmpty);
      expect(missing.missedParts, {2});
    });

    test('match pairs reports wrongly linked left items', () {
      final answer = MatchAnswer({0: 0, 1: 2, 2: 1}, pairCount: 3);
      final outcome = validators.validate(matchLevel, answer);
      expect(outcome.isCorrect, isFalse);
      expect(outcome.wrongParts, {1, 2});
      expect(
        validators.validate(matchLevel, MatchAnswer({0: 0, 1: 1, 2: 2}, pairCount: 3)).isCorrect,
        isTrue,
      );
    });

    test('typed output forgives keyboard quirks but not real differences', () {
      bool ok(String text) => validators.validate(typedLevel, TextAnswer(text)).isCorrect;
      expect(ok('ёж [1, 2]\nok'), isTrue);
      expect(ok('еж [1,2]\nok\n'), isTrue, reason: 'ё/е and a missing space after a comma');
      expect(ok('ёж [1, 2]  \r\nok'), isTrue, reason: 'trailing spaces and CRLF');
      expect(ok('ёж [1, 2]'), isFalse);
      expect(ok('ёж [1, 3]\nok'), isFalse);
      expect(ok('ёж[1, 2]\nok'), isFalse, reason: 'a missing space is still a difference');
    });

    test('OutputText converts smart quotes from mobile keyboards', () {
      expect(OutputText.differentLines(expected: "['a']", actual: '[’a’]'), isEmpty);
      expect(OutputText.differentLines(expected: '"x"', actual: '«x»'), isEmpty);
    });
  });

  group('initial answers', () {
    test('typed starts empty, match starts unlinked, multi starts with nothing', () {
      expect(const InitialAnswerFactory().initialFor(typedLevel), const TextAnswer(''));
      final match = const InitialAnswerFactory().initialFor(matchLevel) as MatchAnswer;
      expect(match.links, isEmpty);
      expect(match.isComplete, isFalse);
      expect(const InitialAnswerFactory().initialFor(multiLevel), isNull);
    });

    test('MatchAnswer.link moves a right item from its previous left', () {
      final answer = MatchAnswer.empty(3).link(0, 1).link(2, 1);
      expect(answer.links, {2: 1});
      expect(answer.leftFor(1), 2);
    });
  });

  group('mistake analysis', () {
    const analyzer = MistakeAnalyzer();

    test('multi select names the wrong option with its feedback', () {
      final note = analyzer.analyze(
        multiLevel,
        OptionSetAnswer({0, 1}),
        ValidationOutcome.incorrect({1}, {2}),
      );
      expect(note.text, 'b is wrong because');
    });

    test('multi select with only missing options says how many are missing', () {
      final note = analyzer.analyze(
        multiLevel,
        OptionSetAnswer({0}),
        ValidationOutcome.incorrect(const {}, {2}),
      );
      expect(note.text, contains('не хватает ещё 1'));
    });

    test('fill code shows what the program really does with the answer', () {
      final answer = FillCodeAnswer(['"5"', '+']);
      final outcome = validators.validate(fillLevel, answer);
      final note = analyzer.analyze(fillLevel, answer, outcome);
      expect(note.text, 'Пропуск 1 заполнен неверно.');
      expect(note.programResult, startsWith('TypeError'));
    });

    test('typed output compares line counts first', () {
      final note = analyzer.analyze(
        typedLevel,
        const TextAnswer('ёж [1, 2]'),
        validators.validate(typedLevel, const TextAnswer('ёж [1, 2]')),
      );
      expect(note.text, 'Программа выводит 2 строки, а у вас 1 строку.');
    });

    test('progress hint points at the first differing character', () {
      final payload = typedLevel.payload as TypeOutputPayload;
      expect(
        typeOutputProgressHint(payload, 'ёж [1, 9]\nok'),
        // Compared after normalization (ё → е, no space after commas).
        'Строка 1 начинается с «еж [1,», расхождение в символе 7.',
      );
      expect(typeOutputProgressHint(payload, 'ёж [1, 2]\nok'), isNull);
    });
  });

  group('after a mistake', () {
    test('multi select keeps only the right picks', () {
      final next = LevelController.answerAfterMistake(
        OptionSetAnswer({0, 1}),
        ValidationOutcome.incorrect({1}, {2}),
      );
      expect((next! as OptionSetAnswer).options, {0});
    });

    test('match pairs keeps the right links', () {
      final next = LevelController.answerAfterMistake(
        MatchAnswer({0: 0, 1: 2, 2: 1}, pairCount: 3),
        ValidationOutcome.incorrect({1, 2}),
      );
      expect((next! as MatchAnswer).links, {0: 0});
    });

    test('typed text stays for editing', () {
      const answer = TextAnswer('abc');
      expect(
        LevelController.answerAfterMistake(answer, ValidationOutcome.incorrect({0})),
        same(answer),
      );
    });
  });
}
