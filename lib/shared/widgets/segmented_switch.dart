import 'package:flutter/material.dart';

import '../../core/theme/app_spacing.dart';
import '../../core/theme/game_colors.dart';

class SegmentOption<T> {
  const SegmentOption(this.value, this.label, {this.icon});

  final T value;
  final String label;
  final IconData? icon;
}

/// Two-to-four-way switch in a recessed track; the selected option is a
/// raised key.
class SegmentedSwitch<T> extends StatelessWidget {
  const SegmentedSwitch({
    super.key,
    required this.options,
    required this.selected,
    required this.onChanged,
    this.semanticLabel,
  });

  final List<SegmentOption<T>> options;
  final T selected;
  final ValueChanged<T> onChanged;
  final String? semanticLabel;

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    final scheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    // In the timed palette the selected key takes the action color.
    final accentSelected = scheme.brightness == Brightness.dark;
    return Semantics(
      label: semanticLabel,
      container: true,
      child: Container(
        padding: const EdgeInsets.all(Spacing.xs),
        decoration: BoxDecoration(
          color: game.track,
          borderRadius: AppRadius.mdAll,
        ),
        child: Row(
          children: [
            for (final option in options)
              Expanded(
                child: _Segment(
                  label: option.label,
                  icon: option.icon,
                  isSelected: option.value == selected,
                  onTap: () => onChanged(option.value),
                  face: accentSelected ? scheme.primary : game.keyFace,
                  edge: accentSelected ? game.primaryEdge : game.keyEdge,
                  selectedText:
                      accentSelected ? game.onPrimary : scheme.onSurface,
                  idleText: game.textMuted,
                  textStyle: textTheme.titleSmall,
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _Segment extends StatelessWidget {
  const _Segment({
    required this.label,
    required this.icon,
    required this.isSelected,
    required this.onTap,
    required this.face,
    required this.edge,
    required this.selectedText,
    required this.idleText,
    required this.textStyle,
  });

  final String label;
  final IconData? icon;
  final bool isSelected;
  final VoidCallback onTap;
  final Color face;
  final Color edge;
  final Color selectedText;
  final Color idleText;
  final TextStyle? textStyle;

  @override
  Widget build(BuildContext context) {
    final color = isSelected ? selectedText : idleText;
    return Semantics(
      button: true,
      selected: isSelected,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: onTap,
        child: AnimatedContainer(
          duration: AppDurations.fast,
          height: 40,
          decoration: BoxDecoration(
            color: isSelected ? face : Colors.transparent,
            borderRadius: BorderRadius.circular(AppRadius.sm),
            boxShadow: isSelected ? AppShadows.edge(edge, depth: 2) : null,
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              if (icon != null) ...[
                Icon(icon, size: 18, color: color),
                const SizedBox(width: Spacing.xs + Spacing.xxs),
              ],
              Flexible(
                child: Text(
                  label,
                  overflow: TextOverflow.ellipsis,
                  style: textStyle?.copyWith(
                    color: color,
                    fontWeight: isSelected ? FontWeight.w800 : FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
