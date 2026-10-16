import 'package:flutter/material.dart';

import '../../core/theme/app_spacing.dart';
import '../../core/theme/game_colors.dart';
import 'keycap.dart';

/// A large flat key: white face, border, solid edge. Tappable when [onTap]
/// is given.
class AppCard extends StatelessWidget {
  const AppCard({
    super.key,
    required this.child,
    this.onTap,
    this.padding = const EdgeInsets.all(Spacing.lg),
    this.color,
    this.borderColor,
    this.edgeColor,
    this.semanticLabel,
  });

  final Widget child;
  final VoidCallback? onTap;
  final EdgeInsetsGeometry padding;
  final Color? color;
  final Color? borderColor;
  final Color? edgeColor;
  final String? semanticLabel;

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    return Keycap(
      onTap: onTap,
      haptic: onTap != null,
      face: color ?? game.keyFace,
      edge: edgeColor ?? borderColor ?? game.keyEdge,
      border: borderColor ?? game.keyBorder,
      radius: AppRadius.xl,
      padding: padding,
      alignment: AlignmentDirectional.topStart,
      semanticLabel: semanticLabel,
      child: child,
    );
  }
}

/// Section heading: sentence case, no eyebrow labels.
class SectionTitle extends StatelessWidget {
  const SectionTitle(this.text, {super.key, this.trailing});

  final String text;
  final String? trailing;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    return Padding(
      padding: const EdgeInsets.only(top: Spacing.xxl, bottom: Spacing.md),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.baseline,
        textBaseline: TextBaseline.alphabetic,
        children: [
          Expanded(
            child: Text(
              text,
              style: textTheme.titleMedium?.copyWith(fontSize: 18),
            ),
          ),
          if (trailing != null)
            Text(
              trailing!,
              style: textTheme.labelMedium
                  ?.copyWith(color: context.gameColors.textMuted),
            ),
        ],
      ),
    );
  }
}
