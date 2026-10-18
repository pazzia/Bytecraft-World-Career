/// Interaction mechanic of a level. Serialized by [id] in content JSON.
///
/// Unknown ids map to [unknown] so content published for a newer app
/// version never crashes an older client — such levels are skipped.
enum LevelType {
  multipleChoice('multiple_choice'),
  fillCode('fill_code'),
  codeOrdering('code_ordering'),
  bugFinder('bug_finder'),
  predictOutput('predict_output'),
  typeOutput('type_output'),
  matchPairs('match_pairs'),
  multiSelect('multi_select'),
  robotPuzzle('robot_puzzle'),
  optimization('optimization'),
  unknown('unknown');

  const LevelType(this.id);

  final String id;

  static LevelType fromId(String? id) => LevelType.values.firstWhere(
        (type) => type.id == id,
        orElse: () => LevelType.unknown,
      );
}

/// Place of a level in the learning arc. Independent of [LevelType]:
/// a boss can be any mechanic, it just weighs more (XP, map icon).
enum LevelRole {
  lesson('lesson'),
  practice('practice'),
  challenge('challenge'),
  boss('boss');

  const LevelRole(this.id);

  final String id;

  static LevelRole fromId(String? id) => LevelRole.values.firstWhere(
        (role) => role.id == id,
        orElse: () => LevelRole.lesson,
      );
}
