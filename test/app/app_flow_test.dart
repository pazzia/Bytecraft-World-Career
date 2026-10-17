import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/app_harness.dart';

/// End-to-end smoke test on a phone-sized screen with the real bundled
/// course: onboarding → home → first level → rewards → map.
/// Any layout overflow fails the test.
void main() {
  testWidgets('a new player completes the first level', (tester) async {
    final store = await pumpBytecraft(tester);

    expect(find.text('Код за пару минут в день'), findsOneWidget);
    expect(find.text('Версия dev'), findsOneWidget);
    await tester.tap(find.text('Немного знаю'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Дальше'));
    await tester.pumpAndSettle();

    expect(find.text('Что будем учить?'), findsOneWidget);
    // The only available course is pre-selected.
    await tester.tap(find.text('Начать'));
    await tester.pumpAndSettle();

    // Home: the next level on the board.
    dumpTexts(tester, 'home');
    expect(find.text('Переменные'), findsWidgets);
    expect(find.text('Первая переменная'), findsOneWidget);
    await tester.tap(find.text('Продолжить'));
    await tester.pumpAndSettle();

    // Level: x = 5 → answer "5".
    expect(find.text('Какое значение будет у x?'), findsOneWidget);
    await tester.tap(find.byKey(const ValueKey('option_1')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Проверить'));
    await tester.pumpAndSettle();

    expect(find.text('Верно!'), findsOneWidget);
    await tester.tap(find.text('Продолжить'));
    await tester.pumpAndSettle();

    expect(find.text('С первой попытки'), findsOneWidget);
    expect(find.text('+15'), findsOneWidget);
    await tester.tap(find.text('К карте'));
    await tester.pumpAndSettle();

    expect(find.text('1 из 8'), findsOneWidget);
    expect(find.text('Обучение'), findsOneWidget);

    // Progress was persisted.
    expect(store.snapshot.keys, contains('player.course.python'));
  });
}
