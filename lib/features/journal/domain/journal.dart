import '../../../core/utils/json_reader.dart';

/// One topic the player saved to the journal.
///
/// Review uses Leitner boxes: a successful review moves the topic one box
/// up (longer interval), a failed one sends it back to the first box.
class JournalEntry {
  JournalEntry({
    required this.topicId,
    required this.addedAt,
    required this.dueAt,
    this.box = 0,
    this.reviews = 0,
    this.lapses = 0,
    this.lastReviewedAt,
    List<String> mistakeLevelIds = const [],
  }) : mistakeLevelIds = List.unmodifiable(mistakeLevelIds);

  final String topicId;
  final DateTime addedAt;
  final DateTime dueAt;
  final int box;
  final int reviews;
  final int lapses;
  final DateTime? lastReviewedAt;

  /// Levels of this topic where the player made mistakes (newest last).
  final List<String> mistakeLevelIds;

  bool isDue(DateTime now) => !dueAt.isAfter(now);

  bool get isMastered => box >= ReviewScheduler.masteredBox;

  JournalEntry copyWith({
    DateTime? dueAt,
    int? box,
    int? reviews,
    int? lapses,
    DateTime? lastReviewedAt,
    List<String>? mistakeLevelIds,
  }) =>
      JournalEntry(
        topicId: topicId,
        addedAt: addedAt,
        dueAt: dueAt ?? this.dueAt,
        box: box ?? this.box,
        reviews: reviews ?? this.reviews,
        lapses: lapses ?? this.lapses,
        lastReviewedAt: lastReviewedAt ?? this.lastReviewedAt,
        mistakeLevelIds: mistakeLevelIds ?? this.mistakeLevelIds,
      );

  JournalEntry withMistake(String levelId) => copyWith(
        mistakeLevelIds: [
          ...mistakeLevelIds.where((id) => id != levelId),
          levelId,
        ],
      );

  Map<String, dynamic> toJson() => {
        'topicId': topicId,
        'addedAt': addedAt.toIso8601String(),
        'dueAt': dueAt.toIso8601String(),
        'box': box,
        'reviews': reviews,
        'lapses': lapses,
        if (lastReviewedAt != null)
          'lastReviewedAt': lastReviewedAt!.toIso8601String(),
        'mistakeLevelIds': mistakeLevelIds,
      };

  factory JournalEntry.fromJson(JsonReader json) {
    final last = json.optionalString('lastReviewedAt');
    return JournalEntry(
      topicId: json.requireString('topicId'),
      addedAt: DateTime.parse(json.requireString('addedAt')),
      dueAt: DateTime.parse(json.requireString('dueAt')),
      box: json.optionalInt('box') ?? 0,
      reviews: json.optionalInt('reviews') ?? 0,
      lapses: json.optionalInt('lapses') ?? 0,
      lastReviewedAt: last == null ? null : DateTime.parse(last),
      mistakeLevelIds: json.optionalStringList('mistakeLevelIds'),
    );
  }
}

/// The player's journal for one course: saved topics plus a tally of
/// mistakes per topic (to suggest what to save).
class Journal {
  Journal({
    required this.courseId,
    Map<String, JournalEntry> entries = const {},
    Map<String, List<String>> mistakes = const {},
  })  : entries = Map.unmodifiable(entries),
        mistakes = Map.unmodifiable(mistakes);

  final String courseId;

  /// Saved topics by topic id.
  final Map<String, JournalEntry> entries;

  /// Topic id -> levels where the player answered wrong (unique, newest
  /// last). Kept for topics that are not saved too.
  final Map<String, List<String>> mistakes;

  bool contains(String topicId) => entries.containsKey(topicId);

  List<JournalEntry> due(DateTime now) =>
      entries.values.where((entry) => entry.isDue(now)).toList()
        ..sort((a, b) => a.dueAt.compareTo(b.dueAt));

  /// Topics with mistakes that are not in the journal yet, most mistakes
  /// first.
  List<String> suggestedTopicIds() {
    final ids = mistakes.keys.where((id) => !entries.containsKey(id)).toList()
      ..sort((a, b) => mistakes[b]!.length.compareTo(mistakes[a]!.length));
    return ids;
  }

  Journal copyWith({
    Map<String, JournalEntry>? entries,
    Map<String, List<String>>? mistakes,
  }) =>
      Journal(
        courseId: courseId,
        entries: entries ?? this.entries,
        mistakes: mistakes ?? this.mistakes,
      );

  Map<String, dynamic> toJson() => {
        'courseId': courseId,
        'entries': [for (final entry in entries.values) entry.toJson()],
        'mistakes': mistakes,
      };

  factory Journal.fromJson(Map<String, dynamic> raw) {
    final json = JsonReader(raw);
    final entries = {
      for (final entry in json.optionalObjectList('entries'))
        entry.requireString('topicId'): JournalEntry.fromJson(entry),
    };
    final mistakes = <String, List<String>>{};
    final rawMistakes = raw['mistakes'];
    if (rawMistakes is Map<String, dynamic>) {
      rawMistakes.forEach((topicId, levels) {
        if (levels is List) {
          mistakes[topicId] = levels.whereType<String>().toList();
        }
      });
    }
    return Journal(
      courseId: json.requireString('courseId'),
      entries: entries,
      mistakes: mistakes,
    );
  }
}

/// Spaced-repetition intervals (Leitner boxes).
class ReviewScheduler {
  const ReviewScheduler();

  /// Days until the next review after reaching box `i + 1`.
  static const List<int> intervalDays = [1, 3, 7, 16, 35];

  static int get masteredBox => intervalDays.length;

  /// A freshly saved topic is due for its first review tomorrow.
  DateTime firstDue(DateTime now) => now.add(Duration(days: intervalDays[0]));

  JournalEntry review(
    JournalEntry entry, {
    required bool remembered,
    required DateTime now,
  }) {
    if (!remembered) {
      return entry.copyWith(
        box: 0,
        lapses: entry.lapses + 1,
        reviews: entry.reviews + 1,
        lastReviewedAt: now,
        dueAt: now.add(Duration(days: intervalDays[0])),
      );
    }
    final box = entry.box >= masteredBox ? masteredBox : entry.box + 1;
    return entry.copyWith(
      box: box,
      reviews: entry.reviews + 1,
      lastReviewedAt: now,
      dueAt: now.add(Duration(days: intervalDays[box - 1])),
    );
  }
}
