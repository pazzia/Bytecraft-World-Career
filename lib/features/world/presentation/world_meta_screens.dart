import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../domain/world_state.dart';
import '../domain/world_challenge.dart';
import '../domain/world_rules.dart';
import 'world_challenge_screens.dart';
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
          AspectRatio(
            aspectRatio: 1,
            child: WorldPanel(
              glow: WorldPalette.purple,
              padding: EdgeInsets.zero,
              child: ClipRRect(
                borderRadius: BorderRadius.circular(18),
                child: WorldCityScene(
                  levels: world.cityLevels,
                  onBuilding: (id) {
                    final building = _buildings.firstWhere((b) => b.$1 == id);
                    showModalBottomSheet<void>(
                      context: context,
                      backgroundColor: WorldPalette.bg,
                      builder: (sheetContext) => SafeArea(
                        child: Padding(
                          padding: const EdgeInsets.all(20),
                          child: _BuildingCard(
                            id: id,
                            title: building.$2,
                            icon: building.$3,
                            color: building.$4,
                            level: world.cityLevels[id] ?? 1,
                            coins: world.coins,
                            cap: world.buildingCap,
                            onUpgrade: () async {
                              Navigator.of(sheetContext).pop();
                              await ref
                                  .read(worldControllerProvider.notifier)
                                  .upgradeBuilding(id);
                            },
                          ),
                        ),
                      ),
                    );
                  },
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
          Text(
            'Монеты тратятся на улучшения. Каждые 200 XP открывают следующий уровень зданий, максимум 5. Сейчас доступен уровень ${world.buildingCap}.',
            style: const TextStyle(color: WorldPalette.muted),
          ),
          const SizedBox(height: 12),
          for (final building in _buildings) ...[
            _BuildingCard(
              id: building.$1,
              title: building.$2,
              icon: building.$3,
              color: building.$4,
              level: world.cityLevels[building.$1] ?? 1,
              coins: world.coins,
              cap: world.buildingCap,
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
                  'Текущий проект · калькулятор',
                  style: TextStyle(
                    color: WorldPalette.text,
                    fontSize: 16,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 6),
                const Text(
                  'Экспедиция → 4 компонента проекта → битва с боссом',
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
    required this.cap,
    required this.onUpgrade,
  });

  final String id;
  final String title;
  final IconData icon;
  final Color color;
  final int level;
  final int coins;
  final int cap;
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
                  'Уровень $level · ${WorldRules.buildingEffect(id, level)}\nСледующий: ${WorldRules.buildingEffect(id, level + 1)}',
                  style: const TextStyle(
                    color: WorldPalette.muted,
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ),
          TextButton(
            onPressed: coins >= cost && level < cap ? onUpgrade : null,
            child: Text(
              level >= 5
                  ? 'Максимум'
                  : level >= cap
                  ? 'Нужен XP'
                  : '⬆ $cost',
            ),
          ),
        ],
      ),
    );
  }
}

class GuildScreen extends StatelessWidget {
  const GuildScreen({super.key});
  @override
  Widget build(BuildContext context) =>
      const WorldQuestScreen(mode: WorldMode.guild);
}

class BuildUnlockScreen extends StatelessWidget {
  const BuildUnlockScreen({super.key});
  @override
  Widget build(BuildContext context) =>
      const WorldQuestScreen(mode: WorldMode.project);
}

class MistakeDnaScreen extends ConsumerWidget {
  const MistakeDnaScreen({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) => WorldPage(
    title: 'Mistake DNA',
    subtitle: 'Незакреплённые ошибки по темам',
    child: _WorldData(
      builder: (s) => ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const WorldPanel(
            child: Text(
              'Здесь учитываются реальные неверные ответы из курса и игровых режимов. Верное решение тренировки закрепляет одну ошибку выбранной темы. В каждом разделе 20 разных подтем: от основ до сложных случаев. После обновления программа DNA начинается заново; награды и остальной прогресс сохранены.',
              style: TextStyle(color: WorldPalette.text),
            ),
          ),
          const SizedBox(height: 16),
          for (final entry in s.mistakes.entries)
            Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: WorldPanel(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      '${entry.key}: ${entry.value} ошибок · пройдено ${s.solved['training:${entry.key}'] ?? 0}/20',
                      style: const TextStyle(
                        color: WorldPalette.text,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 10),
                    WorldButton(
                      label: WorldChallenges.finished(s, WorldMode.training, category: entry.key) ? 'Все 20 подтем пройдены ✓' : 'Продолжить · ${(s.solved['training:${entry.key}'] ?? 0) + 1}/20',
                      icon: Icons.code,
                      onPressed: WorldChallenges.finished(s, WorldMode.training, category: entry.key) ? null : () => Navigator.of(context).push(
                        MaterialPageRoute<void>(
                          builder: (_) => WorldQuestScreen(
                            mode: WorldMode.training,
                            category: entry.key,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
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
    title: 'Сезон · Hacker Academy',
    subtitle: 'Награды за проверенные решения',
    child: _WorldData(
      builder: (s) => ListView(
        padding: const EdgeInsets.all(16),
        children: [
          WorldPanel(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'Уровень ${s.seasonLevel}',
                  style: const TextStyle(
                    color: WorldPalette.gold,
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  '${s.seasonXp}/1000 XP',
                  style: const TextStyle(color: WorldPalette.text),
                ),
                const SizedBox(height: 12),
                WorldProgress(
                  value: (s.seasonXp / 1000).clamp(0.0, 1.0),
                  color: WorldPalette.gold,
                ),
                const SizedBox(height: 12),
                const Text(
                  'За каждые 1000 XP: 60 монет. Каждый третий достигнутый уровень также даёт 1 алмаз. Излишек XP сохраняется. Монеты улучшают город, алмазы восстанавливают жизни забега.',
                  style: TextStyle(color: WorldPalette.text),
                ),
                const SizedBox(height: 12),
                WorldButton(
                  label: s.seasonXp >= 1000
                      ? 'Получить +60 монет${(s.seasonLevel + 1) % 3 == 0 ? ' и 1 💎' : ''}'
                      : 'Осталось ${1000 - s.seasonXp} XP',
                  icon: Icons.card_giftcard,
                  onPressed: s.seasonXp < 1000
                      ? null
                      : () async {
                          await ref
                              .read(worldControllerProvider.notifier)
                              .claimSeasonReward();
                        },
                ),
              ],
            ),
          ),
        ],
      ),
    ),
  );
}

class _WorldData extends ConsumerWidget {
  const _WorldData({required this.builder});
  final Widget Function(WorldState) builder;
  @override
  Widget build(BuildContext context, WidgetRef ref) => ref
      .watch(worldControllerProvider)
      .when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, st) => Center(
          child: Text('$e', style: const TextStyle(color: WorldPalette.text)),
        ),
        data: builder,
      );
}
