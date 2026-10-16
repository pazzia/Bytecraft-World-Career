import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/startup/app_startup.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../shared/widgets/async_value_view.dart';

/// Shown while [appStartupProvider] runs. Navigation away is handled by
/// the router redirect, not by this widget.
class SplashScreen extends ConsumerWidget {
  const SplashScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final startup = ref.watch(appStartupProvider);
    final scheme = Theme.of(context).colorScheme;
    return Scaffold(
      backgroundColor: scheme.primary,
      body: SafeArea(
        child: startup.hasError
            ? ColoredBox(
                color: scheme.surface,
                child: ErrorView(
                  message: '${startup.error}',
                  onRetry: () => ref.invalidate(appStartupProvider),
                ),
              )
            : Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const _Logo(),
                    const SizedBox(height: Spacing.xl),
                    SizedBox.square(
                      dimension: 28,
                      child: CircularProgressIndicator(
                        strokeWidth: 3,
                        color: scheme.onPrimary,
                      ),
                    ),
                  ],
                ),
              ),
      ),
    );
  }
}

class _Logo extends StatelessWidget {
  const _Logo();

  @override
  Widget build(BuildContext context) {
    final onPrimary = Theme.of(context).colorScheme.onPrimary;
    return Column(
      children: [
        Container(
          width: 96,
          height: 96,
          decoration: BoxDecoration(
            color: onPrimary,
            borderRadius: AppRadius.xlAll,
          ),
          alignment: Alignment.center,
          child: Text(
            '{ }',
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  color: Theme.of(context).colorScheme.primary,
                ),
          ),
        ),
        const SizedBox(height: Spacing.lg),
        Text(
          'Bytecraft',
          style: Theme.of(context)
              .textTheme
              .headlineMedium
              ?.copyWith(color: onPrimary),
        ),
        const SizedBox(height: Spacing.xs),
        Text(
          'Код за 2 минуты в день',
          style: TextStyle(color: onPrimary.withValues(alpha: 0.8)),
        ),
      ],
    );
  }
}
