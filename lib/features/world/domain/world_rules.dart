import 'world_challenge.dart';
import 'world_state.dart';
import 'world_hearts.dart';
import 'skill_repair.dart';

class WorldSubmission {
  const WorldSubmission(this.state, this.message, {this.correct = false});
  final WorldState state;
  final String message;
  final bool correct;
}

abstract final class WorldRules {
  static String skillKey(WorldMode mode, String category, int cursor) => switch (mode) {
    WorldMode.training => 'dna:$category:$cursor',
    WorldMode.expedition || WorldMode.boss => 'world:${mode.name}:$cursor',
    _ => 'world:repeat:$category',
  };
  static WorldState recordError(WorldState s, {required String skillId,
    required String title, required String category, required String sourceCode}) {
    final repair = s.repairs[skillId] ?? SkillRepair(skillId: skillId, title: title, category: category);
    return s.copyWith(
      mistakes: {...s.mistakes, category: (s.mistakes[category] ?? 0) + 1},
      repairs: {...s.repairs, skillId: repair.mistake(sourceCode)},
    );
  }
  static String buildingEffect(String id, int level) => switch (id) {
    'office' => '+${level - 1} монет за верное решение',
    'python' => '+${2 * (level - 1)} XP за верное решение',
    'rnd' => '+${3 * (level - 1)} XP за решение без ошибок',
    'servers' => '${3 + level - 1} общих жизней',
    'team' => '$level вклад за верное решение команды',
    _ => '',
  };

  static WorldState active(WorldState s, DateTime now) {
    final today = DateTime(now.year, now.month, now.day);
    final day = today.toIso8601String().substring(0, 10);
    if (s.lastActiveDay == day) return s;
    final yesterday = today
        .subtract(const Duration(days: 1))
        .toIso8601String()
        .substring(0, 10);
    return s.copyWith(
      lastActiveDay: day,
      streak: s.lastActiveDay == yesterday ? s.streak + 1 : 1,
    );
  }

  static WorldState reward(
    WorldState s,
    int xp,
    int coins, {
    bool clean = true,
  }) {
    final bonus =
        2 * ((s.cityLevels['python'] ?? 1) - 1) +
        (clean ? 3 * ((s.cityLevels['rnd'] ?? 1) - 1) : 0);
    return s.copyWith(
      worldXp: s.worldXp + xp + bonus,
      seasonXp: s.seasonXp + xp + bonus,
      coins: s.coins + coins + (s.cityLevels['office'] ?? 1) - 1,
    );
  }

  static WorldSubmission submit(
    WorldState s,
    WorldMode mode,
    String challengeId,
    String answer,
    DateTime now, {
    String category = 'Условия',
    int? elapsedSeconds,
  }) {
    s = WorldHearts.regenerate(s, now);
    if (mode == WorldMode.project) return WorldSubmission(s,
        'Проект проверяется запуском Python. Открой мастерскую калькулятора.');
    final locked = WorldChallenges.locked(s, mode);
    if (locked != null) return WorldSubmission(s, locked);
    if (WorldChallenges.finished(s, mode, category: category))
      return WorldSubmission(s, 'Этот этап уже завершён.');
    if (mode == WorldMode.infinite && s.hearts <= 0) {
      return WorldSubmission(
        s,
        'Жизни закончились. Восстанови их перед новой попыткой.',
      );
    }
    if (mode == WorldMode.training && !s.mistakes.containsKey(category)) {
      return WorldSubmission(s, 'Неизвестная тема.');
    }
    final task = WorldChallenges.at(s, mode, category: category);
    if (task.id != challengeId)
      return WorldSubmission(
        s,
        'Задание уже изменилось. Открой актуальный этап.',
      );
    if (answer.trim().isEmpty)
      return WorldSubmission(s, 'Сначала введи ответ или выбери вариант.');
    if (mode == WorldMode.ghost &&
        (elapsedSeconds == null || elapsedSeconds < 1)) {
      return WorldSubmission(s, 'Запусти попытку заново: время не измерено.');
    }
    if (!task.accepts(answer)) {
      var next = recordError(s, skillId: skillKey(mode, task.category,
          WorldChallenges.cursor(s, mode, category)), title: task.title,
          category: task.category, sourceCode: task.code.replaceAll('___', task.answer)).copyWith(
        failures: {...s.failures, task.id: (s.failures[task.id] ?? 0) + 1},
      );
      var effect =
          'Этап не пройден, награда не начислена. Ошибка добавлена в Mistake DNA.';
      if (mode == WorldMode.infinite) {
        next = WorldHearts.lose(next, now).copyWith(infiniteCurrent: 0);
        effect = '−1 жизнь; серия сброшена. Рекорд сохранён. Награды нет.';
      }
      return WorldSubmission(next, 'Неверно. ${task.explanation}\n$effect');
    }
    final key = WorldChallenges.key(mode, category);
    final count = (s.solved[key] ?? 0) + 1;
    var next = s.copyWith(solved: {...s.solved, key: count});
    var xp = 30;
    var coins = 12;
    String effect;
    switch (mode) {
      case WorldMode.expedition:
        next = next.copyWith(expeditionStep: s.expeditionStep + 1);
        xp = 35;
        coins = 20;
        effect = next.expeditionStep == 5
            ? 'API восстановлен. Открыты сундук и проект калькулятора.'
            : 'Восстановление API: ${next.expeditionStep}/5. Доступен следующий этап.';
      case WorldMode.project:
        final id = WorldState.projectIds[s.completedProjectSteps];
        next = next.copyWith(projectSteps: {...s.projectSteps, id: true});
        xp = 45;
        coins = 25;
        effect = next.projectUnlocked
            ? 'Калькулятор готов. Открыта битва с Bug Lord.'
            : 'Проект: ${next.completedProjectSteps}/4. Открыт следующий компонент.';
      case WorldMode.boss:
        final hp = (s.bossHp - 25).clamp(0, 100);
        next = next.copyWith(
          bossHp: hp,
          bossTask: s.bossTask + 1,
          bossCleared: hp == 0,
        );
        xp = hp == 0 ? 180 : 45;
        coins = hp == 0 ? 120 : 20;
        effect = hp == 0
            ? 'Bug Lord побеждён! История восстановления завершена.'
            : 'Удар −25 HP. У босса осталось $hp HP. Следующая уязвимость открыта.';
      case WorldMode.infinite:
        final run = s.infiniteCurrent + 1;
        next = next.copyWith(
          infiniteCurrent: run,
          infiniteRecord: run > s.infiniteRecord ? run : s.infiniteRecord,
        );
        xp = 20 + run;
        coins = 5;
        effect =
            'Серия $run; рекорд ${next.infiniteRecord}. Следующая задача открыта; сложность растёт каждые 5 решений.';
      case WorldMode.training:
        effect =
            'Учебный пример пройден. Незакреплённых ошибок «$category»: ${next.mistakes[category] ?? 0}. Подтверди исправление отдельным новым примером в DNA.';
      case WorldMode.guild:
        final contribution = (s.cityLevels['team'] ?? 1).clamp(
          0,
          160 - s.guildTotal,
        );
        next = next.copyWith(
          guildContribution: s.guildContribution + contribution,
          guildTotal: (s.guildTotal + contribution).clamp(0, 160),
        );
        if (next.guildTotal >= 160) {
          xp += 150;
          coins += 100;
        }
        effect =
            '+${next.guildTotal - s.guildTotal} к проекту команды. Выполнено ${next.guildTotal}/160.'
            '${next.guildTotal >= 160 ? ' Проект готов! Бонус: 150 XP и 100 монет.' : ''}';
      case WorldMode.rival:
        next = next.copyWith(rivalWins: s.rivalWins + 1);
        xp = 55;
        coins = 25;
        effect =
            'Учебный соперник побеждён. Побед: ${next.rivalWins}. Следующее испытание открыто.';
      case WorldMode.ghost:
        final seconds = elapsedSeconds!;
        final improved =
            s.ghostBestSeconds == 0 || seconds < s.ghostBestSeconds;
        next = next.copyWith(
          ghostBestSeconds: improved ? seconds : s.ghostBestSeconds,
        );
        effect =
            'Решение за $seconds сек. ${improved ? 'Новый личный рекорд!' : 'Рекорд: ${s.ghostBestSeconds} сек.'}';
    }
    if ((s.failures[task.id] ?? 0) > 0) xp = xp ~/ 2;
    final before = next;
    next = active(
      reward(next, xp, coins, clean: (s.failures[task.id] ?? 0) == 0),
      now,
    );
    return WorldSubmission(
      next,
      'Верно. ${task.explanation}\n$effect\n+${next.worldXp - before.worldXp} XP · +${next.coins - before.coins} монет. '
      'Монеты улучшают город; XP открывает уровни зданий и награды сезона.',
      correct: true,
    );
  }

  static WorldState upgrade(WorldState s, String id) {
    if (!s.cityLevels.containsKey(id)) return s;
    final level = s.cityLevels[id]!;
    final cost = 80 + level * 40;
    if (level >= s.buildingCap || s.coins < cost) return s;
    return s.copyWith(
      coins: s.coins - cost,
      cityLevels: {...s.cityLevels, id: level + 1},
      hearts: id == 'servers' ? s.hearts + 1 : s.hearts,
    );
  }

  static WorldState claimSeason(WorldState s) {
    if (s.seasonXp < 1000) return s;
    final level = s.seasonLevel + 1;
    return s.copyWith(
      seasonLevel: level,
      seasonXp: s.seasonXp - 1000,
      coins: s.coins + 60,
      gems: s.gems + (level % 3 == 0 ? 1 : 0),
    );
  }
}
