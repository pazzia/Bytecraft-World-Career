"""Модули 13–17: функции, аргументы, области видимости и замыкания,
функциональный стиль, рекурсия."""
from bclib import choice, fill, match, multi, order, predict, bug, typed, topic, task, run


def runs(code):
    return run(code).ok


def result_of(code):
    """Output of the program, or the exception name if it fails."""
    result = run(code)
    return result.out.strip() if result.ok else result.error


MODULES = []

# ---------------------------------------------------------------- functions
MODULES.append(dict(
    id="functions", title="Функции", description="def, параметры и return", icon="🧩",
    topics=[
        topic("func_def", "Объявление функции и return",
              "def имя(параметры): — объявляет функцию; return возвращает результат в место вызова.",
              """
              Функция — именованный блок кода. Тело пишется с отступом под строкой def и выполняется только при вызове: имя(аргументы).

              return завершает функцию и отдаёт значение туда, откуда её вызвали. Его можно сохранить в переменную или сразу использовать в выражении.

              Если функция дошла до конца без return или выполнила return без значения, она возвращает None. print внутри функции только показывает текст на экране и ничего не возвращает.

              Функция может вернуть несколько значений через запятую: return lo, hi — это кортеж, его удобно распаковать: a, b = f(...).

              Строка в тройных кавычках первой строкой тела — docstring, описание функции: его показывает help(f) и f.__doc__.

              Функция — такое же значение, как число или строка: её можно передать в другую функцию аргументом и вызвать там.
              """,
              [("""\
                def square(x):
                    return x * x

                area = square(4) + 1
                print(area)""", "Результат return участвует в выражении."),
               ("""\
                def shout(text):
                    print(text.upper())

                result = shout("привет")
                print(result)""", "Функция без return возвращает None.")],
              ["Путать print и return: напечатанное значение нельзя использовать дальше в программе.",
               "Ждать, что аннотации типов (a: int) проверяются: Python их не проверяет, add(\"4\", \"2\") вернёт «42».",
               "Забыть скобки при вызове: square вместо square(4) — это сама функция, а не результат."]),
        topic("func_params", "Параметры и аргументы",
              "Параметры — имена в объявлении, аргументы — значения при вызове. Бывают позиционные, именованные и со значением по умолчанию.",
              """
              def power(base, exp=2) — у exp есть значение по умолчанию: power(3) — это 3 ** 2.

              Аргументы можно передать по позиции power(2, 5) или по имени power(exp=5, base=2). Именованные аргументы идут после позиционных.

              Количество аргументов должно подходить к параметрам, иначе TypeError: missing ... argument или takes ... positional arguments but ... were given.
              """,
              [("""\
                def power(base, exp=2):
                    return base ** exp

                print(power(3), power(2, 5), power(exp=3, base=2))""", None)],
              ["Ставить именованный аргумент перед позиционным: f(a=1, 2) — SyntaxError.",
               "Передавать одно значение дважды: f(1, a=2) — TypeError: multiple values."]),
    ],
    tasks=[
        task("t_func_clamp", "Ограничить число",
             "Напишите функцию clamp(x, lo, hi), которая возвращает x, но не меньше lo и не больше hi (гарантируется lo ≤ hi). Прочитайте три целых числа x lo hi из одной строки и выведите clamp(x, lo, hi).",
             solution="""\
                def clamp(x, lo, hi):
                    return max(lo, min(x, hi))

                x, lo, hi = map(int, input().split())
                print(clamp(x, lo, hi))""",
             starter="""\
                def clamp(x, lo, hi):
                    pass

                x, lo, hi = map(int, input().split())
                print(clamp(x, lo, hi))""",
             tests=["5 0 10\n", "-3 0 10\n", "42 0 10\n", "7 7 7\n", "-50 -10 -5\n"],
             hint="min(x, hi) срезает сверху, max(lo, ...) — снизу.", difficulty=1,
             requires=dict(defines=["clamp"])),
        task("t_func_palindrome", "Палиндром",
             "Напишите функцию is_palindrome(word), которая возвращает True, если слово читается одинаково в обе стороны (без учёта регистра). Прочитайте слово и выведите «да» или «нет».",
             solution="""\
                def is_palindrome(word):
                    word = word.lower()
                    return word == word[::-1]

                print("да" if is_palindrome(input().strip()) else "нет")""",
             starter="""\
                def is_palindrome(word):
                    return False

                print("да" if is_palindrome(input().strip()) else "нет")""",
             tests=["Шалаш\n", "python\n", "Anna\n", "a\n", "abca\n"],
             hint="Срез [::-1] разворачивает строку.", difficulty=2,
             requires=dict(defines=["is_palindrome"])),
    ],
    levels=[
        choice("py_func_001", "Зачем return", "Что делает return внутри функции?",
               ["Печатает значение на экран", "Возвращает значение в место вызова и завершает функцию",
                "Объявляет новую функцию", "Повторяет функцию заново"], 1,
               topic="func_def", hint="Результат return можно сохранить в переменную.",
               explanation="return отдаёт значение туда, где функцию вызвали, и сразу завершает её. Печатает на экран print.",
               feedback={"Печатает значение на экран": "Печатает print. return ничего не показывает, он отдаёт значение.",
                         "Объявляет новую функцию": "Функцию объявляет def.",
                         "Повторяет функцию заново": "Повторяют циклы. return, наоборот, завершает функцию."}),
        predict("py_func_002", "print или return", """\
                def add(a, b):
                    print(a + b)

                result = add(2, 3)
                print(result)""",
                ["5\n5", "5", "None"], position=1, topic="func_def",
                hint="Что возвращает функция, в которой нет return?",
                explanation="add печатает 5, но ничего не возвращает. Поэтому result равен None, и второй print выводит None.",
                feedback={"5\n5": "В add нет return, значит result — None, а не 5.",
                          "5": "Второй print тоже выводит строку: значение result.",
                          "None": "Первым срабатывает print внутри add: он выводит 5."}),
        fill("py_func_003", "Вернуть квадрат", "Сделайте так, чтобы функция возвращала квадрат числа",
             """\
             def square(x):
                 {{0}} x * x

             print(square(4))""", ["return", "print", "pass", "def"], ["return"],
             topic="func_def", hint="Значение из функции отдаёт одно ключевое слово.",
             explanation="return x * x возвращает 16 в место вызова, и print(square(4)) выводит его.",
             expect="16\n"),
        typed("py_func_004", "Значения по умолчанию", """\
              def power(base, exp=2):
                  return base ** exp

              print(power(3))
              print(power(2, 5))
              print(power(exp=3, base=2))""",
              topic="func_params", hint="Если exp не передан, он равен 2. Именованные аргументы можно передавать в любом порядке.",
              explanation="power(3) = 3² = 9, power(2, 5) = 2⁵ = 32, power(exp=3, base=2) = 2³ = 8."),
        order("py_func_005", "Собери функцию", "Расставьте строки так, чтобы программа вывела 12",
              ["def total(prices):", "    s = 0", "    for p in prices:", "        s += p", "    return s",
               "print(total([3, 4, 5]))"], topic="func_def",
              hint="Сначала объявление функции и её тело, затем вызов.",
              explanation="Тело функции идёт под def с отступом: обнуляем сумму, в цикле прибавляем, после цикла возвращаем. Вызов — в самом конце."),
        match("py_func_006", "Вызовы функции",
              ["f(1)", "f(1, 2)", "f(y=1, x=5)", "f('a', 'b')"],
              setup="""\
                def f(x, y=10):
                    return x + y""",
              topic="func_params", hint="Если y не передан, он равен 10. + для строк склеивает.",
              explanation="f(1) = 1 + 10, f(1, 2) = 3, f(y=1, x=5) = 5 + 1, а для строк + склеивает их: ab."),
        multi("py_func_007", "Корректные вызовы", "Функция объявлена как def f(a, b=0). Какие вызовы сработают без ошибки?",
              ["f(1)", "f(1, 2)", "f(b=2, a=1)", "f()", "f(a=1, 2)", "f(1, a=2)"], [0, 1, 2],
              check=lambda call: runs(f"def f(a, b=0):\n    return a\n{call}"),
              topic="func_params", hint="a обязателен, позиционные аргументы идут раньше именованных.",
              explanation="f(1), f(1, 2) и f(b=2, a=1) корректны. f() не передаёт обязательный a, f(a=1, 2) ставит позиционный после именованного, f(1, a=2) передаёт a дважды.",
              feedback={"f()": "Параметр a обязательный: TypeError missing argument.",
                        "f(a=1, 2)": "Позиционный аргумент не может идти после именованного: SyntaxError.",
                        "f(1, a=2)": "1 уже попал в a, а потом a передан ещё раз: TypeError multiple values."}),
        bug("py_func_008", "Пропавший результат", """\
            def area(w, h):
                w * h

            print(area(2, 3) + 1)""", {1: "    return w * h"},
            prompt="Программа должна вывести 7. Найдите строку с ошибкой", topic="func_def",
            hint="Что вернёт функция, если в ней нет return?",
            explanation="Выражение w * h вычисляется и пропадает. Функция возвращает None, а None + 1 — это TypeError. Нужно return w * h.",
            expect_error="TypeError"),
        predict("py_func_010", "Два результата", """\
                def min_max(nums):
                    return min(nums), max(nums)

                lo, hi = min_max([4, 1, 9])
                print(lo, hi)
                print(min_max([2]))""",
                ["1 9\n2", "1 9\n[2, 2]", "Ошибка"], position=2, topic="func_def",
                hint="return a, b возвращает кортеж из двух значений.",
                explanation="min_max возвращает кортеж (min, max). В первом вызове он распаковывается в lo и hi, во втором печатается целиком: (2, 2).",
                role="practice", difficulty=2,
                feedback={"1 9\n2": "Функция всегда возвращает пару значений, даже если они совпадают.",
                          "1 9\n[2, 2]": "Значения через запятую образуют кортеж, а не список.",
                          "Ошибка": "Вернуть несколько значений через запятую — обычное дело."}),
        predict("py_func_011", "Функция как значение", """\
                def twice(f, x):
                    return f(f(x))

                def inc(n):
                    return n + 1

                print(twice(inc, 5), twice(str.upper, "ok"))""",
                ["6 ok", "7 OKOK", "TypeError"], position=1, topic="func_def",
                hint="twice вызывает переданную функцию два раза подряд.",
                explanation="Функцию можно передать аргументом. inc(inc(5)) = 7. str.upper(str.upper(\"ok\")) = «OK».",
                role="practice", difficulty=2,
                feedback={"6 ok": "f вызывается дважды: f(f(x)).",
                          "7 OKOK": "upper не повторяет строку, он делает буквы заглавными — дважды заглавными остаются те же.",
                          "TypeError": "Функцию можно передать как обычное значение и вызвать внутри."}),
        predict("py_func_009", "Босс: забытая ветка", """\
                def sign(n):
                    if n > 0:
                        return "+"
                    elif n < 0:
                        return "-"

                print(sign(5), sign(-2), sign(0))""",
                ["+ - 0", "+ - +", "Ошибка"], position=2, topic="func_def",
                hint="Какая ветка сработает для 0 и что вернёт функция, если ни один return не выполнился?",
                explanation="Для 0 не подходит ни одно условие, return не выполняется, и функция возвращает None.",
                role="boss", difficulty=3,
                feedback={"+ - 0": "Функция не возвращает 0: для n = 0 не срабатывает ни один return.",
                          "+ - +": "0 > 0 — ложь, ветка с \"+\" не выполняется.",
                          "Ошибка": "Ошибки нет: функция без сработавшего return просто возвращает None."}),
    ],
))

# ------------------------------------------------------------- args/kwargs
MODULES.append(dict(
    id="args", title="Гибкие аргументы", description="*args, **kwargs и распаковка", icon="🎛️",
    topics=[
        topic("args_star", "*args и **kwargs",
              "*args собирает лишние позиционные аргументы в кортеж, **kwargs — лишние именованные в словарь.",
              """
              def total(*nums) принимает любое количество чисел: внутри nums — кортеж. total() тоже работает: nums будет пустым кортежем.

              def info(**options) принимает любые именованные аргументы: внутри options — словарь {имя: значение}.

              Имена args и kwargs — соглашение. Важны звёздочки: одна — кортеж позиционных, две — словарь именованных. Полный порядок параметров: def f(только_позиционные, /, обычные, *args, только_именованные, **kwargs).
              """,
              [("""\
                def total(*nums):
                    return sum(nums)

                print(total(1, 2, 3), total())""", None),
               ("""\
                def info(**options):
                    for key, value in options.items():
                        print(key, "=", value)

                info(color="red", size=3)""", "Порядок ключей совпадает с порядком аргументов.")],
              ["Ждать в *args список: это кортеж.",
               "Ставить **kwargs раньше *args в объявлении: SyntaxError."]),
        topic("args_unpack", "Распаковка при вызове",
              "f(*список) раскладывает элементы по позиционным параметрам, f(**словарь) — по именованным.",
              """
              Звёздочка при вызове делает обратное сбору: f(*[1, 2]) — то же, что f(1, 2), а f(**{"x": 1}) — то же, что f(x=1).

              Ключи словаря должны совпадать с именами параметров, иначе TypeError: unexpected keyword argument (если у функции нет **kwargs).

              print(*[1, 2, 3], sep="-") печатает 1-2-3: список распакован в три аргумента print.

              Распаковку можно сочетать: f(*coords, **options).
              """,
              [("""\
                def point(x, y, z=0):
                    return (x, y, z)

                coords = [1, 2]
                print(point(*coords), point(*coords, **{"z": 5}))""", None)],
              ["Передать список без звёздочки: f([1, 2]) — это один аргумент, а не два."]),
        topic("args_kwonly", "Только именованные и только позиционные",
              "Параметры после * передаются только по имени; параметры до / — только по позиции.",
              """
              def connect(host, *, timeout=5): timeout можно передать только как timeout=10. Это защищает от ошибок: в вызове сразу видно, что значит число.

              def div(a, b, /): a и b нельзя передать по имени. Так сделаны многие встроенные функции: len(obj=[1]) не сработает.

              Можно сочетать: def f(a, /, b, *, c).
              """,
              [("""\
                def connect(host, *, timeout=5):
                    return f"{host}:{timeout}"

                print(connect("db", timeout=10))""", None)],
              ["Передавать параметр после * позиционно: TypeError takes 1 positional argument."]),
        topic("args_mutable_default", "Изменяемое значение по умолчанию",
              "Значение по умолчанию вычисляется один раз при объявлении функции. Список по умолчанию общий для всех вызовов.",
              """
              def add(item, items=[]) создаёт один список в момент def. Каждый вызов без items берёт этот же список и продолжает его заполнять.

              Правильный приём — None по умолчанию и новый список внутри:
              if items is None: items = []

              Это касается любых изменяемых значений: списков, словарей, множеств.
              """,
              [("""\
                def add(item, items=None):
                    if items is None:
                        items = []
                    items.append(item)
                    return items

                print(add("a"), add("b"))""", "Каждый вызов получает новый список.")],
              ["items=[] или options={} в объявлении: данные «перетекают» между вызовами."]),
    ],
    tasks=[
        task("t_args_average", "Среднее любого количества",
             "Напишите функцию average(*nums), которая возвращает среднее арифметическое аргументов, а для пустого вызова — целое 0. Прочитайте числа из строки (через пробел, строка может быть пустой) и выведите результат так, как в заготовке: print(round(average(*числа), 2)).",
             solution="""\
                def average(*nums):
                    if not nums:
                        return 0
                    return sum(nums) / len(nums)

                numbers = [float(x) for x in input().split()]
                print(round(average(*numbers), 2))""",
             starter="""\
                def average(*nums):
                    return sum(nums)

                numbers = [float(x) for x in input().split()]
                print(round(average(*numbers), 2))""",
             tests=["1 2 3 4\n", "10\n", "\n", "2.5 3.5\n", "1 2 2\n"],
             hint="Пустой кортеж — это ложь: if not nums.", difficulty=2,
             requires=dict(defines=["average"], uses=["star_args"])),
    ],
    levels=[
        predict("py_args_001", "Сколько угодно чисел", """\
                def count(*items):
                    return len(items)

                print(count("a", "b"), count())""",
                ["2", "2 None", "TypeError"], position=0, topic="args_star",
                hint="Без аргументов items — пустой кортеж. Какая у него длина?",
                explanation="*items собирает аргументы в кортеж: ('a', 'b') и (). Длина пустого кортежа — 0.",
                feedback={"2": "print выводит два значения: второе — count() = 0.",
                          "2 None": "len пустого кортежа — 0, а не None.",
                          "TypeError": "*items принимает и ноль аргументов."}),
        fill("py_args_002", "Собрать остальное", "Сделайте так, чтобы функция принимала любое число аргументов после a",
             """\
             def f(a, {{0}}rest):
                 print(a, rest)

             f(1, 2, 3)""", ["*", "**", "&", "@"], ["*"],
             topic="args_star", hint="Одна звёздочка собирает позиционные аргументы в кортеж.",
             explanation="*rest собирает 2 и 3 в кортеж (2, 3). Две звёздочки собирают только именованные аргументы.",
             expect="1 (2, 3)\n"),
        predict("py_args_003", "Словарь параметров", """\
                def info(**options):
                    print(options)

                info(color="red", size=3)""",
                ["{color: red, size: 3}", "('red', 3)", "['color', 'size']"], position=2, topic="args_star",
                hint="Две звёздочки собирают именованные аргументы в словарь.",
                explanation="**options — словарь {'color': 'red', 'size': 3}; print показывает строки в кавычках.",
                feedback={"{color: red, size: 3}": "Ключи словаря — строки, print показывает их в кавычках.",
                          "('red', 3)": "Кортеж собирает *args. ** собирает словарь.",
                          "['color', 'size']": "Сохраняются и имена, и значения: это словарь."}),
        match("py_args_004", "Что попало в args и kwargs",
              ["show(1, 2)", "show(x=1)", "show(1, y=2)", "show(*[1, 2], **{'z': 3})"],
              setup="""\
                def show(*args, **kwargs):
                    return f"{args} {kwargs}\"""",
              topic="args_unpack", hint="Позиционные — в кортеж args, именованные — в словарь kwargs. Звёздочки при вызове распаковывают.",
              explanation="Кортеж из одного элемента пишется с запятой: (1,). Распаковка *[1, 2] даёт позиционные 1 и 2, **{'z': 3} — именованный z=3."),
        typed("py_args_005", "Распаковка", """\
              def point(x, y, z=0):
                  return f"({x}, {y}, {z})"

              coords = [1, 2]
              opts = {"z": 5}
              print(point(*coords))
              print(point(*coords, **opts))
              print(point(**{"y": 7, "x": 3}))""",
              topic="args_unpack", hint="*coords даёт x=1, y=2. Ключи словаря становятся именами параметров.",
              explanation="point(1, 2) → z по умолчанию 0; затем z=5; в третьем вызове x=3, y=7 по именам."),
        predict("py_args_006", "Общий список", """\
                def add_item(item, items=[]):
                    items.append(item)
                    return items

                print(add_item("a"))
                print(add_item("b"))""",
                ["['a']\n['b']", "['a', 'b']\n['a', 'b']", "TypeError"], position=1, topic="args_mutable_default",
                hint="Когда создаётся значение по умолчанию — при def или при каждом вызове?",
                explanation="Список [] по умолчанию создаётся один раз при def и общий для всех вызовов. Первый вызов печатает ['a'], второй добавляет «b» в тот же список.",
                role="challenge", difficulty=3,
                feedback={"['a']\n['b']": "Значение по умолчанию создаётся один раз, и второй вызов получает тот же список.",
                          "['a', 'b']\n['a', 'b']": "Первый print срабатывает сразу после первого вызова — тогда в списке только «a».",
                          "TypeError": "Список по умолчанию — допустимый, хоть и опасный код."}),
        multi("py_args_007", "Только по имени", "В каких объявлениях параметр c можно передать только по имени?",
              ["def f(a, b, *, c=0)", "def f(a, *args, c=0)", "def f(a, b, c=0)", "def f(*, a=0, b=0, c=0)",
               "def f(a, b, /, c=0)"], [0, 1, 3],
              check=lambda sig: run(f"{sig}:\n    return c\nassert f(1, 2, 3) == 3").error is not None,
              topic="args_kwonly", hint="Параметры после * или после *args нельзя заполнить позиционно.",
              explanation="После * и после *args идут только именованные параметры. / делает параметры до него только позиционными, но c стоит после /, так что его можно передать как угодно.",
              feedback={"def f(a, b, c=0)": "Обычный параметр можно передать и позиционно: f(1, 2, 3).",
                        "def f(a, b, /, c=0)": "/ ограничивает только a и b. c можно передать позиционно."}),
        choice("py_args_008", "Только позиционные", "Что произойдёт при вызове div(a=7, b=2)?",
               ["3", "3.5", "TypeError", "SyntaxError"], 2,
               code="""\
                def div(a, b, /):
                    return a // b

                print(div(a=7, b=2))""",
               check=lambda option: result_of("def div(a, b, /):\n    return a // b\nprint(div(a=7, b=2))") == option,
               topic="args_kwonly", hint="Что означает / в списке параметров?",
               explanation="Параметры до / передаются только по позиции. Вызов с a= и b= — TypeError: positional-only arguments passed as keyword.",
               role="practice", difficulty=2,
               feedback={"3": "Так было бы при div(7, 2). Здесь аргументы переданы по именам.",
                         "3.5": "// — целочисленное деление, и до вычисления дело не дойдёт.",
                         "SyntaxError": "Синтаксис корректен, ошибка возникает при вызове: TypeError."}),
        typed("py_args_010", "Звёздочка в print", """\
              nums = [1, 2, 3]
              print(*nums, sep="-")
              print(nums, sep="-")""",
              topic="args_unpack", hint="*nums превращает список в три отдельных аргумента.",
              explanation="print(*nums) получает три аргумента и ставит между ними sep. Без звёздочки аргумент один — сам список, разделителю ставить нечего.",
              role="practice", difficulty=2),
        order("py_args_009", "Босс: журнал вызовов", "Соберите функцию-обёртку, которая выведет max(3, 9, 4) -> 9",
              ["def log_call(func, *args, **kwargs):", "    result = func(*args, **kwargs)",
               "    print(f\"{func.__name__}{args} -> {result}\")", "    return result", "log_call(max, 3, 9, 4)"],
              topic="args_unpack", hint="Сначала функция вызывается с распакованными аргументами, потом печатается результат.",
              explanation="*args собирает (3, 9, 4), а func(*args, **kwargs) передаёт их дальше без изменений. Это основа декораторов.",
              role="boss", difficulty=3),
    ],
))

# --------------------------------------------------------- scope & closures
MODULES.append(dict(
    id="scope", title="Области видимости", description="LEGB, global, nonlocal, замыкания", icon="🔭",
    topics=[
        topic("scope_legb", "Правило LEGB",
              "Имя ищется по очереди: Local → Enclosing → Global → Built-in. Присваивание внутри функции делает имя локальным.",
              """
              Local — переменные текущей функции. Enclosing — переменные внешней функции (если функция вложенная). Global — переменные модуля. Built-in — встроенные имена вроде len и print.

              Читать глобальную переменную внутри функции можно без объявлений. Но если внутри функции этому имени что-то присваивается (даже ниже по тексту), имя считается локальным во всей функции. Тогда чтение до присваивания даёт UnboundLocalError.

              Локальным имя делает любое связывание внутри функции: =, +=, for x in, import, def, del. А блоки if и for своей области видимости не создают: переменная, заданная внутри if, видна после него.
              """,
              [("""\
                x = 10

                def show():
                    x = 5
                    print("внутри", x)

                show()
                print("снаружи", x)""", "Локальная x не меняет глобальную."),
               ("""\
                rate = 2

                def apply(n):
                    return n * rate

                print(apply(21))""", "Чтение глобальной переменной работает без global.")],
              ["count += 1 внутри функции без global: UnboundLocalError.",
               "Называть переменные именами встроенных функций (list, sum): они перекрывают встроенные."]),
        topic("scope_global", "global и nonlocal",
              "global имя — присваивать глобальной переменной; nonlocal имя — переменной внешней функции.",
              """
              global count внутри функции говорит: count — это переменная модуля, присваивание меняет её.

              nonlocal count во вложенной функции говорит: count — переменная из объемлющей функции. На уровне модуля nonlocal не работает (SyntaxError).

              Глобальное состояние усложняет программы. Чаще лучше вернуть значение из функции или использовать замыкание или класс.
              """,
              [("""\
                count = 0

                def inc():
                    global count
                    count += 1

                inc()
                inc()
                print(count)""", None)],
              ["nonlocal для переменной модуля: SyntaxError no binding for nonlocal."]),
        topic("scope_closure", "Замыкания",
              "Вложенная функция запоминает переменные внешней функции, даже когда внешняя уже завершилась.",
              """
              multiplier(k) объявляет внутри себя функцию mul(x), которая возвращает x * k, и возвращает mul — саму функцию, без вызова. mul «замыкает» k: multiplier(3) возвращает функцию, которая умножает на 3. Код — в примере ниже.

              Замыкание хранит ссылку на переменную, а не её значение на момент создания. Поэтому функции, созданные в цикле, видят последнее значение переменной цикла. Решение: передать значение параметром по умолчанию (def f(i=i)) или создать функцию через фабрику.
              """,
              [("""\
                def multiplier(k):
                    def mul(x):
                        return x * k
                    return mul

                triple = multiplier(3)
                print(triple(5), multiplier(10)(4))""", None),
               ("""\
                def make_counter():
                    count = 0
                    def step():
                        nonlocal count
                        count += 1
                        return count
                    return step

                c = make_counter()
                print(c(), c(), c())""", "У каждого счётчика своя переменная count.")],
              ["Ждать, что функции из цикла запомнят разные значения переменной цикла."]),
    ],
    tasks=[
        task("t_scope_running_total", "Накопитель",
             "Напишите функцию make_acc(), которая возвращает функцию add(x): add прибавляет x к накопленной сумме и возвращает новую сумму. Прочитайте целые числа через пробел и выведите накопленную сумму после каждого числа, через пробел.",
             solution="""\
                def make_acc():
                    total = 0
                    def add(x):
                        nonlocal total
                        total += x
                        return total
                    return add

                add = make_acc()
                print(" ".join(str(add(int(x))) for x in input().split()))""",
             starter="""\
                def make_acc():
                    def add(x):
                        return x
                    return add

                add = make_acc()
                print(" ".join(str(add(int(x))) for x in input().split()))""",
             tests=["1 2 3\n", "5\n", "10 -4 7 1\n", "0 0 7\n"],
             hint="Сумму храните в переменной make_acc и меняйте её через nonlocal.", difficulty=3,
             requires=dict(defines=["make_acc"], uses=["nonlocal"])),
    ],
    levels=[
        predict("py_scope_001", "Две переменные x", """\
                x = 10

                def show():
                    x = 5
                    print(x)

                show()
                print(x)""",
                ["5\n5", "10\n10", "10\n5"], position=1, topic="scope_legb",
                hint="Присваивание внутри функции создаёт новую, локальную переменную.",
                explanation="x = 5 внутри show — локальная переменная. Глобальная x остаётся 10.",
                feedback={"5\n5": "Локальная x не меняет глобальную.",
                          "10\n10": "Внутри функции печатается локальная x = 5.",
                          "10\n5": "Сначала вызывается show (печатает 5), потом печатается глобальная x."}),
        fill("py_scope_002", "Глобальный счётчик", "Сделайте так, чтобы функция меняла глобальную переменную count",
             """\
             count = 0

             def inc():
                 {{0}} count
                 count += 1

             inc()
             inc()
             print(count)""", ["global", "nonlocal", "local", "static"], ["global"],
             topic="scope_global", hint="Нужна переменная уровня модуля.",
             explanation="global count разрешает функции присваивать переменной модуля. nonlocal работает только с переменными внешней функции.",
             expect="2\n"),
        bug("py_scope_003", "Снятие со счёта", """\
            balance = 100

            def withdraw(amount):
                if amount > balance:
                    return "мало средств"
                balance = balance - amount

            print(withdraw(30))""", {5: "    return balance - amount"},
            prompt="Функция должна вернуть остаток 70, не меняя глобальную переменную. Найдите строку, из-за которой возникает ошибка",
            topic="scope_legb",
            hint="Python падает на строке с if, но причина ниже: что делает присваивание внутри функции?",
            explanation="Из-за присваивания balance = ... имя balance становится локальным во всей функции. Тогда уже в if читается локальная переменная, которой ещё нет: UnboundLocalError. Достаточно вернуть balance - amount.",
            expect_error="UnboundLocalError", difficulty=3),
        fill("py_scope_004", "Счётчик-замыкание", "Сделайте так, чтобы step увеличивал счётчик внешней функции",
             """\
             def make_counter():
                 count = 0
                 def step():
                     {{0}} count
                     count += 1
                     return count
                 return step

             c = make_counter()
             c()
             print(c())""", ["nonlocal", "global", "return", "del"], ["nonlocal"],
             topic="scope_closure", hint="count живёт во внешней функции, а не в модуле.",
             explanation="nonlocal count связывает имя с переменной make_counter. global искал бы count в модуле, где её нет.",
             expect="2\n"),
        typed("py_scope_005", "Фабрика функций", """\
              def multiplier(k):
                  def mul(x):
                      return x * k
                  return mul

              double = multiplier(2)
              triple = multiplier(3)
              print(double(5), triple(5))
              print(multiplier(10)(4))""",
              topic="scope_closure", hint="Каждая функция mul помнит своё k.",
              explanation="double умножает на 2, triple — на 3: 10 и 15. multiplier(10) сразу вызывается с 4: 40."),
        match("py_scope_006", "LEGB", ["Local", "Enclosing", "Global", "Built-in"],
              rights=["Внутри текущей функции", "Во внешней функции", "На уровне модуля", "Встроенные имена: len, print"],
              prompt="Сопоставьте область видимости и где живёт имя", topic="scope_legb",
              hint="Порядок поиска имени — от ближнего к дальнему.",
              explanation="Python ищет имя сначала в текущей функции, затем во внешних функциях, затем в модуле и в конце среди встроенных имён."),
        multi("py_scope_007", "Верные утверждения", "Какие утверждения верны?",
              ["Функция может читать глобальную переменную без global",
               "Присваивание внутри функции (без global и nonlocal) создаёт локальную переменную",
               "nonlocal можно применить к переменной модуля",
               "Замыкание помнит переменные внешней функции после её завершения",
               "global нужен, чтобы прочитать глобальную переменную"], [0, 1, 3],
              check=lambda s: {
                  "Функция может читать глобальную переменную без global":
                      runs("x = 1\ndef f():\n    return x\nassert f() == 1"),
                  "Присваивание внутри функции (без global и nonlocal) создаёт локальную переменную":
                      runs("x = 1\ndef f():\n    x = 2\nf()\nassert x == 1"),
                  "nonlocal можно применить к переменной модуля":
                      runs("x = 1\ndef f():\n    nonlocal x\n    x = 2\nf()"),
                  "Замыкание помнит переменные внешней функции после её завершения":
                      runs("def o():\n    v = 7\n    return lambda: v\nassert o()() == 7"),
                  "global нужен, чтобы прочитать глобальную переменную":
                      not runs("x = 1\ndef f():\n    return x\nf()"),
              }[s],
              topic="scope_global", hint="Чтение и присваивание работают по-разному.",
              explanation="Читать глобальную переменную можно свободно, global нужен только для присваивания. nonlocal работает лишь с переменными внешней функции.",
              feedback={"nonlocal можно применить к переменной модуля": "Для переменной модуля nonlocal даёт SyntaxError: нужен global.",
                        "global нужен, чтобы прочитать глобальную переменную": "Для чтения global не нужен — только для присваивания."}),
        predict("py_scope_008", "Функции в цикле", """\
                def make_funcs():
                    funcs = []
                    for i in range(3):
                        def f():
                            return i
                        funcs.append(f)
                    return funcs

                print([f() for f in make_funcs()])""",
                ["[0, 1, 2]", "[0, 0, 0]", "[3, 3, 3]"], position=3, topic="scope_closure",
                hint="Функция читает i в момент вызова, а не в момент создания.",
                explanation="Все три замыкания ссылаются на одну и ту же переменную i функции make_funcs. К моменту вызова цикл закончился и i = 2. Исправление — def f(i=i): значение по умолчанию вычисляется в момент создания.",
                role="challenge", difficulty=3,
                feedback={"[0, 1, 2]": "Функции не запоминают значение i при создании, они читают переменную при вызове.",
                          "[0, 0, 0]": "i меняется в цикле, и все функции видят последнее значение.",
                          "[3, 3, 3]": "range(3) заканчивается на 2: после цикла i = 2."}),
        bug("py_scope_010", "Занятое имя", """\
            list = [3, 1, 2]
            letters = list("ab")
            print(list, letters)""", {0: "nums = [3, 1, 2]"},
            prompt="Найдите строку, из-за которой падает программа (вывод исправленной версии может отличаться)",
            topic="scope_legb", hint="Где Python найдёт имя list — среди встроенных или в модуле?",
            explanation="Переменная list на уровне модуля перекрыла встроенную функцию list (правило LEGB: Global раньше Built-in). list(\"ab\") пытается вызвать список: TypeError. Не занимайте имена встроенных функций.",
            expect_error="TypeError", difficulty=2),
        predict("py_scope_009", "Босс: nonlocal", """\
                x = "global"

                def outer():
                    x = "enclosing"
                    def inner():
                        nonlocal x
                        x = "changed"
                    inner()
                    return x

                print(outer(), x)""",
                ["enclosing global", "changed changed", "global global"], position=3, topic="scope_global",
                hint="nonlocal меняет переменную outer, но не глобальную.",
                explanation="inner меняет x из outer на «changed», и outer возвращает его. Глобальная x не тронута.",
                role="boss", difficulty=3,
                feedback={"enclosing global": "nonlocal x позволяет inner изменить x из outer.",
                          "changed changed": "nonlocal не трогает глобальную переменную.",
                          "global global": "outer возвращает свою x, а не глобальную."}),
    ],
))

# ----------------------------------------------------- functional style
MODULES.append(dict(
    id="functional", title="Функциональный стиль", description="lambda, sorted, map, filter, functools",
    icon="λ",
    topics=[
        topic("fn_lambda_key", "lambda и параметр key",
              "lambda x: выражение — короткая безымянная функция. Часто передаётся в key у sorted, min, max.",
              """
              lambda x: x * x — то же, что def f(x): return x * x, но в одну строку и без имени. Внутри lambda только одно выражение, без return. Lambda нужна там, где функция передаётся аргументом; давать ей имя (square = lambda ...) не принято — для этого есть def.

              key — функция, которая для каждого элемента вычисляет ключ сравнения. sorted(words, key=len) сортирует по длине, max(people, key=lambda p: p[1]) ищет человека с наибольшим вторым полем.

              sorted возвращает новый список, list.sort() сортирует на месте и возвращает None. Сортировка устойчивая: равные по ключу элементы сохраняют исходный порядок.
              """,
              [("""\
                words = ["banana", "kiwi", "apple"]
                print(sorted(words, key=len))
                print(max(words, key=lambda w: w[-1]))""", "max по последней букве: a, i, e — наибольшая i."),
               ("""\
                people = [("Ann", 31), ("Bob", 25)]
                people.sort(key=lambda p: p[1])
                print(people)""", "sort меняет сам список.")],
              ["x = items.sort() — в x окажется None.",
               "Писать key=len() со скобками: нужно передать функцию, а не результат её вызова."]),
        topic("fn_builtins", "map, filter, zip, enumerate, any, all",
              "Встроенные функции для работы с последовательностями. Многие возвращают ленивые объекты, которые превращают в список через list().",
              """
              map(f, seq) применяет f к каждому элементу. filter(f, seq) оставляет элементы, для которых f истинна (filter(None, seq) убирает «ложные»).

              zip(a, b) идёт по двум последовательностям параллельно и останавливается на самой короткой. enumerate(seq, start=1) добавляет номер.

              any(seq) — есть ли хоть одно истинное значение, all(seq) — все ли истинны. all([]) — True.

              map, filter и zip возвращают итераторы: их можно пройти один раз. map может идти по нескольким последовательностям сразу: map(lambda a, b: a * b, xs, ys). zip(a, b, strict=True) вызывает ValueError, если длины разные.
              """,
              [("""\
                nums = [3, 0, 8]
                print(list(map(str, nums)), list(filter(None, nums)))
                print(any(n > 7 for n in nums), all(nums))""", None),
               ("""\
                for i, (name, year) in enumerate(zip(["Ада", "Линус"], [1815, 1969]), start=1):
                    print(i, name, year)""", None)],
              ["print(map(...)) показывает объект map, а не значения: нужен list().",
               "Второй проход по одному и тому же map или zip ничего не даёт: итератор исчерпан."]),
        topic("fn_functools", "functools: reduce и partial",
              "reduce сворачивает последовательность в одно значение; partial фиксирует часть аргументов функции.",
              """
              reduce(f, seq, начальное) вызывает f(acc, x) для каждого элемента, накапливая результат: reduce(lambda a, x: a * x, [1, 2, 3, 4]) = 24. Начальное значение передаётся только позиционно.

              partial(int, base=2) создаёт вызываемый объект, похожий на int, но с уже заданным base. Удобно для колбэков и настройки функций.

              Для простых сумм есть sum — она понятнее reduce.
              """,
              [("""\
                from functools import reduce, partial

                print(reduce(lambda acc, x: acc * x, [1, 2, 3, 4]))
                from_binary = partial(int, base=2)
                print(from_binary("1010"))""", None)],
              ["reduce без начального значения на пустом списке — TypeError."]),
    ],
    tasks=[
        task("t_fn_rank", "Таблица результатов",
             "В первой строке — число n, далее n строк «имя баллы». Выведите имена по убыванию баллов, а при равных баллах — по алфавиту, каждое с новой строки.",
             solution="""\
                n = int(input())
                rows = []
                for _ in range(n):
                    name, score = input().split()
                    rows.append((name, int(score)))
                for name, _ in sorted(rows, key=lambda r: (-r[1], r[0])):
                    print(name)""",
             starter="""\
                n = int(input())
                rows = []
                for _ in range(n):
                    name, score = input().split()
                    rows.append((name, int(score)))
                for name, _ in rows:
                    print(name)""",
             tests=["3\nann 5\nbob 9\ncid 7\n", "3\nzoe 5\namy 5\nbob 1\n", "1\nsolo 3\n",
                    "4\nd 1\nc 1\nb 2\na 1\n"],
             hint="Ключ сортировки может быть кортежем: (-баллы, имя).", difficulty=3,
             requires=dict(uses=["lambda"])),
    ],
    levels=[
        predict("py_fn_001", "Ключ сортировки", """\
                nums = [3, 1, 2]
                print(sorted(nums, key=lambda x: -x))""",
                ["[1, 2, 3]", "[-3, -2, -1]", "[-1, -2, -3]"], position=1, topic="fn_lambda_key",
                hint="key только вычисляет, по чему сравнивать. В результате — сами элементы.",
                explanation="Ключи -3, -1, -2: по возрастанию ключа порядок 3, 2, 1. В результат попадают исходные числа, а не ключи.",
                feedback={"[1, 2, 3]": "Сравниваются ключи -x: наибольшее число даёт наименьший ключ.",
                          "[-3, -2, -1]": "key не меняет элементы, он только задаёт порядок.",
                          "[-1, -2, -3]": "key не меняет элементы, он только задаёт порядок."}),
        predict("py_fn_002", "Сортировка по длине", """\
                words = ["banana", "kiwi", "apple"]
                print(sorted(words, key=len))""",
                ["['apple', 'banana', 'kiwi']", "['banana', 'apple', 'kiwi']", "[4, 5, 6]"], position=1,
                topic="fn_lambda_key", hint="key=len сравнивает длины слов.",
                explanation="Длины: kiwi — 4, apple — 5, banana — 6. sorted возвращает сами слова в порядке возрастания ключа.",
                feedback={"['apple', 'banana', 'kiwi']": "Так сортирует sorted без key — по алфавиту.",
                          "['banana', 'apple', 'kiwi']": "Это сортировка по убыванию длины, а sorted по умолчанию сортирует по возрастанию.",
                          "[4, 5, 6]": "key влияет только на порядок: возвращаются сами слова."}),
        fill("py_fn_003", "Самый старший", "Найдите самого старшего: возраст — второй элемент кортежа",
             """\
             people = [("Zoe", 31), ("Bob", 25), ("Ann", 40)]
             oldest = max(people, key=lambda p: p[{{0}}])
             print(oldest[0])""", ["1", "0", "-2", "2"], ["1"],
             topic="fn_lambda_key", hint="Индексация с нуля: имя — p[0].",
             explanation="key=lambda p: p[1] сравнивает возрасты, и max находит («Ann», 40).",
             expect="Ann\n"),
        match("py_fn_004", "Встроенные помощники",
              ["list(map(str, nums))", "list(filter(None, nums))", "any(n > 7 for n in nums)", "all(nums)",
               "list(zip(nums, 'ab'))"],
              setup="nums = [3, 0, 8, 5]", topic="fn_builtins",
              hint="filter(None, ...) убирает ложные значения. zip останавливается на короткой последовательности.",
              explanation="map превращает числа в строки, filter(None) убирает 0, any находит 8 > 7, all ложно из-за 0, zip берёт две пары."),
        typed("py_fn_005", "Второй проход", """\
              pairs = zip([1, 2, 3], [4, 5, 6])
              print(sum(x * y for x, y in pairs))
              print(sum(x * y for x, y in pairs))""",
              topic="fn_builtins", hint="zip возвращает итератор. Сколько раз по нему можно пройти?",
              explanation="Первый проход: 1·4 + 2·5 + 3·6 = 32. zip — итератор, после первого прохода он исчерпан, и второй sum получает пустую последовательность — 0."),
        bug("py_fn_006", "Пропавшая сортировка", """\
            scores = [70, 95, 82]
            top = scores.sort(reverse=True)
            print(top[0], scores)""", {1: "top = sorted(scores, reverse=True)"},
            prompt="Нужно вывести наибольший балл и не испортить исходный порядок scores. Найдите строку с ошибкой",
            topic="fn_lambda_key", alt_fixes={2: "print(scores[0], scores)"},
            hint="Что возвращает метод sort?",
            explanation="list.sort() сортирует список на месте и возвращает None, поэтому top[0] — TypeError. sorted возвращает новый список.",
            expect_error="TypeError"),
        predict("py_fn_007", "reduce и partial", """\
                from functools import reduce, partial

                print(reduce(lambda acc, s: s + acc, ["a", "b", "c"], ""))
                from_hex = partial(int, base=16)
                print(from_hex("ff"))""",
                ["abc\n255", "cba\nff", "abc\nff"], position=1, topic="fn_functools",
                hint="Лямбда приклеивает новый элемент слева от накопленного. int с base=16 читает шестнадцатеричную запись.",
                explanation="acc: \"\" → \"a\" → \"ba\" → \"cba\". partial фиксирует base=16, и «ff» читается как 255.",
                role="practice", difficulty=2,
                feedback={"abc\n255": "s + acc ставит новый элемент перед накопленным: строка собирается задом наперёд.",
                          "cba\nff": "from_hex возвращает число: шестнадцатеричное ff — это 255.",
                          "abc\nff": "Порядок склейки — s + acc, а int возвращает число."}),
        multi("py_fn_008", "Отбор больших", "nums = [1, 5, 2, 7]. Какие выражения дают список [5, 7]?",
              ["[n for n in nums if n > 2]", "list(filter(lambda n: n > 2, nums))", "filter(lambda n: n > 2, nums)",
               "list(map(lambda n: n > 2, nums))", "sorted(n for n in nums if n > 2)"], [0, 1, 4],
              check=lambda expr: eval(expr, {"nums": [1, 5, 2, 7]}) == [5, 7],
              topic="fn_builtins", hint="Нужен именно список чисел.",
              explanation="Включение, list(filter(...)) и sorted(...) дают [5, 7]. Голый filter — ленивый объект, а map с условием даёт список True/False.",
              feedback={"filter(lambda n: n > 2, nums)": "filter возвращает ленивый объект, а не список.",
                        "list(map(lambda n: n > 2, nums))": "map применяет условие к каждому: [False, True, False, True]."}),
        predict("py_fn_010", "lambda в цикле", """\
                fs = [lambda: i for i in range(3)]
                gs = [lambda i=i: i for i in range(3)]
                print([f() for f in fs], [g() for g in gs])""",
                ["[0, 1, 2] [0, 1, 2]", "[2, 2, 2] [2, 2, 2]", "[0, 1, 2] [2, 2, 2]"], position=1, topic="fn_lambda_key",
                hint="Значение по умолчанию вычисляется при создании функции, а тело — при вызове.",
                explanation="Лямбды из fs читают i при вызове, когда i уже 2. В gs значение i сохранено в параметре по умолчанию в момент создания каждой лямбды.",
                role="challenge", difficulty=3,
                feedback={"[0, 1, 2] [0, 1, 2]": "Тело lambda: i читает переменную в момент вызова — тогда i = 2.",
                          "[2, 2, 2] [2, 2, 2]": "i=i сохраняет значение при создании функции.",
                          "[0, 1, 2] [2, 2, 2]": "Наоборот: без i=i все лямбды видят последнее значение."}),
        order("py_fn_009", "Босс: конвейер заказов", "Расставьте строки так, чтобы вывелось tea, coffee",
              ["orders = [(\"tea\", 3), (\"cake\", 0), (\"coffee\", 2)]",
               "in_stock = [o for o in orders if o[1] > 0]",
               "in_stock.sort(key=lambda o: o[1], reverse=True)",
               "names = [name for name, _ in in_stock]",
               "print(\", \".join(names))"],
              topic="fn_lambda_key", hint="Данные → фильтр → сортировка → имена → вывод.",
              explanation="Сначала отбрасываем товары с нулевым остатком, затем сортируем по остатку по убыванию и берём имена.",
              role="boss", difficulty=3),
    ],
))

# --------------------------------------------------------------- recursion
MODULES.append(dict(
    id="recursion", title="Рекурсия", description="Функция вызывает саму себя", icon="🪆",
    topics=[
        topic("rec_basics", "Базовый случай и шаг рекурсии",
              "Рекурсивная функция вызывает саму себя для задачи поменьше и останавливается на базовом случае.",
              """
              Две обязательные части: базовый случай (ответ известен сразу, например factorial(0) = 1) и рекурсивный шаг, который приближает к базовому случаю (factorial(n) = n * factorial(n - 1)).

              Каждый вызов ждёт результата следующего — они складываются в стек вызовов. Код после рекурсивного вызова выполняется на обратном пути, в обратном порядке.

              Без базового случая (или если шаг к нему не приближает) вызовы не кончаются, и Python останавливает программу: RecursionError (глубина около 1000 вызовов).
              """,
              [("""\
                def factorial(n):
                    if n == 0:
                        return 1
                    return n * factorial(n - 1)

                print(factorial(5))""", None),
               ("""\
                def show(n):
                    if n == 0:
                        return
                    print("вход", n)
                    show(n - 1)
                    print("выход", n)

                show(2)""", "После рекурсивного вызова код выполняется в обратном порядке.")],
              ["Шаг, который пропускает базовый случай: countdown(n - 2) при нечётном n никогда не даст 0."]),
        topic("rec_structures", "Рекурсия по вложенным структурам",
              "Рекурсия естественна для вложенных данных: списков в списках, деревьев, папок.",
              """
              Если элемент сам является списком — обрабатываем его той же функцией. Иначе это «лист», и с ним работаем напрямую.

              Так считают глубину вложенности, «расплющивают» списки, обходят дерево каталогов или JSON.

              isinstance(x, list) возвращает True, если x — список. max(..., default=0) возвращает 0 для пустой последовательности вместо ValueError.
              """,
              [("""\
                def flatten(items):
                    result = []
                    for x in items:
                        if isinstance(x, list):
                            result.extend(flatten(x))
                        else:
                            result.append(x)
                    return result

                print(flatten([1, [2, [3, 4]], 5]))""", None)],
              ["append вместо extend для результата рекурсии: вложенность сохранится."]),
        topic("rec_memo", "Мемоизация",
              "functools.lru_cache (или cache) запоминает результаты вызовов. Повторные вызовы с теми же аргументами не пересчитываются.",
              """
              Наивный fib(n) = fib(n - 1) + fib(n - 2) вызывает одни и те же значения экспоненциально много раз: fib(35) считается секунды, fib(50) — десятки минут.

              Мемоизация вручную: словарь memo хранит готовые ответы, и перед вычислением функция проверяет, нет ли там уже результата.

              То же самое одной строкой: @lru_cache(maxsize=None) над функцией (это декоратор, о них — в отдельном модуле) кэширует результаты: каждое fib(k) вычисляется один раз, и время становится линейным.

              Аргументы кэшируемой функции должны быть хешируемыми: числа, строки, кортежи из хешируемых значений.
              """,
              [("""\
                memo = {}

                def fib(n):
                    if n < 2:
                        return n
                    if n not in memo:
                        memo[n] = fib(n - 1) + fib(n - 2)
                    return memo[n]

                print(fib(80))""", "Без кэша такой вызов не закончился бы."),
               ("""\
                from functools import lru_cache

                @lru_cache(maxsize=None)
                def fib(n):
                    return n if n < 2 else fib(n - 1) + fib(n - 2)

                print(fib(90))""", "То же через lru_cache.")],
              ["Кэшировать функцию со списком в аргументах: TypeError unhashable type.",
               "Думать, что кэш снимает лимит глубины: fib(1500) с lru_cache всё равно даст RecursionError. Для больших n — цикл.",
               "Ждать оптимизации хвостовой рекурсии: в Python её нет, глубина ограничена (sys.getrecursionlimit(), обычно 1000)."]),
    ],
    tasks=[
        task("t_rec_digits", "Сумма цифр",
             "Напишите рекурсивную функцию digit_sum(n), которая возвращает сумму цифр неотрицательного числа (без циклов и строк). Прочитайте n и выведите digit_sum(n).",
             solution="""\
                def digit_sum(n):
                    if n < 10:
                        return n
                    return n % 10 + digit_sum(n // 10)

                print(digit_sum(int(input())))""",
             starter="""\
                def digit_sum(n):
                    return n % 10

                print(digit_sum(int(input())))""",
             tests=["12345\n", "7\n", "0\n", "909\n", "999999999999999999\n"],
             hint="Последняя цифра — n % 10, остальные — n // 10.", difficulty=2,
             requires=dict(defines=["digit_sum"], recursive=["digit_sum"], forbids=["loop", "comprehension"],
                           no_calls=["str"])),
        task("t_rec_hanoi", "Ханойская башня",
             "В строке — целое n (1 ≤ n ≤ 10). Выведите ходы минимального решения задачи о Ханойской башне: перенос n дисков со стержня A на стержень C через B. Каждый ход — строка вида «A -> C».",
             solution="""\
                def hanoi(n, src, via, dst):
                    if n == 0:
                        return
                    hanoi(n - 1, src, dst, via)
                    print(f"{src} -> {dst}")
                    hanoi(n - 1, via, src, dst)

                hanoi(int(input()), "A", "B", "C")""",
             starter="""\
                def hanoi(n, src, via, dst):
                    print(f"{src} -> {dst}")

                hanoi(int(input()), "A", "B", "C")""",
             tests=["1\n", "2\n", "3\n", "5\n", "7\n"],
             hint="Перенесите n - 1 дисков на вспомогательный стержень, самый большой — на цель, затем n - 1 дисков сверху.",
             difficulty=3, requires=dict(defines=["hanoi"], recursive=["hanoi"])),
    ],
    levels=[
        predict("py_rec_001", "Сумма степеней", """\
                def total(n):
                    if n == 0:
                        return 0
                    return n * n + total(n - 1)

                print(total(4))""",
                ["10", "16", "RecursionError"], position=2, topic="rec_basics",
                hint="total(4) = 16 + total(3) = 16 + 9 + total(2) …",
                explanation="total(4) = 4² + 3² + 2² + 1² + 0 = 16 + 9 + 4 + 1 = 30.",
                feedback={"10": "Это сумма 1..4, а функция складывает квадраты.",
                          "16": "16 — только первое слагаемое 4²; дальше рекурсия добавляет 3², 2², 1².",
                          "RecursionError": "Базовый случай n == 0 есть, и n уменьшается до него."}),
        typed("py_rec_002", "Вход и выход", """\
              def show(n):
                  if n == 0:
                      return
                  print("in", n)
                  show(n - 1)
                  print("out", n)

              show(2)""",
              topic="rec_basics", hint="Строка после рекурсивного вызова выполнится, когда вложенный вызов закончится.",
              explanation="show(2) печатает in 2, вызывает show(1): in 1, show(0) сразу выходит, затем out 1, и в конце out 2."),
        fill("py_rec_003", "Рекурсивная сумма", "Допишите базовый случай и шаг рекурсии",
             """\
             def total(items):
                 if not items:
                     return {{0}}
                 return items[0] + total(items{{1}})

             print(total([2, 4, 6]))""", ["0", "[1:]", "1", "[0]", "None", "[:-1]"], ["0", "[1:]"],
             topic="rec_basics", hint="Сумма пустого списка — 0. Хвост списка — всё, кроме первого элемента.",
             explanation="Сумма пустого списка равна 0. Иначе первый элемент плюс сумма остальных: items[1:].",
             expect="12\n"),
        bug("py_rec_004", "Бесконечный отсчёт", """\
            def countdown(n):
                if n == 0:
                    print("Старт!")
                    return
                print(n)
                countdown(n - 2)

            countdown(3)""", {5: "    countdown(n - 1)"},
            prompt="Программа должна вывести 3, 2, 1 и «Старт!». Найдите строку с ошибкой", topic="rec_basics",
            hint="Попадёт ли n когда-нибудь ровно в 0?",
            explanation="Шаг n - 2 из 3 даёт 1, затем -1, -3… Базовый случай n == 0 никогда не срабатывает, и Python останавливает программу с RecursionError.",
            expect_error="RecursionError"),
        match("py_rec_005", "Глубина вложенности",
              ["depth(5)", "depth([])", "depth([1, [2]])", "depth([[[]]])"],
              setup="""\
                def depth(x):
                    if not isinstance(x, list):
                        return 0
                    return 1 + max((depth(i) for i in x), default=0)""",
              topic="rec_structures", hint="Не список — глубина 0. Каждый уровень скобок добавляет 1.",
              explanation="Число — 0. Пустой список — один уровень. [1, [2]] — два уровня, [[[]]] — три."),
        choice("py_rec_006", "Быстрый Фибоначчи", "Почему fib(70) с @lru_cache считается мгновенно, а без него — практически бесконечно?",
               ["lru_cache переписывает рекурсию в цикл",
                "lru_cache запоминает результаты, и каждое fib(k) вычисляется один раз",
                "lru_cache увеличивает лимит рекурсии",
                "lru_cache запускает вычисления параллельно"], 1,
               code="""\
                from functools import lru_cache

                @lru_cache(maxsize=None)
                def fib(n):
                    return n if n < 2 else fib(n - 1) + fib(n - 2)

                print(fib(70))""",
               topic="rec_memo", hint="Сколько раз без кэша вычисляется fib(2) при расчёте fib(30)?",
               explanation="Без кэша одни и те же fib(k) пересчитываются экспоненциально много раз. Кэш хранит готовые ответы, и вызовов становится порядка n.",
               role="practice", difficulty=2,
               feedback={"lru_cache переписывает рекурсию в цикл": "Рекурсия остаётся, просто повторные вызовы берут ответ из кэша.",
                         "lru_cache увеличивает лимит рекурсии": "Лимит не меняется: глубина fib(70) и так около 70.",
                         "lru_cache запускает вычисления параллельно": "Кэш не распараллеливает вычисления, он их не повторяет."}),
        order("py_rec_007", "Быстрое возведение в степень", "Соберите функцию, которая выведет 1024",
              ["def power(base, n):", "    if n == 0:", "        return 1", "    half = power(base, n // 2)",
               "    return half * half if n % 2 == 0 else half * half * base", "print(power(2, 10))"],
              topic="rec_basics", hint="Базовый случай проверяется до рекурсивного вызова.",
              explanation="base^n = (base^(n//2))², и ещё раз умножить на base, если n нечётное. Так нужно около log₂(n) вызовов вместо n.",
              role="challenge", difficulty=3),
        multi("py_rec_008", "Где закончится рекурсия", "Какие вызовы f(5) вернут результат без ошибки?",
              ["def f(n):\n    return 0 if n <= 0 else f(n - 1)",
               "def f(n):\n    return 0 if n == 0 else f(n - 2)",
               "def f(n):\n    return 0 if n == 0 else f(n + 1)",
               "def f(n):\n    return 1 if n < 2 else f(n // 2)",
               "def f(n):\n    return f(n - 1) if n > 0 else 0"], [0, 3, 4],
              check=lambda code: runs(f"{code}\nf(5)"),
              topic="rec_basics", hint="Проверьте, достигает ли шаг базового случая из n = 5.",
              explanation="n - 1 до n <= 0 и n // 2 до n < 2 обязательно доходят. n - 2 из 5 проскакивает 0, а n + 1 удаляется от него — RecursionError.",
              feedback={"def f(n):\n    return 0 if n == 0 else f(n - 2)": "5 → 3 → 1 → -1… ноль пропущен, будет RecursionError.",
                        "def f(n):\n    return 0 if n == 0 else f(n + 1)": "n растёт и никогда не станет 0."}),
        predict("py_rec_010", "Без хвостовой оптимизации", """\
                import sys

                def count(n, acc=0):
                    return acc if n == 0 else count(n - 1, acc + 1)

                print(count(100))
                try:
                    count(sys.getrecursionlimit() + 10)
                except RecursionError:
                    print("RecursionError")""",
                ["100\n0", "100", "RecursionError"], position=1, topic="rec_memo",
                hint="Python не превращает хвостовой вызов в цикл: каждый вызов занимает место в стеке.",
                explanation="count(100) работает. Глубже лимита рекурсии (sys.getrecursionlimit()) Python не пускает даже хвостовую рекурсию — RecursionError. Для таких задач нужен цикл.",
                role="challenge", difficulty=3,
                feedback={"100\n0": "Рекурсия глубже лимита не возвращает результат — она падает с RecursionError.",
                          "100": "Второй вызов превышает лимит глубины, и except печатает сообщение.",
                          "RecursionError": "count(100) намного меньше лимита и успешно возвращает 100."}),
        predict("py_rec_009", "Босс: сумма вложенного словаря", """\
                def total(data):
                    if isinstance(data, dict):
                        return sum(total(v) for v in data.values())
                    return data

                print(total({"a": 1, "b": {"c": 2, "d": {"e": 3}}, "f": 4}))""",
                ["5", "1", "TypeError"], position=1, topic="rec_structures",
                hint="Словарь — сумма его значений, число — само число. Вложенные словари обрабатываются той же функцией.",
                explanation="total проходит любую глубину вложенности: 1 + (2 + 3) + 4 = 10. Так обходят JSON и деревья настроек.",
                role="boss", difficulty=3,
                feedback={"5": "5 — это 1 + 4 без вложенных словарей, а рекурсия заходит и внутрь них.",
                          "1": "Складываются все числа на любой глубине.",
                          "TypeError": "Вложенный словарь не складывается напрямую: для него вызывается total, и он возвращает число."}),
    ],
))
