import 'level_definition.dart';

class CourseModule {
  CourseModule({
    required this.id,
    required this.title,
    required this.description,
    required this.icon,
    required List<LevelDefinition> levels,
  }) : levels = List.unmodifiable(levels);

  final String id;
  final String title;
  final String description;

  /// Emoji or short glyph used on the map header.
  final String icon;
  final List<LevelDefinition> levels;
}

/// A course: ordered modules, each with ordered levels.
/// The flattened order of levels is the canonical learning path.
class Course {
  Course({
    required this.id,
    required this.title,
    required this.language,
    required this.version,
    required List<CourseModule> modules,
  }) : modules = List.unmodifiable(modules) {
    final flat = <LevelDefinition>[];
    for (final module in this.modules) {
      flat.addAll(module.levels);
    }
    levels = List.unmodifiable(flat);
    _indexById = {
      for (var i = 0; i < levels.length; i++) levels[i].id: i,
    };
    _moduleByLevelId = {
      for (final module in this.modules)
        for (final level in module.levels) level.id: module,
    };
  }

  final String id;
  final String title;
  final String language;

  /// Content version; higher versions replace cached/bundled content.
  final int version;
  final List<CourseModule> modules;
  late final List<LevelDefinition> levels;
  late final Map<String, int> _indexById;
  late final Map<String, CourseModule> _moduleByLevelId;

  int indexOf(String levelId) => _indexById[levelId] ?? -1;

  LevelDefinition? levelById(String levelId) {
    final index = _indexById[levelId];
    return index == null ? null : levels[index];
  }

  CourseModule? moduleOf(String levelId) => _moduleByLevelId[levelId];

  List<LevelDefinition> get playableLevels =>
      levels.where((level) => level.isSupported).toList(growable: false);
}
