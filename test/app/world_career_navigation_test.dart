import 'dart:convert';

import 'package:bytecraft/core/storage/game_save_store.dart';
import 'package:bytecraft/core/storage/key_value_store.dart';
import 'package:bytecraft/features/career/domain/career_dashboard.dart';
import 'package:bytecraft/features/world/domain/world_state.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/app_harness.dart';

void main() {
  testWidgets('five tabs expose career and the practice editor on a narrow phone', (tester) async {
    await pumpBytecraft(tester);
    tester.view.physicalSize = const Size(320, 800);
    await tester.pumpAndSettle();
    await openTab(tester, 'Карьера');
    expect(find.text('Карьерная цель'), findsOneWidget);
    await openTab(tester, 'Практика');
    expect(find.text('Написать код'), findsOneWidget);
    expect(find.text('Работа над ошибками'), findsOneWidget);
    await tester.tap(find.text('Открыть редактор'));
    await tester.pumpAndSettle();
    expect(find.byKey(const ValueKey('code_editor')), findsOneWidget);
    await openTab(tester, 'Мир');
    expect(find.text('Bytecraft World'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('completed expedition suggests chest and its fixed button pays once', (tester) async {
    final source = InMemoryKeyValueStore({
      'bytecraft_world_state': jsonEncode({
        ...WorldState.initial().copyWith(expeditionStep: 5).toJson(), 'schemaVersion': 2,
      }),
    });
    await pumpBytecraft(tester, store: source);
    await tester.scrollUntilVisible(find.text('Забрать сундук экспедиции'), 150,
        scrollable: find.byType(Scrollable).first);
    await tester.tap(find.text('Забрать сундук экспедиции'));
    await tester.pumpAndSettle();
    final button = tester.widget<FilledButton>(find.ancestor(
        of: find.text('Открыть сундук'), matching: find.byWidgetPredicate((widget) => widget is FilledButton)));
    for (var i = 0; i < 8; i++) { button.onPressed!(); }
    await tester.pumpAndSettle();
    final wallet = WorldState.fromJson(jsonDecode((await GameSaveStore(source)
        .read('bytecraft_world_state'))!) as Map<String, dynamic>);
    expect(wallet.coins, 80);
    expect(wallet.gems, 5);
    expect(wallet.worldXp, 100);
    expect(find.text('К проекту'), findsWidgets);
    expect(tester.takeException(), isNull);
  });

  testWidgets('failed goal save restores the displayed goal and permits retry', (tester) async {
    final source = _Disk();
    await pumpBytecraft(tester, store: source);
    await openTab(tester, 'Карьера');
    source.fail = true;
    await tester.tap(find.byType(DropdownButtonFormField<CareerTargetId>));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Junior Python Backend').last);
    await tester.pumpAndSettle();
    expect(find.text('Python Backend Developer'), findsOneWidget);
    expect(find.text('Не удалось сохранить цель. Повтори выбор.'), findsOneWidget);
    source.fail = false;
    await tester.tap(find.byType(DropdownButtonFormField<CareerTargetId>));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Junior Python Backend').last);
    await tester.pumpAndSettle();
    expect(find.text('Junior Python Backend'), findsOneWidget);
    expect((await GameSaveStore(source).read('app.settings'))!, contains('junior_python_backend'));
    expect(tester.takeException(), isNull);
  });
}

class _Disk extends InMemoryKeyValueStore {
  bool fail = false;
  @override
  Future<void> write(String key, String value) async {
    if (fail) throw StateError('disk full');
    await super.write(key, value);
  }
}
