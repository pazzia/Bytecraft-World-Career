import 'dart:convert';

import '../../../core/storage/game_save_store.dart';
import '../../../core/storage/json_document_store.dart';
import '../../../core/time/clock.dart';
import '../../../core/utils/id_generator.dart';
import '../../courses/data/content_sources.dart';
import '../../playground/domain/python_runner.dart';
import '../../world/data/world_repository.dart';
import '../../world/domain/world_rules.dart';
import '../../world/domain/world_state.dart';
import 'calculator_project.dart';

class ProjectService {
  ProjectService(
    this.documents,
    this.save,
    this.world,
    this.runner,
    this.loadAsset,
    this.clock,
  );
  static const key = 'player.project.calculator';
  final JsonDocumentStore documents;
  final GameSaveStore save;
  final WorldRepository world;
  final PythonRunner runner;
  final TextAssetLoader loadAsset;
  final Clock clock;

  Future<CalculatorProject> load() async {
    final json = await documents.read(key);
    if (json == null && await documents.raw.read(key) != null)
      throw StateError('Corrupt project');
    if (json != null &&
        (json['schemaVersion'] != 1 ||
            json['checkerRevision'] != CalculatorProject.revision)) {
      throw StateError('Unsupported project version');
    }
    return CalculatorProject.fromJson(json);
  }

  Future<void> saveDraft(String code) => save.transaction(() async {
    if (code.length > 50000) throw StateError('Код превышает 50 000 символов');
    final current = await load();
    await documents.write(key, {
      ...current.toJson(),
      'draft': code,
    }, schemaVersion: 1);
  });

  Future<ProjectCheck> check(String code) async {
    if (code.trim().isEmpty)
      return const ProjectCheck('Сначала напиши программу.');
    final before = await save.transaction(() async {
      final state = await world.load();
      if (state.expeditionProgress < 5) return null;
      await saveDraft(code);
      return load();
    });
    if (before == null)
      return const ProjectCheck('Сначала заверши пять этапов экспедиции.');
    final stage = before.step.clamp(0, 3);
    final nonce = RandomIdGenerator().newId();
    final source = await loadAsset('assets/projects/calculator_check.py');
    final result = await runner.run(
      source,
      stdin: jsonEncode({'code': code, 'step': stage, 'nonce': nonce}),
      timeout: const Duration(seconds: 5),
      echoInputPrompt: false,
    );
    if (result.status == RunStatus.unavailable) {
      return const ProjectCheck(
        'Python пока недоступен. Черновик сохранён; повтори проверку позже.',
      );
    }
    var passed = false;
    var lines = <String>[];
    if (result.status == RunStatus.timeout) {
      lines = ['Программа не завершилась за 5 секунд.'];
    } else if (!result.isOk) {
      return const ProjectCheck(
        'Не удалось завершить проверку Python. Черновик сохранён. Повтори попытку; награда не снижена.',
      );
    } else {
      try {
        final report = jsonDecode(result.stdout.trim()) as Map<String, dynamic>;
        final checks = List<Map<String, dynamic>>.from(
          report['checks'] as List,
        );
        final loadError =
            checks.length == 1 &&
            checks.single['name'] == 'Загрузка программы' &&
            checks.single['passed'] == false;
        final expected = CalculatorProject.checkNames
            .take(CalculatorProject.checkCounts[stage])
            .toList();
        final fullReport =
            checks.length == expected.length &&
            List.generate(
              checks.length,
              (i) => checks[i]['name'] == expected[i],
            ).every((match) => match);
        if (report['nonce'] != nonce ||
            !(loadError || fullReport) ||
            !checks.every(
              (check) =>
                  check['passed'] is bool &&
                  (check['detail'] == null || check['detail'] is String),
            )) {
          throw const FormatException('Invalid checker report');
        }
        passed = !loadError && checks.every((check) => check['passed'] == true);
        lines = checks
            .map(
              (check) =>
                  '${check['passed'] == true ? '✓' : '×'} ${check['name']}: ${check['detail'] ?? (check['passed'] == true ? 'пройдено' : 'проверка не пройдена')}',
            )
            .toList();
      } catch (_) {
        return const ProjectCheck(
          'Ответ проверяющего скрипта повреждён или неполон. Черновик сохранён. Повтори проверку; награда не снижена.',
        );
      }
    }
    return save.transaction(() async {
      final current = await load();
      if (current.draft != code || current.step != before.step) {
        return const ProjectCheck(
          'Код или этап изменился. Открой актуальный проект и проверь снова.',
        );
      }
      if (!passed) {
        await documents.write(key, {
          ...current.toJson(),
          'failures': {
            ...current.failures,
            '$stage': (current.failures['$stage'] ?? 0) + 1,
          },
        }, schemaVersion: 1);
        return ProjectCheck(
          'Проверки не пройдены. Этап и награда сохранены без изменений.',
          lines: lines,
        );
      }
      final state = await world.load();
      if (state.expeditionProgress < 5)
        return const ProjectCheck('Экспедиция была сброшена. Начни её заново.');
      final nextStep = current.complete ? 4 : current.step + 1;
      var next = state;
      if (!current.complete) {
        final component = WorldState.projectIds[stage];
        if (state.projectSteps[component] != true) {
          next = WorldRules.reward(
            state,
            (current.failures['$stage'] ?? 0) == 0 ? 45 : 22,
            25,
            clean: (current.failures['$stage'] ?? 0) == 0,
          );
        }
        next = WorldRules.active(
          next.copyWith(
            projectSteps: {...next.projectSteps, component: true},
            solved: {
              ...next.solved,
              'project': nextStep > (next.solved['project'] ?? 0)
                  ? nextStep
                  : next.solved['project']!,
            },
            hasVerifiedProject: nextStep == 4,
          ),
          clock.now(),
        );
      }
      if (nextStep == 4)
        next = next.copyWith(
          hasVerifiedProject: true,
          projectSteps: {for (final id in WorldState.projectIds) id: true},
        );
      final award = next.worldXp == state.worldXp && next.coins == state.coins
          ? 'Награда за этот компонент уже получена.'
          : '+${next.worldXp - state.worldXp} XP · +${next.coins - state.coins} монет.';
      await world.write(next);
      await documents.write(key, {
        ...current.toJson(),
        'step': nextStep,
        if (nextStep == 4) 'verifiedCode': code,
        'checkedAt': clock.now().toIso8601String(),
      }, schemaVersion: 1);
      return ProjectCheck(
        nextStep == 4
            ? 'Калькулятор прошёл 14 проверок. Рабочий код сохранён; босс открыт. $award'
            : 'Этап $nextStep/4 проверен запуском Python. $award',
        passed: true,
        lines: lines,
      );
    });
  }
}
