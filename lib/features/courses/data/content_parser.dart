import '../../../core/errors/app_exception.dart';
import '../../../core/utils/json_reader.dart';
import '../domain/course.dart';
import '../domain/course_summary.dart';
import '../domain/fill_code_template.dart';
import '../domain/level_definition.dart';
import '../domain/level_payload.dart';
import '../domain/level_type.dart';

typedef PayloadParser = LevelPayload Function(
  JsonReader payload,
  JsonReader level,
);

/// Converts content JSON into domain objects.
///
/// Course-level structure errors throw [ContentFormatException].
/// Level-level errors never break the course: the level becomes
/// [UnsupportedPayload] and is skipped by the player.
class ContentParser {
  ContentParser({Map<LevelType, PayloadParser>? payloadParsers})
      : _payloadParsers = payloadParsers ?? defaultPayloadParsers;

  static const int defaultDifficulty = 1;
  static const int defaultLivesPenalty = 1;

  static final Map<LevelType, PayloadParser> defaultPayloadParsers = {
    LevelType.multipleChoice: _parseMultipleChoice,
    LevelType.predictOutput: _parseMultipleChoice,
    LevelType.fillCode: _parseFillCode,
    LevelType.codeOrdering: _parseCodeOrdering,
    LevelType.bugFinder: _parseBugFinder,
  };

  final Map<LevelType, PayloadParser> _payloadParsers;

  List<CourseSummary> parseCatalog(Map<String, dynamic> json) {
    try {
      final reader = JsonReader(json);
      return reader.requireObjectList('courses').map((course) {
        return CourseSummary(
          id: course.requireString('id'),
          title: course.requireString('title'),
          language: course.requireString('language'),
          icon: course.optionalString('icon') ?? '',
          description: course.optionalString('description') ?? '',
          availability: course.optionalString('status') == 'available'
              ? CourseAvailability.available
              : CourseAvailability.comingSoon,
        );
      }).toList(growable: false);
    } on JsonFormatException catch (error) {
      throw ContentFormatException(error.message);
    }
  }

  /// Parses an assembled course document (modules with inline `levels`).
  Course parseCourse(Map<String, dynamic> json) {
    try {
      final reader = JsonReader(json);
      final courseId = reader.requireString('id');
      final modules = reader.requireObjectList('modules').map((module) {
        final moduleId = module.requireString('id');
        return CourseModule(
          id: moduleId,
          title: module.requireString('title'),
          description: module.optionalString('description') ?? '',
          icon: module.optionalString('icon') ?? '',
          levels: module
              .requireObjectList('levels')
              .map((level) => parseLevel(level, courseId, moduleId))
              .toList(),
        );
      }).toList();
      _ensureUniqueIds(modules);
      return Course(
        id: courseId,
        title: reader.requireString('title'),
        language: reader.requireString('language'),
        version: reader.requireInt('version'),
        modules: modules,
      );
    } on JsonFormatException catch (error) {
      throw ContentFormatException(error.message);
    }
  }

  LevelDefinition parseLevel(
    JsonReader level,
    String courseId,
    String moduleId,
  ) {
    final id = level.requireString('id');
    final type = LevelType.fromId(level.optionalString('type'));
    LevelPayload payload;
    try {
      final parser = _payloadParsers[type];
      payload = parser == null
          ? UnsupportedPayload(reason: 'Unsupported type "${type.id}"')
          : parser(level.requireObject('payload'), level);
    } on JsonFormatException catch (error) {
      payload = UnsupportedPayload(reason: error.message);
    }
    return LevelDefinition(
      id: id,
      courseId: courseId,
      moduleId: moduleId,
      type: type,
      role: LevelRole.fromId(level.optionalString('role')),
      title: level.requireString('title'),
      prompt: level.requireString('prompt'),
      code: level.optionalString('code'),
      difficulty: level.optionalInt('difficulty') ?? defaultDifficulty,
      xpOverride: level.optionalInt('xp'),
      livesPenalty: level.optionalInt('livesPenalty') ?? defaultLivesPenalty,
      hint: level.optionalString('hint'),
      explanation: level.optionalString('explanation'),
      payload: payload,
    );
  }

  static void _ensureUniqueIds(List<CourseModule> modules) {
    final seen = <String>{};
    for (final module in modules) {
      for (final level in module.levels) {
        if (!seen.add(level.id)) {
          throw JsonFormatException('Duplicate level id "${level.id}"');
        }
      }
    }
  }

  static LevelPayload _parseMultipleChoice(JsonReader p, JsonReader level) {
    final options = p.requireStringList('options');
    final correct = p.requireInt('correctIndex');
    if (options.length < 2) {
      throw JsonFormatException('${p.path}.options: need at least 2 options');
    }
    if (correct < 0 || correct >= options.length) {
      throw JsonFormatException('${p.path}.correctIndex: out of range');
    }
    return MultipleChoicePayload(options: options, correctIndex: correct);
  }

  static LevelPayload _parseFillCode(JsonReader p, JsonReader level) {
    final template = p.requireString('template');
    final options = p.requireStringList('options');
    final answers = p.requireStringList('answers');
    final blanks = FillCodeTemplate.blankIndexes(template);
    final expected = List<int>.generate(answers.length, (i) => i);
    if (blanks.length != expected.length ||
        !blanks.every((index) => index < answers.length)) {
      throw JsonFormatException(
        '${p.path}: template blanks $blanks do not match '
        '${answers.length} answers',
      );
    }
    for (final answer in answers) {
      if (!options.contains(answer)) {
        throw JsonFormatException('${p.path}: answer "$answer" not in options');
      }
    }
    return FillCodePayload(
      template: template,
      options: options,
      answers: answers,
    );
  }

  static LevelPayload _parseCodeOrdering(JsonReader p, JsonReader level) {
    final lines = p.requireStringList('lines');
    if (lines.length < 2) {
      throw JsonFormatException('${p.path}.lines: need at least 2 lines');
    }
    final alternatives = p.optionalIntMatrix('alternativeOrders');
    for (final order in alternatives) {
      final sorted = [...order]..sort();
      final isPermutation = sorted.length == lines.length &&
          List.generate(lines.length, (i) => i)
              .every((i) => sorted[i] == i);
      if (!isPermutation) {
        throw JsonFormatException(
          '${p.path}.alternativeOrders: $order is not a permutation',
        );
      }
    }
    return CodeOrderingPayload(lines: lines, alternativeOrders: alternatives);
  }

  static LevelPayload _parseBugFinder(JsonReader p, JsonReader level) {
    final code = level.requireString('code');
    final lineCount = code.split('\n').length;
    final buggy = p.requireIntList('buggyLines').toSet();
    if (buggy.isEmpty || buggy.any((i) => i < 0 || i >= lineCount)) {
      throw JsonFormatException('${p.path}.buggyLines: out of range');
    }
    return BugFinderPayload(buggyLines: Set.unmodifiable(buggy));
  }
}
