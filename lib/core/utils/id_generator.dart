import 'dart:math';

/// Generates opaque identifiers (local user ids, event ids).
abstract interface class IdGenerator {
  String newId();
}

class RandomIdGenerator implements IdGenerator {
  RandomIdGenerator([Random? random]) : _random = random ?? Random.secure();

  static const int _bytes = 16;

  final Random _random;

  @override
  String newId() {
    final buffer = StringBuffer();
    for (var i = 0; i < _bytes; i++) {
      buffer.write(_random.nextInt(256).toRadixString(16).padLeft(2, '0'));
    }
    return buffer.toString();
  }
}
