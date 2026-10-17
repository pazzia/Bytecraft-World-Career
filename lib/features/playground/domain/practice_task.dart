import '../../level/engine/validators/type_output_validator.dart';
import 'python_runner.dart';

/// A "write the program" exercise: the player's code must pass every test
/// (stdin -> expected stdout). The reference solution and the tests were
/// checked by running them in Python when the content was built.
class PracticeTask {
  PracticeTask({
    required this.id,
    required this.moduleId,
    required this.title,
    required this.prompt,
    required this.starter,
    required List<PracticeTest> tests,
    required this.solution,
    this.hint,
    this.difficulty = 1,
  }) : tests = List.unmodifiable(tests);

  final String id;
  final String moduleId;
  final String title;
  final String prompt;

  /// Code the editor starts with.
  final String starter;
  final List<PracticeTest> tests;
  final String solution;
  final String? hint;
  final int difficulty;
}

class PracticeTest {
  const PracticeTest({required this.stdin, required this.expected});

  final String stdin;
  final String expected;
}

class TestOutcome {
  const TestOutcome({
    required this.test,
    required this.result,
    required this.passed,
  });

  final PracticeTest test;
  final RunResult result;
  final bool passed;
}

/// Runs a task's tests against the player's code.
class PracticeChecker {
  const PracticeChecker(this._runner);

  final PythonRunner _runner;

  static const Duration testTimeout = Duration(seconds: 5);

  Future<List<TestOutcome>> check(PracticeTask task, String code) async {
    final outcomes = <TestOutcome>[];
    for (final test in task.tests) {
      final result =
          await _runner.run(code, stdin: test.stdin, timeout: testTimeout);
      final passed = result.isOk &&
          OutputText.differentLines(
            expected: test.expected,
            actual: result.stdout,
          ).isEmpty;
      outcomes.add(TestOutcome(test: test, result: result, passed: passed));
      // The interpreter is gone: further tests would fail the same way.
      if (result.status == RunStatus.unavailable) break;
    }
    return outcomes;
  }
}

/// Plain-Russian explanation of a Python error, by its name in stderr.
abstract final class PythonErrorExplainer {
  static const Map<String, String> _explanations = {
    'SyntaxError': 'Синтаксическая ошибка: Python не понимает запись. '
        'Проверьте двоеточия, скобки и кавычки в указанной строке.',
    'IndentationError': 'Ошибка отступа: тело if/for/def должно быть '
        'сдвинуто одинаково (обычно на 4 пробела).',
    'NameError': 'Имя не найдено: переменная или функция не определена '
        'или в имени опечатка.',
    'TypeError': 'Операция не подходит для этого типа: например, '
        'число складывают со строкой или функции передали не те аргументы.',
    'ValueError': 'Тип правильный, а значение — нет: например, int("abc").',
    'ZeroDivisionError': 'Деление на ноль.',
    'IndexError': 'Индекс за пределами списка или строки.',
    'KeyError': 'В словаре нет такого ключа.',
    'AttributeError': 'У объекта нет такого атрибута или метода.',
    'RecursionError': 'Слишком глубокая рекурсия: функция вызывает себя '
        'без условия остановки.',
    'ModuleNotFoundError': 'Такого модуля нет во встроенном интерпретаторе: '
        'доступна стандартная библиотека без сети.',
    'EOFError': 'Программа ждёт ввода (input), а данных нет. '
        'Заполните поле «Ввод»: каждая строка — один input().',
    'UnboundLocalError': 'Локальную переменную читают до присваивания: '
        'внутри функции она не связана с глобальной.',
    'StopIteration': 'Итератор закончился: next() больше нечего вернуть.',
    'AssertionError': 'Проверка assert не прошла.',
  };

  static final RegExp _errorName = RegExp(r'^(\w+(?:Error|Exception|Iteration))\b', multiLine: true);

  /// Explanation for the last error named in [stderr], or null.
  static String? explain(String stderr) {
    final matches = _errorName.allMatches(stderr).toList();
    if (matches.isEmpty) return null;
    return _explanations[matches.last.group(1)];
  }
}
