"""Модули 27–30: итераторы и генераторы, декораторы, контекстные
менеджеры, аннотации типов."""
from bclib import choice, fill, match, multi, order, predict, bug, typed, topic, task, run, pitfall


def runs(code):
    return run(code).ok


MODULES = []

# --------------------------------------------------------------- generators
MODULES.append(dict(
    id="generators", title="Итераторы и генераторы", description="iter, next, yield, ленивые вычисления",
    icon="🌀",
    topics=[
        topic("gen_iter", "Протокол итерации",
              "Цикл `for` получает у объекта итератор через `iter()` и берёт из него значения через `next()`, пока они не кончатся.",
              """
              `for` перебирает списки, строки, словари, файлы и `range` одинаково. За этим стоит один общий механизм — протокол итерации. Зная его, можно сделать перебираемым и свой объект.

              ## Итерируемый объект и итератор

              - Итерируемый объект (список, строка, `range`, словарь) отдаёт каждому `for` новый итератор.
              - Итератор выдаёт значения по одному и помнит позицию. Он одноразовый: после конца он пуст.

              Итераторы возвращают `iter()`, `map`, `filter`, `zip`, `enumerate` и [[gen_yield|генераторы]].

              ## Что делает for

              Цикл `for x in items` выполняет шаги:

              1. `it = iter(items)` — получает итератор;
              2. `x = next(it)` — берёт следующее значение и выполняет тело;
              3. повторяет шаг 2, пока `next` не выбросит `StopIteration`;
              4. перехватывает `StopIteration` и тихо завершает цикл.

              `next(it, значение)` в конце не выбрасывает исключение, а возвращает значение по умолчанию.

              ## Свой итератор

              Итератор — объект с двумя методами:

              - `__iter__` возвращает сам объект;
              - `__next__` возвращает следующее значение или выбрасывает `StopIteration`.

              Короче то же самое записывают функцией с `yield`.
              """,
              [("""\
                it = iter(["a", "b"])
                print(next(it))
                print(next(it))
                print(next(it, "конец"))""",
                "Значения кончились — next вернул значение по умолчанию"),
               ("""\
                sizes = map(abs, [-1, -2])
                print(list(sizes))
                print(list(sizes))

                nums = [1, 2]
                print(sum(nums), sum(nums))""",
                "map — одноразовый итератор, список — многоразовый"),
               ("""\
                items = ["x", "y"]
                it = iter(items)
                while True:
                    try:
                        x = next(it)
                    except StopIteration:
                        break
                    print(x)""",
                "Так for работает изнутри: next до StopIteration"),
               ("""\
                class Countdown:
                    def __init__(self, n):
                        self.n = n
                    def __iter__(self):
                        return self
                    def __next__(self):
                        if self.n == 0:
                            raise StopIteration
                        self.n -= 1
                        return self.n + 1

                for x in Countdown(3):
                    print(x)""",
                "Свой итератор: __next__ выдал 3, 2, 1 и закончил")],
              [pitfall("Итератор одноразовый: второй проход по `map`, `zip` или генератору пуст.",
                       bad='''
                           evens = filter(is_even, nums)
                           print(list(evens))
                           print(list(evens))''',
                       good='''
                           evens = list(filter(is_even, nums))
                           print(evens)
                           print(evens)'''),
               pitfall("Список — не итератор: {`next([1, 2])`} даёт `TypeError: 'list' object is not an iterator`.",
                       bad="first = next(names)", good="first = next(iter(names))"),
               pitfall("`__next__` без `StopIteration`: цикл `for` по такому объекту никогда не закончится.",
                       bad='''
                           def __next__(self):
                               self.n -= 1
                               return self.n''',
                       good='''
                           def __next__(self):
                               if self.n == 0:
                                   raise StopIteration
                               self.n -= 1
                               return self.n''')]),
        topic("gen_yield", "Функции-генераторы и yield",
              "Функция с `yield` возвращает генератор: она отдаёт значения по одному и замирает между ними.",
              """
              Свой итератор-класс требует `__iter__`, `__next__` и ручного хранения позиции. Функция-генератор делает то же самое короче: значения отдаются по одному через `yield`, а место остановки Python запоминает сам.

              ## Как записать

              ```syntax
              def имя(параметры):
                  действия
                  yield значение
              ```

              Функция, в теле которой есть `yield`, — функция-генератор. Её вызов возвращает объект-генератор, это [[gen_iter|итератор]].

              ## Как выполняется тело

              1. Вызов `g = имя()` не выполняет ни строчки тела.
              2. `next(g)` выполняет тело до ближайшего `yield` и отдаёт его значение.
              3. Функция замирает, локальные переменные сохраняются.
              4. Следующий `next(g)` продолжает с места остановки.
              5. Конец функции или `return` завершает генератор: `next` выбрасывает `StopIteration`, `for` заканчивается.

              Значение после `return` в генераторе не попадает в поток значений.

              ## yield from

              `yield from другой` по очереди отдаёт все значения другого генератора или коллекции. Так генератор собирают из частей. Значение `return` вложенного генератора становится результатом выражения `yield from`.

              ## Обмен с генератором

              - `x = yield v` отдаёт `v` и ждёт значение от `g.send(значение)`. Первый шаг всегда `next(g)`.
              - `g.close()` останавливает генератор; его блок `finally` выполняется.
              - Если внутри генератора вылетел чужой `StopIteration`, Python заменит его на `RuntimeError`.

              Простой генератор записывают и одной строкой — [[comp_dict_set|генераторным выражением]] `(x * x for x in data)`.
              """,
              [("""\
                def ticks(n):
                    for i in range(1, n + 1):
                        yield f"тик {i}"

                for t in ticks(3):
                    print(t)""",
                "for получает значения по одному, пока функция не закончится"),
               ("""\
                def running_total(nums):
                    total = 0
                    for n in nums:
                        total += n
                        yield total

                sums = running_total([5, 3, 2])
                print(list(sums))""",
                "Переменная total сохранилась между шагами"),
               ("""\
                def letters():
                    yield "a"
                    yield "b"

                def chars():
                    yield from letters()
                    yield from "12"

                print(list(chars()))""",
                "yield from отдал значения генератора, затем строки"),
               ("""\
                def echo():
                    reply = None
                    while True:
                        msg = yield reply
                        reply = msg.upper()

                g = echo()
                next(g)
                print(g.send("привет"))
                print(g.send("пока"))""",
                "next запустил генератор, send передаёт значение внутрь")],
              [pitfall("`return` в цикле завершает функцию на первом значении; для потока значений нужен `yield`.",
                       bad='''
                           for n in nums:
                               return n * 2''',
                       good='''
                           for n in nums:
                               yield n * 2'''),
               pitfall("Вызов генераторной функции ничего не выполняет: результат перебирают через `for` или `list`.",
                       bad="ticks(3)", good="print(list(ticks(3)))"),
               pitfall("`send` до первого `next`: `TypeError: can't send non-None value to a just-started generator`.",
                       bad='''
                           g = echo()
                           g.send("привет")''',
                       good='''
                           g = echo()
                           next(g)
                           g.send("привет")''')]),
        topic("gen_lazy", "Ленивые вычисления и конвейеры",
              "Ленивые вычисления считают каждое значение только тогда, когда его просят, и не держат весь поток в памяти.",
              """
              Список хранит все значения сразу. Если строк в файле миллион, а нужна первая подходящая, считать и хранить остальные незачем. Генераторы считают значения по требованию.

              ## Ленивое и жадное

              - {`[x * 2 for x in data]`} — список: всё считается сразу и лежит в памяти.
              - `(x * 2 for x in data)` — генераторное выражение: значения считаются по одному.

              Значения по запросу выдают [[gen_yield|генераторы]], `map`, `filter`, `zip` и открытый файл. `range` тоже не хранит числа, а вычисляет их.

              Если перебор остановился раньше — `any` нашёл истину, сработал `break`, — остальные значения не считаются вовсе. Сколько памяти экономит генератор — в теме [[perf_tricks|Быстрые идиомы и память]].

              ## Конвейер

              Генераторы соединяют в цепочку: каждый берёт значения у предыдущего.

              ```syntax
              чистые = (s.strip() for s in источник)
              непустые = (s for s in чистые if s)
              числа = (int(s) for s in непустые)
              ```

              Пока результат не перебирают, ничего не считается. При переборе каждое значение проходит всю цепочку, и только потом берётся следующее. В памяти одновременно одно значение.

              ## Бесконечный поток

              Генератор с `while True` сам не заканчивается. Из него берут столько, сколько нужно:

              - `islice(поток, n)` из [[std_itertools|itertools]] — первые `n` значений;
              - `next(поток)` — одно значение;
              - цикл `for` с [[loopx_break|break]].

              `list`, `sum` и `sorted` перебирают поток до конца: на бесконечном генераторе программа зависнет.

              `batched(поток, n)` режет поток на пачки по `n` (с Python 3.12).
              """,
              [("""\
                def is_big(price):
                    print("проверяю", price)
                    return price > 20

                prices = [5, 30, 7, 50]
                print(any(is_big(p) for p in prices))
                print("---")
                print(any([is_big(p) for p in prices]))""",
                "Генератор остановился на 30, список проверил все цены заранее"),
               ("""\
                lines = ["10", " ", "7 ", "x", "3"]
                clean = (s.strip() for s in lines)
                digits = (s for s in clean
                          if s.isdigit())
                nums = (int(s) for s in digits)
                print(sum(nums))""",
                "Конвейер: очистка, фильтр и перевод в числа за один проход"),
               ("""\
                from itertools import count, islice

                ids = (f"user{n}" for n in count(1))
                print(list(islice(ids, 3)))
                print(next(ids))""",
                "Бесконечный поток: islice взял три, next — следующий"),
               ("""\
                from itertools import batched

                for pack in batched(range(1, 8), 3):
                    print(pack)""",
                "batched режет поток на пачки по 3, последняя короче")],
              [pitfall("`list()` перебирает поток до конца: на бесконечном генераторе программа зависнет.",
                       bad="ids = list(count(1))", good="ids = list(islice(count(1), 5))"),
               pitfall("Генератор одноразовый: после `sum` он пуст, и `max` даёт `ValueError`.",
                       bad='''
                           nums = (int(s) for s in data)
                           print(sum(nums), max(nums))''',
                       good='''
                           nums = [int(s) for s in data]
                           print(sum(nums), max(nums))'''),
               pitfall("У генератора нет длины: `TypeError: object of type 'generator' has no len()`.",
                       bad="n = len(nums)", good="n = sum(1 for _ in nums)")]),
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
              "Декоратор — функция, которая принимает функцию и возвращает её дополненную версию; `@имя` над `def` применяет его.",
              """
              Одно и то же действие часто нужно добавить ко многим функциям: записать вызов в лог, замерить время, проверить права. Декоратор описывает добавку один раз и подключает её одной строкой.

              ## На чём это держится

              Функция в Python — такое же значение, как число или строка. Её можно передать в другую функцию, создать внутри функции и вернуть как результат.

              Вложенная функция помнит переменные внешней — это [[scope_closure|замыкание]]. Декоратор использует всё это сразу.

              ## Как записать

              ```syntax
              def декоратор(func):
                  def wrapper(*args, **kwargs):
                      действия_до
                      result = func(*args, **kwargs)
                      действия_после
                      return result
                  return wrapper
              ```

              - `func` — исходная функция, `wrapper` — обёртка: она вызывает `func` и добавляет действия до или после.
              - [[args_star|`*args, **kwargs`]] передают в `func` любые аргументы без изменений, поэтому обёртка подходит к любой функции.
              - `return result` обязателен: без него функция будет возвращать `None`.

              ## Что значит @

              Запись `@декоратор` над `def f` — то же, что `f = декоратор(f)` сразу после объявления. Имя `f` теперь указывает на обёртку, а исходная функция живёт внутри неё.

              **Декоратор вызывается один раз — когда Python выполняет `def`.** При каждом вызове `f()` работает уже обёртка.

              ## Имя исходной функции

              У обёртки своё имя — `wrapper`, поэтому `f.__name__` и `help(f)` показывают не ту функцию. `@functools.wraps(func)` над обёрткой копирует имя и описание оригинала. Его ставят всегда.

              ## Несколько декораторов

              Декораторы применяются снизу вверх: `@a` над `@b` над `def f` означает `f = a(b(f))`. При вызове первой срабатывает внешняя обёртка `a`.

              Декоратор с настройкой, например `@repeat(3)`, — это три уровня функций: см. [[deco_params|Параметры и состояние декоратора]].

              Готовые декораторы уже встречались в курсе: [[prop_property|`@property`]] и [[dc_basics|`@dataclass`]].
              """,
              [("""\
                def loud(func):
                    def wrapper():
                        print("до")
                        func()
                        print("после")
                    return wrapper

                def hello():
                    print("привет")

                hello = loud(hello)
                hello()""",
                "Декоратор без @: функция подменена обёрткой"),
               ("""\
                from functools import wraps

                def trace(func):
                    @wraps(func)
                    def wrapper(*args, **kwargs):
                        print("аргументы:", args)
                        result = func(*args, **kwargs)
                        print("результат:", result)
                        return result
                    return wrapper

                @trace
                def area(w, h):
                    return w * h

                print(area(2, 3) * 10)
                print(area.__name__)""",
                "Обёртка передала аргументы и вернула результат; имя сохранил wraps"),
               ("""\
                def register(func):
                    print("регистрирую", func.__name__)
                    return func

                @register
                def start():
                    print("старт")

                print("до вызова")
                start()
                start()""",
                "Декоратор сработал один раз — при def, ещё до вызовов"),
               ("""\
                def bold(func):
                    def wrapper():
                        return "<b>" + func() + "</b>"
                    return wrapper

                def italic(func):
                    def wrapper():
                        return "<i>" + func() + "</i>"
                    return wrapper

                @bold
                @italic
                def word():
                    return "py"

                print(word())""",
                "Снизу вверх: italic обернул первым, bold — снаружи")],
              [pitfall("Обёртка не вернула результат, и функция стала возвращать `None`.",
                       bad='''
                           def wrapper(*args, **kwargs):
                               func(*args, **kwargs)''',
                       good='''
                           def wrapper(*args, **kwargs):
                               return func(*args, **kwargs)'''),
               pitfall("Декоратор должен вернуть функцию, а не результат её вызова.",
                       bad="return wrapper()", good="return wrapper"),
               pitfall("Обёртка без параметров ломается на аргументах: `TypeError: wrapper() takes 0 positional arguments`.",
                       bad='''
                           def wrapper():
                               return func()''',
                       good='''
                           def wrapper(*args, **kwargs):
                               return func(*args, **kwargs)'''),
               pitfall("`@log()` вызывает `log` без функции: `TypeError: log() missing 1 required positional argument`.",
                       bad='''
                           @log()
                           def area(w, h): ...''',
                       good='''
                           @log
                           def area(w, h): ...''')]),
        topic("deco_params", "Параметры и состояние декоратора",
              "Декоратор с параметром — функция, которая по настройке создаёт декоратор; обёртка может помнить данные между вызовами.",
              """
              Декоратору часто нужна настройка: сколько раз повторить, какой уровень лога писать, какую роль проверять. Ещё ему бывает нужна память между вызовами: счётчик, кэш, время последнего запуска.

              ## Как записать

              ```syntax
              def фабрика(настройка):
                  def декоратор(func):
                      @wraps(func)
                      def wrapper(*args, **kwargs):
                          действия_с_настройкой
                          return func(*args, **kwargs)
                      return wrapper
                  return декоратор
              ```

              ## Три уровня функций

              Запись `@фабрика(3)` над `def f` выполняется в два шага:

              1. `фабрика(3)` вызывается и возвращает декоратор; настройка запоминается в [[scope_closure|замыкании]].
              2. Этот декоратор применяется к функции, как обычный [[deco_basics|`@декоратор`]].

              Итого `f = фабрика(3)(f)`. Скобки здесь обязательны: без них фабрика получит функцию вместо настройки.

              ## Состояние между вызовами

              Обёртка живёт столько же, сколько функция, поэтому может хранить данные:

              - атрибут обёртки: `wrapper.calls = 0`, затем `wrapper.calls += 1`;
              - словарь в замыкании декоратора — например, кэш результатов.

              Чтобы изменить число из замыкания, нужен [[scope_global|`nonlocal`]]. Атрибут обёртки и содержимое словаря меняются без него.

              ## Где это встречается

              - [[rec_memo|`lru_cache(maxsize=128)`]] — кэш с настройкой размера;
              - проверка прав в веб-фреймворках: `@require("admin")`;
              - повтор при ошибке, замер времени, ограничение частоты вызовов.
              """,
              [("""\
                from functools import wraps

                def tag(name):
                    def deco(func):
                        @wraps(func)
                        def wrapper(*args):
                            text = func(*args)
                            return f"<{name}>{text}</{name}>"
                        return wrapper
                    return deco

                @tag("b")
                def hello(who):
                    return "привет, " + who

                print(hello("Ада"))
                print(hello.__name__)""",
                "tag(\"b\") вернул декоратор, а настройка name запомнилась"),
               ("""\
                def limit(n):
                    def deco(func):
                        def wrapper():
                            if wrapper.left == 0:
                                return "лимит"
                            wrapper.left -= 1
                            return func()
                        wrapper.left = n
                        return wrapper
                    return deco

                hint = limit(2)(lambda: "совет")
                for _ in range(3):
                    print(hint())""",
                "limit(2) без @: настройка в замыкании, остаток — в атрибуте"),
               ("""\
                def tag(name):
                    def deco(func):
                        return func
                    return deco

                @tag
                def hello():
                    return "привет"

                print(hello.__name__)""",
                "Без скобок tag получил функцию, и hello стал декоратором deco")],
              [pitfall("Без скобок фабрика получает функцию вместо настройки, и вызов ломается.",
                       bad='''
                           @tag
                           def hello(who): ...''',
                       good='''
                           @tag("b")
                           def hello(who): ...'''),
               pitfall("Число из замыкания меняют через `nonlocal`, иначе `UnboundLocalError`.",
                       bad='''
                           def wrapper():
                               calls += 1''',
                       good='''
                           def wrapper():
                               nonlocal calls
                               calls += 1'''),
               pitfall("Фабрика без `return deco`: `TypeError: 'NoneType' object is not callable`.",
                       bad='''
                           def tag(name):
                               def deco(func):
                                   return func''',
                       good='''
                           def tag(name):
                               def deco(func):
                                   return func
                               return deco''')]),
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
              "Блок `with` вызывает `__enter__` при входе и `__exit__` при любом выходе, даже если внутри случилась ошибка.",
              """
              Файл нужно закрыть, блокировку — снять, соединение — разорвать. Причём даже если в середине работы случилась ошибка. Блок `with` гарантирует такую уборку, а объект, который её выполняет, называют контекстным менеджером.

              ## Как записать

              ```syntax
              with менеджер as имя:
                  действия
              ```

              Часть `as имя` необязательна. Несколько менеджеров перечисляют через запятую: `with a() as x, b() as y:`. Самый частый пример — [[files_open|open]].

              ## Что делает with

              1. Вызывает `__enter__()` у менеджера; результат попадает в `имя`.
              2. Выполняет тело блока.
              3. При любом выходе — обычном, по `return` или по исключению — вызывает `__exit__`.

              Если ошибка случилась в самом `__enter__`, блок не начинается и `__exit__` не вызывается. Несколько менеджеров закрываются в обратном порядке.

              ## Свой менеджер

              ```syntax
              class Менеджер:
                  def __enter__(self):
                      return значение_для_as
                  def __exit__(self, exc_type, exc, tb):
                      уборка
              ```

              `__exit__` получает тип исключения, само исключение и трассировку. Если блок закончился без ошибки, все три равны `None`.

              ## Подавление ошибки

              Если `__exit__` вернул истинное значение, исключение гасится, и программа идёт дальше после `with`. Обычно `__exit__` ничего не возвращает — тогда ошибка летит дальше, к [[exc_try|try / except]]. Гасить стоит только ожидаемые ошибки, проверив `exc_type`.

              Менеджер без класса делают через [[ctx_contextlib|contextlib]].
              """,
              [("""\
                class Door:
                    def __enter__(self):
                        print("открыл")
                        return "ключ"
                    def __exit__(self, exc_type, exc, tb):
                        print("закрыл")

                with Door() as k:
                    print("внутри:", k)
                print("дальше")""",
                "В as попал результат __enter__, __exit__ сработал после тела"),
               ("""\
                class Tag:
                    def __init__(self, name):
                        self.name = name
                    def __enter__(self):
                        print(f"<{self.name}>")
                    def __exit__(self, *exc):
                        print(f"</{self.name}>")

                with Tag("ul"), Tag("li"):
                    print("пункт")""",
                "Два менеджера: закрываются в обратном порядке"),
               ("""\
                class Door:
                    def __enter__(self):
                        return self
                    def __exit__(self, exc_type, exc, tb):
                        print("закрыл:", exc_type.__name__)

                try:
                    with Door():
                        int("x")
                except ValueError:
                    print("ошибка дошла до except")""",
                "__exit__ сработал до except и получил тип ошибки"),
               ("""\
                class Skip:
                    def __enter__(self):
                        return self
                    def __exit__(self, exc_type, exc, tb):
                        if exc_type is ZeroDivisionError:
                            print("пропуск:", exc)
                            return True

                with Skip():
                    print(1 / 0)
                print("работаем дальше")""",
                "__exit__ вернул True — ошибка погашена")],
              [pitfall("`__exit__` всегда возвращает `True`: любые ошибки в блоке молча пропадут.",
                       bad="return True", good="return exc_type is KeyError"),
               pitfall("Если `read` упадёт, `close` не выполнится; `with` закроет файл при любом выходе.",
                       bad='''
                           f = open(path)
                           data = f.read()
                           f.close()''',
                       good='''
                           with open(path) as f:
                               data = f.read()'''),
               pitfall("`__enter__` без `return`: в `as` попадёт `None`, и обращение к атрибуту даст `AttributeError`.",
                       bad='''
                           def __enter__(self):
                               self.start = 0''',
                       good='''
                           def __enter__(self):
                               self.start = 0
                               return self'''),
               pitfall("`__exit__` принимает три аргумента: `TypeError: … takes 1 positional argument but 4 were given`.",
                       bad='''
                           def __exit__(self):
                               self.close()''',
                       good='''
                           def __exit__(self, exc_type, exc, tb):
                               self.close()''')]),
        topic("ctx_contextlib", "contextlib",
              "Модуль `contextlib` делает контекстный менеджер из функции с `yield` и даёт готовые менеджеры для частых задач.",
              """
              Писать класс с `__enter__` и `__exit__` ради пары строк до и после блока — долго. Модуль `contextlib` даёт короткий способ сделать свой менеджер и несколько готовых.

              ## Как записать

              ```syntax
              from contextlib import contextmanager

              @contextmanager
              def имя(параметры):
                  подготовка
                  try:
                      yield значение_для_as
                  finally:
                      уборка
              ```

              ## Как работает @contextmanager

              Функция с одним [[gen_yield|`yield`]] превращается в менеджер:

              1. код до `yield` выполняется при входе в `with`;
              2. значение `yield` попадает в `as`;
              3. на месте `yield` выполняется тело блока;
              4. код после `yield` выполняется при выходе.

              Ошибка из тела блока появляется в функции на строке `yield`. Поэтому уборку ставят в `finally`: иначе при исключении она не выполнится.

              ## Готовые менеджеры

              - `suppress(KeyError)` — гасит указанные исключения внутри блока;
              - `redirect_stdout(buf)` — временно направляет `print` в другой поток;
              - `ExitStack()` — вход в заранее неизвестное число менеджеров;
              - `nullcontext()` — пустой менеджер, когда `with` нужен только для формы.

              ## ExitStack

              `stack.enter_context(m)` входит в менеджер и возвращает результат его `__enter__`. При выходе из `with ExitStack() as stack` все менеджеры закрываются в обратном порядке. Так открывают, например, список файлов, длина которого известна только при запуске.
              """,
              [("""\
                from contextlib import contextmanager

                @contextmanager
                def box(title):
                    print("+--", title)
                    try:
                        yield len(title)
                    finally:
                        print("+-- конец")

                with box("итоги") as n:
                    print("длина заголовка", n)""",
                "До yield — вход, значение yield — в as, после yield — выход"),
               ("""\
                from contextlib import contextmanager

                @contextmanager
                def guard():
                    try:
                        yield
                    finally:
                        print("уборка")

                try:
                    with guard():
                        int("x")
                except ValueError:
                    print("ошибка дошла")""",
                "finally сработал, а ошибка ушла дальше, к except"),
               ("""\
                from contextlib import suppress

                stock = {"чай": 3}
                with suppress(KeyError):
                    stock["кофе"] -= 1
                    print("не выполнится")
                print(stock)""",
                "KeyError погашен, остаток блока пропущен")],
              [pitfall("Без `try/finally` код после `yield` не выполнится, если в блоке случилась ошибка.",
                       bad='''
                           print("вход")
                           yield
                           print("выход")''',
                       good='''
                           print("вход")
                           try:
                               yield
                           finally:
                               print("выход")'''),
               pitfall("`except` вокруг `yield` без `raise` гасит ошибку: вызывающий код о ней не узнает.",
                       bad='''
                           try:
                               yield
                           except ValueError:
                               rollback()''',
                       good='''
                           try:
                               yield
                           except ValueError:
                               rollback()
                               raise'''),
               pitfall("Два `yield` в одной функции: `RuntimeError: generator didn't stop`.",
                       bad='''
                           yield 1
                           yield 2''',
                       good="yield 1")]),
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
              "Аннотации типов записывают, что функция принимает и возвращает; Python их не проверяет, это делают анализаторы.",
              """
              В большой программе трудно помнить, что функция принимает и что возвращает. Аннотации типов записывают это прямо в коде. Их читают люди, редактор кода и анализаторы, которые находят ошибки до запуска.

              ## Как записать

              ```syntax
              def функция(имя: тип) -> тип_результата:
                  тело

              переменная: тип = значение
              ```

              Аннотация параметра стоит после двоеточия, аннотация результата — после `->`. Значение по умолчанию пишут после аннотации: `times: int = 1`.

              ## Типы коллекций

              | Запись | Значит |
              |---|---|
              | {`list[int]`} | список целых |
              | {`dict[str, float]`} | словарь: строка и число |
              | {`tuple[int, str]`} | пара: число и строка |
              | {`tuple[int, ...]`} | кортеж любой длины |
              | {`Callable[[int], str]`} | функция из {`int`} в {`str`} |

              «Значение или `None`» записывают как `int | None`. `Callable` импортируют из `collections.abc`. Старые записи {`List[int]`} и {`Optional[int]`} из модуля `typing` встречаются в чужом коде; сейчас пишут {`list[int]`} и `int | None`.

              ## Python не проверяет типы

              Аннотации не влияют на выполнение: функция с `x: int` спокойно примет строку. Ошибки ищут анализаторы — `mypy`, `pyright` или встроенный в редактор. Они читают код, не запуская его.

              Аннотации хранятся в словаре `f.__annotations__`.

              ## Что аннотировать

              Сначала — параметры и результат функций. Переменные — когда тип не очевиден, например у пустого списка: {`names: list[str] = []`}.

              Для сложных случаев есть [[typing_generics|дженерики]] и [[typing_advanced|Protocol]].
              """,
              [("""\
                def double(x: int) -> int:
                    return x * 2

                print(double(21))
                print(double("ab"))""",
                "Аннотация не помешала передать строку"),
               ("""\
                def age(name: str) -> int | None:
                    ages = {"Ада": 36}
                    return ages.get(name)

                print(age("Ада"))
                print(age("Боб"))""",
                "Результат — число или None, аннотация это описывает"),
               ("""\
                from collections.abc import Callable

                Op = Callable[[int], int]

                def twice(f: Op, x: int) -> int:
                    return f(f(x))

                print(twice(lambda n: n + 3, 1))""",
                "Callable описывает функцию: принимает int, возвращает int")],
              [pitfall("Аннотация не остановит `pay(\"5\")`: вернётся `\"55\"`. Данные извне проверяйте сами.",
                       bad='''
                           def pay(amount: int) -> int:
                               return amount * 2''',
                       good='''
                           def pay(amount: int) -> int:
                               if not isinstance(amount, int):
                                   raise TypeError("нужно int")
                               return amount * 2'''),
               pitfall("`List` без импорта: `NameError: name 'List' is not defined`. Сейчас пишут {`list[int]`}.",
                       bad="def total(xs: List[int]): ...", good="def total(xs: list[int]): ..."),
               pitfall("Параметр со значением `None` по умолчанию имеет тип `str | None`, а не `str`.",
                       bad="def greet(name: str = None): ...", good="def greet(name: str | None = None): ...")]),
        topic("typing_advanced", "Protocol: интерфейс по форме",
              "`Protocol` описывает, какие методы нужны объекту, и любой класс с ними подходит без наследования.",
              """
              Функции часто нужен не конкретный класс, а умение: «объект, у которого есть `read`». Наследовать все такие классы от общего родителя неудобно, а чужие классы не поменять. `Protocol` описывает умение для анализатора типов без наследования.

              ## Как записать

              ```syntax
              from typing import Protocol

              class Умеет(Protocol):
                  def метод(self, x: int) -> str: ...
              ```

              Тело методов — `...`: протокол только перечисляет, что должно быть. Протокол может требовать и атрибуты: `name: str`.

              ## Подходит по форме

              Класс подходит под протокол, если у него есть методы с нужными именами и типами. Наследовать протокол не нужно. Это [[inh_poly|утиная типизация]], которую понимает анализатор: он проверит вызов `load(obj)` до запуска программы.

              Сам протокол объект не создаёт: `Reader()` даёт `TypeError`.

              ## isinstance с протоколом

              Обычный протокол нельзя передать в `isinstance`: будет `TypeError`. Декоратор `@runtime_checkable` это разрешает, но проверка грубая: смотрит только, есть ли атрибуты с такими именами. Сигнатуры и типы не проверяются.

              ## Что выбрать

              - `Protocol` — классы не связаны, менять их нельзя или не нужно.
              - Абстрактный класс {`ABC`} — классы ваши, и общий родитель даёт им готовые методы.
              """,
              [("""\
                from typing import Protocol

                class Reader(Protocol):
                    def read(self) -> str: ...

                class Disk:
                    def read(self) -> str:
                        return "данные с диска"

                def load(src: Reader) -> str:
                    return src.read()

                print(load(Disk()))""",
                "Disk не наследует Reader, но подходит по форме"),
               ("""\
                from typing import Protocol
                from typing import runtime_checkable

                @runtime_checkable
                class Sized(Protocol):
                    def size(self) -> int: ...

                class Box:
                    def size(self) -> int:
                        return 3

                print(isinstance(Box(), Sized))
                print(isinstance("abc", Sized))""",
                "isinstance с протоколом: у Box есть size, у строки — нет"),
               ("""\
                from typing import Protocol

                class Named(Protocol):
                    name: str

                try:
                    isinstance("x", Named)
                except TypeError as e:
                    print(e)""",
                "Без @runtime_checkable isinstance с протоколом — TypeError")],
              [pitfall("`isinstance` с протоколом без `@runtime_checkable` даёт `TypeError`.",
                       bad='''
                           class Reader(Protocol):
                               def read(self) -> str: ...''',
                       good='''
                           @runtime_checkable
                           class Reader(Protocol):
                               def read(self) -> str: ...'''),
               pitfall("`@runtime_checkable` проверяет только имена: объект с `read = 5` пройдёт `isinstance`, а вызов упадёт.",
                       bad='''
                           if isinstance(src, Reader):
                               text = src.read()''',
                       good='''
                           if callable(getattr(src, "read", None)):
                               text = src.read()'''),
               pitfall("Протокол — описание, а не класс для объектов: `TypeError: Protocols cannot be instantiated`.",
                       bad="src = Reader()", good="src = Disk()")]),
        topic("typing_generics", "Дженерики и псевдонимы типов",
              "Параметр типа `T` связывает типы входа и выхода, а `type` даёт длинной аннотации короткое имя.",
              """
              Функция `first(items)` возвращает элемент списка: для списка чисел — число, для списка строк — строку. Аннотация `-> object` теряет эту связь. С параметром типа анализатор знает точный тип результата.

              ## Как записать

              ```syntax
              def функция[T](items: list[T]) -> T:
                  тело

              class Класс[T]:
                  тело

              type Псевдоним = тип
              ```

              Запись {`[T]`} после имени появилась в Python 3.12. В старом коде то же пишут через `TypeVar` и `Generic` из модуля `typing`.

              ## Параметр типа

              `T` — переменная для типа. В одном вызове все `T` означают один и тот же тип: для {`first([1, 2])`} анализатор выведет `int`, для {`first(["a"])`} — `str`. Параметров может быть несколько: {`[K, V]`}.

              Запись {`[N: (int, float)]`} разрешает только перечисленные типы.

              ## Обобщённый класс

              {`class Stack[T]`} — контейнер для значений одного типа: {`Stack[int]`} хранит числа. При выполнении {`Stack[int]()`} — обычный вызов класса, тип элементов никто не проверяет.

              ## Псевдоним типа

              {`type UserId = int`} даёт аннотации короткое или говорящее имя. Это подсказка для анализатора, а не новый класс: `isinstance(5, UserId)` даёт `TypeError`.
              """,
              [("""\
                def first[T](items: list[T]) -> T:
                    return items[0]

                print(first([10, 20]))
                print(first(["чай", "кофе"]))""",
                "Одна функция для любых списков; T связывает вход и выход"),
               ("""\
                class Stack[T]:
                    def __init__(self) -> None:
                        self.items: list[T] = []
                    def push(self, x: T) -> None:
                        self.items.append(x)
                    def pop(self) -> T:
                        return self.items.pop()

                s = Stack[int]()
                s.push(1)
                s.push(2)
                print(s.pop())""",
                "Stack[int] — подсказка анализатору, при запуске обычный класс"),
               ("""\
                type Point = tuple[float, float]

                def dist(p: Point) -> float:
                    return (p[0]**2 + p[1]**2) ** 0.5

                print(dist((3.0, 4.0)))
                print(Point.__value__)""",
                "Псевдоним Point — короткое имя для tuple[float, float]")],
              [pitfall("Псевдоним из `type` — не класс: `isinstance(5, UserId)` даёт `TypeError`.",
                       bad="isinstance(uid, UserId)", good="isinstance(uid, int)"),
               pitfall("`T` без объявления в {`[T]`}: `NameError: name 'T' is not defined`.",
                       bad="def first(items: list[T]) -> T: ...", good="def first[T](items: list[T]) -> T: ..."),
               pitfall("{`Stack[int]`} при запуске примет и строку: ошибку покажет только анализатор. Приводите тип сами.",
                       bad='''
                           s = Stack[int]()
                           s.push(input())''',
                       good='''
                           s = Stack[int]()
                           s.push(int(input()))''')]),
        topic("typing_typeddict", "TypedDict, Literal и Final",
              "`TypedDict` описывает ключи словаря, `Literal` — допустимые значения, `Final` — константу; это подсказки анализатору.",
              """
              Данные из [[data_json|JSON]] приходят словарями: `{"id": 7, "name": "Ада"}`. Аннотация {`dict[str, object]`} ничего не говорит о ключах. {`TypedDict`}, {`Literal`} и `Final` уточняют такие места для анализатора.

              ## Словарь с известными ключами

              ```syntax
              from typing import TypedDict

              class Имя(TypedDict):
                  ключ: тип
                  другой_ключ: тип
              ```

              Анализатор проверит, что у словаря есть все ключи и значения нужных типов, и заметит опечатку в ключе. Во время выполнения это обычный `dict`, проверок нет. Необязательный ключ помечают {`NotRequired[тип]`}.

              ## Только перечисленные значения

              {`Literal["asc", "desc"]`} разрешает только эти значения. Подходит для параметров-режимов. Если вариантов много или им нужно поведение, лучше [[dc_enum|Enum]].

              ## Константа

              `MAX: Final = 3` объявляет константу: анализатор сообщит о повторном присваивании. Сам Python присваивание не запретит.

              ## Общее правило

              Все три — подсказки, как и остальные [[typing_basics|аннотации]]. Проверку данных во время выполнения пишут сами: через `isinstance` или в `__post_init__` у [[dc_basics|dataclass]].
              """,
              [("""\
                from typing import TypedDict

                class Song(TypedDict):
                    title: str
                    year: int

                s: Song = {
                    "title": "Тишина",
                    "year": 1965,
                }
                print(s["title"])
                print(s["year"] + 1)""",
                "Значение Song создаётся обычным словарём"),
               ("""\
                from typing import TypedDict

                class Song(TypedDict):
                    title: str
                    year: int

                bad: Song = {"title": "X", "year": "65"}
                print(bad["year"] * 2)""",
                "Строка вместо числа прошла: при запуске проверки нет"),
               ("""\
                from typing import Literal

                Order = Literal["asc", "desc"]

                def arrange(xs: list[int], order: Order):
                    rev = order == "desc"
                    return sorted(xs, reverse=rev)

                print(arrange([3, 1, 2], "asc"))
                print(arrange([3, 1, 2], "desc"))""",
                "Literal перечисляет допустимые строки-режимы")],
              [pitfall("{`TypedDict`} ничего не проверяет при создании: это обычный `dict`. Данные из JSON проверяют сами.",
                       bad='''
                           song: Song = json.loads(text)
                           print(song["year"] + 1)''',
                       good='''
                           song: Song = json.loads(text)
                           if not isinstance(song["year"], int):
                               raise ValueError("year — не число")'''),
               pitfall("{`Literal`} при запуске пропустит опечатку: с `\"down\"` список молча отсортируется по возрастанию.",
                       bad='''
                           def arrange(xs, order: Order):
                               return sorted(xs, reverse=order == "desc")''',
                       good='''
                           def arrange(xs, order: Order):
                               if order not in get_args(Order):
                                   raise ValueError(order)
                               return sorted(xs, reverse=order == "desc")'''),
               pitfall("`Final` не запрещает присваивание при выполнении: `LIMIT = 4` сработает, предупредит только анализатор.",
                       bad='''
                           LIMIT: Final = 3
                           LIMIT = 4''',
                       good='''
                           LIMIT: Final = 3
                           limit = LIMIT + 1''')]),
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
              topic="typing_generics", hint="[T] после имени класса объявляет параметр типа. Box[str] при выполнении ничего не проверяет.",
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
                ["3 x", "TypeError", "4 r"], position=0, topic="typing_typeddict",
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
                ["User '7' ['id', 'name']", "dict 7 ['id', 'name']", "TypeError"], position=1, topic="typing_typeddict",
                hint="TypedDict существует только для анализатора: во время выполнения — обычный словарь без проверок.",
                explanation="u — обычный dict, и строка «7» вместо числа проходит без ошибки. get_type_hints(User) возвращает объявленные ключи: id и name.",
                role="boss", difficulty=4,
                feedback={"User '7' ['id', 'name']": "Объект, созданный литералом {...}, — обычный dict.",
                          "dict 7 ['id', 'name']": "Значение осталось строкой: TypedDict ничего не преобразует — repr показывает кавычки.",
                          "TypeError": "Во время выполнения TypedDict ничего не проверяет."}),
    ],
))
