import 'package:dio/dio.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/config/app_config.dart';
import '../../core/storage/json_document_store.dart';
import '../../core/storage/key_value_store.dart';
import '../../core/time/clock.dart';
import '../../core/utils/id_generator.dart';
import '../../features/courses/data/content_sources.dart';
import '../../features/courses/data/default_content_repository.dart';
import '../../features/courses/data/dio_remote_content_source.dart';
import '../../features/courses/domain/content_repository.dart';
import '../../features/daily_challenge/data/local_daily_challenge_service.dart';
import '../../features/daily_challenge/domain/daily_challenge.dart';
import '../../features/gamification/domain/game_rules.dart';
import '../../features/leaderboard/data/mock_leaderboard_repository.dart';
import '../../features/leaderboard/domain/leaderboard.dart';
import '../../features/level/engine/answer_validator.dart';
import '../../features/level/engine/level_engine.dart';
import '../../features/metagame/data/mock_metagame_service.dart';
import '../../features/metagame/domain/metagame.dart';
import '../../features/progress/data/local_progress_repository.dart';
import '../../features/progress/domain/progress_repository.dart';
import '../../features/settings/data/local_settings_repository.dart';
import '../../features/settings/domain/settings_repository.dart';
import '../../features/shop/domain/economy_service.dart';
import '../../services/ai_tutor/ai_tutor_service.dart';
import '../../services/analytics/analytics_service.dart';
import '../../services/auth/auth_service.dart';
import '../../services/code_execution/code_execution_service.dart';
import '../../services/feature_flags/feature_flag_service.dart';
import '../../services/monetization/mock_monetization_service.dart';
import '../../services/monetization/monetization_service.dart';
import '../../services/sync/cloud_sync.dart';

// Composition root: the only place where interfaces are bound to
// implementations. Tests override any of these with ProviderScope/Container.

// ---------------------------------------------------------------- core ----

final appConfigProvider = Provider<AppConfig>(
  (ref) => AppConfig.fromEnvironment(),
);

/// Overridden in bootstrap with the SharedPreferences adapter.
final keyValueStoreProvider = Provider<KeyValueStore>(
  (ref) => throw UnimplementedError(
    'keyValueStoreProvider must be overridden at app start',
  ),
);

final documentStoreProvider = Provider<JsonDocumentStore>(
  (ref) => JsonDocumentStore(ref.watch(keyValueStoreProvider)),
);

final textAssetLoaderProvider = Provider<TextAssetLoader>(
  (ref) => rootBundle.loadString,
);

final clockProvider = Provider<Clock>((ref) => const SystemClock());

final gameRulesProvider = Provider<GameRules>((ref) => GameRules.standard);

final idGeneratorProvider = Provider<IdGenerator>(
  (ref) => RandomIdGenerator(),
);

// ------------------------------------------------------------ services ----

final analyticsProvider = Provider<AnalyticsService>(
  (ref) => const LoggingAnalyticsService(),
);

final featureFlagsProvider = Provider<FeatureFlagService>(
  (ref) => LocalFeatureFlagService(),
);

final monetizationProvider = Provider<MonetizationService>(
  (ref) => MockMonetizationService(),
);

final aiTutorProvider = Provider<AITutorService>(
  (ref) => const MockAITutorService(),
);

final codeExecutionProvider = Provider<CodeExecutionService>(
  (ref) => const UnavailableCodeExecutionService(),
);

final cloudSyncProvider = Provider<CloudSyncService>(
  (ref) => const NoopCloudSyncService(),
);

final leaderboardRepositoryProvider = Provider<LeaderboardRepository>(
  (ref) => MockLeaderboardRepository(ref.watch(clockProvider)),
);

final metaGameProvider = Provider<MetaGameService>(
  (ref) => const MockMetaGameService(),
);

final authServiceProvider = Provider<AuthService>(
  (ref) => LocalAnonymousAuthService(
    () async => (await ref.read(progressRepositoryProvider).loadProfile())
        .userId,
  ),
);

// -------------------------------------------------------- repositories ----

final contentRepositoryProvider = Provider<ContentRepository>((ref) {
  final config = ref.watch(appConfigProvider);
  final RemoteContentSource remote = config.remoteContentEnabled
      ? DioRemoteContentSource(
          Dio(
            BaseOptions(
              baseUrl: config.contentBaseUrl,
              connectTimeout: config.networkTimeout,
              receiveTimeout: config.networkTimeout,
            ),
          ),
        )
      : const DisabledRemoteContentSource();
  return DefaultContentRepository(
    bundled: BundledContentSource(ref.watch(textAssetLoaderProvider)),
    remote: remote,
    cache: ContentCache(ref.watch(documentStoreProvider)),
  );
});

final progressRepositoryProvider = Provider<ProgressRepository>(
  (ref) => LocalProgressRepository(
    documents: ref.watch(documentStoreProvider),
    clock: ref.watch(clockProvider),
    rules: ref.watch(gameRulesProvider),
    ids: ref.watch(idGeneratorProvider),
  ),
);

final settingsRepositoryProvider = Provider<SettingsRepository>(
  (ref) => LocalSettingsRepository(
    ref.watch(documentStoreProvider),
    defaultCourseId: ref.watch(appConfigProvider).defaultCourseId,
  ),
);

// ------------------------------------------------------------- engines ----

final validatorRegistryProvider = Provider<ValidatorRegistry>(
  (ref) => ValidatorRegistry.standard(),
);

final levelEngineProvider = Provider<LevelEngine>(
  (ref) => LevelEngine(
    content: ref.watch(contentRepositoryProvider),
    progress: ref.watch(progressRepositoryProvider),
    settings: ref.watch(settingsRepositoryProvider),
    validators: ref.watch(validatorRegistryProvider),
    rules: ref.watch(gameRulesProvider),
    clock: ref.watch(clockProvider),
    analytics: ref.watch(analyticsProvider),
    flags: ref.watch(featureFlagsProvider),
  ),
);

final economyServiceProvider = Provider<EconomyService>(
  (ref) => EconomyService(
    progress: ref.watch(progressRepositoryProvider),
    monetization: ref.watch(monetizationProvider),
    analytics: ref.watch(analyticsProvider),
    rules: ref.watch(gameRulesProvider),
    clock: ref.watch(clockProvider),
  ),
);

final dailyChallengeServiceProvider = Provider<DailyChallengeService>(
  (ref) => LocalDailyChallengeService(
    content: ref.watch(contentRepositoryProvider),
    progress: ref.watch(progressRepositoryProvider),
    settings: ref.watch(settingsRepositoryProvider),
    rules: ref.watch(gameRulesProvider),
  ),
);

final syncCoordinatorProvider = Provider<SyncCoordinator>(
  (ref) => SyncCoordinator(
    progress: ref.watch(progressRepositoryProvider),
    store: ref.watch(keyValueStoreProvider),
    cloud: ref.watch(cloudSyncProvider),
  ),
);
