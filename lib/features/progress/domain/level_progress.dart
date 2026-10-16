/// Per-level persisted progress.
class LevelProgress {
  const LevelProgress({
    required this.levelId,
    this.completed = false,
    this.attempts = 0,
    this.bestStars = 0,
    this.xpEarned = 0,
    this.completedAt,
    this.lastPlayedAt,
  });

  factory LevelProgress.fromJson(Map<String, dynamic> json) {
    int read(String key) {
      final value = json[key];
      return value is int ? value : 0;
    }

    DateTime? date(String key) {
      final value = json[key];
      return value is String ? DateTime.tryParse(value) : null;
    }

    return LevelProgress(
      levelId: json['levelId'] as String,
      completed: json['completed'] == true,
      attempts: read('attempts'),
      bestStars: read('bestStars'),
      xpEarned: read('xpEarned'),
      completedAt: date('completedAt'),
      lastPlayedAt: date('lastPlayedAt'),
    );
  }

  final String levelId;
  final bool completed;

  /// Number of times the level was started.
  final int attempts;

  /// Best score achieved (stars are the score in this game).
  final int bestStars;
  final int xpEarned;
  final DateTime? completedAt;
  final DateTime? lastPlayedAt;

  bool get isPerfect => bestStars >= 3;

  LevelProgress copyWith({
    bool? completed,
    int? attempts,
    int? bestStars,
    int? xpEarned,
    DateTime? completedAt,
    DateTime? lastPlayedAt,
  }) =>
      LevelProgress(
        levelId: levelId,
        completed: completed ?? this.completed,
        attempts: attempts ?? this.attempts,
        bestStars: bestStars ?? this.bestStars,
        xpEarned: xpEarned ?? this.xpEarned,
        completedAt: completedAt ?? this.completedAt,
        lastPlayedAt: lastPlayedAt ?? this.lastPlayedAt,
      );

  Map<String, dynamic> toJson() => {
        'levelId': levelId,
        'completed': completed,
        'attempts': attempts,
        'bestStars': bestStars,
        'xpEarned': xpEarned,
        if (completedAt != null) 'completedAt': completedAt!.toIso8601String(),
        if (lastPlayedAt != null)
          'lastPlayedAt': lastPlayedAt!.toIso8601String(),
      };
}
