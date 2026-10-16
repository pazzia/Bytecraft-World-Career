class AppProgress {
  const AppProgress({
    this.completedLevelIds = const <String>[],
    this.hardcoreCompletedLevelIds = const <String>[],
    this.hardcoreDeadlines = const <String, String>{},
    this.hardcoreMode = false,
    this.totalXp = 0,
    this.lives = 5,
    this.streak = 0,
    this.lastActiveDay,
    this.onboardingDone = false,
  });

  final List<String> completedLevelIds;
  final List<String> hardcoreCompletedLevelIds;
  final Map<String, String> hardcoreDeadlines;
  final bool hardcoreMode;
  final int totalXp;
  final int lives;
  final int streak;
  final String? lastActiveDay;
  final bool onboardingDone;

  AppProgress copyWith({
    List<String>? completedLevelIds,
    List<String>? hardcoreCompletedLevelIds,
    Map<String, String>? hardcoreDeadlines,
    bool? hardcoreMode,
    int? totalXp,
    int? lives,
    int? streak,
    String? lastActiveDay,
    bool? onboardingDone,
  }) {
    return AppProgress(
      completedLevelIds: completedLevelIds ?? this.completedLevelIds,
      hardcoreCompletedLevelIds: hardcoreCompletedLevelIds ?? this.hardcoreCompletedLevelIds,
      hardcoreDeadlines: hardcoreDeadlines ?? this.hardcoreDeadlines,
      hardcoreMode: hardcoreMode ?? this.hardcoreMode,
      totalXp: totalXp ?? this.totalXp,
      lives: lives ?? this.lives,
      streak: streak ?? this.streak,
      lastActiveDay: lastActiveDay ?? this.lastActiveDay,
      onboardingDone: onboardingDone ?? this.onboardingDone,
    );
  }
}
