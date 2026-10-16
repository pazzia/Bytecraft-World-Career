/// Version of this build, shown in the profile so the player can tell
/// which release is installed. CI passes the values with
/// `--dart-define=APP_VERSION=0.1.0 --dart-define=BUILD_NUMBER=21`.
abstract final class BuildInfo {
  static const String version =
      String.fromEnvironment('APP_VERSION', defaultValue: 'dev');
  static const String buildNumber = String.fromEnvironment('BUILD_NUMBER');

  /// "0.1.0 (сборка 21)", or just "dev" for local builds.
  static String get label =>
      buildNumber.isEmpty ? version : '$version (сборка $buildNumber)';
}
