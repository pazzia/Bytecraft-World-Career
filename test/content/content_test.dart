import 'dart:convert';
import 'dart:io';

import 'package:bytecraft/core/errors/app_exception.dart';
import 'package:bytecraft/core/storage/json_document_store.dart';
import 'package:bytecraft/core/storage/key_value_store.dart';
import 'package:bytecraft/features/courses/data/content_parser.dart';
import 'package:bytecraft/features/courses/data/content_sources.dart';
import 'package:bytecraft/features/courses/data/default_content_repository.dart';
import 'package:bytecraft/features/courses/domain/level_payload.dart';
import 'package:bytecraft/features/courses/domain/level_type.dart';
import 'package:bytecraft/features/journal/data/topic_repository.dart';
import 'package:bytecraft/features/level/engine/answer_validator.dart';
import 'package:bytecraft/features/playground/data/practice_repository.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/test_env.dart';

class FakeRemoteSource implements RemoteContentSource {
  FakeRemoteSource(this.document);

  Map<String, dynamic>? document;

  @override
  Future<Map<String, dynamic>?> fetchCourse(String courseId) async => document;
}

/// Reads bundled assets straight from the project directory.
Future<String> readAsset(String path) => File(path).readAsString();

void main() {
  group('bundled Python course', () {
    const bundled = BundledContentSource(readAsset);

    test('starts with the basics, every module has a boss', () async {
      final course =
          ContentParser().parseCourse(await bundled.fetchCourse('python'));
      expect(
        course.modules.take(6).map((module) => module.id),
        ['variables', 'types', 'operators', 'strings', 'io', 'conditions'],
      );
      expect(course.modules.length, greaterThanOrEqualTo(12));
      for (final module in course.modules) {
        expect(module.levels.length, greaterThanOrEqualTo(6), reason: module.id);
        expect(module.levels.last.role, LevelRole.boss, reason: module.id);
      }
    });

    test('every level links to a topic of the journal catalog', () async {
      final course =
          ContentParser().parseCourse(await bundled.fetchCourse('python'));
      final catalog = TopicRepository.parseTopics(
        jsonDecode(await readAsset('assets/content/python/topics.json'))
            as Map<String, dynamic>,
      );
      for (final level in course.levels) {
        expect(catalog.byId(level.topicId), isNotNull, reason: level.id);
      }
      for (final topic in catalog.topics) {
        expect(topic.examples, isNotEmpty, reason: topic.id);
        expect(topic.body.trim(), isNotEmpty, reason: topic.id);
      }
    });

    test('practice tasks parse and have tests', () async {
      final tasks = PracticeRepository.parseTasks(
        jsonDecode(await readAsset('assets/content/python/practice.json'))
            as Map<String, dynamic>,
      );
      expect(tasks, isNotEmpty);
      for (final task in tasks) {
        expect(task.tests.length, greaterThanOrEqualTo(3), reason: task.id);
      }
    });

    test('every level is valid and supported by the engine', () async {
      final course =
          ContentParser().parseCourse(await bundled.fetchCourse('python'));
      final validators = ValidatorRegistry.standard();
      for (final level in course.levels) {
        expect(
          level.payload,
          isNot(isA<UnsupportedPayload>()),
          reason: '${level.id}: ${level.payload}',
        );
        expect(validators.supports(level.type), isTrue, reason: level.id);
        expect(level.hint, isNotNull, reason: level.id);
        expect(level.explanation, isNotNull, reason: level.id);
      }
    });

    test('each module ends with a boss level', () async {
      final course =
          ContentParser().parseCourse(await bundled.fetchCourse('python'));
      for (final module in course.modules) {
        expect(module.levels.last.role, LevelRole.boss, reason: module.id);
      }
    });

    test('catalog lists Python as available', () async {
      final catalog = ContentParser().parseCatalog(await bundled.fetchCatalog());
      final python = catalog.firstWhere((course) => course.id == 'python');
      expect(python.isAvailable, isTrue);
      expect(catalog.where((course) => !course.isAvailable), isNotEmpty);
    });
  });

  group('ContentParser', () {
    test('invalid level data becomes an unsupported level', () {
      final json = testCourseJson();
      final modules = json['modules'] as List<dynamic>;
      final levels = (modules.first as Map<String, dynamic>)['levels']
          as List<dynamic>;
      (levels.first as Map<String, dynamic>)['payload'] = {
        'options': ['a', 'b'],
        'correctIndex': 7,
      };
      final course = ContentParser().parseCourse(json);
      expect(course.levelById('l1')!.isSupported, isFalse);
      expect(course.levelById('l2')!.isSupported, isTrue);
    });

    test('unknown level types are preserved as unsupported', () {
      final level = buildTestCourse().levelById('l5')!;
      expect(level.type, LevelType.robotPuzzle);
      expect(level.isSupported, isFalse);
    });

    test('broken course structure throws ContentFormatException', () {
      expect(
        () => ContentParser().parseCourse({'title': 'no id'}),
        throwsA(isA<ContentFormatException>()),
      );
    });
  });

  group('DefaultContentRepository', () {
    late ContentCache cache;
    late FakeRemoteSource remote;
    late DefaultContentRepository repository;

    setUp(() {
      cache = ContentCache(JsonDocumentStore(InMemoryKeyValueStore()));
      remote = FakeRemoteSource(null);
      repository = DefaultContentRepository(
        bundled: BundledContentSource(
          (path) async => throw StateError('use cache in this test'),
        ),
        remote: remote,
        cache: cache,
      );
    });

    test('refresh stores a newer remote version and serves it', () async {
      final bundledRepo = DefaultContentRepository(
        bundled: const BundledContentSource(readAsset),
        remote: FakeRemoteSource(
          {...await const BundledContentSource(readAsset).fetchCourse('python'),
            'version': 999},
        ),
        cache: cache,
      );
      expect((await bundledRepo.loadCourse('python')).version, 2);
      expect(await bundledRepo.refreshCourse('python'), isTrue);
      expect((await bundledRepo.loadCourse('python')).version, 999);
      expect(await cache.read('python'), isNotNull);
    });

    test('rejects invalid remote content and keeps the current course', () async {
      final bundledRepo = DefaultContentRepository(
        bundled: const BundledContentSource(readAsset),
        remote: FakeRemoteSource({'id': 'python', 'version': 5}),
        cache: cache,
      );
      expect(await bundledRepo.refreshCourse('python'), isFalse);
      expect((await bundledRepo.loadCourse('python')).version, 2);
    });

    test('missing bundled asset surfaces as ContentNotFoundException', () async {
      await expectLater(
        repository.loadCourse('python'),
        throwsA(isA<ContentNotFoundException>()),
      );
    });
  });
}
