import '../../world/presentation/repair_screen.dart';
import '../domain/career_next_step.dart';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/routes.dart';
import '../../progress/domain/unlock_policy.dart';
import '../../progress/presentation/progress_providers.dart';
import '../../settings/presentation/settings_controller.dart';
import '../../world/presentation/world_controller.dart';
import '../../world/presentation/world_ui.dart';
import '../domain/career_dashboard.dart';
import 'career_providers.dart';

class CareerScreen extends ConsumerStatefulWidget {
  const CareerScreen({super.key});
  @override
  ConsumerState<CareerScreen> createState() => _CareerScreenState();
}

class _CareerScreenState extends ConsumerState<CareerScreen> {
  int _goalRevision = 0;
  bool _savingGoal = false;
  bool _startingStep = false;

  @override
  Widget build(BuildContext context) => WorldPage(
    title: 'Карьера',
    subtitle: 'Цель, учебный прогресс и следующий шаг',
    child: ref
        .watch(careerDashboardProvider)
        .when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, stack) => Center(
            child: TextButton(
              onPressed: () => ref.invalidate(careerDashboardProvider),
              child: const Text('Не удалось загрузить навыки. Повторить'),
            ),
          ),
          data: (vm) => ListView(
            padding: const EdgeInsets.all(16),
            children: [
              const Text('Карьерная цель', style: _heading),
              const SizedBox(height: 8),
              DropdownButtonFormField<CareerTargetId>(
                key: ValueKey(_goalRevision),
                initialValue: vm.targetId,
                isExpanded: true,
                decoration: const InputDecoration(
                  labelText: 'Выбери направление',
                  border: OutlineInputBorder(),
                ),
                items: [
                  for (final target in CareerTargetId.values)
                    DropdownMenuItem(
                      value: target,
                      child: Text(
                        target.title,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                ],
                onChanged: _savingGoal
                    ? null
                    : (target) async {
                        if (target == null) return;
                        setState(() => _savingGoal = true);
                        try {
                          await ref
                              .read(settingsControllerProvider.notifier)
                              .setCareerGoal(target.id);
                        } catch (_) {
                          if (mounted) setState(() => _goalRevision++);
                          if (context.mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text(
                                  'Не удалось сохранить цель. Повтори выбор.',
                                ),
                              ),
                            );
                          }
                        } finally {
                          if (mounted) setState(() => _savingGoal = false);
                        }
                      },
              ),
              const SizedBox(height: 12),
              WorldPanel(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Учебный маршрут: ${vm.readiness}%', style: _heading),
                    const SizedBox(height: 8),
                    LinearProgressIndicator(value: vm.readiness / 100),
                    const SizedBox(height: 8),
                    Text(
                      'Пройдено ${vm.completedLevels} из ${vm.totalLevels} уровней курса.',
                      style: _body,
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Процент показывает долю учебных ориентиров выбранной цели. Это не оценка готовности к трудоустройству. Смена цели меняет ориентиры, сохраняя пройденные уровни.',
                      style: _muted,
                    ),
                    TextButton.icon(
                      onPressed: () => _explain(context),
                      icon: const Icon(Icons.help_outline),
                      label: const Text('Как считается прогресс?'),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),
              WorldButton(
                label: 'Продолжить обучение',
                icon: Icons.play_arrow_rounded,
                onPressed: () async {
                  final course = await ref.read(activeCourseProvider.future);
                  final progress = await ref.read(
                    activeCourseProgressProvider.future,
                  );
                  final mode = await ref.read(unlockModeProvider.future);
                  final next = const UnlockPolicy().nextToPlay(
                    course,
                    progress,
                    mode: mode,
                  );
                  if (!context.mounted) return;
                  if (next == null) {
                    context.go(Routes.map);
                  } else {
                    context.push(Routes.level(course.id, next.id));
                  }
                },
              ),
              const SizedBox(height: 20),
              const Text('Карта навыков', style: _heading),
              const SizedBox(height: 8),
              for (final skill in vm.skills) ...[
                WorldPanel(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(skill.title, style: _heading),
                      const SizedBox(height: 8),
                      LinearProgressIndicator(value: skill.courseScore / 100),
                      const SizedBox(height: 8),
                      Text(
                        'Учебные баллы: ${skill.courseScore}/100 · ориентир: ${skill.target}',
                        style: _body,
                      ),
                      Text(
                        'Задания навыка: ${skill.completedLevels}/${skill.totalLevels}',
                        style: _body,
                      ),
                      const SizedBox(height: 8),
                      Text(skill.evidence.status, style: _heading),
                      Text(
                        'Изучено: ${skill.evidence.studied.length} уровней · '
                        'отработано: ${skill.evidence.practiced.length} задач · '
                        'подтверждено: ${skill.evidence.confirmed.length} подтем',
                        style: _body,
                      ),
                      if (skill.evidence.pending.isNotEmpty)
                        Text(
                          'Требуют закрепления: ${skill.evidence.pending.length} подтем. '
                          'Предыдущие решения сохранены.',
                          style: _muted,
                        ),
                      const Text(
                        'Подтверждение относится к указанной подтеме, а не ко всему навыку.',
                        style: _muted,
                      ),
                      ExpansionTile(
                        key: ValueKey('evidence_${skill.id.name}'),
                        title: const Text(
                          'Выполненная работа и проверки',
                          style: _body,
                        ),
                        tilePadding: EdgeInsets.zero,
                        children: [
                          for (final title in skill.evidence.studied)
                            ListTile(
                              title: Text('Изучено: $title', style: _body),
                            ),
                          for (final title in skill.evidence.practiced)
                            ListTile(
                              title: Text('Отработано: $title', style: _body),
                              subtitle: const Text(
                                'Программа прошла проверки.',
                                style: _muted,
                              ),
                            ),
                          for (final repair in skill.evidence.confirmed)
                            ListTile(
                              title: Text(
                                'Подтверждено: ${repair.title}',
                                style: _body,
                              ),
                              subtitle: Text(
                                'Другой пример решён самостоятельно · ${_proofDate(repair.proofs.last['verifiedAt'])}',
                                style: _muted,
                              ),
                            ),
                          for (final repair in skill.evidence.pending)
                            ListTile(
                              title: Text(
                                'Закрепить: ${repair.title}',
                                style: _body,
                              ),
                              subtitle: const Text(
                                'Нужна новая самостоятельная проверка.',
                                style: _muted,
                              ),
                            ),
                          if (skill.evidence.studied.isEmpty &&
                              skill.evidence.practiced.isEmpty &&
                              skill.evidence.confirmed.isEmpty &&
                              skill.evidence.pending.isEmpty)
                            const Text(
                              'Начни со следующего шага на этой карточке.',
                              style: _muted,
                            ),
                        ],
                      ),
                      if (skill.nextStep != null) ...[
                        Text(skill.nextStep!.reason, style: _muted),
                        TextButton(
                          key: ValueKey('next_${skill.id.name}'),
                          onPressed: _startingStep
                              ? null
                              : () => _runNext(context, skill.nextStep!),
                          child: Text(skill.nextStep!.label),
                        ),
                      ] else
                        const Text(
                          'Все доступные работы этого навыка выполнены. Новые проверки появятся с расширением курса.',
                          style: _muted,
                        ),
                    ],
                  ),
                ),
                const SizedBox(height: 10),
              ],
              const SizedBox(height: 10),
              const Text('Как связан игровой прогресс', style: _heading),
              const SizedBox(height: 8),
              WorldPanel(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Экспедиция: ${ref.watch(worldControllerProvider).value?.expeditionProgress ?? 0}/5 этапов',
                      style: _body,
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Экспедиция даёт награды для города и открывает проект. Карта навыков показывает уровни курса, задачи с проверками и самостоятельные решения по подтемам. Покупка зданий и накопление XP не повышают учебные баллы.',
                      style: _muted,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
  );

  Future<void> _runNext(BuildContext context, CareerNextStep step) async {
    setState(() => _startingStep = true);
    try {
      if (step.kind == CareerStepKind.assessment) {
        await ref.read(repairServiceProvider).beginAssessment(step.id);
        if (!context.mounted) return;
        await Navigator.of(context).push(
          MaterialPageRoute<void>(
            builder: (_) => RepairScreen(skillId: step.id),
          ),
        );
      } else {
        final course = await ref.read(activeCourseProvider.future);
        if (!context.mounted) return;
        final route = switch (step.kind) {
          CareerStepKind.course => Routes.level(course.id, step.id),
          CareerStepKind.practice => Routes.practiceTask(step.id),
          CareerStepKind.project => Routes.worldBuild,
          CareerStepKind.expedition => Routes.worldExpedition,
          CareerStepKind.assessment => throw StateError(
            'Unexpected assessment',
          ),
        };
        await context.push(route);
      }
    } catch (_) {
      if (context.mounted)
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Не удалось открыть следующий шаг. Повтори попытку.'),
          ),
        );
    } finally {
      if (mounted) setState(() => _startingStep = false);
    }
  }

  static String _proofDate(String? value) {
    final date = DateTime.tryParse(value ?? '')?.toLocal();
    if (date == null) return 'дата недоступна';
    String two(int n) => n.toString().padLeft(2, '0');
    return '${two(date.day)}.${two(date.month)}.${date.year}';
  }

  static const _heading = TextStyle(
    color: WorldPalette.text,
    fontSize: 18,
    fontWeight: FontWeight.w800,
  );
  static const _body = TextStyle(color: WorldPalette.text);
  static const _muted = TextStyle(color: WorldPalette.muted);

  static void _explain(BuildContext context) => showModalBottomSheet<void>(
    context: context,
    backgroundColor: WorldPalette.panel,
    isScrollControlled: true,
    builder: (context) => SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Откуда берутся баллы', style: _heading),
            const SizedBox(height: 12),
            const Text(
              'Для каждого навыка берём связанные модули курса. До 70 баллов даёт доля пройденных уровней, до 30 — доля заработанных звёзд от максимума. Повторное прохождение улучшает лучший результат, но не удваивает прогресс. Баллы округляются до целого; точное число выполненных заданий показано на карточке навыка.\n\n'
              'Общий процент — средняя доля достижения ориентиров по шести навыкам; каждый вклад ограничен 100%. Ориентиры — внутренние цели учебного маршрута.\n\n'
              '«Изучено» — пройденный уровень курса. «Отработано» — программа прошла проверки задачи или все 14 проверок калькулятора. «Подтверждено» — новый пример конкретной подтемы решён без предварительного разбора; результат и дата сохранены. Проверку можно начать после изучения, даже если ошибок не было. Новая ошибка по той же подтеме возвращает её в закрепление, сохраняя историю.\n\nПодтверждение одной подтемы не означает освоение всего навыка. Покупки, XP и смена цели не дают подтверждений. Это учебные результаты, не профессиональная аттестация.',
              style: _body,
            ),
            const SizedBox(height: 16),
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Понятно'),
            ),
          ],
        ),
      ),
    ),
  );
}
