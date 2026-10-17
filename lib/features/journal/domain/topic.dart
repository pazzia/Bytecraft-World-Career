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
    List<String> pitfalls = const [],
  })  : examples = List.unmodifiable(examples),
        pitfalls = List.unmodifiable(pitfalls);

  final String id;
  final String moduleId;
  final String title;

  /// One-sentence essence of the topic.
  final String summary;

  /// Detailed explanation (paragraphs separated by blank lines).
  final String body;
  final List<TopicExample> examples;

  /// Typical mistakes, one per item.
  final List<String> pitfalls;
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
