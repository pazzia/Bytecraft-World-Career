import 'package:flutter/material.dart';

import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';
import '../../../core/theme/game_colors.dart';
import '../domain/practice_task.dart';
import '../domain/python_runner.dart';

/// Result of a run: status, stdout, traceback and a plain explanation of
/// the error.
class RunOutputView extends StatelessWidget {
  const RunOutputView({super.key, required this.result});

  final RunResult result;

  String get _status => switch (result.status) {
        RunStatus.ok => 'Готово за ${result.duration.inMilliseconds} мс',
        RunStatus.error => 'Ошибка',
        RunStatus.timeout =>
          'Остановлено: программа работала дольше ${result.duration.inSeconds > 0 ? result.duration.inSeconds : 5} с',
        RunStatus.limit => 'Остановлено: слишком много вывода',
        RunStatus.unavailable => 'Интерпретатор недоступен',
      };

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    final textTheme = Theme.of(context).textTheme;
    final isOk = result.status == RunStatus.ok;
    final explanation = PythonErrorExplainer.explain(result.stderr);
    final stdout = result.stdout.endsWith('\n')
        ? result.stdout.substring(0, result.stdout.length - 1)
        : result.stdout;
    final stderr = result.stderr.trimRight();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            Icon(
              isOk ? Icons.check_circle_rounded : Icons.error_rounded,
              color: isOk ? game.success : game.error,
              size: 20,
            ),
            const SizedBox(width: Spacing.xs),
            Expanded(
              child: Text(
                _status,
                style: textTheme.labelLarge?.copyWith(
                  color: isOk ? game.success : game.error,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: Spacing.sm),
        Container(
          padding: const EdgeInsets.all(Spacing.md),
          decoration: BoxDecoration(
            color: game.board,
            borderRadius: AppRadius.lgAll,
          ),
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: SelectableText.rich(
              TextSpan(
                children: [
                  if (stdout.isNotEmpty)
                    TextSpan(
                      text: stdout,
                      style: AppTypography.code(color: game.codeText, size: 14),
                    ),
                  if (stdout.isNotEmpty && stderr.isNotEmpty)
                    const TextSpan(text: '\n'),
                  if (stderr.isNotEmpty)
                    TextSpan(
                      text: stderr,
                      style: AppTypography.code(color: game.errorBright, size: 14),
                    ),
                  if (stdout.isEmpty && stderr.isEmpty)
                    TextSpan(
                      text: '(программа ничего не вывела)',
                      style: AppTypography.code(color: game.boardMuted, size: 14),
                    ),
                ],
              ),
            ),
          ),
        ),
        if (explanation != null) ...[
          const SizedBox(height: Spacing.sm),
          Container(
            padding: const EdgeInsets.all(Spacing.md),
            decoration: BoxDecoration(
              color: game.errorTint,
              borderRadius: AppRadius.lgAll,
            ),
            child: Text(explanation, style: textTheme.bodyMedium),
          ),
        ],
      ],
    );
  }
}

/// One line about the interpreter: loading, ready, failed.
class RunnerStatusLine extends StatelessWidget {
  const RunnerStatusLine({
    super.key,
    required this.state,
    this.version,
    this.error,
    this.onRetry,
  });

  final PythonRunnerState state;
  final String? version;
  final String? error;
  final VoidCallback? onRetry;

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    final style = Theme.of(context).textTheme.bodySmall?.copyWith(color: game.textMuted);
    return switch (state) {
      PythonRunnerState.idle => Text('Python запустится при первом запуске кода', style: style),
      PythonRunnerState.loading => Row(
          children: [
            const SizedBox.square(
              dimension: 14,
              child: CircularProgressIndicator(strokeWidth: 2),
            ),
            const SizedBox(width: Spacing.sm),
            Expanded(
              child: Text('Загружаю Python (первый раз — до полуминуты)…', style: style),
            ),
          ],
        ),
      PythonRunnerState.ready =>
        Text('Python ${version ?? ''} готов · без сети, стандартная библиотека', style: style),
      PythonRunnerState.failed => Row(
          children: [
            Expanded(
              child: Text(
                error ?? 'Интерпретатор не запустился',
                style: style?.copyWith(color: game.error),
              ),
            ),
            if (onRetry != null)
              TextButton(onPressed: onRetry, child: const Text('Повторить')),
          ],
        ),
    };
  }
}
