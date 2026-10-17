import 'dart:convert';

import 'package:bytecraft/features/playground/data/practice_repository.dart';
import 'package:bytecraft/features/playground/domain/practice_task.dart';
import 'package:bytecraft/features/playground/domain/python_runner.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/fake_python_runner.dart';

const String checkerSource = '# checker';

PracticeTask task({Map<String, Object?> requires = const {}}) => PracticeTask(
      id: 't',
      moduleId: 'm',
      title: 'Double',
      prompt: 'Print 2n',
      starter: '',
      solution: 'print(int(input()) * 2)',
      tests: const [
        PracticeTest(stdin: '2\n', expected: '4\n'),
        PracticeTest(stdin: '5\n', expected: '10\n'),
      ],
      requires: requires,
      checker: checkerSource,
    );

void main() {
  test('all tests pass when the output matches; prompts are not echoed', () async {
    final runner = FakePythonRunner((code, stdin) {
      final n = int.parse(stdin.trim());
      return RunResult(status: RunStatus.ok, stdout: '${n * 2}\n');
    });
    final report = await PracticeChecker(runner).check(task(), 'code');
    expect(report.passedAll(task()), isTrue);
    expect(runner.calls, hasLength(2), reason: 'no requirements: checker is not run');
    expect(runner.calls.every((call) => !call.echo), isTrue);
  });

  test('a failing test is reported with its output', () async {
    final runner = FakePythonRunner(
      (code, stdin) => const RunResult(status: RunStatus.ok, stdout: '4\n'),
    );
    final report = await PracticeChecker(runner).check(task(), 'print(4)');
    expect(report.passedAll(task()), isFalse);
    expect(report.outcomes.map((o) => o.passed), [true, false]);
  });

  test('requirement problems stop the check before the tests', () async {
    final runner = FakePythonRunner((code, stdin) {
      expect(code, checkerSource);
      final request = jsonDecode(stdin) as Map<String, dynamic>;
      expect(request['code'], 'print(4)');
      expect(request['requires'], {'uses': ['def']});
      return RunResult(
        status: RunStatus.ok,
        stdout: '${jsonEncode(['В решении нужно использовать: def.'])}\n',
      );
    });
    final t = task(requires: const {'uses': ['def']});
    final report = await PracticeChecker(runner).check(t, 'print(4)');
    expect(report.problems, ['В решении нужно использовать: def.']);
    expect(report.outcomes, isEmpty);
    expect(report.passedAll(t), isFalse);
    expect(runner.calls, hasLength(1));
  });

  test('a broken checker never blocks the player', () async {
    final runner = FakePythonRunner((code, stdin) => code == checkerSource
        ? const RunResult(status: RunStatus.error, stderr: 'boom')
        : RunResult(status: RunStatus.ok, stdout: '${int.parse(stdin.trim()) * 2}\n'));
    final t = task(requires: const {'uses': ['def']});
    final report = await PracticeChecker(runner).check(t, 'code');
    expect(report.problems, isEmpty);
    expect(report.passedAll(t), isTrue);
  });

  test('an unavailable interpreter stops after the first test', () async {
    final runner = FakePythonRunner(
      (code, stdin) => const RunResult(status: RunStatus.unavailable),
    );
    final report = await PracticeChecker(runner).check(task(), 'code');
    expect(report.outcomes, hasLength(1));
  });

  test('tasks parse with requirements and the shared checker', () {
    final tasks = PracticeRepository.parseTasks({
      'checker': 'print([])',
      'tasks': [
        {
          'id': 't1',
          'module': 'm',
          'title': 'T',
          'prompt': 'p',
          'solution': 's',
          'requires': {'defines': ['f']},
          'tests': [
            {'stdin': '1\n', 'expected': '1\n'},
          ],
        },
        {'id': 'broken'},
      ],
    });
    expect(tasks.single.requires, {'defines': ['f']});
    expect(tasks.single.checker, 'print([])');
  });

  test('error explainer names the last error in a traceback', () {
    expect(
      PythonErrorExplainer.explain(
        'Traceback (most recent call last):\n  File "main.py", line 1\nZeroDivisionError: division by zero',
      ),
      'Деление на ноль.',
    );
    expect(PythonErrorExplainer.explain('all good'), isNull);
  });
}
