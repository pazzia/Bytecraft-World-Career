import 'level_payload.dart';
import 'level_type.dart';

/// Immutable, data-driven description of one level.
class LevelDefinition {
  const LevelDefinition({
    required this.id,
    required this.courseId,
    required this.moduleId,
    required this.type,
    required this.role,
    required this.title,
    required this.prompt,
    required this.difficulty,
    required this.livesPenalty,
    required this.payload,
    this.code,
    this.xpOverride,
    this.hint,
    this.explanation,
  });

  final String id;
  final String courseId;
  final String moduleId;
  final LevelType type;
  final LevelRole role;
  final String title;

  /// Task statement shown above the interactive area.
  final String prompt;

  /// Optional code shown with the task (MC, bug finder).
  final String? code;
  final int difficulty;

  /// Explicit XP reward; when null the reward comes from game rules by role.
  final int? xpOverride;
  final int livesPenalty;
  final String? hint;
  final String? explanation;
  final LevelPayload payload;

  bool get isSupported => payload is! UnsupportedPayload;

  List<String> get codeLines => code == null ? const [] : code!.split('\n');

  @override
  String toString() => 'LevelDefinition($id, ${type.id})';
}
