/// A learning topic: the reference card a journal entry is built on.
/// Comes from content (`assets/content/{course}/topics.json`); every code
/// example and its output were checked by running them in Python.
class Topic {
  Topic({
    required this.id,
    required this.moduleId,
    required this.title,
    required this.summary,
    required this.body,
    required List<TopicExample> examples,
    List<TopicPitfall> pitfalls = const [],
  })  : examples = List.unmodifiable(examples),
        pitfalls = List.unmodifiable(pitfalls);

  final String id;
  final String moduleId;
  final String title;

  /// One-sentence essence of the topic.
  final String summary;

  /// Detailed explanation in the topic markup (see TopicMarkup).
  final String body;
  final List<TopicExample> examples;

  /// Typical mistakes.
  final List<TopicPitfall> pitfalls;

  /// Topics this one links to, in order of first mention.
  List<String> get linkedTopicIds {
    final ids = <String>[];
    final texts = [body, for (final pitfall in pitfalls) pitfall.why];
    for (final text in texts) {
      for (final match in topicLinkPattern.allMatches(text)) {
        final target = match.group(1)!;
        if (!target.startsWith('g:') && target != id && !ids.contains(target)) ids.add(target);
      }
    }
    return ids;
  }
}

/// `[[target|text]]` or `[[target|text|term]]`.
final RegExp topicLinkPattern = RegExp(r'\[\[([^\]|]+)\|([^\]|]+)(?:\|([^\]|]+))?\]\]');

/// A typical mistake: why it is wrong, and optionally the wrong and the
/// right code («так нельзя / так можно»).
class TopicPitfall {
  const TopicPitfall({required this.why, this.bad, this.good});

  final String why;
  final String? bad;
  final String? good;

  bool get hasCode => bad != null && good != null;
}

/// A glossary entry shown in the sheet when a linked term is tapped.
class GlossaryEntry {
  const GlossaryEntry({
    required this.key,
    required this.brief,
    this.topicId,
    this.example,
    this.output,
  });

  final String key;
  final String brief;

  /// The topic that explains the term; null for glossary-only entries.
  final String? topicId;
  final String? example;
  final String? output;
}

class Glossary {
  Glossary(Map<String, GlossaryEntry> entries) : _entries = Map.unmodifiable(entries);

  static final Glossary empty = Glossary(const {});

  final Map<String, GlossaryEntry> _entries;

  GlossaryEntry? operator [](String? key) => key == null ? null : _entries[key];

  int get length => _entries.length;
}

class TopicExample {
  const TopicExample({required this.code, required this.output, this.note});

  final String code;

  /// What [code] prints; empty when it prints nothing.
  final String output;
  final String? note;
}

class TopicCatalog {
  TopicCatalog(List<Topic> topics)
      : topics = List.unmodifiable(topics),
        _byId = {for (final topic in topics) topic.id: topic};

  static final TopicCatalog empty = TopicCatalog(const []);

  final List<Topic> topics;
  final Map<String, Topic> _byId;

  Topic? byId(String? id) => id == null ? null : _byId[id];

  List<Topic> forModule(String moduleId) =>
      topics.where((topic) => topic.moduleId == moduleId).toList();
}
