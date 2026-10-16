import 'package:flutter/material.dart';

import '../../../core/theme/game_colors.dart';
import '../../../shared/widgets/keycap.dart';
import '../domain/achievement.dart';

/// Icon and color for each achievement (UI only; the catalog stays data).
(IconData, Color Function(GameColors)) achievementVisual(Achievement a) =>
    switch (a.id) {
      'first_code' => (Icons.code_rounded, (c) => const Color(0xFF2F6DB5)),
      'levels_10' => (Icons.filter_9_plus_rounded, (c) => c.success),
      'xp_1000' => (Icons.bolt_rounded, (c) => c.rewardEdge),
      'streak_7' => (Icons.local_fire_department_rounded, (c) => c.streak),
      'streak_30' => (Icons.whatshot_rounded, (c) => c.errorEdge),
      'perfect_level' => (Icons.star_rounded, (c) => c.rewardEdge),
      'python_beginner' => (Icons.school_rounded, (c) => c.success),
      'python_explorer' => (Icons.explore_rounded, (c) => const Color(0xFF2F6DB5)),
      'python_master' => (Icons.workspace_premium_rounded, (c) => c.streak),
      _ => (Icons.emoji_events_rounded, (c) => c.rewardEdge),
    };

/// Square key badge; flat and grey while locked.
class AchievementBadge extends StatelessWidget {
  const AchievementBadge({
    super.key,
    required this.achievement,
    required this.unlocked,
    this.size = 60,
  });

  final Achievement achievement;
  final bool unlocked;
  final double size;

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    final (icon, colorOf) = achievementVisual(achievement);
    final color = colorOf(game);
    if (!unlocked) {
      return Container(
        width: size,
        height: size,
        margin: const EdgeInsets.only(bottom: 4),
        decoration: BoxDecoration(
          color: game.locked,
          borderRadius: BorderRadius.circular(size * 0.3),
        ),
        child: Icon(Icons.lock_rounded, color: game.lockedIcon, size: size * 0.4),
      );
    }
    return Keycap(
      face: color,
      edge: Color.lerp(color, Colors.black, 0.3)!,
      radius: size * 0.3,
      width: size,
      height: size + 4,
      haptic: false,
      child: Icon(icon, color: Colors.white, size: size * 0.46),
    );
  }
}
