import 'dart:io';

import 'package:bytecraft/app/app.dart';
import 'package:bytecraft/app/di/providers.dart';
import 'package:bytecraft/core/storage/key_value_store.dart';
import 'package:bytecraft/core/time/clock.dart';
import 'package:bytecraft/features/playground/domain/python_runner.dart';
import 'package:bytecraft/features/playground/presentation/playground_providers.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'fake_python_runner.dart';

/// Bundled content read up front: no real IO inside the fake-async test.
Map<String, String> readBundledContent() => {
      for (final file
          in Directory('assets/content').listSync(recursive: true).whereType<File>())
        file.path.replaceAll(r'\', '/'): file.readAsStringSync(),
    };

/// The whole app on a phone-sized screen with the real bundled course, an
/// in-memory store, a fixed clock and a fake Python interpreter.
Future<InMemoryKeyValueStore> pumpBytecraft(
  WidgetTester tester, {
  PythonRunner? runner,
  InMemoryKeyValueStore? store,
}) async {
  tester.view.physicalSize = const Size(390, 844);
  tester.view.devicePixelRatio = 1;
  addTearDown(tester.view.reset);
  final kv = store ?? InMemoryKeyValueStore();
  final assets = readBundledContent();
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        keyValueStoreProvider.overrideWithValue(kv),
        textAssetLoaderProvider.overrideWithValue((path) async {
          final text = assets[path];
          if (text == null) throw StateError('No asset $path');
          return text;
        }),
        clockProvider.overrideWithValue(FixedClock(DateTime(2026, 10, 17, 12))),
        pythonRunnerProvider.overrideWithValue(
          runner ??
              FakePythonRunner(
                (code, stdin) => const RunResult(status: RunStatus.ok, stdout: 'ok\n'),
              ),
        ),
      ],
      child: const BytecraftApp(),
    ),
  );
  await tester.pumpAndSettle();
  return kv;
}

/// Onboarding: "a little experience", the only course, start.
Future<void> completeOnboarding(WidgetTester tester) async {
  await tester.tap(find.text('Немного знаю'));
  await tester.pumpAndSettle();
  await tester.tap(find.text('Дальше'));
  await tester.pumpAndSettle();
  await tester.tap(find.text('Начать'));
  await tester.pumpAndSettle();
}

/// Prints visible texts: CI only shows test output, so this is how a
/// failing screen can be inspected.
void dumpTexts(WidgetTester tester, String screen) {
  final texts = tester
      .widgetList<Text>(find.byType(Text))
      .map((text) => text.data ?? text.textSpan?.toPlainText() ?? '')
      .where((text) => text.isNotEmpty)
      .join(' | ');
  debugPrint('SCREEN[$screen]: $texts');
}

/// Taps a bottom tab by its label (the label may also be a screen title).
Future<void> openTab(WidgetTester tester, String label) async {
  await tester.tap(find.text(label).last);
  await tester.pumpAndSettle();
}
