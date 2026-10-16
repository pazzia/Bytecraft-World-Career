import 'package:flutter_test/flutter_test.dart';
import 'package:codequest_mvp/core/level_engine.dart';
import 'package:codequest_mvp/models/level.dart';

void main() {
  const engine = LevelEngine();
  const level = Level(
    id: 'test', module: 'Test', title: 'T', description: 'D',
    type: LevelType.multipleChoice, code: 'x=1', options: ['1','2'],
    correctAnswer: '1', explanation: 'ok', xp: 10,
  );

  test('validates correct answer', () {
    expect(engine.validate(level, '1'), isTrue);
    expect(engine.validate(level, '2'), isFalse);
  });

  test('awards 3 stars without mistakes', () {
    final result = engine.evaluate(level, '1', 0);
    expect(result.isCorrect, isTrue);
    expect(result.stars, 3);
    expect(result.xpAwarded, 10);
  });

  test('wrong answer gives no reward', () {
    final result = engine.evaluate(level, '2', 0);
    expect(result.isCorrect, isFalse);
    expect(result.xpAwarded, 0);
  });
}
