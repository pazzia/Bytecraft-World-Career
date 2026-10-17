/// Central registry of persistence keys and schema versions.
///
/// Bump a schema version together with a migration in the owning repository.
abstract final class StorageKeys {
  static const String profile = 'player.profile';
  static const int profileSchema = 1;

  static const String courseProgressPrefix = 'player.course.';
  static String courseProgress(String courseId) =>
      '$courseProgressPrefix$courseId';
  static const int courseProgressSchema = 1;

  static String timedProgress(String courseId) => 'player.timed.$courseId';
  static const int timedProgressSchema = 1;

  static String journal(String courseId) => 'player.journal.$courseId';
  static const int journalSchema = 1;

  static const String settings = 'app.settings';
  static const int settingsSchema = 1;

  static const String contentCachePrefix = 'content.cache.';
  static String contentCache(String courseId) => '$contentCachePrefix$courseId';
  static const int contentCacheSchema = 1;

  static const String syncDirty = 'sync.dirty';

  /// Everything that belongs to the player (used by "reset progress").
  static const String playerPrefix = 'player.';
}
