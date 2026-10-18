"""Модули 27–30: итераторы и генераторы, декораторы, контекстные
менеджеры, аннотации типов."""
from bclib import choice, fill, match, multi, order, predict, bug, typed, topic, task, run


def runs(code):
    return run(code).ok


MODULES = []

# --------------------------------------------------------------- generators
MODULES.append(dict(
    id="generators", title="Итераторы и генераторы", description="iter, next, yield, ленивые вычисления",
    icon="🌀",
    topics=[
        topic("gen_iter", "Протокол итерации",
              "Итерируемый объект отдаёт итератор через iter(); итератор выдаёт значения через next(), а в конце выбрасывает StopIteration.",
              """
              for x in items на самом деле делает так: it = iter(items), затем много раз x = next(it), пока не возникнет StopIteration — тогда цикл тихо заканчивается.

              Итерируемые объекты (список, строка, range, словарь) можно пройти сколько угодно раз: каждый for получает новый итератор. Итератор (результат iter(), map, filter, zip, генератор) — одноразовый: он помнит позицию и после конца пуст.

              Проверить: у итератора есть метод __next__, а iter(it) возвращает его самого.
              """,
              [("""\
                it = iter("xyz")
                print(next(it), next(it))
                print(list(it))
                print(list(it))""", "Итератор помнит позицию и после конца пуст."),
               ("""\
                it = iter("ab")
                print(next(it), next(it), next(it, "конец"))""", "Второй аргумент next — значение вместо StopIteration.")],
              ["Ждать, что второй проход по итератору (map, zip, генератору) снова выдаст значения.",
               "Путать range (итерируемый, многоразовый) и итератор (одноразовый)."]),
        topic("gen_yield", "Функции-генераторы и yield",
              "Функция с yield возвращает генератор: тело выполняется по шагам, на каждом yield отдаёт значение и замирает до следующего next().",
              """
              Вызов функции-генератора не выполняет её тело — он только создаёт объект-генератор. Код запускается при первом next() и идёт до ближайшего yield. Локальные переменные сохраняются между шагами.

              Когда функция доходит до конца (или до return), генератор заканчивается: next() выбрасывает StopIteration, а for завершает цикл. Если внутри генератора «вылетает» чужой StopIteration (например, от next() без значения по умолчанию), Python превращает его в RuntimeError — чтобы ошибка не выглядела как тихий конец (PEP 479).

              yield from другой_генератор отдаёт все его значения по очереди — так генераторы складывают в цепочки. Значение return вложенного генератора становится результатом выражения yield from.

              Генератор умеет и принимать данные: x = yield отдаёт значение и ждёт, что пришлёт g.send(значение). g.close() останавливает генератор (срабатывает его finally).

              Генераторное выражение (x * x for x in data) — короткая запись простого генератора.
              """,
              [("""\
                def evens(limit):
                    n = 0
                    while n <= limit:
                        yield n
                        n += 2

                print(list(evens(6)))
                g = evens(2)
                print(next(g), next(g), next(g, "стоп"))""", None),
               ("""\
                def inner():
                    yield 1
                    yield 2

                def outer():
                    yield 0
                    yield from inner()
                    yield 3

                print(list(outer()))""", None)],
              ["Писать return вместо yield внутри цикла: функция вернёт одно значение и закончится.",
               "Ждать, что вызов генераторной функции сразу выполнит её тело."]),
        topic("gen_lazy", "Ленивые вычисления и конвейеры",
              "Генераторы считают значения по требованию: можно обрабатывать бесконечные потоки и огромные файлы, не держа всё в памяти.",
              """
              Бесконечный генератор (while True: yield n) безопасен, если брать из него ограниченное число значений: itertools.islice(gen, 5), next() или цикл с break.

              Конвейер из генераторов (прочитать → отфильтровать → преобразовать) обрабатывает данные по одному элементу: каждый элемент проходит всю цепочку, прежде чем начнётся следующий.

              list(...) или sum(...) по генератору «прокручивает» его до конца — для бесконечного генератора это зависание.
              """,
              [("""\
                from itertools import islice, batched

                def squares_forever():
                    n = 0
                    while True:
                        yield n * n
                        n += 1

                print(list(islice(squares_forever(), 6)))
                print(list(batched("abcde", 2)))""", "itertools.batched (Python 3.12) режет поток на пачки.")],
              ["Вызвать list() у бесконечного генератора — программа никогда не закончится."]),
    ],
    tasks=[
        task("t_gen_chunks", "Пачки",
             "Напишите генератор chunks(items, size), который выдаёт подряд идущие куски списка длиной size (последний может быть короче). В первой строке — size, во второй — слова через пробел. Выведите каждую пачку на отдельной строке, слова через пробел.",
             solution="""\
                def chunks(items, size):
                    for start in range(0, len(items), size):
                        yield items[start:start + size]

                size = int(input())
                for part in chunks(input().split(), size):
                    print(" ".join(part))""",
             starter="""\
                def chunks(items, size):
                    return [items]

                size = int(input())
                for part in chunks(input().split(), size):
                    print(" ".join(part))""",
             tests=["2\na b c d e\n", "3\nx y z\n", "1\nодин два\n", "4\na b c d e f g h i\n"],
             hint="range(0, len(items), size) даёт начало каждой пачки; срез — саму пачку.", difficulty=2,
             requires=dict(defines=["chunks"], yields=["chunks"], calls=["chunks"])),
        task("t_gen_fib", "Бесконечный Фибоначчи",
             "Напишите бесконечный генератор fib(), выдающий числа Фибоначчи 0, 1, 1, 2, 3, 5… Прочитайте n и выведите первые n чисел через пробел.",
             solution="""\
                from itertools import islice

                def fib():
                    a, b = 0, 1
                    while True:
                        yield a
                        a, b = b, a + b

                n = int(input())
                print(" ".join(str(x) for x in islice(fib(), n)))""",
             starter="""\
                def fib():
                    yield 0

                n = int(input())
                print(0)""",
             tests=["5\n", "1\n", "2\n", "10\n", "15\n"],
             hint="Храните пару a, b и сдвигайте её: a, b = b, a + b. Первые n значений даст itertools.islice.",
             difficulty=2, requires=dict(defines=["fib"], yields=["fib"], calls=["fib"])),
    ],
    levels=[
        predict("py_gen_001", "Ручной next", """\
                it = iter([5, 6, 7])
                print(next(it))
                print(list(it), list(it))""",
                ["5\n[5, 6, 7] [5, 6, 7]", "5\n[6, 7] [6, 7]", "5\n[5, 6, 7] []"], position=1, topic="gen_iter",
                hint="Итератор помнит, сколько уже выдал, и проходится один раз.",
                explanation="next забрал 5. Первый list получает остаток [6, 7] и исчерпывает итератор, второй list получает пустой список.",
                feedback={"5\n[5, 6, 7] [5, 6, 7]": "Итератор не начинает сначала: 5 уже выдано.",
                          "5\n[6, 7] [6, 7]": "Итератор одноразовый: после первого list он пуст.",
                          "5\n[5, 6, 7] []": "next уже забрал 5 — оно не вернётся."}),
        predict("py_gen_002", "Когда выполняется тело", """\
                def gen():
                    print("старт")
                    yield 1
                    print("дальше")
                    yield 2

                g = gen()
                print("создан")
                print(next(g))
                print(next(g))""",
                ["старт\nсоздан\n1\nдальше\n2", "создан\nстарт\nдальше\n1\n2", "создан\n1\n2"], position=1,
                topic="gen_yield", hint="Вызов gen() не выполняет тело. Каждый next доходит до ближайшего yield.",
                explanation="gen() только создаёт генератор. Первый next выполняет код до первого yield (печатает «старт» и отдаёт 1), второй — до второго yield.",
                feedback={"старт\nсоздан\n1\nдальше\n2": "Вызов gen() не запускает тело — «старт» печатается только при первом next.",
                          "создан\nстарт\nдальше\n1\n2": "Генератор останавливается на каждом yield: «дальше» печатается только при втором next.",
                          "создан\n1\n2": "print внутри генератора тоже выполняются — по мере продвижения."}),
        fill("py_gen_003", "Обратный отсчёт", "Сделайте countdown генератором",
             """\
             def countdown(n):
                 while n > 0:
                     {{0}} n
                     n -= 1

             print(list(countdown(3)))""", ["yield", "return", "yield from", "pass"], ["yield"],
             topic="gen_yield", hint="Нужно отдать значение и продолжить с того же места.",
             explanation="yield отдаёт значение и замораживает функцию до следующего шага. return вернул бы одно число и закончил функцию, а yield from ждёт не число, а последовательность.",
             expect="[3, 2, 1]\n"),
        predict("py_gen_004", "Что вернул yield from", """\
                def inner():
                    yield 1
                    return "готово"

                def outer():
                    result = yield from inner()
                    print("inner вернул", result)

                print(list(outer()))""",
                ["[1, 'готово']", "[1]\ninner вернул готово", "inner вернул None\n[1]"], position=3, topic="gen_yield",
                hint="return внутри генератора не попадает в поток значений — он становится результатом yield from. И когда срабатывает print внутри outer?",
                explanation="inner отдаёт 1, а «готово» становится результатом выражения yield from. print внутри outer выполняется, пока list прокручивает генератор, — то есть раньше, чем list будет напечатан.",
                role="practice", difficulty=3,
                feedback={"[1, 'готово']": "Значение return не выдаётся как элемент: оно становится результатом yield from.",
                          "[1]\ninner вернул готово": "print внутри outer срабатывает во время работы list — раньше внешнего print.",
                          "inner вернул None\n[1]": "yield from возвращает то, что вернул inner, — «готово»."}),
        match("py_gen_005", "Генератор квадратов",
              ["list(squares(4))", "sum(squares(4))", "next(squares(4))", "max(squares(3))", "list(squares(0))"],
              setup="""\
                def squares(n):
                    for i in range(n):
                        yield i * i""",
              topic="gen_yield", hint="Каждый вызов squares создаёт новый генератор квадратов от 0 до (n-1)².",
              explanation="Каждое выражение создаёт свой генератор, поэтому они не мешают друг другу: список, сумма 14, первое значение 0, максимум 4 для n = 3, пустой список для n = 0."),
        bug("py_gen_006", "Только первая строка", """\
            def clean(text):
                for line in text.split("\\n"):
                    return line.strip()

            for line in clean(" a \\n b \\n c "):
                print(line)""", {2: "        yield line.strip()"},
            prompt="Должно вывести a, b и c на отдельных строках. Найдите строку с ошибкой", topic="gen_yield",
            hint="Что делает return внутри цикла?",
            explanation="return завершает функцию на первой же строке и возвращает строку «a». for идёт по её символам и печатает только a. yield отдаёт строки по одной.",
            difficulty=3),
        multi("py_gen_007", "Кто итератор", "Какие объекты — итераторы (одноразовые, с методом __next__)?",
              ["iter([1, 2])", "[1, 2]", "(x for x in [1, 2])", "range(3)", "map(str, [1, 2])", "\"abc\""], [0, 2, 4],
              check=lambda expr: hasattr(eval(expr), "__next__"), topic="gen_iter",
              hint="Списки, строки и range можно пройти много раз — они итерируемые, но не итераторы.",
              explanation="iter(...), генераторное выражение и map — итераторы. Список, range и строка — итерируемые объекты: каждый for получает от них новый итератор.",
              feedback={"[1, 2]": "Список итерируемый, но не итератор: next([1, 2]) — TypeError.",
                        "range(3)": "range итерируемый и многоразовый, у него нет __next__.",
                        "\"abc\"": "Строка итерируемая, но не итератор."}),
        predict("py_gen_010", "Генератор принимает данные", """\
                def average():
                    total = count = 0
                    result = None
                    while True:
                        x = yield result
                        total += x
                        count += 1
                        result = total / count

                g = average()
                next(g)
                print(g.send(10), g.send(20), g.send(0))""",
                ["10 20 0", "None 10.0 15.0", "10.0 30.0 30.0"], position=3, topic="gen_yield",
                hint="send передаёт значение в x и возвращает следующее значение yield — текущее среднее.",
                explanation="next(g) доводит генератор до первого yield. Каждый send кладёт число в x, генератор пересчитывает среднее и отдаёт его: 10 / 1, 30 / 2, 30 / 3.",
                role="challenge", difficulty=4,
                feedback={"10 20 0": "Генератор возвращает не присланное число, а текущее среднее.",
                          "None 10.0 15.0": "None отдал первый yield при next(g); send получает уже новые значения.",
                          "10.0 30.0 30.0": "Возвращается среднее, а не сумма: 30 / 2 = 15.0."}),
        predict("py_gen_011", "Чужой StopIteration", """\
                def first_two(items):
                    it = iter(items)
                    yield next(it)
                    yield next(it)

                print(list(first_two([1, 2, 3])))
                try:
                    print(list(first_two([1])))
                except RuntimeError:
                    print("RuntimeError")""",
                ["[1, 2]\n[1]", "[1, 2]\n[]", "[1, 2]\nStopIteration"], position=3, topic="gen_yield",
                hint="Что Python делает со StopIteration, вылетевшим изнутри генератора?",
                explanation="Во втором вызове next(it) внутри генератора выбрасывает StopIteration. Начиная с Python 3.7 он превращается в RuntimeError — иначе ошибка выглядела бы как тихий конец генератора.",
                role="challenge", difficulty=4,
                feedback={"[1, 2]\n[1]": "Так было до Python 3.7. Теперь StopIteration изнутри генератора превращается в RuntimeError.",
                          "[1, 2]\n[]": "Ошибка не глотается: list получает RuntimeError.",
                          "[1, 2]\nStopIteration": "StopIteration превращён в RuntimeError — его и ловит except."}),
        predict("py_gen_008", "Бесконечность под контролем", """\
                from itertools import islice

                def naturals():
                    n = 1
                    while True:
                        yield n
                        n += 1

                print(list(islice(naturals(), 4)))
                print(sum(islice((x * x for x in naturals()), 3)))""",
                ["[1, 2, 3, 4]\n9", "[0, 1, 2, 3]\n5", "Программа зависнет"], position=1, topic="gen_lazy",
                hint="islice берёт из генератора только нужное число значений.",
                explanation="islice забирает первые 4 значения, и бесконечный генератор останавливается. Во второй строке складываются 1 + 4 + 9 = 14.",
                role="practice", difficulty=3,
                feedback={"[1, 2, 3, 4]\n9": "Складываются квадраты 1, 4 и 9.",
                          "[0, 1, 2, 3]\n5": "naturals начинается с 1.",
                          "Программа зависнет": "islice берёт ровно столько значений, сколько нужно, — бесконечный цикл не прокручивается до конца."}),
        predict("py_gen_009", "Босс: ленивый конвейер", """\
                def source():
                    for x in [1, 2, 3]:
                        print("взял", x)
                        yield x

                def double(items):
                    for x in items:
                        yield x * 2

                for y in double(source()):
                    print("получил", y)""",
                ["взял 1\nвзял 2\nвзял 3\nполучил 2\nполучил 4\nполучил 6",
                 "получил 2\nвзял 1\nполучил 4\nвзял 2\nполучил 6\nвзял 3", "получил 2\nполучил 4\nполучил 6"],
                position=0, topic="gen_lazy",
                hint="Каждое значение проходит весь конвейер, прежде чем берётся следующее.",
                explanation="Генераторы не готовят всё заранее: double просит у source одно значение, удваивает и отдаёт циклу. Поэтому «взял» и «получил» чередуются.",
                role="boss", difficulty=4,
                feedback={"взял 1\nвзял 2\nвзял 3\nполучил 2\nполучил 4\nполучил 6": "Так работали бы списки. Генераторы обрабатывают по одному значению.",
                          "получил 2\nвзял 1\nполучил 4\nвзял 2\nполучил 6\nвзял 3": "Значение сначала нужно взять из source — только потом его можно удвоить и получить.",
                          "получил 2\nполучил 4\nполучил 6": "print внутри source тоже выполняется — при каждом взятии значения."}),
    ],
))

# --------------------------------------------------------------- decorators
STDLIB_DECORATORS = ["functools.wraps", "functools.singledispatch", "typing.override", "contextlib.contextmanager",
                     "functools.memoize", "functools.retry"]


def resolves(name):
    module, _, attr = name.rpartition(".")
    code = f"import {module}\nassert callable({name})" if module and module != "builtins" else \
        f"import builtins\nassert callable(getattr(builtins, '{attr}'))"
    return runs(code)


MODULES.append(dict(
    id="decorators", title="Декораторы", description="Функции, которые меняют функции", icon="🎀",
    topics=[
        topic("deco_basics", "Как работает декоратор",
              "Декоратор — функция, которая принимает функцию и возвращает новую (обычно обёртку). @deco над def f — по сути то же, что f = deco(f).",
              """
              Функции в Python — обычные значения: их можно передать в другую функцию и вернуть из неё. Декоратор пользуется этим: получает функцию, создаёт внутри обёртку wrapper, которая что-то делает до и после вызова оригинала, и возвращает wrapper.

              Чтобы обёртка подходила к любой функции, она принимает *args, **kwargs и передаёт их дальше: func(*args, **kwargs). И обязательно возвращает результат — иначе декорированная функция будет возвращать None.

              @functools.wraps(func) над wrapper копирует имя, docstring и другие атрибуты оригинала — без этого f.__name__ станет «wrapper».

              Декоратор срабатывает один раз — в момент объявления функции, а не при каждом вызове: при каждом вызове работает уже обёртка.

              Несколько декораторов применяются снизу вверх: @a @b def f — это f = a(b(f)). Декорировать можно и классы: декоратор получает класс (так устроены реестры плагинов и @dataclass).
              """,
              [("""\
                from functools import wraps

                def log(func):
                    @wraps(func)
                    def wrapper(*args, **kwargs):
                        print("вызов", func.__name__, args)
                        return func(*args, **kwargs)
                    return wrapper

                @log
                def add(a, b):
                    return a + b

                print(add(2, 3), add.__name__)""", None)],
              ["Забыть return в обёртке — функция станет возвращать None.",
               "Обёртка без *args, **kwargs ломается на функциях с аргументами.",
               "Без @wraps у всех декорированных функций одинаковое имя wrapper."]),
        topic("deco_params", "Декораторы с параметрами и состояние",
              "@repeat(3) — это вызов фабрики, которая возвращает декоратор. Обёртка может хранить состояние: счётчик вызовов, кэш.",
              """
              Декоратор с параметром — три уровня функций: repeat(n) возвращает deco(func), deco возвращает wrapper. @repeat(3) сначала вызывает repeat(3), а результат применяет к функции.

              Обёртке можно добавить атрибуты (wrapper.calls = 0) или хранить данные в замыкании (словарь-кэш). Так устроены functools.lru_cache, повтор при ошибке (retry), замер времени, проверка прав доступа в веб-фреймворках.

              Стандартные декораторы: @property, @staticmethod, @classmethod, @functools.lru_cache, @functools.cache, @dataclasses.dataclass.
              """,
              [("""\
                def repeat(n):
                    def deco(func):
                        def wrapper(*args):
                            return [func(*args) for _ in range(n)]
                        return wrapper
                    return deco

                @repeat(3)
                def hello(name):
                    return f"привет, {name}"

                print(hello("Ада"))""", None)],
              ["Писать @repeat без скобок, если декоратор ждёт параметр: repeat получит функцию вместо числа."]),
    ],
    tasks=[
        task("t_deco_memo", "Свой кэш",
             "Напишите декоратор memoize, который запоминает результаты функции по её аргументам. Примените его к рекурсивной функции fib(n) (fib(0) = 0, fib(1) = 1). Прочитайте n (до 300) и выведите fib(n). Без кэша большие n не успеют посчитаться.",
             solution="""\
                def memoize(func):
                    cache = {}
                    def wrapper(n):
                        if n not in cache:
                            cache[n] = func(n)
                        return cache[n]
                    return wrapper

                @memoize
                def fib(n):
                    return n if n < 2 else fib(n - 1) + fib(n - 2)

                print(fib(int(input())))""",
             starter="""\
                def memoize(func):
                    return func

                @memoize
                def fib(n):
                    return n if n < 2 else fib(n - 1) + fib(n - 2)

                print(fib(int(input())))""",
             tests=["10\n", "1\n", "50\n", "300\n"],
             hint="Словарь cache внутри memoize живёт в замыкании обёртки.", difficulty=3,
             requires=dict(defines=["memoize", "fib"], recursive=["fib"], decorated={"fib": "memoize"},
                           returns_function=["memoize"], no_calls=["lru_cache", "cache"])),
    ],
    levels=[
        predict("py_deco_001", "Первый декоратор", """\
                def shout(func):
                    def wrapper():
                        return func().upper() + "!"
                    return wrapper

                @shout
                def greet():
                    return "привет"

                print(greet())""",
                ["привет", "привет!", "ПРИВЕТ"], position=3, topic="deco_basics",
                hint="@shout заменяет greet на wrapper, который вызывает исходную функцию и меняет результат.",
                explanation="После @shout имя greet указывает на wrapper. Он вызывает исходную greet, переводит результат в верхний регистр и добавляет «!».",
                feedback={"привет": "Декоратор заменил функцию обёрткой — результат меняется.",
                          "привет!": "upper() переводит буквы в верхний регистр.",
                          "ПРИВЕТ": "Обёртка добавляет ещё и «!»."}),
        choice("py_deco_002", "Синтаксис @", "Запись @deco над def f(): ... — это то же самое, что:",
               ["f = deco(f)", "f = deco(f())", "f = deco", "deco(f)"], 0,
               check=lambda option: runs(
                   "def deco(fn):\n    return lambda: fn() + '!'\n"
                   "def f():\n    return 'f'\n"
                   f"{option}\n"
                   "assert f() == 'f!'"),
               topic="deco_basics", hint="Декоратор получает функцию и возвращает то, что займёт её имя.",
               explanation="@deco — сокращение для f = deco(f): функция передаётся декоратору, а имя f связывается с тем, что он вернул.",
               feedback={"f = deco(f())": "Декоратору передают саму функцию, а не результат её вызова.",
                         "f = deco": "Декоратор нужно вызвать с функцией: иначе f станет самим декоратором.",
                         "deco(f)": "Результат декоратора должен заменить f — нужно присваивание."}),
        fill("py_deco_003", "Обёртка на все случаи", "Сделайте обёртку, которая подходит для любых аргументов",
             """\
             def log(func):
                 def wrapper({{0}}):
                     print("вызов", func.__name__)
                     return func({{1}})
                 return wrapper

             @log
             def add(a, b):
                 return a + b

             print(add(2, b=3))""", ["*args, **kwargs", "*args", "**kwargs", "args, kwargs"],
             ["*args, **kwargs", "*args, **kwargs"],
             topic="deco_basics", hint="Вызов add(2, b=3) передаёт и позиционный, и именованный аргумент.",
             explanation="wrapper должен принять любые аргументы (*args, **kwargs) и передать их дальше в том же виде.",
             expect="вызов add\n5\n"),
        typed("py_deco_004", "Порядок декораторов", """\
              def square(f):
                  def w():
                      return "[" + f() + "]"
                  return w

              def round_(f):
                  def w():
                      return "(" + f() + ")"
                  return w

              @square
              @round_
              def text():
                  return "hi"

              print(text())""",
              topic="deco_basics", hint="Декораторы применяются снизу вверх: text = square(round_(text)).",
              explanation="Сначала round_ оборачивает text в круглые скобки, затем square оборачивает результат в квадратные."),
        predict("py_deco_005", "Потерянное имя", """\
                from functools import wraps

                def plain(f):
                    def wrapper(*a):
                        return f(*a)
                    return wrapper

                def nice(f):
                    @wraps(f)
                    def wrapper(*a):
                        return f(*a)
                    return wrapper

                @plain
                def area():
                    pass

                @nice
                def volume():
                    pass

                print(area.__name__, volume.__name__)""",
                ["area volume", "wrapper wrapper", "area wrapper"], position=1, topic="deco_basics",
                hint="@wraps копирует имя оригинала на обёртку.",
                explanation="После декорирования имя area указывает на wrapper, и __name__ у неё «wrapper». @wraps(f) копирует __name__ оригинала, поэтому volume сохраняет своё имя.",
                role="practice", difficulty=2,
                feedback={"area volume": "plain не использует @wraps: у обёртки своё имя.",
                          "wrapper wrapper": "@wraps(f) копирует имя volume на обёртку.",
                          "area wrapper": "Наоборот: имя теряется у функции без @wraps."}),
        bug("py_deco_006", "Пропавший результат", """\
            def count_calls(func):
                def wrapper(*args):
                    wrapper.calls += 1
                    func(*args)
                wrapper.calls = 0
                return wrapper

            @count_calls
            def square(x):
                return x * x

            print(square(4), square.calls)""", {3: "        return func(*args)"},
            prompt="Должно вывести 16 1. Найдите строку с ошибкой", topic="deco_basics",
            hint="Что возвращает wrapper?",
            explanation="Обёртка вызывает func, но не возвращает результат — значит, возвращает None. Нужно return func(*args).",
            difficulty=2),
        predict("py_deco_010", "Когда срабатывает декоратор", """\
                def announce(func):
                    print("декорирую", func.__name__)
                    return func

                @announce
                def ping():
                    print("ping")

                print("старт")
                ping()
                ping()""",
                ["старт\nдекорирую ping\nping\nping", "старт\nдекорирую ping\nping\nдекорирую ping\nping",
                 "старт\nping\nping"], position=0, topic="deco_basics",
                hint="@announce — это ping = announce(ping). Когда выполняется эта строка?",
                explanation="Декоратор вызывается один раз — при объявлении функции, ещё до print(\"старт\"). Дальше вызывается уже то, что он вернул (здесь — сама функция).",
                role="practice", difficulty=2,
                feedback={"старт\nдекорирую ping\nping\nping": "Декоратор срабатывает при объявлении функции — раньше, чем print(\"старт\").",
                          "старт\nдекорирую ping\nping\nдекорирую ping\nping": "Декоратор вызывается один раз, а не при каждом вызове функции.",
                          "старт\nping\nping": "print внутри декоратора выполняется — при объявлении ping."}),
        match("py_deco_007", "Фабрика декораторов", ["one()", "echo('a')", "len(one())", "repeat(1)(len)('ab')"],
              setup="""\
                def repeat(n):
                    def deco(f):
                        def w(*a):
                            return [f(*a) for _ in range(n)]
                        return w
                    return deco

                @repeat(3)
                def one():
                    return 1

                @repeat(2)
                def echo(x):
                    return x""",
              topic="deco_params", hint="@repeat(3) возвращает список из трёх результатов.",
              explanation="one вызывается трижды, echo — дважды. repeat(1)(len) применяет декоратор вручную: len('ab') один раз в списке."),
        multi("py_deco_008", "Стандартные декораторы", "Какие из этих декораторов есть в стандартной библиотеке Python 3.12?",
              STDLIB_DECORATORS, [0, 1, 2, 3], check=resolves, topic="deco_params",
              hint="Кэш в functools называется lru_cache (и cache), повтор при ошибке пишут сами.",
              explanation="wraps и singledispatch — из functools, override — новинка typing в 3.12, contextmanager — из contextlib. functools.memoize и functools.retry не существуют: кэш — это lru_cache, а повтор пишут сами или берут из сторонних библиотек.",
              feedback={"functools.memoize": "Такого нет: кэш в functools — это lru_cache и cache.",
                        "functools.retry": "В стандартной библиотеке повтора при ошибке нет — его пишут сами (как в боссе этого модуля)."}),
        predict("py_deco_009", "Босс: повтор при ошибке", """\
                def retry(times):
                    def deco(func):
                        def wrapper(*args, **kwargs):
                            for attempt in range(1, times + 1):
                                try:
                                    return func(*args, **kwargs)
                                except ValueError:
                                    print("попытка", attempt, "не удалась")
                            return "сдаюсь"
                        return wrapper
                    return deco

                calls = 0

                @retry(3)
                def flaky():
                    global calls
                    calls += 1
                    if calls < 3:
                        raise ValueError
                    return "успех"

                print(flaky())""",
                ["попытка 1 не удалась\nпопытка 2 не удалась\nпопытка 3 не удалась\nсдаюсь",
                 "успех", "попытка 1 не удалась\nпопытка 2 не удалась\nуспех\nсдаюсь"], position=2,
                topic="deco_params", hint="flaky падает два раза, а на третий вызов возвращает «успех».",
                explanation="Первые два вызова бросают ValueError — обёртка печатает сообщение и пробует снова. Третий вызов успешен, и return сразу возвращает «успех».",
                role="boss", difficulty=4,
                feedback={"попытка 1 не удалась\nпопытка 2 не удалась\nпопытка 3 не удалась\nсдаюсь": "На третьем вызове calls = 3, и flaky возвращает «успех».",
                          "успех": "Первые две попытки падают, и обёртка печатает об этом.",
                          "попытка 1 не удалась\nпопытка 2 не удалась\nуспех\nсдаюсь": "return внутри цикла сразу завершает обёртку — до «сдаюсь» дело не доходит."}),
    ],
))

# ------------------------------------------------------------ context managers
WITH_OBJECTS = ["open(\"f.txt\", \"w\")", "contextlib.suppress(KeyError)", "contextlib.nullcontext()",
                "io.StringIO()", "iter([1, 2])", "contextlib.contextmanager"]

MODULES.append(dict(
    id="contexts", title="Контекстные менеджеры", description="with, __enter__, __exit__, contextlib", icon="🚪",
    topics=[
        topic("ctx_protocol", "Протокол with",
              "with obj as x: вызывает obj.__enter__() (его результат попадает в x), а при выходе — obj.__exit__(тип, ошибка, трассировка), даже если внутри было исключение.",
              """
              Контекстный менеджер гарантирует «закрытие» ресурса: файла, соединения, блокировки. __exit__ вызывается при любом выходе из блока — нормальном, по return или по исключению.

              Если внутри блока было исключение, __exit__ получает его тип, объект и трассировку; если нет — три None. Если __exit__ вернёт истинное значение (обычно True), исключение подавляется и программа продолжается после with. Обычно возвращают None — тогда исключение летит дальше.

              Если ошибка возникла в самом __enter__, блок не начинается и __exit__ не вызывается.

              Несколько менеджеров: with a() as x, b() as y: — выход идёт в обратном порядке.
              """,
              [("""\
                class Tag:
                    def __init__(self, name):
                        self.name = name
                    def __enter__(self):
                        print(f"<{self.name}>")
                        return self
                    def __exit__(self, exc_type, exc, tb):
                        print(f"</{self.name}>")

                with Tag("div"), Tag("p"):
                    print("текст")""", "Закрываются в обратном порядке.")],
              ["Возвращать True из __exit__ всегда — так молча проглатываются любые ошибки.",
               "Делать уборку после with-блока вручную, а не в __exit__: при исключении она не выполнится."]),
        topic("ctx_contextlib", "contextlib",
              "@contextmanager делает менеджер из генератора: код до yield — вход, после — выход. suppress, redirect_stdout и ExitStack закрывают типовые задачи.",
              """
              @contextmanager над функцией с одним yield: всё до yield выполняется при входе (значение yield попадает в as), всё после — при выходе. Чтобы выход выполнился и при исключении, yield оборачивают в try/finally.

              suppress(KeyError) игнорирует указанные исключения внутри блока. redirect_stdout(buffer) временно направляет print в другой поток. ExitStack позволяет войти в заранее неизвестное число менеджеров и выйти из всех в обратном порядке.
              """,
              [("""\
                from contextlib import contextmanager, suppress

                @contextmanager
                def section(title):
                    print("начало", title)
                    try:
                        yield title.upper()
                    finally:
                        print("конец", title)

                with section("отчёт") as name:
                    print("внутри", name)

                with suppress(KeyError):
                    {}["нет"]
                print("ошибка подавлена")""", None)],
              ["Писать уборку после yield без try/finally: при исключении внутри with она не выполнится.",
               "Перехватить исключение вокруг yield и не пробросить его дальше (raise): @contextmanager тогда тихо проглотит ошибку.",
               "Использовать объект из @contextmanager дважды: он одноразовый, для второго with нужен новый вызов."]),
    ],
    tasks=[
        task("t_ctx_tags", "Вложенные теги",
             "Напишите контекстный менеджер tag(name) через @contextmanager: при входе он печатает <name>, при выходе — </name>. Прочитайте имена тегов через пробел, вложите их друг в друга в этом порядке и внутри выведите «текст».",
             solution="""\
                from contextlib import contextmanager, ExitStack

                @contextmanager
                def tag(name):
                    print(f"<{name}>")
                    try:
                        yield
                    finally:
                        print(f"</{name}>")

                with ExitStack() as stack:
                    for name in input().split():
                        stack.enter_context(tag(name))
                    print("текст")""",
             starter="""\
                def tag(name):
                    print(f"<{name}>")

                for name in input().split():
                    tag(name)
                print("текст")""",
             tests=["html body p\n", "b\n", "a b\n", "div section article span\n"],
             hint="ExitStack.enter_context входит в менеджер и закроет его в конце, в обратном порядке. Рекурсия тоже подойдёт.",
             difficulty=3, requires=dict(defines=["tag"], yields=["tag"], decorated={"tag": "contextmanager"}, uses=["with"])),
    ],
    levels=[
        predict("py_ctx_001", "Вход и выход", """\
                class Timer:
                    def __enter__(self):
                        print("старт")
                        return 42
                    def __exit__(self, exc_type, exc, tb):
                        print("стоп")

                with Timer() as t:
                    print("внутри", t)""",
                ["внутри 42", "старт\nвнутри Timer\nстоп", "старт\nстоп\nвнутри 42"], position=3, topic="ctx_protocol",
                hint="__enter__ — при входе в блок, и его результат попадает в as. __exit__ — при выходе.",
                explanation="with вызывает __enter__ (печатает «старт» и возвращает 42 — оно попадает в t), выполняет тело, затем __exit__.",
                feedback={"внутри 42": "with вызывает __enter__ и __exit__ — их print тоже выполняются.",
                          "старт\nвнутри Timer\nстоп": "В t попадает то, что вернул __enter__, — 42, а не сам объект.",
                          "старт\nстоп\nвнутри 42": "__exit__ вызывается после тела блока."}),
        fill("py_ctx_002", "Уборка при ошибке", "Сделайте так, чтобы «конец» печатался даже при ошибке внутри with",
             """\
             from contextlib import contextmanager

             @contextmanager
             def section(title):
                 print("начало", title)
                 {{0}}:
                     yield
                 {{1}}:
                     print("конец", title)

             try:
                 with section("A"):
                     1 / 0
             except ZeroDivisionError:
                 print("поймали")""", ["try", "finally", "except", "else", "with"], ["try", "finally"],
             topic="ctx_contextlib", hint="Тело with выполняется на месте yield. Какой блок выполняется всегда?",
             explanation="try/finally вокруг yield гарантирует «конец» при любом выходе, а исключение летит дальше и попадает в except снаружи. except проглотил бы ошибку, else не выполнился бы при ошибке.",
             role="practice", difficulty=3, expect="начало A\nконец A\nпоймали\n"),
        predict("py_ctx_003", "Выход при ошибке", """\
                class Resource:
                    def __enter__(self):
                        print("открыт")
                    def __exit__(self, exc_type, exc, tb):
                        print("закрыт", exc_type.__name__ if exc_type else None)

                try:
                    with Resource():
                        1 / 0
                except ZeroDivisionError:
                    print("поймали")""",
                ["открыт\nпоймали", "открыт\nпоймали\nзакрыт ZeroDivisionError", "открыт\nзакрыт None\nпоймали"],
                position=1, topic="ctx_protocol",
                hint="__exit__ вызывается даже при исключении — и получает его тип.",
                explanation="Деление на ноль прерывает блок, Python вызывает __exit__ с типом ошибки. __exit__ вернул None, поэтому исключение летит дальше и попадает в except.",
                feedback={"открыт\nпоймали": "__exit__ вызывается при любом выходе из with, в том числе по исключению.",
                          "открыт\nпоймали\nзакрыт ZeroDivisionError": "__exit__ срабатывает раньше, чем исключение доберётся до except снаружи.",
                          "открыт\nзакрыт None\nпоймали": "__exit__ получает тип исключения — ZeroDivisionError."}),
        typed("py_ctx_004", "Подавление ошибок", """\
              class Ignore:
                  def __enter__(self):
                      return self
                  def __exit__(self, exc_type, exc, tb):
                      return exc_type is KeyError

              with Ignore():
                  {}["x"]
              print("дальше")
              try:
                  with Ignore():
                      [][0]
              except IndexError:
                  print("индекс прошёл")""",
              topic="ctx_protocol", hint="Истинное значение из __exit__ подавляет исключение, ложное — пропускает дальше.",
              explanation="Для KeyError __exit__ возвращает True — ошибка подавлена, программа идёт дальше. Для IndexError — False, и исключение долетает до except.",
              role="practice", difficulty=3),
        match("py_ctx_005", "Детали протокола",
              ["__enter__", "__exit__", "return True из __exit__", "@contextmanager", "suppress(KeyError)"],
              rights=["Вызывается при входе в with", "Вызывается при выходе, даже при ошибке",
                      "Менеджер сам решает подавить ошибку", "Делает менеджер из генератора с yield",
                      "Подавляет KeyError и его подклассы, остальные пропускает"],
              prompt="Сопоставьте элемент и его роль", topic="ctx_contextlib",
              hint="Вход, выход, подавление, генератор, готовый инструмент.",
              explanation="__enter__ и __exit__ — две половины протокола. True из __exit__ подавляет исключение. @contextmanager и suppress — готовые инструменты из contextlib."),
        bug("py_ctx_006", "Замок не открылся", """\
            from contextlib import contextmanager

            log = []

            @contextmanager
            def lock():
                log.append("lock")
                try:
                    yield
                except ValueError:
                    log.append("unlock")

            with lock():
                log.append("работа")
            print(log)""", {9: "    finally:"},
            prompt="Замок должен открываться всегда: программа должна вывести ['lock', 'работа', 'unlock']. Найдите строку с ошибкой",
            topic="ctx_contextlib", hint="Когда выполняется блок except, а когда — finally?",
            explanation="except срабатывает только при ValueError, а здесь ошибки нет — unlock не выполнился. finally выполняется всегда: и при успехе, и при исключении.",
            difficulty=3),
        multi("py_ctx_007", "Что подходит для with", "Какие объекты можно поставить в with?", WITH_OBJECTS, [0, 1, 2, 3],
              check=lambda expr: run(f"import io, contextlib\nobj = {expr}\n"
                                     "assert hasattr(obj, '__enter__') and hasattr(obj, '__exit__')").ok,
              topic="ctx_protocol", hint="Нужны методы __enter__ и __exit__.",
              explanation="Файл, suppress, nullcontext (менеджер-пустышка) и StringIO реализуют протокол. Итератор — нет. contextmanager — это декоратор: он делает менеджер из функции, но сам менеджером не является.",
              feedback={"iter([1, 2])": "У итератора нет __enter__ и __exit__: with iter(...) — TypeError.",
                        "contextlib.contextmanager": "Это декоратор для создания менеджеров, а не сам менеджер."}),
        predict("py_ctx_008", "ExitStack", """\
                from contextlib import ExitStack

                class Step:
                    def __init__(self, n):
                        self.n = n
                    def __enter__(self):
                        print("вход", self.n)
                        return self.n
                    def __exit__(self, *exc):
                        print("выход", self.n)

                with ExitStack() as stack:
                    nums = [stack.enter_context(Step(i)) for i in range(1, 3)]
                    print("внутри", nums)""",
                ["вход 1\nвход 2\nвнутри [1, 2]\nвыход 1\nвыход 2", "вход 1\nвыход 1\nвход 2\nвыход 2\nвнутри [1, 2]",
                 "вход 1\nвход 2\nвнутри [None, None]\nвыход 2\nвыход 1"], position=1, topic="ctx_contextlib",
                hint="Выход из менеджеров — в обратном порядке, как у вложенных with.",
                explanation="enter_context входит в каждый менеджер и возвращает результат __enter__ (числа). При выходе ExitStack закрывает их в обратном порядке: сначала 2, потом 1.",
                role="challenge", difficulty=3,
                feedback={"вход 1\nвход 2\nвнутри [1, 2]\nвыход 1\nвыход 2": "ExitStack закрывает менеджеры в обратном порядке.",
                          "вход 1\nвыход 1\nвход 2\nвыход 2\nвнутри [1, 2]": "Менеджеры остаются открытыми до конца блока with.",
                          "вход 1\nвход 2\nвнутри [None, None]\nвыход 2\nвыход 1": "enter_context возвращает то, что вернул __enter__, — числа."}),
        bug("py_ctx_010", "Проглоченная ошибка", """\
            from contextlib import contextmanager

            @contextmanager
            def transaction(log):
                log.append("begin")
                try:
                    yield
                except ValueError:
                    log.append("rollback")
                    return

            log = []
            try:
                with transaction(log):
                    raise ValueError("плохие данные")
            except ValueError:
                log.append("ошибка дошла")
            print(log)""", {9: "        raise"},
            prompt="После отката ошибка должна дойти до вызывающего кода. Найдите строку с ошибкой", topic="ctx_contextlib",
            hint="Что происходит с исключением, если генератор менеджера его перехватил и просто завершился?",
            explanation="Перехватив ValueError и выйдя через return, генератор сообщает @contextmanager, что всё в порядке, — ошибка подавлена. Чтобы откатить и всё равно сообщить о проблеме, исключение пробрасывают дальше голым raise.",
            difficulty=4, role="challenge"),
        predict("py_ctx_011", "Ошибка при входе", """\
                class Conn:
                    def __enter__(self):
                        print("вход")
                        raise ConnectionError("нет сети")
                    def __exit__(self, *exc):
                        print("выход")

                try:
                    with Conn():
                        print("тело")
                except ConnectionError:
                    print("поймали")""",
                ["вход\nвыход\nпоймали", "вход\nтело\nвыход\nпоймали", "вход\nпоймали\nвыход"], position=3,
                topic="ctx_protocol", hint="Если __enter__ не завершился, начался ли блок with?",
                explanation="Ошибка возникла в __enter__: блок with не начался, поэтому и __exit__ не вызывается. Исключение сразу летит в except.",
                role="practice", difficulty=3,
                feedback={"вход\nвыход\nпоймали": "__exit__ вызывается только для блока, который начался. Здесь вход не завершился.",
                          "вход\nтело\nвыход\nпоймали": "Тело не выполняется: ошибка случилась ещё при входе.",
                          "вход\nпоймали\nвыход": "__exit__ не вызывается вовсе."}),
        predict("py_ctx_009", "Босс: перенаправления", """\
                import io
                from contextlib import redirect_stdout, suppress

                buffer = io.StringIO()
                with redirect_stdout(buffer):
                    print("скрыто")
                with suppress(ZeroDivisionError):
                    print("до")
                    1 / 0
                    print("после")
                print("в буфере:", buffer.getvalue().strip())""",
                ["скрыто\nдо\nпосле\nв буфере: скрыто", "до\nпосле\nв буфере: скрыто", "скрыто\nдо\nв буфере:"],
                position=2, topic="ctx_contextlib",
                hint="redirect_stdout уводит print в буфер, suppress прерывает блок на ошибке, но не пропускает её дальше.",
                explanation="«скрыто» попало в буфер, а не на экран. В блоке suppress ошибка прерывает выполнение после «до», «после» не печатается, программа продолжается. В конце печатается содержимое буфера.",
                role="boss", difficulty=4,
                feedback={"скрыто\nдо\nпосле\nв буфере: скрыто": "redirect_stdout отправил «скрыто» в буфер, а suppress прервал блок на делении на ноль.",
                          "до\nпосле\nв буфере: скрыто": "suppress не продолжает блок после ошибки — он выходит из него.",
                          "скрыто\nдо\nв буфере:": "Текст «скрыто» записан в буфер, а не на экран."}),
    ],
))

# ------------------------------------------------------------------- typing
ANNOTATIONS = ["list[int]", "int | None", "List[int]", "tuple[int, ...]", "\"Node\"", "int + str"]

MODULES.append(dict(
    id="typing", title="Аннотации типов", description="Подсказки типов, Protocol, дженерики", icon="🏷️",
    topics=[
        topic("typing_basics", "Аннотации и проверка типов",
              "def f(x: int) -> str — подсказка для людей и инструментов (mypy, IDE). Python при выполнении их не проверяет.",
              """
              Аннотации пишутся после двоеточия у параметров и после -> у результата: def add(a: int, b: int) -> int. У переменных: count: int = 0.

              Встроенные коллекции параметризуются прямо: list[int], dict[str, float], tuple[int, ...] (любой длины), set[str]. «Значение или None» — int | None (раньше писали Optional[int]). Функции описывают через Callable[[аргументы], результат] из collections.abc.

              Python не проверяет типы при выполнении: add("4", "2") вернёт «42». Ошибки находят статические анализаторы — mypy, pyright — до запуска программы. Аннотации доступны как f.__annotations__ или typing.get_type_hints(f).
              """,
              [("""\
                def mul(a: int, b: int) -> int:
                    return a * b

                print(mul(2, 3), mul("ab", 3))
                print(mul.__annotations__)""", "Аннотации не мешают передать строку."),
               ("""\
                def first_word(text: str) -> str | None:
                    words = text.split()
                    return words[0] if words else None

                print(first_word("Привет, мир"), first_word("   "))""", None)],
              ["Ждать, что аннотация защитит от неверного типа во время выполнения.",
               "Писать List[int] без from typing import List — в Python 3.9+ просто list[int]."]),
        topic("typing_advanced", "Protocol, дженерики, TypedDict",
              "Protocol описывает «утиный» интерфейс, def first[T](x: list[T]) -> T — обобщённую функцию, TypedDict — словарь с известными ключами.",
              """
              Protocol: класс-протокол перечисляет методы. Любой класс с такими методами подходит, даже не наследуя протокол (структурная типизация). @runtime_checkable разрешает isinstance с протоколом — но проверяет только наличие атрибутов с такими именами, а не их сигнатуры и типы.

              Дженерики (Python 3.12): def first[T](items: list[T]) -> T и class Box[T]: — параметр типа T связывает вход и выход: first([1, 2]) — это int, first(["a"]) — str. type UserId = int — псевдоним типа.

              TypedDict задаёт ключи и типы значений словаря для анализатора. Во время выполнения это обычный dict — никакой проверки нет. Literal["r", "w"] — только перечисленные значения, Callable[[int], str] — функция int → str.
              """,
              [("""\
                from typing import Protocol, runtime_checkable

                @runtime_checkable
                class Speaker(Protocol):
                    def speak(self) -> str: ...

                class Dog:
                    def speak(self) -> str:
                        return "гав"

                def talk(s: Speaker) -> str:
                    return s.speak()

                print(talk(Dog()), isinstance(Dog(), Speaker), isinstance(42, Speaker))""", "Dog не наследует Speaker, но подходит по форме."),
               ("""\
                def first[T](items: list[T]) -> T:
                    return items[0]

                print(first([3, 1]), first(["a", "b"]), first.__type_params__)""", "Синтаксис дженериков Python 3.12.")],
              ["isinstance с Protocol без @runtime_checkable — TypeError.",
               "Полагаться на isinstance с runtime_checkable-протоколом: он пропустит даже speak = 5, если имя совпадает.",
               "type UserId = int — псевдоним только для анализатора: isinstance(5, UserId) даёт TypeError.",
               "Думать, что TypedDict проверяет значения при создании: это обычный dict."]),
    ],
    tasks=[
        task("t_typing_parse", "Разбор настроек",
             "Напишите функцию parse(text: str) -> dict[str, int] с аннотациями типов: она принимает строку вида «a=1,b=20» и возвращает словарь. После запятых могут стоять пробелы — убирайте их у ключей. Прочитайте строку и выведите пары «ключ значение» по одной на строке в порядке sorted() ключей.",
             solution="""\
                def parse(text: str) -> dict[str, int]:
                    result: dict[str, int] = {}
                    for part in text.split(","):
                        key, value = part.split("=")
                        result[key.strip()] = int(value)
                    return result

                for key, value in sorted(parse(input()).items()):
                    print(key, value)""",
             starter="""\
                def parse(text):
                    return {}

                for key, value in sorted(parse(input()).items()):
                    print(key, value)""",
             tests=["a=1,b=20\n", "x=5\n", "z=1, a=2, m=3\n", "width=800,height=600\n"],
             hint="split(\",\") даёт пары, split(\"=\") — ключ и значение.", difficulty=2,
             requires=dict(defines=["parse"], annotated=["parse"])),
    ],
    levels=[
        predict("py_typing_001", "Аннотация — не проверка", """\
                def add(a: int, b: int) -> int:
                    return a + b

                print(add("4", "2"))""",
                ["6", "TypeError", "None"], position=3, topic="typing_basics",
                hint="Проверяет ли Python аннотации во время выполнения?",
                explanation="Аннотации не проверяются при выполнении. Строки складываются как обычно: «4» + «2» = «42».",
                feedback={"6": "Строки «4» и «2» склеиваются, а не складываются как числа.",
                          "TypeError": "Python не проверяет аннотации при вызове — это делают инструменты вроде mypy.",
                          "None": "Функция возвращает a + b."}),
        predict("py_typing_002", "Где хранятся аннотации", """\
                def greet(name: str, times: int = 1) -> str:
                    return name * times

                print(greet.__annotations__)""",
                ["{'name': str, 'times': int, 'return': str}", "{'name': 'str', 'times': 'int'}", "None"], position=0,
                topic="typing_basics", hint="Аннотации хранятся в словаре __annotations__. Что в нём лежит и как это печатается?",
                explanation="__annotations__ — словарь «параметр → тип», результат хранится под ключом 'return'. Значения — объекты-классы, поэтому печатаются как <class 'str'>.",
                role="practice", difficulty=2,
                feedback={"{'name': str, 'times': int, 'return': str}": "Классы в словаре печатаются как <class 'str'>.",
                          "{'name': 'str', 'times': 'int'}": "Типы хранятся как классы, а не строки, и есть ключ 'return'.",
                          "None": "Аннотации сохраняются в __annotations__."}),
        fill("py_typing_003", "Значение или None", "Опишите, что функция возвращает число или None",
             """\
             def find(names: list[str], target: str) -> int {{0}} None:
                 return names.index(target) if target in names else None

             print(find(["a", "b"], "b"), find.__annotations__["return"])""", ["|", "or", "&", "+"], ["|"],
             topic="typing_basics", hint="Объединение типов записывается тем же оператором, что объединение множеств.",
             explanation="int | None — «целое или None». int or None просто вычисляется в int, а & и + с типами дают TypeError.",
             expect="1 int | None\n"),
        match("py_typing_004", "Читаем аннотации",
              ["list[int]", "dict[str, float]", "tuple[int, ...]", "int | None", "Callable[[int], str]"],
              rights=["Список целых чисел", "Словарь: строка → число float", "Кортеж любой длины из целых",
                      "Целое число или None", "Функция: принимает int, возвращает str"],
              prompt="Сопоставьте аннотацию и её смысл", topic="typing_basics",
              hint="Многоточие в tuple означает «сколько угодно элементов».",
              explanation="list[int] и dict[str, float] описывают содержимое коллекций, tuple[int, ...] — кортеж произвольной длины, | — объединение типов, Callable[[аргументы], результат] — функцию."),
        multi("py_typing_005", "Допустимые аннотации", "Какие аннотации сработают в def f(x: <аннотация>): без импортов?",
              ANNOTATIONS, [0, 1, 3, 4],
              check=lambda ann: runs(f"def f(x: {ann}):\n    pass"), topic="typing_basics",
              hint="Аннотация вычисляется при объявлении функции. Строка в кавычках не вычисляется.",
              explanation="list[int], int | None и tuple[int, ...] — корректные выражения. \"Node\" в кавычках — отложенная ссылка (класс можно объявить позже). List без импорта — NameError, int + str — TypeError.",
              feedback={"List[int]": "List нужно импортировать из typing — а лучше писать list[int].",
                        "int + str": "Типы не складываются: это TypeError при объявлении функции."}),
        predict("py_typing_006", "Протокол", """\
                from typing import Protocol, runtime_checkable

                @runtime_checkable
                class Closer(Protocol):
                    def close(self) -> None: ...

                class Socket:
                    def close(self) -> None:
                        print("закрыт")

                class Fake:
                    close = 5

                print(isinstance(Socket(), Closer), isinstance(Fake(), Closer), isinstance("hi", Closer))""",
                ["True False False", "False False False", "TypeError"], position=1, topic="typing_advanced",
                hint="runtime_checkable-протокол при isinstance проверяет только наличие атрибута с нужным именем.",
                explanation="Socket не наследует Closer, но у него есть close — подходит. У Fake тоже есть атрибут close (пусть и число), и isinstance его пропускает: проверяются только имена. У строки close нет.",
                role="practice", difficulty=3,
                feedback={"True False False": "isinstance с протоколом проверяет лишь, что атрибут close есть, — у Fake он есть.",
                          "False False False": "Наследовать протокол не нужно: у Socket есть close.",
                          "TypeError": "@runtime_checkable разрешает isinstance с протоколом."}),
        typed("py_typing_007", "Обобщённый класс", """\
              class Box[T]:
                  def __init__(self, item: T):
                      self.item = item

              print(Box(5).item, Box[str]("x").item)
              print(Box.__type_params__)""",
              topic="typing_advanced", hint="[T] после имени класса объявляет параметр типа. Box[str] при выполнении ничего не проверяет.",
              explanation="Box хранит значение любого типа. Box[str](...) работает как обычный вызов. __type_params__ — кортеж из параметра T, он печатается как (T,).",
              role="practice", difficulty=3),
        bug("py_typing_008", "Забытый None", """\
            def greet(name: str | None) -> str:
                return "Привет, " + name.title()

            print(greet("ада"))
            print(greet(None))""", {1: "    return \"Привет, \" + (name or \"гость\").title()"},
            alt_fixes={0: "def greet(name: str = \"гость\") -> str:"},
            prompt="Если имени нет (None), функция должна приветствовать гостя. Найдите строку с ошибкой", topic="typing_basics",
            hint="Аннотация str | None говорит: name может быть None. Что тогда сделает name.title()?",
            explanation="У None нет метода title — AttributeError. Анализатор типов предупредил бы об этом заранее. Нужно обработать None, например name or \"гость\".",
            expect_error="AttributeError", difficulty=2),
        predict("py_typing_010", "Final и Literal", """\
                from typing import Final, Literal

                LIMIT: Final = 3
                LIMIT = 4

                def open_mode(m: Literal["r", "w"]) -> str:
                    return m

                print(LIMIT, open_mode("x"))""",
                ["3 x", "TypeError", "4 r"], position=0, topic="typing_advanced",
                hint="Final и Literal — подсказки для анализатора. Что из этого проверяется при выполнении?",
                explanation="Python не мешает переприсвоить Final и передать в Literal другое значение: программа печатает 4 x. Ошибки покажет только статический анализатор (mypy, pyright) — до запуска.",
                role="practice", difficulty=3,
                feedback={"3 x": "Final не запрещает присваивание во время выполнения — LIMIT стал 4.",
                          "TypeError": "Аннотации не проверяются при выполнении.",
                          "4 r": "Literal ничего не подставляет: функция возвращает переданное «x»."}),
        predict("py_typing_009", "Босс: TypedDict и псевдонимы", """\
                from typing import TypedDict, get_type_hints

                type UserId = int

                class User(TypedDict):
                    id: UserId
                    name: str

                u: User = {"id": "7", "name": "Ада"}
                print(type(u).__name__, repr(u["id"]), list(get_type_hints(User)))""",
                ["User '7' ['id', 'name']", "dict 7 ['id', 'name']", "TypeError"], position=1, topic="typing_advanced",
                hint="TypedDict существует только для анализатора: во время выполнения — обычный словарь без проверок.",
                explanation="u — обычный dict, и строка «7» вместо числа проходит без ошибки. get_type_hints(User) возвращает объявленные ключи: id и name.",
                role="boss", difficulty=4,
                feedback={"User '7' ['id', 'name']": "Объект, созданный литералом {...}, — обычный dict.",
                          "dict 7 ['id', 'name']": "Значение осталось строкой: TypedDict ничего не преобразует — repr показывает кавычки.",
                          "TypeError": "Во время выполнения TypedDict ничего не проверяет."}),
    ],
))
