import '../../features/courses/domain/level_definition.dart';
import '../../features/level/domain/answer.dart';

class TutorReply {
  const TutorReply({required this.text, this.isFromAi = false});

  final String text;

  /// False when the reply is a static fallback (offline, mock, free tier).
  final bool isFromAi;
}

/// AI tutor port. The Level Engine never depends on it — UI asks the tutor
/// on demand, so any LLM provider can be plugged in behind this interface.
abstract interface class AITutorService {
  Future<TutorReply> explainMistake({
    required LevelDefinition level,
    required Answer answer,
  });

  Future<TutorReply> explainCode(String code, {required String language});

  Future<TutorReply> hint(LevelDefinition level);

  Future<TutorReply> explainSolution(LevelDefinition level);

  /// Generates a similar exercise; null when unavailable.
  Future<LevelDefinition?> generateSimilar(LevelDefinition level);
}

/// Offline mock that answers from the level's authored hint/explanation.
class MockAITutorService implements AITutorService {
  const MockAITutorService();

  static const String _fallback = 'Попробуйте разобрать код построчно.';

  @override
  Future<TutorReply> explainMistake({
    required LevelDefinition level,
    required Answer answer,
  }) async =>
      TutorReply(text: level.hint ?? _fallback);

  @override
  Future<TutorReply> explainCode(
    String code, {
    required String language,
  }) async =>
      const TutorReply(text: _fallback);

  @override
  Future<TutorReply> hint(LevelDefinition level) async =>
      TutorReply(text: level.hint ?? _fallback);

  @override
  Future<TutorReply> explainSolution(LevelDefinition level) async =>
      TutorReply(text: level.explanation ?? _fallback);

  @override
  Future<LevelDefinition?> generateSimilar(LevelDefinition level) async =>
      null;
}
