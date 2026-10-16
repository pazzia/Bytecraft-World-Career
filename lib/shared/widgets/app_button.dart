import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../core/theme/app_spacing.dart';
import '../../core/theme/game_colors.dart';

enum AppButtonVariant { primary, success, danger, secondary }

/// Large, chunky game button with a solid bottom edge. Sized for thumbs.
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

  static const double _edgeDarken = 0.25;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final game = context.gameColors;
    final (Color background, Color foreground) = switch (variant) {
      AppButtonVariant.primary => (scheme.primary, scheme.onPrimary),
      AppButtonVariant.success => (game.success, AppColors.white),
      AppButtonVariant.danger => (game.error, AppColors.white),
      AppButtonVariant.secondary => (scheme.surface, scheme.onSurface),
    };
    final enabled = onPressed != null && !isLoading;
    final fill = enabled ? background : game.locked;
    final edge = variant == AppButtonVariant.secondary
        ? scheme.outline
        : Color.lerp(fill, Colors.black, _edgeDarken)!;

    final text = Text(
      label.toUpperCase(),
      textAlign: TextAlign.center,
      style: Theme.of(context).textTheme.labelLarge?.copyWith(color: foreground),
    );
    final content = isLoading
        ? SizedBox.square(
            dimension: 22,
            child: CircularProgressIndicator(strokeWidth: 3, color: foreground),
          )
        : Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (icon != null) ...[
                Icon(icon, color: foreground),
                const SizedBox(width: Spacing.sm),
              ],
              // Flexible needs bounded width; compact buttons may sit in a Row.
              if (expand) Flexible(child: text) else text,
            ],
          );

    final button = AnimatedContainer(
      duration: AppDurations.fast,
      constraints: const BoxConstraints(minHeight: Spacing.touchTarget),
      decoration: BoxDecoration(
        color: fill,
        borderRadius: AppRadius.lgAll,
        border: variant == AppButtonVariant.secondary
            ? Border.all(color: scheme.outline, width: 2)
            : null,
        boxShadow: enabled ? AppShadows.edge(edge) : null,
      ),
      child: Material(
        type: MaterialType.transparency,
        child: InkWell(
          borderRadius: AppRadius.lgAll,
          onTap: enabled ? onPressed : null,
          child: Padding(
            padding: const EdgeInsets.symmetric(
              horizontal: Spacing.xl,
              vertical: Spacing.md,
            ),
            child: Center(widthFactor: 1, child: content),
          ),
        ),
      ),
    );
    return expand ? SizedBox(width: double.infinity, child: button) : button;
  }
}
