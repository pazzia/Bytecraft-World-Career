import 'package:bytecraft/core/utils/json_reader.dart';
import 'package:bytecraft/features/courses/data/content_parser.dart';
import 'package:bytecraft/features/courses/domain/level_definition.dart';
import 'package:bytecraft/features/courses/domain/level_payload.dart';
import 'package:bytecraft/features/level/domain/answer.dart';
import 'package:bytecraft/features/level/domain/initial_answer_factory.dart';
import 'package:bytecraft/features/level/domain/mistake_analysis.dart';
import 'package:bytecraft/features/level/engine/answer_validator.dart';
import 'package:bytecraft/features/level/presentation/level_controller.dart';
import 'package:flutter_test/flutter_test.dart';

LevelDefinition parse(Map<String, dynamic> json) =>
    ContentParser().parseLevel(JsonReader(json), 'c', 'm');

final LevelDefinition traceLevel = parse({
  'id': 'trace',
  'type': 'trace_table',
  'title': 'Trace',
  'prompt': 'fill',
  'code': 'a = 1\nb = a\na = 3',
  'payload': {
    'columns': ['a', 'b'],
    'rows': [
      {'line': 1, 'values': ['1', '—']},
      {'line': 2, 'values': ['1', '1']},
      {'line': 3, 'values': ['3', '1']},
    ],
    'blanks': [
      [1, 1],
      [2, 0],
    ],
    'bank': ['1', '2', '3'],
  },
});

final LevelDefinition sortLevel = parse({
  'id': 'sort',
  'type': 'categorize',
  'title': 'Sort',
  'prompt': 'sort',
  'payload': {
    'categories': ['Изменяемые', 'Неизменяемые'],
    'items': [
      {'text': '[1]', 'category': 0, 'code': true},
      {'text': '(1,)', 'category': 1, 'code': true, 'feedback': 'Кортеж не меняется.'},
      {'text': "'a'", 'category': 1, 'code': true},
    ],
  },
});

final LevelDefinition fixLevel = parse({
  'id': 'fix',
  'type': 'fix_line',
  'title': 'Fix',
  'prompt': 'fix',
  'code': 'age = 18\nif age > 18:\n    print("ok")',
  'payload': {
    'line': 1,
    'accepted': ['if age >= 18:'],
    'expectedOutput': 'ok\n',
  },
});

void main() {
  final validators = ValidatorRegistry.standard();

  test('new types parse', () {
    expect(traceLevel.payload, isA<TraceTablePayload>());
    expect(sortLevel.payload, isA<CategorizePayload>());
    expect(fixLevel.payload, isA<FixLinePayload>());
    final trace = traceLevel.payload as TraceTablePayload;
    expect(trace.answerFor(0), '1');
    expect(trace.answerFor(1), '3');
    expect(trace.slotOf(2, 0), 1);
    expect(trace.slotOf(0, 0), isNull);
  });

  test('a trace bank without a right answer is rejected', () {
    final broken = parse({
      'id': 'bad',
      'type': 'trace_table',
      'title': 'x',
      'prompt': 'x',
      'code': 'a = 1',
      'payload': {
        'columns': ['a'],
        'rows': [
          {'line': 1, 'values': ['1']},
          {'line': 1, 'values': ['2']},
        ],
        'blanks': [
          [1, 0],
        ],
        'bank': ['1'],
      },
    });
    expect(broken.payload, isA<UnsupportedPayload>());
  });

  test('trace table: wrong cells are reported and dropped on retry', () {
    final answer = AssignmentAnswer({0: '1', 1: '2'}, slotCount: 2);
    final outcome = validators.validate(traceLevel, answer);
    expect(outcome.isCorrect, isFalse);
    expect(outcome.wrongParts, {1});
    final note = const MistakeAnalyzer().analyze(traceLevel, answer, outcome);
    expect(note.text, contains('после строки 3'));
    final retry = LevelController.answerAfterMistake(answer, outcome)! as AssignmentAnswer;
    expect(retry.values, {0: '1'});
    expect(retry.firstEmpty, 1);
    expect(
      validators.validate(traceLevel, AssignmentAnswer({0: '1', 1: '3'}, slotCount: 2)).isCorrect,
      isTrue,
    );
  });

  test('categorize: groups are compared by index, feedback explains', () {
    final answer = AssignmentAnswer({0: '0', 1: '0', 2: '1'}, slotCount: 3);
    final outcome = validators.validate(sortLevel, answer);
    expect(outcome.wrongParts, {1});
    final note = const MistakeAnalyzer().analyze(sortLevel, answer, outcome);
    expect(note.text, contains('Кортеж не меняется.'));
    expect(const InitialAnswerFactory().initialFor(sortLevel), isA<AssignmentAnswer>());
  });

  test('fix line starts from the broken line and forgives spacing and quotes', () {
    expect((const InitialAnswerFactory().initialFor(fixLevel)! as TextAnswer).text, 'if age > 18:');
    bool ok(String text) => validators.validate(fixLevel, TextAnswer(text)).isCorrect;
    expect(ok('if age >= 18:'), isTrue);
    expect(ok('   if age>=18 :'), isTrue);
    expect(ok('if age > 18:'), isFalse);
    expect(FixLineText.normalize("print('a b')"), FixLineText.normalize('print("a b")'));
    expect(FixLineText.normalize("print('a b')") == FixLineText.normalize("print('ab')"), isFalse,
        reason: 'spaces inside strings matter');
  });
}
