/// Build-time configuration. Values can be supplied with
/// `--dart-define=CONTENT_BASE_URL=https://...`.
class AppConfig {
  const AppConfig({
    required this.defaultCourseId,
    required this.contentBaseUrl,
    required this.networkTimeout,
  });

  factory AppConfig.fromEnvironment() => const AppConfig(
        defaultCourseId: 'python',
        contentBaseUrl: String.fromEnvironment('CONTENT_BASE_URL'),
        networkTimeout: Duration(seconds: 10),
      );

  final String defaultCourseId;

  /// Empty string means "remote content disabled" (bundled content only).
  final String contentBaseUrl;
  final Duration networkTimeout;

  bool get remoteContentEnabled => contentBaseUrl.isNotEmpty;
}
