import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../domain/world_state.dart';
import 'world_controller.dart';
import 'world_ui.dart';

class ExpeditionScreen extends ConsumerWidget {
  const ExpeditionScreen({super.key});

  static const _tasks = [
    'Найди ошибку в расчёте скидки',
    'Исправь цикл обработки заказов',
    'Стабилизируй API',
    'Оптимизируй фильтрацию данных',
    'Финальный deploy-check',
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) => WorldPage(
        title: 'Сегодняшняя экспедиция',
        subtitle: 'Короткое приключение · 10–20 минут',
        child: _WorldData(
          builder: (world) => ListView(
            padding: const EdgeInsets.all(16),
            children: [
              WorldPanel(
                glow: WorldPalette.green,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const AspectRatio(
                      aspectRatio: 1,
                      child: WorldArtwork(WorldScene.expedition),
                    ),
                    const SizedBox(height: 16),
                    const Row(
                      children: [
                        Icon(Icons.explore_rounded, color: WorldPalette.green),
                        SizedBox(width: 8),
                        Text(
                          'Спасти продакшен!',
                          style: TextStyle(
                            color: WorldPalette.text,
                            fontSize: 19,
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 7),
                    const Text(
                      'Прод падает. Пройди цепочку задач, восстанови API и забери сундук.',
                      style: TextStyle(color: WorldPalette.muted, fontSize: 12),
                    ),
                    const SizedBox(height: 14),
                    _ExpeditionPath(step: world.expeditionStep),
                  ],
                ),
              ),
              const SizedBox(height: 18),
              if (world.expeditionStep < 5)
                WorldPanel(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Задание ${world.expeditionStep + 1}/5',
                        style: const TextStyle(
                          color: WorldPalette.green,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        _tasks[world.expeditionStep],
                        style: const TextStyle(
                          color: WorldPalette.text,
                          fontSize: 18,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      const SizedBox(height: 12),
                      const CodeBlock(
                        "orders = [120, 80, 0, 250]\nresult = []\nfor price in orders:\n    result.append(100 / price)\nprint(result)",
                      ),
                      const SizedBox(height: 12),
                      const Text(
                        'Найди потенциальный crash и исправь обработку данных.',
                        style: TextStyle(color: WorldPalette.muted, fontSize: 12),
                      ),
                      const SizedBox(height: 14),
                      WorldButton(
                        label: 'Решить и продолжить',
                        icon: Icons.play_arrow_rounded,
                        onPressed: () async {
                          await ref
                              .read(worldControllerProvider.notifier)
                              .advanceExpedition();
                        },
                      ),
                    ],
                  ),
                )
              else
                WorldPanel(
                  glow: WorldPalette.gold,
                  child: Column(
                    children: [
                      const Icon(
                        Icons.inventory_2_rounded,
                        color: WorldPalette.gold,
                        size: 56,
                      ),
                      const SizedBox(height: 10),
                      const Text(
                        'Экспедиция завершена',
                        style: TextStyle(
                          color: WorldPalette.text,
                          fontSize: 20,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      const SizedBox(height: 6),
                      const Text(
                        '+150 XP · +50 монет · редкий сундук',
                        style: TextStyle(color: WorldPalette.muted),
                      ),
                      const SizedBox(height: 14),
                      WorldButton(
                        label: world.expeditionChestClaimed
                            ? 'Сундук уже получен ✓'
                            : 'Открыть сундук',
                        icon: Icons.card_giftcard_rounded,
                        onPressed: world.expeditionChestClaimed
                            ? null
                            : () async {
                                await ref
                                    .read(worldControllerProvider.notifier)
                                    .claimExpeditionChest();
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

class _ExpeditionPath extends StatelessWidget {
  const _ExpeditionPath({required this.step});

  final int step;

  @override
  Widget build(BuildContext context) => Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          for (var i = 0; i < 5; i++) ...[
            Container(
              width: 38,
              height: 38,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: i < step
                    ? WorldPalette.green
                    : i == step
                        ? WorldPalette.purple
                        : WorldPalette.panel2,
                border: Border.all(
                  color: i <= step ? WorldPalette.cyan : WorldPalette.border,
                ),
              ),
              child: Center(
                child: Text(
                  '${i + 1}',
                  style: const TextStyle(
                    color: WorldPalette.text,
                    fontWeight: FontWeight.w900,
                  ),
                ),
              ),
            ),
            if (i < 4)
              Expanded(
                child: Container(
                  height: 2,
                  color: i < step ? WorldPalette.green : WorldPalette.border,
                ),
              ),
          ],
        ],
      );
}

class BossFightScreen extends ConsumerWidget {
  const BossFightScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) => WorldPage(
        title: 'Босс: Bug Lord',
        subtitle: 'Глава · Functions',
        child: _WorldData(
          builder: (world) => ListView(
            padding: const EdgeInsets.all(16),
            children: [
              WorldPanel(
                glow: WorldPalette.red,
                child: Column(
                  children: [
                    Container(
                      height: 280,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(18),
                        gradient: const RadialGradient(
                          colors: [Color(0xFF6A1B2D), Color(0xFF160B20)],
                        ),
                      ),
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          const Positioned.fill(
                            child: WorldArtwork(WorldScene.boss),
                          ),
                          Positioned(
                            bottom: 12,
                            left: 20,
                            right: 20,
                            child: WorldProgress(
                              value: world.bossHp / 100,
                              color: WorldPalette.red,
                              height: 12,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      world.bossCleared
                          ? 'BOSS DEFEATED'
                          : 'HP ${world.bossHp}%',
                      style: TextStyle(
                        color: world.bossCleared
                            ? WorldPalette.green
                            : WorldPalette.red,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              WorldPanel(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Задание ${(world.bossTask + 1).clamp(1, 5)}/5',
                      style: const TextStyle(
                        color: WorldPalette.muted,
                        fontSize: 12,
                      ),
                    ),
                    const SizedBox(height: 5),
                    const Text(
                      'Исправь код, чтобы босс потерял HP',
                      style: TextStyle(
                        color: WorldPalette.text,
                        fontSize: 17,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    const SizedBox(height: 12),
                    const CodeBlock(
                      "def calculate_total(items):\n    total = 0\n    for item in items:\n        total = item.price\n    return total",
                    ),
                    const SizedBox(height: 12),
                    const _TestRow(ok: true, text: 'Тест 1: Базовый случай'),
                    const _TestRow(ok: true, text: 'Тест 2: Пустой список'),
                    _TestRow(
                      ok: world.bossCleared,
                      text: 'Тест 3: Несколько элементов',
                    ),
                    const SizedBox(height: 14),
                    WorldButton(
                      label: world.bossCleared
                          ? 'Переиграть босса'
                          : 'Запустить код · ударить босса',
                      icon: Icons.play_arrow_rounded,
                      onPressed: () async {
                        final controller =
                            ref.read(worldControllerProvider.notifier);
                        if (world.bossCleared) {
                          await controller.resetBoss();
                        } else {
                          await controller.attackBoss();
                        }
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

class _TestRow extends StatelessWidget {
  const _TestRow({required this.ok, required this.text});

  final bool ok;
  final String text;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 6),
        child: Row(
          children: [
            Icon(
              ok ? Icons.check_box_rounded : Icons.cancel_rounded,
              color: ok ? WorldPalette.green : WorldPalette.red,
              size: 18,
            ),
            const SizedBox(width: 7),
            Text(text, style: const TextStyle(color: WorldPalette.muted)),
          ],
        ),
      );
}

class GhostPvpScreen extends ConsumerWidget {
  const GhostPvpScreen({super.key});

  String _time(int seconds) =>
      '${seconds ~/ 60}:${(seconds % 60).toString().padLeft(2, '0')}';

  @override
  Widget build(BuildContext context, WidgetRef ref) => WorldPage(
        title: 'Ghost PvP',
        subtitle: 'Побей рекорд другого разработчика',
        child: _WorldData(
          builder: (world) => ListView(
            padding: const EdgeInsets.all(16),
            children: [
              WorldPanel(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Лучшие решения',
                      style: TextStyle(
                        color: WorldPalette.text,
                        fontWeight: FontWeight.w900,
                        fontSize: 17,
                      ),
                    ),
                    const SizedBox(height: 12),
                    const _LeaderboardRow(1, 'Dmitry', '2:41', '1 ошибка'),
                    const _LeaderboardRow(2, 'Anna', '3:12', '0 ошибок'),
                    const _LeaderboardRow(3, 'Alex', '3:35', '2 ошибки'),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              WorldPanel(
                glow: WorldPalette.violet,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Expanded(
                          child: Text(
                            'Твоя попытка',
                            style: TextStyle(
                              color: WorldPalette.text,
                              fontSize: 17,
                              fontWeight: FontWeight.w900,
                            ),
                          ),
                        ),
                        Text(
                          _time(world.ghostBestSeconds),
                          style: const TextStyle(
                            color: WorldPalette.orange,
                            fontSize: 18,
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    const CodeBlock(
                      "def is_prime(n):\n    if n < 2:\n        return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            return False\n    return True",
                    ),
                    const SizedBox(height: 12),
                    const Text(
                      'Задача: ускорь решение и сохрани корректность на скрытых тестах.',
                      style: TextStyle(color: WorldPalette.muted, fontSize: 12),
                    ),
                    const SizedBox(height: 14),
                    WorldButton(
                      label: 'Отправить решение',
                      icon: Icons.bolt_rounded,
                      onPressed: () async {
                        await ref
                            .read(worldControllerProvider.notifier)
                            .submitGhostRun();
                      },
                    ),
                    const SizedBox(height: 8),
                    Text(
                      world.ghostBestSeconds < 161
                          ? 'Ты уже быстрее Dmitry!'
                          : 'Dmitry: 2:41 · попробуй сократить ещё ${world.ghostBestSeconds - 161} сек.',
                      style: const TextStyle(
                        color: WorldPalette.cyan,
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      );
}

class _LeaderboardRow extends StatelessWidget {
  const _LeaderboardRow(this.place, this.name, this.time, this.errors);

  final int place;
  final String name;
  final String time;
  final String errors;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 10),
        child: Row(
          children: [
            CircleAvatar(
              radius: 15,
              backgroundColor: place == 1
                  ? WorldPalette.gold
                  : WorldPalette.panel2,
              child: Text(
                '$place',
                style: TextStyle(
                  color: place == 1 ? WorldPalette.bg : WorldPalette.text,
                  fontWeight: FontWeight.w900,
                ),
              ),
            ),
            const SizedBox(width: 9),
            Expanded(
              child: Text(
                name,
                style: const TextStyle(
                  color: WorldPalette.text,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
            Text(time, style: const TextStyle(color: WorldPalette.text)),
            const SizedBox(width: 10),
            Text(errors, style: const TextStyle(color: WorldPalette.muted)),
          ],
        ),
      );
}

class AiRivalScreen extends ConsumerWidget {
  const AiRivalScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) => WorldPage(
        title: 'Kai · AI Rival',
        subtitle: 'Соперник, который растёт вместе с тобой',
        child: _WorldData(
          builder: (world) => ListView(
            padding: const EdgeInsets.all(16),
            children: [
              WorldPanel(
                glow: WorldPalette.cyan,
                child: Column(
                  children: [
                    const AspectRatio(
                      aspectRatio: 1.15,
                      child: WorldArtwork(WorldScene.kai),
                    ),
                    const SizedBox(height: 10),
                    const Text(
                      'Kai',
                      style: TextStyle(
                        color: WorldPalette.text,
                        fontSize: 22,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    const Text(
                      'Твой AI-соперник',
                      style: TextStyle(color: WorldPalette.muted),
                    ),
                    const SizedBox(height: 14),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: WorldPalette.panel2,
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: const Text(
                        '«Я решил эту задачу за 6 строк. Сможешь за 5?»',
                        style: TextStyle(
                          color: WorldPalette.text,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              WorldPanel(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Challenge · Compact Counter',
                      style: TextStyle(
                        color: WorldPalette.text,
                        fontSize: 17,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    const SizedBox(height: 10),
                    const CodeBlock(
                      "def count_even(nums):\n    return len([x for x in nums if x % 2 == 0])",
                    ),
                    const SizedBox(height: 12),
                    const Text(
                      'Напиши решение не длиннее и сохрани читаемость.',
                      style: TextStyle(color: WorldPalette.muted, fontSize: 12),
                    ),
                    const SizedBox(height: 14),
                    WorldButton(
                      label: 'Бросить вызов Kai',
                      icon: Icons.sports_esports_rounded,
                      onPressed: () async {
                        await ref
                            .read(worldControllerProvider.notifier)
                            .beatRival();
                      },
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              WorldPanel(
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _RivalStat('${world.rivalWins}', 'побед'),
                    const _RivalStat('6', 'задач подряд'),
                    _RivalStat('${50 + world.rivalWins * 2}%', 'win rate'),
                  ],
                ),
              ),
            ],
          ),
        ),
      );
}

class _RivalStat extends StatelessWidget {
  const _RivalStat(this.value, this.label);

  final String value;
  final String label;

  @override
  Widget build(BuildContext context) => Column(
        children: [
          Text(
            value,
            style: const TextStyle(
              color: WorldPalette.cyan,
              fontSize: 22,
              fontWeight: FontWeight.w900,
            ),
          ),
          Text(label, style: const TextStyle(color: WorldPalette.muted, fontSize: 10)),
        ],
      );
}

class InfiniteRunScreen extends ConsumerWidget {
  const InfiniteRunScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) => WorldPage(
        title: 'Infinite Coding Run',
        subtitle: 'Задача за задачей · сложность растёт',
        child: _WorldData(
          builder: (world) => ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Row(
                children: [
                  Expanded(
                    child: StatPill(
                      icon: Icons.local_fire_department_rounded,
                      value: 'Серия ${world.infiniteCurrent}',
                      color: WorldPalette.green,
                    ),
                  ),
                  const SizedBox(width: 8),
                  StatPill(
                    icon: Icons.favorite_rounded,
                    value: '${world.hearts}',
                    color: WorldPalette.red,
                  ),
                  const SizedBox(width: 8),
                  StatPill(
                    icon: Icons.bolt_rounded,
                    value: 'x${(1 + world.infiniteCurrent / 10).toStringAsFixed(1)} XP',
                    color: WorldPalette.cyan,
                  ),
                ],
              ),
              const SizedBox(height: 16),
              WorldPanel(
                glow: WorldPalette.purple,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            'Задача ${world.infiniteCurrent + 1}',
                            style: const TextStyle(
                              color: WorldPalette.text,
                              fontSize: 20,
                              fontWeight: FontWeight.w900,
                            ),
                          ),
                        ),
                        const Text(
                          'Средняя',
                          style: TextStyle(
                            color: WorldPalette.orange,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 5),
                    const Text(
                      'Найди ошибку в коде:',
                      style: TextStyle(color: WorldPalette.muted),
                    ),
                    const SizedBox(height: 12),
                    const CodeBlock(
                      "def find_max(nums):\n    max_val = nums[0]\n    for i in range(1, len(nums)):\n        if nums[i] < max_val:\n            max_val = nums[i]\n    return max_val",
                    ),
                    const SizedBox(height: 14),
                    Row(
                      children: [
                        Expanded(
                          child: WorldButton(
                            label: 'Проверить',
                            icon: Icons.check_rounded,
                            onPressed: () async {
                              await ref
                                  .read(worldControllerProvider.notifier)
                                  .solveInfinite();
                            },
                          ),
                        ),
                        const SizedBox(width: 9),
                        Expanded(
                          child: WorldButton(
                            label: 'Ошибка',
                            secondary: true,
                            icon: Icons.close_rounded,
                            onPressed: world.hearts > 0
                                ? () async {
                                    await ref
                                        .read(worldControllerProvider.notifier)
                                        .failInfinite();
                                  }
                                : null,
                          ),
                        ),
                      ],
                    ),
                    if (world.hearts == 0) ...[
                      const SizedBox(height: 12),
                      WorldButton(
                        label: 'Revive за 1 💎',
                        icon: Icons.favorite_rounded,
                        onPressed: world.gems > 0
                            ? () async {
                                await ref
                                    .read(worldControllerProvider.notifier)
                                    .reviveInfinite();
                              }
                            : null,
                      ),
                    ],
                  ],
                ),
              ),
              const SizedBox(height: 16),
              WorldPanel(
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _RivalStat('${world.infiniteRecord}', 'личный рекорд'),
                    _RivalStat('#${12 - (world.infiniteCurrent ~/ 10)}', 'место в топе'),
                    _RivalStat('${world.worldXp}', 'World XP'),
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
