import 'package:shared_preferences/shared_preferences.dart';
import '../models/progress.dart';

class ProgressStore {
  static const _completedKey = 'completed_levels';
  static const _hardcoreCompletedKey = 'hardcore_completed_levels';
  static const _hardcoreModeKey = 'hardcore_mode';
  static const _xpKey = 'total_xp';
  static const _livesKey = 'lives';
  static const _streakKey = 'streak';
  static const _lastActiveKey = 'last_active_day';
  static const _onboardingKey = 'onboarding_done';
  static const _deadlinePrefix = 'hardcore_deadline_';

  Future<AppProgress> load() async {
    final prefs = await SharedPreferences.getInstance();
    final deadlines = <String, String>{};
    for (final key in prefs.getKeys()) {
      if (key.startsWith(_deadlinePrefix)) {
        final value = prefs.getString(key);
        if (value != null) deadlines[key.substring(_deadlinePrefix.length)] = value;
      }
    }
    return AppProgress(
      completedLevelIds: prefs.getStringList(_completedKey) ?? const <String>[],
      hardcoreCompletedLevelIds: prefs.getStringList(_hardcoreCompletedKey) ?? const <String>[],
      hardcoreDeadlines: deadlines,
      hardcoreMode: prefs.getBool(_hardcoreModeKey) ?? false,
      totalXp: prefs.getInt(_xpKey) ?? 0,
      lives: prefs.getInt(_livesKey) ?? 5,
      streak: prefs.getInt(_streakKey) ?? 0,
      lastActiveDay: prefs.getString(_lastActiveKey),
      onboardingDone: prefs.getBool(_onboardingKey) ?? false,
    );
  }

  Future<void> save(AppProgress progress) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList(_completedKey, progress.completedLevelIds);
    await prefs.setStringList(_hardcoreCompletedKey, progress.hardcoreCompletedLevelIds);
    await prefs.setBool(_hardcoreModeKey, progress.hardcoreMode);
    await prefs.setInt(_xpKey, progress.totalXp);
    await prefs.setInt(_livesKey, progress.lives);
    await prefs.setInt(_streakKey, progress.streak);
    if (progress.lastActiveDay != null) await prefs.setString(_lastActiveKey, progress.lastActiveDay!);
    await prefs.setBool(_onboardingKey, progress.onboardingDone);

    for (final key in prefs.getKeys().where((k) => k.startsWith(_deadlinePrefix)).toList()) {
      await prefs.remove(key);
    }
    for (final entry in progress.hardcoreDeadlines.entries) {
      await prefs.setString('$_deadlinePrefix${entry.key}', entry.value);
    }
  }
}
