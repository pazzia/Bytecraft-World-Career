import 'package:bytecraft/app/di/providers.dart';
import 'package:bytecraft/features/level/domain/answer.dart';
import 'package:bytecraft/features/level/domain/level_session.dart';
import 'package:bytecraft/features/level/domain/validation_outcome.dart';
import 'package:bytecraft/features/level/presentation/level_controller.dart';
import 'package:bytecraft/features/level/presentation/level_ui_state.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/test_env.dart';

Future<LevelUiState> settled(
  ProviderContainer container,
  LevelArgs args,
) async {
  for (var i = 0; i < 20; i++) {
    await Future<void>.delayed(Duration.zero);
    final state = container.read(levelControllerProvider(args));
    if (state.phase != LevelPhase.loading && !state.isSubmitting) return state;
  }
  return container.read(levelControllerProvider(args));
}

void main() {
  late TestEnv env;
  late ProviderContainer container;

  setUp(() {
    env = TestEnv();
    container = ProviderContainer(
      overrides: [levelEngineProvider.overrideWithValue(env.engine)],
    );
    addTearDown(container.dispose);
  });

  LevelArgs args(String levelId, [LevelMode mode = LevelMode.standard]) =>
      (courseId: testCourseId, levelId: levelId, mode: mode);

  test('a wrong choice is cleared, so a double tap cannot cost two lives',
      () async {
    final a = args('l1');
    container.listen(levelControllerProvider(a), (_, _) {});
    await settled(container, a);
    final controller = container.read(levelControllerProvider(a).notifier);

    controller.updateAnswer(const ChoiceAnswer(0));
    await controller.submit();
    expect(container.read(levelControllerProvider(a)).phase, LevelPhase.wrongAnswer);

    controller.dismissMistake();
    final state = container.read(levelControllerProvider(a));
    expect(state.phase, LevelPhase.playing);
    expect(state.answer, isNull);
    expect(state.canSubmit, isFalse);
  });

  test('a timed level without a running clock shows "time up"', () async {
    final a = args('l1', LevelMode.timed);
    container.listen(levelControllerProvider(a), (_, _) {});
    final state = await settled(container, a);
    expect(state.phase, LevelPhase.timeUp);
  });

  group('answerAfterMistake', () {
    test('keeps right blanks, clears wrong ones', () {
      final next = LevelController.answerAfterMistake(
        FillCodeAnswer(['in', 'x']),
        ValidationOutcome.incorrect({1}),
      );
      expect((next! as FillCodeAnswer).tokens, ['in', null]);
    });

    test('drops falsely selected bug lines only', () {
      final next = LevelController.answerAfterMistake(
        LineSelectionAnswer({1, 2}),
        ValidationOutcome.incorrect({2}),
      );
      expect((next! as LineSelectionAnswer).lines, {1});
    });

    test('keeps the ordering so the player can adjust it', () {
      final order = OrderingAnswer([1, 0, 2]);
      expect(
        LevelController.answerAfterMistake(order, ValidationOutcome.incorrect()),
        same(order),
      );
    });
  });
}
