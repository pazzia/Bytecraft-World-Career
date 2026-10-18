"""Модули 7–12: циклы, управление циклами, списки, кортежи и множества,
словари, генераторы коллекций."""
from bclib import choice, fill, match, multi, order, predict, bug, typed, topic, task, run, pitfall


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
              "Цикл `for` перебирает элементы последовательности по одному и для каждого выполняет тело.",
              """
              Многие задачи звучат как «сделать для каждого»: для каждой буквы в слове, каждого числа в списке, каждой строки файла. Для этого есть `for`.

              ## Как записать

              ```syntax
              for переменная in последовательность:
                  тело
              ```

              - последовательность — строка, список, [[loop_range|`range`]] и другие коллекции
              - на каждом шаге переменная получает следующий элемент
              - тело пишут с отступом; строки без отступа выполнятся один раз, после цикла

              ## Как выполняется

              1. Python берёт первый элемент и связывает с ним переменную.
              2. Выполняет тело.
              3. Берёт следующий элемент и повторяет, пока элементы не кончатся.

              ## Накопление результата

              Частый шаблон — сумма или счётчик:

              1. до цикла заводят `total = 0`;
              2. в теле прибавляют: `total += n`;
              3. после цикла выводят `total`.

              Если поставить `total = 0` внутрь цикла, сумма будет обнуляться на каждом шаге.
              """,
              [("""\
                for letter in "кот":
                    print(letter)
                print("готово")""",
                "Тело выполнилось трижды, строка без отступа — один раз"),
               ("""\
                prices = [120, 45, 300]
                total = 0
                for price in prices:
                    total += price
                print(total)""",
                "Сумма заведена до цикла и растёт в теле"),
               ("""\
                count = 0
                for ch in "абракадабра":
                    if ch == "а":
                        count += 1
                print(count)""",
                "Счётчик: сколько раз встретилась буква")],
              [pitfall("Итог печатается на каждом шаге: `print` стоит с отступом внутри цикла.",
                       bad="for n in nums:\n    total += n\n    print(total)",
                       good="for n in nums:\n    total += n\nprint(total)"),
               pitfall("Сумма внутри цикла обнуляется на каждом шаге.",
                       bad="for n in nums:\n    total = 0\n    total += n",
                       good="total = 0\nfor n in nums:\n    total += n"),
               pitfall("Число не перебирается: TypeError: 'int' object is not iterable. Нужен `range`.",
                       bad="for i in 3:\n    print(i)",
                       good="for i in range(3):\n    print(i)")]),
        topic("loop_range", "range",
              "`range` выдаёт последовательность целых чисел от `start` до `stop`, не включая `stop`.",
              """
              Когда нужно повторить действие n раз или перебрать числа по порядку, используют `range`. Его почти всегда пишут в паре с [[loop_for|for]].

              ## Как записать

              ```syntax
              range(стоп)
              range(старт, стоп)
              range(старт, стоп, шаг)
              ```

              - `старт` по умолчанию `0`, `шаг` — `1`
              - `стоп` не входит: `range(1, 5)` — это 1, 2, 3, 4
              - числа от 1 до n включительно — `range(1, n + 1)`

              | Вызов | Числа |
              |---|---|
              | {`range(6)`} | 0, 1, 2, 3, 4, 5 |
              | {`range(3, 7)`} | 3, 4, 5, 6 |
              | {`range(0, 20, 5)`} | 0, 5, 10, 15 |
              | {`range(10, 0, -3)`} | 10, 7, 4, 1 |
              | {`range(5, 5)`} | пусто |

              ## Отрицательный шаг

              С отрицательным шагом числа идут вниз, а `стоп` по-прежнему не входит. Если `старт` уже за `стопом` по направлению шага, `range` пустой: `range(5, 1)` ничего не выдаст.

              ## Это не список

              `range` не хранит все числа, а выдаёт их по одному. Поэтому `range(1_000_000)` почти не занимает памяти. Чтобы увидеть числа сразу, их собирают в [[list_basics|список]]: `list(range(3, 7))`.
              """,
              [("""\
                for i in range(3, 7):
                    print(i)""",
                "Начало входит, конец — нет"),
               ("""\
                print(list(range(0, 20, 5)))
                print(list(range(10, 0, -3)))""",
                "Шаг вверх и шаг вниз"),
               ("""\
                n = 4
                total = 0
                for i in range(1, n + 1):
                    total += i * i
                print(total)""",
                "range(1, n + 1) включает само n: 1 + 4 + 9 + 16"),
               ("""\
                print(list(range(5, 1)))
                print(len(range(100)))""",
                "Пустой range и длина без создания списка")],
              [pitfall("Неделя — дни с 1 по 7, а `range(1, 7)` остановится на 6: `stop` не входит.",
                       bad="for day in range(1, 7):\n    print(day)",
                       good="for day in range(1, 8):\n    print(day)"),
               pitfall("Чтобы идти вниз, нужен отрицательный шаг: `range(5, 0)` пустой.",
                       bad="for i in range(5, 0):\n    print(i)",
                       good="for i in range(5, 0, -1):\n    print(i)"),
               pitfall("`range` принимает только целые: TypeError: 'float' object cannot be interpreted as an integer.",
                       bad="for i in range(n / 2):\n    print(i)",
                       good="for i in range(n // 2):\n    print(i)")]),
        topic("loop_while", "Цикл while",
              "Цикл `while` повторяет тело, пока условие истинно, и проверяет его перед каждым шагом.",
              """
              Иногда заранее неизвестно, сколько будет шагов: спрашивать пароль, пока не введут верный, или копить, пока не хватит денег. Для таких задач есть `while`.

              ## Как записать

              ```syntax
              while условие:
                  тело
              ```

              1. Python проверяет условие.
              2. Если оно истинно — выполняет тело и возвращается к шагу 1.
              3. Если ложно — переходит к строке после цикла.

              Если условие ложно с самого начала, тело не выполнится ни разу.

              ## Цикл должен закончиться

              Тело обязано менять то, от чего зависит условие. Иначе цикл станет бесконечным и программа зависнет. В задачах курса такую программу остановит ограничение по времени.

              ## while True и break

              Когда условие выхода удобнее проверить в середине шага, пишут `while True` и выходят через [[loopx_break|break]]:

              ```syntax
              while True:
                  строка = input()
                  if условие_выхода:
                      break
                  обработка
              ```

              Так читают ввод, пока не придёт, например, слово «стоп».

              ## Что выбрать

              - известно, что перебирать или сколько раз, — `for`
              - повторять, пока что-то не случится, — `while`
              """,
              [("""\
                balance = 1000
                years = 0
                while balance < 2000:
                    balance *= 1.1
                    years += 1
                print(years)""",
                "Сколько лет копить: число шагов заранее неизвестно"),
               ("""\
                total = 0
                while True:
                    line = input()
                    if line == "стоп":
                        break
                    total += int(line)
                print(total)""",
                "Ввели 5, 10 и «стоп»: числа читаются до слова-сигнала",
                {"stdin": "5\n10\nстоп\n"}),
               ("""\
                n = 0
                while n > 0:
                    print("не выполнится")
                print("цикл пропущен")""",
                "Условие ложно сразу — тело не выполнилось ни разу")],
              [pitfall("Переменная условия не меняется — цикл бесконечный.",
                       bad="i = 0\nwhile i < 5:\n    print(i)",
                       good="i = 0\nwhile i < 5:\n    print(i)\n    i += 1"),
               pitfall("Перебор по счётчику: `for` с `range` короче и не забудет `i += 1`.",
                       bad="i = 0\nwhile i < 3:\n    print(i)\n    i += 1",
                       good="for i in range(3):\n    print(i)")]),
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
              "`break` сразу завершает цикл, а `continue` пропускает остаток текущего шага и переходит к следующему.",
              """
              Не каждый цикл нужно доводить до конца. Если нужное уже найдено, перебирать дальше незачем. А неподходящий элемент удобно отбросить в самом начале шага.

              ## Как записать

              ```syntax
              for элемент in последовательность:
                  if нашли:
                      break
                  if не_подходит:
                      continue
                  обработка
              ```

              - `break` — выйти из цикла; следующей выполнится строка после него
              - `continue` — бросить текущий шаг и взять следующий элемент

              Оба работают и в `for`, и в [[loop_while|while]].

              ## Только ближайший цикл

              Во [[loopx_nested|вложенных циклах]] `break` и `continue` действуют только на тот цикл, в котором стоят. Внешний цикл продолжит работу.

              ## Что остаётся после break

              Переменная цикла сохраняет значение, на котором цикл прервался. А `while True` без `break` не закончится никогда: внутри функции из него выходят ещё через `return`, иначе — только через `break`.
              """,
              [("""\
                pets = ["кот", "ёж", "лис"]
                for p in pets:
                    if p == "ёж":
                        print("нашли ежа")
                        break
                    print("проверили", p)""",
                "После находки цикл остановился, «лис» не проверялся"),
               ("""\
                scores = [5, -1, 3, -2, 4]
                total = 0
                for s in scores:
                    if s < 0:
                        continue
                    total += s
                print(total)""",
                "Отрицательные пропущены, сложились только 5, 3 и 4"),
               ("""\
                for i in range(3):
                    for j in range(3):
                        if j == 1:
                            break
                        print(i, j)""",
                "break прервал только внутренний цикл")],
              [pitfall("`continue` стоит до `i += 1`, и счётчик перестаёт расти — цикл бесконечный.",
                       bad="i = 0\nwhile i < 5:\n    if i == 2:\n        continue\n    i += 1",
                       good="i = 0\nwhile i < 5:\n    i += 1\n    if i == 2:\n        continue"),
               "Ждать, что `break` выйдет сразу из всех вложенных циклов: он прерывает только ближайший."]),
        topic("loopx_else", "else у цикла",
              "Ветка `else` у цикла выполняется, если цикл закончился сам, без `break`.",
              """
              Частая задача — найти элемент и сообщить, если его нет. Без `else` для этого заводят переменную-флаг `found = False`. `else` у цикла делает то же короче.

              ## Как записать

              ```syntax
              for элемент in последовательность:
                  if нашли:
                      break
              else:
                  действия_если_не_нашли
              ```

              `else` стоит на одном уровне с `for`, а не с `if`.

              ## Когда выполняется

              - цикл дошёл до конца — `else` выполняется
              - цикл прервал [[loopx_break|break]] — `else` пропускается
              - последовательность пустая — `else` выполняется: `break` не было

              Удобно читать `else` у цикла как «если не было `break`».

              ## У while тоже есть else

              У [[loop_while|while]] `else` работает так же: выполняется, когда условие стало ложным, и пропускается при выходе через `break`.
              """,
              [("""\
                guests = ["Ада", "Алан", "Грейс"]
                for g in guests:
                    if g == "Линус":
                        print("Линус пришёл")
                        break
                else:
                    print("Линуса нет")""",
                "break не случился — сработал else"),
               ("""\
                nums = [7, 11, 12, 13]
                for n in nums:
                    if n % 2 == 0:
                        print("чётное:", n)
                        break
                else:
                    print("чётных нет")""",
                "Нашли — break, и else пропущен"),
               ("""\
                tries = 3
                while tries > 0:
                    if input() == "1234":
                        print("Вход")
                        break
                    tries -= 1
                else:
                    print("Попытки кончились")""",
                "while с else: три неверных пароля подряд",
                {"stdin": "0000\n1111\n2222\n"})],
              [pitfall("`else` с отступом относится к `if` и печатает на каждом шаге. У цикла `else` — на уровне `for`.",
                       bad="for n in nums:\n    if n < 0:\n        break\n    else:\n        print(\"нет\")",
                       good="for n in nums:\n    if n < 0:\n        break\nelse:\n    print(\"нет\")"),
               "Считать, что `else` у цикла значит «не было ни одного шага»: он срабатывает при любом завершении без `break`."]),
        topic("loopx_nested", "Вложенные циклы",
              "Во вложенном цикле внутренний цикл проходит целиком на каждом шаге внешнего.",
              """
              Таблицы, пары, клетки игрового поля — это данные «в два измерения». Чтобы обойти все строки и в каждой все клетки, один цикл ставят внутрь другого.

              ## Как записать

              ```syntax
              for строка in строки:
                  for клетка in строка:
                      действия
                  после_каждой_строки
              ```

              Тело внутреннего цикла сдвинуто ещё на один уровень. Строка на уровне внешнего тела выполняется после каждого полного прохода внутреннего цикла.

              ## Сколько раз выполнится тело

              Если внешний цикл делает 3 шага, а внутренний — 4, тело внутреннего выполнится 3 × 4 = 12 раз. Поэтому вложенные циклы по большим данным работают медленно, подробнее — в теме [[algo_complexity|Сложность алгоритма]].

              ## Выход сразу из двух циклов

              [[loopx_break|break]] прерывает только внутренний цикл. Чтобы остановить оба, используют флаг:

              1. до циклов заводят `found = False`;
              2. при находке ставят `found = True` и делают `break`;
              3. во внешнем цикле после внутреннего проверяют `if found: break`.

              Короче выйти через `return`, если циклы стоят внутри [[func_def|функции]].
              """,
              [("""\
                for i in range(2):
                    for j in range(3):
                        print(i, j)""",
                "На каждый i внутренний цикл прошёл j = 0, 1, 2"),
               ("""\
                board = ["X.O", ".X.", "O.X"]
                for row in board:
                    for cell in row:
                        print(cell, end=" ")
                    print()""",
                "Внутренний цикл идёт по клеткам, print() завершает строку"),
               ("""\
                board = ["X.O", ".X.", "O.X"]
                found = False
                for r in range(3):
                    for c in range(3):
                        if board[r][c] == "O":
                            found = True
                            break
                    if found:
                        break
                print(r, c)""",
                "Флаг found остановил и внешний цикл на первой «O»")],
              [pitfall("Одно имя у двух циклов: внутренний затирает значение внешнего.",
                       bad="for i in range(3):\n    for i in range(2):\n        print(i)",
                       good="for i in range(3):\n    for j in range(2):\n        print(i, j)"),
               pitfall("Строку начинают заново внутри внешнего цикла, иначе она копится через все проходы.",
                       bad="row = \"\"\nfor i in range(3):\n    for j in range(3):\n        row += \"#\"\n    print(row)",
                       good="for i in range(3):\n    row = \"\"\n    for j in range(3):\n        row += \"#\"\n    print(row)"),
               "Ждать, что `break` во внутреннем цикле остановит и внешний: нужен флаг или `return`."]),
        topic("loopx_enumerate", "enumerate и zip",
              "`enumerate` добавляет к элементам номера, а `zip` перебирает несколько последовательностей параллельно.",
              """
              При переборе часто нужен номер элемента («1. Ада, 2. Алан») или пара значений из двух списков: имя и оценка. `enumerate` и `zip` дают это без индексов и `range(len(…))`.

              ## Как записать

              ```syntax
              for номер, элемент in enumerate(последовательность):
                  действия
              for a, b in zip(первая, вторая):
                  действия
              ```

              - `enumerate` даёт пары «номер, элемент»; номер с `0`, а `start=1` — с единицы
              - `zip` выдаёт пары из элементов, стоящих на одинаковых местах

              Каждая пара — [[tuple_basics|кортеж]] вроде `(0, 'a')`. Запись `номер, элемент` раскладывает его на два имени, как при [[var_multi|множественном присваивании]].

              ## zip останавливается раньше

              Если последовательности разной длины, `zip` остановится на самой короткой, а лишние элементы молча пропадут. С `strict=True` вместо этого будет `ValueError` (с Python 3.10).

              `zip` принимает и три последовательности, и больше. Другие встроенные функции для перебора — в теме [[fn_builtins|Функции для последовательностей]].
              """,
              [("""\
                todo = ["хлеб", "позвонить"]
                for i, t in enumerate(todo, 1):
                    print(f"{i}. {t}")""",
                "Нумерация с 1 без счётчика и range(len(...))"),
               ("""\
                names = ["Ада", "Алан", "Грейс"]
                scores = [95, 88, 91]
                for n, s in zip(names, scores):
                    print(n, s)""",
                "Элементы двух списков идут парами"),
               ("""\
                days = ["пн", "вт", "ср"]
                temps = [12, 15]
                for d, t in zip(days, temps):
                    print(d, t)""",
                "«ср» пропала: zip остановился на коротком списке")],
              [pitfall("Индексы через `range(len(…))` длиннее, и в них легче ошибиться.",
                       bad="for i in range(len(names)):\n    print(i, names[i])",
                       good="for i, name in enumerate(names):\n    print(i, name)"),
               pitfall("`enumerate` отдаёт сначала номер, потом элемент — иначе имена перепутаются.",
                       bad="for name, i in enumerate(names):\n    print(i, name)",
                       good="for i, name in enumerate(names):\n    print(i, name)"),
               pitfall("Разная длина незаметна: `zip` молча обрежет. С `strict=True` будет ValueError.",
                       bad="pairs = zip(names, scores)",
                       good="pairs = zip(names, scores, strict=True)")]),
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
              "Список хранит несколько значений по порядку под одним именем, и его можно менять.",
              """
              Когда значений много — оценки класса, товары в корзине, ходы игрока, — заводить переменную на каждое неудобно. Список хранит их все вместе и по порядку.

              ## Как записать

              ```syntax
              имя = [элемент1, элемент2, элемент3]
              ```

              - `[]` — пустой список, его заполняют потом
              - элементы — любые значения, даже разных типов и другие списки
              - `len(nums)` — число элементов

              ## Индексы и срезы

              Работают [[str_index|как у строк]]: `nums[0]` — первый элемент, `nums[-1]` — последний, `nums[1:3]` — новый список из элементов 1 и 2.

              В отличие от строки, элемент списка можно заменить: `nums[0] = 10`.

              ## Операции

              - `a + b` — новый список из элементов обоих
              - `[0] * 3` — новый список `[0, 0, 0]`
              - `x in nums` — есть ли элемент в списке
              - `for x in nums:` — перебор по порядку

              Как добавлять, удалять и сортировать элементы — в теме [[list_methods|Методы списков]].
              """,
              [("""\
                cart = ["хлеб", "сыр", "чай"]
                print(cart[0])
                print(cart[-1])
                print(len(cart))""",
                "Первый, последний элемент и длина"),
               ("""\
                marks = [4, 5, 3]
                marks[2] = 5
                print(marks)
                print(marks[:2])""",
                "Элемент заменён, срез дал новый список"),
               ("""\
                week = ["пн", "вт"] + ["ср"]
                print(week)
                print([0] * 4)
                print("вт" in week)""",
                "Склейка, повтор и проверка вхождения")],
              [pitfall("Счёт идёт с нуля: `nums[1]` — второй элемент.",
                       bad="first = nums[1]", good="first = nums[0]"),
               pitfall("Последний индекс — `len(nums) - 1`: IndexError: list index out of range.",
                       bad="last = nums[len(nums)]", good="last = nums[-1]"),
               pitfall("`+` склеивает только списки: TypeError: can only concatenate list (not \"int\") to list.",
                       bad="nums = nums + 5", good="nums = nums + [5]")]),
        topic("list_methods", "Методы списков",
              "Методы списка добавляют, удаляют и сортируют элементы прямо в нём; `sorted` вместо этого возвращает новый список.",
              """
              Список живёт вместе с программой: в корзину добавляют товары, из очереди убирают обработанных, результаты сортируют. Методы делают это на месте, не создавая новый список.

              ## Меняют список на месте

              | Метод | Что делает |
              |---|---|
              | {`append(x)`} | добавить в конец |
              | {`insert(i, x)`} | вставить на место {`i`} |
              | {`extend(other)`} | добавить все элементы |
              | {`remove(x)`} | удалить первое {`x`} |
              | {`pop()`} | забрать последний |
              | {`pop(i)`} | забрать элемент {`i`} |
              | {`sort()`} | отсортировать |
              | {`reverse()`} | развернуть |

              Все они, кроме `pop`, возвращают [[none_value|`None`]]: результат — изменённый список, а не новое значение. `pop` возвращает забранный элемент.

              ## Ищут и считают

              - `nums.index(x)` — позиция первого `x`
              - `nums.count(x)` — сколько раз встречается `x`
              - `min(nums)`, `max(nums)`, `sum(nums)` — встроенные функции, а не методы: минимум, максимум, сумма

              `index` и `remove` для отсутствующего элемента дают `ValueError`. Перед ними проверяйте `x in nums`.

              ## Что выбрать: sort или sorted

              - `nums.sort()` — сортирует сам список, прежний порядок пропадает
              - `sorted(nums)` — новый отсортированный список, исходный не меняется

              Оба принимают `reverse=True` для сортировки по убыванию.
              """,
              [("""\
                queue = ["Ада", "Алан"]
                queue.append("Грейс")
                queue.insert(0, "Линус")
                print(queue)""",
                "append — в конец, insert — на указанное место"),
               ("""\
                queue = ["Ада", "Алан", "Грейс"]
                first = queue.pop(0)
                queue.remove("Грейс")
                print(first)
                print(queue)""",
                "pop вернул забранный элемент, remove — нет"),
               ("""\
                scores = [7, 3, 9]
                top = sorted(scores, reverse=True)
                print(top)
                print(scores)
                scores.sort()
                print(scores)""",
                "sorted дал новый список, sort изменил сам scores"),
               ("""\
                a = [1, 2]
                a.append([3, 4])
                print(a)
                b = [1, 2]
                b.extend([3, 4])
                print(b)""",
                "append добавил список одним элементом, extend — по одному")],
              [pitfall("`sort` возвращает None, и после присваивания список потерян.",
                       bad="scores = scores.sort()",
                       good="scores.sort()  # или scores = sorted(scores)"),
               pitfall("`append` добавляет один элемент: список станет вложенным.",
                       bad="nums.append([4, 5])", good="nums.extend([4, 5])"),
               pitfall("Удалить отсутствующее нельзя: ValueError: list.remove(x): x not in list.",
                       bad="nums.remove(10)",
                       good="if 10 in nums:\n    nums.remove(10)")]),
        topic("list_mutable", "Изменяемость и ссылки",
              "Присваивание `b = a` не копирует список: оба имени указывают на один объект, и изменения видны через оба.",
              """
              Список может быть большим, поэтому Python не копирует его при присваивании. Имя — лишь ярлык на объект. Если ярлыков два, а объект один, изменение через одно имя видно и через другое.

              ## Одно имя или копия

              - `b = a` — второе имя для того же списка
              - `b = a.copy()` или `b = a[:]` — новый список с теми же элементами
              - `a is b` — один ли это объект
              - `a == b` — равны ли значения

              ## Поверхностная копия

              `copy()` создаёт новый внешний список, но вложенные списки не копирует: обе копии ссылаются на одни и те же внутренние объекты. Такую копию называют поверхностной.

              Для списка чисел или строк этого достаточно. Если внутри есть списки, которые будут меняться, нужна глубокая копия: `copy.deepcopy(a)` копирует все уровни. Модуль `copy` подключают через [[std_import|import]].

              ## Изменяемые и неизменяемые

              Списки, [[dict_basics|словари]] и множества изменяемы: их меняют на месте. Числа, строки и [[tuple_basics|кортежи]] неизменяемы: «изменение» создаёт новый объект. Поэтому `x = y = 0` безопасно, а `x = y = []` даёт один общий список.
              """,
              [("""\
                team = ["Ада", "Алан"]
                squad = team
                squad.append("Грейс")
                print(team)
                print(team is squad)""",
                "Добавили через squad — изменился и team: это один список"),
               ("""\
                team = ["Ада", "Алан"]
                backup = team.copy()
                team.append("Грейс")
                print(team)
                print(backup)""",
                "Копия не заметила изменений оригинала"),
               ("""\
                board = [["."], ["."]]
                shallow = board.copy()
                shallow[0][0] = "X"
                print(board)""",
                "Поверхностная копия: вложенные списки общие"),
               ("""\
                import copy
                board = [["."], ["."]]
                deep = copy.deepcopy(board)
                deep[0][0] = "X"
                print(board)
                print(deep)""",
                "deepcopy скопировал и вложенные списки")],
              [pitfall("`b = a` не копирует: изменения через `backup` видны в `scores`.",
                       bad="backup = scores", good="backup = scores.copy()"),
               pitfall("`x = y = []` — один список под двумя именами.",
                       bad="wins = losses = []", good="wins = []\nlosses = []"),
               pitfall("`* 3` повторил ссылку на один внутренний список: изменение одной строки видно во всех.",
                       bad="grid = [[0] * 3] * 3",
                       good="grid = [[0] * 3 for _ in range(3)]"),
               pitfall("Удаление во время перебора сдвигает элементы, и часть пропускается. Перебирайте копию.",
                       bad="for x in nums:\n    if x < 0:\n        nums.remove(x)",
                       good="for x in nums.copy():\n    if x < 0:\n        nums.remove(x)")]),
        topic("none_value", "None: значения нет",
              "`None` — особое значение «ничего нет»: им отмечают пустое место, его возвращают функции и методы без результата.",
              """
              Иногда значения ещё нет: игрок не выбрал город, поиск ничего не нашёл. Для этого в Python есть {`None`} — единственное значение типа `NoneType`.

              ## Где встречается

              - переменная, которую заполнят позже: `winner = None`
              - метод, который меняет список на месте: [[list_methods|`nums.sort()`]] возвращает {`None`}
              - функция без [[func_def|`return`]] возвращает {`None`}
              - [[dict_methods|`d.get(k)`]] даёт {`None`}, если ключа нет

              `print(None)` выводит слово `None`. В условии {`None`} — [[types_bool|ложь]], но оно не равно ни `0`, ни пустой строке.

              ## Как проверить

              Проверяют через `is`: `x is None` или `x is not None`. {`None`} в программе всегда один объект, поэтому `is` здесь точен. Чем `is` отличается от `==` — в теме [[list_mutable|Изменяемость и ссылки]].

              ## Ошибки с None

              С {`None`} нельзя считать и брать элементы. Если в сообщении об ошибке есть `NoneType`, значит, где-то вместо значения пришло {`None`}:

              - `TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'`
              - `TypeError: 'NoneType' object is not subscriptable`

              Ищите, откуда взялось {`None`}. Часто это результат метода, который меняет объект на месте, сохранённый в переменную.
              """,
              [("""\
                winner = None
                print(winner)
                print(type(winner).__name__)""",
                "None печатается словом None, его тип — NoneType"),
               ("""\
                winner = None
                if winner is None:
                    print("Победителя нет")
                winner = "Ада"
                print(winner is None)""",
                "is None — проверка «значение ещё не задано»"),
               ("""\
                scores = [5, 9, 7]
                result = scores.sort()
                print(result)
                print(scores)""",
                "sort изменил список, а вернул None"),
               ("""\
                print(bool(None))
                print(None == 0)
                print(None == "")""",
                "None — ложь в условии, но не ноль и не пустая строка")],
              [pitfall("`sort` вернул None, и список потерян: TypeError: 'NoneType' object is not subscriptable.",
                       bad="names = names.sort()\nprint(names[0])",
                       good="names.sort()\nprint(names[0])"),
               pitfall("Проверку на {`None`} пишут через `is`: так принято, и это короче.",
                       bad="if city == None:\n    city = \"Москва\"",
                       good="if city is None:\n    city = \"Москва\""),
               pitfall("`not count` ловит и {`None`}, и 0. Если 0 — допустимое значение, проверяйте `is None`.",
                       bad="if not count:\n    print(\"нет данных\")",
                       good="if count is None:\n    print(\"нет данных\")")]),
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
            {1: "nums.sort()"}, topic="none_value", hint="Что возвращает метод sort?",
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
              "Кортеж — неизменяемая последовательность: его элементы нельзя заменить, добавить или удалить.",
              """
              Некоторые данные не должны меняться после создания: координаты точки, дата, цвет в RGB. Для них есть кортеж — «замороженный» список.

              ## Как записать

              ```syntax
              имя = (элемент1, элемент2)
              имя = элемент1, элемент2
              ```

              Кортеж делает запятая, скобки только группируют. `(5)` — обычное число, `(5,)` — кортеж из одного элемента. Исключение — пустой кортеж `()`.

              ## Что можно делать

              Индексы, срезы, `len`, `in` и `for` работают как у [[list_basics|списка]]. Заменить элемент нельзя: `t[0] = 1` даёт `TypeError`.

              Кортеж удобно распаковывать: `x, y = point`. На этом держится и [[var_multi|множественное присваивание]].

              ## Зачем кортеж, если есть список

              - данные защищены от случайного изменения
              - кортеж может быть ключом [[dict_basics|словаря]] и элементом множества
              - функция возвращает несколько значений именно кортежем

              ## Хешируемость

              Ключом словаря и элементом множества может быть только хешируемое значение. Оно не меняется, поэтому функция `hash` всегда даёт для него одно и то же число-«отпечаток». По этому числу Python сразу находит место значения, без перебора.

              Числа, строки и кортежи хешируемы, списки и словари — нет. Кортеж хешируем, только если хешируемы все его элементы: `(1, [2])` в множество не положить.
              """,
              [("""\
                rgb = (255, 128, 0)
                print(rgb[0])
                print(len(rgb))
                r, g, b = rgb
                print(g)""",
                "Индекс, длина и распаковка — как у списка"),
               ("""\
                one = (7,)
                seven = (7)
                print(type(one).__name__)
                print(type(seven).__name__)""",
                "Кортеж делает запятая, а не скобки"),
               ("""\
                visited = {(0, 0), (1, 2)}
                print((1, 2) in visited)
                print((2, 1) in visited)""",
                "Кортежи-координаты лежат в множестве")],
              [pitfall("Без запятой скобки ничего не создают: `(5)` — число.",
                       bad="single = (5)", good="single = (5,)"),
               pitfall("Кортеж нельзя изменить: TypeError: 'tuple' object does not support item assignment.",
                       bad="point[0] = 10", good="point = (10, point[1])"),
               pitfall("Кортеж со списком внутри не хешируется: TypeError: unhashable type: 'list'.",
                       bad="seen = {(1, [2, 3])}", good="seen = {(1, (2, 3))}")]),
        topic("set_basics", "Множества",
              "Множество хранит только уникальные элементы без порядка и быстро отвечает, есть ли в нём значение.",
              """
              Нужно убрать повторы из списка, посчитать разные слова или быстро проверять «было ли уже такое»? Для этого есть множество.

              ## Как записать

              ```syntax
              имя = {элемент1, элемент2}
              имя = set(последовательность)
              ```

              - повторы отбрасываются сами: `{1, 1, 2}` — это `{1, 2}`
              - порядка нет, поэтому индексов `s[0]` у множества не бывает
              - `set()` — пустое множество, а `{}` — пустой [[dict_basics|словарь]]

              ## Изменение

              - `s.add(x)` — добавить элемент
              - `s.remove(x)` — удалить; если `x` нет — `KeyError`
              - `s.discard(x)` — удалить, если есть, без ошибки

              ## Быстрая проверка

              `x in s` для множества работает почти мгновенно даже на миллионе элементов. [[list_basics|Список]] же проверяется перебором. Поэтому для частых проверок «было ли» используют множество.

              ## Что можно положить

              Только [[tuple_basics|хешируемые]] значения: числа, строки, кортежи. Список или словарь положить нельзя: `TypeError: unhashable type: 'list'`.

              Порядок вывода множества не гарантирован. Чтобы вывести элементы предсказуемо, используйте `sorted(s)`.
              """,
              [("""\
                visits = ["Ада", "Алан", "Ада"]
                unique = set(visits)
                print(len(unique))
                print(sorted(unique))""",
                "Повторы исчезли, sorted дал предсказуемый порядок"),
               ("""\
                tags = set()
                tags.add("python")
                tags.add("игры")
                tags.add("python")
                print(len(tags))
                tags.discard("музыка")
                print(sorted(tags))""",
                "Повторный add ничего не меняет, discard без ошибки"),
               ("""\
                seen = set()
                for n in [3, 7, 3, 9, 7]:
                    if n in seen:
                        print("повтор:", n)
                    seen.add(n)""",
                "Множество как память «уже встречалось»")],
              [pitfall("`{}` — пустой словарь, а не множество, у него нет `add`.",
                       bad="tags = {}", good="tags = set()"),
               pitfall("`remove` отсутствующего элемента — KeyError. Без ошибки удаляет `discard`.",
                       bad="tags.remove(\"музыка\")", good="tags.discard(\"музыка\")"),
               pitfall("У множества нет индексов: TypeError: 'set' object is not subscriptable.",
                       bad="first = s[0]", good="first = sorted(s)[0]"),
               pitfall("Список в множество не положить: TypeError: unhashable type: 'list'.",
                       bad="s.add([1, 2])", good="s.add((1, 2))")]),
        topic("set_ops", "Операции над множествами",
              "Операции над множествами находят общие, различные и все вместе элементы двух наборов.",
              """
              Какие увлечения общие у двух людей? Каких навыков не хватает кандидату? Такие вопросы решаются одной операцией над множествами.

              ## Операции

              - `a | b` — объединение: элементы из обоих
              - `a & b` — пересечение: только общие
              - `a - b` — разность: есть в `a`, но нет в `b`
              - `a ^ b` — симметрическая разность: есть ровно в одном

              Все операции возвращают новое множество, исходные не меняются. Разность несимметрична: `a - b` и `b - a` — разные множества.

              ## Методы с теми же действиями

              `a.union(b)`, `a.intersection(b)` и `a.difference(b)` делают то же, что {`|`}, {`&`} и {`-`}. Разница в том, что методы принимают любую последовательность, например [[list_basics|список]]. Операторам нужны множества с обеих сторон.

              ## Проверки

              - `a <= b` или `a.issubset(b)` — все элементы `a` есть в `b`
              - `a >= b` или `a.issuperset(b)` — `a` содержит все элементы `b`
              - `a.isdisjoint(b)` — общих элементов нет
              """,
              [("""\
                ada = {"чай", "книги", "бег"}
                alan = {"бег", "шахматы", "чай"}
                print(sorted(ada & alan))
                print(sorted(ada | alan))""",
                "Общие увлечения и все вместе"),
               ("""\
                need = {"python", "sql", "git"}
                have = {"python", "git"}
                print(need - have)
                print(have <= need)""",
                "Чего не хватает и входят ли навыки в нужные"),
               ("""\
                a = {1, 2, 3}
                print(sorted(a ^ {3, 4}))
                print(sorted(a.union([9, 1])))""",
                "Симметрическая разность и метод, который принимает список")],
              [pitfall("Оператору нужны два множества: TypeError: unsupported operand type(s) for |: 'set' and 'list'.",
                       bad="a | [4, 5]", good="a.union([4, 5])"),
               pitfall("Множество не хранит порядок. Для предсказуемого вывода сортируйте.",
                       bad="print(a & b)", good="print(sorted(a & b))")]),
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
              "Словарь хранит пары «ключ — значение» и сразу находит значение по ключу: `ages[\"Ада\"]`.",
              """
              Телефонная книга, цены товаров, настройки игры — всё это пары «по чему ищем — что находим». Словарь хранит такие пары и находит значение по ключу без перебора.

              ## Как записать

              ```syntax
              имя = {ключ1: значение1, ключ2: значение2}
              ```

              - `{}` — пустой словарь
              - ключи уникальны: при повторе остаётся последнее значение
              - ключ — [[g:хешируемый|хешируемое]] значение: строка, число, кортеж; список ключом быть не может

              ## Чтение и запись

              - `d[ключ]` — значение; если ключа нет — `KeyError`
              - `d[ключ] = значение` — добавить пару или заменить значение
              - {`del d[ключ]`} — удалить пару
              - `ключ in d` — есть ли такой ключ
              - `len(d)` — число пар

              ## Перебор

              `for k in d:` перебирает ключи в порядке добавления. Чтобы получить и ключ, и значение, используют `d.items()` — подробнее в теме [[dict_methods|Методы словарей]].
              """,
              [("""\
                prices = {"чай": 120, "кофе": 180}
                print(prices["кофе"])
                prices["сок"] = 150
                prices["чай"] = 100
                print(prices)""",
                "Новый ключ добавился, существующий — заменился"),
               ("""\
                stock = {"яблоки": 5, "груши": 0}
                del stock["груши"]
                print(stock)
                print("груши" in stock)""",
                "del удалил пару, in проверяет ключи"),
               ("""\
                capitals = {
                    "Франция": "Париж",
                    "Япония": "Токио",
                }
                for c in capitals:
                    print(c, capitals[c])""",
                "Перебор идёт по ключам в порядке добавления")],
              [pitfall("Обращение к отсутствующему ключу: KeyError: 'груши'. Сначала проверьте `in`.",
                       bad="print(stock[\"груши\"])",
                       good="if \"груши\" in stock:\n    print(stock[\"груши\"])"),
               pitfall("Список ключом быть не может: TypeError: unhashable type: 'list'.",
                       bad="d = {[1, 2]: \"точка\"}", good="d = {(1, 2): \"точка\"}"),
               "Ждать, что `\"Чай\"` и `\"чай\"` — один ключ: ключи сравниваются точно, с учётом регистра и пробелов."]),
        topic("dict_methods", "Методы словарей",
              "Методы словаря читают значения без `KeyError`, перебирают пары и меняют словарь целиком.",
              """
              Словарь часто читают «осторожно»: ключа может не оказаться. А перебирать его удобнее парами. Для этого у словаря есть методы, которые обходятся без ошибок и лишних проверок.

              ## Чтение без ошибки

              - `d.get(k)` — значение или [[none_value|`None`]], если ключа нет
              - `d.get(k, 0)` — значение или `0`
              - `d.setdefault(k, v)` — значение; если ключа нет, сначала записывает `v`

              ## Перебор

              - `for k in d:` — ключи
              - `for v in d.values():` — значения
              - `for k, v in d.items():` — пары, сразу [[var_multi|разложенные]] на два имени

              `in` смотрит только ключи: `3 in d` не ищет среди значений.

              ## Изменение

              - `d.pop(k)` — удалить ключ и вернуть его значение
              - `d.pop(k, None)` — то же, но без ошибки, если ключа нет
              - `d.update(other)` — добавить пары из другого словаря
              - {`del d[k]`} — удалить без возврата значения

              `update` перезаписывает значения совпадающих ключей.

              ## Живые представления

              `keys()`, `values()` и `items()` возвращают не копию, а «окно» в словарь: изменится словарь — изменится и представление.

              Менять размер словаря во время перебора нельзя — ни самого словаря, ни его представлений: будет `RuntimeError`. Перебирайте копию ключей: `list(d)`.
              """,
              [("""\
                settings = {"звук": True}
                print(settings.get("звук"))
                print(settings.get("язык"))
                print(settings.get("язык", "ru"))""",
                "get не падает: None или значение по умолчанию"),
               ("""\
                menu = {"суп": 250, "салат": 180}
                for dish, price in menu.items():
                    print(dish, price)""",
                "items даёт пары, они раскладываются на два имени"),
               ("""\
                cart = {"чай": 2, "хлеб": 1}
                removed = cart.pop("хлеб")
                cart.update({"чай": 3, "сыр": 1})
                print(removed)
                print(cart)""",
                "pop вернул значение, update заменил и добавил пары"),
               ("""\
                d = {"a": 1}
                keys = d.keys()
                d["b"] = 2
                print(keys)""",
                "Представление keys увидело новый ключ")],
              [pitfall("`in` ищет среди ключей, а не значений.",
                       bad="found = 250 in menu", good="found = 250 in menu.values()"),
               pitfall("Размер изменился при переборе: RuntimeError: dictionary changed size during iteration.",
                       bad="for k in d:\n    if d[k] == 0:\n        del d[k]",
                       good="for k in list(d):\n    if d[k] == 0:\n        del d[k]"),
               pitfall("`get` только читает: ключ в словаре не появится. Записывает `setdefault` или присваивание.",
                       bad="d.get(\"новый\", 0)", good="d.setdefault(\"новый\", 0)")]),
        topic("dict_counting", "Подсчёт с помощью словаря",
              "Словарь удобен как счётчик: ключ — что считаем, значение — сколько раз это встретилось.",
              """
              Сколько раз встречается каждое слово в тексте, каждая оценка в журнале, каждый ответ в опросе? Такие задачи решаются одним шаблоном со словарём.

              ## Как записать

              ```syntax
              counts = {}
              for элемент in последовательность:
                  counts[элемент] = counts.get(элемент, 0) + 1
              ```

              1. [[dict_methods|`counts.get(элемент, 0)`]] берёт текущее число, для нового ключа — `0`.
              2. К нему прибавляют `1`.
              3. Результат записывают обратно по тому же ключу.

              Словарь-счётчик создают до цикла. Порядок ключей — порядок первого появления.

              ## Готовый счётчик

              В стандартной библиотеке есть `collections.Counter`: `Counter(текст)` строит такой же словарь одной строкой. Подробнее — в теме [[std_collections|collections]]. Шаблон с `get` всё равно стоит знать: он работает везде и легко меняется под задачу.
              """,
              [("""\
                votes = ["да", "нет", "да", "да"]
                counts = {}
                for v in votes:
                    counts[v] = counts.get(v, 0) + 1
                print(counts)""",
                "Каждый голос прибавил 1 к своему ключу"),
               ("""\
                text = "кот пёс кот ёж кот"
                counts = {}
                for w in text.split():
                    counts[w] = counts.get(w, 0) + 1
                for w, n in counts.items():
                    print(w, n)""",
                "Подсчёт слов, вывод в порядке первого появления"),
               ("""\
                from collections import Counter
                print(Counter("ананас"))""",
                "Counter делает то же самое одной строкой")],
              [pitfall("Новый ключ ещё не в словаре: `counts[ch] += 1` даёт KeyError.",
                       bad="counts[ch] += 1", good="counts[ch] = counts.get(ch, 0) + 1"),
               pitfall("Счётчик, созданный внутри цикла, обнуляется на каждом шаге.",
                       bad="for w in words:\n    counts = {}\n    counts[w] = counts.get(w, 0) + 1",
                       good="counts = {}\nfor w in words:\n    counts[w] = counts.get(w, 0) + 1")]),
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
              "Списковое включение строит новый список из последовательности одной строкой: `[x * 2 for x in nums]`.",
              """
              Частая задача — получить из одного списка другой: цены со скидкой, длины слов, имена заглавными. Обычно это цикл с `append`. Включение делает то же короче и нагляднее.

              ## Как записать

              ```syntax
              [выражение for переменная in последовательность]
              ```

              Читается как «выражение для каждой переменной из последовательности». Результат — новый список, исходный не меняется.

              ## То же, что цикл

              Включение повторяет цикл с [[list_methods|`append`]]: тот же перебор, но без пустого списка и вызова метода. Разницу видно в первых двух примерах ниже.

              Включение работает немного быстрее такого цикла: на каждом шаге не нужно искать и вызывать метод `append`. Но выбирают его ради читаемости, а не скорости.

              ## Несколько for

              `[r + c for r in "AB" for c in "12"]` — это два [[loopx_nested|вложенных цикла]]. Порядок как в обычной записи: первый `for` — внешний.

              Если включение не помещается в строку или в нём больше двух `for`, обычный цикл понятнее.
              """,
              [("""\
                words = ["кот", "собака", "ёж"]
                lengths = []
                for w in words:
                    lengths.append(len(w))
                print(lengths)""",
                "Цикл с append: пустой список, перебор, добавление"),
               ("""\
                words = ["кот", "собака", "ёж"]
                lengths = [len(w) for w in words]
                print(lengths)""",
                "То же включением — одна строка"),
               ("""\
                names = ["ада", "алан"]
                print([n.upper() for n in names])
                print(names)""",
                "Включение дало новый список, исходный не изменился"),
               ("""\
                cells = [
                    r + c for r in "AB" for c in "12"
                ]
                print(cells)""",
                "Первый for — внешний: сначала все клетки ряда A")],
              [pitfall("Включение ради действия строит ненужный список из None. Для действий пишут цикл.",
                       bad="[print(x) for x in nums]",
                       good="for x in nums:\n    print(x)"),
               "Писать слишком сложные включения: если не помещается в строку, понятнее обычный цикл."]),
        topic("comp_cond", "Фильтр и условие",
              "Условие в конце включения отбирает элементы, а условное выражение в начале выбирает значение для каждого.",
              """
              Из списка часто нужны не все элементы, а только подходящие: положительные числа, длинные слова. Или все, но с заменой: отрицательные — нулями. Включение умеет и то, и другое.

              ## Фильтр: if в конце

              ```syntax
              [выражение for x in последовательность if условие]
              ```

              Элемент попадает в результат, только если условие истинно. Новый список может быть короче исходного.

              ## Выбор значения: if-else в начале

              ```syntax
              [да if условие else нет for x in последовательность]
              ```

              Это [[cond_ternary|условное выражение]]: для каждого элемента вычисляется одно из двух значений. Длина результата равна длине исходного списка.

              ## Где что стоит

              - `if` без `else` — только в конце, после `for`
              - `if` с `else` — только в начале, перед `for`

              Перепутать места нельзя: оба варианта дают `SyntaxError`. Фильтр и выбор можно сочетать, но такую строку трудно читать — подумайте об обычном цикле.
              """,
              [("""\
                temps = [12, -3, 7, -8, 0]
                warm = [t for t in temps if t > 0]
                print(warm)""",
                "Фильтр оставил только положительные"),
               ("""\
                temps = [12, -3, 7, -8, 0]
                fixed = [
                    t if t > 0 else 0 for t in temps
                ]
                print(fixed)""",
                "Выбор значения: длина та же, отрицательные стали нулями"),
               ("""\
                words = ["я", "кот", "", "лиса"]
                long = [
                    w.upper() for w in words
                    if len(w) > 2
                ]
                print(long)""",
                "Фильтр и преобразование вместе")],
              [pitfall("Условие с `else` пишут перед `for`, а не после: SyntaxError.",
                       bad="[t for t in temps if t > 0 else 0]",
                       good="[t if t > 0 else 0 for t in temps]", syntax_error=True),
               pitfall("Условное выражение в начале требует `else`, иначе SyntaxError. Фильтр — в конец.",
                       bad="[t if t > 0 for t in temps]",
                       good="[t for t in temps if t > 0]", syntax_error=True)]),
        topic("comp_dict_set", "Включения словарей и множеств",
              "Фигурные скобки во включении создают словарь или множество, а круглые — генераторное выражение.",
              """
              Включение строит не только списки. Словарь «имя — длина» или множество разных букв тоже собираются одной строкой.

              ## Как записать

              ```syntax
              {ключ: значение for x in последовательность}
              {выражение for x in последовательность}
              (выражение for x in последовательность)
              ```

              - двоеточие в фигурных скобках — [[dict_basics|словарь]]
              - фигурные скобки без двоеточия — [[set_basics|множество]], повторы уберутся
              - круглые скобки — генераторное выражение, а не кортеж

              Фильтр `if` в конце работает так же, как [[comp_cond|у списков]].

              ## Генераторное выражение

              Оно не строит список целиком, а выдаёт значения по одному, когда их просят. Такие вычисления называют ленивыми. Это экономит память: `sum(x * x for x in range(1_000_000))` не хранит миллион чисел.

              Если выражение — единственный аргумент функции, вторые скобки не нужны: `sum(…)`, `max(…)`, `"".join(…)`.

              Генератор одноразовый: после полного перебора он пуст. Подробнее — в теме [[gen_lazy|Ленивые вычисления и конвейеры]].
              """,
              [("""\
                names = ["Ада", "Алан", "Грейс"]
                sizes = {n: len(n) for n in names}
                print(sizes)""",
                "Ключ — слева от двоеточия, значение — справа"),
               ("""\
                letters = {ch for ch in "банан"}
                print(sorted(letters))""",
                "Множество оставило только разные буквы"),
               ("""\
                prices = {"чай": 120, "кофе": 180}
                cheap = {
                    k: v for k, v in prices.items()
                    if v < 150
                }
                print(cheap)""",
                "Фильтр по значению словаря"),
               ("""\
                gen = (c.upper() for c in "abc")
                print(list(gen))
                print(list(gen))""",
                "Генератор отдал значения один раз, второй раз — пусто")],
              [pitfall("Круглые скобки дают генератор, а не кортеж: TypeError: 'generator' object is not subscriptable.",
                       bad="sq = (x * x for x in nums)\nprint(sq[0])",
                       good="sq = [x * x for x in nums]\nprint(sq[0])"),
               pitfall("Генератор одноразовый: второй проход ничего не даст. Сохраните значения в список.",
                       bad="total = sum(g)\ncount = len(list(g))",
                       good="items = list(g)\ntotal = sum(items)\ncount = len(items)")]),
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
