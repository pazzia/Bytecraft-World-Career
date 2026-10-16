import 'course_progress.dart';
import 'user_profile.dart';

/// Persistence port for player state. Local-first: implementations must
/// work offline and mark data for cloud sync.
abstract interface class ProgressRepository {
  /// Returns the stored profile or creates (and persists) a new one.
  Future<UserProfile> loadProfile();

  Future<void> saveProfile(UserProfile profile);

  Future<CourseProgress> loadCourseProgress(String courseId);

  Future<void> saveCourseProgress(CourseProgress progress);

  /// Wipes all player data (profile + every course).
  Future<void> resetAll();
}
