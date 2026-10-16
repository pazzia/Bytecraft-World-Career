import 'package:flutter/material.dart';

import '../../core/theme/app_spacing.dart';
import '../../core/theme/game_colors.dart';
import 'keycap.dart';

enum AppButtonVariant {
  /// Main action (blue; ember in the timed mode).
  primary,
  success,
  danger,

  /// Yellow: only for continuing towards a reward.
  reward,

  /// Flat white key with a border.
  secondary,

  /// Text-only, no key.
  quiet,
}

/// Full-width keycap button, 56 px high. Labels are sentence case.
class AppButton extends StatelessWidget {
  const AppButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.variant = AppButtonVariant.primary,
    this.icon,
    this.isLoading = false,
    this.expand = true,
  });

  final String label;
  final VoidCallback? onPressed;
  final AppButtonVariant variant;
  final IconData? icon;
  final bool isLoading;
  final bool expand;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final game = context.gameColors;
    final enabled = onPressed != null && !isLoading;

    if (variant == AppButtonVariant.quiet) {
      return SizedBox(
        width: expand ? double.infinity : null,
        height: Spacing.keyHeight - Spacing.xs,
        child: TextButton(
          onPressed: enabled ? onPressed : null,
          style: TextButton.styleFrom(
            foregroundColor: scheme.primary,
            textStyle: Theme.of(context).textTheme.titleMedium,
          ),
          child: Text(label),
        ),
      );
    }

    final (Color face, Color edge, Color text, Color? border) = switch (variant) {
      AppButtonVariant.primary =>
        (scheme.primary, game.primaryEdge, game.onPrimary, null),
      AppButtonVariant.success =>
        (game.success, game.successEdge, Colors.white, null),
      AppButtonVariant.danger => (game.error, game.errorEdge, Colors.white, null),
      AppButtonVariant.reward =>
        (game.reward, game.rewardEdge, game.onReward, null),
      AppButtonVariant.secondary =>
        (game.keyFace, game.keyEdge, scheme.onSurface, game.keyBorder),
      AppButtonVariant.quiet => (scheme.surface, scheme.surface, scheme.primary, null),
    };

    final labelText = Text(
      label,
      textAlign: TextAlign.center,
      overflow: TextOverflow.ellipsis,
      style: Theme.of(context).textTheme.labelLarge?.copyWith(
            color: enabled ? text : game.textMuted,
          ),
    );
    final content = isLoading
        ? SizedBox.square(
            dimension: 22,
            child: CircularProgressIndicator(strokeWidth: 3, color: text),
          )
        : Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (icon != null) ...[
                Icon(icon, color: enabled ? text : game.textMuted, size: 22),
                const SizedBox(width: Spacing.sm),
              ],
              // Flexible needs a bounded width: compact buttons may sit in
              // a Row, where the width is unbounded.
              if (expand) Flexible(child: labelText) else labelText,
            ],
          );

    final key = Keycap(
      onTap: enabled ? onPressed : null,
      face: enabled ? face : game.track,
      edge: enabled ? edge : game.track,
      border: enabled ? border : null,
      // Same depth when disabled, so enabling a button never shifts layout.
      depth: AppShadows.keyDepth,
      height: Spacing.keyHeight,
      padding: const EdgeInsets.symmetric(horizontal: Spacing.xl),
      semanticLabel: label,
      child: content,
    );
    return expand ? SizedBox(width: double.infinity, child: key) : key;
  }
}
