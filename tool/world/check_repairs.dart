// Offline integration: actual repair service, catalogue and atomic saves.
import 'dart:convert';
import 'dart:io';

import '../../lib/core/storage/game_save_store.dart';
import '../../lib/core/storage/json_document_store.dart';
import '../../lib/core/storage/key_value_store.dart';
import '../../lib/core/time/clock.dart';
import '../../lib/features/world/data/world_repository.dart';
import '../../lib/features/world/domain/repair_service.dart';
import '../../lib/features/world/domain/world_challenge.dart';
import '../../lib/features/world/domain/world_rules.dart';
import '../../lib/features/world/domain/world_state.dart';

void check(bool value, String message) {
  if (!value) throw StateError(message);
}

Future<void> main() async {
  final raw = InMemoryKeyValueStore();
  final save = GameSaveStore(raw);
  final clock = FixedClock(DateTime(2026, 10, 19));
  final world = WorldRepository(JsonDocumentStore(save), clock, save);
  final service = RepairService(
    save,
    world,
    (p) => File(p).readAsString(),
    clock,
  );
  final catalog = await service.catalog();
  check(catalog.skills.length >= 267, 'Missing concrete skills');
  for (final category in WorldState.initial().mistakes.keys) {
    for (var n = 0; n < 20; n++) {
      check(
        catalog.skills.containsKey('dna:$category:$n'),
        'Missing DNA concept',
      );
    }
  }
  for (final topic
      in (jsonDecode(
            File('assets/content/python/topics.json').readAsStringSync(),
          ) as Map)['topics']
          as List) {
    check(
      catalog.skills.containsKey('topic:python:${topic['id']}'),
      'Missing course topic',
    );
  }
  var state = WorldState.initial();
  final original = WorldChallenges.at(state, WorldMode.training);
  state = WorldRules.submit(
    state,
    WorldMode.training,
    original.id,
    'WRONG',
    clock.now(),
  ).state;
  state = WorldRules.submit(
    state,
    WorldMode.training,
    original.id,
    original.answer,
    clock.now(),
  ).state;
  check(
    state.mistakes['Условия'] == 1,
    'Original answer incorrectly confirmed learning',
  );
  await world.write(state);
  var repair = state.repairs.values.single;
  final first = catalog.next(repair)!;
  await service.submit(repair.skillId, repair.generation, first.id, 'WRONG');
  repair = (await world.load()).repairs[repair.skillId]!;
  final second = catalog.next(repair)!;
  check(second.id != first.id, 'Disclosed example repeated');
  check(
    !(await service.submit(
      repair.skillId,
      repair.generation,
      first.id,
      first.answer,
    )).passed,
    'Disclosed answer was accepted',
  );
  final results = await Future.wait(
    List.generate(
      8,
      (_) => service.submit(
        repair.skillId,
        repair.generation,
        second.id,
        second.answer,
      ),
    ),
  );
  check(results.where((r) => r.passed).length == 1, 'Duplicate proof/reward');
  // Use a single transaction owner for every repository instance.
  final restartedSave = GameSaveStore(raw);
  final restarted = WorldRepository(
    JsonDocumentStore(restartedSave),
    clock,
    restartedSave,
  );
  final loaded = await restarted.load();
  check(
    loaded.repairs[repair.skillId]!.proofs.length == 1,
    'Proof lost on restart',
  );
  check(loaded.mistakes['Условия'] == 0, 'Concrete error not cleared');
  check(loaded.coins == state.coins + 12, 'Incorrect repair reward');
  // Keep the old broad counts; no synthetic evidence is created for them.
  check(
    WorldState.fromJson({
      'mistakes': {'Условия': 19},
    }).repairs.isEmpty,
    'Invented legacy proof',
  );
  print(
    'Repair service: concrete topics, independent examples, stale answers, duplicate rewards and restart passed',
  );
}
