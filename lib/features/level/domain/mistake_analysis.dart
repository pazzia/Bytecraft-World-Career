import '../../courses/domain/level_definition.dart';
import '../../courses/domain/level_payload.dart';
import '../engine/validators/type_output_validator.dart';
import 'answer.dart';
import 'validation_outcome.dart';

/// Short explanation of a concrete wrong answer, shown in the feedback
/// panel. Never reveals the correct answer.
class MistakeNote {
  const MistakeNote({required this.text, this.programResult});

  /// What is wrong with the answer, in plain words.
  final String text;

  /// What the program does with the player's version (fill-code), as
  /// computed by real Python when the content was built.
  final String? programResult;
}

/// Pure: (level, answer, outcome) -> note.
class MistakeAnalyzer {
  const MistakeAnalyzer();

  MistakeNote analyze(
    LevelDefinition level,
    Answer? answer,
    ValidationOutcome outcome,
  ) {
    final payload = level.payload;
    switch ((payload, answer)) {
      case (final MultipleChoicePayload p, ChoiceAnswer(:final optionIndex)):
        return MistakeNote(
          text: p.feedbackFor(optionIndex) ??
              '«${p.options[optionIndex]}» — не тот вариант.',
        );
      case (final MultiSelectPayload p, OptionSetAnswer()):
        final wrong = outcome.wrongParts.toList()..sort();
        if (wrong.isNotEmpty) {
          final first = wrong.first;
          return MistakeNote(
            text: p.feedbackFor(first) ??
                '«${p.options[first]}» сюда не подходит.',
          );
        }
        final missed = outcome.missedParts.length;
        return MistakeNote(
          text: 'Всё выбранное верно, но найдено не всё: '
              'не хватает ещё $missed.',
        );
      case (final FillCodePayload p, FillCodeAnswer(:final tokens)):
        final result = p.variantResults[FillCodePayload.variantKey(tokens)];
        final blanks = outcome.wrongParts.map((i) => i + 1).toList()..sort();
        final where = blanks.length == 1
            ? 'Пропуск ${blanks.first} заполнен неверно.'
            : 'Пропуски ${blanks.join(', ')} заполнены неверно.';
        return MistakeNote(text: where, programResult: result);
      case (CodeOrderingPayload(), OrderingAnswer()):
        final positions = outcome.wrongParts.map((i) => i + 1).toList()..sort();
        return MistakeNote(
          text: positions.isEmpty
              ? 'Порядок строк неверный.'
              : 'Не на своём месте: '
                  '${positions.length == 1 ? 'строка' : 'строки'} '
                  '${positions.join(', ')}.',
        );
      case (BugFinderPayload(), LineSelectionAnswer()):
        final wrong = outcome.wrongParts.map((i) => i + 1).toList()..sort();
        if (wrong.isNotEmpty) {
          return MistakeNote(
            text: wrong.length == 1
                ? 'В строке ${wrong.first} ошибки нет.'
                : 'В строках ${wrong.join(', ')} ошибки нет.',
          );
        }
        return const MistakeNote(
          text: 'Ошибка найдена не полностью: есть ещё строка с ошибкой.',
        );
      case (final TypeOutputPayload p, TextAnswer(:final text)):
        final want = OutputText.lines(p.expectedOutput);
        final got = OutputText.lines(text);
        if (got.length != want.length) {
          return MistakeNote(
            text: 'Программа выводит ${_lines(want.length)}, '
                'а у вас ${_lines(got.length)}.',
          );
        }
        final first = (outcome.wrongParts.toList()..sort()).first;
        return MistakeNote(
          text: 'Строка ${first + 1} вывода отличается от настоящей.',
        );
      case (MatchPairsPayload(), MatchAnswer()):
        final count = outcome.wrongParts.length;
        return MistakeNote(
          text: count == 1
              ? 'Одна пара соединена неверно.'
              : 'Неверных пар: $count.',
        );
      default:
        return const MistakeNote(text: 'Ответ неверный.');
    }
  }

  static String _lines(int count) {
    final mod10 = count % 10;
    final mod100 = count % 100;
    final word = mod10 == 1 && mod100 != 11
        ? 'строку'
        : mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)
            ? 'строки'
            : 'строк';
    return '$count $word';
  }
}

/// Fine-grained hint for type-output after several failures: where the
/// first difference is, without giving the whole answer.
String? typeOutputProgressHint(TypeOutputPayload payload, String typed) {
  final want = OutputText.lines(payload.expectedOutput);
  final got = OutputText.lines(typed);
  for (var i = 0; i < want.length; i++) {
    final expected = want[i];
    final actual = i < got.length ? got[i] : '';
    if (expected == actual) continue;
    var column = 0;
    while (column < expected.length &&
        column < actual.length &&
        expected[column] == actual[column]) {
      column++;
    }
    if (column == 0) {
      return 'Строка ${i + 1}: расхождение уже в первом символе.';
    }
    final prefix = expected.substring(0, column);
    return 'Строка ${i + 1} начинается с «$prefix», '
        'расхождение в символе ${column + 1}.';
  }
  if (got.length > want.length) {
    return 'Все строки верны, но после строки ${want.length} '
        'у вас лишний текст.';
  }
  return null;
}
