import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/app_harness.dart';

/// End-to-end smoke test on a phone-sized screen with the real bundled
/// course: World hub → learning map → first level → rewards → map.
/// Any layout overflow fails the test.
void main() {
  testWidgets('a World player enters learning and completes the first level',
      (tester) async {
    final store = await pumpBytecraft(tester);

    expect(find.text('Bytecraft World'), findsOneWidget);
    expect(find.text('Учись. Пиши. Строй. Соревнуйся.'), findsOneWidget);
    expect(find.text('CODE CITY'), findsOneWidget);
    expect(find.text('Жизни забега: 3/3'), findsOneWidget);

    await openTab(tester, 'Учёба');
    expect(find.text('Переменные'), findsWidgets);
    expect(find.text('Первая переменная'), findsOneWidget);
    await tester.tap(find.text('Первая переменная'));
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

    // Both learning progress and the World meta-game were persisted.
    expect(store.snapshot.keys, contains('player.course.python'));
    expect(store.snapshot.keys, contains('bytecraft_world_state'));
  });
}
