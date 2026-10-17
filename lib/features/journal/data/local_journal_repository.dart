import '../../../core/storage/json_document_store.dart';
import '../../../core/storage/storage_keys.dart';
import '../domain/journal.dart';

/// Journal persistence. Lives under the player prefix, so "reset progress"
/// clears it together with the rest of the player state.
class LocalJournalRepository {
  const LocalJournalRepository(this._documents);

  final JsonDocumentStore _documents;

  Future<Journal> load(String courseId) async {
    final json = await _documents.read(StorageKeys.journal(courseId));
    if (json == null || json['courseId'] != courseId) {
      return Journal(courseId: courseId);
    }
    try {
      return Journal.fromJson(json);
    } catch (_) {
      return Journal(courseId: courseId);
    }
  }

  Future<void> save(Journal journal) => _documents.write(
        StorageKeys.journal(journal.courseId),
        journal.toJson(),
        schemaVersion: StorageKeys.journalSchema,
      );
}
