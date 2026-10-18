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

class CareerScreen extends ConsumerWidget {
  const CareerScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) => WorldPage(
        title: 'Карьера',
        subtitle: 'Цель, учебный прогресс и следующий шаг',
        child: ref.watch(careerDashboardProvider).when(
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
                initialValue: vm.targetId,
                isExpanded: true,
                decoration: const InputDecoration(
                  labelText: 'Выбери направление',
                  border: OutlineInputBorder(),
                ),
                items: [
                  for (final target in CareerTargetId.values)
                    DropdownMenuItem(value: target, child: Text(target.title, maxLines: 1, overflow: TextOverflow.ellipsis)),
                ],
                onChanged: (target) async {
                  if (target == null) return;
                  try {
                    await ref.read(settingsControllerProvider.notifier)
                        .setCareerGoal(target.id);
                  } catch (_) {
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
                        content: Text('Не удалось сохранить цель. Повтори выбор.'),
                      ));
                    }
                  }
                },
              ),
              const SizedBox(height: 12),
              WorldPanel(child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Учебный маршрут: ${vm.readiness}%', style: _heading),
                  const SizedBox(height: 8),
                  LinearProgressIndicator(value: vm.readiness / 100),
                  const SizedBox(height: 8),
                  Text('Пройдено ${vm.completedLevels} из ${vm.totalLevels} уровней курса.', style: _body),
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
              )),
              const SizedBox(height: 12),
              WorldButton(
                label: 'Продолжить обучение',
                icon: Icons.play_arrow_rounded,
                onPressed: () async {
                  final course = await ref.read(activeCourseProvider.future);
                  final progress = await ref.read(activeCourseProgressProvider.future);
                  final mode = await ref.read(unlockModeProvider.future);
                  final next = const UnlockPolicy().nextToPlay(course, progress, mode: mode);
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
                WorldPanel(child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(skill.title, style: _heading),
                    const SizedBox(height: 8),
                    LinearProgressIndicator(value: skill.courseScore / 100),
                    const SizedBox(height: 8),
                    Text('Учебные баллы: ${skill.courseScore}/100 · ориентир: ${skill.target}', style: _body),
                    Text('Задания навыка: ${skill.completedLevels}/${skill.totalLevels}', style: _body),
                    Text(skill.completedLevels == 0
                        ? 'Пока нет пройденных уровней по этому навыку.'
                        : skill.readyForAssessment
                            ? 'Учебный ориентир достигнут. Навык предстоит подтвердить отдельной практикой.'
                            : 'Изучается в курсе. До ориентира: ${skill.gap} баллов.', style: _muted),
                  ],
                )),
                const SizedBox(height: 10),
              ],
              const SizedBox(height: 10),
              const Text('Как связан игровой прогресс', style: _heading),
              const SizedBox(height: 8),
              WorldPanel(child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Экспедиция: ${ref.watch(worldControllerProvider).value?.expeditionProgress ?? 0}/5 этапов', style: _body),
                  const SizedBox(height: 8),
                  const Text(
                    'Экспедиция даёт награды для города и открывает проект. Карта навыков учитывает уровни курса и звёзды. Покупка зданий и накопление XP не повышают учебные баллы.',
                    style: _muted,
                  ),
                ],
              )),
            ],
          ),
        ),
      );

  static const _heading = TextStyle(color: WorldPalette.text, fontSize: 18, fontWeight: FontWeight.w800);
  static const _body = TextStyle(color: WorldPalette.text);
  static const _muted = TextStyle(color: WorldPalette.muted);

  static void _explain(BuildContext context) => showModalBottomSheet<void>(
        context: context,
        backgroundColor: WorldPalette.panel,
        isScrollControlled: true,
        builder: (context) => SafeArea(child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Text('Откуда берутся баллы', style: _heading),
            const SizedBox(height: 12),
            const Text(
              'Для каждого навыка берём связанные модули курса. До 70 баллов даёт доля пройденных уровней, до 30 — доля заработанных звёзд от максимума. Повторное прохождение улучшает лучший результат, но не удваивает прогресс. Баллы округляются до целого; точное число выполненных заданий показано на карточке навыка.\n\n'
              'Общий процент — средняя доля достижения ориентиров по шести навыкам; каждый вклад ограничен 100%. Ориентиры — внутренние цели учебного маршрута.\n\n'
              'Статус «подтверждён» появится только после отдельной практической проверки. Сейчас приложение её не проводит.',
              style: _body,
            ),
            const SizedBox(height: 16),
            TextButton(onPressed: () => Navigator.pop(context), child: const Text('Понятно')),
          ]),
        )),
      );
}
