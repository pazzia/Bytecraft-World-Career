import 'package:flutter/material.dart';

import '../../../../core/theme/app_spacing.dart';
import '../../../../core/theme/app_typography.dart';
import '../../../../core/theme/game_colors.dart';
import '../../../../shared/widgets/game_icons.dart';
import '../../../../shared/widgets/keycap.dart';
import '../../../../shared/widgets/stat_badges.dart';
import '../../../courses/domain/level_payload.dart';
import '../../../courses/domain/level_type.dart';
import '../../domain/learning_map_model.dart';

/// One level on the map: a square key (done / current / locked) and its
/// label. The current level gets a ring and an expanded card.
class MapNodeTile extends StatelessWidget {
  const MapNodeTile({super.key, required this.node, required this.onTap});

  final MapNode node;
  final VoidCallback onTap;

  static const double _column = 64;

  @override
  Widget build(BuildContext context) {
    final isCurrent = node.state == MapNodeState.current;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: Spacing.xs),
      child: Row(
        children: [
          SizedBox(
            width: _column,
            child: Center(child: _NodeKey(node: node, onTap: onTap)),
          ),
          const SizedBox(width: Spacing.md),
          Expanded(
            child: isCurrent
                ? _CurrentCard(node: node, onTap: onTap)
                : _NodeLabel(node: node, onTap: onTap),
          ),
        ],
      ),
    );
  }
}

class _NodeKey extends StatelessWidget {
  const _NodeKey({required this.node, required this.onTap});

  final MapNode node;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    final scheme = Theme.of(context).colorScheme;
    final isBoss = node.level.role == LevelRole.boss;
    final label = '${node.level.title}: ${switch (node.state) {
      MapNodeState.completed => 'пройден, ${node.stars} из 3 звёзд',
      MapNodeState.current => 'следующий уровень',
      MapNodeState.available => 'доступен',
      MapNodeState.locked => 'закрыт',
    }}';

    switch (node.state) {
      case MapNodeState.locked:
        return Semantics(
          label: label,
          button: true,
          excludeSemantics: true,
          child: GestureDetector(
            onTap: onTap,
            child: Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: game.locked,
                borderRadius: BorderRadius.circular(15),
              ),
              child: Icon(Icons.lock_rounded, size: 20, color: game.lockedIcon),
            ),
          ),
        );
      case MapNodeState.completed:
        return Keycap(
          onTap: onTap,
          face: game.success,
          edge: game.successEdge,
          radius: 16,
          width: isBoss ? 56 : 52,
          height: isBoss ? 60 : 56,
          semanticLabel: label,
          child: isBoss
              ? CrownIcon(size: 28, color: game.reward)
              : const Icon(Icons.check_rounded, color: Colors.white, size: 28),
        );
      case MapNodeState.current:
      case MapNodeState.available:
        final current = node.state == MapNodeState.current;
        return Container(
          decoration: current
              ? BoxDecoration(
                  borderRadius: BorderRadius.circular(22),
                  border: Border.all(color: game.primaryTint, width: 5),
                )
              : null,
          child: Keycap(
            onTap: onTap,
            face: current ? scheme.primary : game.keyFace,
            edge: current ? game.primaryEdge : game.keyEdge,
            border: current ? null : game.keyBorder,
            radius: 18,
            width: 56,
            height: 60,
            semanticLabel: label,
            child: isBoss
                ? CrownIcon(
                    size: 26,
                    color: current ? game.reward : game.rewardIcon,
                  )
                : Icon(
                    Icons.play_arrow_rounded,
                    size: 28,
                    color: current ? game.onPrimary : scheme.primary,
                  ),
          ),
        );
    }
  }
}

class _NodeLabel extends StatelessWidget {
  const _NodeLabel({required this.node, required this.onTap});

  final MapNode node;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    final locked = node.state == MapNodeState.locked;
    return ExcludeSemantics(
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: Spacing.sm),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (node.level.role == LevelRole.boss)
                Text(
                  'Босс модуля',
                  style: textTheme.labelMedium?.copyWith(
                    color: game.streakText,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              Text(
                node.level.title,
                style: textTheme.titleMedium?.copyWith(
                  color: locked ? game.textMuted : null,
                  fontWeight: locked ? FontWeight.w600 : FontWeight.w700,
                ),
              ),
              if (node.state == MapNodeState.completed) ...[
                const SizedBox(height: Spacing.xxs),
                StarRow(stars: node.stars),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _CurrentCard extends StatelessWidget {
  const _CurrentCard({required this.node, required this.onTap});

  final MapNode node;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;
    final game = context.gameColors;
    final codeHint = switch (node.level.payload) {
      FillCodePayload() || CodeOrderingPayload() => null,
      _ => node.level.codeLines.isEmpty ? null : node.level.codeLines.first,
    };
    return ExcludeSemantics(
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(
            horizontal: Spacing.lg,
            vertical: Spacing.md,
          ),
          decoration: BoxDecoration(
            color: game.keyFace,
            borderRadius: BorderRadius.circular(18),
            border: Border.all(color: scheme.primary, width: 2),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (node.level.role == LevelRole.boss)
                Text(
                  'Босс модуля',
                  style: textTheme.labelMedium?.copyWith(
                    color: game.streakText,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              Text(node.level.title, style: textTheme.titleMedium),
              if (codeHint != null)
                Text(
                  codeHint,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: AppTypography.code(size: 14, color: game.textMuted),
                ),
              const SizedBox(height: Spacing.xs),
              Text(
                'Начать',
                style: textTheme.titleSmall?.copyWith(color: scheme.primary),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
