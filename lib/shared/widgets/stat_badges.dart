import 'package:flutter/material.dart';

import '../../core/theme/app_spacing.dart';
import '../../core/theme/game_colors.dart';

/// Pill with an emoji/icon glyph and a value. Base for all HUD badges.
class StatBadge extends StatelessWidget {
  const StatBadge({
    super.key,
    required this.glyph,
    required this.value,
    required this.color,
    this.tooltip,
  });

  final String glyph;
  final String value;
  final Color color;
  final String? tooltip;

  static const double _backgroundAlpha = 0.14;

  @override
  Widget build(BuildContext context) {
    final badge = Container(
      padding: const EdgeInsets.symmetric(
        horizontal: Spacing.md,
        vertical: Spacing.xs + Spacing.xxs,
      ),
      decoration: BoxDecoration(
        color: color.withValues(alpha: _backgroundAlpha),
        borderRadius: AppRadius.pillAll,
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(glyph, style: const TextStyle(fontSize: 16)),
          const SizedBox(width: Spacing.xs),
          Text(
            value,
            style: Theme.of(context)
                .textTheme
                .titleSmall
                ?.copyWith(color: color, fontWeight: FontWeight.w800),
          ),
        ],
      ),
    );
    return tooltip == null ? badge : Tooltip(message: tooltip, child: badge);
  }
}

class StreakBadge extends StatelessWidget {
  const StreakBadge({super.key, required this.days});

  final int days;

  @override
  Widget build(BuildContext context) => StatBadge(
        glyph: '🔥',
        value: '$days',
        color: context.gameColors.streak,
        tooltip: 'Серия дней',
      );
}

class XpBadge extends StatelessWidget {
  const XpBadge({super.key, required this.xp});

  final int xp;

  @override
  Widget build(BuildContext context) => StatBadge(
        glyph: '⚡',
        value: '$xp XP',
        color: context.gameColors.xp,
      );
}

class CoinBadge extends StatelessWidget {
  const CoinBadge({super.key, required this.coins});

  final int coins;

  @override
  Widget build(BuildContext context) => StatBadge(
        glyph: '🪙',
        value: '$coins',
        color: context.gameColors.coin,
        tooltip: 'Монеты',
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
        glyph: '❤️',
        value: isUnlimited ? '∞' : '$current',
        color: context.gameColors.life,
        tooltip: 'Жизни',
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
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        for (var i = 0; i < max; i++)
          Icon(
            Icons.star_rounded,
            size: size,
            color: i < stars ? colors.coin : colors.locked,
          ),
      ],
    );
  }
}
