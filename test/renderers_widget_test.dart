import 'package:bytecraft/core/theme/app_theme.dart';
import 'package:bytecraft/features/level/domain/answer.dart';
import 'package:bytecraft/features/level/renderers/fill_code_renderer.dart';
import 'package:bytecraft/features/level/renderers/multiple_choice_renderer.dart';
import 'package:bytecraft/features/level/renderers/question_renderer.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'helpers/test_env.dart';

Widget host(Widget child) => MaterialApp(
      theme: AppTheme.light,
      home: Scaffold(body: SingleChildScrollView(child: child)),
    );

void main() {
  final course = buildTestCourse();

  testWidgets('multiple choice renderer reports the tapped option',
      (tester) async {
    Answer? reported;
    await tester.pumpWidget(
      host(
        MultipleChoiceView(
          question: QuestionContext(
            level: course.levelById('l1')!,
            answer: null,
            isLocked: false,
            onChanged: (answer) => reported = answer,
          ),
        ),
      ),
    );
    expect(find.text('5'), findsOneWidget);
    await tester.tap(find.byKey(const ValueKey('option_1')));
    expect(reported, const ChoiceAnswer(1));
  });

  testWidgets('locked multiple choice ignores taps', (tester) async {
    Answer? reported;
    await tester.pumpWidget(
      host(
        MultipleChoiceView(
          question: QuestionContext(
            level: course.levelById('l1')!,
            answer: null,
            isLocked: true,
            onChanged: (answer) => reported = answer,
          ),
        ),
      ),
    );
    await tester.tap(find.byKey(const ValueKey('option_1')));
    expect(reported, isNull);
  });

  testWidgets('fill-code renderer places a tapped token into the blank',
      (tester) async {
    Answer? reported;
    await tester.pumpWidget(
      host(
        FillCodeView(
          question: QuestionContext(
            level: course.levelById('l2')!,
            answer: FillCodeAnswer.empty(1),
            isLocked: false,
            onChanged: (answer) => reported = answer,
          ),
        ),
      ),
    );
    await tester.tap(find.byKey(const ValueKey('token_0')));
    expect(reported, isA<FillCodeAnswer>());
    expect((reported! as FillCodeAnswer).tokens, ['in']);
  });

  test('used token detection supports duplicate tokens', () {
    expect(
      FillCodeView.usedOptionIndexes(['x', 'x', 'y'], ['x', null]),
      {0},
    );
  });
}
