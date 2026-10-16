import 'package:flutter/material.dart';

import '../../../../core/theme/app_spacing.dart';
import '../../../../core/theme/app_typography.dart';
import '../../../../core/theme/game_colors.dart';
import '../../../../shared/widgets/stat_badges.dart';
import '../../../courses/domain/level_type.dart';
import '../../domain/learning_map_model.dart';

/// One stop on the "circuit" path: a chip-shaped node on the rail plus a
/// card with the level title. Visual concept: a circuit board trace that
/// the player "powers up" level by level.
class MapNodeTile extends StatelessWidget {
  const MapNodeTile({
    super.key,
    required this.node,
    required this.isFirst,
    required this.isLast,
    required this.onTap,
  });

  final MapNode node;
  final bool isFirst;
  final bool isLast;
  final VoidCallback onTap;

  static const double _nodeSize = 56;
  static const double _railWidth = 6;
  static const double _railColumn = 72;

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    final scheme = Theme.of(context).colorScheme;
    final poweredRail = node.state == MapNodeState.completed
        ? game.success
        : game.locked;

    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SizedBox(
            width: _railColumn,
            child: Stack(
              alignment: Alignment.center,
              children: [
                Column(
                  children: [
                    Expanded(
                      child: Container(
                        width: _railWidth,
                        color: isFirst ? Colors.transparent : poweredRail,
                      ),
                    ),
                    Expanded(
                      child: Container(
                        width: _railWidth,
                        color: isLast ? Colors.transparent : poweredRail,
                      ),
                    ),
                  ],
                ),
                _NodeChip(node: node, size: _nodeSize, onTap: onTap),
              ],
            ),
          ),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: Spacing.sm),
              child: Material(
                color: node.state == MapNodeState.current
                    ? scheme.primary.withValues(alpha: 0.1)
                    : Colors.transparent,
                borderRadius: AppRadius.mdAll,
                child: InkWell(
                  borderRadius: AppRadius.mdAll,
                  onTap: onTap,
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: Spacing.md,
                      vertical: Spacing.md,
                    ),
                    child: _NodeLabel(node: node),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _NodeLabel extends StatelessWidget {
  const _NodeLabel({required this.node});

  final MapNode node;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    final isLocked = node.state == MapNodeState.locked;
    final roleLabel = switch (node.level.role) {
      LevelRole.boss => 'BOSS',
      LevelRole.challenge => 'CHALLENGE',
      LevelRole.practice => 'PRACTICE',
      LevelRole.lesson => null,
    };
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (roleLabel != null)
          Text(
            roleLabel,
            style: AppTypography.code(size: 11, color: game.streak)
                .copyWith(fontWeight: FontWeight.w800),
          ),
        Text(
          node.level.title,
          style: textTheme.titleMedium?.copyWith(
            color: isLocked ? game.locked : null,
          ),
        ),
        if (node.state == MapNodeState.completed) ...[
          const SizedBox(height: Spacing.xs),
          StarRow(stars: node.stars),
        ],
        if (node.state == MapNodeState.current)
          Text(
            'Продолжить →',
            style: textTheme.labelLarge?.copyWith(
              color: Theme.of(context).colorScheme.primary,
            ),
          ),
      ],
    );
  }
}

class _NodeChip extends StatelessWidget {
  const _NodeChip({required this.node, required this.size, required this.onTap});

  final MapNode node;
  final double size;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    final scheme = Theme.of(context).colorScheme;
    final isBoss = node.level.role == LevelRole.boss;
    final color = switch (node.state) {
      MapNodeState.completed => game.success,
      MapNodeState.current => scheme.primary,
      MapNodeState.available => scheme.secondary,
      MapNodeState.locked => game.locked,
    };
    final glyph = switch (node.state) {
      MapNodeState.locked => '🔒',
      MapNodeState.completed => isBoss ? '👑' : '✓',
      _ => switch (node.level.role) {
          LevelRole.boss => '👑',
          LevelRole.challenge => '★',
          LevelRole.practice => '⚙',
          LevelRole.lesson => '▶',
        },
    };
    final chipSize = isBoss ? size + Spacing.md : size;
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: chipSize,
        height: chipSize,
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: color,
          // Rounded square = "chip" on the circuit, not a bubble.
          borderRadius: BorderRadius.circular(chipSize / 3.2),
          boxShadow: AppShadows.edge(Color.lerp(color, Colors.black, 0.3)!),
          border: node.state == MapNodeState.current
              ? Border.all(color: scheme.onPrimary, width: 3)
              : null,
        ),
        child: Text(
          glyph,
          style: TextStyle(
            fontSize: 22,
            fontWeight: FontWeight.w900,
            color: scheme.onPrimary,
          ),
        ),
      ),
    );
  }
}
