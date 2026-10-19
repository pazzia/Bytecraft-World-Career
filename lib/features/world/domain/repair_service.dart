import 'dart:convert';

import '../../../core/storage/game_save_store.dart';
import '../../../core/time/clock.dart';
import '../../courses/data/content_sources.dart';
import '../data/world_repository.dart';
import 'repair_catalog.dart';
import 'world_rules.dart';
import 'skill_repair.dart';

class RepairResult {
  const RepairResult(this.message, {this.passed = false});
  final String message;
  final bool passed;
}

class RepairService {
  RepairService(this.save, this.world, this.loadAsset, this.clock);
  final GameSaveStore save;
  final WorldRepository world;
  final TextAssetLoader loadAsset;
  final Clock clock;
  Future<RepairCatalog>? _catalog;
  Future<RepairCatalog> catalog() =>
      _catalog ??= _load().catchError((Object error) {
        _catalog = null;
        throw error;
      });
  Future<RepairCatalog> _load() async {
    final bank = RepairCatalog.fromJson(
      jsonDecode(await loadAsset('assets/projects/repair_catalog.json'))
          as Map<String, dynamic>,
    );
    await save.transaction(() async {
      final current = await world.load();
      if (current.repairMigrationVersion >= 1) return;
      final repairs = {...current.repairs};
      for (final entry in current.failures.entries) {
        final origin = bank.origins[entry.key];
        if (origin == null || entry.value <= 0) continue;
        final skill = origin['skillId'] as String;
        final definition = bank.skills[skill];
        if (definition == null || current.repairs.containsKey(skill)) continue;
        final previous = repairs[skill];
        final sources = {
          for (final source in origin['sources'] as List)
            SkillRepair.signature(
              source['code'] as String,
              source['stdin'] as String? ?? '',
            ),
        };
        repairs[skill] = SkillRepair(
          skillId: skill,
          title: definition['title'] as String,
          category: definition['category'] as String,
          generation: 1,
          openErrors: (previous?.openErrors ?? 0) + entry.value,
          sources: {...?previous?.sources, ...sources}.toList(),
        );
      }
      final counts = {...current.mistakes};
      for (final category in {
        ...counts.keys,
        ...repairs.values.map((r) => r.category),
      }) {
        final imported = repairs.values
            .where((r) => r.category == category)
            .fold<int>(0, (sum, r) => sum + r.openErrors);
        if (imported > (counts[category] ?? 0)) counts[category] = imported;
      }
      await world.write(
        current.copyWith(
          repairMigrationVersion: 1,
          repairs: repairs,
          mistakes: counts,
        ),
      );
    });
    return bank;
  }

  /// A first independent check is available without deliberately making errors.
  /// Existing proofs cannot be farmed by requesting the same check again.
  Future<void> beginAssessment(String skillId) async {
    final bank = await catalog();
    final definition = bank.skills[skillId];
    if (definition == null) throw StateError('Нет проверки этой подтемы');
    await save.transaction(() async {
      final current = await world.load();
      final previous = current.repairs[skillId];
      if (previous != null && (previous.pending || previous.proofs.isNotEmpty))
        return;
      final next = SkillRepair(
        skillId: skillId,
        title: definition['title'] as String,
        category: definition['category'] as String,
        assessmentRequested: true,
        generation: (previous?.generation ?? 0) + 1,
        seen: previous?.seen ?? const [],
        sources: previous?.sources ?? const [],
        attempts: previous?.attempts ?? 0,
      );
      if (bank.next(next) == null) throw StateError('Нужны новые примеры');
      await world.write(
        current.copyWith(repairs: {...current.repairs, skillId: next}),
      );
    });
  }

  Future<RepairResult> submit(
    String skillId,
    int generation,
    String exampleId,
    String answer,
  ) async {
    if (answer.trim().isEmpty)
      return const RepairResult('Сначала введи ответ.');
    final bank = await catalog();
    return save.transaction(() async {
      final current = await world.load();
      final repair = current.repairs[skillId];
      if (repair == null ||
          !repair.pending ||
          repair.generation != generation) {
        return const RepairResult(
          'Данные проверки уже изменились. Открой актуальную проверку.',
        );
      }
      final example = bank.next(repair);
      if (example == null || example.id != exampleId)
        return const RepairResult(
          'Этот пример уже разобран или недоступен. Нужен другой.',
        );
      final passed = example.question(repair).accepts(answer);
      final nextRepair = repair.review(
        example.id,
        passed: passed,
        code: example.code,
        stdin: example.stdin,
        now: clock.now(),
      );
      var next = current.copyWith(
        repairs: {...current.repairs, skillId: nextRepair},
      );
      if (passed) {
        next = next.copyWith(
          mistakes: {
            ...next.mistakes,
            repair.category:
                ((next.mistakes[repair.category] ?? 0) - repair.openErrors)
                    .clamp(0, 1 << 30),
          },
          solved: {
            ...next.solved,
            'repair:$skillId': (next.solved['repair:$skillId'] ?? 0) + 1,
          },
        );
        next = WorldRules.active(WorldRules.reward(next, 30, 12), clock.now());
      }
      await world.write(next);
      return RepairResult(
        passed
            ? 'Подтема подтверждена новым самостоятельным решением. Доказательство сохранено. +${next.worldXp - current.worldXp} XP · +${next.coins - current.coins} монет.'
            : 'Ответ не совпал. ${example.question(repair).explanation}\nЭтот пример теперь разобран и не может дать самостоятельное подтверждение. Следующая проверка будет другой.',
        passed: passed,
      );
    });
  }
}
