import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/theme/app_spacing.dart';
import '../../core/theme/game_colors.dart';
import 'app_button.dart';

/// Standard loading / error / data rendering for [AsyncValue].
class AsyncValueView<T> extends StatelessWidget {
  const AsyncValueView({
    super.key,
    required this.value,
    required this.data,
    this.onRetry,
  });

  final AsyncValue<T> value;
  final Widget Function(T data) data;
  final VoidCallback? onRetry;

  @override
  Widget build(BuildContext context) => value.when(
        // Keep showing the previous data while a dependency reloads
        // (e.g. after finishing a level) instead of flashing a spinner.
        skipLoadingOnReload: true,
        data: data,
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => ErrorView(message: '$error', onRetry: onRetry),
      );
}

class ErrorView extends StatelessWidget {
  const ErrorView({super.key, required this.message, this.onRetry});

  final String message;
  final VoidCallback? onRetry;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(Spacing.xxl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.error_outline_rounded,
              size: 48,
              color: context.gameColors.error,
            ),
            const SizedBox(height: Spacing.md),
            Text('Не удалось загрузить', style: textTheme.titleMedium),
            const SizedBox(height: Spacing.sm),
            Text(
              message,
              textAlign: TextAlign.center,
              style: textTheme.bodyMedium
                  ?.copyWith(color: context.gameColors.textMuted),
            ),
            if (onRetry != null) ...[
              const SizedBox(height: Spacing.lg),
              AppButton(
                label: 'Повторить',
                expand: false,
                variant: AppButtonVariant.secondary,
                onPressed: onRetry,
              ),
            ],
          ],
        ),
      ),
    );
  }
}
