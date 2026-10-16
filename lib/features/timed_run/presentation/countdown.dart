import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/di/providers.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/game_colors.dart';

/// `m:ss` for a duration (negative durations render as 0:00).
String formatClock(Duration duration) {
  final safe = duration.isNegative ? Duration.zero : duration;
  final minutes = safe.inMinutes;
  final seconds = safe.inSeconds.remainder(60).toString().padLeft(2, '0');
  return '$minutes:$seconds';
}

/// Live countdown to [deadline]. Calls [onFinished] once when it hits zero.
class CountdownBadge extends ConsumerStatefulWidget {
  const CountdownBadge({super.key, required this.deadline, this.onFinished});

  final DateTime deadline;
  final VoidCallback? onFinished;

  @override
  ConsumerState<CountdownBadge> createState() => _CountdownBadgeState();
}

class _CountdownBadgeState extends ConsumerState<CountdownBadge> {
  static const Duration _tick = Duration(seconds: 1);
  static const Duration _warning = Duration(seconds: 30);

  Timer? _timer;
  bool _finishedReported = false;

  @override
  void initState() {
    super.initState();
    _timer = Timer.periodic(_tick, (_) => _onTick());
  }

  @override
  void didUpdateWidget(CountdownBadge oldWidget) {
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
    final game = context.gameColors;
    final remaining = _remaining;
    final urgent = remaining <= _warning;
    final color = urgent ? game.error : game.streak;
    return Semantics(
      label: 'Осталось ${formatClock(remaining)}',
      child: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: Spacing.md,
          vertical: Spacing.xs + Spacing.xxs,
        ),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.14),
          borderRadius: AppRadius.pillAll,
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.timer_outlined, size: 18, color: color),
            const SizedBox(width: Spacing.xs),
            Text(
              formatClock(remaining),
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    color: color,
                    fontWeight: FontWeight.w800,
                    fontFeatures: const [FontFeature.tabularFigures()],
                  ),
            ),
          ],
        ),
      ),
    );
  }
}
