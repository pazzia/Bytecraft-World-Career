import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/di/providers.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';
import '../../../core/theme/game_colors.dart';

/// `m:ss` for a duration (negative durations render as 0:00).
String formatClock(Duration duration) {
  final safe = duration.isNegative ? Duration.zero : duration;
  final minutes = safe.inMinutes;
  final seconds = safe.inSeconds.remainder(60).toString().padLeft(2, '0');
  return '$minutes:$seconds';
}

/// Spoken form for screen readers: «3 мин 12 с».
String spokenClock(Duration duration) {
  final safe = duration.isNegative ? Duration.zero : duration;
  return '${safe.inMinutes} мин ${safe.inSeconds.remainder(60)} с';
}

/// Rebuilds every second with the time left until [deadline] and calls
/// [onFinished] once when it reaches zero. Time comes from [clockProvider].
class CountdownBuilder extends ConsumerStatefulWidget {
  const CountdownBuilder({
    super.key,
    required this.deadline,
    required this.builder,
    this.onFinished,
  });

  final DateTime deadline;
  final Widget Function(BuildContext context, Duration remaining) builder;
  final VoidCallback? onFinished;

  @override
  ConsumerState<CountdownBuilder> createState() => _CountdownBuilderState();
}

class _CountdownBuilderState extends ConsumerState<CountdownBuilder> {
  static const Duration _tick = Duration(seconds: 1);

  Timer? _timer;
  bool _finishedReported = false;

  @override
  void initState() {
    super.initState();
    _timer = Timer.periodic(_tick, (_) => _onTick());
  }

  @override
  void didUpdateWidget(CountdownBuilder oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.deadline != widget.deadline) _finishedReported = false;
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Duration get _remaining =>
      widget.deadline.difference(ref.read(clockProvider).now());

  void _onTick() {
    if (!mounted) return;
    setState(() {});
    if (!_finishedReported && _remaining <= Duration.zero) {
      _finishedReported = true;
      widget.onFinished?.call();
    }
  }

  @override
  Widget build(BuildContext context) {
    final remaining = _remaining;
    return widget.builder(
      context,
      remaining.isNegative ? Duration.zero : remaining,
    );
  }
}

/// Live `m:ss` countdown in monospace; turns red for the last 30 seconds.
class CountdownBadge extends StatelessWidget {
  const CountdownBadge({
    super.key,
    required this.deadline,
    this.onFinished,
    this.size = 22,
  });

  final DateTime deadline;
  final VoidCallback? onFinished;
  final double size;

  static const Duration _warning = Duration(seconds: 30);

  @override
  Widget build(BuildContext context) => CountdownBuilder(
        deadline: deadline,
        onFinished: onFinished,
        builder: (context, remaining) {
          final game = context.gameColors;
          final color = remaining <= _warning ? game.errorBright : game.streakText;
          return Semantics(
            label: 'Осталось ${spokenClock(remaining)}',
            excludeSemantics: true,
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.timer_outlined, size: size - 2, color: color),
                const SizedBox(width: Spacing.xs),
                Text(
                  formatClock(remaining),
                  style: AppTypography.code(
                    color: color,
                    size: size,
                    weight: FontWeight.w700,
                  ).copyWith(
                    height: 1.1,
                    fontFeatures: const [FontFeature.tabularFigures()],
                  ),
                ),
              ],
            ),
          );
        },
      );
}
