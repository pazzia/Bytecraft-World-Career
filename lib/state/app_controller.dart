import 'package:flutter/foundation.dart';

import '../core/level_engine.dart';
import '../models/level.dart';
import '../models/progress.dart';
import '../services/progress_store.dart';

class AppController extends ChangeNotifier {
  AppController({ProgressStore? store, LevelEngine? engine})
      : _store = store ?? ProgressStore(),
        _engine = engine ?? const LevelEngine();

  final ProgressStore _store;
  final LevelEngine _engine;

  AppProgress progress = const AppProgress();
  bool initialized = false;

  Future<void> init() async {
    progress = await _store.load();
    initialized = true;
    notifyListeners();
  }

  Future<void> finishOnboarding() async {
    progress = progress.copyWith(onboardingDone: true);
    await _store.save(progress);
    notifyListeners();
  }

  Future<void> setHardcoreMode(bool enabled, List<Level> levels) async {
    progress = progress.copyWith(hardcoreMode: enabled);
    if (enabled) await refreshHardcoreExpirations(levels, notify: false);
    await _store.save(progress);
    notifyListeners();
  }

  Duration hardcoreDurationFor(String module) => switch (module) {
        'Variables' => const Duration(minutes: 5),
        'Types' => const Duration(minutes: 6),
        'Operators' => const Duration(minutes: 7),
        'Conditions' => const Duration(minutes: 8),
        'Loops' => const Duration(minutes: 10),
        _ => const Duration(minutes: 10),
      };

  int hardcoreTimeBonusFor(String module, Duration remaining) {
    final max = hardcoreDurationFor(module).inSeconds;
    if (max <= 0 || remaining.inSeconds <= 0) return 0;
    final ratio = (remaining.inSeconds / max).clamp(0.0, 1.0);
    return (100 * ratio).round();
  }

  bool isUnlocked(List<Level> levels, int index) {
    if (progress.hardcoreMode) return isHardcoreUnlocked(levels, index);
    if (index == 0) return true;
    return progress.completedLevelIds.contains(levels[index - 1].id);
  }

  bool isHardcoreUnlocked(List<Level> levels, int index) {
    final level = levels[index];
    final moduleLevels = levels.where((item) => item.module == level.module).toList();
    final moduleIndex = moduleLevels.indexWhere((item) => item.id == level.id);
    if (moduleIndex == 0) return true;
    return progress.hardcoreCompletedLevelIds.contains(moduleLevels[moduleIndex - 1].id);
  }

  bool isCompleted(Level level) => progress.hardcoreMode
      ? progress.hardcoreCompletedLevelIds.contains(level.id)
      : progress.completedLevelIds.contains(level.id);

  DateTime? hardcoreDeadlineFor(String module) {
    final raw = progress.hardcoreDeadlines[module];
    return raw == null ? null : DateTime.tryParse(raw);
  }

  Duration? hardcoreRemainingFor(String module) {
    final deadline = hardcoreDeadlineFor(module);
    if (deadline == null) return null;
    final remaining = deadline.difference(DateTime.now());
    return remaining.isNegative ? Duration.zero : remaining;
  }

  Future<void> refreshHardcoreExpirations(List<Level> levels, {bool notify = true}) async {
    var changed = false;
    final completed = <String>[...progress.hardcoreCompletedLevelIds];
    final deadlines = <String, String>{...progress.hardcoreDeadlines};

    for (final entry in progress.hardcoreDeadlines.entries.toList()) {
      final deadline = DateTime.tryParse(entry.value);
      if (deadline == null || DateTime.now().isBefore(deadline)) continue;
      final moduleLevels = levels.where((level) => level.module == entry.key).toList();
      final allDone = moduleLevels.isNotEmpty && moduleLevels.every((level) => completed.contains(level.id));
      if (!allDone) {
        final ids = moduleLevels.map((level) => level.id).toSet();
        completed.removeWhere(ids.contains);
      }
      deadlines.remove(entry.key);
      changed = true;
    }

    if (changed) {
      progress = progress.copyWith(
        hardcoreCompletedLevelIds: completed,
        hardcoreDeadlines: deadlines,
      );
      await _store.save(progress);
      if (notify) notifyListeners();
    }
  }

  Future<LevelResult> submit({
    required Level level,
    required String answer,
    required int mistakes,
    List<Level> allLevels = const <Level>[],
  }) async {
    if (progress.hardcoreMode && allLevels.isNotEmpty) {
      await refreshHardcoreExpirations(allLevels, notify: false);
    }

    final result = _engine.evaluate(level, answer, mistakes);
    if (result.isCorrect) {
      if (progress.hardcoreMode) {
        await _completeHardcoreLevel(level, allLevels);
      } else {
        final alreadyCompleted = progress.completedLevelIds.contains(level.id);
        final completed = <String>[...progress.completedLevelIds];
        if (!alreadyCompleted) completed.add(level.id);
        progress = progress.copyWith(
          completedLevelIds: completed,
          totalXp: progress.totalXp + (alreadyCompleted ? 0 : result.xpAwarded),
          streak: _calculateStreak(progress.lastActiveDay, progress.streak),
          lastActiveDay: _today(),
        );
      }
    } else {
      progress = progress.copyWith(lives: progress.lives > 0 ? progress.lives - 1 : 0);
    }
    await _store.save(progress);
    notifyListeners();
    return result;
  }

  Future<void> _completeHardcoreLevel(Level level, List<Level> allLevels) async {
    final completed = <String>[...progress.hardcoreCompletedLevelIds];
    final deadlines = <String, String>{...progress.hardcoreDeadlines};
    final alreadyCompleted = completed.contains(level.id);
    if (!alreadyCompleted) completed.add(level.id);

    final moduleLevels = allLevels.where((item) => item.module == level.module).toList();
    final moduleCompleted = moduleLevels.isNotEmpty && moduleLevels.every((item) => completed.contains(item.id));

    var timeBonus = 0;
    if (moduleCompleted) {
      final remaining = hardcoreRemainingFor(level.module);
      if (remaining != null) timeBonus = hardcoreTimeBonusFor(level.module, remaining);
      deadlines.remove(level.module);
    } else if (!deadlines.containsKey(level.module)) {
      deadlines[level.module] = DateTime.now().add(hardcoreDurationFor(level.module)).toIso8601String();
    }

    progress = progress.copyWith(
      hardcoreCompletedLevelIds: completed,
      hardcoreDeadlines: deadlines,
      totalXp: progress.totalXp + (alreadyCompleted ? 0 : resultXpBonus(level)) + timeBonus,
      streak: _calculateStreak(progress.lastActiveDay, progress.streak),
      lastActiveDay: _today(),
    );
  }

  int resultXpBonus(Level level) => level.xp * 2;

  int _calculateStreak(String? lastDay, int current) {
    final today = DateTime.now();
    final normalizedToday = DateTime(today.year, today.month, today.day);
    if (lastDay == null) return 1;
    final parsed = DateTime.tryParse(lastDay);
    if (parsed == null) return 1;
    final last = DateTime(parsed.year, parsed.month, parsed.day);
    final diff = normalizedToday.difference(last).inDays;
    if (diff == 0) return current == 0 ? 1 : current;
    if (diff == 1) return current + 1;
    return 1;
  }

  String _today() {
    final now = DateTime.now();
    return DateTime(now.year, now.month, now.day).toIso8601String();
  }
}
