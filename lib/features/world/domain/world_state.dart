import 'skill_repair.dart';

class WorldState {
  const WorldState({
    this.trainingCurriculumVersion = 2,
    this.hasVerifiedProject = false,
    this.repairs = const {},
    this.solved = const {},
    this.failures = const {},
    this.lastActiveDay = '',
    this.showMigrationNotice = false,
    required this.coins,
    required this.gems,
    required this.worldXp,
    required this.seasonLevel,
    required this.seasonXp,
    required this.streak,
    required this.hearts,
    this.heartRegenAnchor,
    required this.expeditionStep,
    required this.expeditionChestClaimed,
    required this.bossHp,
    required this.bossTask,
    required this.bossCleared,
    required this.ghostBestSeconds,
    required this.guildContribution,
    required this.guildTotal,
    required this.rivalWins,
    required this.infiniteCurrent,
    required this.infiniteRecord,
    required this.cityLevels,
    required this.projectSteps,
    required this.mistakes,
  });

  factory WorldState.initial() => const WorldState(
    coins: 0,
    gems: 3,
    worldXp: 0,
    seasonLevel: 1,
    seasonXp: 0,
    streak: 0,
    hearts: 3,
    expeditionStep: 0,
    expeditionChestClaimed: false,
    bossHp: 100,
    bossTask: 0,
    bossCleared: false,
    ghostBestSeconds: 0,
    guildContribution: 0,
    guildTotal: 0,
    rivalWins: 0,
    infiniteCurrent: 0,
    infiniteRecord: 0,
    cityLevels: {'office': 1, 'python': 1, 'rnd': 1, 'servers': 1, 'team': 1},
    projectSteps: {
      'basic': false,
      'history': false,
      'errors': false,
      'ui': false,
    },
    mistakes: {
      'Условия': 0,
      'Циклы': 0,
      'Индексы': 0,
      'Типы данных': 0,
      'Функции': 0,
    },
  );

  factory WorldState.fromJson(Map<String, dynamic> json) {
    Map<String, int> ints(String key, Map<String, int> fallback) {
      final raw = json[key];
      if (raw is! Map) return fallback;
      return raw.map((k, v) => MapEntry('$k', v is num ? v.toInt() : 0));
    }

    Map<String, bool> bools(String key, Map<String, bool> fallback) {
      final raw = json[key];
      if (raw is! Map) return fallback;
      return raw.map((k, v) => MapEntry('$k', v == true));
    }

    final initial = WorldState.initial();
    return WorldState(
      repairs: {for (final entry in (json['repairs'] as Map? ?? {}).entries)
        '${entry.key}': SkillRepair.fromJson(Map<String, dynamic>.from(entry.value as Map))},
      hasVerifiedProject: json['hasVerifiedProject'] == true,
      trainingCurriculumVersion: (json['trainingCurriculumVersion'] as num?)?.toInt() ?? 1,
      solved: ints('solved', {}),
      failures: ints('failures', {}),
      lastActiveDay: json['lastActiveDay'] as String? ?? '',
      showMigrationNotice: json['showMigrationNotice'] == true,
      coins: (json['coins'] as num?)?.toInt() ?? initial.coins,
      gems: (json['gems'] as num?)?.toInt() ?? initial.gems,
      worldXp: (json['worldXp'] as num?)?.toInt() ?? initial.worldXp,
      seasonLevel:
          (json['seasonLevel'] as num?)?.toInt() ?? initial.seasonLevel,
      seasonXp: (json['seasonXp'] as num?)?.toInt() ?? initial.seasonXp,
      streak: (json['streak'] as num?)?.toInt() ?? initial.streak,
      hearts: (json['hearts'] as num?)?.toInt() ?? initial.hearts,
      heartRegenAnchor: DateTime.tryParse('${json['heartRegenAnchor']}'),
      expeditionStep:
          (json['expeditionStep'] as num?)?.toInt() ?? initial.expeditionStep,
      expeditionChestClaimed: json['expeditionChestClaimed'] == true,
      bossHp: (json['bossHp'] as num?)?.toInt() ?? initial.bossHp,
      bossTask: (json['bossTask'] as num?)?.toInt() ?? initial.bossTask,
      bossCleared: json['bossCleared'] == true,
      ghostBestSeconds:
          (json['ghostBestSeconds'] as num?)?.toInt() ??
          initial.ghostBestSeconds,
      guildContribution:
          (json['guildContribution'] as num?)?.toInt() ??
          initial.guildContribution,
      guildTotal: (json['guildTotal'] as num?)?.toInt() ?? initial.guildTotal,
      rivalWins: (json['rivalWins'] as num?)?.toInt() ?? initial.rivalWins,
      infiniteCurrent:
          (json['infiniteCurrent'] as num?)?.toInt() ?? initial.infiniteCurrent,
      infiniteRecord:
          (json['infiniteRecord'] as num?)?.toInt() ?? initial.infiniteRecord,
      cityLevels: ints('cityLevels', initial.cityLevels),
      projectSteps: bools('projectSteps', initial.projectSteps),
      mistakes: ints('mistakes', initial.mistakes),
    );
  }

  final bool hasVerifiedProject;
  final Map<String, SkillRepair> repairs;
  final int trainingCurriculumVersion;
  final Map<String, int> solved;
  final Map<String, int> failures;
  final String lastActiveDay;
  final bool showMigrationNotice;
  final int coins;
  final int gems;
  final int worldXp;
  final int seasonLevel;
  final int seasonXp;
  final int streak;
  final int hearts;
  final DateTime? heartRegenAnchor;
  final int expeditionStep;
  final bool expeditionChestClaimed;
  final int bossHp;
  final int bossTask;
  final bool bossCleared;
  final int ghostBestSeconds;
  final int guildContribution;
  final int guildTotal;
  final int rivalWins;
  final int infiniteCurrent;
  final int infiniteRecord;
  final Map<String, int> cityLevels;
  final Map<String, bool> projectSteps;
  final Map<String, int> mistakes;

  static const projectIds = ['basic', 'history', 'errors', 'ui'];
  int get completedProjectSteps =>
      projectIds.where((id) => projectSteps[id] == true).length;
  int get maxHearts => 3 + (cityLevels['servers'] ?? 1) - 1;
  int get buildingCap => (1 + worldXp ~/ 200).clamp(1, 5);
  int get solvedTotal => solved.entries
      .where((e) => !e.key.startsWith('lesson:'))
      .fold(0, (n, e) => n + e.value);
  bool get projectUnlocked => completedProjectSteps >= 4;
  int get expeditionProgress => expeditionStep.clamp(0, 5).toInt();

  WorldState copyWith({
    Map<String, SkillRepair>? repairs,
    int? trainingCurriculumVersion,
    bool? hasVerifiedProject,
    Map<String, int>? solved,
    Map<String, int>? failures,
    String? lastActiveDay,
    bool? showMigrationNotice,
    int? coins,
    int? gems,
    int? worldXp,
    int? seasonLevel,
    int? seasonXp,
    int? streak,
    int? hearts,
    DateTime? heartRegenAnchor,
    bool clearHeartRegenAnchor = false,
    int? expeditionStep,
    bool? expeditionChestClaimed,
    int? bossHp,
    int? bossTask,
    bool? bossCleared,
    int? ghostBestSeconds,
    int? guildContribution,
    int? guildTotal,
    int? rivalWins,
    int? infiniteCurrent,
    int? infiniteRecord,
    Map<String, int>? cityLevels,
    Map<String, bool>? projectSteps,
    Map<String, int>? mistakes,
  }) => WorldState(
    repairs: repairs ?? this.repairs,
    hasVerifiedProject: hasVerifiedProject ?? this.hasVerifiedProject,
    trainingCurriculumVersion: trainingCurriculumVersion ?? this.trainingCurriculumVersion,
    solved: solved ?? this.solved,
    failures: failures ?? this.failures,
    lastActiveDay: lastActiveDay ?? this.lastActiveDay,
    showMigrationNotice: showMigrationNotice ?? this.showMigrationNotice,
    coins: coins ?? this.coins,
    gems: gems ?? this.gems,
    worldXp: worldXp ?? this.worldXp,
    seasonLevel: seasonLevel ?? this.seasonLevel,
    seasonXp: seasonXp ?? this.seasonXp,
    streak: streak ?? this.streak,
    hearts: hearts ?? this.hearts,
    heartRegenAnchor: clearHeartRegenAnchor ? null : heartRegenAnchor ?? this.heartRegenAnchor,
    expeditionStep: expeditionStep ?? this.expeditionStep,
    expeditionChestClaimed:
        expeditionChestClaimed ?? this.expeditionChestClaimed,
    bossHp: bossHp ?? this.bossHp,
    bossTask: bossTask ?? this.bossTask,
    bossCleared: bossCleared ?? this.bossCleared,
    ghostBestSeconds: ghostBestSeconds ?? this.ghostBestSeconds,
    guildContribution: guildContribution ?? this.guildContribution,
    guildTotal: guildTotal ?? this.guildTotal,
    rivalWins: rivalWins ?? this.rivalWins,
    infiniteCurrent: infiniteCurrent ?? this.infiniteCurrent,
    infiniteRecord: infiniteRecord ?? this.infiniteRecord,
    cityLevels: cityLevels ?? this.cityLevels,
    projectSteps: projectSteps ?? this.projectSteps,
    mistakes: mistakes ?? this.mistakes,
  );

  Map<String, dynamic> toJson() => {
    'repairs': {for (final entry in repairs.entries) entry.key: entry.value.toJson()},
    'hasVerifiedProject': hasVerifiedProject,
    'trainingCurriculumVersion': trainingCurriculumVersion,
    'solved': solved,
    'failures': failures,
    'lastActiveDay': lastActiveDay,
    'showMigrationNotice': showMigrationNotice,
    'coins': coins,
    'gems': gems,
    'worldXp': worldXp,
    'seasonLevel': seasonLevel,
    'seasonXp': seasonXp,
    'streak': streak,
    'hearts': hearts,
    if (heartRegenAnchor != null) 'heartRegenAnchor': heartRegenAnchor!.toUtc().toIso8601String(),
    'expeditionStep': expeditionStep,
    'expeditionChestClaimed': expeditionChestClaimed,
    'bossHp': bossHp,
    'bossTask': bossTask,
    'bossCleared': bossCleared,
    'ghostBestSeconds': ghostBestSeconds,
    'guildContribution': guildContribution,
    'guildTotal': guildTotal,
    'rivalWins': rivalWins,
    'infiniteCurrent': infiniteCurrent,
    'infiniteRecord': infiniteRecord,
    'cityLevels': cityLevels,
    'projectSteps': projectSteps,
    'mistakes': mistakes,
  };
}
