enum LevelType { multipleChoice, fillMissing, codeOrdering }

class Level {
  const Level({required this.id, required this.module, required this.title, required this.description, required this.type, required this.code, required this.options, required this.correctAnswer, required this.explanation, required this.xp});
  final String id;
  final String module;
  final String title;
  final String description;
  final LevelType type;
  final String code;
  final List<String> options;
  final String correctAnswer;
  final String explanation;
  final int xp;
}
