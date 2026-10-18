import 'dart:convert';

import 'package:bytecraft/app/di/providers.dart';
import 'package:bytecraft/core/storage/key_value_store.dart';
import 'package:bytecraft/core/time/clock.dart';
import 'package:bytecraft/features/world/domain/world_challenge.dart';
import 'package:bytecraft/features/world/domain/world_hearts.dart';
import 'package:bytecraft/features/world/domain/world_rules.dart';
import 'package:bytecraft/features/world/domain/world_state.dart';
import 'package:bytecraft/features/world/presentation/world_controller.dart';
import 'package:bytecraft/features/world/presentation/world_hearts_panel.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  final now = DateTime.utc(2026, 10, 18, 10);

  test('lives return one at a time, keeping partial interval after another error', () {
    var s = WorldHearts.lose(WorldState.initial(), now);
    s = WorldHearts.lose(s, now.add(const Duration(minutes: 10)));
    expect(s.hearts, 1);
    expect(WorldHearts.nextIn(s, now.add(const Duration(minutes: 29, seconds: 59))), const Duration(seconds: 1));
    s = WorldHearts.regenerate(s, now.add(const Duration(minutes: 30)));
    expect(s.hearts, 2);
    expect(WorldHearts.nextIn(s, now.add(const Duration(minutes: 35))), const Duration(minutes: 25));
    s = WorldHearts.regenerate(s, now.add(const Duration(minutes: 60)));
    expect(s.hearts, 3);
    expect(s.heartRegenAnchor, isNull);
    expect(WorldHearts.nextIn(s, now.add(const Duration(minutes: 60))), isNull);
  });

  test('offline restore respects capacity including server upgrades and starts fresh when full', () {
    final depleted = WorldState.initial().copyWith(hearts: 0, heartRegenAnchor: now,
      cityLevels: {...WorldState.initial().cityLevels, 'servers': 5});
    final loaded = WorldState.fromJson(jsonDecode(jsonEncode(depleted.toJson())) as Map<String, dynamic>);
    expect(loaded.heartRegenAnchor, now);
    expect(WorldHearts.regenerate(loaded, now.add(const Duration(minutes: 95))).hearts, 3);
    final full = WorldHearts.regenerate(loaded, now.add(const Duration(days: 10)));
    expect(full.hearts, 7);
    final lost = WorldHearts.lose(full, now.add(const Duration(days: 10)));
    expect(lost.hearts, 6);
    expect(WorldHearts.nextIn(lost, now.add(const Duration(days: 10))), WorldHearts.interval);
  });

  test('legacy depleted save starts timer and backward clock grants no lives', () {
    final legacy = WorldState.initial().copyWith(hearts: 0);
    final started = WorldHearts.regenerate(legacy, now);
    expect(started.heartRegenAnchor, now);
    final back = WorldHearts.regenerate(started, now.subtract(const Duration(hours: 1)));
    expect(back.hearts, 0);
    expect(WorldHearts.nextIn(back, now.subtract(const Duration(hours: 1))), WorldHearts.interval);
  });

  test('Run is blocked at zero and resumes automatically at next life', () {
    final s = WorldState.initial().copyWith(hearts: 0, heartRegenAnchor: now);
    final task = WorldChallenges.at(s, WorldMode.infinite);
    final blocked = WorldRules.submit(s, WorldMode.infinite, task.id, task.answer, now);
    expect(blocked.correct, isFalse);
    final resumed = WorldRules.submit(s, WorldMode.infinite, task.id, task.answer,
      now.add(const Duration(minutes: 30)));
    expect(resumed.correct, isTrue);
    expect(resumed.state.hearts, 1);
  });

  test('restoration persists, and rapid paid refills charge once before restart', () async {
    final clock = FixedClock(now);
    final initial = WorldState.initial().copyWith(hearts: 0, heartRegenAnchor: now);
    final store = InMemoryKeyValueStore({'bytecraft_world_state': jsonEncode({...initial.toJson(), 'schemaVersion': 2})});
    ProviderContainer container() => ProviderContainer(overrides: [
      keyValueStoreProvider.overrideWithValue(store), clockProvider.overrideWithValue(clock)]);
    final c = container();
    addTearDown(c.dispose);
    await c.read(worldControllerProvider.future);
    clock.advance(const Duration(minutes: 35));
    await c.read(worldControllerProvider.notifier).refreshHearts();
    expect(c.read(worldControllerProvider).value!.hearts, 1);
    await Future.wait(List.generate(8, (_) => c.read(worldControllerProvider.notifier).reviveInfinite()));
    final restored = container();
    addTearDown(restored.dispose);
    final s = await restored.read(worldControllerProvider.future);
    expect(s.hearts, s.maxHearts);
    expect(s.gems, 2);
    expect(s.heartRegenAnchor, isNull);
  });

  testWidgets('phone panel shows empty hearts, countdown, free restore and paid refill', (tester) async {
    tester.view.physicalSize = const Size(320, 950);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.reset);
    final clock = FixedClock(now);
    final initial = WorldState.initial().copyWith(hearts: 0, gems: 0, heartRegenAnchor: now);
    final store = InMemoryKeyValueStore({'bytecraft_world_state': jsonEncode({...initial.toJson(), 'schemaVersion': 2})});
    final c = ProviderContainer(overrides: [keyValueStoreProvider.overrideWithValue(store), clockProvider.overrideWithValue(clock)]);
    addTearDown(c.dispose);
    await c.read(worldControllerProvider.future);
    await tester.pumpWidget(UncontrolledProviderScope(container: c,
      child: const MaterialApp(home: Scaffold(body: SingleChildScrollView(child: WorldHeartsPanel())))));
    await tester.pumpAndSettle();
    expect(find.text('Жизни забега: 0/3'), findsOneWidget);
    expect(find.byIcon(Icons.favorite_border_rounded), findsNWidgets(3));
    expect(find.text('Следующая жизнь через 30:00'), findsOneWidget);
    expect(find.textContaining('Нет алмазов'), findsOneWidget);
    clock.advance(const Duration(minutes: 30));
    await tester.pump(const Duration(seconds: 1));
    await tester.pumpAndSettle();
    expect(find.text('Жизни забега: 1/3'), findsOneWidget);
    expect(find.byIcon(Icons.favorite_rounded), findsOneWidget);
    clock.advance(const Duration(hours: 1));
    await tester.pump(const Duration(seconds: 1));
    await tester.pumpAndSettle();
    expect(find.text('Жизни забега: 3/3'), findsOneWidget);
    expect(find.text('Все жизни восстановлены'), findsOneWidget);
    expect(tester.takeException(), isNull);
    await tester.pumpWidget(const SizedBox.shrink());
  });
}
