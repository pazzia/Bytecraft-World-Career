import 'dart:convert';
import 'dart:io';

import 'package:bytecraft/core/storage/game_save_store.dart';
import 'package:bytecraft/core/storage/key_value_store.dart';
import 'package:bytecraft/features/playground/domain/python_runner.dart';
import 'package:bytecraft/features/projects/domain/calculator_project.dart';
import 'package:bytecraft/features/projects/domain/project_service.dart';
import 'package:bytecraft/features/world/domain/world_state.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/app_harness.dart';
import '../helpers/fake_python_runner.dart';

void main() {
  final reference = File('tool/projects/calculator_reference.py')
      .readAsStringSync();
  testWidgets(
    'expedition chest leads to a saved executable calculator and boss unlock',
    (tester) async {
      final source = InMemoryKeyValueStore({
        'bytecraft_world_state': jsonEncode({
          ...WorldState.initial().copyWith(expeditionStep: 5).toJson(),
          'schemaVersion': 2,
        }),
      });
      final runner = FakePythonRunner((code, stdin) {
        final request = jsonDecode(stdin) as Map<String, dynamic>;
        return RunResult(
          status: RunStatus.ok,
          stdout: jsonEncode({
            'nonce': request['nonce'],
            'checks': List.generate(
              CalculatorProject.checkCounts[request['step'] as int],
              (i) => {'name': CalculatorProject.checkNames[i], 'passed': true},
            ),
          }),
        );
      });
      await pumpBytecraft(tester, store: source, runner: runner);
      await tester.scrollUntilVisible(
        find.text('Забрать сундук экспедиции'),
        150,
        scrollable: find.byType(Scrollable).first,
      );
      await tester.tap(find.text('Забрать сундук экспедиции'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Открыть сундук'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('К проекту').last);
      await tester.pumpAndSettle();
      await tester.scrollUntilVisible(
        find.byKey(const ValueKey('code_editor')),
        200,
        scrollable: find.byType(Scrollable).first,
      );
      await tester.enterText(
        find.byKey(const ValueKey('code_editor')),
        reference,
      );
      var program = reference;
      for (var step = 0; step < 4; step++) {
        await tester.scrollUntilVisible(
          find.text('Проверить программу'),
          200,
          scrollable: find.byType(Scrollable).first,
        );
        await tester.tap(find.text('Проверить программу'));
        await tester.pumpAndSettle();
        if (step == 0) {
          // The report is below the editor in a lazy ListView. Materialize it
          // by scrolling before asserting that the user can see it.
          await tester.scrollUntilVisible(
            find.textContaining('Этап 1/4 проверен запуском Python.'),
            150,
            scrollable: find.byType(Scrollable).first,
          );
          expect(
            find.textContaining('Этап 1/4 проверен запуском Python.'),
            findsOneWidget,
          );
          await tester.scrollUntilVisible(
            find.byKey(const ValueKey('code_editor')),
            -200,
            scrollable: find.byType(Scrollable).first,
          );
          program = '$reference\n# Продолжаю работу';
          await tester.enterText(
            find.byKey(const ValueKey('code_editor')),
            program,
          );
          await tester.pump();
          await tester.drag(find.byType(Scrollable).first, const Offset(0, -1000));
          await tester.pumpAndSettle();
          expect(
            find.textContaining('Этап 1/4 проверен запуском Python.'),
            findsNothing,
          );
        }
      }
      final saved = jsonDecode(
        (await GameSaveStore(source).read(ProjectService.key))!,
      ) as Map<String, dynamic>;
      expect(saved['step'], 4);
      expect(saved['verifiedCode'], program);
      final wallet = WorldState.fromJson(
        jsonDecode((await GameSaveStore(source).read('bytecraft_world_state'))!)
            as Map<String, dynamic>,
      );
      expect(wallet.hasVerifiedProject, isTrue);
      expect(wallet.coins, 180);
      expect(tester.takeException(), isNull);
    },
  );
}
