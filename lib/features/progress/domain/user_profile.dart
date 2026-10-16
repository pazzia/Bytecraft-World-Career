import '../../../core/time/calendar_day.dart';
import '../../gamification/domain/game_rules.dart';
import '../../gamification/domain/lives.dart';
import '../../gamification/domain/streak.dart';

/// The player's account-wide state.
///
/// Account level is derived from [totalXp] (see AccountLevelCalculator).
class UserProfile {
  UserProfile({
    required this.userId,
    required this.displayName,
    required this.avatarId,
    required this.totalXp,
    required this.coins,
    required this.isPremium,
    required this.createdAt,
    required this.lives,
    required this.streak,
    Set<String> unlockedAchievements = const <String>{},
    this.lastActivityAt,
    this.lastDailyChallengeDay,
  }) : unlockedAchievements = Set.unmodifiable(unlockedAchievements);

  factory UserProfile.create({
    required String userId,
    required DateTime now,
    required GameRules rules,
  }) =>
      UserProfile(
        userId: userId,
        displayName: defaultDisplayName,
        avatarId: defaultAvatarId,
        totalXp: 0,
        coins: 0,
        isPremium: false,
        createdAt: now,
        lives: LivesState.full(rules),
        streak: const StreakState(),
      );

  factory UserProfile.fromJson(Map<String, dynamic> json, GameRules rules) {
    int read(String key) {
      final value = json[key];
      return value is int ? value : 0;
    }

    final achievements = json['achievements'];
    final lives = json['lives'];
    final streak = json['streak'];
    final lastActivity = json['lastActivityAt'];
    final createdAt = json['createdAt'];
    return UserProfile(
      userId: json['userId'] as String,
      displayName: json['displayName'] as String? ?? defaultDisplayName,
      avatarId: json['avatarId'] as String? ?? defaultAvatarId,
      totalXp: read('totalXp'),
      coins: read('coins'),
      isPremium: json['isPremium'] == true,
      createdAt: (createdAt is String ? DateTime.tryParse(createdAt) : null) ??
          DateTime.fromMillisecondsSinceEpoch(0),
      lives: lives is Map<String, dynamic>
          ? LivesState.fromJson(lives, rules)
          : LivesState.full(rules),
      streak: streak is Map<String, dynamic>
          ? StreakState.fromJson(streak)
          : const StreakState(),
      unlockedAchievements: achievements is List
          ? achievements.whereType<String>().toSet()
          : const <String>{},
      lastActivityAt:
          lastActivity is String ? DateTime.tryParse(lastActivity) : null,
      lastDailyChallengeDay:
          CalendarDay.tryParse(json['lastDailyChallengeDay'] as String?),
    );
  }

  static const String defaultDisplayName = 'Coder';
  static const String defaultAvatarId = 'robot';

  final String userId;
  final String displayName;
  final String avatarId;
  final int totalXp;
  final int coins;
  final bool isPremium;
  final DateTime createdAt;
  final DateTime? lastActivityAt;
  final LivesState lives;
  final StreakState streak;
  final Set<String> unlockedAchievements;
  final CalendarDay? lastDailyChallengeDay;

  UserProfile copyWith({
    String? displayName,
    String? avatarId,
    int? totalXp,
    int? coins,
    bool? isPremium,
    DateTime? lastActivityAt,
    LivesState? lives,
    StreakState? streak,
    Set<String>? unlockedAchievements,
    CalendarDay? lastDailyChallengeDay,
  }) =>
      UserProfile(
        userId: userId,
        displayName: displayName ?? this.displayName,
        avatarId: avatarId ?? this.avatarId,
        totalXp: totalXp ?? this.totalXp,
        coins: coins ?? this.coins,
        isPremium: isPremium ?? this.isPremium,
        createdAt: createdAt,
        lastActivityAt: lastActivityAt ?? this.lastActivityAt,
        lives: lives ?? this.lives,
        streak: streak ?? this.streak,
        unlockedAchievements: unlockedAchievements ?? this.unlockedAchievements,
        lastDailyChallengeDay:
            lastDailyChallengeDay ?? this.lastDailyChallengeDay,
      );

  Map<String, dynamic> toJson() => {
        'userId': userId,
        'displayName': displayName,
        'avatarId': avatarId,
        'totalXp': totalXp,
        'coins': coins,
        'isPremium': isPremium,
        'createdAt': createdAt.toIso8601String(),
        if (lastActivityAt != null)
          'lastActivityAt': lastActivityAt!.toIso8601String(),
        'lives': lives.toJson(),
        'streak': streak.toJson(),
        'achievements': unlockedAchievements.toList()..sort(),
        if (lastDailyChallengeDay != null)
          'lastDailyChallengeDay': lastDailyChallengeDay!.toIso(),
      };
}
