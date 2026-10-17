import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/startup/app_startup.dart';
import '../../../core/config/build_info.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';
import '../../../shared/widgets/async_value_view.dart';

/// Shown while [appStartupProvider] runs. Navigation away is handled by
/// the router redirect, not by this widget.
class SplashScreen extends ConsumerWidget {
  const SplashScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final startup = ref.watch(appStartupProvider);
    if (startup.hasError) {
      return Scaffold(
        body: SafeArea(
          child: ErrorView(
            message: '${startup.error}',
            onRetry: () => ref.invalidate(appStartupProvider),
          ),
        ),
      );
    }
    final textTheme = Theme.of(context).textTheme;
    return Scaffold(
      backgroundColor: AppColors.ink,
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 104,
              height: 104,
              margin: const EdgeInsets.only(bottom: 6),
              alignment: Alignment.center,
              decoration: BoxDecoration(
                color: AppColors.yellow,
                borderRadius: BorderRadius.circular(30),
                boxShadow: AppShadows.edge(AppColors.yellowEdge, depth: 6),
              ),
              child: Text(
                '{}',
                style: AppTypography.code(
                  color: AppColors.ink,
                  size: 40,
                  weight: FontWeight.w700,
                ),
              ),
            ),
            const SizedBox(height: Spacing.xl),
            Text(
              'Bytecraft',
              style: textTheme.headlineLarge?.copyWith(color: AppColors.white),
            ),
            const SizedBox(height: Spacing.xs),
            Text(
              'Код за пару минут в день',
              style: textTheme.bodyLarge?.copyWith(color: AppColors.nightMuted),
            ),
            const SizedBox(height: Spacing.lg),
            Text(
              'Версия ${BuildInfo.label}',
              key: const ValueKey('splash_version'),
              style: textTheme.bodySmall?.copyWith(color: AppColors.nightMuted),
            ),
          ],
        ),
      ),
    );
  }
}
