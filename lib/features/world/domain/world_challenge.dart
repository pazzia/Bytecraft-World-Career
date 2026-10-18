import 'world_state.dart';

part 'dna_curriculum.dart';

enum WorldMode {
  expedition,
  project,
  boss,
  ghost,
  guild,
  rival,
  training,
  infinite,
}

/// A question is a snapshot of an earned progression cursor, never a UI flag.
class WorldChallenge {
  const WorldChallenge({
    required this.id,
    required this.title,
    required this.code,
    required this.prompt,
    required this.answer,
    required this.explanation,
    required this.category,
    this.options = const [],
    this.verificationOutput,
  });
  final String id, title, code, prompt, answer, explanation, category;
  final List<String> options;
  final String? verificationOutput;

  bool accepts(String input) =>
      input.trim().isNotEmpty &&
      input.trim().replaceAll('\r\n', '\n') == answer;
}

abstract final class WorldChallenges {
  static String key(WorldMode mode, String category) =>
      mode == WorldMode.training ? 'training:$category' : mode.name;

  static String? locked(WorldState s, WorldMode mode) => switch (mode) {
    WorldMode.project when s.expeditionStep < 5 =>
      'Сначала восстанови API: 5 задач экспедиции.',
    WorldMode.boss when !s.projectUnlocked || !s.hasVerifiedProject =>
      'Сначала заверши 4 проверяемых шага проекта.',
    WorldMode.ghost || WorldMode.guild || WorldMode.rival
        when s.expeditionStep < 2 =>
      'Сначала реши 2 задачи экспедиции.',
    _ => null,
  };

  static bool finished(WorldState s, WorldMode mode, {String category = 'Условия'}) => switch (mode) {
    WorldMode.training => cursor(s, mode, category) >= DnaCurriculum.count(category),
    WorldMode.expedition => s.expeditionStep >= 5,
    WorldMode.project => s.projectUnlocked,
    WorldMode.boss => s.bossCleared,
    WorldMode.guild => s.guildTotal >= 160,
    _ => false,
  };

  static int cursor(WorldState s, WorldMode mode, String category) =>
      switch (mode) {
        WorldMode.expedition => s.expeditionStep,
        WorldMode.project => s.completedProjectSteps,
        WorldMode.boss => s.bossTask,
        _ => s.solved[key(mode, category)] ?? 0,
      };

  static WorldChallenge at(
    WorldState s,
    WorldMode mode, {
    String category = 'Условия',
  }) {
    final n = cursor(s, mode, category);
    final id = '${key(mode, category)}:$n';
    if (mode == WorldMode.expedition) return _expedition(n, id);
    if (mode == WorldMode.project) return _project(n, id);
    if (mode == WorldMode.boss) return _boss(n, id);
    if (mode == WorldMode.training) return DnaCurriculum.at(category, n, id);
    // Every repeatable mode uses its own sequence. Training uses the failed topic.
    final offset = mode.index * 17;
    final topic = mode == WorldMode.training
        ? category
        : const ['Условия', 'Циклы', 'Индексы', 'Типы данных', 'Функции'][n %
              5];
    final a = n + offset + 2;
    final difficulty = n ~/ 5 + 1;
    return switch (topic) {
      'Условия' => WorldChallenge(
        id: id,
        title: 'Маршрутизация · $difficulty',
        code:
            'load = $a\nif load > ${a + (n.isEven ? 1 : -1)}:\n    print("queue")\nelse:\n    print("ready")',
        prompt: 'Что напечатает диспетчер? Введи вывод без кавычек.',
        answer: n.isEven ? 'ready' : 'queue',
        category: topic,
        explanation: 'Сравни load с порогом: ветка if выполняется только при истинном условии.',
      ),
      'Циклы' => WorldChallenge(
        id: id,
        title: 'Пакет заказов · $difficulty',
        code:
            'total = 0\nfor i in range($a, ${a + difficulty + 2}):\n    total += i\nprint(total)',
        prompt: 'Введи число, которое напечатает программа.',
        answer: '${(difficulty + 2) * (2 * a + difficulty + 1) ~/ 2}',
        category: topic,
        explanation:
            'range не включает правую границу; total накапливает сумму всех i.',
      ),
      'Индексы' => WorldChallenge(
        id: id,
        title: 'Очередь данных · $difficulty',
        code:
            'values = [$a, ${a + 3}, ${a * 2}, ${a + 7}]\nprint(values[${n.isEven ? '-1' : '1'}])',
        prompt: 'Какое число будет выведено?',
        answer: '${n.isEven ? a + 7 : a + 3}',
        category: topic,
        explanation:
            'Индексы начинаются с нуля, -1 указывает на последний элемент.',
      ),
      'Типы данных' => WorldChallenge(
        id: id,
        title: 'Нормализация данных · $difficulty',
        code: 'value = "$a"\nprint(int(value) + $difficulty)',
        prompt: 'Введи вывод программы.',
        answer: '${a + difficulty}',
        category: topic,
        explanation:
            'int преобразует строку в целое число; затем выполняется сложение.',
      ),
      _ => WorldChallenge(
        id: id,
        title: 'Конвейер функций · $difficulty',
        code:
            'def process(x):\n    return x * $difficulty + 3\nprint(process($a))',
        prompt: 'Какой результат вернёт вызов и напечатает print?',
        answer: '${a * difficulty + 3}',
        category: 'Функции',
        explanation:
            'Подставь аргумент вместо x, выполни умножение, затем сложение.',
      ),
    };
  }

  static WorldChallenge _expedition(int n, String id) {
    final tasks = [
      (
        'Скидка без потерь',
        'price = 200\ndiscount = 15\nprint(price - price * discount // 100)',
        'Рассчитай итоговую цену. Введи вывод программы.',
        '170',
        'Типы данных',
        'Скидка равна 30; итоговая цена — 170.',
      ),
      (
        'Защита от деления на ноль',
        'for price in [120, 0, 80]:\n    if ___:\n        print(100 / price)',
        'Выбери условие, которое пропускает нулевую цену.',
        'price != 0',
        'Условия',
        'Делить можно только на ненулевое число.',
      ),
      (
        'Восстановление API',
        'response = {"status": 200, "data": [3, 5, 8]}\nprint(len(response["data"]))',
        'Сколько записей получил API? Введи вывод.',
        '3',
        'Индексы',
        'В списке data три элемента.',
      ),
      (
        'Фильтр заказов',
        'orders = [120, 80, 0, 250]\nprint(sum(x for x in orders if x >= 100))',
        'Введи сумму принятых заказов.',
        '370',
        'Циклы',
        'Условие проходят 120 и 250; сумма — 370.',
      ),
      (
        'Проверка перед запуском',
        'def healthy(status, errors):\n    return status == 200 and errors == 0\nprint(healthy(200, 1))',
        'Введи True или False: готов ли сервис к запуску?',
        'False',
        'Функции',
        'При errors = 1 сервис не готов: обе части and должны быть истинными.',
      ),
    ];
    final t = tasks[n.clamp(0, 4)];
    return WorldChallenge(
      id: id,
      title: t.$1,
      code: t.$2,
      prompt: t.$3,
      answer: t.$4,
      category: t.$5,
      explanation: t.$6,
      options: n == 1 ? ['price == 0', 'price != 0', 'price < 0'] : const [],
    );
  }

  static WorldChallenge _project(int n, String id) {
    final tasks = [
      (
        'Базовые операции',
        'def add(a, b):\n    ___',
        'Выбери тело функции, возвращающее сумму.',
        'return a + b',
        'Функции',
        'return передаёт результат вызывающему коду.',
        ['print(a + b)', 'return a - b', 'return a + b'],
      ),
      (
        'История вычислений',
        'history = [5, 9]\nhistory.append(12)\nprint(history[-1])',
        'Введи последний сохранённый результат.',
        '12',
        'Индексы',
        'append добавляет элемент в конец списка.',
        <String>[],
      ),
      (
        'Обработка ошибок',
        'def divide(a, b):\n    if b == 0:\n        return "error"\n    return a / b\nprint(divide(8, 0))',
        'Что получит интерфейс? Введи вывод без кавычек.',
        'error',
        'Условия',
        'Ранний return останавливает функцию до опасного деления.',
        <String>[],
      ),
      (
        'Формат результата',
        'result = 7 / 2\nprint(f"{result:.2f}")',
        'Введи ровно тот текст, который увидит пользователь.',
        '3.50',
        'Типы данных',
        '.2f выводит ровно два знака после десятичной точки.',
        <String>[],
      ),
    ];
    final t = tasks[n.clamp(0, 3)];
    return WorldChallenge(
      id: id,
      title: t.$1,
      code: t.$2,
      prompt: t.$3,
      answer: t.$4,
      category: t.$5,
      explanation: t.$6,
      options: t.$7,
    );
  }

  static WorldChallenge _boss(int n, String id) {
    final tasks = [
      (
        'Накопление суммы',
        'def total(items):\n    result = 0\n    for item in items:\n        ___\n    return result',
        'Выбери исправление: total([2, 3]) должен вернуть 5.',
        'result += item',
        'Циклы',
        'Присваивание заменяет сумму; += накапливает её.',
        ['result = item', 'result += item', 'result -= item'],
      ),
      (
        'Граница диапазона',
        'def count(n):\n    return len(range(1, n))\nprint(count(5))',
        'Найди фактический результат, чтобы обнаружить ошибку границы.',
        '4',
        'Циклы',
        'range(1, 5) содержит 1, 2, 3, 4.',
        <String>[],
      ),
      (
        'Возврат результата',
        'def square(x):\n    x * x\nprint(square(4))',
        'Что фактически напечатает этот код?',
        'None',
        'Функции',
        'Без return функция возвращает None.',
        <String>[],
      ),
      (
        'Финальная проверка',
        'def safe_max(values):\n    if not values:\n        return None\n    return max(values)\nprint(safe_max([-5, -2, -8]))',
        'Введи результат для отрицательных чисел.',
        '-2',
        'Условия',
        'Максимальное отрицательное число в списке — -2.',
        <String>[],
      ),
    ];
    final t = tasks[n.clamp(0, 3)];
    return WorldChallenge(
      id: id,
      title: t.$1,
      code: t.$2,
      prompt: t.$3,
      answer: t.$4,
      category: t.$5,
      explanation: t.$6,
      options: t.$7,
    );
  }
}
