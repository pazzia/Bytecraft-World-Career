import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/routes.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/game_colors.dart';
import '../../../shared/widgets/app_button.dart';
import '../../../shared/widgets/app_card.dart';
import '../../../shared/widgets/app_progress_bar.dart';
import '../../../shared/widgets/async_value_view.dart';
import '../../learning_map/domain/learning_map_model.dart';
import '../../learning_map/presentation/learning_map_providers.dart';
import '../domain/career_dashboard.dart';
import 'career_providers.dart';

class CareerScreen extends ConsumerWidget {
  const CareerScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dashboard = ref.watch(careerDashboardProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Карьера')),
      body: AsyncValueView<CareerDashboard>(
        value: dashboard,
        onRetry: () => ref.invalidate(careerDashboardProvider),
        data: (vm) => ListView(
          padding: const EdgeInsets.fromLTRB(
            Spacing.page,
            Spacing.md,
            Spacing.page,
            Spacing.huge,
          ),
          children: [
            _CareerHero(vm: vm),
            const SizedBox(height: Spacing.xl),
            _SectionHeader(
              title: 'Skill Passport',
              trailing: '${vm.assessmentReadyCount} из ${vm.skills.length} готовы',
            ),
            for (final skill in vm.skills) ...[
              _SkillCard(skill: skill),
              const SizedBox(height: Spacing.md),
            ],
            const SizedBox(height: Spacing.lg),
            const _SectionHeader(title: 'Лучшие следующие шаги'),
            for (final action in vm.actions) ...[
              _ActionCard(
                action: action,
                onTap: () => context.go(Routes.map),
              ),
              const SizedBox(height: Spacing.md),
            ],
            const SizedBox(height: Spacing.lg),
            _AssessmentCard(
              onStart: () {
                ref.read(mapModeProvider.notifier).select(MapMode.timed);
                context.go(Routes.map);
              },
            ),
            const SizedBox(height: Spacing.xl),
            const _SectionHeader(title: 'Совпадение с карьерными целями'),
            for (final match in vm.roleMatches) ...[
              _RoleMatchCard(match: match),
              const SizedBox(height: Spacing.md),
            ],
            const SizedBox(height: Spacing.lg),
            _CvCard(vm: vm),
          ],
        ),
      ),
    );
  }
}

class _CareerHero extends StatelessWidget {
  const _CareerHero({required this.vm});

  final CareerDashboard vm;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final game = context.gameColors;
    return AppCard(
      color: game.board,
      borderColor: game.boardEdge,
      edgeColor: game.boardEdge,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'CAREER READINESS',
            style: theme.textTheme.labelMedium?.copyWith(
              color: game.reward,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: Spacing.sm),
          Text(
            '${vm.readiness}%',
            style: theme.textTheme.displaySmall?.copyWith(
              color: game.codeText,
              fontWeight: FontWeight.w900,
            ),
          ),
          Text(
            vm.targetTitle,
            style: theme.textTheme.titleLarge?.copyWith(color: game.codeText),
          ),
          const SizedBox(height: Spacing.lg),
          AppProgressBar(value: vm.readiness / 100, height: 10),
          const SizedBox(height: Spacing.md),
          Text(
            'Career Score ${vm.careerScore} • ${vm.completedLevels} из ${vm.totalLevels} уровней дают доказательства навыка',
            style: theme.textTheme.bodySmall?.copyWith(color: game.boardMuted),
          ),
        ],
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  const _SectionHeader({required this.title, this.trailing});

  final String title;
  final String? trailing;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: Spacing.md),
        child: Row(
          children: [
            Expanded(child: Text(title, style: Theme.of(context).textTheme.titleLarge)),
            if (trailing != null)
              Text(
                trailing!,
                style: Theme.of(context)
                    .textTheme
                    .labelMedium
                    ?.copyWith(color: context.gameColors.textMuted),
              ),
          ],
        ),
      );
}

class _SkillCard extends StatelessWidget {
  const _SkillCard({required this.skill});

  final CareerSkill skill;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final game = context.gameColors;
    final ready = skill.readyForAssessment;
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(child: Text(skill.title, style: theme.textTheme.titleMedium)),
              Text(
                '${skill.score}',
                style: theme.textTheme.titleMedium?.copyWith(
                  color: ready ? game.success : theme.colorScheme.primary,
                  fontWeight: FontWeight.w900,
                ),
              ),
            ],
          ),
          const SizedBox(height: Spacing.sm),
          AppProgressBar(value: skill.score / 100, height: 7),
          const SizedBox(height: Spacing.sm),
          Text(
            ready
                ? 'Готов к тренировочной аттестации'
                : 'Цель ${skill.target} • осталось ${skill.gap} пунктов',
            style: theme.textTheme.bodySmall?.copyWith(color: game.textMuted),
          ),
        ],
      ),
    );
  }
}

class _ActionCard extends StatelessWidget {
  const _ActionCard({required this.action, required this.onTap});

  final CareerAction action;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => AppCard(
        onTap: onTap,
        semanticLabel: action.title,
        child: Row(
          children: [
            Icon(Icons.trending_up_rounded, color: Theme.of(context).colorScheme.primary),
            const SizedBox(width: Spacing.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(action.title, style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: Spacing.xs),
                  Text(
                    action.subtitle,
                    style: Theme.of(context)
                        .textTheme
                        .bodySmall
                        ?.copyWith(color: context.gameColors.textMuted),
                  ),
                ],
              ),
            ),
            const SizedBox(width: Spacing.sm),
            Text(
              '+${action.estimatedGain}%',
              style: Theme.of(context).textTheme.labelLarge?.copyWith(
                    color: context.gameColors.success,
                    fontWeight: FontWeight.w900,
                  ),
            ),
          ],
        ),
      );
}

class _AssessmentCard extends StatelessWidget {
  const _AssessmentCard({required this.onStart});

  final VoidCallback onStart;

  @override
  Widget build(BuildContext context) => AppCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.verified_outlined, color: Theme.of(context).colorScheme.primary),
                const SizedBox(width: Spacing.sm),
                Text('Weekly Skill Check', style: Theme.of(context).textTheme.titleLarge),
              ],
            ),
            const SizedBox(height: Spacing.sm),
            Text(
              'Пройди модуль на время и проверь, насколько навык устойчив без подсказок. Защищённая Verified-аттестация будет отдельным этапом.',
              style: Theme.of(context)
                  .textTheme
                  .bodyMedium
                  ?.copyWith(color: context.gameColors.textMuted),
            ),
            const SizedBox(height: Spacing.lg),
            AppButton(
              label: 'Начать проверку',
              icon: Icons.timer_outlined,
              onPressed: onStart,
            ),
          ],
        ),
      );
}

class _RoleMatchCard extends StatelessWidget {
  const _RoleMatchCard({required this.match});

  final RoleMatch match;

  @override
  Widget build(BuildContext context) => AppCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(child: Text(match.title, style: Theme.of(context).textTheme.titleMedium)),
                Text(
                  '${match.match}%',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: Theme.of(context).colorScheme.primary,
                        fontWeight: FontWeight.w900,
                      ),
                ),
              ],
            ),
            const SizedBox(height: Spacing.sm),
            AppProgressBar(value: match.match / 100, height: 7),
          ],
        ),
      );
}

class _CvCard extends StatelessWidget {
  const _CvCard({required this.vm});

  final CareerDashboard vm;

  @override
  Widget build(BuildContext context) => AppCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('CV Readiness', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: Spacing.sm),
            Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '${vm.cvScore}',
                  style: Theme.of(context).textTheme.displaySmall?.copyWith(
                        color: Theme.of(context).colorScheme.primary,
                        fontWeight: FontWeight.w900,
                      ),
                ),
                Padding(
                  padding: const EdgeInsets.only(bottom: Spacing.sm, left: Spacing.xs),
                  child: Text('/100', style: Theme.of(context).textTheme.titleMedium),
                ),
              ],
            ),
            const SizedBox(height: Spacing.sm),
            Text(
              'Сейчас это внутренняя оценка доказательности навыков: пройденные уровни, качество и готовность по направлениям. Следующий шаг — проекты, импорт GitHub и генерация CV под конкретную вакансию.',
              style: Theme.of(context)
                  .textTheme
                  .bodySmall
                  ?.copyWith(color: context.gameColors.textMuted),
            ),
          ],
        ),
      );
}
