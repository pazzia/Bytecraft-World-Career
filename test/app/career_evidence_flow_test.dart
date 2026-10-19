import 'dart:convert';
import 'dart:io';

import 'package:bytecraft/core/storage/game_save_store.dart';
import 'package:bytecraft/core/storage/key_value_store.dart';
import 'package:bytecraft/features/world/domain/repair_catalog.dart';
import 'package:bytecraft/features/world/domain/world_state.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/app_harness.dart';
import 'career_flow_test.dart' show openCareer;

Future<void> reveal(WidgetTester tester, Finder finder) async {
  await tester.scrollUntilVisible(
    finder,
    160,
    scrollable: find.byType(Scrollable).first,
  );
  await tester.pumpAndSettle();
  await tester.ensureVisible(finder);
  await tester.pumpAndSettle();
}

void main() {
  final bank = RepairCatalog.fromJson(
    jsonDecode(File('assets/projects/repair_catalog.json').readAsStringSync())
        as Map<String, dynamic>,
  );
  testWidgets(
    'Career starts an independent check without mistakes and retains proof after restart',
    (tester) async {
      const id = 'topic:python:var_assign';
      final store = InMemoryKeyValueStore({
        'player.course.python': jsonEncode({
          'schemaVersion': 1,
          'courseId': 'python',
          'levels': [
            {'levelId': 'py_var_001', 'completed': true, 'bestStars': 3},
          ],
        }),
      });
      await pumpBytecraft(tester, store: store);
      await openCareer(tester);
      await reveal(tester, find.byKey(const ValueKey('next_pythonCore')));
      expect(find.text('Изучено уровней: 1'), findsOneWidget);
      await tester.tap(find.byKey(const ValueKey('next_pythonCore')));
      await tester.pumpAndSettle();
      expect(find.text('Самостоятельная проверка'), findsWidgets);
      final save = GameSaveStore(store);
      var state = WorldState.fromJson(
        jsonDecode((await save.read('bytecraft_world_state'))!)
            as Map<String, dynamic>,
      );
      final record = state.repairs[id]!;
      expect(record.openErrors, 0);
      expect(record.assessmentRequested, isTrue);
      final example = bank.next(record)!;
      await reveal(tester, find.byKey(const ValueKey('world-answer')));
      await tester.enterText(
        find.byKey(const ValueKey('world-answer')),
        example.answer,
      );
      await tester.pumpAndSettle();
      await reveal(tester, find.text('Проверить ответ'));
      await tester.tap(find.text('Проверить ответ'));
      await tester.pumpAndSettle();
      state = WorldState.fromJson(
        jsonDecode((await save.read('bytecraft_world_state'))!)
            as Map<String, dynamic>,
      );
      expect(state.repairs[id]!.proofs.single['exampleId'], example.id);
      expect(state.repairs[id]!.pending, isFalse);
      await tester.pumpWidget(const SizedBox());
      await pumpBytecraft(tester, store: store);
      await openCareer(tester);
      await reveal(tester, find.byKey(const ValueKey('evidence_pythonCore')));
      expect(find.text('Подтверждено подтем: 1'), findsOneWidget);
      await tester.tap(find.byKey(const ValueKey('evidence_pythonCore')));
      await tester.pumpAndSettle();
      await reveal(
        tester,
        find.textContaining('Другой пример решён самостоятельно'),
      );
      expect(
        find.textContaining('Другой пример решён самостоятельно'),
        findsOneWidget,
      );
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets('Career evidence cards fit a small phone with enlarged text', (
    tester,
  ) async {
    await pumpBytecraft(tester);
    tester.view.physicalSize = const Size(320, 700);
    tester.platformDispatcher.textScaleFactorTestValue = 1.5;
    addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
    await openCareer(tester);
    expect(find.text('Карьерная цель'), findsOneWidget);
    await reveal(tester, find.byKey(const ValueKey('next_production')));
    expect(tester.takeException(), isNull);
  });
}
