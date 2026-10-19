import 'dart:convert';
import 'package:bytecraft/core/storage/game_save_store.dart';

import 'package:flutter/material.dart';
import 'package:bytecraft/features/career/domain/career_dashboard.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/app_harness.dart';

Future<void> openCareer(WidgetTester tester) async {
  await tester.scrollUntilVisible(find.text('Карьера · цель и навыки'), 200,
      scrollable: find.byType(Scrollable).first);
  await tester.pumpAndSettle();
  await tester.ensureVisible(find.text('Карьера · цель и навыки'));
  await tester.pumpAndSettle();
  await tester.tap(find.text('Карьера · цель и навыки'));
  await tester.pumpAndSettle();
}

void main() {
  testWidgets('career goal persists and course completion updates skills', (tester) async {
    final store = await pumpBytecraft(tester);
    await openCareer(tester);
    expect(find.text('Учебный маршрут: 0%'), findsOneWidget);
    await tester.tap(find.byType(DropdownButtonFormField<CareerTargetId>));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Junior Python Backend').last);
    await tester.pumpAndSettle();
    expect((await GameSaveStore(store).read('app.settings'))!, contains('junior_python_backend'));

    // Recreate the app, so the goal has to come from persisted settings.
    await tester.pumpWidget(const SizedBox());
    await pumpBytecraft(tester, store: store);
    await openCareer(tester);
    expect(find.text('Junior Python Backend'), findsOneWidget);
    await tester.scrollUntilVisible(find.text('Продолжить обучение'), 200,
        scrollable: find.byType(Scrollable).first);
    await tester.tap(find.text('Продолжить обучение'));
    await tester.pumpAndSettle();
    expect(find.text('Какое значение будет у x?'), findsOneWidget);
    await tester.tap(find.byKey(const ValueKey('option_1')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Проверить'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Продолжить'));
    await tester.pumpAndSettle();
    expect(jsonDecode((await GameSaveStore(store).read('player.course.python'))!)['levels'], isNotEmpty);

    await tester.pumpWidget(const SizedBox());
    await pumpBytecraft(tester, store: store);
    await openCareer(tester);
    expect(find.textContaining('Пройдено 1 из'), findsOneWidget);
    await tester.scrollUntilVisible(find.textContaining('Задания навыка: 1/'), 200,
        scrollable: find.byType(Scrollable).first);
    expect(find.textContaining('Задания навыка: 1/'), findsWidgets);
    await tester.scrollUntilVisible(find.text('Как считается прогресс?'), -200,
        scrollable: find.byType(Scrollable).first);
    await tester.tap(find.text('Как считается прогресс?'));
    await tester.pumpAndSettle();
    expect(find.text('Откуда берутся баллы'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
