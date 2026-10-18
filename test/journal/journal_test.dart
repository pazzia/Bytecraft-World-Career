import 'package:bytecraft/core/storage/json_document_store.dart';
import 'package:bytecraft/core/storage/key_value_store.dart';
import 'package:bytecraft/core/time/clock.dart';
import 'package:bytecraft/core/utils/json_reader.dart';
import 'package:bytecraft/features/courses/data/content_parser.dart';
import 'package:bytecraft/features/courses/domain/level_definition.dart';
import 'package:bytecraft/features/journal/data/local_journal_repository.dart';
import 'package:bytecraft/features/journal/data/topic_repository.dart';
import 'package:bytecraft/features/journal/domain/journal.dart';
import 'package:bytecraft/features/journal/domain/journal_service.dart';
import 'package:bytecraft/features/journal/presentation/journal_providers.dart';
import 'package:flutter_test/flutter_test.dart';

const String course = 'python';

LevelDefinition level(String id) => ContentParser().parseLevel(
      JsonReader({
        'id': id,
        'type': 'multiple_choice',
        'title': id,
        'prompt': '?',
        'topic': 'loops',
        'payload': {
          'options': ['a', 'b'],
          'correctIndex': 0,
        },
      }),
      course,
      'm',
    );

void main() {
  late FixedClock clock;
  late LocalJournalRepository repository;
  late JournalService service;

  setUp(() {
    clock = FixedClock(DateTime(2026, 10, 17, 9));
    repository = LocalJournalRepository(JsonDocumentStore(InMemoryKeyValueStore()));
    service = JournalService(repository: repository, clock: clock);
  });

  test('a saved topic is due for review the next day', () async {
    await service.add(course, 'loops', levelId: 'l1');
    final journal = await service.load(course);
    expect(journal.contains('loops'), isTrue);
    expect(journal.due(clock.now()), isEmpty);
    clock.advance(const Duration(days: 1));
    expect(journal.due(clock.now()).single.topicId, 'loops');
  });

  test('mistakes are remembered and suggested for saving', () async {
    await service.recordMistake(course, 'loops', 'l1');
    await service.recordMistake(course, 'loops', 'l2');
    await service.recordMistake(course, 'loops', 'l1');
    await service.recordMistake(course, 'lists', 'l9');
    final journal = await service.load(course);
    expect(journal.mistakes['loops'], ['l2', 'l1']);
    expect(journal.suggestedTopicIds(), ['loops', 'lists']);

    await service.add(course, 'loops');
    final saved = await service.load(course);
    expect(saved.entries['loops']!.mistakeLevelIds, ['l2', 'l1']);
    expect(saved.suggestedTopicIds(), ['lists']);
  });

  test('successful reviews climb the Leitner boxes, a failure resets', () async {
    await service.add(course, 'loops');
    var entry = (await service.recordReview(course, 'loops', remembered: true))!;
    expect(entry.box, 1);
    expect(entry.dueAt, clock.now().add(const Duration(days: 1)));
    entry = (await service.recordReview(course, 'loops', remembered: true))!;
    expect(entry.box, 2);
    expect(entry.dueAt, clock.now().add(const Duration(days: 3)));
    entry = (await service.recordReview(course, 'loops', remembered: false))!;
    expect(entry.box, 0);
    expect(entry.lapses, 1);
    expect(entry.reviews, 3);
  });

  test('a topic becomes mastered after enough successful reviews', () async {
    await service.add(course, 'loops');
    JournalEntry? entry;
    for (var i = 0; i < ReviewScheduler.intervalDays.length + 2; i++) {
      entry = await service.recordReview(course, 'loops', remembered: true);
    }
    expect(entry!.isMastered, isTrue);
    expect(entry.box, ReviewScheduler.masteredBox);
  });

  test('removing a topic keeps the mistake history', () async {
    await service.recordMistake(course, 'loops', 'l1');
    await service.add(course, 'loops');
    await service.remove(course, 'loops');
    final journal = await service.load(course);
    expect(journal.contains('loops'), isFalse);
    expect(journal.mistakes['loops'], ['l1']);
  });

  test('the journal survives a JSON round trip', () async {
    await service.recordMistake(course, 'loops', 'l1');
    await service.add(course, 'loops');
    await service.recordReview(course, 'loops', remembered: true);
    final restored = Journal.fromJson(
      Map<String, dynamic>.from((await service.load(course)).toJson()),
    );
    final entry = restored.entries['loops']!;
    expect(entry.box, 1);
    expect(entry.mistakeLevelIds, ['l1']);
    expect(entry.lastReviewedAt, clock.now());
  });

  test('a corrupted journal falls back to an empty one', () async {
    final store = InMemoryKeyValueStore();
    final documents = JsonDocumentStore(store);
    await documents.write('player.journal.$course', {'courseId': course, 'entries': 'oops'},
        schemaVersion: 1);
    final journal = await LocalJournalRepository(documents).load(course);
    expect(journal.entries, isEmpty);
  });

  test('review picks a level the player got wrong first', () {
    final entry = JournalEntry(
      topicId: 'loops',
      addedAt: DateTime(2026),
      dueAt: DateTime(2026),
      mistakeLevelIds: const ['b'],
    );
    final levels = [level('a'), level('b'), level('c')];
    expect(pickReviewLevel(entry, levels)!.id, 'b');
    expect(pickReviewLevel(entry.copyWith(reviews: 1), levels)!.id, 'b',
        reason: 'odd reviews rotate through all levels: index 1');
    expect(pickReviewLevel(entry, const []), isNull);
  });

  test('topics parse and skip broken entries', () {
    final catalog = TopicRepository.parseTopics({
      'topics': [
        {
          'id': 'loops',
          'module': 'm',
          'title': 'Циклы',
          'summary': 's',
          'body': 'b',
          'examples': [
            {'code': 'print(1)', 'output': '1\n', 'note': 'n'},
          ],
          'pitfalls': ['p'],
        },
        {'id': 'broken'},
      ],
    });
    expect(catalog.topics.single.id, 'loops');
    expect(catalog.byId('loops')!.examples.single.output, '1\n');
    expect(catalog.forModule('m'), hasLength(1));
  });
}
