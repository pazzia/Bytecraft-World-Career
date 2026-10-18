import 'dart:async';
import 'dart:convert';

import 'key_value_store.dart';

/// One durable write commits an entire player action. Legacy documents are
/// imported lazily, without adding prototype balances together. Tombstones keep
/// a reset from resurrecting the old documents that remain on disk.
class GameSaveStore implements KeyValueStore {
  GameSaveStore(this.source);
  static const saveKey = 'game.save.v1';
  final KeyValueStore source;
  final _zoneKey = Object();
  final _changes = StreamController<int>.broadcast(sync: true);
  Future<void> _tail = Future.value();
  int _revision = 0;
  Stream<int> get changes => _changes.stream;
  bool _owns(String key) => key.startsWith('player.') ||
      key == 'bytecraft_world_state' || key == 'app.settings' || key == 'sync.dirty';

  Future<T> transaction<T>(Future<T> Function() action) {
    if (Zone.current[_zoneKey] != null) return action();
    final done = Completer<T>();
    _tail = _tail.then((_) async {
      try {
        final raw = await source.read(saveKey);
        final json = raw == null ? <String, dynamic>{} : jsonDecode(raw) as Map<String, dynamic>;
        if (raw != null && json['schemaVersion'] != 1) {
          throw StateError('Unsupported game save version');
        }
        final tx = _Transaction(
          Map<String, String?>.from(json['documents'] as Map? ?? {}),
          List<String>.from(json['deletedPrefixes'] as List? ?? []),
        );
        final result = await runZoned(action, zoneValues: {_zoneKey: tx});
        if (tx.dirty) {
          await source.write(saveKey, jsonEncode({
            'schemaVersion': 1,
            'documents': tx.documents,
            'deletedPrefixes': tx.deletedPrefixes,
          }));
          _changes.add(++_revision);
        }
        done.complete(result);
      } catch (error, stack) {
        done.completeError(error, stack);
      }
    });
    return done.future;
  }

  @override
  Future<String?> read(String key) => !_owns(key) ? source.read(key) : transaction(() async {
        final tx = Zone.current[_zoneKey] as _Transaction;
        if (tx.documents.containsKey(key)) return tx.documents[key];
        if (tx.deletedPrefixes.any(key.startsWith)) return null;
        final legacy = await source.read(key);
        // Cache reads within this action; persist them together with its writes.
        tx.documents[key] = legacy;
        return legacy;
      });

  @override
  Future<void> write(String key, String value) => !_owns(key) ? source.write(key, value) : transaction(() async {
        final tx = Zone.current[_zoneKey] as _Transaction;
        if (await read(key) == value) return;
        tx.documents[key] = value;
        tx.dirty = true;
      });

  @override
  Future<void> delete(String key) => !_owns(key) ? source.delete(key) : transaction(() async {
        final tx = Zone.current[_zoneKey] as _Transaction;
        tx.documents[key] = null;
        tx.dirty = true;
      });

  @override
  Future<void> deletePrefix(String prefix) => transaction(() async {
        final tx = Zone.current[_zoneKey] as _Transaction;
        tx.documents.removeWhere((key, _) => key.startsWith(prefix));
        if (!tx.deletedPrefixes.contains(prefix)) tx.deletedPrefixes.add(prefix);
        tx.dirty = true;
      });
}

class _Transaction {
  _Transaction(this.documents, this.deletedPrefixes);
  final Map<String, String?> documents;
  final List<String> deletedPrefixes;
  bool dirty = false;
}
