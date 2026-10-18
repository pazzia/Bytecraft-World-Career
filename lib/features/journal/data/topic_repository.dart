import 'dart:convert';

import '../../../core/utils/json_reader.dart';
import '../../courses/data/content_sources.dart';
import '../domain/topic.dart';

/// Loads the bundled topic catalog of a course. A missing or broken file
/// gives an empty catalog: the journal degrades, the game keeps working.
class TopicRepository {
  TopicRepository(this._load, {this.root = 'assets/content'});

  final TextAssetLoader _load;
  final String root;
  final Map<String, TopicCatalog> _cache = {};

  Future<TopicCatalog> load(String courseId) async {
    final cached = _cache[courseId];
    if (cached != null) return cached;
    TopicCatalog catalog;
    try {
      final text = await _load('$root/$courseId/topics.json');
      catalog = parseTopics(jsonDecode(text) as Map<String, dynamic>);
    } catch (_) {
      catalog = TopicCatalog.empty;
    }
    _cache[courseId] = catalog;
    return catalog;
  }

  static TopicCatalog parseTopics(Map<String, dynamic> json) {
    final topics = <Topic>[];
    for (final topic in JsonReader(json).requireObjectList('topics')) {
      try {
        topics.add(
          Topic(
            id: topic.requireString('id'),
            moduleId: topic.requireString('module'),
            title: topic.requireString('title'),
            summary: topic.requireString('summary'),
            body: topic.requireString('body'),
            pitfalls: _pitfalls(topic.raw['pitfalls']),
            examples: [
              for (final example in topic.optionalObjectList('examples'))
                TopicExample(
                  code: example.requireString('code'),
                  output: example.optionalString('output') ?? '',
                  note: example.optionalString('note'),
                ),
            ],
          ),
        );
      } on JsonFormatException {
        // Skip a broken topic, keep the rest.
      }
    }
    return TopicCatalog(topics);
  }

  /// Pitfalls are plain strings (older content) or {why, bad, good}.
  static List<TopicPitfall> _pitfalls(Object? raw) {
    if (raw is! List) return const [];
    return [
      for (final item in raw)
        if (item is String)
          TopicPitfall(why: item)
        else if (item is Map && item['why'] is String)
          TopicPitfall(
            why: item['why'] as String,
            bad: item['bad'] is String ? item['bad'] as String : null,
            good: item['good'] is String ? item['good'] as String : null,
          ),
    ];
  }

  final Map<String, Glossary> _glossaries = {};

  /// The course glossary (`glossary.json`); empty when missing or broken.
  Future<Glossary> loadGlossary(String courseId) async {
    final cached = _glossaries[courseId];
    if (cached != null) return cached;
    Glossary glossary;
    try {
      final text = await _load('$root/$courseId/glossary.json');
      glossary = parseGlossary(jsonDecode(text) as Map<String, dynamic>);
    } catch (_) {
      glossary = Glossary.empty;
    }
    _glossaries[courseId] = glossary;
    return glossary;
  }

  static Glossary parseGlossary(Map<String, dynamic> json) {
    final terms = json['terms'];
    if (terms is! Map) return Glossary.empty;
    final entries = <String, GlossaryEntry>{};
    terms.forEach((key, value) {
      if (key is String && value is Map && value['brief'] is String) {
        entries[key] = GlossaryEntry(
          key: key,
          brief: value['brief'] as String,
          topicId: value['topic'] is String ? value['topic'] as String : null,
          example: value['example'] is String ? value['example'] as String : null,
          output: value['output'] is String ? value['output'] as String : null,
        );
      }
    });
    return Glossary(entries);
  }
}
