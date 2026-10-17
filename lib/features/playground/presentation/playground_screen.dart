import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/routes.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/game_colors.dart';
import '../../../shared/widgets/app_button.dart';
import '../../../shared/widgets/async_value_view.dart';
import '../../../shared/widgets/segmented_switch.dart';
import '../../progress/presentation/progress_providers.dart';
import '../domain/practice_task.dart';
import '../domain/python_runner.dart';
import 'code_editor.dart';
import 'playground_providers.dart';
import 'run_output_view.dart';

enum PlaygroundTab { sandbox, tasks }

final playgroundTabProvider =
    NotifierProvider<PlaygroundTabController, PlaygroundTab>(
  PlaygroundTabController.new,
);

class PlaygroundTabController extends Notifier<PlaygroundTab> {
  @override
  PlaygroundTab build() => PlaygroundTab.sandbox;

  void select(PlaygroundTab tab) => state = tab;
}

/// "Код": a free Python sandbox and coding exercises with automatic tests.
class PlaygroundScreen extends ConsumerWidget {
  const PlaygroundScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tab = ref.watch(playgroundTabProvider);
    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(
                Spacing.page,
                Spacing.xxl,
                Spacing.page,
                Spacing.md,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text('Код', style: Theme.of(context).textTheme.headlineMedium),
                  const SizedBox(height: Spacing.md),
                  SegmentedSwitch<PlaygroundTab>(
                    semanticLabel: 'Раздел',
                    selected: tab,
                    onChanged: ref.read(playgroundTabProvider.notifier).select,
                    options: const [
                      SegmentOption(PlaygroundTab.sandbox, 'Песочница'),
                      SegmentOption(PlaygroundTab.tasks, 'Задачи'),
                    ],
                  ),
                ],
              ),
            ),
            Expanded(
              child: tab == PlaygroundTab.sandbox
                  ? const _Sandbox()
                  : const _TaskList(),
            ),
          ],
        ),
      ),
    );
  }
}

class _Sandbox extends ConsumerStatefulWidget {
  const _Sandbox();

  @override
  ConsumerState<_Sandbox> createState() => _SandboxState();
}

class _SandboxState extends ConsumerState<_Sandbox> {
  late final TextEditingController _code;
  late final TextEditingController _stdin;
  RunResult? _result;
  bool _running = false;

  @override
  void initState() {
    super.initState();
    final draft = ref.read(sandboxDraftProvider);
    _code = TextEditingController(text: draft.code);
    _stdin = TextEditingController(text: draft.stdin);
    // Warm the interpreter up while the player reads the code.
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) ref.read(pythonRunnerProvider).start().ignore();
    });
  }

  @override
  void dispose() {
    _code.dispose();
    _stdin.dispose();
    super.dispose();
  }

  Future<void> _run() async {
    FocusScope.of(context).unfocus();
    setState(() => _running = true);
    final result = await ref
        .read(pythonRunnerProvider)
        .run(_code.text, stdin: _stdin.text);
    if (!mounted) return;
    setState(() {
      _running = false;
      _result = result;
    });
  }

  @override
  Widget build(BuildContext context) {
    final runner = ref.watch(pythonRunnerProvider);
    final state = ref.watch(pythonRunnerStateProvider).value ?? runner.state;
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    return ListView(
      padding: const EdgeInsets.fromLTRB(
        Spacing.page,
        Spacing.sm,
        Spacing.page,
        Spacing.huge,
      ),
      children: [
        RunnerStatusLine(
          state: state,
          version: runner.version,
          error: runner.error,
          onRetry: () => runner.start().ignore(),
        ),
        const SizedBox(height: Spacing.md),
        CodeEditor(
          controller: _code,
          onChanged: ref.read(sandboxDraftProvider.notifier).setCode,
        ),
        const SizedBox(height: Spacing.lg),
        Text('Ввод (для input)', style: textTheme.labelLarge),
        const SizedBox(height: Spacing.xs),
        TextField(
          key: const ValueKey('sandbox_stdin'),
          controller: _stdin,
          onChanged: ref.read(sandboxDraftProvider.notifier).setStdin,
          minLines: 1,
          maxLines: 4,
          autocorrect: false,
          enableSuggestions: false,
          decoration: const InputDecoration(
            hintText: 'Каждая строка — ответ на один input()',
          ),
        ),
        const SizedBox(height: Spacing.lg),
        AppButton(
          key: const ValueKey('sandbox_run'),
          label: 'Запустить',
          icon: Icons.play_arrow_rounded,
          isLoading: _running,
          onPressed: state == PythonRunnerState.failed && runner.error != null
              ? null
              : _run,
        ),
        if (_result != null) ...[
          const SizedBox(height: Spacing.xl),
          RunOutputView(result: _result!),
        ],
        const SizedBox(height: Spacing.xl),
        Text(
          'Код выполняется прямо на телефоне. Время работы программы — до 5 секунд.',
          style: textTheme.bodySmall?.copyWith(color: game.textMuted),
        ),
      ],
    );
  }
}

class _TaskList extends ConsumerWidget {
  const _TaskList();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tasks = ref.watch(practiceTasksProvider);
    final solved = ref.watch(solvedPracticeProvider).value ?? const <String>{};
    final course = ref.watch(activeCourseProvider).value;
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    return AsyncValueView<List<PracticeTask>>(
      value: tasks,
      onRetry: () => ref.invalidate(practiceTasksProvider),
      data: (tasks) {
        final modules = course?.modules ?? const [];
        final titles = {for (final module in modules) module.id: module.title};
        final order = <String>{
          for (final module in modules) module.id,
          for (final task in tasks)
            if (!titles.containsKey(task.moduleId)) task.moduleId,
        }.toList();
        return ListView(
          padding: const EdgeInsets.fromLTRB(
            Spacing.page,
            Spacing.sm,
            Spacing.page,
            Spacing.huge,
          ),
          children: [
            Text(
              'Решено ${solved.where((id) => tasks.any((task) => task.id == id)).length} из ${tasks.length}. '
              'Программа должна пройти все тесты.',
              style: textTheme.bodyMedium?.copyWith(color: game.textMuted),
            ),
            for (final moduleId in order)
              if (tasks.any((task) => task.moduleId == moduleId)) ...[
                const SizedBox(height: Spacing.xl),
                Text(
                  titles[moduleId] ?? moduleId,
                  style: textTheme.labelLarge?.copyWith(color: game.textMuted),
                ),
                for (final task in tasks.where((task) => task.moduleId == moduleId))
                  ListTile(
                    contentPadding: EdgeInsets.zero,
                    leading: Icon(
                      solved.contains(task.id)
                          ? Icons.check_circle_rounded
                          : Icons.code_rounded,
                      color: solved.contains(task.id)
                          ? game.success
                          : Theme.of(context).colorScheme.primary,
                    ),
                    title: Text(task.title, style: textTheme.bodyLarge),
                    subtitle: Text(
                      '${'★' * task.difficulty}${'☆' * (3 - task.difficulty).clamp(0, 3)}',
                      style: textTheme.labelMedium?.copyWith(color: game.rewardIcon),
                    ),
                    trailing: Icon(Icons.chevron_right_rounded, color: game.textMuted),
                    onTap: () => context.push(Routes.practiceTask(task.id)),
                  ),
              ],
          ],
        );
      },
    );
  }
}
