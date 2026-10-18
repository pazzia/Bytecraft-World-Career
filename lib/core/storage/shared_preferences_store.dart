import 'package:shared_preferences/shared_preferences.dart';

import 'key_value_store.dart';

/// [KeyValueStore] adapter backed by SharedPreferences.
///
/// All app keys live under one namespace so a reset never touches
/// keys written by third-party plugins.
class SharedPreferencesStore implements KeyValueStore {
  SharedPreferencesStore(this._prefs, {this.namespace = 'bytecraft.'});

  final SharedPreferences _prefs;
  final String namespace;

  String _k(String key) => '$namespace$key';

  @override
  Future<String?> read(String key) async => _prefs.getString(_k(key));

  @override
  Future<void> write(String key, String value) async {
    if (!await _prefs.setString(_k(key), value)) {
      throw StateError('Could not persist $key');
    }
  }

  @override
  Future<void> delete(String key) async {
    await _prefs.remove(_k(key));
  }

  @override
  Future<void> deletePrefix(String prefix) async {
    final fullPrefix = _k(prefix);
    final keys =
        _prefs.getKeys().where((key) => key.startsWith(fullPrefix)).toList();
    for (final key in keys) {
      await _prefs.remove(key);
    }
  }
}
