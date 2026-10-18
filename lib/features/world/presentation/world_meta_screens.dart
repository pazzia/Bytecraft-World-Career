import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../domain/world_state.dart';
import '../domain/world_challenge.dart';
import '../domain/world_rules.dart';
import 'world_challenge_screens.dart';
import 'world_controller.dart';
import 'world_ui.dart';
import 'world_help.dart';

class CodeCityScreen extends ConsumerWidget {
  const CodeCityScreen({super.key});

  static const _buildings = [
    ('office', 'Офис', Icons.business_rounded, WorldPalette.blue),
    ('python', 'Python Lab', Icons.code_rounded, WorldPalette.purple),
    ('rnd', 'R&D', Icons.science_rounded, WorldPalette.cyan),
    ('servers', 'Серверная', Icons.dns_rounded, WorldPalette.orange),
    ('team', 'Команда', Icons.groups_rounded, WorldPalette.green),
  ];

  Future<void> _upgrade(BuildContext context, WidgetRef ref, String id,
      String title, int previousLevel) async {
    await ref.read(worldControllerProvider.notifier).upgradeBuilding(id);
    if (!context.mounted) return;
    final level = ref.read(worldControllerProvider).value?.cityLevels[id];
    if (level == null || level <= previousLevel) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Text('$title: уровень $level. Теперь ${WorldRules.buildingEffect(id, level)}.'),
    ));
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) => WorldPage(
    title: 'Code City',
    subtitle: 'Выбирай бонусы за монеты из обучения',
    actions: [IconButton(tooltip: 'Как работают награды и улучшения',
      onPressed: () => WorldHelp.showResources(context),
      icon: const Icon(Icons.help_outline_rounded))],
    child: _WorldData(
      builder: (world) => ListView(
        padding: const EdgeInsets.fromLTRB(16, 10, 16, 30),
        children: [
          WorldPanel(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Text('Решай → получай награды → улучшай город',
              style: TextStyle(color: WorldPalette.text, fontWeight: FontWeight.w800)),
            const SizedBox(height: 6),
            const Text('Здания увеличивают награды или запас жизней. Нажми на здание, чтобы увидеть его эффект.',
              style: TextStyle(color: WorldPalette.muted, fontSize: 12)),
            TextButton.icon(onPressed: () => WorldHelp.showResources(context),
              icon: const Icon(Icons.help_outline_rounded, size: 18),
              label: const Text('Что дают XP, монеты и алмазы?')),
          ])),
          const SizedBox(height: 14),
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
                      isScrollControlled: true,
                      builder: (sheetContext) => SafeArea(
                        child: SingleChildScrollView(
                          padding: const EdgeInsets.all(20),
                          child: _BuildingCard(
                            id: id,
                            title: building.$2,
                            icon: building.$3,
                            color: building.$4,
                            level: world.cityLevels[id] ?? 1,
                            coins: world.coins,
                            cap: world.buildingCap,
                            worldXp: world.worldXp,
                            onUpgrade: () async {
                              Navigator.of(sheetContext).pop();
                              await _upgrade(context, ref, id, building.$2,
                                  world.cityLevels[id] ?? 1);
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
            world.buildingCap == 5
                ? 'Все 5 уровней зданий доступны. Выбери нужный бонус и купи улучшение за монеты.'
                : 'Доступны здания до уровня ${world.buildingCap}. До открытия уровня ${world.buildingCap + 1}: ещё ${world.buildingCap * 200 - world.worldXp} XP. Затем улучшение покупается за монеты.',
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
              worldXp: world.worldXp,
              onUpgrade: () async {
                await _upgrade(context, ref, building.$1, building.$2,
                    world.cityLevels[building.$1] ?? 1);
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
  const _BuildingCard({required this.id, required this.title, required this.icon,
    required this.color, required this.level, required this.coins,
    required this.cap, required this.worldXp, required this.onUpgrade});

  final String id;
  final String title;
  final IconData icon;
  final Color color;
  final int level;
  final int coins;
  final int cap;
  final int worldXp;
  final VoidCallback onUpgrade;

  @override
  Widget build(BuildContext context) {
    final cost = 80 + level * 40;
    final maximum = level >= 5;
    final reasons = <String>[
      if (!maximum && level >= cap)
        'Нужно ещё ${level * 200 - worldXp} XP, чтобы открыть уровень ${level + 1}.',
      if (!maximum && coins < cost)
        'Не хватает ${cost - coins} монет. Получай их за решения заданий.',
    ];
    return WorldPanel(child: Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(children: [
          Container(width: 42, height: 42,
            decoration: BoxDecoration(color: color.withValues(alpha: .14),
              borderRadius: BorderRadius.circular(12)),
            child: Icon(icon, color: color)),
          const SizedBox(width: 12),
          Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(title, style: const TextStyle(color: WorldPalette.text,
              fontWeight: FontWeight.w900)),
            Text('Уровень $level из 5',
              style: const TextStyle(color: WorldPalette.muted, fontSize: 12)),
          ])),
          IconButton(tooltip: 'Как работает $title',
            icon: const Icon(Icons.help_outline_rounded, color: WorldPalette.cyan),
            onPressed: () => WorldHelp.show(context, title, [
              (WorldHelp.purpose(id), WorldHelp.explanation(id)),
              ('Где действует', WorldHelp.scope(id)),
              ('Твой эффект сейчас', WorldRules.buildingEffect(id, level)),
              if (!maximum) ('После улучшения', WorldRules.buildingEffect(id, level + 1)),
            ])),
        ]),
        const SizedBox(height: 10),
        Text(WorldHelp.purpose(id), style: const TextStyle(color: WorldPalette.text,
          fontSize: 14, fontWeight: FontWeight.w700)),
        const SizedBox(height: 4),
        Text('Где: ${WorldHelp.scope(id)}',
          style: const TextStyle(color: WorldPalette.muted, fontSize: 12)),
        const SizedBox(height: 12),
        Text('Сейчас: ${WorldRules.buildingEffect(id, level)}',
          style: const TextStyle(color: WorldPalette.text, fontSize: 13)),
        if (!maximum) ...[
          const SizedBox(height: 6),
          Text('После улучшения: ${WorldRules.buildingEffect(id, level + 1)}',
            style: const TextStyle(color: WorldPalette.green, fontSize: 13,
              fontWeight: FontWeight.w700)),
          const SizedBox(height: 8),
          Text('Баланс: $coins монет · после покупки: ${coins >= cost ? coins - cost : "недостаточно монет"}',
            style: const TextStyle(color: WorldPalette.muted, fontSize: 12)),
        ],
        const SizedBox(height: 12),
        FilledButton.icon(
          onPressed: !maximum && reasons.isEmpty ? onUpgrade : null,
          icon: Icon(maximum ? Icons.check_rounded : Icons.upgrade_rounded),
          label: Text(maximum ? 'Максимальный уровень' : 'Улучшить за $cost монет'),
        ),
        if (reasons.isNotEmpty) ...[
          const SizedBox(height: 8),
          Text(reasons.join('\n'), style: const TextStyle(color: WorldPalette.orange,
            fontSize: 12, height: 1.4)),
        ],
      ],
    ));
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
