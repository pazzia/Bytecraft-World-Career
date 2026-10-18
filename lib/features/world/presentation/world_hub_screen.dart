import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/routes.dart';
import '../domain/world_state.dart';
import 'world_controller.dart';
import 'world_ui.dart';

class WorldHubScreen extends ConsumerWidget {
  const WorldHubScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(worldControllerProvider);
    return Scaffold(
      backgroundColor: WorldPalette.bg,
      body: SafeArea(
        child: state.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, stack) => Center(
            child: Text('$error', style: const TextStyle(color: Colors.white)),
          ),
          data: (world) => RefreshIndicator(
            onRefresh: () async => ref.invalidate(worldControllerProvider),
            child: ListView(
              padding: const EdgeInsets.fromLTRB(16, 14, 16, 110),
              children: [
                _TopBar(world: world),
                if (world.showMigrationNotice) ...[
                  const SizedBox(height: 12),
                  WorldPanel(
                    child: Column(
                      children: [
                        const Text(
                          'Обновлены правила: старые квесты и рекорды засчитывались без проверки. Их нужно пройти заново; игровой XP и серия начаты с нуля. Прогресс курса, монеты, алмазы и здания сохранены (уровни зданий ограничены 5).',
                          style: TextStyle(color: WorldPalette.text),
                        ),
                        TextButton(
                          onPressed: () async {
                            await ref
                                .read(worldControllerProvider.notifier)
                                .dismissMigrationNotice();
                          },
                          child: const Text('Понятно'),
                        ),
                      ],
                    ),
                  ),
                ],
                const SizedBox(height: 18),
                Text(
                  'BYTECRAFT WORLD',
                  style: TextStyle(
                    color: WorldPalette.cyan.withValues(alpha: .9),
                    letterSpacing: 2.2,
                    fontSize: 11,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 5),
                const Text(
                  'Учись. Пиши. Строй. Соревнуйся.',
                  style: TextStyle(
                    color: WorldPalette.text,
                    fontSize: 24,
                    fontWeight: FontWeight.w900,
                    height: 1.1,
                  ),
                ),
                const SizedBox(height: 6),
                const Text(
                  'Цель: восстановить API → собрать калькулятор → победить Bug Lord. Только верные ответы открывают этапы. XP открывает улучшения города; монеты оплачивают их. Ошибки попадают в тренировки.',
                  style: TextStyle(color: WorldPalette.muted, fontSize: 13),
                ),
                const SizedBox(height: 18),
                WorldPanel(
                  glow: WorldPalette.purple,
                  onTap: () => context.push(Routes.worldCity),
                  padding: EdgeInsets.zero,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      AspectRatio(
                        aspectRatio: 1,
                        child: Stack(
                          children: [
                            Positioned.fill(
                              child: WorldCityScene(levels: world.cityLevels),
                            ),
                            const Positioned(
                              left: 16,
                              top: 14,
                              child: _OverlayLabel(
                                icon: Icons.apartment_rounded,
                                text: 'CODE CITY',
                              ),
                            ),
                            Positioned(
                              right: 14,
                              top: 14,
                              child: Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 10,
                                  vertical: 6,
                                ),
                                decoration: BoxDecoration(
                                  color: const Color(0xCC08111F),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: Text(
                                  '${world.cityLevels.values.reduce((a, b) => a + b)} ур.',
                                  style: const TextStyle(
                                    color: WorldPalette.gold,
                                    fontWeight: FontWeight.w900,
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const Padding(
                        padding: EdgeInsets.fromLTRB(16, 14, 16, 3),
                        child: Text(
                          'Твоя IT-компания растёт вместе с навыками',
                          style: TextStyle(
                            color: WorldPalette.text,
                            fontSize: 16,
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                      ),
                      const Padding(
                        padding: EdgeInsets.fromLTRB(16, 0, 16, 16),
                        child: Text(
                          'Прокачивай офис, Python Lab, R&D и серверную за награды из обучения.',
                          style: TextStyle(
                            color: WorldPalette.muted,
                            fontSize: 12,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 20),
                const SectionTitle('Твой прогресс'),
                _TodayGrid(world: world),
                const SizedBox(height: 20),
                const SectionTitle('Игровые режимы'),
                _FeatureTile(
                  number: '01',
                  title: 'Экспедиция · восстановить API',
                  subtitle:
                      '${world.expeditionProgress}/5 задач · сундук в конце',
                  icon: Icons.explore_rounded,
                  color: WorldPalette.green,
                  onTap: () => context.push(Routes.worldExpedition),
                ),
                _FeatureTile(
                  number: '02',
                  title: 'Boss Fight',
                  subtitle: world.bossCleared
                      ? 'Bug Lord побеждён ✓'
                      : 'Bug Lord · HP ${world.bossHp}%',
                  icon: Icons.smart_toy_rounded,
                  color: WorldPalette.red,
                  onTap: () => context.push(Routes.worldBoss),
                ),
                _FeatureTile(
                  number: '03',
                  title: 'Забег на время',
                  subtitle: 'Реши задачу и установи личный рекорд',
                  icon: Icons.bolt_rounded,
                  color: WorldPalette.violet,
                  onTap: () => context.push(Routes.worldGhost),
                ),
                _FeatureTile(
                  number: '04',
                  title: 'Учебная команда',
                  subtitle: '${world.guildTotal}/160 · локальный проект',
                  icon: Icons.groups_rounded,
                  color: WorldPalette.blue,
                  onTap: () => context.push(Routes.worldGuild),
                ),
                _FeatureTile(
                  number: '05',
                  title: 'Учебный соперник · Kai',
                  subtitle: '${world.rivalWins} побед за проверенные ответы',
                  icon: Icons.psychology_alt_rounded,
                  color: WorldPalette.cyan,
                  onTap: () => context.push(Routes.worldRival),
                ),
                _FeatureTile(
                  number: '06',
                  title: 'Mistake DNA',
                  subtitle: 'Тренировка строится из твоих реальных ошибок',
                  icon: Icons.donut_large_rounded,
                  color: WorldPalette.orange,
                  onTap: () => context.push(Routes.worldMistakes),
                ),
                _FeatureTile(
                  number: '07',
                  title: 'Build to Unlock',
                  subtitle:
                      '${world.completedProjectSteps}/4 шагов проекта выполнено',
                  icon: Icons.construction_rounded,
                  color: WorldPalette.green,
                  onTap: () => context.push(Routes.worldBuild),
                ),
                _FeatureTile(
                  number: '08',
                  title: 'Season 1 · Hacker Academy',
                  subtitle:
                      'Уровень ${world.seasonLevel} · ${world.seasonXp}/1000 XP',
                  icon: Icons.workspace_premium_rounded,
                  color: WorldPalette.gold,
                  onTap: () => context.push(Routes.worldSeason),
                ),
                _FeatureTile(
                  number: '09',
                  title: 'Infinite Coding Run',
                  subtitle:
                      'Рекорд ${world.infiniteRecord} задач · серия ${world.infiniteCurrent}',
                  icon: Icons.all_inclusive_rounded,
                  color: WorldPalette.purple,
                  onTap: () => context.push(Routes.worldInfinite),
                ),
                const SizedBox(height: 10),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _TopBar extends StatelessWidget {
  const _TopBar({required this.world});

  final WorldState world;

  @override
  Widget build(BuildContext context) => Row(
    children: [
      Container(
        width: 42,
        height: 42,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          gradient: const LinearGradient(
            colors: [WorldPalette.purple, WorldPalette.blue],
          ),
        ),
        child: const Icon(Icons.code_rounded, color: Colors.white),
      ),
      const SizedBox(width: 10),
      const Expanded(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Bytecraft World',
              style: TextStyle(
                color: WorldPalette.text,
                fontWeight: FontWeight.w900,
                fontSize: 16,
              ),
            ),
            Text(
              'твоя история в мире Python',
              style: TextStyle(color: WorldPalette.muted, fontSize: 11),
            ),
          ],
        ),
      ),
      StatPill(icon: Icons.monetization_on_rounded, value: '${world.coins}'),
      const SizedBox(width: 6),
      StatPill(
        icon: Icons.diamond_rounded,
        value: '${world.gems}',
        color: WorldPalette.cyan,
      ),
    ],
  );
}

class _OverlayLabel extends StatelessWidget {
  const _OverlayLabel({required this.icon, required this.text});

  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
    decoration: BoxDecoration(
      color: const Color(0xD908111F),
      borderRadius: BorderRadius.circular(12),
      border: Border.all(color: WorldPalette.border),
    ),
    child: Row(
      children: [
        Icon(icon, color: WorldPalette.cyan, size: 17),
        const SizedBox(width: 6),
        Text(
          text,
          style: const TextStyle(
            color: WorldPalette.text,
            fontWeight: FontWeight.w900,
            fontSize: 12,
          ),
        ),
      ],
    ),
  );
}

class _TodayGrid extends StatelessWidget {
  const _TodayGrid({required this.world});

  final WorldState world;

  @override
  Widget build(BuildContext context) => Row(
    children: [
      Expanded(
        child: _MiniGoal(
          icon: Icons.local_fire_department_rounded,
          value: '${world.streak}',
          label: 'дней с решениями',
          color: WorldPalette.orange,
        ),
      ),
      const SizedBox(width: 10),
      Expanded(
        child: _MiniGoal(
          icon: Icons.workspace_premium_rounded,
          value: '${world.seasonLevel}',
          label: 'уровень сезона',
          color: WorldPalette.gold,
        ),
      ),
      const SizedBox(width: 10),
      Expanded(
        child: _MiniGoal(
          icon: Icons.favorite_rounded,
          value: '${world.hearts}',
          label: 'жизни Run',
          color: WorldPalette.red,
        ),
      ),
    ],
  );
}

class _MiniGoal extends StatelessWidget {
  const _MiniGoal({
    required this.icon,
    required this.value,
    required this.label,
    required this.color,
  });

  final IconData icon;
  final String value;
  final String label;
  final Color color;

  @override
  Widget build(BuildContext context) => WorldPanel(
    padding: const EdgeInsets.all(12),
    child: Column(
      children: [
        Icon(icon, color: color, size: 22),
        const SizedBox(height: 5),
        Text(
          value,
          style: const TextStyle(
            color: WorldPalette.text,
            fontSize: 20,
            fontWeight: FontWeight.w900,
          ),
        ),
        Text(
          label,
          textAlign: TextAlign.center,
          style: const TextStyle(
            color: WorldPalette.muted,
            fontSize: 9,
            fontWeight: FontWeight.w700,
          ),
        ),
      ],
    ),
  );
}

class _FeatureTile extends StatelessWidget {
  const _FeatureTile({
    required this.number,
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.color,
    required this.onTap,
  });

  final String number;
  final String title;
  final String subtitle;
  final IconData icon;
  final Color color;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 10),
    child: WorldPanel(
      onTap: onTap,
      padding: const EdgeInsets.all(13),
      child: Row(
        children: [
          Container(
            width: 46,
            height: 46,
            decoration: BoxDecoration(
              color: color.withValues(alpha: .14),
              borderRadius: BorderRadius.circular(13),
              border: Border.all(color: color.withValues(alpha: .35)),
            ),
            child: Icon(icon, color: color),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '$number · $title',
                  style: const TextStyle(
                    color: WorldPalette.text,
                    fontWeight: FontWeight.w900,
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 3),
                Text(
                  subtitle,
                  style: const TextStyle(
                    color: WorldPalette.muted,
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ),
          const Icon(Icons.chevron_right_rounded, color: WorldPalette.muted),
        ],
      ),
    ),
  );
}
