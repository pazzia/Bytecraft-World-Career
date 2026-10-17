import 'dart:convert';

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
    this.requires = const {},
    this.checker,
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

  /// How the code must be written (recursion, a class, no loops...), in
  /// the format of tool/content/requirements_checker.py.
  final Map<String, Object?> requires;

  /// Source of the requirement checker (a Python program), shared by all
  /// tasks of the course. Null: requirements are not checked.
  final String? checker;
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

/// Result of checking a solution: requirement problems (how the code is
/// written) and test outcomes (what it prints).
class PracticeReport {
  const PracticeReport({this.problems = const [], this.outcomes = const []});

  /// Requirements the code breaks, in plain Russian. Tests are not run
  /// when this is not empty.
  final List<String> problems;
  final List<TestOutcome> outcomes;

  bool passedAll(PracticeTask task) =>
      problems.isEmpty &&
      outcomes.length == task.tests.length &&
      outcomes.every((outcome) => outcome.passed);
}

/// Runs a task's checks against the player's code: first the requirements
/// (in Python, by the checker from the content), then every test.
class PracticeChecker {
  const PracticeChecker(this._runner);

  final PythonRunner _runner;

  static const Duration testTimeout = Duration(seconds: 5);

  Future<PracticeReport> check(PracticeTask task, String code) async {
    final problems = await requirementProblems(task, code);
    if (problems.isNotEmpty) return PracticeReport(problems: problems);
    return PracticeReport(outcomes: await runTests(task, code));
  }

  /// Empty when the code is written as the task asks (or nothing to check).
  Future<List<String>> requirementProblems(PracticeTask task, String code) async {
    final checker = task.checker;
    if (checker == null || task.requires.isEmpty) return const [];
    final result = await _runner.run(
      checker,
      stdin: jsonEncode({'code': code, 'requires': task.requires}),
      timeout: testTimeout,
    );
    if (!result.isOk) return const []; // A checker failure never blocks the player.
    try {
      final decoded = jsonDecode(result.stdout.trim());
      if (decoded is List) return decoded.whereType<String>().toList();
    } on FormatException {
      return const [];
    }
    return const [];
  }

  Future<List<TestOutcome>> runTests(PracticeTask task, String code) async {
    final outcomes = <TestOutcome>[];
    for (final test in task.tests) {
      final result = await _runner.run(
        code,
        stdin: test.stdin,
        timeout: testTimeout,
        echoInputPrompt: false,
      );
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
    'DeadlockError': 'Взаимная блокировка: все потоки ждут друг друга или события, '
        'которое никогда не наступит. Проверьте порядок захвата замков, join и '
        'get из пустой очереди.',
    'CancelledError': 'Задачу asyncio отменили (cancel или таймаут).',
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
