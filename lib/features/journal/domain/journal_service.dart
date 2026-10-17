import '../../../core/time/clock.dart';
import '../data/local_journal_repository.dart';
import 'journal.dart';

/// Use cases of the journal. All writes go through here.
class JournalService {
  JournalService({
    required LocalJournalRepository repository,
    required Clock clock,
    ReviewScheduler scheduler = const ReviewScheduler(),
  })  : _repository = repository,
        _clock = clock,
        _scheduler = scheduler;

  /// How many mistaken levels are remembered per topic.
  static const int maxMistakesPerTopic = 20;

  final LocalJournalRepository _repository;
  final Clock _clock;
  final ReviewScheduler _scheduler;

  Future<Journal> load(String courseId) => _repository.load(courseId);

  /// Saves a topic to the journal; [levelId] is where the player came from
  /// (kept as a mistake when they had answered it wrong).
  Future<Journal> add(String courseId, String topicId, {String? levelId}) async {
    final journal = await _repository.load(courseId);
    if (journal.contains(topicId)) return journal;
    final now = _clock.now();
    final mistakes = journal.mistakes[topicId] ?? const <String>[];
    final entry = JournalEntry(
      topicId: topicId,
      addedAt: now,
      dueAt: _scheduler.firstDue(now),
      mistakeLevelIds: mistakes,
    );
    final next = journal.copyWith(entries: {...journal.entries, topicId: entry});
    await _repository.save(next);
    return next;
  }

  Future<Journal> remove(String courseId, String topicId) async {
    final journal = await _repository.load(courseId);
    if (!journal.contains(topicId)) return journal;
    final next = journal.copyWith(
      entries: {...journal.entries}..remove(topicId),
    );
    await _repository.save(next);
    return next;
  }

  /// Remembers a wrong answer on a level of [topicId].
  Future<void> recordMistake(
    String courseId,
    String topicId,
    String levelId,
  ) async {
    final journal = await _repository.load(courseId);
    final previous = journal.mistakes[topicId] ?? const <String>[];
    var levels = [...previous.where((id) => id != levelId), levelId];
    if (levels.length > maxMistakesPerTopic) {
      levels = levels.sublist(levels.length - maxMistakesPerTopic);
    }
    final entry = journal.entries[topicId];
    await _repository.save(
      journal.copyWith(
        mistakes: {...journal.mistakes, topicId: levels},
        entries: entry == null
            ? null
            : {...journal.entries, topicId: entry.withMistake(levelId)},
      ),
    );
  }

  /// Records the result of reviewing a saved topic.
  Future<JournalEntry?> recordReview(
    String courseId,
    String topicId, {
    required bool remembered,
  }) async {
    final journal = await _repository.load(courseId);
    final entry = journal.entries[topicId];
    if (entry == null) return null;
    final reviewed =
        _scheduler.review(entry, remembered: remembered, now: _clock.now());
    await _repository.save(
      journal.copyWith(entries: {...journal.entries, topicId: reviewed}),
    );
    return reviewed;
  }
}
