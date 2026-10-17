import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/game_colors.dart';
import '../../../shared/widgets/app_button.dart';
import '../../../shared/widgets/app_card.dart';
import '../../../shared/widgets/app_progress_bar.dart';
import '../../settings/presentation/settings_controller.dart';
import '../domain/career_dashboard.dart';
import '../domain/cv_draft_builder.dart';
import '../domain/github_portfolio.dart';
import '../domain/vacancy_match.dart';
import 'career_providers.dart';

class CareerEvidenceSection extends ConsumerStatefulWidget {
  const CareerEvidenceSection({required this.vm, super.key});

  final CareerDashboard vm;

  @override
  ConsumerState<CareerEvidenceSection> createState() =>
      _CareerEvidenceSectionState();
}

class _CareerEvidenceSectionState extends ConsumerState<CareerEvidenceSection> {
  final _vacancyController = TextEditingController();
  VacancyMatchReport? _vacancyReport;

  @override
  void dispose() {
    _vacancyController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _GitHubCard(
            portfolio: widget.vm.portfolio,
            portfolioScore: widget.vm.portfolioScore,
            onEdit: () => unawaited(_editGitHub()),
          ),
          const SizedBox(height: Spacing.xl),
          _VacancyCard(
            controller: _vacancyController,
            report: _vacancyReport,
            onAnalyze: _analyzeVacancy,
          ),
          const SizedBox(height: Spacing.xl),
          _CvDraftCard(
            vm: widget.vm,
            onOpen: () => unawaited(_showCvDraft()),
          ),
        ],
      );

  Future<void> _editGitHub() async {
    final controller = TextEditingController(text: widget.vm.portfolio.username);
    final username = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('GitHub-портфолио'),
        content: TextField(
          controller: controller,
          autofocus: true,
          autocorrect: false,
          textInputAction: TextInputAction.done,
          decoration: const InputDecoration(
            labelText: 'Username',
            hintText: 'octocat',
            prefixText: '@',
          ),
          onSubmitted: (value) => Navigator.of(context).pop(value),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Отмена'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(context).pop(controller.text),
            child: const Text('Подключить'),
          ),
        ],
      ),
    );
    controller.dispose();
    if (username == null || !mounted) return;
    await ref.read(settingsControllerProvider.notifier).setGitHubUsername(username);
    ref.invalidate(githubPortfolioProvider);
    ref.invalidate(careerDashboardProvider);
  }

  void _analyzeVacancy() {
    setState(() {
      _vacancyReport = const VacancyMatcher().analyze(
        _vacancyController.text,
        widget.vm.skills,
      );
    });
  }

  Future<void> _showCvDraft() async {
    final draft = const CvDraftBuilder().build(widget.vm);
    await showDialog<void>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Черновик CV'),
        content: SizedBox(
          width: 520,
          child: SingleChildScrollView(child: SelectableText(draft)),
        ),
        actions: [
          TextButton(
            onPressed: () {
              unawaited(Clipboard.setData(ClipboardData(text: draft)));
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Черновик CV скопирован')),
              );
            },
            child: const Text('Копировать'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(dialogContext).pop(),
            child: const Text('Готово'),
          ),
        ],
      ),
    );
  }
}

class _GitHubCard extends StatelessWidget {
  const _GitHubCard({
    required this.portfolio,
    required this.portfolioScore,
    required this.onEdit,
  });

  final GitHubPortfolio portfolio;
  final int portfolioScore;
  final VoidCallback onEdit;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final muted = context.gameColors.textMuted;
    final connected = portfolio.connected;
    final title = switch (portfolio.status) {
      GitHubPortfolioStatus.disconnected => 'Подключи GitHub-портфолио',
      GitHubPortfolioStatus.connected => '@${portfolio.username}',
      GitHubPortfolioStatus.unavailable => 'GitHub: @${portfolio.username}',
    };

    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.code_rounded, color: theme.colorScheme.primary),
              const SizedBox(width: Spacing.sm),
              Expanded(child: Text(title, style: theme.textTheme.titleLarge)),
              if (connected)
                Text(
                  '$portfolioScore/100',
                  style: theme.textTheme.titleMedium?.copyWith(
                    color: theme.colorScheme.primary,
                    fontWeight: FontWeight.w900,
                  ),
                ),
            ],
          ),
          const SizedBox(height: Spacing.sm),
          if (portfolio.status == GitHubPortfolioStatus.disconnected)
            Text(
              'Bytecraft проверит публичные репозитории и добавит небольшой proof-бонус за реальные Python-проекты, тесты, CI и Docker. Приватные репозитории не читаются.',
              style: theme.textTheme.bodyMedium?.copyWith(color: muted),
            )
          else if (portfolio.status == GitHubPortfolioStatus.unavailable)
            Text(
              portfolio.message ?? 'GitHub сейчас недоступен.',
              style: theme.textTheme.bodyMedium?.copyWith(color: muted),
            )
          else ...[
            AppProgressBar(value: portfolioScore / 100, height: 7),
            const SizedBox(height: Spacing.sm),
            Text(
              '${portfolio.projectCount} публичных проектов учтено. GitHub подтверждает навык, но не заменяет прохождение курса.',
              style: theme.textTheme.bodySmall?.copyWith(color: muted),
            ),
            if (portfolio.projects.isNotEmpty) ...[
              const SizedBox(height: Spacing.md),
              for (final project in portfolio.projects.take(4))
                Padding(
                  padding: const EdgeInsets.only(bottom: Spacing.xs),
                  child: Text(
                    '• ${_projectSummary(project)}',
                    style: theme.textTheme.bodySmall,
                  ),
                ),
            ],
          ],
          const SizedBox(height: Spacing.lg),
          AppButton(
            label: connected ? 'Сменить GitHub' : 'Подключить GitHub',
            icon: Icons.link_rounded,
            onPressed: onEdit,
          ),
        ],
      ),
    );
  }

  String _projectSummary(GitHubProjectEvidence project) {
    final signals = <String>[
      if (project.primaryLanguage.isNotEmpty) project.primaryLanguage,
      if (project.hasTests) 'tests',
      if (project.hasCi) 'CI',
      if (project.hasDocker) 'Docker',
    ];
    return signals.isEmpty
        ? project.name
        : '${project.name} · ${signals.join(' · ')}';
  }
}

class _VacancyCard extends StatelessWidget {
  const _VacancyCard({
    required this.controller,
    required this.report,
    required this.onAnalyze,
  });

  final TextEditingController controller;
  final VacancyMatchReport? report;
  final VoidCallback onAnalyze;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final muted = context.gameColors.textMuted;
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Vacancy Match', style: theme.textTheme.titleLarge),
          const SizedBox(height: Spacing.sm),
          Text(
            'Вставь требования вакансии. Анализ выполняется локально: Bytecraft найдёт технические требования и сопоставит их с Skill Passport.',
            style: theme.textTheme.bodySmall?.copyWith(color: muted),
          ),
          const SizedBox(height: Spacing.md),
          TextField(
            controller: controller,
            minLines: 3,
            maxLines: 6,
            decoration: const InputDecoration(
              hintText: 'Python, FastAPI, PostgreSQL, Docker, pytest, asyncio…',
              labelText: 'Текст вакансии',
            ),
          ),
          const SizedBox(height: Spacing.md),
          AppButton(
            label: 'Проверить совпадение',
            icon: Icons.work_outline_rounded,
            onPressed: onAnalyze,
          ),
          if (report != null) ...[
            const SizedBox(height: Spacing.lg),
            if (!report!.hasRequirements)
              Text(
                'Не нашёл знакомых технических требований. Вставь более полный текст вакансии.',
                style: theme.textTheme.bodySmall?.copyWith(color: muted),
              )
            else ...[
              Row(
                children: [
                  Expanded(
                    child: Text('Совпадение', style: theme.textTheme.titleMedium),
                  ),
                  Text(
                    '${report!.match}%',
                    style: theme.textTheme.titleLarge?.copyWith(
                      color: theme.colorScheme.primary,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: Spacing.sm),
              AppProgressBar(value: report!.match / 100, height: 7),
              const SizedBox(height: Spacing.md),
              for (final requirement in report!.requirements)
                Padding(
                  padding: const EdgeInsets.only(bottom: Spacing.xs),
                  child: Text(
                    '${requirement.label}: ${requirement.score}/100',
                    style: theme.textTheme.bodySmall,
                  ),
                ),
              if (report!.gaps.isNotEmpty) ...[
                const SizedBox(height: Spacing.sm),
                Text(
                  'Главный gap: ${report!.gaps.first.label} (${report!.gaps.first.score}/100)',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: context.gameColors.warning,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ],
            ],
          ],
        ],
      ),
    );
  }
}

class _CvDraftCard extends StatelessWidget {
  const _CvDraftCard({required this.vm, required this.onOpen});

  final CareerDashboard vm;
  final VoidCallback onOpen;

  @override
  Widget build(BuildContext context) => AppCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Evidence CV', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: Spacing.sm),
            Text(
              'Собери черновик резюме из подтверждённых навыков Bytecraft и публичных GitHub-проектов. Это не заменяет опыт работы — он добавляется вручную.',
              style: Theme.of(context)
                  .textTheme
                  .bodySmall
                  ?.copyWith(color: context.gameColors.textMuted),
            ),
            const SizedBox(height: Spacing.lg),
            AppButton(
              label: 'Сформировать черновик CV',
              icon: Icons.description_outlined,
              onPressed: onOpen,
            ),
          ],
        ),
      );
}
