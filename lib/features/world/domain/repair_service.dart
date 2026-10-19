import 'dart:convert';

import '../../../core/storage/game_save_store.dart';
import '../../../core/time/clock.dart';
import '../../courses/data/content_sources.dart';
import '../data/world_repository.dart';
import 'repair_catalog.dart';
import 'world_rules.dart';

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
  Future<RepairCatalog> _load() async => RepairCatalog.fromJson(
    jsonDecode(await loadAsset('assets/projects/repair_catalog.json'))
        as Map<String, dynamic>,
  );

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
          'Запись ошибки уже изменилась. Открой актуальную проверку.',
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
            ? 'Исправление подтверждено новым самостоятельным решением. Доказательство сохранено. +${next.worldXp - current.worldXp} XP · +${next.coins - current.coins} монет.'
            : 'Ответ не совпал. ${example.question(repair).explanation}\nЭтот пример теперь разобран и не может подтвердить исправление. Следующая проверка будет другой.',
        passed: passed,
      );
    });
  }
}
