"""Модули 7–12: циклы, управление циклами, списки, кортежи и множества,
словари, генераторы коллекций."""
from bclib import choice, fill, match, multi, order, predict, bug, typed, topic, task, run


def iterations(header):
    """How many times a loop header runs its body."""
    result = run(f"count = 0\n{header}\n    count += 1\nprint(count)")
    return result.out.strip() if result.ok else None


def mutates_in_place(call):
    nums = [3, 1, 2]
    before = list(nums)
    value = eval(call, {"nums": nums, "sorted": sorted})
    return value is None and nums != before


def hashable(expr):
    try:
        {eval(expr)}
        return True
    except TypeError:
        return False


MODULES = []

# -------------------------------------------------------------------- loops
MODULES.append(dict(
    id="loops", title="Циклы", description="for и while", icon="🔁",
    topics=[
        topic("loop_for", "Цикл for",
              "for перебирает элементы последовательности: строки, списка, range — по одному за шаг.",
              """
              for буква in "кот": — тело выполнится три раза, и переменная буква по очереди будет «к», «о», «т».

              Тело цикла — строки с отступом после двоеточия. Строки без отступа после цикла выполняются один раз, когда цикл закончился.

              Классический шаблон — накопление: заводим total = 0 до цикла и прибавляем в теле.
              """,
              [("total = 0\nfor n in [3, 5, 7]:\n    total += n\nprint(total)", None),
               ("for ch in 'кот':\n    print(ch)\nprint('готово')", "«готово» печатается один раз — после цикла.")],
              ["Поставить print с отступом внутрь цикла, хотя нужен один итоговый вывод.",
               "Обнулять счётчик внутри цикла — он будет сбрасываться на каждом шаге."]),
        topic("loop_range", "range",
              "range(stop), range(start, stop), range(start, stop, step) — последовательность целых чисел; stop не входит.",
              """
              range(3) — это 0, 1, 2. range(2, 5) — 2, 3, 4. range(0, 10, 4) — 0, 4, 8.

              Шаг может быть отрицательным: range(5, 0, -2) — 5, 3, 1. Если start >= stop при положительном шаге, последовательность пустая: range(3, 3).

              range не создаёт список заранее, а выдаёт числа по одному. list(range(...)) показывает все числа сразу — в квадратных скобках, это список (о списках подробно — в отдельном модуле).
              """,
              [("print(list(range(4)), list(range(2, 5)), list(range(5, 0, -2)))", None)],
              ["Ждать, что range(1, 5) включит 5. Для чисел от 1 до n — range(1, n + 1)."]),
        topic("loop_while", "Цикл while",
              "while повторяет тело, пока условие истинно. Условие проверяется перед каждым шагом.",
              """
              Внутри тела что-то должно менять условие, иначе цикл будет бесконечным.

              while удобен, когда заранее неизвестно, сколько будет шагов: например, делим число, пока оно больше 1.
              """,
              [("n = 10\nsteps = 0\nwhile n > 1:\n    n //= 2\n    steps += 1\nprint(steps)", "10 → 5 → 2 → 1: три шага.")],
              ["Забыть изменить переменную условия — цикл не остановится."]),
    ],
    tasks=[
        task("t_loop_sum_to_n", "Сумма до n", "Прочитайте n и выведите сумму чисел от 1 до n.",
             solution="n = int(input())\ntotal = 0\nfor i in range(1, n + 1):\n    total += i\nprint(total)",
             tests=["5\n", "1\n", "100\n", "10\n"],
             starter="n = int(input())\ntotal = 0\nfor i in range(n):\n    total += i\nprint(total)",
             hint="range(1, n + 1) — числа от 1 до n включительно.", difficulty=1),
        task("t_loop_fizzbuzz", "FizzBuzz",
             "Прочитайте n и выведите числа от 1 до n, каждое на своей строке. Вместо чисел, кратных 3, выведите Fizz, кратных 5 — Buzz, кратных 15 — FizzBuzz.",
             solution="n = int(input())\nfor i in range(1, n + 1):\n    if i % 15 == 0:\n        print('FizzBuzz')\n    elif i % 3 == 0:\n        print('Fizz')\n    elif i % 5 == 0:\n        print('Buzz')\n    else:\n        print(i)",
             tests=["5\n", "15\n", "3\n", "16\n"],
             starter="n = int(input())\nfor i in range(1, n + 1):\n    print(i)",
             hint="Проверяйте кратность 15 первой.", difficulty=2),
    ],
    levels=[
        fill("py_loop_001", "Цикл for", "Допишите цикл, который выведет числа от 0 до 4",
             "for i {{0}} range(5):\n    print(i)", ["in", "of", "from", "inside"], ["in"],
             topic="loop_for", hint="for <переменная> ___ <последовательность>",
             explanation="Цикл for перебирает элементы последовательности с помощью ключевого слова in.",
             expect="0\n1\n2\n3\n4\n"),
        choice("py_loop_002", "range", "Какое последнее число выведет программа?", ["2", "3", "4", "Ничего"], 0,
               code="for i in range(3):\n    print(i)",
               check=lambda option: run("for i in range(3):\n    print(i)").out.split()[-1] == option,
               topic="loop_range", hint="range(3) начинается с 0 и не включает 3.",
               explanation="range(3) даёт 0, 1, 2 — последнее число 2.",
               feedback={"3": "Граница stop в range не входит.", "4": "range(3) — всего три числа: 0, 1, 2."}),
        predict("py_loop_003", "Сумма в цикле", "total = 0\nfor n in range(1, 4):\n    total += n\nprint(total)",
                ["10", "3", "4"], position=0, topic="loop_for", hint="range(1, 4) — это 1, 2, 3.",
                explanation="1 + 2 + 3 = 6.", role="practice", difficulty=2,
                feedback={"10": "Так было бы для range(1, 5): 4 в range(1, 4) не входит.",
                          "3": "3 — последнее число, а мы считаем сумму."}),
        typed("py_loop_006", "Шаг range", "for i in range(2, 11, 3):\n    print(i)",
              topic="loop_range", hint="Начинаем с 2 и прибавляем 3, пока меньше 11.",
              explanation="2, 5, 8 — следующее было бы 11, но stop не входит."),
        match("py_loop_007", "Какой range?", ["list(range(4))", "list(range(2, 5))", "list(range(0, 10, 4))",
                                              "list(range(5, 0, -2))", "list(range(3, 3))"],
              topic="loop_range", hint="stop не входит, отрицательный шаг идёт вниз.",
              explanation="range(4): 0..3; range(2, 5): 2..4; шаг 4 от 0: 0, 4, 8; шаг -2 от 5: 5, 3, 1; range(3, 3) пустой."),
        predict("py_loop_008", "Пока больше одного",
                "n = 20\nsteps = 0\nwhile n > 1:\n    n //= 2\n    steps += 1\nprint(steps)",
                ["5", "3", "20"], position=1, topic="loop_while",
                hint="Распишите значения n после каждого шага.", explanation="Четыре деления: 20 → 10 → 5 → 2 → 1, затем условие n > 1 ложно.",
                role="practice", difficulty=2,
                feedback={"5": "Когда n стало 1, условие n > 1 ложно — пятого шага нет.",
                          "3": "Посчитайте шаги: 20 → 10 → 5 → 2 → 1.",
                          "20": "steps считает шаги, а не хранит n."}),
        order("py_loop_004", "Обратный отсчёт", "Соберите программу: 3, 2, 1, затем «Старт!»",
              ["count = 3", "while count > 0:", "    print(count)", "    count -= 1", "print(\"Старт!\")"],
              topic="loop_while", hint="Тело цикла — строки с отступом. Что должно выполниться один раз, уже после цикла?",
              explanation="while повторяет тело, пока count > 0. «Старт!» стоит без отступа — после цикла.",
              role="challenge", difficulty=3),
        bug("py_loop_005", "Босс: сумма не считается",
            "total = 0\nfor i in range(1, 6):\n    total == total + i\nprint(total)", {2: "    total = total + i"},
            prompt="Программа должна вывести 15, но выводит 0. Найдите ошибку",
            topic="loop_for", hint="Чем отличаются = и ==?",
            explanation="== только сравнивает и ничего не меняет. Нужно присваивание: total = total + i.",
            role="boss", difficulty=3),
    ],
))

# ------------------------------------------------------------ loops_control
MODULES.append(dict(
    id="loops_control", title="Управление циклами", description="break, continue, else, вложенные циклы",
    icon="🎛️",
    topics=[
        topic("loopx_break", "break и continue",
              "break сразу завершает цикл, continue пропускает остаток шага и переходит к следующему.",
              """
              break нужен, когда искомое уже найдено: дальше перебирать незачем.

              continue — «этот элемент пропускаем»: удобно отфильтровать неподходящие значения в начале тела.

              Оба действуют только на ближайший цикл, в котором стоят.
              """,
              [("for n in range(10):\n    if n == 3:\n        break\n    print(n)", "На 3 цикл закончился, 3 не напечаталось."),
               ("total = 0\nfor n in range(6):\n    if n % 2 == 0:\n        continue\n    total += n\nprint(total)", "Чётные пропущены: 1 + 3 + 5.")],
              ["Ждать, что break выйдет сразу из всех вложенных циклов — он прерывает только внутренний."]),
        topic("loopx_else", "else у цикла",
              "Ветка else после for/while выполняется, если цикл закончился сам, без break.",
              """
              Это удобный способ сказать «не нашли»: ищем в цикле, при находке делаем break, а в else пишем, что ничего не нашлось.
              """,
              [("for n in [3, 5, 7]:\n    if n % 2 == 0:\n        print('нашли чётное')\n        break\nelse:\n    print('все нечётные')", None)],
              ["Думать, что else у цикла означает «если не было ни одного шага». Он выполняется при любом завершении без break — в том числе когда последовательность пустая."]),
        topic("loopx_nested", "Вложенные циклы",
              "Цикл внутри цикла: внутренний проходит полностью на каждом шаге внешнего.",
              """
              Если внешний цикл делает 3 шага, а внутренний — 4, тело внутреннего выполнится 3 × 4 = 12 раз.

              Отступы показывают вложенность: тело внутреннего цикла сдвинуто ещё на один уровень.
              """,
              [("for i in range(1, 4):\n    print('*' * i)", "Строка из i звёздочек: здесь цикл один, а повтор делает умножение строки."),
               ("for i in range(1, 3):\n    for j in range(1, 3):\n        print(i, j)", None)],
              ["Использовать одну и ту же переменную во внешнем и внутреннем цикле: внешний цикл продолжит работать, но после внутреннего цикла переменная будет равна его последнему значению, а не значению внешнего."]),
        topic("loopx_enumerate", "enumerate и zip",
              "enumerate даёт пары (индекс, элемент), zip идёт по нескольким последовательностям параллельно.",
              """
              for i, name in enumerate(names): — индекс и значение без range(len(...)). Параметр start задаёт первый номер.

              zip(a, b) останавливается на самой короткой последовательности.

              list(enumerate("ab")) покажет пары в круглых скобках: (0, 'a'). Такая пара — кортеж; подробно о кортежах — в модуле 10.
              """,
              [("for i, ch in enumerate('ab', start=1):\n    print(i, ch)", None),
               ("for name, score in zip(['Ада', 'Алан'], [5, 4]):\n    print(name, score)", None)],
              ["Писать for i in range(len(items)) и items[i], когда хватает enumerate."]),
    ],
    tasks=[
        task("t_loopx_first_negative", "Первое отрицательное",
             "В строке записаны целые числа через пробел. Выведите первое отрицательное число или «нет», если таких нет.",
             solution="for x in input().split():\n    n = int(x)\n    if n < 0:\n        print(n)\n        break\nelse:\n    print('нет')",
             starter="for x in input().split():\n    print(x)",
             tests=["4 7 -2 5 -9\n", "1 2 3\n", "-1\n", "0 0 -3\n"],
             hint="Пригодятся break и else у цикла.", difficulty=2),
        task("t_loopx_triangle", "Треугольник",
             "Прочитайте n и выведите треугольник: в строке i (от 1 до n) — i звёздочек.",
             solution="n = int(input())\nfor i in range(1, n + 1):\n    print('*' * i)",
             starter="n = int(input())\nprint('*' * n)",
             tests=["3\n", "1\n", "5\n", "2\n"], hint="'*' * i — строка из i звёздочек.", difficulty=1),
    ],
    levels=[
        predict("py_loopx_001", "Стоп-кран",
                "total = 0\nfor n in range(10):\n    if n == 3:\n        break\n    total += n\nprint(total, n)",
                ["6 3", "45 9", "3 2"], position=0, topic="loopx_break",
                hint="break завершает цикл сразу — даже текущий шаг не доделывается.",
                explanation="Складываются 0, 1, 2 — это 3. Когда n стало 3, сработал break до total += n, и n так и осталось 3.",
                feedback={"6 3": "break срабатывает до total += n, поэтому 3 не прибавляется.",
                          "45 9": "Так было бы без break: цикл прерывается на n = 3.",
                          "3 2": "Переменная цикла сохраняет значение, на котором сработал break, — 3."}),
        predict("py_loopx_002", "Пропуск кратных трём",
                "total = 0\nfor n in range(1, 8):\n    if n % 3 == 0:\n        continue\n    total += n\nprint(total)",
                ["28", "9", "0"], topic="loopx_break", hint="continue пропускает остаток шага.",
                explanation="3 и 6 пропущены, складываются 1 + 2 + 4 + 5 + 7 = 19.",
                feedback={"28": "28 — сумма всех чисел от 1 до 7, но кратные трём пропущены.",
                          "9": "9 — это как раз пропущенные 3 + 6.",
                          "0": "continue пропускает только кратные трём."}),
        fill("py_loopx_003", "Только первое", "Выведите только первое отрицательное число",
             "nums = [4, 7, -2, 5, -9]\nfor n in nums:\n    if n < 0:\n        print(n)\n        {{0}}",
             ["break", "continue", "pass", "return"], ["break"], topic="loopx_break",
             hint="После находки цикл нужно завершить.",
             explanation="break завершает цикл после первой находки. continue и pass позволили бы напечатать и -9.",
             expect="-2\n"),
        typed("py_loopx_004", "Лесенка вниз", "for i in range(3, 0, -1):\n    print(\"#\" * i)",
              topic="loop_range", hint="Шаг -1: i принимает значения 3, 2, 1. \"#\" * i — строка из i решёток.",
              explanation="range(3, 0, -1) — это 3, 2, 1 (0 не входит). На каждом шаге печатается строка из i решёток."),
        predict("py_loopx_005", "else у цикла",
                "for n in [3, 5, 7]:\n    if n % 2 == 0:\n        print(\"чётное\")\n        break\nelse:\n    print(\"все нечётные\")",
                ["чётное", "чётное\nвсе нечётные", "Ничего"], position=2, topic="loopx_else",
                hint="else выполняется, если цикл закончился без break.",
                explanation="Чётных нет, break не сработал, поэтому выполнилась ветка else.",
                role="practice", difficulty=2,
                feedback={"чётное": "В списке нет чётных чисел.",
                          "Ничего": "Цикл дошёл до конца без break — значит, выполняется else."}),
        multi("py_loopx_006", "Ровно три раза", "Какие циклы выполнят тело ровно 3 раза?",
              ["for i in range(3):", "for i in range(1, 3):", "for c in \"abc\":", "for i in range(0, 6, 2):",
               "for i in range(3, 0):", "for x in [0, 0, 0]:"], [0, 2, 3, 5],
              check=lambda header: iterations(header) == "3", topic="loop_range",
              hint="Посчитайте элементы каждой последовательности.",
              explanation="range(3) — 3 числа, «abc» — 3 буквы, range(0, 6, 2) — 0, 2, 4, список из трёх нулей — 3 элемента. range(1, 3) даёт 2 числа, range(3, 0) пустой.",
              feedback={"for i in range(1, 3):": "range(1, 3) — это 1 и 2, всего два шага.",
                        "for i in range(3, 0):": "При положительном шаге range(3, 0) пустой."}),
        match("py_loopx_008", "enumerate и zip",
              ["list(enumerate(\"ab\"))", "list(enumerate(\"ab\", start=1))", "list(zip([1, 2], \"xy\"))",
               "list(zip(\"ab\", [1, 2, 3]))"],
              topic="loopx_enumerate", hint="zip останавливается на самой короткой последовательности.",
              explanation="enumerate нумерует с 0 (или с start), zip склеивает элементы попарно и обрезает по короткой стороне."),
        bug("py_loopx_007", "На одно меньше",
            "total = 0\nfor i in range(1, 5):\n    total += i\nprint(total)", {1: "for i in range(1, 6):"},
            prompt="Нужна сумма чисел от 1 до 5 (15), а программа выводит 10. Найдите ошибку",
            topic="loop_range", hint="Входит ли stop в range?",
            explanation="range(1, 5) — это 1, 2, 3, 4. Чтобы включить 5, нужно range(1, 6)."),
        typed("py_loopx_011", "Таблица умножения", """\
              for i in range(1, 4):
                  row = ""
                  for j in range(1, 4):
                      row += str(i * j) + " "
                  print(row.strip())""", topic="loopx_nested",
              hint="Внутренний цикл собирает одну строку таблицы для каждого i.",
              explanation="Для каждого i внутренний цикл проходит j = 1, 2, 3 и добавляет i · j. strip убирает лишний пробел в конце строки.",
              role="practice", difficulty=2),
        typed("py_loopx_010", "while True и break", """\
              n = 6
              steps = 0
              while True:
                  if n == 1:
                      break
                  n = n // 2 if n % 2 == 0 else 3 * n + 1
                  steps += 1
              print(steps)""", topic="loopx_break",
              hint="Чётное делим пополам, нечётное — 3n + 1. Считайте шаги до 1.",
              explanation="6 → 3 → 10 → 5 → 16 → 8 → 4 → 2 → 1 — восемь шагов. while True повторяется бесконечно, пока break не прервёт цикл.",
              role="challenge", difficulty=3),
        order("py_loopx_009", "Босс: простые числа", "Соберите программу, которая выведет простые числа меньше 10",
              ["for n in range(2, 10):", "    for d in range(2, n):", "        if n % d == 0:", "            break",
               "    else:", "        print(n)"],
              topic="loopx_else", hint="else относится к внутреннему циклу: «делителей не нашли».",
              explanation="Для каждого n перебираем делители. Нашли делитель — break. Не нашли — срабатывает else внутреннего цикла и печатается n.",
              role="boss", difficulty=3),
    ],
))

# -------------------------------------------------------------------- lists
MODULES.append(dict(
    id="lists", title="Списки", description="Изменяемые последовательности", icon="📋",
    topics=[
        topic("list_basics", "Списки: основы",
              "Список — изменяемая упорядоченная коллекция: [1, 2, 3]. Индексы и срезы — как у строк.",
              """
              nums[0] — первый элемент, nums[-1] — последний, nums[1:3] — новый список из элементов с индексами 1 и 2. len(nums) — длина.

              В отличие от строки, элемент списка можно заменить: nums[0] = 10.

              Список может хранить что угодно, в том числе другие списки.
              """,
              [("nums = [10, 20, 30]\nnums[0] = 5\nprint(nums, nums[-1], nums[1:], len(nums))", None)],
              ["Обращаться к nums[len(nums)] — последний индекс равен len(nums) - 1."]),
        topic("list_methods", "Методы списков",
              "append, insert, extend, remove, pop, sort, reverse меняют список на месте и (кроме pop) возвращают None.",
              """
              append(x) добавляет в конец, insert(i, x) — на позицию i, extend(other) — все элементы другого списка. remove(x) удаляет первое вхождение, pop() — последний элемент и возвращает его.

              nums.sort() сортирует сам список и возвращает None. sorted(nums) возвращает новый отсортированный список, не трогая исходный.

              index(x) возвращает индекс первого вхождения x, count(x) — сколько раз x встречается. Если x нет в списке, index и remove вызывают ValueError — сначала проверяйте x in nums.

              min, max и sum работают с любым списком чисел.
              """,
              [("nums = [3, 1, 2]\nnums.append(5)\nnums.sort()\nlast = nums.pop()\nprint(nums, last)", None),
               ("nums = [3, 1, 2]\nprint(sorted(nums), nums)", "sorted не меняет исходный список.")],
              ["nums = nums.sort() — теперь в nums лежит None.",
               "append([4]) добавляет список как один элемент; для добавления всех элементов — extend.",
               "nums.remove(10), когда 10 нет в списке, — ValueError: list.remove(x): x not in list."]),
        topic("list_mutable", "Изменяемость и ссылки",
              "b = a не копирует список: оба имени ссылаются на один объект. Копия — a.copy() или a[:].",
              """
              Если изменить список через одно имя, изменение видно и через другое — это один и тот же объект.

              a.copy() и a[:] создают поверхностную копию: новый список с теми же элементами.

              is проверяет, один ли это объект; == — равны ли значения.
              """,
              [("a = [1, 2]\nb = a\nb.append(3)\nprint(a, a is b)", None),
               ("a = [1, 2]\nb = a.copy()\nb.append(3)\nprint(a, b, a == [1, 2])", None)],
              ["Ждать, что b = a создаст независимую копию.",
               "Писать x = y = [] — это один общий список под двумя именами.",
               "[[0] * 2] * 2 — два раза один и тот же внутренний список: изменение m[0][0] видно и в m[1][0].",
               "Удалять элементы из списка во время перебора этого же списка: часть элементов пропустится."]),
    ],
    tasks=[
        task("t_list_min_max", "Минимум и максимум",
             "В строке — целые числа через пробел. Выведите минимум и максимум через пробел.",
             solution="nums = list(map(int, input().split()))\nprint(min(nums), max(nums))",
             tests=["3 9 1 7\n", "5\n", "-2 -8 0\n", "9 10 2\n"],
             starter="nums = input().split()\nprint(min(nums), max(nums))",
             hint="Без int() числа сравниваются как строки: '9' > '10'.", difficulty=1),
        task("t_list_second_max", "Второй максимум",
             "В строке — целые числа через пробел (различных чисел минимум два). Выведите второе по величине различное число.",
             solution="nums = sorted(map(int, input().split()))\nbiggest = nums[-1]\nfor x in reversed(nums):\n    if x < biggest:\n        print(x)\n        break",
             starter="nums = sorted(map(int, input().split()))\nprint(nums[-2])",
             tests=["3 9 1 7\n", "5 5 4\n", "10 -1 10 3\n", "1 2\n", "7 7 7 2\n"],
             hint="Отсортируйте числа и идите с конца до первого числа, которое меньше максимума.", difficulty=2),
    ],
    levels=[
        predict("py_list_001", "Индекс и длина", "nums = [10, 20, 30]\nprint(nums[1], len(nums))",
                ["10 3", "20 2", "30 3"], position=1, topic="list_basics",
                hint="Индексы начинаются с 0.", explanation="nums[1] — второй элемент, 20; в списке 3 элемента.",
                feedback={"10 3": "10 — это nums[0].", "20 2": "len считает все элементы: их три."}),
        predict("py_list_002", "Добавление", "nums = [1, 2]\nnums.append(3)\nnums.append([4])\nprint(len(nums))",
                ["5", "3", "Ошибка"], position=0, topic="list_methods",
                hint="append добавляет ровно один элемент — каким бы он ни был.",
                explanation="После append(3) и append([4]) список [1, 2, 3, [4]] — четыре элемента, последний сам является списком.",
                feedback={"5": "append([4]) добавляет список целиком как один элемент.",
                          "Ошибка": "В список можно добавить любой объект, даже другой список."}),
        fill("py_list_003", "В конец списка", "Добавьте \"слива\" в конец списка",
             "fruits = [\"яблоко\", \"груша\"]\nfruits.{{0}}(\"слива\")\nprint(fruits)",
             ["append", "add", "insert", "push"], ["append"], topic="list_methods",
             hint="Метод, который добавляет элемент в конец.",
             explanation="append добавляет элемент в конец списка. add — метод множеств, push в Python нет, insert требует позицию.",
             expect="['яблоко', 'груша', 'слива']\n"),
        match("py_list_004", "Срезы списка", ["a[1:3]", "a[-2:]", "a[::2]", "a[::-1]", "a[:0]"],
              setup="a = [1, 2, 3, 4, 5]", topic="list_basics", hint="Срезы списков работают как у строк.",
              explanation="[1:3] — элементы 1 и 2; [-2:] — два последних; [::2] — через один; [::-1] — в обратном порядке; [:0] — пустой."),
        typed("py_list_005", "Одно имя, один список", "a = [1, 2]\nb = a\nb.append(3)\nprint(a)",
              topic="list_mutable", hint="b = a не копирует список.",
              explanation="a и b ссылаются на один список, поэтому append через b виден через a."),
        predict("py_list_006", "Копия", "a = [1, 2]\nb = a.copy()\nb.append(3)\nprint(a, b)",
                ["[1, 2, 3] [1, 2, 3]", "[1, 2] [1, 2]", "[1, 2, 3] [1, 2]"], position=1, topic="list_mutable",
                hint="copy() создаёт новый список.", explanation="b — независимая копия, поэтому изменился только b.",
                role="practice", difficulty=2,
                feedback={"[1, 2, 3] [1, 2, 3]": "Так было бы при b = a. copy() создал отдельный список.",
                          "[1, 2] [1, 2]": "append изменил копию b."}),
        multi("py_list_007", "Меняют на месте", "Какие вызовы меняют список nums и возвращают None?",
              ["nums.sort()", "sorted(nums)", "nums.append(4)", "nums.reverse()", "nums.copy()", "nums + [4]"],
              [0, 2, 3], check=mutates_in_place, topic="list_methods",
              hint="Какие вызовы возвращают новый список, а какие меняют сам nums?",
              explanation="sort, append и reverse изменяют сам список и возвращают None. sorted, copy и + возвращают новые списки.",
              feedback={"sorted(nums)": "sorted возвращает новый список, исходный не меняется.",
                        "nums.copy()": "copy создаёт новый список.",
                        "nums + [4]": "+ создаёт новый список, nums остаётся прежним."}),
        bug("py_list_008", "Пропавший список", "nums = [3, 1, 2]\nnums = nums.sort()\nprint(nums[0])",
            {1: "nums.sort()"}, topic="list_methods", hint="Что возвращает метод sort?",
            explanation="sort() сортирует список на месте и возвращает None. После nums = nums.sort() в nums лежит None, и nums[0] вызывает TypeError.",
            expect_error="TypeError"),
        predict("py_list_010", "Размноженный список", "m = [[0] * 2] * 2\nm[0][0] = 1\nprint(m)",
                ["[[1, 0], [0, 0]]", "[[1, 1], [0, 0]]", "TypeError"], position=1, topic="list_mutable",
                hint="* 2 повторяет ссылку на один и тот же внутренний список.",
                explanation="Внешний список содержит две ссылки на один и тот же список [0, 0]. Изменение через m[0] видно и через m[1]: [[1, 0], [1, 0]].",
                role="challenge", difficulty=3,
                feedback={"[[1, 0], [0, 0]]": "Внутренний список один на двоих: изменение видно в обеих строках.",
                          "[[1, 1], [0, 0]]": "Меняется только элемент с индексом 0 внутреннего списка.",
                          "TypeError": "Список можно умножать на число, а элементы — менять."}),
        typed("py_list_009", "Босс: операции со списком",
              "nums = [5, 3, 8, 1]\nnums.sort()\nnums.insert(0, 0)\nlast = nums.pop()\nprint(nums, last, nums.index(5))",
              topic="list_methods", hint="Выполните операции по очереди на бумаге.",
              explanation="После sort — [1, 3, 5, 8], insert(0, 0) — [0, 1, 3, 5, 8], pop() убирает и возвращает 8. Число 5 имеет индекс 3.",
              role="boss", difficulty=3),
    ],
))

# --------------------------------------------------------------- tuples_sets
MODULES.append(dict(
    id="tuples_sets", title="Кортежи и множества", description="Неизменяемые пары и уникальные значения",
    icon="🧩",
    topics=[
        topic("tuple_basics", "Кортежи",
              "Кортеж (1, 2) — неизменяемая последовательность. Удобен для пар и возврата нескольких значений.",
              """
              Кортеж нельзя изменить: t[0] = 1 — TypeError. Зато его можно распаковать: x, y = point.

              Кортеж делает запятая, а скобки только группируют: (5) — это просто число 5, а (5,) — кортеж из одного элемента. Исключение — пустой кортеж ().

              Кортеж хешируется, только если хешируются все его элементы: {(1, [2])} — TypeError: unhashable type: 'list'.
              """,
              [("point = (3, 4)\nx, y = point\nprint(x * y, type((5)).__name__, type((5,)).__name__)", None)],
              ["Забыть запятую в кортеже из одного элемента."]),
        topic("set_basics", "Множества",
              "Множество {1, 2, 3} хранит только уникальные элементы без порядка; проверка x in s очень быстрая.",
              """
              set(список) убирает повторы. Порядок элементов в множестве не гарантирован — для вывода лучше sorted().

              Элементы множества должны быть хешируемыми (неизменяемыми): числа, строки, кортежи. Список или словарь положить нельзя.

              {} — это пустой словарь, пустое множество — set().
              """,
              [("words = ['кот', 'пёс', 'кот']\nunique = set(words)\nprint(len(unique), sorted(unique), 'кот' in unique)", None)],
              ["Создавать пустое множество через {} — получится словарь."]),
        topic("set_ops", "Операции над множествами",
              "| — объединение, & — пересечение, - — разность, ^ — симметрическая разность.",
              """
              a | b — элементы из любого множества, a & b — общие, a - b — есть в a, но нет в b, a ^ b — есть ровно в одном из них.
              """,
              [("a = {1, 2, 3}\nb = {2, 3, 4}\nprint(sorted(a | b), sorted(a & b), sorted(a - b), sorted(a ^ b))", None)],
              ["Ждать, что множество сохранит порядок добавления."]),
    ],
    tasks=[
        task("t_set_common", "Общие слова",
             "В двух строках — слова через пробел. Выведите общие слова через пробел в порядке sorted() или «нет», если общих нет.",
             solution="a = set(input().split())\nb = set(input().split())\ncommon = sorted(a & b)\nprint(' '.join(common) if common else 'нет')",
             starter="a = input().split()\nb = input().split()\nprint('нет')",
             tests=["кот пёс мышь\nпёс ёж кот\n", "a b\nc d\n", "x\nx\n", "c b a\na b z\n"],
             hint="Пересечение множеств: a & b.", difficulty=2),
    ],
    levels=[
        predict("py_tup_001", "Распаковка", "point = (3, 4)\nx, y = point\nprint(x * y)", ["7", "(3, 4)", "34"],
                position=1, topic="tuple_basics", hint="x получает 3, y — 4.",
                explanation="Кортеж распаковывается в две переменные: 3 * 4 = 12.",
                feedback={"7": "Здесь умножение, а не сложение.", "34": "x и y — числа, их перемножают."}),
        predict("py_tup_003", "Запятая решает", "print(type((5)).__name__, type((5,)).__name__)",
                ["tuple tuple", "int int", "tuple int"], position=1, topic="tuple_basics",
                hint="Кортеж делает запятая, а не скобки.",
                explanation="(5) — просто число в скобках, (5,) — кортеж из одного элемента.", difficulty=2,
                feedback={"tuple tuple": "(5) без запятой — обычное число.",
                          "int int": "(5,) — кортеж: запятая делает кортеж."}),
        bug("py_tup_002", "Неизменяемый кортеж", "t = (1, 2, 3)\nt[0] = 10\nprint(t)", {1: "t = (10,) + t[1:]"},
            topic="tuple_basics", hint="Можно ли изменить элемент кортежа?",
            explanation="Кортеж неизменяем: присваивание t[0] вызывает TypeError. Можно собрать новый кортеж.",
            expect_error="TypeError"),
        predict("py_set_001", "Без повторов", "print(len({1, 2, 2, 3, 3, 3}))", ["6", "1", "2"], position=2,
                topic="set_basics", hint="Множество хранит только уникальные элементы.",
                explanation="Уникальных значений три: 1, 2 и 3.",
                feedback={"6": "Повторы в множество не попадают.", "1": "Уникальных значений больше одного."}),
        fill("py_set_004", "Пустое множество", "Создайте пустое множество",
             "s = {{0}}\ns.add(1)\nprint(len(s))", ["set()", "{}", "[]", "()"], ["set()"], topic="set_basics",
             hint="{} создаёт не множество.",
             explanation="set() — пустое множество. {} — пустой словарь, у него нет метода add.", expect="1\n"),
        match("py_set_002", "Операции над множествами",
              ["sorted(a | b)", "sorted(a & b)", "sorted(a - b)", "sorted(a ^ b)", "3 in a"],
              setup="a = {1, 3, 5, 7}\nb = {3, 4, 5}", topic="set_ops",
              hint="| — все, & — общие, - — только из a, ^ — ровно в одном.",
              explanation="Объединение — все шесть чисел, пересечение — 3 и 5, разность — 1 и 7, симметрическая разность — 1, 4 и 7; 3 есть в a."),
        multi("py_set_003", "Что можно в множество", "Какие значения можно добавить в множество?",
              ["5", "'текст'", "(1, 2)", "[1, 2]", "{1: 2}", "3.5"], [0, 1, 2, 5], check=hashable,
              topic="set_basics", hint="Подходят только неизменяемые (хешируемые) значения.",
              explanation="Числа, строки и кортежи хешируемы. Список и словарь изменяемы — TypeError: unhashable type.",
              feedback={"[1, 2]": "Список изменяем и не хешируется.",
                        "{1: 2}": "Словарь изменяем и не хешируется."}),
        typed("py_set_005", "Босс: уникальные слова",
              "words = \"кот пёс кот мышь пёс кот\".split()\nunique = set(words)\nprint(len(words), len(unique), \", \".join(sorted(unique)))",
              topic="set_basics", hint="Сколько всего слов и сколько разных? sorted упорядочит по алфавиту.",
              explanation="Слов шесть, разных три. sorted расставляет их по алфавиту: кот, мышь, пёс.",
              role="boss", difficulty=3),
    ],
))

# -------------------------------------------------------------------- dicts
MODULES.append(dict(
    id="dicts", title="Словари", description="Ключ → значение", icon="📒",
    topics=[
        topic("dict_basics", "Словари: основы",
              "Словарь хранит пары ключ → значение: {\"Ада\": 36}. Доступ по ключу — d[ключ].",
              """
              Ключи уникальны: если ключ повторить, останется последнее значение. Ключом может быть любое хешируемое значение (строка, число, кортеж).

              d[k] = v добавляет пару или заменяет значение. Обращение к несуществующему ключу через d[k] вызывает KeyError.

              Словари сохраняют порядок добавления ключей.
              """,
              [("ages = {'Ада': 36, 'Алан': 41}\nages['Грейс'] = 85\nprint(ages['Алан'], len(ages))", None),
               ("d = {'x': 1, 'x': 2}\nprint(d)", "Повторный ключ перезаписал значение.")],
              ["Обращаться к отсутствующему ключу через [] — KeyError."]),
        topic("dict_methods", "Методы словарей",
              "get, keys, values, items, pop, update, setdefault — основные операции.",
              """
              d.get(k, default) возвращает default, если ключа нет — без ошибки. Без default get возвращает None.

              d.pop(k) удаляет ключ и возвращает его значение. d.update(other) добавляет пары из другого словаря, перезаписывая совпадающие ключи. d.setdefault(k, v) возвращает d[k], а если ключа нет — сначала записывает d[k] = v.

              for k, v in d.items(): — перебор пар; for k in d: — перебор ключей; d.values() — значения.

              k in d проверяет наличие ключа (а не значения).
              """,
              [("prices = {'чай': 3, 'кофе': 5}\nfor name, price in prices.items():\n    print(name, price)\nprint(prices.get('сок', 0), 'чай' in prices, 3 in prices)", None)],
              ["Проверять 3 in d, ожидая поиск по значениям: in смотрит только ключи.",
               "Удалять или добавлять ключи во время перебора словаря — RuntimeError: dictionary changed size during iteration. Перебирайте копию: for k in list(d)."]),
        topic("dict_counting", "Подсчёт с помощью словаря",
              "Частый шаблон: counts[x] = counts.get(x, 0) + 1.",
              """
              Так считают, сколько раз встречается каждое слово или буква. get(x, 0) даёт 0 для нового ключа.

              В стандартной библиотеке для этого есть collections.Counter — он делает то же самое одной строкой.
              """,
              [("counts = {}\nfor ch in 'abracadabra':\n    counts[ch] = counts.get(ch, 0) + 1\nprint(counts)", None)],
              ["counts[ch] += 1 без инициализации — KeyError на первом же новом символе."]),
    ],
    tasks=[
        task("t_dict_word_count", "Самое частое слово",
             "Прочитайте строку слов через пробел. Выведите самое частое слово и сколько раз оно встретилось. Если таких несколько — то, которое идёт первым в порядке sorted().",
             solution="counts = {}\nfor w in input().split():\n    counts[w] = counts.get(w, 0) + 1\nbest = None\nfor w in sorted(counts):\n    if best is None or counts[w] > counts[best]:\n        best = w\nprint(best, counts[best])",
             starter="words = input().split()\nprint(words[0], 1)",
             tests=["кот пёс кот\n", "b a b a\n", "один\n", "x y z y z\n"],
             hint="Посчитайте слова в словаре, затем пройдите по sorted(counts) и запоминайте слово, у которого частота строго больше лучшей.", difficulty=3),
        task("t_dict_phonebook", "Телефонная книга",
             "В первой строке n — число записей, затем n строк «имя номер», затем строка с именем для поиска. Выведите номер или «не найдено».",
             solution="n = int(input())\nbook = {}\nfor _ in range(n):\n    name, phone = input().split()\n    book[name] = phone\nprint(book.get(input().strip(), 'не найдено'))",
             starter="n = int(input())\nfor _ in range(n):\n    input()\nprint('не найдено')",
             tests=["2\nАда 123\nАлан 456\nАлан\n", "1\nБоб 7\nЕва\n", "3\na 1\nb 2\nc 3\na\n", "2\nx 1\nx 2\nx\n"],
             hint="Сохраните записи в словарь и используйте get со значением по умолчанию.", difficulty=2),
    ],
    levels=[
        predict("py_dict_001", "Значение по ключу", "ages = {\"Ада\": 36, \"Алан\": 41}\nprint(ages[\"Алан\"])",
                ["36", "Алан", "KeyError"], position=1, topic="dict_basics", hint="d[ключ] возвращает значение.",
                explanation="По ключу «Алан» хранится 41.",
                feedback={"36": "36 — значение для ключа «Ада».", "Алан": "По ключу возвращается значение, а не ключ."}),
        predict("py_dict_002", "Без ошибки", "ages = {\"Ада\": 36, \"Алан\": 41}\nprint(ages.get(\"Боб\", 0), len(ages))",
                ["KeyError", "None 2", "0 3"], position=1, topic="dict_methods",
                hint="get не вызывает ошибку для отсутствующего ключа.",
                explanation="Ключа «Боб» нет, get возвращает значение по умолчанию 0. Словарь не изменился — в нём 2 пары.",
                feedback={"KeyError": "KeyError вызвал бы ages[\"Боб\"], а get безопасен.",
                          "None 2": "None возвращается, только если default не передан.",
                          "0 3": "get ничего не добавляет в словарь."}),
        fill("py_dict_003", "Пары ключ-значение", "Переберите словарь парами «название цена»",
             "prices = {\"чай\": 3, \"кофе\": 5}\nfor name, price in prices.{{0}}():\n    print(name, price)",
             ["items", "keys", "values", "get"], ["items"], topic="dict_methods",
             hint="Нужен метод, который отдаёт пары.",
             explanation="items() отдаёт кортежи (ключ, значение), которые распаковываются в name и price.",
             expect="чай 3\nкофе 5\n"),
        match("py_dict_006", "Что внутри словаря", ["list(d)", "list(d.values())", "\"a\" in d", "1 in d", "len(d)"],
              setup="d = {\"a\": 1, \"b\": 2}", topic="dict_methods",
              hint="list(d) и in работают с ключами.",
              explanation="list(d) — список ключей, values() — значения, in ищет среди ключей, поэтому 1 in d — False; пар две."),
        predict("py_dict_007", "Повторный ключ", "d = {\"a\": 1, \"b\": 2, \"a\": 3}\nprint(d)",
                ["{'a': 1, 'b': 2}", "{'b': 2, 'a': 3}", "SyntaxError"], position=1, topic="dict_basics",
                hint="Ключи в словаре уникальны. Где окажется перезаписанный ключ?",
                explanation="Второе значение для ключа «a» перезаписывает первое, но ключ остаётся на своём первоначальном месте.",
                role="practice", difficulty=2,
                feedback={"{'a': 1, 'b': 2}": "Последнее значение для ключа побеждает: a = 3.",
                          "{'b': 2, 'a': 3}": "Перезапись значения не переносит ключ в конец: он остаётся первым.",
                          "SyntaxError": "Это корректный код: ключ просто перезаписывается."}),
        bug("py_dict_009", "Удаление на ходу", """\
            prices = {"чай": 0, "кофе": 5, "сок": 0}
            for name in prices:
                if prices[name] == 0:
                    del prices[name]
            print(prices)""", {1: "for name in list(prices):"},
            prompt="Нужно удалить товары с нулевой ценой. Найдите строку с ошибкой", topic="dict_methods",
            hint="Можно ли менять размер словаря, пока по нему идёт цикл?",
            explanation="Удаление ключа во время перебора словаря вызывает RuntimeError: dictionary changed size during iteration. list(prices) делает копию ключей, и перебор идёт по ней.",
            expect_error="RuntimeError", role="challenge", difficulty=3),
        typed("py_dict_005", "Подсчёт букв",
              "counts = {}\nfor ch in \"abracadabra\":\n    counts[ch] = counts.get(ch, 0) + 1\nprint(counts[\"a\"], counts[\"b\"], len(counts))",
              topic="dict_counting", hint="Посчитайте каждую букву в abracadabra.",
              explanation="a встречается 5 раз, b — 2 раза, разных букв пять: a, b, r, c, d."),
        bug("py_dict_004", "Нет такого ключа", "stock = {\"apple\": 3}\nprint(stock[\"pear\"])",
            {1: "print(stock.get(\"pear\", 0))"}, prompt="Если товара нет, программа должна вывести 0. Найдите ошибку",
            topic="dict_methods", hint="Что будет при обращении к отсутствующему ключу через []?",
            explanation="stock[\"pear\"] вызывает KeyError. get(\"pear\", 0) вернёт 0.", expect_error="KeyError"),
        order("py_dict_008", "Босс: длины слов", "Соберите программу, которая выведет «6 3»",
              ["words = [\"кот\", \"собака\", \"ёж\"]", "lengths = {}", "for w in words:", "    lengths[w] = len(w)",
               "print(lengths[\"собака\"], len(lengths))"],
              topic="dict_basics", hint="Словарь нужно создать до цикла, а вывести — после.",
              explanation="Создаём пустой словарь, в цикле записываем длину каждого слова, в конце выводим длину «собака» и число ключей.",
              role="boss", difficulty=3),
    ],
))

# ------------------------------------------------------------ comprehensions
MODULES.append(dict(
    id="comprehensions", title="Включения", description="Списки, словари и множества в одну строку (comprehensions)",
    icon="⚡",
    topics=[
        topic("comp_list", "Списковые включения",
              "[выражение for x in последовательность] строит новый список за одну строку.",
              """
              [x * 2 for x in range(4)] — то же, что цикл с append, но короче и быстрее.

              Можно перебирать несколько последовательностей: [f"{a}{b}" for a in "xy" for b in "12"] — циклы вложены слева направо.
              """,
              [("print([x * 2 for x in range(4)])", None),
               ("print([f'{a}{b}' for a in 'xy' for b in '12'])", "Первый for — внешний цикл.")],
              ["Писать слишком сложные включения: если не помещается в строку, лучше обычный цикл."]),
        topic("comp_cond", "Фильтр и условие",
              "[x for x in seq if условие] — фильтр; [a if усл else b for x in seq] — выбор значения.",
              """
              if в конце отбирает элементы: [x for x in range(10) if x % 2 == 0].

              Условное выражение стоит в начале и меняет значение, а не отбирает: ["чёт" if x % 2 == 0 else "нечет" for x in range(3)].

              Перепутать места нельзя: [x for x in nums if x > 0 else 0] — синтаксическая ошибка.
              """,
              [("nums = [3, -1, 5]\nprint([x for x in nums if x > 0])\nprint([x if x > 0 else 0 for x in nums])", None)],
              ["Ставить if ... else ... в конец включения."]),
        topic("comp_dict_set", "Включения для словарей и множеств, генераторные выражения",
              "{k: v for ...} — словарь, {x for ...} — множество, (x for ...) — ленивый генератор.",
              """
              Фигурные скобки с двоеточием создают словарь, без двоеточия — множество.

              Круглые скобки создают генераторное выражение: значения вычисляются по одному, когда их запрашивают. Часто передают прямо в функцию: sum(x * x for x in range(4)).
              """,
              [("words = ['apple', 'kiwi', 'fig']\nprint({w: len(w) for w in words})\nprint({len(w) for w in words})\nprint(sum(len(w) for w in words))", None)],
              ["(x for x in ...) — это не кортеж, а генераторное выражение.",
               "Генераторное выражение одноразовое: второй sum(g) по тому же g даст 0."]),
    ],
    tasks=[
        task("t_comp_even_squares", "Квадраты чётных",
             "Прочитайте n и выведите через пробел квадраты всех чётных чисел от 0 до n включительно.",
             solution="n = int(input())\nprint(' '.join(str(x * x) for x in range(0, n + 1, 2)))",
             starter="n = int(input())\nprint(n * n)",
             tests=["6\n", "0\n", "9\n", "2\n"], hint="Включение + ' '.join(str(...)).", difficulty=2,
             requires=dict(uses=["comprehension"])),
    ],
    levels=[
        predict("py_comp_001", "Утроение", "print([x * 3 for x in range(1, 4)])",
                ["[1, 2, 3]", "[0, 3, 6]", "[3, 6, 9, 12]"], position=1, topic="comp_list",
                hint="range(1, 4) — 1, 2, 3.", explanation="Каждое число от 1 до 3 умножается на 3.",
                feedback={"[1, 2, 3]": "Каждый x умножается на 3.",
                          "[0, 3, 6]": "range(1, 4) начинается с 1.",
                          "[3, 6, 9, 12]": "В range(1, 4) нет числа 4."}),
        fill("py_comp_002", "Только чётные", "Оставьте в списке только чётные числа",
             "evens = [x for x in range(10) {{0}} x % 2 == 0]\nprint(evens)", ["if", "and", "while", "for"], ["if"],
             topic="comp_cond", hint="Фильтр во включении задаётся словом из условий.",
             explanation="if в конце включения отбирает элементы.", expect="[0, 2, 4, 6, 8]\n"),
        match("py_comp_003", "Какие скобки?",
              ["[c.upper() for c in \"ab\"]", "{x: x * x for x in range(3)}", "{len(w) for w in [\"a\", \"bb\", \"cc\"]}",
               "[x for x in range(5) if x > 2]", "sum(x for x in range(4))"],
              topic="comp_dict_set", hint="Двоеточие внутри фигурных скобок — словарь.",
              explanation="Квадратные скобки — список, фигурные с двоеточием — словарь, без двоеточия — множество (повторы убираются), генератор в sum складывает 0 + 1 + 2 + 3."),
        typed("py_comp_004", "Пары", "pairs = [f\"{i}{j}\" for i in range(1, 3) for j in range(1, 3)]\nprint(\" \".join(pairs))",
              topic="comp_list", hint="Первый for — внешний цикл.",
              explanation="Для i = 1: 11, 12; для i = 2: 21, 22."),
        predict("py_comp_005", "Чёт или нечет", "print([\"чёт\" if n % 2 == 0 else \"нечет\" for n in range(3)])",
                ["['нечет', 'чёт', 'нечет']", "['чёт', 'чёт']", "SyntaxError"], position=0, topic="comp_cond",
                hint="0 — чётное число.", explanation="Для 0 и 2 — «чёт», для 1 — «нечет».",
                role="practice", difficulty=2,
                feedback={"['нечет', 'чёт', 'нечет']": "Ноль чётный.",
                          "['чёт', 'чёт']": "Условие в начале не отбирает, а выбирает значение — элементов три.",
                          "SyntaxError": "if ... else в начале включения — корректный синтаксис."}),
        multi("py_comp_007", "Квадраты", "Какие выражения дают список [0, 1, 4]?",
              ["[x * x for x in range(3)]", "list(x ** 2 for x in range(3))", "[x ** 2 for x in [0, 1, 2]]",
               "{x * x for x in range(3)}", "(x * x for x in range(3))", "[x * 2 for x in range(3)]"], [0, 1, 2],
              check=lambda expr: eval(expr) == [0, 1, 4], topic="comp_dict_set",
              hint="Нужен именно список, а не множество или генератор.",
              explanation="Первые три дают список [0, 1, 4]. Фигурные скобки дают множество, круглые — генератор, x * 2 — удвоение.",
              feedback={"{x * x for x in range(3)}": "Фигурные скобки создают множество, а не список.",
                        "(x * x for x in range(3))": "Круглые скобки создают генератор, а не список.",
                        "[x * 2 for x in range(3)]": "x * 2 — удвоение: [0, 2, 4]."}),
        bug("py_comp_006", "Перепутанное условие", "nums = [3, -1, 5]\nresult = [x for x in nums if x > 0 else 0]\nprint(result)",
            {1: "result = [x if x > 0 else 0 for x in nums]"},
            prompt="Отрицательные числа нужно заменить нулями. Найдите строку с ошибкой", topic="comp_cond",
            hint="Где во включении стоит условное выражение с else?",
            explanation="Условное выражение с else ставится в начало, перед for. if в конце только фильтрует и не может иметь else.",
            expect_error="SyntaxError"),
        predict("py_comp_009", "Одноразовый генератор", "g = (x * x for x in range(4))\nprint(sum(g), sum(g))",
                ["14 14", "0 14", "TypeError"], position=1, topic="comp_dict_set",
                hint="Генераторное выражение выдаёт значения один раз.",
                explanation="Первый sum забирает все значения 0 + 1 + 4 + 9 = 14. Генератор исчерпан, второй sum получает пустую последовательность — 0.",
                role="challenge", difficulty=3,
                feedback={"14 14": "Генератор нельзя пройти второй раз: он уже исчерпан.",
                          "0 14": "Первым считается первый sum — он получает все значения.",
                          "TypeError": "sum принимает генератор, ошибки нет."}),
        predict("py_comp_008", "Босс: словарь длин",
                "words = [\"apple\", \"kiwi\", \"banana\", \"fig\"]\nby_len = {w: len(w) for w in words if len(w) > 3}\nprint(by_len)",
                ["{'apple': 5, 'kiwi': 4, 'banana': 6, 'fig': 3}", "{5: 'apple', 4: 'kiwi', 6: 'banana'}",
                 "['apple', 'kiwi', 'banana']"], position=2, topic="comp_dict_set",
                hint="Фильтр отбрасывает слова из 3 букв и короче. Ключ — слово.",
                explanation="fig отфильтрован (3 буквы). Ключи — слова, значения — длины, порядок как в списке.",
                role="boss", difficulty=3,
                feedback={"{'apple': 5, 'kiwi': 4, 'banana': 6, 'fig': 3}": "Условие len(w) > 3 отбрасывает fig.",
                          "{5: 'apple', 4: 'kiwi', 6: 'banana'}": "Ключ — то, что слева от двоеточия: слово.",
                          "['apple', 'kiwi', 'banana']": "Фигурные скобки с двоеточием создают словарь."}),
    ],
))
