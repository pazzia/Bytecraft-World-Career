import 'dart:async';
import 'dart:developer' as developer;

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../features/courses/domain/content_repository.dart';
import '../../features/settings/presentation/settings_controller.dart';
import '../../services/analytics/analytics_service.dart';
import '../../services/sync/cloud_sync.dart';
import '../di/providers.dart';

/// Everything that must happen before the first real screen.
///
/// Network work (content refresh, cloud sync) is fire-and-forget so the app
/// starts instantly offline.
final appStartupProvider = FutureProvider<void>((ref) async {
  // read, not watch: later settings changes must not re-run startup.
  final settings = await ref.read(settingsControllerProvider.future);
  await ref.read(featureFlagsProvider).refresh();
  final profile = await ref.read(progressRepositoryProvider).loadProfile();

  final analytics = ref.read(analyticsProvider)..setUserId(profile.userId);
  analytics.track(AnalyticsEvent.appOpen);

  final courseId = settings.activeCourseId;
  final content = ref.read(contentRepositoryProvider);
  // Warm the content cache so the map opens instantly.
  await content.loadCourse(courseId);

  unawaited(
    _backgroundSync(
      content: content,
      sync: ref.read(syncCoordinatorProvider),
      courseId: courseId,
    ),
  );
});

Future<void> _backgroundSync({
  required ContentRepository content,
  required SyncCoordinator sync,
  required String courseId,
}) async {
  try {
    await content.refreshCourse(courseId);
    await sync.syncIfNeeded(courseIds: [courseId]);
  } catch (error) {
    developer.log('Background startup task failed: $error', name: 'startup');
  }
}
