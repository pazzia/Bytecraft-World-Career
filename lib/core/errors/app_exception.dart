/// Base type for expected, recoverable failures surfaced to the UI.
sealed class AppException implements Exception {
  const AppException(this.message);

  final String message;

  @override
  String toString() => '$runtimeType: $message';
}

class ContentNotFoundException extends AppException {
  const ContentNotFoundException(super.message);
}

class ContentFormatException extends AppException {
  const ContentFormatException(super.message);
}

class UnsupportedLevelTypeException extends AppException {
  const UnsupportedLevelTypeException(super.message);
}

class InvalidLevelStateException extends AppException {
  const InvalidLevelStateException(super.message);
}
