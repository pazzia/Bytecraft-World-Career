/// Minimal persistence port. The app depends on this interface only;
/// concrete engines (SharedPreferences today, Drift/SQLite later) are adapters.
abstract interface class KeyValueStore {
  Future<String?> read(String key);

  Future<void> write(String key, String value);

  Future<void> delete(String key);

  /// Deletes every key starting with [prefix].
  Future<void> deletePrefix(String prefix);
}

/// Volatile implementation for tests and previews.
class InMemoryKeyValueStore implements KeyValueStore {
  InMemoryKeyValueStore([Map<String, String>? initial])
      : _data = {...?initial};

  final Map<String, String> _data;

  Map<String, String> get snapshot => Map.unmodifiable(_data);

  @override
  Future<String?> read(String key) async => _data[key];

  @override
  Future<void> write(String key, String value) async => _data[key] = value;

  @override
  Future<void> delete(String key) async => _data.remove(key);

  @override
  Future<void> deletePrefix(String prefix) async =>
      _data.removeWhere((key, _) => key.startsWith(prefix));
}
