import 'dart:developer' as developer;

import '../../../core/errors/app_exception.dart';
import '../domain/content_repository.dart';
import '../domain/course.dart';
import '../domain/course_summary.dart';
import 'content_parser.dart';
import 'content_sources.dart';

/// Offline-first content repository.
///
/// Resolution order for a course: newest valid version among
/// (cache of remote content, bundled content). Remote refresh is explicit
/// and only replaces the cache after the document parses successfully.
class DefaultContentRepository implements ContentRepository {
  DefaultContentRepository({
    required BundledContentSource bundled,
    required RemoteContentSource remote,
    required ContentCache cache,
    ContentParser? parser,
  })  : _bundled = bundled,
        _remote = remote,
        _cache = cache,
        _parser = parser ?? ContentParser();

  final BundledContentSource _bundled;
  final RemoteContentSource _remote;
  final ContentCache _cache;
  final ContentParser _parser;

  final Map<String, Course> _memory = {};
  List<CourseSummary>? _catalog;

  @override
  Future<List<CourseSummary>> loadCatalog() async {
    return _catalog ??= _parser.parseCatalog(await _bundled.fetchCatalog());
  }

  @override
  Future<Course> loadCourse(String courseId) async {
    final cached = _memory[courseId];
    if (cached != null) return cached;

    final bundled = _parser.parseCourse(await _bundled.fetchCourse(courseId));
    var best = bundled;
    final cachedDoc = await _cache.read(courseId);
    if (cachedDoc != null) {
      try {
        final fromCache = _parser.parseCourse(cachedDoc);
        if (fromCache.version > bundled.version) best = fromCache;
      } on ContentFormatException catch (error) {
        developer.log('Dropping invalid cache: $error', name: 'content');
        await _cache.clear(courseId);
      }
    }
    _memory[courseId] = best;
    return best;
  }

  @override
  Future<bool> refreshCourse(String courseId) async {
    final document = await _remote.fetchCourse(courseId);
    if (document == null) return false;
    try {
      final remote = _parser.parseCourse(document);
      final current = await loadCourse(courseId);
      if (remote.version <= current.version) return false;
      await _cache.write(courseId, document);
      _memory[courseId] = remote;
      return true;
    } on ContentFormatException catch (error) {
      developer.log('Rejected remote content: $error', name: 'content');
      return false;
    }
  }
}
