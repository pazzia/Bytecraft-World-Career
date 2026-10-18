import 'package:bytecraft/features/courses/domain/fill_code_template.dart';
import 'package:bytecraft/features/level/domain/answer.dart';
import 'package:bytecraft/features/level/domain/initial_answer_factory.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/test_env.dart';

void main() {
  group('FillCodeAnswer', () {
    test('place fills the first empty blank, clear empties it', () {
      final answer = FillCodeAnswer.empty(2).place('a').place('b');
      expect(answer.tokens, ['a', 'b']);
      expect(answer.isComplete, isTrue);
      final cleared = answer.clear(0);
      expect(cleared.tokens, [null, 'b']);
      expect(cleared.place('c').tokens, ['c', 'b']);
    });

    test('place is a no-op when all blanks are filled', () {
      final answer = FillCodeAnswer(['x']);
      expect(answer.place('y').tokens, ['x']);
    });
  });

  group('OrderingAnswer.move', () {
    test('moves an item to the target position', () {
      expect(OrderingAnswer([0, 1, 2, 3]).move(0, 2).order, [1, 2, 0, 3]);
      expect(OrderingAnswer([0, 1, 2, 3]).move(3, 0).order, [3, 0, 1, 2]);
    });

    test('ignores out-of-range moves', () {
      expect(OrderingAnswer([0, 1]).move(0, 5).order, [0, 1]);
    });
  });

  test('LineSelectionAnswer.toggle adds and removes lines', () {
    final selection = LineSelectionAnswer(const <int>{}).toggle(2).toggle(4);
    expect(selection.lines, {2, 4});
    expect(selection.toggle(2).lines, {4});
  });

  group('InitialAnswerFactory', () {
    test('ordering never starts in an accepted order', () {
      for (var seed = 0; seed < 200; seed++) {
        final order = InitialAnswerFactory.shuffledOrder(
          3,
          const [
            [1, 0, 2],
          ],
          seed,
        );
        expect(order..sort(), [0, 1, 2]);
      }
      for (var seed = 0; seed < 200; seed++) {
        final order = InitialAnswerFactory.shuffledOrder(
          3,
          const [
            [1, 0, 2],
          ],
          seed,
        );
        expect(order, isNot([0, 1, 2]));
        expect(order, isNot([1, 0, 2]));
      }
    });

    test('creates empty blanks for fill-code levels', () {
      final level = buildTestCourse().levelById('l2')!;
      final answer = const InitialAnswerFactory().initialFor(level);
      expect(answer, isA<FillCodeAnswer>());
      expect((answer! as FillCodeAnswer).tokens, [null]);
    });
  });

  test('FillCodeTemplate parses text and blanks per line', () {
    final lines = FillCodeTemplate.lines('if x {{0}} 1:\n    {{1}}');
    expect(lines, hasLength(2));
    expect(lines[0].whereType<BlankSegment>().single.index, 0);
    expect(lines[1].whereType<BlankSegment>().single.index, 1);
    expect(FillCodeTemplate.blankIndexes('{{1}} {{0}} {{1}}'), [0, 1]);
  });
}
