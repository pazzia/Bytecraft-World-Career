import 'dart:convert';

import 'package:bytecraft/core/storage/key_value_store.dart';
import 'package:bytecraft/features/world/domain/world_state.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:bytecraft/features/profile/presentation/profile_screen.dart';

import '../helpers/app_harness.dart';

void main() {
  testWidgets(
    'confirmed profile reset also clears World progression and reward history',
    (tester) async {
      final previous = WorldState.initial().copyWith(
        coins: 999,
        worldXp: 900,
        expeditionStep: 4,
        solved: {'expedition': 4, 'lesson:python:first': 1},
        infiniteRecord: 12,
      );
      final store = InMemoryKeyValueStore({
        'bytecraft_world_state': jsonEncode({
          ...previous.toJson(),
          'schemaVersion': 2,
        }),
      });
      await pumpBytecraft(tester, store: store);
      await openTab(tester, 'Профиль');
      await tester.scrollUntilVisible(
        find.text('Сбросить прогресс'),
        200,
        scrollable: find
            .descendant(
              of: find.byType(ProfileScreen),
              matching: find.byType(Scrollable),
            )
            .first,
      );
      await tester.pumpAndSettle();
      await tester.tap(find.text('Сбросить прогресс'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Сбросить прогресс').last);
      await tester.pumpAndSettle();
      final saved = WorldState.fromJson(
        jsonDecode((await store.read('bytecraft_world_state'))!)
            as Map<String, dynamic>,
      );
      expect(saved.coins, 0);
      expect(saved.expeditionStep, 0);
      expect(saved.solved, isEmpty);
      expect(saved.infiniteRecord, 0);
      expect(tester.takeException(), isNull);
    },
  );
}
