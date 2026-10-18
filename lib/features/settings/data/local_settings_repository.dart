import '../../../core/storage/json_document_store.dart';
import '../../../core/storage/storage_keys.dart';
import '../domain/app_settings.dart';
import '../domain/settings_repository.dart';

class LocalSettingsRepository implements SettingsRepository {
  LocalSettingsRepository(this._documents, {required this.defaultCourseId});

  final JsonDocumentStore _documents;
  final String defaultCourseId;

  @override
  Future<AppSettings> load() async {
    final json = await _documents.read(StorageKeys.settings);
    if (json == null) return AppSettings.initial(defaultCourseId);
    return AppSettings.fromJson(json, defaultCourseId: defaultCourseId);
  }

  @override
  Future<void> save(AppSettings settings) => _documents.write(
        StorageKeys.settings,
        settings.toJson(),
        schemaVersion: StorageKeys.settingsSchema,
      );
}
