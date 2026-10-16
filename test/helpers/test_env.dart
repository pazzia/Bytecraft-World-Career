import 'package:bytecraft/core/storage/json_document_store.dart';
import 'package:bytecraft/core/storage/key_value_store.dart';
import 'package:bytecraft/core/time/clock.dart';
import 'package:bytecraft/core/utils/id_generator.dart';
import 'package:bytecraft/features/courses/data/content_parser.dart';
import 'package:bytecraft/features/courses/domain/content_repository.dart';
import 'package:bytecraft/features/courses/domain/course.dart';
import 'package:bytecraft/features/courses/domain/course_summary.dart';
import 'package:bytecraft/features/gamification/domain/game_rules.dart';
import 'package:bytecraft/features/level/domain/level_result.dart';
import 'package:bytecraft/features/level/domain/level_session.dart';
import 'package:bytecraft/features/level/engine/answer_validator.dart';
import 'package:bytecraft/features/level/engine/level_engine.dart';
import 'package:bytecraft/features/progress/data/local_progress_repository.dart';
import 'package:bytecraft/features/settings/data/local_settings_repository.dart';
import 'package:bytecraft/services/analytics/analytics_service.dart';
import 'package:bytecraft/services/feature_flags/feature_flag_service.dart';

const String testCourseId = 'test';

/// Two modules, six levels, one of them an unsupported (future) type:
///
///   basics:   l1 MC lesson -> l2 fill lesson -> l3 ordering boss
///   advanced: l4 MC lesson -> l5 robot (unsupported) -> l6 bug finder
Map<String, dynamic> testCourseJson({int version = 1}) => {
      'id': testCourseId,
      'title': 'Test course',
      'language': 'python',
      'version': version,
      'modules': [
        {
          'id': 'basics',
          'title': 'Basics',
          'levels': [
            {
              'id': 'l1',
              'type': 'multiple_choice',
              'title': 'MC',
              'prompt': 'x?',
              'code': 'x = 5',
              'hint': 'hint',
              'payload': {
                'options': ['3', '5'],
                'correctIndex': 1,
              },
            },
            {
              'id': 'l2',
              'type': 'fill_code',
              'title': 'Fill',
              'prompt': 'fill',
              'payload': {
                'template': 'for i {{0}} range(3):\n    print(i)',
                'options': ['in', 'of'],
                'answers': ['in'],
              },
            },
            {
              'id': 'l3',
              'type': 'code_ordering',
              'role': 'boss',
              'title': 'Order',
              'prompt': 'order',
              'payload': {
                'lines': ['a = 1', 'b = 2', 'print(a + b)'],
                'alternativeOrders': [
                  [1, 0, 2],
                ],
              },
            },
          ],
        },
        {
          'id': 'advanced',
          'title': 'Advanced',
          'levels': [
            {
              'id': 'l4',
              'type': 'multiple_choice',
              'title': 'MC 2',
              'prompt': 'y?',
              'payload': {
                'options': ['a', 'b', 'c'],
                'correctIndex': 2,
              },
            },
            {
              'id': 'l5',
              'type': 'robot_puzzle',
              'title': 'Robot',
              'prompt': 'robot',
              'payload': <String, dynamic>{},
            },
            {
              'id': 'l6',
              'type': 'bug_finder',
              'role': 'challenge',
              'title': 'Bug',
              'prompt': 'bug',
              'code': 'x = 1\nprint(y)\nprint(x)',
              'payload': {
                'buggyLines': [1],
              },
            },
          ],
        },
      ],
    };

Course buildTestCourse({int version = 1}) =>
    ContentParser().parseCourse(testCourseJson(version: version));

class FakeContentRepository implements ContentRepository {
  FakeContentRepository(this.course);

  final Course course;

  @override
  Future<List<CourseSummary>> loadCatalog() async => const [];

  @override
  Future<Course> loadCourse(String courseId) async => course;

  @override
  Future<bool> refreshCourse(String courseId) async => false;
}

class FixedIdGenerator implements IdGenerator {
  @override
  String newId() => 'user-1';
}

/// Wires the real engine + repositories over an in-memory store.
class TestEnv {
  TestEnv({
    KeyValueStore? store,
    DateTime? now,
    Map<FeatureFlag, bool> flags = const {},
    Course? course,
  })  : store = store ?? InMemoryKeyValueStore(),
        clock = FixedClock(now ?? DateTime(2026, 10, 11, 12)),
        flags = LocalFeatureFlagService(overrides: flags),
        course = course ?? buildTestCourse() {
    final documents = JsonDocumentStore(this.store);
    progress = LocalProgressRepository(
      documents: documents,
      clock: clock,
      rules: rules,
      ids: FixedIdGenerator(),
    );
    settings = LocalSettingsRepository(documents, defaultCourseId: testCourseId);
    engine = LevelEngine(
      content: FakeContentRepository(this.course),
      progress: progress,
      settings: settings,
      validators: ValidatorRegistry.standard(),
      rules: rules,
      clock: clock,
      analytics: analytics,
      flags: this.flags,
    );
  }

  final KeyValueStore store;
  final FixedClock clock;
  final LocalFeatureFlagService flags;
  final Course course;
  final GameRules rules = GameRules.standard;
  final RecordingAnalyticsService analytics = RecordingAnalyticsService();
  late final LocalProgressRepository progress;
  late final LocalSettingsRepository settings;
  late final LevelEngine engine;

  Future<LevelStartResult> start(
    String levelId, {
    LevelMode mode = LevelMode.standard,
  }) =>
      engine.start(courseId: testCourseId, levelId: levelId, mode: mode);

  /// Starts a level and fails the test if it can't be started.
  Future<LevelSession> startOk(
    String levelId, {
    LevelMode mode = LevelMode.standard,
  }) async {
    final result = await start(levelId, mode: mode);
    if (result is! LevelStarted) {
      throw StateError('Expected $levelId to start, got $result');
    }
    return result.session;
  }
}
