import 'package:bytecraft/features/playground/domain/python_runner.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/app_harness.dart';
import '../helpers/fake_python_runner.dart';

/// Mistake → short note → detailed review → saved to the journal → the
/// journal tab and the topic card. Then the Python sandbox.
void main() {
  testWidgets('a mistake can be reviewed and saved to the journal', (tester) async {
    await pumpBytecraft(tester);
    await completeOnboarding(tester);
    await tester.tap(find.text('Продолжить'));
    await tester.pumpAndSettle();

    // Wrong answer: "3".
    await tester.tap(find.byKey(const ValueKey('option_0')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Проверить'));
    await tester.pumpAndSettle();
    dumpTexts(tester, 'wrong');
    expect(find.text('Не то'), findsOneWidget);

    // Detailed review with the topic and the journal button.
    await tester.tap(find.byKey(const ValueKey('review_button')));
    await tester.pumpAndSettle();
    dumpTexts(tester, 'review');
    expect(find.text('Что не так'), findsOneWidget);
    expect(find.text('Присваивание'), findsWidgets);
    // The sheet's list builds lazily: scroll down to the button.
    await tester.scrollUntilVisible(
      find.byKey(const ValueKey('journal_toggle')),
      300,
      scrollable: find
          .descendant(
            of: find.byType(DraggableScrollableSheet),
            matching: find.byType(Scrollable),
          )
          .first,
    );
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const ValueKey('journal_toggle')));
    await tester.pumpAndSettle();
    expect(find.text('В журнале · убрать'), findsOneWidget);

    // Close the sheet, try again correctly.
    await tester.tapAt(const Offset(195, 20));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Ещё раз'));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const ValueKey('option_1')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Проверить'));
    await tester.pumpAndSettle();
    expect(find.text('Верно!'), findsOneWidget);
    await tester.tap(find.text('Продолжить'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('К карте'));
    await tester.pumpAndSettle();

    // The journal tab lists the saved topic.
    await openTab(tester, 'Журнал');
    dumpTexts(tester, 'journal');
    expect(find.text('Мои темы'), findsOneWidget);
    expect(find.text('Присваивание'), findsWidgets);

    await tester.tap(find.text('Присваивание').first);
    await tester.pumpAndSettle();
    dumpTexts(tester, 'topic');
    expect(find.textContaining('Переменная — это имя'), findsWidgets);
  });

  testWidgets('the sandbox runs code and shows the output', (tester) async {
    final runner = FakePythonRunner(
      (code, stdin) => RunResult(status: RunStatus.ok, stdout: 'Привет, ${stdin.trim()}!\n'),
    );
    await pumpBytecraft(tester, runner: runner);
    await completeOnboarding(tester);

    await openTab(tester, 'Код');
    dumpTexts(tester, 'code');
    await tester.ensureVisible(find.byKey(const ValueKey('sandbox_run')));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const ValueKey('sandbox_run')));
    await tester.pumpAndSettle();
    dumpTexts(tester, 'code-run');
    expect(runner.calls, isNotEmpty);
    expect(runner.calls.last.echo, isTrue, reason: 'the sandbox shows input prompts');
    expect(find.textContaining('Привет, Ада!'), findsOneWidget);
  });
}
