"""Модули 13–17: функции, аргументы, области видимости и замыкания,
функциональный стиль, рекурсия."""
from bclib import choice, fill, match, multi, order, predict, bug, typed, topic, task, run, pitfall


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
              "`def` объявляет функцию — именованный блок кода, а `return` отдаёт результат в место вызова.",
              """
              Функция даёт имя куску кода, который нужен много раз: посчитать скидку, проверить пароль, вывести меню. Код пишут один раз, а вызывают сколько угодно — с разными данными.

              ## Как записать

              ```syntax
              def имя(параметры):
                  \"\"\"Что делает функция.\"\"\"
                  тело
                  return результат
              ```

              - Тело пишут с отступом; оно выполняется только при вызове `имя(аргументы)`.
              - Скобки нужны и при вызове без аргументов: `menu()`.
              - Строка в тройных кавычках в начале тела — docstring, её показывает `help(имя)`.

              Как передавать значения в функцию — в теме [[func_params|Параметры и аргументы]].

              ## Что делает return

              `return` сразу завершает функцию и отдаёт значение туда, откуда её вызвали. Результат сохраняют в переменную или используют в выражении: `square(4) + 1`.

              Функция без `return` или с пустым `return` возвращает `None` — «значения нет».

              ## print или return

              `print` только показывает текст на экране и ничего не возвращает в программу. Если результат нужен дальше — для расчёта, сравнения, записи в файл, — нужен `return`.

              ## Несколько значений

              `return lo, hi` возвращает [[tuple_basics|кортеж]] из двух значений. Его сразу раскладывают по переменным: `lo, hi = bounds(nums)`.

              Функция — такое же значение, как число или строка: её можно передать в другую функцию аргументом и вызвать там.
              """,
              [("""\
                def discount(price):
                    return price * 0.9

                total = discount(200) + 50
                print(total)""",
                "Значение из return сразу участвует в выражении"),
               ("""\
                def greet(name):
                    print("Привет,", name)

                result = greet("Ада")
                print(result)""",
                "Функция без return печатает текст, но возвращает None"),
               ("""\
                def to_hours(minutes):
                    return minutes // 60, minutes % 60

                h, m = to_hours(135)
                print(h, m)
                print(to_hours(59))""",
                "Два значения через запятую — кортеж, его раскладывают по именам"),
               ("""\
                def grade(score):
                    if score < 0:
                        return "ошибка"
                    if score >= 50:
                        return "зачёт"
                    return "незачёт"

                print(grade(73))
                print(grade(-5))""",
                "return сразу завершает функцию: строки ниже не выполняются")],
              [pitfall("print только показывает число, а функция возвращает None: `cost(2, 3) + 1` даст TypeError.",
                       bad='''
                           def cost(qty, price):
                               print(qty * price)''',
                       good='''
                           def cost(qty, price):
                               return qty * price'''),
               pitfall("Без скобок `discount` — сама функция, а не результат её вызова.",
                       bad="print(discount)", good="print(discount(200))"),
               pitfall("Если ни один `return` не сработал, функция возвращает `None`.",
                       bad='''
                           def is_adult(age):
                               if age >= 18:
                                   return True''',
                       good='''
                           def is_adult(age):
                               if age >= 18:
                                   return True
                               return False''')]),
        topic("func_params", "Параметры и аргументы",
              "Параметры — имена в объявлении функции, аргументы — значения, которые передают при вызове.",
              """
              Параметры делают функцию гибкой: одна функция считает объём и коробки, и комнаты. Какое значение попадёт в какой параметр, решают при вызове.

              ## Как записать

              ```syntax
              def имя(обязательный, необязательный=значение):
                  тело

              имя(значение1, необязательный=значение2)
              ```

              ## Позиционные и именованные

              - Позиционный аргумент попадает в параметр по порядку: `box(2, 3)`.
              - Именованный — по имени, порядок не важен: `box(h=3, w=2)`.
              - Именованные аргументы пишут после позиционных.

              ## Значение по умолчанию

              Параметр со значением по умолчанию можно не передавать. При `def box(w, h, depth=1)` вызов `box(2, 3)` — это `box(2, 3, 1)`. Такие параметры ставят после обязательных.

              Список или словарь по умолчанию — ловушка, о ней тема [[args_mutable_default|Изменяемое значение по умолчанию]].

              ## Когда аргументы не подходят

              Если аргументы не совпадают с параметрами, будет [[exc_types|TypeError]] с подсказкой:

              - `missing 1 required positional argument` — не хватает аргумента;
              - `takes 2 positional arguments but 3 were given` — лишний аргумент;
              - `got multiple values for argument` — значение передано дважды.
              """,
              [("""\
                def greet(name, word="Привет"):
                    return f"{word}, {name}"

                print(greet("Ада"))
                print(greet("Линус", "Здравствуй"))""",
                "Второй аргумент не передан — взято значение по умолчанию"),
               ("""\
                def box(w, h, depth=1):
                    return w * h * depth

                print(box(2, 3))
                print(box(h=3, w=2, depth=4))
                print(box(2, 3, depth=5))""",
                "Именованные аргументы можно передавать в любом порядке"),
               ("""\
                def box(w, h, depth=1):
                    return w * h * depth

                # try/except — тема «Исключения»
                try:
                    box(2)
                except TypeError as e:
                    print(e)""",
                "Не хватило аргумента: Python называет пропущенный параметр")],
              [pitfall("Позиционный аргумент после именованного — SyntaxError: positional argument follows keyword argument.",
                       bad="box(w=2, 3)", good="box(2, h=3)", syntax_error=True),
               pitfall("2 уже попало в `w`, а потом `w` передан ещё раз: TypeError: got multiple values for argument 'w'.",
                       bad="box(2, w=3)", good="box(2, h=3)"),
               pitfall("Параметр без значения по умолчанию после параметра со значением — SyntaxError.",
                       bad="def box(w=1, h): ...", good="def box(h, w=1): ...", syntax_error=True)]),
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
        topic("args_star", "Любое число аргументов",
              "`*args` собирает лишние позиционные аргументы в кортеж, а `**kwargs` — лишние именованные в словарь.",
              """
              Иногда заранее неизвестно, сколько аргументов передадут: `print` и `max` принимают любое число значений. Свою такую функцию объявляют со звёздочками.

              ## Как записать

              ```syntax
              def имя(обычные, *args, **kwargs):
                  тело
              ```

              - `*args` — [[tuple_basics|кортеж]] лишних позиционных аргументов. Если их нет — пустой кортеж `()`.
              - `**kwargs` — словарь лишних именованных: `{"имя": значение}`.
              - Имена `args` и `kwargs` — соглашение. Работают звёздочки: можно `*prices` или `**options`.

              ## Порядок параметров

              Сначала обычные параметры, потом `*args`, в конце `**kwargs`. Параметры между `*args` и `**kwargs` передаются только по имени — об этом тема [[args_kwonly|Параметры после * и до /]].

              ## Зачем это нужно

              Чаще всего — чтобы принять любые аргументы и передать их дальше другой функции без изменений: `func(*args, **kwargs)`. Звёздочки при вызове раскладывают значения обратно — это [[args_unpack|распаковка]]. На этом построены [[deco_basics|декораторы]].
              """,
              [("""\
                def total(*prices):
                    print(prices)
                    return sum(prices)

                print(total(120, 80, 45))
                print(total())""",
                "Внутри *prices — кортеж; без аргументов он пустой"),
               ("""\
                def card(name, **extra):
                    print(name, extra)

                card("Ада")
                card("Ада", age=36, city="Лондон")""",
                "Лишние именованные аргументы попали в словарь"),
               ("""\
                def log(level, *parts, **opts):
                    sep = opts.get("sep", " ")
                    print(level + ":", sep.join(parts))

                log("INFO", "файл", "сохранён")
                log("WARN", "a", "b", sep="-")""",
                "Обычный параметр, *parts и **opts в одной функции")],
              [pitfall("`*args` — кортеж, а не список: `append` даст AttributeError.",
                       bad="args.append(x)",
                       good='''
                           items = list(args)
                           items.append(x)'''),
               pitfall("`**kwargs` пишут последним, иначе SyntaxError: arguments cannot follow var-keyword argument.",
                       bad="def f(**kwargs, *args): ...", good="def f(*args, **kwargs): ...", syntax_error=True),
               pitfall("Список без звёздочки — один аргумент: в `prices` будет кортеж из списка, и `sum` упадёт с TypeError.",
                       bad="total([120, 80])", good="total(*[120, 80])")]),
        topic("args_unpack", "Распаковка при вызове",
              "Звёздочка при вызове раскладывает список по позиционным аргументам, две звёздочки — словарь по именованным.",
              """
              Данные часто уже лежат в списке или словаре: размеры, координаты, настройки из файла. Распаковка передаёт их в функцию без того, чтобы выписывать каждый элемент вручную.

              ## Как записать

              ```syntax
              функция(*последовательность)
              функция(**словарь)
              ```

              - `f(*[1, 2])` — то же, что `f(1, 2)`.
              - `f(**{"x": 1})` — то же, что `f(x=1)`.
              - Распаковку сочетают с обычными аргументами: `f(0, *coords, z=5)`.

              Звёздочки при объявлении функции, наоборот, собирают аргументы — это тема [[args_star|`*args` и `**kwargs`]].

              ## Правила для словаря

              Ключи словаря должны совпадать с именами параметров. Лишний ключ даёт TypeError: `got an unexpected keyword argument`, если у функции нет `**kwargs`.

              ## Распаковка в print

              `print(*items)` печатает элементы через пробел, без скобок и запятых. Параметр `sep` задаёт свой разделитель: `print(*items, sep=", ")`.

              Звёздочка работает и в присваивании: `first, *rest = items` — об этом тема [[idiom_unpack|Распаковка со звёздочкой]].
              """,
              [("""\
                def rect(w, h):
                    return w * h

                size = [4, 5]
                print(rect(*size))""",
                "*size разложил список на два аргумента"),
               ("""\
                def move(x, y, speed=1):
                    return x * speed, y * speed

                opts = {"y": 2, "x": 3, "speed": 10}
                print(move(**opts))""",
                "Ключи словаря стали именованными аргументами"),
               ("""\
                scores = [5, 3, 4]
                print(scores)
                print(*scores)
                print(*scores, sep=" | ")""",
                "Без звёздочки печатается список, со звёздочкой — его элементы")],
              [pitfall("Без звёздочки список — один аргумент: TypeError: missing 1 required positional argument.",
                       bad="rect([4, 5])", good="rect(*[4, 5])"),
               pitfall("Ключ, которого нет среди параметров: TypeError: got an unexpected keyword argument 'height'.",
                       bad='rect(**{"w": 4, "height": 5})', good='rect(**{"w": 4, "h": 5})')]),
        topic("args_kwonly", "Параметры после * и до /",
              "Параметры после `*` передаются только по имени, а параметры до `/` — только по позиции.",
              """
              Вызов `connect("db", 30)` не объясняет, что значит 30: таймаут, порт или число попыток. Звёздочка в списке параметров заставляет писать имя. Косая черта, наоборот, запрещает его.

              ## Как записать

              ```syntax
              def имя(позиционные, /, обычные, *, именованные):
                  тело
              ```

              - до `/` — только по позиции;
              - между `/` и `*` — как угодно;
              - после `*` — только по имени.

              Любую часть можно опустить. После [[args_star|`*args`]] параметры тоже только именованные, отдельная `*` там не нужна.

              ## Зачем только по имени

              Для настроек и флагов: `sorted(items, reverse=True)`, `connect(host, timeout=30)`. Имя в вызове объясняет значение и защищает от путаницы, если параметры поменяют местами.

              ## Зачем только по позиции

              Когда имя параметра ничего не добавляет к смыслу, и автор хочет оставить себе право его переименовать. Так устроены многие встроенные функции: `len(obj=[1])` даёт TypeError.

              В своём коде `/` встречается редко, а `*` — часто.
              """,
              [("""\
                def connect(host, *, timeout=5):
                    return f"{host}:{timeout}"

                print(connect("db"))
                print(connect("db", timeout=30))""",
                "timeout передан по имени — вызов понятен без документации"),
               ("""\
                def connect(host, *, timeout=5):
                    return f"{host}:{timeout}"

                try:
                    connect("db", 30)
                except TypeError as e:
                    print(e)""",
                "Число без имени не попало в timeout: TypeError"),
               ("""\
                print(len([1, 2]))
                try:
                    len(obj=[1, 2])
                except TypeError as e:
                    print(e)""",
                "У встроенной len параметр только позиционный")],
              [pitfall("Параметр после `*` передали по позиции: TypeError: takes 1 positional argument but 2 were given.",
                       bad='connect("db", 30)', good='connect("db", timeout=30)'),
               pitfall("Параметры до `/` передали по имени: TypeError: got some positional-only arguments passed as keyword arguments.",
                       bad='''
                           def ratio(a, b, /):
                               return a / b

                           ratio(a=1, b=2)''',
                       good='''
                           def ratio(a, b, /):
                               return a / b

                           ratio(1, 2)''')]),
        topic("args_mutable_default", "Изменяемое значение по умолчанию",
              "Значение по умолчанию создаётся один раз при `def`, поэтому список по умолчанию общий для всех вызовов.",
              """
              Ошибка из этой темы не выдаёт сообщений: программа работает, но данные одного вызова «перетекают» в другой. Её трудно найти, если не знать о ней заранее.

              ## Как это получается

              Значение по умолчанию вычисляется один раз — когда Python выполняет строку `def`. При `def add(item, items=[])` создаётся один список, и каждый вызов без `items` получает этот же список.

              Пока значение не меняют, это незаметно. Но `items.append(item)` меняет [[list_mutable|общий объект]], и следующий вызов видит изменения.

              ## Как записать правильно

              ```syntax
              def имя(параметр=None):
                  if параметр is None:
                      параметр = []
              ```

              `None` — неизменяемая метка «аргумент не передан». Новый список создаётся внутри функции, при каждом вызове свой.

              ## Что считается опасным

              Изменяемые значения: список `[]`, словарь `{}`, множество `set()`. Числа, строки, кортежи, `None`, `True` и `False` безопасны: их нельзя изменить на месте.
              """,
              [("""\
                def add_tag(tag, tags=[]):
                    tags.append(tag)
                    return tags

                print(add_tag("python"))
                print(add_tag("игра"))""",
                "Второй вызов получил тот же список, что и первый"),
               ("""\
                def add_tag(tag, tags=None):
                    if tags is None:
                        tags = []
                    tags.append(tag)
                    return tags

                print(add_tag("python"))
                print(add_tag("игра"))""",
                "С None каждый вызов создаёт свой новый список"),
               ("""\
                def bag(items=[]):
                    return items

                a = bag()
                b = bag()
                a.append("ключ")
                print(b)
                print(a is b)""",
                "Оба вызова вернули один и тот же объект")],
              [pitfall("Словарь по умолчанию тоже общий: настройки одного вызова попадут в следующий.",
                       bad='''
                           def save(data, opts={}):
                               opts["saved"] = True''',
                       good='''
                           def save(data, opts=None):
                               if opts is None:
                                   opts = {}
                               opts["saved"] = True'''),
               pitfall("`if not tags` подменит и переданный пустой список: вызывающий код не увидит изменений. Проверяйте `is None`.",
                       bad='''
                           if not tags:
                               tags = []''',
                       good='''
                           if tags is None:
                               tags = []''')]),
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
              "Python ищет имя в четырёх областях по очереди: в функции, во внешней функции, в модуле и среди встроенных имён.",
              """
              Одно и то же имя `x` может жить в функции и в модуле одновременно. Правило LEGB объясняет, какую из переменных увидит строка кода.

              ## Четыре области

              1. Local — переменные текущей функции и её параметры.
              2. Enclosing — переменные внешней функции, если функция вложенная.
              3. Global — переменные модуля, то есть файла.
              4. Built-in — встроенные имена: `len`, `print`, `sum`.

              Python берёт первое найденное. Если имени нет нигде — [[exc_types|NameError]].

              ## Присваивание и локальное имя

              Читать переменную модуля внутри функции можно без объявлений. Но если внутри функции этому имени что-то присваивается, оно локальное во всей функции — даже в строках выше присваивания.

              Тогда чтение до присваивания даёт `UnboundLocalError`. Изменить переменную модуля позволяет [[scope_global|global]], но чаще лучше вернуть значение через `return`.

              Локальным имя делает любое связывание: `=`, `+=`, `for x in`, `import`, `def`.

              ## Блоки не создают область

              `if`, `for` и `while` своей области не создают: переменная из тела `if` или цикла видна после него. Новую область создаёт функция, а не блок.
              """,
              [("""\
                level = 1

                def play():
                    level = 5
                    print("в игре:", level)

                play()
                print("в модуле:", level)""",
                "Присваивание в функции создало отдельную локальную переменную"),
               ("""\
                score = 10

                def show():
                    print(score)
                    score = 0

                try:
                    show()
                except UnboundLocalError as e:
                    print(e)""",
                "Из-за присваивания ниже score локальная во всей функции"),
               ("""\
                for i in range(3):
                    last = i * 10
                print(i)
                print(last)""",
                "Переменные цикла видны и после него")],
              [pitfall("`+=` внутри функции делает имя локальным: UnboundLocalError.",
                       bad='''
                           def inc():
                               count += 1''',
                       good='''
                           def inc(count):
                               return count + 1'''),
               pitfall("Переменная `sum` перекрывает встроенную функцию: `sum([1, 2])` дальше даст TypeError.",
                       bad="sum = 0", good="total = 0")]),
        topic("scope_global", "global и nonlocal",
              "`global` разрешает функции менять переменную модуля, а `nonlocal` — переменную внешней функции.",
              """
              По правилу [[scope_legb|LEGB]] присваивание внутри функции создаёт локальную переменную. Иногда нужно другое — изменить переменную снаружи. Для этого имя объявляют заранее.

              ## Как записать

              ```syntax
              def функция():
                  global имя
                  имя = новое_значение

              def внешняя():
                  имя = значение
                  def вложенная():
                      nonlocal имя
                      имя = новое_значение
              ```

              - `global` — имя из модуля;
              - `nonlocal` — имя из ближайшей внешней функции.

              Объявление пишут до первого использования имени. `nonlocal` для переменной модуля даёт SyntaxError — там нужен `global`.

              ## Когда объявление не нужно

              Для чтения объявлять не нужно — только для присваивания. `log.append(x)` или `d[k] = v` тоже обходятся без `global`: они меняют объект, а не связывают имя заново.

              `nonlocal` чаще всего встречается в [[scope_closure|замыканиях]] — например, в счётчике вызовов.

              ## Почему global избегают

              Функция, которая меняет глобальную переменную, зависит от порядка вызовов, и её трудно проверить. Обычно лучше принять значение параметром и вернуть результат через `return`.
              """,
              [("""\
                coins = 0

                def collect(n):
                    global coins
                    coins += n

                collect(5)
                collect(3)
                print(coins)""",
                "global: функция изменила переменную модуля"),
               ("""\
                def game():
                    lives = 3
                    def hit():
                        nonlocal lives
                        lives -= 1
                    hit()
                    hit()
                    return lives

                print(game())""",
                "nonlocal: вложенная hit меняет lives из game"),
               ("""\
                log = []

                def note(text):
                    log.append(text)

                note("старт")
                note("финиш")
                print(log)""",
                "append меняет сам список, global не нужен"),
               ("""\
                def collect(coins, n):
                    return coins + n

                coins = 0
                coins = collect(coins, 5)
                print(coins)""",
                "Без global: значение передано параметром и возвращено")],
              [pitfall("`nonlocal` для переменной модуля — SyntaxError: no binding for nonlocal 'x' found. Нужен `global`.",
                       bad='''
                           x = 1
                           def f():
                               nonlocal x''',
                       good='''
                           x = 1
                           def f():
                               global x''', syntax_error=True),
               pitfall("Объявление после использования — SyntaxError: name 'x' is used prior to global declaration.",
                       bad='''
                           def f():
                               print(x)
                               global x''',
                       good='''
                           def f():
                               global x
                               print(x)''', syntax_error=True)]),
        topic("scope_closure", "Замыкания",
              "Замыкание — вложенная функция, которая помнит переменные внешней функции и после её завершения.",
              """
              Замыкание позволяет «заготовить» функцию с настройкой: умножать на 3, добавлять приставку, считать вызовы. Настройку не передают при каждом вызове — функция помнит её сама.

              ## Как записать

              ```syntax
              def внешняя(настройка):
                  def внутренняя(аргумент):
                      return действие(аргумент, настройка)
                  return внутренняя
              ```

              - `внешняя` возвращает саму функцию `внутренняя` — без скобок, без вызова.
              - Каждый вызов `внешняя` создаёт новую функцию со своей настройкой.

              ## Что именно помнит замыкание

              Замыкание хранит ссылку на переменную, а не её значение в момент создания. Если переменная потом изменится, функция увидит новое значение.

              Чтобы присвоить такой переменной новое значение изнутри, нужен [[scope_global|nonlocal]].

              ## Ловушка с циклом

              Функции, созданные в цикле, ссылаются на одну переменную цикла. К моменту вызова цикл закончился, и все видят последнее значение.

              Решение — сохранить текущее значение в параметре по умолчанию: `def f(i=i)`. Оно вычисляется при создании функции.

              Замыкания лежат в основе [[deco_basics|декораторов]].
              """,
              [("""\
                def prefix(tag):
                    def add(text):
                        return tag + text
                    return add

                warn = prefix("[!] ")
                print(warn("мало места"))
                print(prefix("> ")("ok"))""",
                "Каждая созданная функция помнит свой tag"),
               ("""\
                def make():
                    price = 100
                    def show():
                        return price
                    price = 150
                    return show

                print(make()())""",
                "Замыкание видит значение переменной на момент вызова"),
               ("""\
                greets = []
                for name in ["Ада", "Линус"]:
                    def hi():
                        return "Привет, " + name
                    greets.append(hi)

                print(greets[0]())""",
                "Ловушка: первая функция видит последнее значение name"),
               ("""\
                greets = []
                for name in ["Ада", "Линус"]:
                    def hi(name=name):
                        return "Привет, " + name
                    greets.append(hi)

                print(greets[0]())""",
                "Параметр по умолчанию сохранил значение при создании")],
              [pitfall("`return add()` вызывает функцию сразу, а нужно вернуть её саму.",
                       bad="return add()", good="return add"),
               pitfall("Функции из цикла читают переменную при вызове, поэтому все видят последнее значение.",
                       bad='''
                           def hi():
                               return name''',
                       good='''
                           def hi(name=name):
                               return name'''),
               pitfall("Присваивание переменной внешней функции без `nonlocal` даёт UnboundLocalError.",
                       bad='''
                           def step():
                               count += 1''',
                       good='''
                           def step():
                               nonlocal count
                               count += 1''')]),
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
              "`lambda` — короткая функция без имени; её часто передают в `key`, чтобы задать признак сортировки.",
              """
              Отсортировать слова по длине, найти самый дешёвый товар, игрока с максимумом очков — для этого нужно сказать функции, по какому признаку сравнивать. Это делает параметр `key`.

              ## Как записать

              ```syntax
              lambda параметры: выражение
              ```

              `lambda x: x * x` — то же, что `def f(x): return x * x`, но в одну строку и без имени. Внутри только одно выражение, без `return`: его значение и есть результат.

              ## Как работает key

              `key` — функция, которая для каждого элемента вычисляет значение для сравнения. Сравниваются эти значения, а в результат попадают сами элементы.

              - `sorted(words, key=len)` — по длине;
              - `min(goods, key=lambda g: g[1])` — по второму полю;
              - `sorted(names, key=str.lower)` — без учёта регистра.

              `key` есть у `sorted`, `list.sort`, `min` и `max`. Сортировка устойчивая: равные по ключу элементы сохраняют исходный порядок.

              ## Что выбрать

              - `sorted(список)` возвращает новый список, исходный не меняется.
              - `список.sort()` сортирует на месте и возвращает `None`.
              - `lambda` — для короткого выражения в вызове, `def` — для всего остального.
              """,
              [("""\
                cities = ["Омск", "Москва", "Уфа"]
                print(sorted(cities))
                print(sorted(cities, key=len))""",
                "Без key — по алфавиту, с key=len — по длине"),
               ("""\
                goods = [
                    ("чай", 120),
                    ("сок", 90),
                    ("кофе", 300),
                ]
                cheap = min(goods, key=lambda g: g[1])
                print(cheap)""",
                "min сравнил цены, а вернул весь кортеж"),
               ("""\
                names = ["ann", "Bob", "cid", "Ada"]
                print(sorted(names))
                print(sorted(names, key=str.lower))""",
                "Заглавные буквы идут раньше строчных; key=str.lower это убирает"),
               ("""\
                marks = [4, 2, 5]
                result = marks.sort()
                print(result)
                print(marks)""",
                "sort меняет сам список и возвращает None")],
              [pitfall("`sort()` возвращает `None`: в `ranked` окажется `None`, а не список.",
                       bad="ranked = names.sort()", good="ranked = sorted(names)"),
               pitfall("`key=len()` вызывает `len` без аргумента: TypeError. Нужна сама функция, без скобок.",
                       bad="sorted(words, key=len())", good="sorted(words, key=len)"),
               pitfall("Функции с именем пишут через `def`: у неё понятное имя в трассировке и место для docstring.",
                       bad="square = lambda x: x * x",
                       good='''
                           def square(x):
                               return x * x''')]),
        topic("fn_builtins", "Функции для последовательностей",
              "Встроенные функции преобразуют, отбирают, проверяют и сводят к одному числу элементы последовательности без явного цикла.",
              """
              Многие циклы делают одно из четырёх: применяют действие к каждому элементу, отбирают подходящие, проверяют условие или считают итог. Для этих задач есть готовые встроенные функции.

              ## Как записать

              ```syntax
              map(функция, последовательность)
              filter(функция, последовательность)
              any(последовательность)
              all(последовательность)
              ```

              - `map` применяет функцию к каждому элементу;
              - `filter` оставляет элементы, для которых функция вернула истину;
              - `any` — есть ли хоть одно истинное значение;
              - `all` — все ли значения истинны.

              `filter(None, xs)` убирает [[types_bool|ложные]] значения. Для пустого списка `all([])` даёт `True`: ложных значений в нём нет.

              ## sum, min и max

              Эти функции сводят последовательность к одному значению:

              - `sum(xs)` — сумма чисел
              - `min(xs)`, `max(xs)` — наименьший и наибольший элемент
              - `max(xs, key=len)` — сравнить по результату функции, см. [[fn_lambda_key|параметр key]]
              - `max(xs, default=0)` — ответ для пустой последовательности вместо `ValueError`

              `min` и `max` принимают и отдельные значения: `max(3, 8)`. `sum` складывает только числа, строки склеивают методом [[str_methods|`join`]].

              ## Ленивые объекты

              `map` и `filter` ничего не считают сразу, а возвращают [[gen_iter|итератор]]: значения вычисляются по одному, когда их просят. Чтобы увидеть всё, оборачивают в `list()`.

              Итератор проходят один раз. Второй проход по тому же `map` ничего не даст.

              ## Что выбрать

              - [[comp_list|Включение]] `[f(x) for x in xs]` читается проще, чем `map` с `lambda`.
              - `any(x > 7 for x in xs)` короче цикла с флагом и `break`.
              - Для перебора с номером и параллельного перебора есть [[loopx_enumerate|enumerate и zip]].
              """,
              [("""\
                prices = ["120", "80", "45"]
                nums = list(map(int, prices))
                print(nums)
                print(sum(nums))""",
                "map превратил каждую строку в число"),
               ("""\
                names = ["Ада", "", "Линус", ""]
                print(list(filter(None, names)))
                big = filter(lambda s: len(s) > 3, names)
                print(list(big))""",
                "filter(None) убрал пустые строки, lambda — короткие имена"),
               ("""\
                marks = [5, 4, 2, 5]
                print(any(m == 2 for m in marks))
                print(all(m >= 3 for m in marks))""",
                "Есть ли двойка и все ли оценки не ниже тройки"),
               ("""\
                marks = [5, 3, 4]
                print(sum(marks))
                print(max(marks))
                words = ["кот", "собака", "ёж"]
                print(max(words, key=len))
                print(max([], default=0))""",
                "sum и max сводят список к одному значению; key и default меняют правила"),
               ("""\
                sq = map(lambda x: x * x, [1, 2, 3])
                print(type(sq).__name__)
                print(list(sq))
                print(list(sq))""",
                "map — ленивый объект; после первого прохода он пуст")],
              [pitfall("`print(map(...))` показывает объект `<map object …>`, а не значения.",
                       bad="print(map(str, nums))", good="print(list(map(str, nums)))"),
               pitfall("Второй проход по тому же `filter` пуст: итератор уже исчерпан.",
                       bad='''
                           evens = filter(lambda n: n % 2 == 0, nums)
                           print(list(evens))
                           print(sum(evens))''',
                       good='''
                           evens = [n for n in nums if n % 2 == 0]
                           print(evens)
                           print(sum(evens))'''),
               pitfall("`all` для пустого списка даёт `True`. Если пустой список — это ошибка, проверьте его отдельно.",
                       bad="ok = all(answers)", good="ok = bool(answers) and all(answers)"),
               pitfall("`sum` не склеивает строки: TypeError: unsupported operand type(s) for +: 'int' and 'str'.",
                       bad="text = sum(words)", good='text = "".join(words)')]),
        topic("fn_functools", "functools: reduce и partial",
              "`reduce` сворачивает последовательность в одно значение, а `partial` создаёт функцию с заранее заданными аргументами.",
              """
              Модуль `functools` — набор инструментов для работы с функциями. Чаще других встречаются два: `reduce` накапливает результат, `partial` настраивает готовую функцию.

              ## Как записать

              ```syntax
              from functools import reduce, partial

              reduce(функция, последовательность, начальное)
              partial(функция, аргументы)
              ```

              ## Как работает reduce

              1. Берёт начальное значение — это накопитель.
              2. Для каждого элемента вызывает `функция(накопитель, элемент)`.
              3. Результат становится новым накопителем.
              4. После последнего элемента возвращает накопитель.

              Без начального значения накопителем становится первый элемент, а на пустом списке будет TypeError.

              ## Как работает partial

              `partial(int, base=2)` возвращает новую функцию: она вызывает `int` с уже заданным `base=2`.

              Так готовят колбэк (от англ. callback — «обратный вызов»): функцию, которую вызывает не автор, а другой код. Например, `map` или [[fn_lambda_key|`key` у `sorted`]]. Им нужна функция, которую можно вызвать с одним аргументом.

              ## Что выбрать

              - Для суммы, максимума и склейки есть `sum`, `max`, `"".join` — они понятнее `reduce`.
              - `partial` короче `lambda` и сразу показывает зафиксированные аргументы.
              """,
              [("""\
                from functools import reduce

                def mul(acc, x):
                    print(acc, x)
                    return acc * x

                print(reduce(mul, [2, 3, 4], 1))""",
                "Каждая строка — накопитель и очередной элемент"),
               ("""\
                from functools import reduce

                def add(acc, x):
                    return acc + x

                print(reduce(add, [], 0))
                try:
                    reduce(add, [])
                except TypeError as e:
                    print(e)""",
                "Пустой список без начального значения — TypeError"),
               ("""\
                from functools import partial

                from_bin = partial(int, base=2)
                print(from_bin("1010"))
                print(from_bin("111"))""",
                "partial заранее задал base=2"),
               ("""\
                from functools import partial

                def with_rate(rate, price):
                    return round(price * rate)

                sale = partial(with_rate, 0.8)
                print(list(map(sale, [100, 250])))""",
                "Функция со скидкой передана в map как колбэк")],
              [pitfall("`reduce` без начального значения на пустом списке — TypeError: reduce() of empty iterable with no initial value.",
                       bad="reduce(add, items)", good="reduce(add, items, 0)"),
               pitfall("В Python 3.12 `reduce` не принимает `initial=`: TypeError. Начальное значение — третий аргумент.",
                       bad="reduce(add, items, initial=0)", good="reduce(add, items, 0)"),
               pitfall("`partial(pow, 0.5)` займёт первый параметр: получится `pow(0.5, x)`, а не корень.",
                       bad="root = partial(pow, 0.5)", good="root = partial(pow, exp=0.5)")]),
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
              Некоторые задачи сводятся к такой же, но меньшей: факториал 5 — это 5, умноженное на факториал 4. Рекурсия записывает такое решение напрямую.

              ## Как записать

              ```syntax
              def функция(задача):
                  if задача_простая:
                      return готовый_ответ
                  return собрать(функция(меньшая_задача))
              ```

              - Базовый случай — ответ известен сразу: `factorial(0)` равен 1.
              - Рекурсивный шаг обязан приближать к базовому случаю: `n - 1`, а не `n + 1`.

              ## Стек вызовов

              Каждый вызов ждёт результата следующего. Незавершённые вызовы складываются в стек, как тарелки. Когда срабатывает базовый случай, ответы возвращаются обратно по цепочке.

              Код после рекурсивного вызова выполняется на обратном пути — в обратном порядке.

              ## Предел глубины

              Если базовый случай не достигается, вызовы не кончаются. Python останавливает программу с `RecursionError`: по умолчанию глубина ограничена примерно 1000 вызовов. Узнать лимит можно через `sys.getrecursionlimit()`.
              """,
              [("""\
                def factorial(n):
                    if n == 0:
                        return 1
                    return n * factorial(n - 1)

                print(factorial(5))""",
                "Шаг уменьшает n, базовый случай factorial(0) останавливает спуск"),
               ("""\
                def length(word):
                    if word == "":
                        return 0
                    return 1 + length(word[1:])

                print(length("кот"))""",
                "Строка укорачивается на букву, пока не станет пустой"),
               ("""\
                def backwards(n):
                    if n == 0:
                        return
                    backwards(n - 1)
                    print(n)

                backwards(3)""",
                "print стоит после вызова: числа печатаются на обратном пути"),
               ("""\
                def down(n):
                    return down(n - 1)

                try:
                    down(5)
                except RecursionError as e:
                    print(e)""",
                "Без базового случая вызовы не кончаются")],
              [pitfall("Без `return` в шаге результат теряется: функция вернёт `None`, и умножение упадёт с TypeError.",
                       bad='''
                           if n == 0:
                               return 1
                           n * factorial(n - 1)''',
                       good='''
                           if n == 0:
                               return 1
                           return n * factorial(n - 1)'''),
               pitfall("Нет базового случая — RecursionError: maximum recursion depth exceeded.",
                       bad='''
                           def down(n):
                               return down(n - 1)''',
                       good='''
                           def down(n):
                               if n == 0:
                                   return 0
                               return down(n - 1)''')]),
        topic("rec_structures", "Рекурсия по вложенным структурам",
              "Рекурсия удобна для вложенных данных: одна функция обходит списки в списках и папки в папках любой глубины.",
              """
              Вложенные данные встречаются часто: папки внутри папок, комментарии с ответами, [[data_json|JSON]] из сети. Сколько будет уровней, заранее неизвестно, поэтому цикл в цикле не спасает.

              ## Как устроено решение

              Функция смотрит на элемент:

              - если он сам контейнер (список, словарь) — вызывает себя для его содержимого;
              - иначе это «лист», простое значение, — с ним работают напрямую.

              Базовый случай здесь — лист.

              ## Как проверить тип

              `isinstance(x, list)` возвращает `True`, если `x` — список. Можно передать кортеж типов: `isinstance(x, (list, tuple))`. Подробнее о проверке типов — в теме [[inh_poly|Полиморфизм и утиная типизация]].

              `max(значения, default=0)` возвращает 0 для пустой последовательности вместо ValueError. Это пригодится, когда у узла нет вложенных элементов.
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

                print(flatten([1, [2, [3, 4]], 5]))""",
                "extend добавил элементы из вложенного результата"),
               ("""\
                def count(items):
                    n = 0
                    for x in items:
                        if isinstance(x, list):
                            n += count(x)
                        else:
                            n += 1
                    return n

                print(count([1, [2, [3, 4]], []]))""",
                "Пустой вложенный список не добавил ни одного элемента"),
               ("""\
                def show(tree, indent=""):
                    for name, sub in tree.items():
                        print(indent + name)
                        if isinstance(sub, dict):
                            show(sub, indent + "  ")

                tree = {
                    "docs": {"2024": {}, "old": {}},
                    "readme.txt": None,
                }
                show(tree)""",
                "Отступ растёт с каждым уровнем вложенности")],
              [pitfall("`append` кладёт результат рекурсии целым списком, и вложенность сохраняется.",
                       bad="result.append(flatten(x))", good="result.extend(flatten(x))"),
               pitfall("`max` от пустой последовательности — ValueError: max() iterable argument is empty.",
                       bad="deepest = max(sizes)", good="deepest = max(sizes, default=0)")]),
        topic("rec_memo", "Мемоизация",
              "Мемоизация запоминает результаты вызовов, чтобы функция не считала одно и то же повторно.",
              """
              Наивная рекурсия иногда пересчитывает одни и те же значения снова и снова. `fib(n) = fib(n - 1) + fib(n - 2)` для `fib(35)` вызывает `fib(2)` миллионы раз и работает секунды, а `fib(50)` не досчитать за разумное время.

              ## Мемоизация вручную

              Словарь хранит готовые ответы. Перед вычислением функция проверяет, нет ли результата в словаре, а после — записывает его туда. Каждое `fib(k)` считается один раз, и время растёт линейно.

              ## Как записать через lru_cache

              ```syntax
              from functools import lru_cache

              @lru_cache(maxsize=None)
              def функция(аргументы):
                  тело
              ```

              Строка с `@` над `def` — это [[deco_basics|декоратор]]: он оборачивает функцию и добавляет ей кэш. `@cache` (с Python 3.9) — то же, что `@lru_cache(maxsize=None)`.

              Аргументы становятся ключами словаря-кэша, поэтому должны быть [[g:хешируемый|хешируемыми]]: числа, строки, кортежи. Список даст `TypeError: unhashable type: 'list'`.

              ## Что кэш не решает

              Глубина рекурсии остаётся прежней: первый же вызов `fib(5000)` с кэшем упадёт с [[rec_basics|RecursionError]]. Оптимизации хвостовой рекурсии в Python нет. Для больших `n` пишут цикл.
              """,
              [("""\
                calls = 0

                def fib(n):
                    global calls
                    calls += 1
                    if n < 2:
                        return n
                    return fib(n - 1) + fib(n - 2)

                print(fib(20))
                print(calls)""",
                "Без кэша ради fib(20) функция вызвана десятки тысяч раз"),
               ("""\
                memo = {}

                def fib(n):
                    if n < 2:
                        return n
                    if n not in memo:
                        memo[n] = fib(n - 1) + fib(n - 2)
                    return memo[n]

                print(fib(80))
                print(len(memo))""",
                "Каждое значение посчитано один раз и лежит в словаре"),
               ("""\
                from functools import cache

                @cache
                def paths(r, c):
                    if r == 0 or c == 0:
                        return 1
                    return paths(r - 1, c) + paths(r, c - 1)

                print(paths(16, 16))""",
                "Сетка 16 × 16: без кэша понадобилось бы больше миллиарда вызовов"),
               ("""\
                from functools import cache

                @cache
                def total(nums):
                    return sum(nums)

                print(total((1, 2, 3)))
                try:
                    total([1, 2, 3])
                except TypeError as e:
                    print(e)""",
                "Кортеж кэшируется, список — нет")],
              [pitfall("Аргументы кэшируемой функции — ключи словаря: список даёт TypeError: unhashable type: 'list'.",
                       bad="total([1, 2, 3])", good="total((1, 2, 3))"),
               pitfall("Кэш не снимает лимит глубины: `fib(5000)` с первого вызова даст RecursionError. Для больших `n` нужен цикл.",
                       bad="print(fib(5000))",
                       good='''
                           a, b = 0, 1
                           for _ in range(5000):
                               a, b = b, a + b'''),
               "Кэшировать функцию, которая печатает или пишет в файл: при повторном вызове с теми же аргументами тело не выполнится."]),
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
