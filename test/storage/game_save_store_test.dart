import 'package:bytecraft/core/storage/game_save_store.dart';
import 'package:bytecraft/core/storage/key_value_store.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('nested writes commit once; failure rolls back every document', () async {
    final source = _Disk();
    final save = GameSaveStore(source);
    await save.transaction(() async {
      await save.write('player.course.python', 'completed');
      await save.transaction(() => save.write('bytecraft_world_state', 'reward'));
    });
    expect(source.writes, 1);
    source.fail = true;
    await expectLater(save.transaction(() async {
      await save.write('player.course.python', 'changed');
      await save.write('bytecraft_world_state', 'doubled');
    }), throwsStateError);
    final restarted = GameSaveStore(source);
    expect(await restarted.read('player.course.python'), 'completed');
    expect(await restarted.read('bytecraft_world_state'), 'reward');
    source.fail = false;
    await save.write('bytecraft_world_state', 'retry');
    expect(await restarted.read('bytecraft_world_state'), 'retry');
  });

  test('parallel actions serialize without lost updates', () async {
    final save = GameSaveStore(InMemoryKeyValueStore());
    await Future.wait(List.generate(30, (_) => save.transaction(() async {
      final before = int.parse(await save.read('player.coins') ?? '0');
      await Future<void>.delayed(Duration.zero);
      await save.write('player.coins', '${before + 1}');
    })));
    expect(await save.read('player.coins'), '30');
  });

  test('reset cannot resurrect legacy documents and preserves settings', () async {
    final source = InMemoryKeyValueStore({
      'player.course.python': 'old progress',
      'player.course.other': 'old unopened course',
      'app.settings': 'career goal',
    });
    final save = GameSaveStore(source);
    await save.deletePrefix('player.');
    final restarted = GameSaveStore(source);
    expect(await restarted.read('player.course.python'), isNull);
    expect(await restarted.read('player.course.other'), isNull);
    expect(await restarted.read('app.settings'), 'career goal');
    await restarted.write('player.course.python', 'new progress');
    expect(await GameSaveStore(source).read('player.course.python'), 'new progress');
  });

  test('unknown or corrupt aggregate is not replaced by an empty save', () async {
    for (final data in ['broken', '{"schemaVersion":99}']) {
      final source = InMemoryKeyValueStore({GameSaveStore.saveKey: data});
      final save = GameSaveStore(source);
      await expectLater(save.write('player.coins', '0'), throwsA(anything));
      expect(await source.read(GameSaveStore.saveKey), data);
    }
  });
}

class _Disk extends InMemoryKeyValueStore {
  bool fail = false;
  int writes = 0;
  @override
  Future<void> write(String key, String value) async {
    if (fail) throw StateError('disk full');
    writes++;
    await super.write(key, value);
  }
}
