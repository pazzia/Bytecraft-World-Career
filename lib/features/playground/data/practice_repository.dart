import 'dart:convert';

import '../../../core/storage/json_document_store.dart';
import '../../../core/utils/json_reader.dart';
import '../../courses/data/content_sources.dart';
import '../domain/practice_task.dart';

/// Bundled coding exercises (`assets/content/{course}/practice.json`) and
/// the set of exercises the player has solved.
class PracticeRepository {
  PracticeRepository(this._load, this._documents, {this.root = 'assets/content'});

  final TextAssetLoader _load;
  final JsonDocumentStore _documents;
  final String root;
  final Map<String, List<PracticeTask>> _cache = {};

  static String _solvedKey(String courseId) => 'player.practice.$courseId';
  static const int _solvedSchema = 1;

  Future<List<PracticeTask>> tasks(String courseId) async {
    final cached = _cache[courseId];
    if (cached != null) return cached;
    List<PracticeTask> tasks;
    try {
      final text = await _load('$root/$courseId/practice.json');
      tasks = parseTasks(jsonDecode(text) as Map<String, dynamic>);
    } catch (_) {
      tasks = const [];
    }
    return _cache[courseId] = tasks;
  }

  static List<PracticeTask> parseTasks(Map<String, dynamic> json) {
    final result = <PracticeTask>[];
    for (final task in JsonReader(json).requireObjectList('tasks')) {
      try {
        result.add(
          PracticeTask(
            id: task.requireString('id'),
            moduleId: task.requireString('module'),
            title: task.requireString('title'),
            prompt: task.requireString('prompt'),
            starter: task.optionalString('starter') ?? '',
            solution: task.requireString('solution'),
            hint: task.optionalString('hint'),
            difficulty: task.optionalInt('difficulty') ?? 1,
            tests: [
              for (final test in task.requireObjectList('tests'))
                PracticeTest(
                  stdin: test.optionalString('stdin') ?? '',
                  expected: test.optionalString('expected') ?? '',
                ),
            ],
          ),
        );
      } on JsonFormatException {
        // Skip a broken task.
      }
    }
    return List.unmodifiable(result);
  }

  Future<Set<String>> solved(String courseId) async {
    final json = await _documents.read(_solvedKey(courseId));
    final ids = json?['solved'];
    return ids is List ? ids.whereType<String>().toSet() : <String>{};
  }

  Future<void> markSolved(String courseId, String taskId) async {
    final ids = await solved(courseId);
    if (!ids.add(taskId)) return;
    await _documents.write(
      _solvedKey(courseId),
      {'solved': ids.toList()..sort()},
      schemaVersion: _solvedSchema,
    );
  }
}
