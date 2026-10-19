import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/routes.dart';
import '../../../shared/widgets/code_copy.dart';
import '../../playground/presentation/code_editor.dart';
import '../../world/presentation/world_controller.dart';
import '../../world/presentation/world_ui.dart';
import '../domain/calculator_project.dart';
import '../domain/project_service.dart';
import 'project_providers.dart';
import '../../world/domain/story_journey.dart';
import '../../world/presentation/story_guide.dart';

class ProjectScreen extends ConsumerStatefulWidget {
  const ProjectScreen({super.key});
  @override
  ConsumerState<ProjectScreen> createState() => _ProjectScreenState();
}

class _ProjectScreenState extends ConsumerState<ProjectScreen> {
  final _code = TextEditingController();
  Timer? _debounce;
  bool _loaded = false;
  bool _busy = false;
  String? _saveError;
  ProjectCheck? _report;
  late ProjectService _service;

  @override
  void initState() {
    super.initState();
    _service = ref.read(projectServiceProvider);
  }

  @override
  void dispose() {
    _debounce?.cancel();
    if (_loaded)
      unawaited(_service.saveDraft(_code.text).catchError((Object _) {}));
    _code.dispose();
    super.dispose();
  }

  Future<bool> _save() async {
    _debounce?.cancel();
    try {
      await _service.saveDraft(_code.text);
      if (mounted) setState(() => _saveError = null);
      return true;
    } catch (_) {
      if (mounted)
        setState(
          () =>
              _saveError = 'Не удалось сохранить черновик. Повтори сохранение.',
        );
      return false;
    }
  }

  Future<void> _check() async {
    FocusScope.of(context).unfocus();
    setState(() {
      _busy = true;
      _report = null;
    });
    try {
      if (!await _save()) return;
      final report = await _service.check(_code.text);
      if (mounted) setState(() => _report = report);
    } catch (_) {
      if (mounted)
        setState(
          () => _report = const ProjectCheck(
            'Проверка не завершена. Код сохранён; повтори попытку.',
          ),
        );
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => WorldPage(
    title: 'Проект · калькулятор Python',
    subtitle: 'Свой код, запуск и автоматические проверки',
    child: ref
        .watch(calculatorProjectProvider)
        .when(
          skipLoadingOnReload: true,
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (e, s) => Center(
            child: TextButton(
              onPressed: () => ref.invalidate(calculatorProjectProvider),
              child: const Text('Повторить загрузку проекта'),
            ),
          ),
          data: (project) {
            if (!_loaded) {
              _code.text = project.draft;
              _loaded = true;
            }
            final world = ref.watch(worldControllerProvider).value;
            if (world == null)
              return const Center(child: CircularProgressIndicator());
            if (world.expeditionProgress < 5)
              return Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    const Text(
                      'Код проекта откроется после пяти этапов экспедиции.',
                      style: TextStyle(color: WorldPalette.text),
                    ),
                    const SizedBox(height: 16),
                    WorldButton(
                      label: 'Продолжить экспедицию',
                      onPressed: () => context.push(Routes.worldExpedition),
                    ),
                  ],
                ),
              );
            return CodeCopyScope(
              wrongAnswers: project.wrongAnswers,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  StoryGuide(journey: StoryJourney(world, verifiedComponents: project.step), showAction: false),
                  const SizedBox(height: 12),
                  Text(
                    'Проверено ${project.step}/4 компонентов',
                    style: const TextStyle(
                      color: WorldPalette.cyan,
                      fontSize: 18,
                    ),
                  ),
                  const SizedBox(height: 8),
                  LinearProgressIndicator(value: project.step / 4),
                  const SizedBox(height: 12),
                  WorldPanel(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          project.complete
                              ? 'Калькулятор готов'
                              : CalculatorProject.titles[project.step],
                          style: const TextStyle(
                            color: WorldPalette.text,
                            fontSize: 19,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          CalculatorProject.instructions[project.step.clamp(
                            0,
                            3,
                          )],
                          style: const TextStyle(color: WorldPalette.text),
                        ),
                        const SizedBox(height: 8),
                        const Text(
                          'Новые компоненты: 45 XP и 25 монет до бонусов; после ошибки — 22 XP. Повторная проверка готового этапа не удваивает награду. На следующих шагах проверяются и предыдущие функции.',
                          style: TextStyle(color: WorldPalette.muted),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 12),
                  IgnorePointer(
                    ignoring: _busy,
                    child: CodeEditor(
                      controller: _code,
                      minLines: 10,
                      onChanged: (_) {
                        if (_report != null) setState(() => _report = null);
                        _debounce?.cancel();
                        _debounce = Timer(
                          const Duration(milliseconds: 750),
                          () => unawaited(_save().then<void>((_) {})),
                        );
                      },
                    ),
                  ),
                  const SizedBox(height: 8),
                  if (_saveError != null)
                    Text(
                      _saveError!,
                      style: const TextStyle(color: WorldPalette.red),
                    ),
                  TextButton(
                    onPressed: _busy ? null : _save,
                    child: const Text('Сохранить черновик'),
                  ),
                  WorldButton(
                    label: _busy ? 'Проверка Python…' : 'Проверить программу',
                    onPressed: _busy ? null : _check,
                  ),
                  if (_report != null) ...[
                    const SizedBox(height: 12),
                    WorldPanel(
                      glow: _report!.passed
                          ? WorldPalette.green
                          : WorldPalette.red,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            _report!.message,
                            style: const TextStyle(color: WorldPalette.text),
                          ),
                          for (final line in _report!.lines)
                            Padding(
                              padding: const EdgeInsets.only(top: 6),
                              child: Text(
                                line,
                                style: const TextStyle(
                                  color: WorldPalette.muted,
                                ),
                              ),
                            ),
                        ],
                      ),
                    ),
                  ],
                  if (project.complete) ...[
                    const SizedBox(height: 12),
                    WorldButton(
                      label: 'Скопировать проверенную программу',
                      secondary: true,
                      onPressed: () async => Clipboard.setData(
                        ClipboardData(text: project.verifiedCode),
                      ),
                    ),
                    if (project.draft != project.verifiedCode)
                      const Padding(
                        padding: EdgeInsets.symmetric(vertical: 8),
                        child: Text(
                          'Черновик изменён. Кнопка копирования отдаёт последнюю проверенную версию.',
                          style: TextStyle(color: WorldPalette.muted),
                        ),
                      ),
                    const SizedBox(height: 8),
                    WorldButton(
                      label: 'К боссу',
                      onPressed: () => context.push(Routes.worldBoss),
                    ),
                  ],
                  const SizedBox(height: 24),
                ],
              ),
            );
          },
        ),
  );
}
