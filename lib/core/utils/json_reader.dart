/// Thrown when externally supplied JSON (content, cache, backend) is invalid.
class JsonFormatException implements Exception {
  const JsonFormatException(this.message);

  final String message;

  @override
  String toString() => 'JsonFormatException: $message';
}

/// Typed, path-aware accessor for decoded JSON objects.
///
/// Error messages include the JSON path, which makes broken content
/// files easy to locate.
class JsonReader {
  const JsonReader(this.raw, [this.path = r'$']);

  final Map<String, dynamic> raw;
  final String path;

  bool has(String key) => raw.containsKey(key) && raw[key] != null;

  Never _fail(String key, String expected) => throw JsonFormatException(
        '$path.$key: expected $expected, got ${raw[key]?.runtimeType}',
      );

  String requireString(String key) {
    final value = raw[key];
    if (value is String && value.isNotEmpty) return value;
    _fail(key, 'non-empty string');
  }

  String? optionalString(String key) {
    final value = raw[key];
    if (value == null) return null;
    if (value is String) return value;
    _fail(key, 'string');
  }

  int requireInt(String key) {
    final value = raw[key];
    if (value is int) return value;
    _fail(key, 'int');
  }

  int? optionalInt(String key) {
    final value = raw[key];
    if (value == null) return null;
    if (value is int) return value;
    _fail(key, 'int');
  }

  bool optionalBool(String key, {required bool fallback}) {
    final value = raw[key];
    if (value == null) return fallback;
    if (value is bool) return value;
    _fail(key, 'bool');
  }

  List<String> requireStringList(String key) {
    final value = raw[key];
    if (value is List && value.every((element) => element is String)) {
      return List<String>.unmodifiable(value.cast<String>());
    }
    _fail(key, 'list of strings');
  }

  List<int> requireIntList(String key) {
    final value = raw[key];
    if (value is List && value.every((element) => element is int)) {
      return List<int>.unmodifiable(value.cast<int>());
    }
    _fail(key, 'list of ints');
  }

  List<List<int>> optionalIntMatrix(String key) {
    final value = raw[key];
    if (value == null) return const [];
    if (value is List) {
      final result = <List<int>>[];
      for (final row in value) {
        if (row is List && row.every((element) => element is int)) {
          result.add(List<int>.unmodifiable(row.cast<int>()));
        } else {
          _fail(key, 'list of int lists');
        }
      }
      return List.unmodifiable(result);
    }
    _fail(key, 'list of int lists');
  }

  JsonReader requireObject(String key) {
    final value = raw[key];
    if (value is Map<String, dynamic>) return JsonReader(value, '$path.$key');
    _fail(key, 'object');
  }

  List<JsonReader> requireObjectList(String key) {
    final value = raw[key];
    if (value is! List) _fail(key, 'list of objects');
    final result = <JsonReader>[];
    for (var i = 0; i < value.length; i++) {
      final element = value[i];
      if (element is Map<String, dynamic>) {
        result.add(JsonReader(element, '$path.$key[$i]'));
      } else {
        throw JsonFormatException('$path.$key[$i]: expected object');
      }
    }
    return result;
  }
}
