import 'dart:convert';
import 'dart:developer' as developer;

import 'key_value_store.dart';

/// Stores JSON documents on top of a [KeyValueStore].
///
/// Every document carries a `schemaVersion`; corrupted or unknown documents
/// are treated as missing so the app falls back to defaults instead of
/// crashing on start.
class JsonDocumentStore {
  const JsonDocumentStore(this._store);

  static const String schemaVersionKey = 'schemaVersion';

  final KeyValueStore _store;

  KeyValueStore get raw => _store;

  Future<Map<String, dynamic>?> read(String key) async {
    final raw = await _store.read(key);
    if (raw == null) return null;
    try {
      final decoded = jsonDecode(raw);
      if (decoded is Map<String, dynamic>) return decoded;
    } on FormatException catch (error) {
      developer.log('Corrupted document "$key": $error', name: 'storage');
    }
    return null;
  }

  Future<void> write(
    String key,
    Map<String, dynamic> document, {
    required int schemaVersion,
  }) {
    final payload = {...document, schemaVersionKey: schemaVersion};
    return _store.write(key, jsonEncode(payload));
  }

  Future<void> delete(String key) => _store.delete(key);
}
