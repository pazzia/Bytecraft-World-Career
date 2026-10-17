class WorldState {
  const WorldState({
    required this.coins,
    required this.gems,
    required this.worldXp,
    required this.seasonLevel,
    required this.seasonXp,
    required this.streak,
    required this.hearts,
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
        coins: 1240,
        gems: 15,
        worldXp: 450,
        seasonLevel: 12,
        seasonXp: 450,
        streak: 23,
        hearts: 3,
        expeditionStep: 0,
        expeditionChestClaimed: false,
        bossHp: 100,
        bossTask: 0,
        bossCleared: false,
        ghostBestSeconds: 268,
        guildContribution: 42,
        guildTotal: 87,
        rivalWins: 0,
        infiniteCurrent: 0,
        infiniteRecord: 37,
        cityLevels: {
          'office': 2,
          'python': 3,
          'rnd': 1,
          'servers': 2,
          'team': 2,
        },
        projectSteps: {
          'basic': true,
          'history': true,
          'errors': false,
          'ui': false,
        },
        mistakes: {
          'Условия': 42,
          'Циклы': 28,
          'Индексы': 15,
          'Типы данных': 8,
          'Функции': 7,
        },
      );

  factory WorldState.fromJson(Map<String, dynamic> json) {
    Map<String, int> ints(String key, Map<String, int> fallback) {
      final raw = json[key];
      if (raw is! Map) return fallback;
      return raw.map(
        (k, v) => MapEntry('$k', v is num ? v.toInt() : 0),
      );
    }

    Map<String, bool> bools(String key, Map<String, bool> fallback) {
      final raw = json[key];
      if (raw is! Map) return fallback;
      return raw.map((k, v) => MapEntry('$k', v == true));
    }

    final initial = WorldState.initial();
    return WorldState(
      coins: (json['coins'] as num?)?.toInt() ?? initial.coins,
      gems: (json['gems'] as num?)?.toInt() ?? initial.gems,
      worldXp: (json['worldXp'] as num?)?.toInt() ?? initial.worldXp,
      seasonLevel:
          (json['seasonLevel'] as num?)?.toInt() ?? initial.seasonLevel,
      seasonXp: (json['seasonXp'] as num?)?.toInt() ?? initial.seasonXp,
      streak: (json['streak'] as num?)?.toInt() ?? initial.streak,
      hearts: (json['hearts'] as num?)?.toInt() ?? initial.hearts,
      expeditionStep:
          (json['expeditionStep'] as num?)?.toInt() ?? initial.expeditionStep,
      expeditionChestClaimed: json['expeditionChestClaimed'] == true,
      bossHp: (json['bossHp'] as num?)?.toInt() ?? initial.bossHp,
      bossTask: (json['bossTask'] as num?)?.toInt() ?? initial.bossTask,
      bossCleared: json['bossCleared'] == true,
      ghostBestSeconds:
          (json['ghostBestSeconds'] as num?)?.toInt() ?? initial.ghostBestSeconds,
      guildContribution: (json['guildContribution'] as num?)?.toInt() ??
          initial.guildContribution,
      guildTotal:
          (json['guildTotal'] as num?)?.toInt() ?? initial.guildTotal,
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

  final int coins;
  final int gems;
  final int worldXp;
  final int seasonLevel;
  final int seasonXp;
  final int streak;
  final int hearts;
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

  int get completedProjectSteps => projectSteps.values.where((v) => v).length;
  bool get projectUnlocked => completedProjectSteps >= 4;
  int get expeditionProgress => expeditionStep.clamp(0, 5).toInt();

  WorldState copyWith({
    int? coins,
    int? gems,
    int? worldXp,
    int? seasonLevel,
    int? seasonXp,
    int? streak,
    int? hearts,
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
  }) =>
      WorldState(
        coins: coins ?? this.coins,
        gems: gems ?? this.gems,
        worldXp: worldXp ?? this.worldXp,
        seasonLevel: seasonLevel ?? this.seasonLevel,
        seasonXp: seasonXp ?? this.seasonXp,
        streak: streak ?? this.streak,
        hearts: hearts ?? this.hearts,
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
        'coins': coins,
        'gems': gems,
        'worldXp': worldXp,
        'seasonLevel': seasonLevel,
        'seasonXp': seasonXp,
        'streak': streak,
        'hearts': hearts,
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
