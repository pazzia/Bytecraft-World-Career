import 'course.dart';
import 'course_summary.dart';

/// Single entry point for educational content.
///
/// Implementations decide where content comes from (bundled JSON,
/// cache, remote API); callers never know.
abstract interface class ContentRepository {
  Future<List<CourseSummary>> loadCatalog();

  Future<Course> loadCourse(String courseId);

  /// Pulls a newer version from the remote source into the cache.
  /// Returns true if content changed. Never throws on network errors.
  Future<bool> refreshCourse(String courseId);
}
