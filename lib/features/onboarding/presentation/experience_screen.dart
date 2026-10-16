import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/routes.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';
import '../../../core/theme/game_colors.dart';
import '../../../shared/widgets/app_button.dart';
import '../../../shared/widgets/code_block.dart';
import '../../../shared/widgets/keycap.dart';
import '../../settings/domain/app_settings.dart';

/// Onboarding step 1: self-assessed experience.
class ExperienceScreen extends StatefulWidget {
  const ExperienceScreen({super.key});

  @override
  State<ExperienceScreen> createState() => _ExperienceScreenState();
}

class _ExperienceScreenState extends State<ExperienceScreen> {
  ExperienceLevel? _selected;

  static const Map<ExperienceLevel, (String, String)> _options = {
    ExperienceLevel.beginner: (
      'Никогда не программировал',
      'Начнём с самых основ',
    ),
    ExperienceLevel.someExperience: (
      'Немного знаю',
      'Освежим базу и пойдём дальше',
    ),
    ExperienceLevel.developer: (
      'Уже программирую',
      'Все модули открыты сразу',
    ),
  };

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: ListView(
                padding: const EdgeInsets.fromLTRB(
                  Spacing.page,
                  Spacing.xxxl,
                  Spacing.page,
                  Spacing.lg,
                ),
                children: [
                  const _HelloBoard(),
                  const SizedBox(height: Spacing.xxl),
                  Text('Код за пару минут в день', style: textTheme.headlineLarge),
                  const SizedBox(height: Spacing.sm),
                  Text(
                    'Короткие головоломки на Python. Сначала скажите, с чего начнём.',
                    style: textTheme.bodyLarge?.copyWith(color: game.textMuted),
                  ),
                  const SizedBox(height: Spacing.xxl),
                  for (final entry in _options.entries)
                    Padding(
                      padding: const EdgeInsets.only(bottom: Spacing.md),
                      child: _ExperienceOption(
                        title: entry.value.$1,
                        subtitle: entry.value.$2,
                        selected: _selected == entry.key,
                        onTap: () => setState(() => _selected = entry.key),
                      ),
                    ),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(
                Spacing.page,
                Spacing.sm,
                Spacing.page,
                Spacing.lg,
              ),
              child: AppButton(
                label: 'Дальше',
                onPressed: _selected == null
                    ? null
                    : () => context.push(Routes.onboardingCourseFor(_selected!.id)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _HelloBoard extends StatelessWidget {
  const _HelloBoard();

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    Widget key(String label, {bool lit = false}) => Padding(
          padding: const EdgeInsets.only(right: Spacing.sm),
          child: Keycap(
            face: lit ? game.reward : const Color(0xFFF4F7FB),
            edge: lit ? game.rewardEdge : const Color(0xFF8FA1B8),
            radius: 10,
            depth: 3,
            haptic: false,
            padding: const EdgeInsets.symmetric(
              horizontal: Spacing.md,
              vertical: Spacing.sm,
            ),
            child: Text(
              label,
              style: AppTypography.code(
                color: game.onReward,
                size: 16,
                weight: FontWeight.w700,
              ).copyWith(height: 1.2),
            ),
          ),
        );
    return ExcludeSemantics(
      child: CodeBoard(
        padding: const EdgeInsets.all(Spacing.xl),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text.rich(
              TextSpan(children: highlightPython('print("Привет!")', game)),
              style: AppTypography.code(color: game.codeText, size: 20),
            ),
            const SizedBox(height: Spacing.lg),
            Row(
              children: [
                key('print', lit: true),
                key('for'),
                key('if'),
                key('=='),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _ExperienceOption extends StatelessWidget {
  const _ExperienceOption({
    required this.title,
    required this.subtitle,
    required this.selected,
    required this.onTap,
  });

  final String title;
  final String subtitle;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final game = context.gameColors;
    final scheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    return Keycap(
      onTap: onTap,
      selected: selected,
      semanticLabel: '$title. $subtitle',
      face: selected ? game.primaryTint : game.keyFace,
      edge: selected ? game.primaryEdge : game.keyEdge,
      border: selected ? scheme.primary : game.keyBorder,
      radius: 18,
      padding: const EdgeInsets.symmetric(
        horizontal: Spacing.lg,
        vertical: Spacing.md + Spacing.xxs,
      ),
      alignment: AlignmentDirectional.centerStart,
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: textTheme.titleMedium),
                const SizedBox(height: Spacing.xxs),
                Text(
                  subtitle,
                  style: textTheme.bodyMedium?.copyWith(color: game.textMuted),
                ),
              ],
            ),
          ),
          if (selected)
            Container(
              width: 28,
              height: 28,
              decoration: BoxDecoration(
                color: scheme.primary,
                borderRadius: BorderRadius.circular(9),
              ),
              child: Icon(Icons.check_rounded, size: 20, color: game.onPrimary),
            ),
        ],
      ),
    );
  }
}
