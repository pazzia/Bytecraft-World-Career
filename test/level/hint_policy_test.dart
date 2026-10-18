import 'package:bytecraft/features/gamification/domain/game_rules.dart';
import 'package:bytecraft/features/gamification/domain/score_calculators.dart';
import 'package:bytecraft/features/level/domain/answer.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/test_env.dart';

void main() {
  test('hint limits clean answer to two stars and removes perfect XP bonus', () async {
    final env = TestEnv();
    final session = env.engine.useHint(await env.startOk('l1'));
    final submitted = await env.engine.submit(session, const ChoiceAnswer(1));
    expect(submitted.completion!.stars, 2);
    expect(submitted.completion!.xpEarned, 10);
    expect((await env.progress.loadCourseProgress(testCourseId)).levelOf('l1').bestStars, 2);
    const calculator = StarCalculator(GameRules.standard);
    expect(calculator.starsFor(1, hintsUsed: 1), 2);
    expect(calculator.starsFor(2, hintsUsed: 1), 1);
  });
}
