import 'dart:io';

import 'package:bytecraft/core/storage/game_save_store.dart';
import 'package:bytecraft/core/storage/json_document_store.dart';
import 'package:bytecraft/core/storage/key_value_store.dart';
import 'package:bytecraft/core/time/clock.dart';
import 'package:bytecraft/features/world/data/world_repository.dart';
import 'package:bytecraft/features/world/domain/repair_catalog.dart';
import 'package:bytecraft/features/world/domain/repair_service.dart';
import 'package:bytecraft/features/world/domain/skill_repair.dart';
import 'package:bytecraft/features/world/domain/world_challenge.dart';
import 'package:bytecraft/features/world/domain/world_rules.dart';
import 'package:bytecraft/features/world/domain/world_state.dart';
import 'package:flutter_test/flutter_test.dart';

class Env {
  Env({InMemoryKeyValueStore? source}) {
    raw = source ?? InMemoryKeyValueStore();
    save = GameSaveStore(raw);
    world = WorldRepository(JsonDocumentStore(save), clock, save);
    service = RepairService(
      save,
      world,
      (path) => File(path).readAsString(),
      clock,
    );
  }
  final clock = FixedClock(DateTime(2026, 10, 19, 22));
  late final InMemoryKeyValueStore raw;
  late final GameSaveStore save;
  late final WorldRepository world;
  late final RepairService service;
  Future<SkillRepair> seed() async {
    final q = WorldChallenges.at(WorldState.initial(), WorldMode.training);
    final result = WorldRules.submit(
      WorldState.initial(),
      WorldMode.training,
      q.id,
      'WRONG',
      clock.now(),
    );
    await world.write(result.state);
    return result.state.repairs.values.single;
  }
}

void main() {
  test('the repaired original does not prove learning; a distinct example does and survives restart', () async {
    final env = Env();
    var record = await env.seed();
    var s = await env.world.load();
    final original = WorldChallenges.at(s, WorldMode.training);
    s = WorldRules.submit(
      s,
      WorldMode.training,
      original.id,
      original.answer,
      env.clock.now(),
    ).state;
    expect(s.repairs[record.skillId]!.pending, isTrue);
    expect(s.mistakes['Условия'], 1);
    await env.world.write(s);
    final catalog = await env.service.catalog();
    final example = catalog.next(record)!;
    expect(
      SkillRepair.signature(example.code, example.stdin),
      isNot(SkillRepair.signature(original.code)),
    );
    expect(
      (await env.service.submit(
        record.skillId,
        record.generation,
        example.id,
        example.answer,
      )).passed,
      isTrue,
    );
    final restored = Env(source: env.raw);
    final saved = await restored.world.load();
    record = saved.repairs[record.skillId]!;
    expect(record.pending, isFalse);
    expect(record.proofs.single['exampleId'], example.id);
    expect(
      record.proofs.single['verifiedAt'],
      env.clock.now().toIso8601String(),
    );
    expect(saved.mistakes['Условия'], 0);
  });

  test('a shown answer consumes its example; only another clean example can confirm', () async {
    final env = Env();
    var r = await env.seed();
    final catalog = await env.service.catalog();
    final first = catalog.next(r)!;
    await env.service.submit(r.skillId, r.generation, first.id, 'WRONG');
    r = (await env.world.load()).repairs[r.skillId]!;
    expect(r.pending, isTrue);
    expect(catalog.next(r)!.id, isNot(first.id));
    expect(
      (await env.service.submit(
        r.skillId,
        r.generation,
        first.id,
        first.answer,
      )).passed,
      isFalse,
    );
    final second = catalog.next(r)!;
    expect(
      (await env.service.submit(
        r.skillId,
        r.generation,
        second.id,
        second.answer,
      )).passed,
      isTrue,
    );
  });

  test('parallel duplicate verification awards once and does not clear another skill', () async {
    final env = Env();
    final r = await env.seed();
    var state = await env.world.load();
    state = WorldRules.recordError(
      state,
      skillId: 'another',
      title: 'Другая ошибка',
      category: 'Циклы',
      sourceCode: 'other',
    );
    await env.world.write(state);
    final e = (await env.service.catalog()).next(r)!;
    final results = await Future.wait(
      List.generate(
        8,
        (_) => env.service.submit(r.skillId, r.generation, e.id, e.answer),
      ),
    );
    expect(results.where((r) => r.passed).length, 1);
    final saved = await env.world.load();
    expect(saved.worldXp, 30);
    expect(saved.coins, 12);
    expect(saved.repairs['another']!.pending, isTrue);
    expect(saved.mistakes['Циклы'], 1);
  });

  test('save failure commits neither reward, consumed example nor proof; retry works', () async {
    final disk = FailingDisk();
    final env = Env(source: disk);
    final r = await env.seed();
    final e = (await env.service.catalog()).next(r)!;
    disk.fail = true;
    await expectLater(
      env.service.submit(r.skillId, r.generation, e.id, e.answer),
      throwsStateError,
    );
    disk.fail = false;
    final saved = await env.world.load();
    expect(saved.repairs[r.skillId]!.seen, isEmpty);
    expect(saved.repairs[r.skillId]!.proofs, isEmpty);
    expect(saved.coins, 0);
    expect(
      (await env.service.submit(
        r.skillId,
        r.generation,
        e.id,
        e.answer,
      )).passed,
      isTrue,
    );
  });

  test(
    'a new mistake reopens the same skill without losing previous evidence',
    () async {
      final env = Env();
      final r = await env.seed();
      final bank = await env.service.catalog();
      final e = bank.next(r)!;
      await env.service.submit(r.skillId, r.generation, e.id, e.answer);
      var saved = await env.world.load();
      saved = WorldRules.recordError(
        saved,
        skillId: r.skillId,
        title: r.title,
        category: r.category,
        sourceCode: 'new mistake',
      );
      await env.world.write(saved);
      final reopened = saved.repairs[r.skillId]!;
      expect(reopened.pending, isTrue);
      expect(reopened.proofs.length, 1);
      expect(bank.next(reopened)!.id, isNot(e.id));
      expect(
        (await env.service.submit(
          r.skillId,
          r.generation,
          e.id,
          e.answer,
        )).passed,
        isFalse,
      );
    },
  );

  test('empty answers and an exhausted bank cannot create proof', () async {
    final env = Env();
    final r = await env.seed();
    final bank = await env.service.catalog();
    final e = bank.next(r)!;
    expect(
      (await env.service.submit(r.skillId, r.generation, e.id, '')).passed,
      isFalse,
    );
    expect((await env.world.load()).repairs[r.skillId]!.seen, isEmpty);
    final empty = RepairCatalog({});
    expect(empty.next(r), isNull);
    expect(r.pending, isTrue);
  });
}

class FailingDisk extends InMemoryKeyValueStore {
  bool fail = false;
  @override
  Future<void> write(String key, String value) async {
    if (fail) throw StateError('disk full');
    await super.write(key, value);
  }
}
