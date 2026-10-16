import 'dart:developer' as developer;

import '../../core/storage/key_value_store.dart';
import '../../core/storage/storage_keys.dart';
import '../../features/progress/domain/course_progress.dart';
import '../../features/progress/domain/progress_repository.dart';
import '../../features/progress/domain/user_profile.dart';

class SyncSnapshot {
  const SyncSnapshot({required this.profile, required this.courses});

  final UserProfile profile;
  final List<CourseProgress> courses;
}

enum SyncStatus { synced, offline, failed, notConfigured }

/// Backend sync port (account, cloud save). Conflict resolution lives on
/// the server; the client sends its full local snapshot.
abstract interface class CloudSyncService {
  Future<SyncStatus> push(SyncSnapshot snapshot);
}

class NoopCloudSyncService implements CloudSyncService {
  const NoopCloudSyncService();

  @override
  Future<SyncStatus> push(SyncSnapshot snapshot) async =>
      SyncStatus.notConfigured;
}

/// Pushes local changes when the repository has marked them dirty.
class SyncCoordinator {
  SyncCoordinator({
    required ProgressRepository progress,
    required KeyValueStore store,
    required CloudSyncService cloud,
  })  : _progress = progress,
        _store = store,
        _cloud = cloud;

  final ProgressRepository _progress;
  final KeyValueStore _store;
  final CloudSyncService _cloud;
  bool _running = false;

  Future<SyncStatus?> syncIfNeeded({required List<String> courseIds}) async {
    if (_running) return null;
    final dirtyMarker = await _store.read(StorageKeys.syncDirty);
    if (dirtyMarker == null) return SyncStatus.synced;
    _running = true;
    try {
      final snapshot = SyncSnapshot(
        profile: await _progress.loadProfile(),
        courses: [
          for (final id in courseIds) await _progress.loadCourseProgress(id),
        ],
      );
      final status = await _cloud.push(snapshot);
      final current = await _store.read(StorageKeys.syncDirty);
      // Only clear if nothing changed while we were pushing.
      if (status == SyncStatus.synced && current == dirtyMarker) {
        await _store.delete(StorageKeys.syncDirty);
      }
      return status;
    } catch (error) {
      developer.log('Sync failed: $error', name: 'sync');
      return SyncStatus.failed;
    } finally {
      _running = false;
    }
  }
}
