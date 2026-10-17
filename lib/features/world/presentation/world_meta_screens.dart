import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../domain/world_state.dart';
import 'world_controller.dart';
import 'world_ui.dart';

class CodeCityScreen extends ConsumerWidget {
  const CodeCityScreen({super.key});

  static const _buildings = [
    ('office', 'Офис', Icons.business_rounded, WorldPalette.blue),
    ('python', 'Python Lab', Icons.code_rounded, WorldPalette.purple),
    ('rnd', 'R&D', Icons.science_rounded, WorldPalette.cyan),
    ('servers', 'Серверная', Icons.dns_rounded, WorldPalette.orange),
    ('team', 'Команда', Icons.groups_rounded, WorldPalette.green),
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) => WorldPage(
        title: 'Code City',
        subtitle: 'Твоя IT-компания растёт вместе с навыками',
        child: _WorldData(
          builder: (world) => ListView(
            padding: const EdgeInsets.fromLTRB(16, 10, 16, 30),
            children: [
              SizedBox(
                height: 300,
                child: WorldPanel(
                  glow: WorldPalette.purple,
                  padding: EdgeInsets.zero,
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(18),
                    child: CustomPaint(
                      painter: CityPainter(levels: world.cityLevels),
                      child: const SizedBox.expand(),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  StatPill(
                    icon: Icons.monetization_on_rounded,
                    value: '${world.coins}',
                  ),
                  const SizedBox(width: 8),
                  StatPill(
                    icon: Icons.auto_awesome_rounded,
                    value: '${world.worldXp} XP',
                    color: WorldPalette.purple,
                  ),
                ],
              ),
              const SizedBox(height: 20),
              const SectionTitle('Районы компании'),
              for (final building in _buildings) ...[
                _BuildingCard(
                  id: building.$1,
                  title: building.$2,
                  icon: building.$3,
                  color: building.$4,
                  level: world.cityLevels[building.$1] ?? 1,
                  coins: world.coins,
                  onUpgrade: () async {
                    await ref
                        .read(worldControllerProvider.notifier)
                        .upgradeBuilding(building.$1);
                  },
                ),
                const SizedBox(height: 10),
              ],
              const SizedBox(height: 10),
              WorldPanel(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Текущий проект · Web API',
                      style: TextStyle(
                        color: WorldPalette.text,
                        fontSize: 16,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    const SizedBox(height: 6),
                    const Text(
                      'Разблокируется через Functions и Build to Unlock',
                      style: TextStyle(color: WorldPalette.muted, fontSize: 12),
                    ),
                    const SizedBox(height: 12),
                    WorldProgress(
                      value: world.completedProjectSteps / 4,
                      color: WorldPalette.green,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      );
}

class _BuildingCard extends StatelessWidget {
  const _BuildingCard({
    required this.id,
    required this.title,
    required this.icon,
    required this.color,
    required this.level,
    required this.coins,
    required this.onUpgrade,
  });

  final String id;
  final String title;
  final IconData icon;
  final Color color;
  final int level;
  final int coins;
  final VoidCallback onUpgrade;

  @override
  Widget build(BuildContext context) {
    final cost = 80 + level * 40;
    return WorldPanel(
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: color.withValues(alpha: .14),
              borderRadius: BorderRadius.circular(14),
            ),
            child: Icon(icon, color: color),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    color: WorldPalette.text,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                Text(
                  'Уровень $level · следующий апгрейд +20 XP',
                  style: const TextStyle(color: WorldPalette.muted, fontSize: 11),
                ),
              ],
            ),
          ),
          TextButton(
            onPressed: coins >= cost ? onUpgrade : null,
            child: Text('⬆ $cost'),
          ),
        ],
      ),
    );
  }
}

class GuildScreen extends ConsumerWidget {
  const GuildScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) => WorldPage(
        title: 'Python Masters',
        subtitle: 'Команда · 12 участников',
        child: _WorldData(
          builder: (world) => ListView(
            padding: const EdgeInsets.all(16),
            children: [
              WorldPanel(
                glow: WorldPalette.blue,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          width: 56,
                          height: 56,
                          decoration: BoxDecoration(
                            color: WorldPalette.blue.withValues(alpha: .18),
                            borderRadius: BorderRadius.circular(18),
                          ),
                          child: const Icon(
                            Icons.groups_rounded,
                            color: WorldPalette.cyan,
                            size: 30,
                          ),
                        ),
                        const SizedBox(width: 12),
                        const Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Недельный проект',
                                style: TextStyle(
                                  color: WorldPalette.muted,
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                              Text(
                                'Построить Data Analyzer',
                                style: TextStyle(
                                  color: WorldPalette.text,
                                  fontSize: 17,
                                  fontWeight: FontWeight.w900,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 14),
                    const Text(
                      'Вместе решите 160 задач и закройте мини-проект для анализа данных.',
                      style: TextStyle(color: WorldPalette.muted, fontSize: 12),
                    ),
                    const SizedBox(height: 12),
                    WorldProgress(
                      value: world.guildTotal / 160,
                      color: WorldPalette.purple,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      '${world.guildTotal}/160 · осталось ${160 - world.guildTotal > 0 ? 160 - world.guildTotal : 0}',
                      style: const TextStyle(color: WorldPalette.text, fontSize: 11),
                    ),
                    const SizedBox(height: 14),
                    WorldButton(
                      label: 'Внести вклад · +8 задач',
                      icon: Icons.add_task_rounded,
                      onPressed: () async {
                        await ref
                            .read(worldControllerProvider.notifier)
                            .contributeGuild();
                      },
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 18),
              const SectionTitle('Вклад участников'),
              _Member('Ты', world.guildContribution, WorldPalette.purple),
              const _Member('Anna', 28, WorldPalette.cyan),
              const _Member('Dmitry', 25, WorldPalette.blue),
              const _Member('Alex', 18, WorldPalette.orange),
              const _Member('Maria', 12, WorldPalette.green),
              const SizedBox(height: 18),
              WorldPanel(
                child: Row(
                  children: [
                    const Icon(Icons.chat_bubble_rounded, color: WorldPalette.cyan),
                    const SizedBox(width: 10),
                    const Expanded(
                      child: Text(
                        'Anna: «Я закрыла парсинг CSV. Кто возьмёт визуализацию?»',
                        style: TextStyle(color: WorldPalette.text, fontSize: 12),
                      ),
                    ),
                    IconButton(
                      onPressed: () {},
                      icon: const Icon(Icons.send_rounded, color: WorldPalette.purple),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      );
}

class _Member extends StatelessWidget {
  const _Member(this.name, this.score, this.color);

  final String name;
  final int score;
  final Color color;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 10),
        child: Row(
          children: [
            CircleAvatar(
              radius: 17,
              backgroundColor: color.withValues(alpha: .2),
              child: Text(name.characters.first),
            ),
            const SizedBox(width: 10),
            SizedBox(
              width: 68,
              child: Text(
                name,
                style: const TextStyle(
                  color: WorldPalette.text,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
            Expanded(
              child: WorldProgress(value: score / 50, color: color, height: 7),
            ),
            const SizedBox(width: 10),
            Text('$score', style: const TextStyle(color: WorldPalette.muted)),
          ],
        ),
      );
}

class MistakeDnaScreen extends ConsumerWidget {
  const MistakeDnaScreen({super.key});

  static const _colors = [
    WorldPalette.red,
    WorldPalette.blue,
    WorldPalette.green,
    WorldPalette.cyan,
    WorldPalette.purple,
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) => WorldPage(
        title: 'Mistake DNA',
        subtitle: 'Игра на твоих ошибках',
        child: _WorldData(
          builder: (world) {
            final entries = world.mistakes.entries.toList();
            return ListView(
              padding: const EdgeInsets.all(16),
              children: [
                WorldPanel(
                  glow: WorldPalette.orange,
                  child: Column(
                    children: [
                      const Text(
                        'Твой профиль ошибок',
                        style: TextStyle(
                          color: WorldPalette.text,
                          fontWeight: FontWeight.w900,
                          fontSize: 18,
                        ),
                      ),
                      const SizedBox(height: 14),
                      Row(
                        children: [
                          DonutChart(values: world.mistakes),
                          const SizedBox(width: 14),
                          Expanded(
                            child: Column(
                              children: [
                                for (var i = 0; i < entries.length; i++)
                                  Padding(
                                    padding: const EdgeInsets.only(bottom: 7),
                                    child: Row(
                                      children: [
                                        Container(
                                          width: 9,
                                          height: 9,
                                          decoration: BoxDecoration(
                                            color: _colors[i % _colors.length],
                                            shape: BoxShape.circle,
                                          ),
                                        ),
                                        const SizedBox(width: 7),
                                        Expanded(
                                          child: Text(
                                            entries[i].key,
                                            style: const TextStyle(
                                              color: WorldPalette.muted,
                                              fontSize: 11,
                                            ),
                                          ),
                                        ),
                                        Text(
                                          '${entries[i].value}%',
                                          style: const TextStyle(
                                            color: WorldPalette.text,
                                            fontWeight: FontWeight.w800,
                                            fontSize: 11,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 18),
                const SectionTitle('Тренировка слабых мест'),
                for (var i = 0; i < entries.length; i++) ...[
                  WorldPanel(
                    child: Row(
                      children: [
                        Container(
                          width: 44,
                          height: 44,
                          decoration: BoxDecoration(
                            color: _colors[i % _colors.length].withValues(alpha: .15),
                            borderRadius: BorderRadius.circular(13),
                          ),
                          child: Icon(
                            Icons.bug_report_rounded,
                            color: _colors[i % _colors.length],
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                entries[i].key,
                                style: const TextStyle(
                                  color: WorldPalette.text,
                                  fontWeight: FontWeight.w900,
                                ),
                              ),
                              Text(
                                '${(entries[i].value / 8).ceil().clamp(1, 8)} задач для улучшения',
                                style: const TextStyle(
                                  color: WorldPalette.muted,
                                  fontSize: 11,
                                ),
                              ),
                            ],
                          ),
                        ),
                        FilledButton(
                          onPressed: () async {
                            await ref
                                .read(worldControllerProvider.notifier)
                                .trainMistake(entries[i].key);
                          },
                          child: const Text('Начать'),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 10),
                ],
              ],
            );
          },
        ),
      );
}

class BuildUnlockScreen extends ConsumerWidget {
  const BuildUnlockScreen({super.key});

  static const _steps = [
    ('basic', 'Базовые операции', 'Основа калькулятора'),
    ('history', 'История вычислений', 'Список последних результатов'),
    ('errors', 'Обработка ошибок', 'ZeroDivision и неверный ввод'),
    ('ui', 'Приятный интерфейс', 'Опциональный polishing'),
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) => WorldPage(
        title: 'Build to Unlock',
        subtitle: 'Реальные мини-проекты открывают главы',
        child: _WorldData(
          builder: (world) => ListView(
            padding: const EdgeInsets.all(16),
            children: [
              WorldPanel(
                glow: world.projectUnlocked ? WorldPalette.green : WorldPalette.purple,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          world.projectUnlocked
                              ? Icons.lock_open_rounded
                              : Icons.lock_outline_rounded,
                          color: world.projectUnlocked
                              ? WorldPalette.green
                              : WorldPalette.gold,
                        ),
                        const SizedBox(width: 10),
                        const Expanded(
                          child: Text(
                            'Разблокируй следующую главу',
                            style: TextStyle(
                              color: WorldPalette.text,
                              fontSize: 18,
                              fontWeight: FontWeight.w900,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Создай полноценный калькулятор и докажи, что умеешь применять функции, условия и обработку ошибок.',
                      style: TextStyle(color: WorldPalette.muted, fontSize: 12),
                    ),
                    const SizedBox(height: 14),
                    WorldProgress(
                      value: world.completedProjectSteps / 4,
                      color: WorldPalette.green,
                      height: 10,
                    ),
                    const SizedBox(height: 7),
                    Text(
                      '${world.completedProjectSteps}/4 · ${world.projectUnlocked ? 'глава открыта' : 'продолжай проект'}',
                      style: TextStyle(
                        color: world.projectUnlocked
                            ? WorldPalette.green
                            : WorldPalette.muted,
                        fontWeight: FontWeight.w800,
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 18),
              const SectionTitle('Чек-лист проекта'),
              for (final step in _steps) ...[
                WorldPanel(
                  onTap: () async {
                    await ref
                        .read(worldControllerProvider.notifier)
                        .toggleProjectStep(step.$1);
                  },
                  child: Row(
                    children: [
                      Icon(
                        world.projectSteps[step.$1] == true
                            ? Icons.check_circle_rounded
                            : Icons.radio_button_unchecked_rounded,
                        color: world.projectSteps[step.$1] == true
                            ? WorldPalette.green
                            : WorldPalette.orange,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              step.$2,
                              style: const TextStyle(
                                color: WorldPalette.text,
                                fontWeight: FontWeight.w900,
                              ),
                            ),
                            Text(
                              step.$3,
                              style: const TextStyle(
                                color: WorldPalette.muted,
                                fontSize: 11,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 10),
              ],
              const SizedBox(height: 8),
              WorldButton(
                label: world.projectUnlocked
                    ? 'Глава Functions разблокирована ✓'
                    : 'Нужно завершить проект',
                icon: world.projectUnlocked
                    ? Icons.lock_open_rounded
                    : Icons.lock_rounded,
                onPressed: world.projectUnlocked ? () {} : null,
              ),
            ],
          ),
        ),
      );
}

class SeasonScreen extends ConsumerWidget {
  const SeasonScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) => WorldPage(
        title: 'Season 1: Hacker Academy',
        subtitle: 'Осталось 18 дней',
        child: _WorldData(
          builder: (world) => ListView(
            padding: const EdgeInsets.all(16),
            children: [
              WorldPanel(
                glow: WorldPalette.gold,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          width: 58,
                          height: 58,
                          decoration: BoxDecoration(
                            gradient: const LinearGradient(
                              colors: [WorldPalette.purple, WorldPalette.orange],
                            ),
                            borderRadius: BorderRadius.circular(18),
                          ),
                          child: const Icon(
                            Icons.school_rounded,
                            color: Colors.white,
                            size: 31,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Уровень ${world.seasonLevel}',
                                style: const TextStyle(
                                  color: WorldPalette.text,
                                  fontSize: 24,
                                  fontWeight: FontWeight.w900,
                                ),
                              ),
                              Text(
                                '${world.seasonXp}/1000 XP',
                                style: const TextStyle(color: WorldPalette.muted),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 14),
                    WorldProgress(
                      value: world.seasonXp / 1000,
                      color: WorldPalette.gold,
                      height: 10,
                    ),
                    const SizedBox(height: 14),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: const [
                        _Reward(Icons.face_rounded, 'Аватар'),
                        _Reward(Icons.inventory_2_rounded, 'Скин'),
                        _Reward(Icons.workspace_premium_rounded, 'Титул'),
                        _Reward(Icons.apartment_rounded, 'Фон'),
                      ],
                    ),
                    const SizedBox(height: 14),
                    WorldButton(
                      label: world.seasonXp >= 1000
                          ? 'Забрать награду уровня'
                          : 'До награды ${1000 - world.seasonXp} XP',
                      icon: Icons.card_giftcard_rounded,
                      onPressed: world.seasonXp >= 1000
                          ? () async {
                              await ref
                                  .read(worldControllerProvider.notifier)
                                  .claimSeasonReward();
                            }
                          : null,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 18),
              const SectionTitle('Дорога наград'),
              WorldPanel(
                child: Column(
                  children: [
                    for (var level = 10; level <= 14; level++)
                      _SeasonLevel(
                        level: level,
                        current: world.seasonLevel,
                        label: switch (level) {
                          10 => 'Cyber avatar',
                          11 => 'Code chest',
                          12 => 'Hacker title',
                          13 => 'Profile background',
                          _ => 'Legendary city skin',
                        },
                      ),
                  ],
                ),
              ),
              const SizedBox(height: 18),
              WorldPanel(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Глобальная цель сообщества',
                      style: TextStyle(
                        color: WorldPalette.text,
                        fontWeight: FontWeight.w900,
                        fontSize: 16,
                      ),
                    ),
                    const SizedBox(height: 6),
                    const Text(
                      'Вместе решить 1 000 000 задач',
                      style: TextStyle(color: WorldPalette.muted, fontSize: 12),
                    ),
                    const SizedBox(height: 12),
                    const WorldProgress(value: .723, color: WorldPalette.green),
                    const SizedBox(height: 6),
                    const Text(
                      '723 450 / 1 000 000',
                      style: TextStyle(color: WorldPalette.text, fontSize: 11),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      );
}

class _Reward extends StatelessWidget {
  const _Reward(this.icon, this.label);

  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) => Column(
        children: [
          Container(
            width: 46,
            height: 46,
            decoration: BoxDecoration(
              color: WorldPalette.purple.withValues(alpha: .17),
              borderRadius: BorderRadius.circular(14),
            ),
            child: Icon(icon, color: WorldPalette.gold),
          ),
          const SizedBox(height: 5),
          Text(
            label,
            style: const TextStyle(color: WorldPalette.muted, fontSize: 9),
          ),
        ],
      );
}

class _SeasonLevel extends StatelessWidget {
  const _SeasonLevel({
    required this.level,
    required this.current,
    required this.label,
  });

  final int level;
  final int current;
  final String label;

  @override
  Widget build(BuildContext context) {
    final done = level <= current;
    return Padding(
      padding: const EdgeInsets.only(bottom: 13),
      child: Row(
        children: [
          CircleAvatar(
            radius: 16,
            backgroundColor:
                done ? WorldPalette.gold : WorldPalette.border,
            child: Text(
              '$level',
              style: TextStyle(
                color: done ? WorldPalette.bg : WorldPalette.muted,
                fontWeight: FontWeight.w900,
              ),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              label,
              style: TextStyle(
                color: done ? WorldPalette.text : WorldPalette.muted,
                fontWeight: FontWeight.w800,
              ),
            ),
          ),
          Icon(
            done ? Icons.check_circle_rounded : Icons.lock_rounded,
            color: done ? WorldPalette.green : WorldPalette.muted,
            size: 19,
          ),
        ],
      ),
    );
  }
}

class _WorldData extends ConsumerWidget {
  const _WorldData({required this.builder});

  final Widget Function(WorldState world) builder;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(worldControllerProvider);
    return state.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stack) => Center(
        child: Text('$error', style: const TextStyle(color: Colors.white)),
      ),
      data: builder,
    );
  }
}
