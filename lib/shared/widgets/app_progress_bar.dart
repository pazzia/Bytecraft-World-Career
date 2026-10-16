import 'package:flutter/material.dart';

import '../../core/theme/app_spacing.dart';
import '../../core/theme/game_colors.dart';

class AppProgressBar extends StatelessWidget {
  const AppProgressBar({
    super.key,
    required this.value,
    this.color,
    this.height = 14,
  });

  /// 0..1
  final double value;
  final Color? color;
  final double height;

  @override
  Widget build(BuildContext context) {
    final clamped = value.clamp(0.0, 1.0);
    return ClipRRect(
      borderRadius: AppRadius.pillAll,
      child: SizedBox(
        height: height,
        child: Stack(
          children: [
            Positioned.fill(
              child: ColoredBox(color: context.gameColors.locked),
            ),
            TweenAnimationBuilder<double>(
              tween: Tween(begin: 0, end: clamped),
              duration: AppDurations.slow,
              curve: Curves.easeOutCubic,
              builder: (context, animated, _) => FractionallySizedBox(
                widthFactor: animated,
                heightFactor: 1,
                child: DecoratedBox(
                  decoration: BoxDecoration(
                    color: color ?? Theme.of(context).colorScheme.primary,
                    borderRadius: AppRadius.pillAll,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
