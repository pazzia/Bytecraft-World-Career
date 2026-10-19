import 'dart:convert';
import 'dart:io';

import 'package:bytecraft/core/storage/game_save_store.dart';
import 'package:bytecraft/core/storage/key_value_store.dart';
import 'package:bytecraft/features/world/domain/repair_catalog.dart';
import 'package:bytecraft/features/world/domain/world_challenge.dart';
import 'package:bytecraft/features/world/domain/world_rules.dart';
import 'package:bytecraft/features/world/domain/world_state.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/app_harness.dart';

void main() {
  final bank = RepairCatalog.fromJson(
    jsonDecode(File('assets/projects/repair_catalog.json').readAsStringSync())
        as Map<String, dynamic>,
  );
  testWidgets(
    'journal opens a concrete gap; disclosed answer is replaced and clean new solution saves proof',
    (tester) async {
      final initial = WorldState.initial();
      final original = WorldChallenges.at(initial, WorldMode.training);
      final wrong = WorldRules.submit(
        initial,
        WorldMode.training,
        original.id,
        'WRONG',
        DateTime(2026, 10, 19),
      ).state;
      final store = InMemoryKeyValueStore({
        'bytecraft_world_state': jsonEncode({
          ...wrong.toJson(),
          'schemaVersion': 2,
        }),
      });
      await pumpBytecraft(tester, store: store);
      await openTab(tester, 'DNA');
      await tester.scrollUntilVisible(
        find.text('Проверить на другом примере'),
        150,
        scrollable: find.byType(Scrollable).first,
      );
      await tester.tap(find.text('Проверить на другом примере'));
      await tester.pumpAndSettle();
      await tester.scrollUntilVisible(
        find.byKey(const ValueKey('world-answer')),
        150,
        scrollable: find.byType(Scrollable).first,
      );
      await tester.enterText(
        find.byKey(const ValueKey('world-answer')),
        'WRONG',
      );
      await tester.scrollUntilVisible(
        find.text('Проверить ответ'),
        150,
        scrollable: find.byType(Scrollable).first,
      );
      await tester.tap(find.text('Проверить ответ'));
      await tester.pumpAndSettle();
      final save = GameSaveStore(store);
      var state = WorldState.fromJson(
        jsonDecode((await save.read('bytecraft_world_state'))!)
            as Map<String, dynamic>,
      );
      final record = state.repairs.values.single;
      expect(record.pending, isTrue);
      expect(record.seen.length, 1);
      expect(record.proofs, isEmpty);
      final next = bank.next(record)!;
      expect(next.id, isNot(record.seen.single));
      await tester.scrollUntilVisible(
        find.byKey(const ValueKey('world-answer')),
        150,
        scrollable: find.byType(Scrollable).first,
      );
      await tester.enterText(
        find.byKey(const ValueKey('world-answer')),
        next.answer,
      );
      await tester.scrollUntilVisible(
        find.text('Проверить ответ'),
        150,
        scrollable: find.byType(Scrollable).first,
      );
      await tester.tap(find.text('Проверить ответ'));
      await tester.pumpAndSettle();
      state = WorldState.fromJson(
        jsonDecode((await save.read('bytecraft_world_state'))!)
            as Map<String, dynamic>,
      );
      expect(state.repairs.values.single.pending, isFalse);
      expect(state.repairs.values.single.proofs.single['exampleId'], next.id);
      expect(state.coins, 12);
      expect(find.textContaining('Подтверждение сохранено.'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );
}
