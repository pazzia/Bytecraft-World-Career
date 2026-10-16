import 'dart:io';

import 'package:bytecraft/app/app.dart';
import 'package:bytecraft/app/di/providers.dart';
import 'package:bytecraft/core/storage/key_value_store.dart';
import 'package:bytecraft/core/time/clock.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

/// End-to-end smoke test on a phone-sized screen with the real bundled
/// course: onboarding → home → first level → rewards → map.
/// Any layout overflow fails the test.
void main() {
  testWidgets('a new player completes the first level', (tester) async {
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.reset);

    final store = InMemoryKeyValueStore();
    // Bundled content read up front: no real IO inside the fake-async test.
    final assets = {
      for (final file in Directory('assets/content')
          .listSync(recursive: true)
          .whereType<File>())
        file.path.replaceAll(r'\', '/'): file.readAsStringSync(),
    };
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          keyValueStoreProvider.overrideWithValue(store),
          textAssetLoaderProvider.overrideWithValue((path) async {
            final text = assets[path];
            if (text == null) throw StateError('No asset $path');
            return text;
          }),
          clockProvider.overrideWithValue(FixedClock(DateTime(2026, 10, 17, 12))),
        ],
        child: const BytecraftApp(),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('Код за пару минут в день'), findsOneWidget);
    await tester.tap(find.text('Немного знаю'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Дальше'));
    await tester.pumpAndSettle();

    expect(find.text('Что будем учить?'), findsOneWidget);
    // The only available course is pre-selected.
    await tester.tap(find.text('Начать'));
    await tester.pumpAndSettle();

    // Home: the next level on the board.
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

    expect(find.text('1 из 5'), findsOneWidget);
    expect(find.text('Обучение'), findsOneWidget);

    // Progress was persisted.
    expect(store.snapshot.keys, contains('player.course.python'));
  });
}
