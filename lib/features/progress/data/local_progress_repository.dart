import '../../../core/storage/json_document_store.dart';
import '../../../core/storage/storage_keys.dart';
import '../../../core/time/clock.dart';
import '../../../core/utils/id_generator.dart';
import '../../gamification/domain/game_rules.dart';
import '../domain/course_progress.dart';
import '../domain/progress_repository.dart';
import '../domain/user_profile.dart';

/// Offline-first player state stored as JSON documents.
///
/// Every write marks the data as "dirty" so the SyncCoordinator can push
/// it to the backend once the device is online.
class LocalProgressRepository implements ProgressRepository {
  LocalProgressRepository({
    required JsonDocumentStore documents,
    required Clock clock,
    required GameRules rules,
    required IdGenerator ids,
  })  : _documents = documents,
        _clock = clock,
        _rules = rules,
        _ids = ids;

  final JsonDocumentStore _documents;
  final Clock _clock;
  final GameRules _rules;
  final IdGenerator _ids;

  @override
  Future<UserProfile> loadProfile() async {
    final json = await _documents.read(StorageKeys.profile);
    if (json != null && json['userId'] is String) {
      return UserProfile.fromJson(json, _rules);
    }
    final profile = UserProfile.create(
      userId: _ids.newId(),
      now: _clock.now(),
      rules: _rules,
    );
    await saveProfile(profile);
    return profile;
  }

  @override
  Future<void> saveProfile(UserProfile profile) async {
    await _documents.write(
      StorageKeys.profile,
      profile.toJson(),
      schemaVersion: StorageKeys.profileSchema,
    );
    await _markDirty();
  }

  @override
  Future<CourseProgress> loadCourseProgress(String courseId) async {
    final json = await _documents.read(StorageKeys.courseProgress(courseId));
    if (json == null || json['courseId'] != courseId) {
      return CourseProgress(courseId: courseId);
    }
    return CourseProgress.fromJson(json);
  }

  @override
  Future<void> saveCourseProgress(CourseProgress progress) async {
    await _documents.write(
      StorageKeys.courseProgress(progress.courseId),
      progress.toJson(),
      schemaVersion: StorageKeys.courseProgressSchema,
    );
    await _markDirty();
  }

  @override
  Future<void> resetAll() async {
    await _documents.raw.deletePrefix(StorageKeys.playerPrefix);
    await _markDirty();
  }

  Future<void> _markDirty() =>
      _documents.raw.write(StorageKeys.syncDirty, _clock.now().toIso8601String());
}
