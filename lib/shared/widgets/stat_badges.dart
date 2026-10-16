import 'package:flutter/material.dart';

import '../../core/theme/app_spacing.dart';
import '../../core/theme/game_colors.dart';

/// Icon + number, no pill. The HUD of the game.
class StatBadge extends StatelessWidget {
  const StatBadge({
    super.key,
    required this.icon,
    required this.value,
    required this.color,
    required this.semanticLabel,
    this.textColor,
  });

  final IconData icon;
  final String value;
  final Color color;
  final Color? textColor;
  final String semanticLabel;

  @override
  Widget build(BuildContext context) => Semantics(
        label: semanticLabel,
        excludeSemantics: true,
        child: ConstrainedBox(
          constraints: const BoxConstraints(minHeight: Spacing.touchTarget - 8),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, color: color, size: 22),
              const SizedBox(width: Spacing.xs),
              Text(
                value,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: textColor,
                      fontWeight: FontWeight.w700,
                      fontFeatures: const [FontFeature.tabularFigures()],
                    ),
              ),
            ],
          ),
        ),
      );
}

class StreakBadge extends StatelessWidget {
  const StreakBadge({super.key, required this.days});

  final int days;

  @override
  Widget build(BuildContext context) => StatBadge(
        icon: Icons.local_fire_department_rounded,
        value: '$days',
        color: context.gameColors.streak,
        semanticLabel: 'Серия: $days дн.',
      );
}

class XpBadge extends StatelessWidget {
  const XpBadge({super.key, required this.xp});

  final int xp;

  @override
  Widget build(BuildContext context) => StatBadge(
        icon: Icons.bolt_rounded,
        value: '$xp',
        color: context.gameColors.rewardIcon,
        semanticLabel: 'Опыт: $xp',
      );
}

class CoinBadge extends StatelessWidget {
  const CoinBadge({super.key, required this.coins});

  final int coins;

  @override
  Widget build(BuildContext context) => StatBadge(
        icon: Icons.toll_rounded,
        value: '$coins',
        color: context.gameColors.rewardIcon,
        semanticLabel: 'Монеты: $coins',
      );
}

class LivesBadge extends StatelessWidget {
  const LivesBadge({
    super.key,
    required this.current,
    required this.isUnlimited,
  });

  final int current;
  final bool isUnlimited;

  @override
  Widget build(BuildContext context) => StatBadge(
        icon: Icons.favorite_rounded,
        value: isUnlimited ? '∞' : '$current',
        color: context.gameColors.life,
        semanticLabel: isUnlimited ? 'Жизни: без ограничений' : 'Жизни: $current',
      );
}

class StarRow extends StatelessWidget {
  const StarRow({
    super.key,
    required this.stars,
    this.max = 3,
    this.size = 16,
  });

  final int stars;
  final int max;
  final double size;

  @override
  Widget build(BuildContext context) {
    final colors = context.gameColors;
    return Semantics(
      label: '$stars из $max звёзд',
      excludeSemantics: true,
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          for (var i = 0; i < max; i++)
            Icon(
              Icons.star_rounded,
              size: size,
              color: i < stars ? colors.rewardIcon : colors.track,
            ),
        ],
      ),
    );
  }
}

/// Russian plural: 1 жизнь, 2 жизни, 5 жизней.
String plural(int n, String one, String few, String many) {
  final mod10 = n % 10;
  final mod100 = n % 100;
  if (mod10 == 1 && mod100 != 11) return one;
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return few;
  return many;
}
