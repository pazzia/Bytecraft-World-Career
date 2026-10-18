import 'package:flutter/material.dart';

import 'world_ui.dart';

/// Shared explanations for the city cards, map sheets and resource counters.
abstract final class WorldHelp {
  static String purpose(String id) => switch (id) {
    'office' => 'Больше монет на следующие улучшения',
    'python' => 'Больше опыта за каждое верное решение',
    'rnd' => 'Бонус опыта за решение с первой попытки',
    'servers' => 'Больше общих жизней',
    'team' => 'Быстрее завершай командный проект',
    _ => '',
  };

  static String scope(String id) => switch (id) {
    'office' || 'python' || 'rnd' => 'Курс Python и задания игровых режимов',
    'servers' => 'Новые уровни курса и бесконечный забег',
    'team' => 'Только командный проект',
    _ => '',
  };

  static String explanation(String id) => switch (id) {
    'office' => 'Каждый уровень выше первого добавляет 1 монету за новое прохождение уровня курса или решение игрового задания. Монеты можно потратить на любое здание. Сам по себе офис монеты не производит.',
    'python' => 'Каждый уровень выше первого добавляет 2 XP к награде за новое прохождение уровня курса или решение игрового задания. Этот опыт попадает и в общий прогресс, и в сезон. Например, на уровне 3 за этап экспедиции без ошибок начисляется 35 + 4 = 39 XP при R&D уровня 1.',
    'rnd' => 'Каждый уровень выше первого добавляет 3 XP, если в этом задании ещё не было неверных ответов. При ошибке бонус R&D за это задание не начисляется. В курсе условие — впервые пройти уровень без ошибок и подсказок. Бонус складывается с Python Lab.',
    'servers' => 'Каждое улучшение увеличивает максимум жизней на 1 и сразу добавляет 1 жизнь. Ошибки в курсе и бесконечном забеге расходуют общий запас. По одной жизни восстанавливается каждые 30 минут, даже при закрытой игре. Улучшение не ускоряет восстановление.',
    'team' => 'Уровень здания равен вкладу за верное решение командного задания. Цель проекта — 160 вкладов. На уровне 2 с нуля нужно 80 верных решений, на уровне 3 — 54. Завершение проекта приносит дополнительно 150 XP и 100 монет.',
    _ => '',
  };

  static const resources = [
    ('Монеты — покупка улучшений',
      'Получай монеты за верные решения, первое прохождение уровней курса и игровые награды. Трать их на здания. Цена на кнопке указана в монетах; опыт при покупке не расходуется.'),
    ('XP — доступ к уровням зданий',
      '200 общего XP открывают уровень 2, 400 — уровень 3, 600 — уровень 4, 800 — уровень 5. После открытия уровня улучшение нужно купить за монеты. Бонусы зданий действуют постоянно после покупки.'),
    ('Сезонный XP — награды сезона',
      'Заработанный опыт также пополняет сезон. За каждые 1000 сезонного XP можно забрать 60 монет; за каждый третий полученный уровень сезона — ещё 1 алмаз. Получение награды сезона не уменьшает общий XP.'),
    ('Алмазы — восстановление жизней',
      'За 1 алмаз можно сразу восстановить весь общий запас жизней. Алмазы можно получить из сундука экспедиции и наград сезона.'),
    ('Как связаны обучение и город',
      'Решай задания → получай XP и монеты → открывай и покупай улучшения → получай больше наград за следующие решения. Курс и мир используют общие XP, монеты и жизни. Первое прохождение даёт полную награду, повторение — 20% базового XP без монет и бонусов зданий. Повторение и режим курса «На время» не расходуют жизни.'),
  ];

  static Future<void> show(BuildContext context, String title,
      List<(String, String)> sections) => showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    showDragHandle: true,
    backgroundColor: WorldPalette.bg,
    builder: (context) => SafeArea(
      child: FractionallySizedBox(
        heightFactor: .8,
        child: Column(children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 0, 8, 8),
            child: Row(children: [
              Expanded(child: Text(title, style: const TextStyle(
                color: WorldPalette.text, fontSize: 20, fontWeight: FontWeight.w800))),
              IconButton(tooltip: 'Закрыть подсказку', onPressed: () => Navigator.pop(context),
                icon: const Icon(Icons.close, color: WorldPalette.muted)),
            ]),
          ),
          Expanded(child: ListView(
            padding: const EdgeInsets.fromLTRB(20, 0, 20, 24),
            children: [for (final section in sections) ...[
              Text(section.$1, style: const TextStyle(color: WorldPalette.cyan,
                fontSize: 15, fontWeight: FontWeight.w800)),
              const SizedBox(height: 6),
              Text(section.$2, style: const TextStyle(color: WorldPalette.text,
                fontSize: 14, height: 1.5)),
              const SizedBox(height: 20),
            ]],
          )),
        ]),
      ),
    ),
  );

  static void showResources(BuildContext context) {
    show(context, 'Награды и улучшения', resources);
  }
}
