import 'package:bytecraft/features/playground/domain/python_runner.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/app_harness.dart';
import '../helpers/fake_python_runner.dart';

void main() {
  testWidgets('a real learning mistake feeds Mistake DNA', (tester) async {
    await pumpBytecraft(tester);

    await openTab(tester, 'Учёба');
    await tester.tap(find.text('Первая переменная'));
    await tester.pumpAndSettle();

    // Wrong answer: "3". This is recorded both by the learning journal and
    // by the World Mistake DNA bridge.
    await tester.tap(find.byKey(const ValueKey('option_0')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Проверить'));
    await tester.pumpAndSettle();
    expect(find.text('Не то'), findsOneWidget);

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

    await openTab(tester, 'DNA');
    dumpTexts(tester, 'mistake-dna');
    expect(find.text('Mistake DNA'), findsOneWidget);
    expect(find.text('Твой профиль ошибок'), findsOneWidget);
    expect(find.text('Функции'), findsWidgets);
    // Default 7% + one real mistake = 9%.
    expect(find.text('9%'), findsOneWidget);
  });

  testWidgets('the sandbox runs code and shows the output', (tester) async {
    final runner = FakePythonRunner(
      (code, stdin) => RunResult(
        status: RunStatus.ok,
        stdout: 'Привет, ${stdin.trim()}!\n',
      ),
    );
    await pumpBytecraft(tester, runner: runner);

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
