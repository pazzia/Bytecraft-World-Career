import 'dart:convert';

import '../../../core/errors/app_exception.dart';
import '../../../core/storage/json_document_store.dart';
import '../../../core/storage/storage_keys.dart';

/// Loads a text file by path (Flutter's rootBundle in the app,
/// file system or in-memory map in tests).
typedef TextAssetLoader = Future<String> Function(String path);

/// Bundled content shipped inside the app binary — always available offline.
///
/// Layout:
///   `assets/content/catalog.json`
///   `assets/content/{course}/course.json` (module list with "file" refs)
///   `assets/content/{course}/{module file}` ({"levels": [...]})
class BundledContentSource {
  const BundledContentSource(this._load, {this.root = 'assets/content'});

  final TextAssetLoader _load;
  final String root;

  Future<Map<String, dynamic>> _json(String path) async {
    final String text;
    try {
      text = await _load(path);
    } catch (error) {
      throw ContentNotFoundException('Asset "$path" not found: $error');
    }
    final decoded = jsonDecode(text);
    if (decoded is! Map<String, dynamic>) {
      throw ContentFormatException('Asset "$path" is not a JSON object');
    }
    return decoded;
  }

  Future<Map<String, dynamic>> fetchCatalog() => _json('$root/catalog.json');

  /// Returns an assembled course document with inline module levels.
  Future<Map<String, dynamic>> fetchCourse(String courseId) async {
    final manifest = await _json('$root/$courseId/course.json');
    final modules = manifest['modules'];
    if (modules is! List) {
      throw ContentFormatException('Course "$courseId" has no modules list');
    }
    final assembled = <Map<String, dynamic>>[];
    for (final module in modules) {
      if (module is! Map<String, dynamic>) {
        throw ContentFormatException('Course "$courseId": bad module entry');
      }
      final file = module['file'];
      if (file is String) {
        final moduleDoc = await _json('$root/$courseId/$file');
        assembled.add({...module, 'levels': moduleDoc['levels']});
      } else {
        assembled.add(module);
      }
    }
    return {...manifest, 'modules': assembled};
  }
}

/// Remote content API (CDN / backend). Returns null when disabled or
/// when the content isn't available remotely.
abstract interface class RemoteContentSource {
  Future<Map<String, dynamic>?> fetchCourse(String courseId);
}

class DisabledRemoteContentSource implements RemoteContentSource {
  const DisabledRemoteContentSource();

  @override
  Future<Map<String, dynamic>?> fetchCourse(String courseId) async => null;
}

/// Persists the last good remote course document for offline use.
class ContentCache {
  const ContentCache(this._documents);

  final JsonDocumentStore _documents;

  Future<Map<String, dynamic>?> read(String courseId) =>
      _documents.read(StorageKeys.contentCache(courseId));

  Future<void> write(String courseId, Map<String, dynamic> document) =>
      _documents.write(
        StorageKeys.contentCache(courseId),
        document,
        schemaVersion: StorageKeys.contentCacheSchema,
      );

  Future<void> clear(String courseId) =>
      _documents.delete(StorageKeys.contentCache(courseId));
}
