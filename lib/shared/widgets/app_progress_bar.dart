import 'package:flutter/material.dart';

import '../../core/theme/app_spacing.dart';
import '../../core/theme/game_colors.dart';

class AppProgressBar extends StatelessWidget {
  const AppProgressBar({
    super.key,
    required this.value,
    this.color,
    this.height = 10,
    this.glow = false,
  });

  /// 0..1
  final double value;
  final Color? color;
  final double height;

  /// Soft glow around the fill (the timed "fuse").
  final bool glow;

  @override
  Widget build(BuildContext context) {
    final clamped = value.clamp(0.0, 1.0);
    final fill = color ?? Theme.of(context).colorScheme.primary;
    final reduceMotion = MediaQuery.maybeDisableAnimationsOf(context) ?? false;
    return Semantics(
      value: '${(clamped * 100).round()}%',
      child: Container(
        height: height,
        decoration: BoxDecoration(
          color: context.gameColors.track,
          borderRadius: AppRadius.pillAll,
        ),
        alignment: Alignment.centerLeft,
        child: TweenAnimationBuilder<double>(
          tween: Tween(begin: 0, end: clamped),
          duration: reduceMotion ? Duration.zero : AppDurations.slow,
          curve: Curves.easeOutCubic,
          builder: (context, animated, _) => FractionallySizedBox(
            widthFactor: animated,
            heightFactor: 1,
            child: DecoratedBox(
              decoration: BoxDecoration(
                color: fill,
                borderRadius: AppRadius.pillAll,
                boxShadow: glow
                    ? [BoxShadow(color: fill, blurRadius: 12)]
                    : null,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

enum SegmentState { done, current, todo }

/// Progress split into equal segments (modules of a course, levels of a
/// module). The current segment is outlined.
class SegmentedProgress extends StatelessWidget {
  const SegmentedProgress({
    super.key,
    required this.segments,
    this.height = 10,
    this.semanticLabel,
  });

  final List<SegmentState> segments;
  final double height;
  final String? semanticLabel;

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    final primary = Theme.of(context).colorScheme.primary;
    return Semantics(
      label: semanticLabel,
      child: Row(
        children: [
          for (var i = 0; i < segments.length; i++) ...[
            if (i > 0) const SizedBox(width: Spacing.xs),
            Expanded(
              child: Container(
                height: height,
                decoration: BoxDecoration(
                  color: switch (segments[i]) {
                    SegmentState.done => game.success,
                    SegmentState.current => game.track,
                    SegmentState.todo => game.track,
                  },
                  borderRadius: AppRadius.pillAll,
                  border: segments[i] == SegmentState.current
                      ? Border.all(color: primary, width: 2)
                      : null,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
