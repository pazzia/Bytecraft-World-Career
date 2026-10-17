import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';
import '../../../core/theme/game_colors.dart';
import '../../../shared/widgets/app_button.dart';
import '../../../shared/widgets/code_block.dart';
import '../../progress/presentation/progress_providers.dart';
import '../domain/practice_task.dart';
import '../domain/python_runner.dart';
import 'code_editor.dart';
import 'playground_providers.dart';
import 'run_output_view.dart';

/// One coding exercise: statement, editor, "check" runs every test.
class PracticeTaskScreen extends ConsumerStatefulWidget {
  const PracticeTaskScreen({super.key, required this.taskId});

  final String taskId;

  @override
  ConsumerState<PracticeTaskScreen> createState() => _PracticeTaskScreenState();
}

class _PracticeTaskScreenState extends ConsumerState<PracticeTaskScreen> {
  TextEditingController? _code;
  PracticeReport? _report;
  RunResult? _lastRun;
  bool _checking = false;
  bool _showSolution = false;
  bool _showHint = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) ref.read(pythonRunnerProvider).start().ignore();
    });
  }

  @override
  void dispose() {
    _code?.dispose();
    super.dispose();
  }

  Future<void> _check(PracticeTask task) async {
    FocusScope.of(context).unfocus();
    setState(() {
      _checking = true;
      _report = null;
      _lastRun = null;
    });
    final report = await PracticeChecker(ref.read(pythonRunnerProvider))
        .check(task, _code!.text);
    if (!mounted) return;
    if (report.passedAll(task)) {
      final courseId = await ref.read(activeCourseIdProvider.future);
      await ref.read(practiceRepositoryProvider).markSolved(courseId, task.id);
      ref.read(progressRevisionProvider.notifier).bump();
    }
    if (!mounted) return;
    setState(() {
      _checking = false;
      _report = report;
    });
  }

  Future<void> _runOnce(PracticeTask task) async {
    FocusScope.of(context).unfocus();
    setState(() => _checking = true);
    final result = await ref.read(pythonRunnerProvider).run(
          _code!.text,
          stdin: task.tests.first.stdin,
        );
    if (!mounted) return;
    setState(() {
      _checking = false;
      _lastRun = result;
      _report = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    final tasks = ref.watch(practiceTasksProvider).value;
    final task = tasks?.where((task) => task.id == widget.taskId).firstOrNull;
    final solved = ref.watch(solvedPracticeProvider).value ?? const <String>{};
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    if (task == null) {
      return Scaffold(
        appBar: AppBar(),
        body: Center(
          child: tasks == null
              ? const CircularProgressIndicator()
              : const Text('Задача не найдена'),
        ),
      );
    }
    final code = _code ??= TextEditingController(text: task.starter);
    final report = _report;
    final outcomes = report?.outcomes;
    final passedAll = report != null && report.passedAll(task);
    return Scaffold(
      appBar: AppBar(title: Text(task.title)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(
          Spacing.page,
          Spacing.md,
          Spacing.page,
          Spacing.huge,
        ),
        children: [
          if (solved.contains(task.id))
            Padding(
              padding: const EdgeInsets.only(bottom: Spacing.md),
              child: Row(
                children: [
                  Icon(Icons.check_circle_rounded, color: game.success),
                  const SizedBox(width: Spacing.sm),
                  Text('Задача решена', style: textTheme.titleSmall),
                ],
              ),
            ),
          Text(task.prompt, style: textTheme.bodyLarge),
          const SizedBox(height: Spacing.sm),
          Text(
            'Проверка запускает программу на нескольких тестах: первый показан '
            'ниже, остальные откроются, если не пройдут. Подсказка в input() '
            'на проверку не влияет.',
            style: textTheme.bodySmall?.copyWith(color: game.textMuted),
          ),
          const SizedBox(height: Spacing.md),
          _ExampleTest(test: task.tests.first),
          const SizedBox(height: Spacing.lg),
          CodeEditor(controller: code, minLines: 8),
          const SizedBox(height: Spacing.lg),
          Row(
            children: [
              Expanded(
                flex: 2,
                child: AppButton(
                  label: 'Запустить',
                  variant: AppButtonVariant.secondary,
                  onPressed: _checking ? null : () => _runOnce(task),
                ),
              ),
              const SizedBox(width: Spacing.md),
              Expanded(
                flex: 3,
                child: AppButton(
                  key: const ValueKey('practice_check'),
                  label: 'Проверить',
                  isLoading: _checking,
                  onPressed: _checking ? null : () => _check(task),
                ),
              ),
            ],
          ),
          if (_lastRun != null) ...[
            const SizedBox(height: Spacing.xl),
            Text('Запуск на вводе из примера', style: textTheme.titleSmall),
            const SizedBox(height: Spacing.sm),
            RunOutputView(result: _lastRun!),
          ],
          if (report != null && report.problems.isNotEmpty) ...[
            const SizedBox(height: Spacing.xl),
            Text(
              'Решение написано не так, как требует задача',
              style: textTheme.titleMedium?.copyWith(color: game.error),
            ),
            const SizedBox(height: Spacing.sm),
            for (final problem in report.problems)
              Padding(
                padding: const EdgeInsets.only(bottom: Spacing.xs),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(Icons.rule_rounded, size: 20, color: game.error),
                    const SizedBox(width: Spacing.sm),
                    Expanded(child: Text(problem, style: textTheme.bodyMedium)),
                  ],
                ),
              ),
          ],
          if (outcomes != null && outcomes.isNotEmpty) ...[
            const SizedBox(height: Spacing.xl),
            Text(
              passedAll
                  ? 'Все тесты пройдены!'
                  : 'Пройдено ${outcomes.where((o) => o.passed).length} из ${task.tests.length}',
              style: textTheme.titleMedium?.copyWith(
                color: passedAll ? game.success : game.error,
              ),
            ),
            const SizedBox(height: Spacing.sm),
            for (var i = 0; i < outcomes.length; i++)
              _TestRow(index: i, outcome: outcomes[i]),
          ],
          const SizedBox(height: Spacing.xl),
          if (task.hint != null)
            _showHint
                ? Container(
                    padding: const EdgeInsets.all(Spacing.md),
                    decoration: BoxDecoration(
                      color: game.primaryTint,
                      borderRadius: AppRadius.lgAll,
                    ),
                    child: Text(task.hint!, style: textTheme.bodyMedium),
                  )
                : AppButton(
                    label: 'Подсказка',
                    variant: AppButtonVariant.quiet,
                    onPressed: () => setState(() => _showHint = true),
                  ),
          if (_showSolution) ...[
            const SizedBox(height: Spacing.md),
            Text('Эталонное решение', style: textTheme.titleSmall),
            const SizedBox(height: Spacing.sm),
            CodeBlock(code: task.solution),
          ] else if (solved.contains(task.id) ||
              (report != null && !passedAll))
            AppButton(
              label: 'Показать эталонное решение',
              variant: AppButtonVariant.quiet,
              onPressed: () => setState(() => _showSolution = true),
            ),
        ],
      ),
    );
  }
}

class _ExampleTest extends StatelessWidget {
  const _ExampleTest({required this.test});

  final PracticeTest test;

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    final style = AppTypography.code(color: game.codeText, size: 14);
    final label = AppTypography.code(color: game.codeLineNumber, size: 12, weight: FontWeight.w700);
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(Spacing.md),
      decoration: BoxDecoration(color: game.board, borderRadius: AppRadius.lgAll),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (test.stdin.isNotEmpty) ...[
            Text('Ввод', style: label),
            Text(test.stdin.trimRight(), style: style),
            const SizedBox(height: Spacing.sm),
          ],
          Text('Ожидаемый вывод', style: label),
          Text(test.expected.trimRight(), style: style),
        ],
      ),
    );
  }
}

class _TestRow extends StatelessWidget {
  const _TestRow({required this.index, required this.outcome});

  final int index;
  final TestOutcome outcome;

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    final textTheme = Theme.of(context).textTheme;
    return Padding(
      padding: const EdgeInsets.only(bottom: Spacing.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Icon(
                outcome.passed ? Icons.check_rounded : Icons.close_rounded,
                color: outcome.passed ? game.success : game.error,
              ),
              const SizedBox(width: Spacing.xs),
              Text('Тест ${index + 1}', style: textTheme.titleSmall),
            ],
          ),
          if (!outcome.passed) ...[
            const SizedBox(height: Spacing.xs),
            if (outcome.test.stdin.isNotEmpty)
              Text(
                'Ввод: ${outcome.test.stdin.trimRight().replaceAll('\n', ' ⏎ ')}',
                style: AppTypography.code(size: 13),
              ),
            Text(
              'Ожидалось: ${outcome.test.expected.trimRight().replaceAll('\n', ' ⏎ ')}',
              style: AppTypography.code(size: 13, color: game.success),
            ),
            const SizedBox(height: Spacing.xs),
            RunOutputView(result: outcome.result),
          ],
        ],
      ),
    );
  }
}
