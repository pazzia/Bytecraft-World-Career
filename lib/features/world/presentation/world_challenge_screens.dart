import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/routes.dart';
import '../../../shared/widgets/code_copy.dart';
import '../domain/world_challenge.dart';
import '../domain/world_state.dart';
import 'world_controller.dart';
import 'world_ui.dart';
import 'world_hearts_panel.dart';
import 'expedition_map.dart';

class ExpeditionScreen extends StatelessWidget {
  const ExpeditionScreen({super.key});
  @override
  Widget build(BuildContext context) =>
      const WorldQuestScreen(mode: WorldMode.expedition);
}

class BossFightScreen extends StatelessWidget {
  const BossFightScreen({super.key});
  @override
  Widget build(BuildContext context) =>
      const WorldQuestScreen(mode: WorldMode.boss);
}

class GhostPvpScreen extends StatelessWidget {
  const GhostPvpScreen({super.key});
  @override
  Widget build(BuildContext context) =>
      const WorldQuestScreen(mode: WorldMode.ghost);
}

class AiRivalScreen extends StatelessWidget {
  const AiRivalScreen({super.key});
  @override
  Widget build(BuildContext context) =>
      const WorldQuestScreen(mode: WorldMode.rival);
}

class InfiniteRunScreen extends StatelessWidget {
  const InfiniteRunScreen({super.key});
  @override
  Widget build(BuildContext context) =>
      const WorldQuestScreen(mode: WorldMode.infinite);
}

class WorldQuestScreen extends ConsumerStatefulWidget {
  const WorldQuestScreen({
    required this.mode,
    this.category = 'Условия',
    super.key,
  });
  final WorldMode mode;
  final String category;
  @override
  ConsumerState<WorldQuestScreen> createState() => _WorldQuestScreenState();
}

class _WorldQuestScreenState extends ConsumerState<WorldQuestScreen> {
  final _feedbackKey = GlobalKey();
  final _expeditionMapKey = GlobalKey();
  String? _feedback;
  bool _next = false;
  bool _correct = false;
  String get _title => switch (widget.mode) {
    WorldMode.expedition => 'Экспедиция · восстановить API',
    WorldMode.project => 'Проект · калькулятор',
    WorldMode.boss => 'Босс · Bug Lord',
    WorldMode.ghost => 'Забег на время',
    WorldMode.guild => 'Проект учебной команды',
    WorldMode.rival => 'Kai · учебный соперник',
    WorldMode.training => 'Тренировка · ${widget.category}',
    WorldMode.infinite => 'Бесконечный забег',
  };
  String _rules(WorldState s) => switch (widget.mode) {
    WorldMode.expedition => '5 разных задач восстанавливают API. За каждую: 35 XP и 20 монет до бонусов города. Сундук за 5 этапов: +100 XP, 80 монет и 2 алмаза, один раз. Экспедиция открывает проект калькулятора.',
    WorldMode.project => '4 компонента калькулятора проверяются по очереди. За каждый: 45 XP и 25 монет до бонусов. Готовый проект открывает босса.',
    WorldMode.boss => '4 уязвимости. Верный ответ снимает 25 HP; ошибка не наносит урон. Победа даёт 180 XP и 120 монет до бонусов.',
    WorldMode.ghost => 'Время считается с появления задания до верного ответа. Неверный ответ не останавливает часы. Сравниваются твои личные попытки; сетевых соперников пока нет.',
    WorldMode.guild =>
      'Это локальный учебный проект. Каждое проверенное решение даёт ${s.cityLevels['team'] ?? 1} вклад. Здание «Команда» увеличивает вклад. Цель — 160.',
    WorldMode.rival => 'Kai — учебный соперник с заранее подготовленными задачами. Победа засчитывается только за верный ответ: 55 XP и 25 монет до бонусов. Задачи меняются.',
    WorldMode.training => 'Верное решение закрепляет одну ошибку выбранной темы: 30 XP и 12 монет до бонусов. Неверное добавляет ошибку. Числа обозначают ошибки, а не проценты.',
    WorldMode.infinite => 'За верный ответ: 20 + длина серии XP и 5 монет до бонусов. Ошибка отнимает жизнь и обнуляет серию; рекорд сохраняется. При нуле жизней продолжить нельзя.',
  };
  @override
  Widget build(BuildContext context) => WorldPage(
    title: _title,
    subtitle: 'После ошибки базовый XP вдвое меньше',
    child: ref
        .watch(worldControllerProvider)
        .when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (e, st) => Center(child: Text('$e')),
          data: (s) {
            final mode = widget.mode;
            final lock = WorldChallenges.locked(s, mode);
            final finished = WorldChallenges.finished(s, mode, category: widget.category);
            final cursor = WorldChallenges.cursor(s, mode, widget.category);
            final task = finished && mode == WorldMode.training
                ? DnaCurriculum.at(widget.category, DnaCurriculum.count(widget.category) - 1, 'finished')
                : WorldChallenges.at(s, mode, category: widget.category);
            return ListView(
              padding: const EdgeInsets.all(16),
              children: [
                if (mode == WorldMode.infinite) ...[
                  const WorldHeartsPanel(),
                  const SizedBox(height: 14),
                ],
                if (mode == WorldMode.expedition)
                  ExpeditionMap(key: _expeditionMapKey, completed: s.expeditionStep),
                if (mode == WorldMode.boss ||
                    mode == WorldMode.rival)
                  SizedBox(
                    height: 200,
                    child: WorldArtwork(switch (mode) {
                      WorldMode.boss => WorldScene.boss,
                      WorldMode.rival => WorldScene.kai,
                      _ => WorldScene.expedition,
                    }),
                  ),
                WorldPanel(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        _rules(s),
                        style: const TextStyle(color: WorldPalette.text),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        '${s.worldXp} XP · ${s.coins} монет · сезон ${s.seasonXp}/1000 XP',
                        style: const TextStyle(color: WorldPalette.gold),
                      ),
                      const SizedBox(height: 8),
                      Text(switch (mode) {
                        WorldMode.expedition =>
                          'Восстановлено $cursor/5 этапов',
                        WorldMode.project => 'Готово $cursor/4 компонентов',
                        WorldMode.boss =>
                          'HP ${s.bossHp}/100 · закрыто $cursor/4 уязвимостей',
                        WorldMode.guild =>
                          'Твой вклад ${s.guildContribution} · цель ${s.guildTotal}/160',
                        WorldMode.rival => 'Побед ${s.rivalWins}',
                        WorldMode.ghost =>
                          s.ghostBestSeconds == 0
                              ? 'Личный рекорд ещё не установлен'
                              : 'Личный рекорд ${s.ghostBestSeconds} сек.',
                        WorldMode.training =>
                          'Пройдено $cursor/${DnaCurriculum.count(widget.category)} · незакреплённых ошибок: ${s.mistakes[widget.category] ?? 0}',
                        WorldMode.infinite =>
                          'Серия ${s.infiniteCurrent} · рекорд ${s.infiniteRecord} · жизни ${s.hearts}/${s.maxHearts}',
                      }, style: const TextStyle(color: WorldPalette.cyan)),
                    ],
                  ),
                ),
                const SizedBox(height: 14),
                if (_feedback != null)
                  WorldPanel(
                    key: _feedbackKey,
                    glow: _correct ? WorldPalette.green : WorldPalette.red,
                    child: Text(
                      _feedback!,
                      key: const ValueKey('world-feedback'),
                      style: const TextStyle(color: WorldPalette.text),
                    ),
                  ),
                const SizedBox(height: 14),
                if (lock != null) ...[
                  WorldPanel(
                    child: Text(
                      lock,
                      style: const TextStyle(color: WorldPalette.orange),
                    ),
                  ),
                  const SizedBox(height: 12),
                  WorldButton(
                    label: 'К обязательному этапу',
                    icon: Icons.arrow_forward,
                    onPressed: () => context.push(
                      mode == WorldMode.boss
                          ? Routes.worldBuild
                          : Routes.worldExpedition,
                    ),
                  ),
                ] else if (finished) ...[
                  WorldPanel(
                    child: Text(switch (mode) {
                      WorldMode.expedition =>
                        'API восстановлен. Открой сундук и переходи к проекту.',
                      WorldMode.project =>
                        'Калькулятор готов. Можно сразиться с Bug Lord.',
                      WorldMode.training => 'Все 20 подтем пройдены. Продолжай курс и применяй знания в практике.',
                      WorldMode.guild => 'Проект команды завершён. Бонус уже начислен. Продолжай курс Python.',
                      _ => 'Bug Lord побеждён. Продолжай курс Python и тренируйся в забегах.',
                    }, style: const TextStyle(color: WorldPalette.green)),
                  ),
                  const SizedBox(height: 12),
                  if (mode == WorldMode.expedition)
                    WorldButton(
                      label: s.expeditionChestClaimed
                          ? 'Сундук получен ✓'
                          : 'Сундук: +100 XP · +80 монет · +2 💎',
                      icon: Icons.card_giftcard,
                      onPressed: s.expeditionChestClaimed
                          ? null
                          : () async {
                              await ref
                                  .read(worldControllerProvider.notifier)
                                  .claimExpeditionChest();
                            },
                    ),
                  const SizedBox(height: 12),
                  WorldButton(
                    label: mode == WorldMode.expedition
                        ? 'К проекту'
                        : mode == WorldMode.project
                        ? 'К боссу'
                        : 'Продолжить курс Python',
                    icon: Icons.arrow_forward,
                    onPressed: () => context.push(switch (mode) {
                      WorldMode.expedition => Routes.worldBuild,
                      WorldMode.project => Routes.worldBoss,
                      _ => Routes.map,
                    }),
                  ),
                ] else if (mode == WorldMode.infinite && s.hearts == 0) ...[
                  CodeCopyScope(wrongAnswers: s.failures[task.id] ?? 0, child: CodeBlock(task.code)),
                  const Text(
                    'Забег остановлен. Пройденные этапы и рекорд сохранены.',
                    style: TextStyle(color: WorldPalette.text),
                  ),
                  const Text(
                    'Дождись следующей жизни или восстанови запас кнопкой выше.',
                    style: TextStyle(color: WorldPalette.muted),
                  ),
                ] else if (_next)
                  WorldButton(
                    label: 'Следующее задание',
                    icon: Icons.arrow_forward,
                    onPressed: () => setState(() {
                      _next = false;
                      _feedback = null;
                    }),
                  )
                else
                  _ChallengeForm(
                    key: ValueKey(task.id),
                    task: task,
                    wrongAnswers: s.failures[task.id] ?? 0,
                    submit: (answer, elapsed) async {
                      final result = await ref
                          .read(worldControllerProvider.notifier)
                          .submitChallenge(
                            mode,
                            task.id,
                            answer,
                            category: widget.category,
                            elapsedSeconds: elapsed,
                          );
                      if (!mounted) return;
                      setState(() {
                        _feedback = result.message;
                        _correct = result.correct;
                        _next = result.correct;
                      });
                      WidgetsBinding.instance.addPostFrameCallback((_) {
                        if (!mounted) return;
                        final target = result.correct && mode == WorldMode.expedition
                            ? _expeditionMapKey.currentContext
                            : _feedbackKey.currentContext;
                        if (target != null) {
                          unawaited(
                            Scrollable.ensureVisible(
                              target,
                              duration: const Duration(milliseconds: 200),
                            ),
                          );
                        }
                      });
                    },
                  ),
                const SizedBox(height: 30),
              ],
            );
          },
        ),
  );
}

class _ChallengeForm extends StatefulWidget {
  const _ChallengeForm({required this.task, required this.submit, required this.wrongAnswers, super.key});
  final WorldChallenge task;
  final int wrongAnswers;
  final Future<void> Function(String, int) submit;
  @override
  State<_ChallengeForm> createState() => _ChallengeFormState();
}

class _ChallengeFormState extends State<_ChallengeForm> {
  final _answer = TextEditingController();
  final _watch = Stopwatch()..start();
  bool _busy = false;
  String? _selected;
  @override
  void dispose() {
    _watch.stop();
    _answer.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final task = widget.task;
    final input = task.options.isEmpty ? _answer.text : _selected ?? '';
    return WorldPanel(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            task.title,
            style: const TextStyle(
              color: WorldPalette.text,
              fontWeight: FontWeight.w900,
              fontSize: 19,
            ),
          ),
          const SizedBox(height: 12),
          CodeCopyScope(wrongAnswers: widget.wrongAnswers, child: CodeBlock(
            task.code.replaceAll('___', _selected ?? '___'))),
          const SizedBox(height: 12),
          Text(task.prompt, style: const TextStyle(color: WorldPalette.text)),
          const SizedBox(height: 12),
          if (task.options.isEmpty)
            TextField(
              key: const ValueKey('world-answer'),
              controller: _answer,
              minLines: 1,
              maxLines: 5,
              keyboardType: TextInputType.multiline,
              enabled: !_busy,
              autocorrect: false,
              enableSuggestions: false,
              style: const TextStyle(color: WorldPalette.text),
              decoration: const InputDecoration(
                labelText: 'Твой ответ',
                border: OutlineInputBorder(),
              ),
              onChanged: (_) => setState(() {}),
            )
          else
            for (final option in task.options)
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: OutlinedButton(
                  onPressed: _busy
                      ? null
                      : () => setState(() => _selected = option),
                  style: OutlinedButton.styleFrom(
                    backgroundColor: _selected == option
                        ? WorldPalette.purple
                        : WorldPalette.panel2,
                  ),
                  child: Text(
                    option,
                    style: const TextStyle(color: WorldPalette.text),
                  ),
                ),
              ),
          const SizedBox(height: 14),
          WorldButton(
            label: _busy ? 'Проверка…' : 'Проверить ответ',
            icon: Icons.fact_check,
            onPressed: _busy || input.trim().isEmpty
                ? null
                : () async {
                    FocusScope.of(context).unfocus();
                    setState(() => _busy = true);
                    try {
                      await widget.submit(
                        input,
                        _watch.elapsed.inSeconds < 1
                            ? 1
                            : _watch.elapsed.inSeconds,
                      );
                    } catch (_) {
                      if (context.mounted)
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text(
                              'Не удалось сохранить результат. Повтори отправку.',
                            ),
                          ),
                        );
                    } finally {
                      if (mounted) setState(() => _busy = false);
                    }
                  },
          ),
        ],
      ),
    );
  }
}
