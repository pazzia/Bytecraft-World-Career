import 'dart:convert';

import 'package:bytecraft/app/di/providers.dart';
import 'package:bytecraft/core/storage/key_value_store.dart';
import 'package:bytecraft/features/world/presentation/world_challenge_screens.dart';
import 'package:bytecraft/features/world/presentation/world_controller.dart';
import 'package:bytecraft/features/world/presentation/expedition_map.dart';
import 'package:bytecraft/features/world/domain/world_challenge.dart';
import 'package:bytecraft/features/world/domain/world_state.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets(
    'phone: blank blocked, wrong answer stays, correct changes question, choice must be selected',
    (tester) async {
      tester.view.physicalSize = const Size(360, 900);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.reset);
      final c = ProviderContainer(
        overrides: [
          keyValueStoreProvider.overrideWithValue(InMemoryKeyValueStore()),
        ],
      );
      addTearDown(c.dispose);
      await tester.pumpWidget(
        UncontrolledProviderScope(
          container: c,
          child: const MaterialApp(home: ExpeditionScreen()),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.byType(ExpeditionMap), findsOneWidget);
      expect(tester.widget<ExpeditionMap>(find.byType(ExpeditionMap)).completed, 0);
      final button = find.ancestor(
        of: find.text('Проверить ответ'),
        matching: find.byWidgetPredicate((w) => w is FilledButton),
      );
      await tester.scrollUntilVisible(find.text('Проверить ответ'), 250,
        scrollable: find.byType(Scrollable).first);
      await tester.pumpAndSettle();
      expect(tester.widget<FilledButton>(button).onPressed, isNull);
      await tester.enterText(
        find.byKey(const ValueKey('world-answer')),
        'wrong',
      );
      await tester.pump();
      await tester.tap(find.text('Проверить ответ'));
      await tester.pumpAndSettle();
      expect(c.read(worldControllerProvider).value!.expeditionStep, 0);
      expect(tester.widget<ExpeditionMap>(find.byType(ExpeditionMap)).completed, 0);
      expect(c.read(worldControllerProvider).value!.mistakes['Типы данных'], 1);
      expect(find.textContaining('Неверно.'), findsOneWidget);
      expect(find.byTooltip('Скопировать код'), findsNothing);
      for (var n = 0; n < 2; n++) {
        await tester.ensureVisible(find.text('Проверить ответ'));
        await tester.pumpAndSettle();
        await tester.tap(find.text('Проверить ответ'));
        await tester.pumpAndSettle();
      }
      expect(find.byTooltip('Скопировать код'), findsOneWidget);
      await tester.enterText(find.byKey(const ValueKey('world-answer')), '170');
      await tester.pump();
      await tester.ensureVisible(find.text('Проверить ответ'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Проверить ответ'));
      await tester.pumpAndSettle();
      expect(c.read(worldControllerProvider).value!.expeditionStep, 1);
      expect(tester.widget<ExpeditionMap>(find.byType(ExpeditionMap)).completed, 1);
      final hero = tester.getRect(find.byKey(const ValueKey('expedition-explorer')));
      expect(hero.top, greaterThanOrEqualTo(0));
      expect(hero.bottom, lessThanOrEqualTo(900));
      await tester.ensureVisible(find.text('Следующее задание'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Следующее задание'));
      await tester.pumpAndSettle();
      expect(find.text('Защита от деления на ноль'), findsOneWidget);
      expect(find.byTooltip('Скопировать код'), findsNothing);
      expect(tester.widget<FilledButton>(button).onPressed, isNull);
      await tester.ensureVisible(find.text('price != 0'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('price != 0'));
      await tester.pumpAndSettle();
      await tester.ensureVisible(find.text('Проверить ответ'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Проверить ответ'));
      await tester.pumpAndSettle();
      expect(c.read(worldControllerProvider).value!.expeditionStep, 2);
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets('all quest modes render on a narrow phone', (tester) async {
    tester.view.physicalSize = const Size(320, 800);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.reset);
    for (final mode in WorldMode.values) {
      final c = ProviderContainer(
        overrides: [
          keyValueStoreProvider.overrideWithValue(InMemoryKeyValueStore()),
        ],
      );
      await tester.pumpWidget(
        UncontrolledProviderScope(
          container: c,
          child: MaterialApp(home: WorldQuestScreen(mode: mode)),
        ),
      );
      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull, reason: mode.name);
      await tester.pumpWidget(const SizedBox());
      c.dispose();
    }
  });

  testWidgets('unlocked boss and project show real questions', (tester) async {
    for (final mode in [WorldMode.boss, WorldMode.project]) {
      final c = ProviderContainer(
        overrides: [
          keyValueStoreProvider.overrideWithValue(InMemoryKeyValueStore()),
        ],
      );
      await c.read(worldControllerProvider.future);
      final state = WorldState.initial().copyWith(
        expeditionStep: 5,
        projectSteps: {
          for (final id in WorldState.projectIds) id: mode == WorldMode.boss,
        },
      );
      await c
          .read(keyValueStoreProvider)
          .write(
            'bytecraft_world_state',
            jsonEncode({...state.toJson(), 'schemaVersion': 2}),
          );
      c.invalidate(worldControllerProvider);
      await tester.pumpWidget(
        UncontrolledProviderScope(
          container: c,
          child: MaterialApp(home: WorldQuestScreen(mode: mode)),
        ),
      );
      await tester.pumpAndSettle();
      expect(
        find.text(
          mode == WorldMode.boss ? 'Накопление суммы' : 'Базовые операции',
        ),
        findsOneWidget,
      );
      expect(tester.takeException(), isNull);
      await tester.pumpWidget(const SizedBox());
      c.dispose();
    }
  });
}
