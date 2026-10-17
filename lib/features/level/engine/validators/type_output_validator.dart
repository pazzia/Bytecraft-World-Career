import '../../../courses/domain/level_definition.dart';
import '../../../courses/domain/level_payload.dart';
import '../../domain/answer.dart';
import '../../domain/validation_outcome.dart';
import '../answer_validator.dart';

/// Compares typed output with the real program output line by line.
/// Wrong parts are the (zero-based) output lines that differ.
class TypeOutputValidator implements AnswerValidator {
  const TypeOutputValidator();

  @override
  ValidationOutcome validate(LevelDefinition level, Answer answer) {
    final payload = level.payload;
    if (payload is! TypeOutputPayload || answer is! TextAnswer) {
      answerMismatch(level, answer);
    }
    final wrong = OutputText.differentLines(
      expected: payload.expectedOutput,
      actual: answer.text,
    );
    return wrong.isEmpty
        ? ValidationOutcome.correct
        : ValidationOutcome.incorrect(wrong);
  }
}

/// Output comparison that forgives what a phone keyboard or invisible
/// whitespace changes, but nothing a program could print differently.
abstract final class OutputText {
  static const Map<String, String> _replacements = {
    '\r\n': '\n',
    '\r': '\n',
    ' ': ' ', // no-break space
    '“': '"', // smart quotes from mobile keyboards
    '”': '"',
    '„': '"',
    '«': '"',
    '»': '"',
    '‘': "'",
    '’': "'",
  };

  /// Lines with trailing spaces removed and trailing empty lines dropped.
  static List<String> lines(String text) {
    var normalized = text;
    _replacements.forEach((from, to) {
      normalized = normalized.replaceAll(from, to);
    });
    final result = normalized
        .split('\n')
        .map((line) => line.trimRight())
        .toList();
    while (result.isNotEmpty && result.last.isEmpty) {
      result.removeLast();
    }
    return result;
  }

  /// Indexes of lines that differ, including missing or extra lines.
  static Set<int> differentLines({
    required String expected,
    required String actual,
  }) {
    final want = lines(expected);
    final got = lines(actual);
    final wrong = <int>{};
    final count = want.length > got.length ? want.length : got.length;
    for (var i = 0; i < count; i++) {
      final a = i < want.length ? want[i] : null;
      final b = i < got.length ? got[i] : null;
      if (a != b) wrong.add(i);
    }
    return wrong;
  }
}
