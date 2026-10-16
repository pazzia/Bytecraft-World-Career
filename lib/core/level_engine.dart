import '../models/level.dart';

class LevelResult {
  const LevelResult({required this.isCorrect, required this.stars, required this.xpAwarded});
  final bool isCorrect;
  final int stars;
  final int xpAwarded;
}

class LevelEngine {
  const LevelEngine();

  bool validate(Level level, String submittedAnswer) => submittedAnswer.trim() == level.correctAnswer.trim();

  LevelResult evaluate(Level level, String submittedAnswer, int mistakes) {
    final correct = validate(level, submittedAnswer);
    if (!correct) return const LevelResult(isCorrect: false, stars: 0, xpAwarded: 0);
    final stars = mistakes == 0 ? 3 : (mistakes == 1 ? 2 : 1);
    final multiplier = stars == 3 ? 1.0 : (stars == 2 ? 0.9 : 0.75);
    return LevelResult(isCorrect: true, stars: stars, xpAwarded: (level.xp * multiplier).round());
  }
}
