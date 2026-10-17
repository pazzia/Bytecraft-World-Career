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
            pitfalls: topic.optionalStringList('pitfalls'),
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
}
