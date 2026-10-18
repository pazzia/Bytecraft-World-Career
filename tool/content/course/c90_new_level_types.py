"""Levels of the newer mechanics, added to existing modules (before their
boss): trace tables, sorting into groups, true/false series, retyping a
broken line. Kept in one file so that topic texts (c01–c08) and these
levels can be edited independently."""
from bclib import categorize, fix_line, trace, true_false, run

MODULES = []


def is_ok(code):
    return run(code).ok


def value_of(expr, setup=""):
    result = run((setup + "\n" if setup else "") + f"print(repr({expr}))")
    assert result.ok, (expr, result.error, result.message)
    return result.out.strip()


def truthy(expr):
    return value_of(f"bool({expr})") == "True"


def hashable(expr):
    return is_ok(f"hash({expr})")


EXTRA_LEVELS = {}

# --------------------------------------------------------------- variables
EXTRA_LEVELS["variables"] = [
    trace("nx_var_trace", "Следим за переменными", """\
          a = 5
          b = a
          a = a + 2
          b = b * 2
          a, b = b, a""", ["a", "b"],
          topic="var_assign", difficulty=2,
          hint="Python вычисляет правую часть, потом связывает имя слева. b = a копирует текущее значение.",
          explanation="b = a даёт b текущее значение 5 — дальше a и b живут отдельно. a, b = b, a меняет их местами за один шаг: сначала вычисляется пара (b, a), потом раздаётся."),
    fix_line("nx_var_fix", "Имя с ошибкой", """\
             price = 120
             count = 3
             total = price * Count
             print(total)""", 2, ["total = price * count"],
             expect_error="NameError", topic="var_names", role="practice", difficulty=2,
             hint="Python различает большие и маленькие буквы в именах.",
             explanation="Count и count — разные имена. Переменной Count нет, поэтому NameError."),
]

# ------------------------------------------------------------------- types
TYPE_ITEMS = [("42", 0), ("3.0", 1), ('"42"', 2), ("7 / 7", 1), ("7 // 7", 0), ("str(5)", 2), ("int('8')", 0)]
EXTRA_LEVELS["types"] = [
    categorize("nx_types_sort", "Какого типа значение", "Разложите значения по типам",
               ["int", "float", "str"], TYPE_ITEMS, code_items=True,
               check=lambda expr: ["int", "float", "str"].index(value_of(f"type({expr}).__name__").strip("'")),
               topic="types_basic", difficulty=1,
               hint="Деление / всегда даёт float, // для целых — int. Кавычки делают строку.",
               explanation="42 и 7 // 7 — целые, 3.0 и 7 / 7 — дробные: / всегда возвращает float. Всё в кавычках и результат str() — строки, int('8') превращает строку в число."),
    true_false("nx_bool_tf", "Истина или ложь", "Что вернёт bool(...) для этих значений: True — «Верно», False — «Неверно»",
               [("0", False), ("''", False), ("' '", True, "Строка из пробела не пустая — значит, истина."),
                ("[]", False), ("[0]", True, "Список с одним элементом не пуст, даже если элемент — ноль."),
                ("-1", True, "Ложь только ноль; любое другое число — истина."), ("None", False)],
               check=truthy, code_items=True, topic="types_bool", difficulty=2,
               hint="Ложны: 0, пустые строки и коллекции, None. Всё остальное — истина.",
               explanation="Пустое и нулевое — ложь, всё остальное — истина. Поэтому ' ' и [0] истинны: они не пустые."),
]

# --------------------------------------------------------------- operators
EXTRA_LEVELS["operators"] = [
    categorize("nx_ops_result", "Что получится", "Разложите выражения по результату",
               ["True", "False"],
               [("7 // 2 == 3", 0), ("7 % 2 == 0", 1), ("2 ** 3 > 7", 0), ("not 3 > 2", 1),
                ("1 < 5 < 4", 1, "Цепочка 1 < 5 < 4 значит 1 < 5 and 5 < 4 — второе ложно."),
                ("'a' < 'b'", 0)],
               check=lambda e: 0 if value_of(e) == "True" else 1, code_items=True,
               topic="ops_compare", difficulty=2,
               hint="Вычислите каждое выражение. Цепочки сравнений Python читает как and.",
               explanation="7 // 2 — 3, 7 % 2 — 1, 2 ** 3 — 8. Цепочка 1 < 5 < 4 ложна, потому что ложно 5 < 4. Строки сравниваются по буквам."),
    fix_line("nx_ops_fix", "Среднее арифметическое", """\
             a, b = 4, 8
             avg = a + b / 2
             print(avg)""", 1, ["avg = (a + b) / 2"],
             topic="ops_precedence", role="practice", difficulty=2,
             hint="Деление выполняется раньше сложения. Как заставить сложить первым?",
             explanation="a + b / 2 — это 4 + 4.0 = 8.0. Нужны скобки: (a + b) / 2 = 6.0."),
]

# ----------------------------------------------------------------- strings
EXTRA_LEVELS["strings"] = [
    trace("nx_str_trace", "Строка по шагам", """\
          word = "кот"
          word = word.upper()
          word = word + "ИК"
          size = len(word)
          first = word[0]""", ["word", "size", "first"],
          extra=["'кот'", "'котИК'", "'к'"],
          topic="str_methods", difficulty=2,
          hint="upper() возвращает новую строку — её нужно присвоить. len считает символы.",
          explanation="Строки неизменяемы: каждый шаг создаёт новую строку и связывает с ней имя word. После «КОТИК» длина 5, первый символ — «К»."),
    true_false("nx_str_tf", "Про строки", "Верно ли утверждение?",
               [("s.upper() меняет строку s на месте", False, "Строки неизменяемы: upper возвращает новую строку."),
                ("'abc'[-1] — это 'c'", True),
                ("'abc'[1:] — это 'bc'", True),
                ("len('привет') равно 12", False, "len считает символы, а не байты: 6."),
                ("f'{2 + 3}' даёт строку '5'", True)],
               check=lambda text: {
                   "s.upper() меняет строку s на месте": value_of("(s.upper(), s)[1]", "s = 'ab'") == "'AB'",
                   "'abc'[-1] — это 'c'": value_of("'abc'[-1]") == "'c'",
                   "'abc'[1:] — это 'bc'": value_of("'abc'[1:]") == "'bc'",
                   "len('привет') равно 12": value_of("len('привет')") == "12",
                   "f'{2 + 3}' даёт строку '5'": value_of("f'{2 + 3}'") == "'5'",
               }[text],
               topic="str_basics", difficulty=2,
               hint="Проверьте каждое утверждение мысленно в интерпретаторе.",
               explanation="Методы строк возвращают новые строки, индекс -1 — последний символ, срез [1:] — всё без первого, len считает символы."),
]

# ---------------------------------------------------------------------- io
EXTRA_LEVELS["io"] = [
    fix_line("nx_io_fix", "Сумма двух чисел", """\
             a = "3"
             b = "4"
             print(a + b)""", 2, ["print(int(a) + int(b))"],
             topic="io_input", role="practice", difficulty=2,
             hint="Что делает + со строками? Как превратить строку в число?",
             explanation="Для строк + склеивает: «34». Чтобы сложить числа, строки переводят в int: 3 + 4 = 7."),
]

# -------------------------------------------------------------- conditions
EXTRA_LEVELS["conditions"] = [
    trace("nx_cond_trace", "Какая ветка сработает", """\
          temp = 18
          clothes = "куртка"
          if temp > 25:
              clothes = "футболка"
          elif temp > 15:
              clothes = "свитер"
          else:
              clothes = "пальто"
          temp = temp + 10""", ["temp", "clothes"],
          extra=["'пальто'", "'футболка'"],
          topic="cond_if", difficulty=2,
          hint="Условия проверяются сверху вниз; выполняется первая подходящая ветка.",
          explanation="18 > 25 — нет, 18 > 15 — да: clothes становится «свитер», else пропускается. Последняя строка меняет только temp."),
    fix_line("nx_cond_fix", "Совершеннолетие", """\
             age = 18
             if age > 18:
                 print("доступ разрешён")
             else:
                 print("доступ закрыт")""", 1, ["if age >= 18:"],
             topic="cond_if", role="practice", difficulty=1,
             hint="18 лет — уже можно. Какой оператор включает границу?",
             explanation="> не включает 18, поэтому 18-летний получает отказ. >= — «больше или равно»."),
]

# ------------------------------------------------------------------- loops
EXTRA_LEVELS["loops"] = [
    trace("nx_loop_trace", "Сумма в цикле", """\
          total = 0
          for n in [3, 5, 2]:
              total = total + n
          done = True""", ["n", "total"], lines=[3],
          topic="loop_for", difficulty=2,
          hint="После каждого прохода total увеличивается на текущий n.",
          explanation="n по очереди принимает 3, 5, 2; total копит сумму: 3, 8, 10."),
    fix_line("nx_loop_fix", "Обратный отсчёт", """\
             n = 3
             while n > 0:
                 print(n)
                 n = n + 1
             print("Старт!")""", 3, ["n = n - 1", "n -= 1"],
             topic="loop_while", role="challenge", difficulty=2,
             hint="Условие n > 0 должно когда-нибудь стать ложным.",
             explanation="n + 1 уводит n от нуля — цикл бесконечный. Нужно уменьшать: n -= 1, тогда напечатается 3, 2, 1 и «Старт!»."),
]

# ----------------------------------------------------------- loops_control
EXTRA_LEVELS["loops_control"] = [
    trace("nx_break_trace", "Поиск с break", """\
          found = None
          checked = 0
          for x in [4, 7, 9, 12]:
              checked = checked + 1
              if x % 3 == 0:
                  found = x
                  break""", ["x", "checked", "found"], lines=[4, 6],
          topic="loopx_break", difficulty=3,
          hint="break выходит из цикла сразу — оставшиеся элементы не проверяются.",
          explanation="4 и 7 не делятся на 3. На 9 found становится 9 и break завершает цикл — 12 уже не проверяется, checked остаётся 3."),
]

# ------------------------------------------------------------------- lists
EXTRA_LEVELS["lists"] = [
    trace("nx_list_trace", "Список меняется", """\
          items = [1, 2]
          items.append(3)
          items.insert(0, 9)
          last = items.pop()
          items[1] = 5""", ["items", "last"],
          topic="list_methods", difficulty=2,
          hint="append — в конец, insert(0, x) — в начало, pop() — забирает последний.",
          explanation="[1, 2] → [1, 2, 3] → [9, 1, 2, 3]; pop убирает 3 и возвращает его; items[1] = 5 заменяет второй элемент."),
    true_false("nx_list_tf", "Про списки", "Верно ли утверждение?",
               [("b = a не копирует список: a и b — один объект", True),
                ("sorted(a) меняет сам список a", False, "sorted возвращает новый список; на месте сортирует a.sort()."),
                ("a.append([1, 2]) добавляет два элемента", False, "append добавляет один элемент — сам список. Два элемента добавит extend."),
                ("a[-1] — последний элемент", True)],
               check=lambda text: {
                   "b = a не копирует список: a и b — один объект": value_of("b is a", "a = [1]; b = a") == "True",
                   "sorted(a) меняет сам список a": value_of("(sorted(a), a)[1]", "a = [2, 1]") == "[1, 2]",
                   "a.append([1, 2]) добавляет два элемента": value_of("(a.append([1, 2]), len(a))[1]", "a = []") == "2",
                   "a[-1] — последний элемент": value_of("a[-1]", "a = [1, 2, 3]") == "3",
               }[text],
               topic="list_mutable", difficulty=2,
               hint="Проверьте, что возвращает функция и меняет ли она исходный список.",
               explanation="Присваивание не копирует список. sorted создаёт новый, append добавляет ровно один элемент."),
]

# ------------------------------------------------------------- tuples_sets
EXTRA_LEVELS["tuples_sets"] = [
    categorize("nx_mutable_sort", "Изменяемое или нет", "Разложите типы: можно ли менять объект после создания?",
               ["Изменяемые", "Неизменяемые"],
               [("[1, 2]", 0), ("(1, 2)", 1), ("{1, 2}", 0), ("'abc'", 1), ("{'a': 1}", 0), ("frozenset({1})", 1), ("42", 1)],
               check=lambda expr: 1 if hashable(expr) else 0, code_items=True,
               topic="tuple_basics", difficulty=2,
               hint="Неизменяемые объекты можно класть в множество и делать ключами словаря.",
               explanation="Списки, множества и словари меняются на месте. Кортежи, строки, числа и frozenset — нет, поэтому они хешируемы."),
]

# ------------------------------------------------------------------- dicts
EXTRA_LEVELS["dicts"] = [
    trace("nx_dict_trace", "Подсчёт букв", """\
          counts = {}
          for ch in "абба":
              counts[ch] = counts.get(ch, 0) + 1
          size = len(counts)""", ["ch", "counts"], lines=[3],
          extra=["{'а': 2, 'б': 1}", "{'б': 1}", "{'а': 2}"],
          topic="dict_counting", difficulty=3,
          hint="get(ch, 0) возвращает 0, если ключа ещё нет.",
          explanation="Каждая буква увеличивает свой счётчик. Порядок ключей — порядок первого появления: 'а', потом 'б'."),
    fix_line("nx_dict_fix", "Безопасное чтение", """\
             stock = {"яблоки": 5}
             print(stock["груши"])""", 1, ['print(stock.get("груши", 0))'],
             expect_error="KeyError", topic="dict_methods", role="practice", difficulty=2,
             hint="Как прочитать ключ, которого может не быть, и получить значение по умолчанию?",
             explanation="stock[\"груши\"] падает с KeyError. get(ключ, по_умолчанию) возвращает 0, если ключа нет."),
]

# ------------------------------------------------------------ comprehensions
EXTRA_LEVELS["comprehensions"] = [
    fix_line("nx_comp_fix", "Только чётные", """\
             nums = [1, 2, 3, 4, 5, 6]
             evens = [n for n in nums if n % 2 == 1]
             print(evens)""", 1, ["evens = [n for n in nums if n % 2 == 0]"],
             topic="comp_cond", role="practice", difficulty=2,
             hint="Остаток от деления на 2 у чётных чисел равен…",
             explanation="n % 2 == 1 отбирает нечётные. У чётных остаток 0."),
]

# --------------------------------------------------------------- functions
EXTRA_LEVELS["functions"] = [
    trace("nx_func_trace", "Внутри функции", """\
          def area(w, h):
              s = w * h
              return s

          a = area(2, 3)
          b = area(a, 2)""", ["a", "b"], lines=[5, 6], first_given=False,
          topic="func_def", difficulty=2,
          hint="Результат функции — то, что после return. Во второй вызов попадает уже вычисленное a.",
          explanation="area(2, 3) возвращает 6, area(6, 2) — 12."),
    fix_line("nx_func_fix", "Функция ничего не вернула", """\
             def double(x):
                 x * 2

             print(double(4))""", 1, ["return x * 2"],
             topic="func_def", role="practice", difficulty=2,
             hint="Что возвращает функция без return?",
             explanation="Без return функция возвращает None. Чтобы вернуть результат, нужен return x * 2."),
]

# -------------------------------------------------------------------- args
EXTRA_LEVELS["args"] = [
    true_false("nx_args_tf", "Про аргументы", "Верно ли утверждение?",
               [("*args собирает лишние позиционные аргументы в кортеж", True),
                ("**kwargs собирает именованные аргументы в список", False, "В словарь: имя → значение."),
                ("Изменяемое значение по умолчанию создаётся заново при каждом вызове", False,
                 "Оно создаётся один раз при объявлении функции — поэтому def f(a=[]) опасен."),
                ("После * в параметрах идут только именованные аргументы", True)],
               check=lambda text: {
                   "*args собирает лишние позиционные аргументы в кортеж": value_of("type(f(1, 2)).__name__", "def f(*args): return args") == "'tuple'",
                   "**kwargs собирает именованные аргументы в список": value_of("type(f(a=1)).__name__", "def f(**kw): return kw") == "'list'",
                   "Изменяемое значение по умолчанию создаётся заново при каждом вызове": value_of("(f(), f())[1]", "def f(a=[]):\n    a.append(1)\n    return a") == "[1]",
                   "После * в параметрах идут только именованные аргументы": not is_ok("def f(*, b): pass\nf(1)"),
               }[text],
               topic="args_star", difficulty=3,
               hint="Проверьте каждое утверждение на маленьком примере.",
               explanation="*args — кортеж, **kwargs — словарь. Значение по умолчанию вычисляется один раз. После * — только именованные параметры."),
]

# ------------------------------------------------------------------- scope
EXTRA_LEVELS["scope"] = [
    trace("nx_scope_trace", "Глобальная и локальная", """\
          x = 1

          def change():
              x = 99
              return x

          y = change()
          z = x""", ["x", "y", "z"], lines=[1, 7, 8],
          topic="scope_legb", difficulty=3,
          hint="Присваивание внутри функции создаёт локальную переменную — глобальная x не меняется.",
          explanation="Внутри change своя x = 99; функция возвращает её. Глобальная x осталась 1, поэтому z = 1."),
]

# --------------------------------------------------------------- functional
EXTRA_LEVELS["functional"] = [
    categorize("nx_fn_sort", "Что возвращают функции", "Разложите выражения по типу результата",
               ["list", "int", "bool"],
               [("sorted([3, 1])", 0), ("sum([1, 2])", 1), ("any([0, 1])", 2), ("list(map(abs, [-1]))", 0),
                ("max([1, 5])", 1), ("all([])", 2, "all от пустой последовательности — True: нет ни одного ложного.")],
               check=lambda e: ["'list'", "'int'", "'bool'"].index(value_of(f"type({e}).__name__")), code_items=True,
               topic="fn_builtins", difficulty=2,
               hint="sorted и list(...) дают список; sum, max — число; any, all — True/False.",
               explanation="sorted всегда возвращает новый список, sum и max — элементы или их сумму, any и all — логические значения."),
]

# --------------------------------------------------------------- recursion
EXTRA_LEVELS["recursion"] = [
    fix_line("nx_rec_fix", "Без условия остановки", """\
             def fact(n):
                 if n == 0:
                     return 0
                 return n * fact(n - 1)

             print(fact(5))""", 2, ["return 1"],
             topic="rec_basics", role="challenge", difficulty=3,
             hint="Чему равен 0! ? И что будет с произведением, если на дне рекурсии ноль?",
             explanation="0! = 1. С return 0 всё произведение обнуляется: 5 · 4 · 3 · 2 · 1 · 0 = 0."),
]

# -------------------------------------------------------------- exceptions
EXTRA_LEVELS["exceptions"] = [
    categorize("nx_exc_sort", "Какое исключение", "Разложите ошибки по типу исключения",
               ["ValueError", "TypeError", "KeyError", "IndexError"],
               [("int('abc')", 0), ("'a' + 1", 1), ("{}['x']", 2), ("[][0]", 3), ("len(5)", 1), ("float('1,5')", 0)],
               check=lambda e: ["ValueError", "TypeError", "KeyError", "IndexError"].index(run(e).error),
               code_items=True, topic="exc_types", difficulty=2,
               hint="ValueError — тип верный, значение плохое; TypeError — операция не для этого типа.",
               explanation="int('abc') и float('1,5') — строки не те по содержанию: ValueError. 'a' + 1 и len(5) — неподходящие типы. Нет ключа — KeyError, нет индекса — IndexError."),
    fix_line("nx_exc_fix", "Поймать нужное", """\
             try:
                 n = int("десять")
             except ZeroDivisionError:
                 n = 0
             print(n)""", 2, ["except ValueError:"],
             expect_error="ValueError", topic="exc_try", role="practice", difficulty=2,
             hint="Какое исключение бросает int для строки, которая не число?",
             explanation="int(\"десять\") бросает ValueError, а except ловит только ZeroDivisionError — ошибка вылетает. Нужен except ValueError."),
]

# ------------------------------------------------------------------- stdlib
EXTRA_LEVELS["stdlib"] = [
    trace("nx_counter_trace", "Counter и deque", """\
          from collections import Counter, deque
          c = Counter("aab")
          top = c.most_common(1)
          q = deque([1, 2])
          q.appendleft(0)
          q.pop()""", ["top", "q"], lines=[3, 4, 5, 6],
          extra=["deque([2, 1])", "deque([1, 2, 0])", "deque([1])"],
          topic="std_collections", difficulty=3,
          hint="most_common(1) — список с одной парой (элемент, сколько раз). appendleft — в начало, pop — с конца.",
          explanation="Чаще всего встречается 'a' — дважды. deque: [1, 2] → [0, 1, 2] → [0, 1]."),
]

# ------------------------------------------------------------------ classes
EXTRA_LEVELS["classes"] = [
    fix_line("nx_class_fix", "Забытый self", """\
             class Counter:
                 def __init__(self):
                     self.value = 0

                 def add(self):
                     value += 1

             c = Counter()
             c.add()
             print(c.value)""", 5, ["self.value += 1"],
             expect_error="UnboundLocalError", topic="oop_class", role="practice", difficulty=2,
             hint="Как метод обращается к атрибуту своего объекта?",
             explanation="value внутри метода — локальная переменная, а не атрибут. Атрибут объекта — self.value."),
    categorize("nx_class_attr_sort", "Атрибут класса или объекта", "Где хранится атрибут?",
               ["Атрибут класса", "Атрибут объекта"],
               [("species = 'кот' прямо в теле class", 0), ("self.name = name в __init__", 1),
                ("count, общий для всех объектов", 0), ("self.age = 3 в методе", 1)],
               topic="oop_class_attrs", difficulty=2,
               hint="Присваивание через self создаёт атрибут конкретного объекта.",
               explanation="Имена в теле класса принадлежат классу и общие для всех. self.x = ... создаёт атрибут одного объекта."),
]

# ------------------------------------------------------------- inheritance
EXTRA_LEVELS["inheritance"] = [
    true_false("nx_inh_tf", "Про наследование", "Верно ли утверждение?",
               [("Дочерний класс получает методы родителя", True),
                ("super().__init__() вызывать не нужно: Python сделает это сам", False,
                 "Если в дочернем классе есть свой __init__, родительский сам не вызовется."),
                ("isinstance(dog, Animal) — True для объекта подкласса Animal", True),
                ("Метод дочернего класса с тем же именем заменяет родительский", True)],
               check=lambda text: {
                   "Дочерний класс получает методы родителя": value_of("B().hi()", "class A:\n    def hi(self): return 1\nclass B(A): pass") == "1",
                   "super().__init__() вызывать не нужно: Python сделает это сам": is_ok("class A:\n    def __init__(self): self.x = 1\nclass B(A):\n    def __init__(self): pass\nB().x"),
                   "isinstance(dog, Animal) — True для объекта подкласса Animal": value_of("isinstance(Dog(), Animal)", "class Animal: pass\nclass Dog(Animal): pass") == "True",
                   "Метод дочернего класса с тем же именем заменяет родительский": value_of("B().hi()", "class A:\n    def hi(self): return 1\nclass B(A):\n    def hi(self): return 2") == "2",
               }[text],
               topic="inh_basics", difficulty=2,
               hint="Проверьте каждое утверждение на коротком классе.",
               explanation="Подкласс наследует методы и может их переопределить. Свой __init__ заменяет родительский — тот вызывают явно через super()."),
]

# ------------------------------------------------------------------- dunder
EXTRA_LEVELS["dunder"] = [
    categorize("nx_dunder_sort", "Какой метод вызовется", "Что Python вызывает для этой записи?",
               ["__len__", "__str__", "__eq__", "__add__"],
               [("len(obj)", 0), ("print(obj)", 1), ("a == b", 2), ("a + b", 3), ("f'{obj}'", 1)],
               code_items=True, topic="dunder_protocols", difficulty=2,
               hint="Для каждого встроенного действия есть свой «магический» метод.",
               explanation="len → __len__, print и f-строка → __str__, == → __eq__, + → __add__."),
]

# --------------------------------------------------------------- properties
EXTRA_LEVELS["properties"] = [
    fix_line("nx_prop_fix", "Свойство вызывают без скобок", """\
             class Circle:
                 def __init__(self, r):
                     self.r = r

                 @property
                 def area(self):
                     return 3 * self.r ** 2

             c = Circle(2)
             print(c.area())""", 9, ["print(c.area)"],
             expect_error="TypeError", topic="prop_property", role="practice", difficulty=2,
             hint="@property превращает метод в атрибут. Как читают атрибут?",
             explanation="c.area уже вычисляет значение (12). c.area() пытается вызвать число — TypeError: 'int' object is not callable."),
]

# -------------------------------------------------------------- dataclasses
EXTRA_LEVELS["dataclasses"] = [
    true_false("nx_dc_tf", "Про dataclass", "Верно ли утверждение?",
               [("@dataclass сам пишет __init__ по аннотациям полей", True),
                ("Два объекта dataclass с равными полями равны (==)", True),
                ("Поле со списком можно задать как items: list = []", False, "Нужно field(default_factory=list) — иначе ValueError."),
                ("frozen=True запрещает менять поля", True)],
               check=lambda text: {
                   "@dataclass сам пишет __init__ по аннотациям полей": is_ok("from dataclasses import dataclass\n@dataclass\nclass P:\n    x: int\nP(1)"),
                   "Два объекта dataclass с равными полями равны (==)": value_of("P(1) == P(1)", "from dataclasses import dataclass\n@dataclass\nclass P:\n    x: int") == "True",
                   "Поле со списком можно задать как items: list = []": is_ok("from dataclasses import dataclass\n@dataclass\nclass P:\n    items: list = []"),
                   "frozen=True запрещает менять поля": not is_ok("from dataclasses import dataclass\n@dataclass(frozen=True)\nclass P:\n    x: int\np = P(1)\np.x = 2"),
               }[text],
               topic="dc_basics", difficulty=2,
               hint="Проверьте каждое утверждение на коротком dataclass.",
               explanation="dataclass генерирует __init__, __repr__ и __eq__. Изменяемые значения по умолчанию задают через field(default_factory=...). frozen=True делает объект неизменяемым."),
]

# -------------------------------------------------------------- generators
EXTRA_LEVELS["generators"] = [
    trace("nx_gen_trace", "Генератор по шагам", """\
          def countdown(n):
              while n > 0:
                  yield n
                  n -= 1

          g = countdown(3)
          a = next(g)
          b = next(g)
          rest = list(g)""", ["a", "b", "rest"], lines=[7, 8, 9],
          extra=["[]", "[2, 1]", "[1, 0]"],
          topic="gen_yield", difficulty=3,
          hint="next выполняет генератор до следующего yield. list забирает всё оставшееся.",
          explanation="Первый next отдаёт 3, второй — 2. list(g) забирает оставшееся: [1]."),
]

# -------------------------------------------------------------- decorators
EXTRA_LEVELS["decorators"] = [
    fix_line("nx_deco_fix", "Обёртка без результата", """\
             def shout(func):
                 def wrapper(*args):
                     func(*args).upper()
                 return wrapper

             @shout
             def greet(name):
                 return "привет, " + name

             print(greet("ада"))""", 2, ["return func(*args).upper()"],
             topic="deco_basics", role="challenge", difficulty=3,
             hint="Что вернёт wrapper, если в нём нет return?",
             explanation="wrapper вычисляет строку и выбрасывает её — возвращается None. Обёртка должна вернуть результат: return func(*args).upper()."),
]

# ---------------------------------------------------------------- contexts
EXTRA_LEVELS["contexts"] = [
    true_false("nx_ctx_tf", "Про with", "Верно ли утверждение?",
               [("Файл, открытый в with open(...), закрывается даже при ошибке", True),
                ("as x получает объект, который вернул __enter__", True),
                ("__exit__ не вызывается, если в блоке было исключение", False, "Вызывается всегда — для этого with и нужен."),
                ("contextlib.suppress(KeyError) глушит любые исключения", False, "Только перечисленные — здесь KeyError.")],
               check=lambda text: {
                   "Файл, открытый в with open(...), закрывается даже при ошибке": value_of("f.closed", "try:\n    with open('t.txt', 'w') as f:\n        1 / 0\nexcept ZeroDivisionError:\n    pass") == "True",
                   "as x получает объект, который вернул __enter__": value_of("x", "class M:\n    def __enter__(self): return 42\n    def __exit__(self, *a): pass\nwith M() as x:\n    pass") == "42",
                   "__exit__ не вызывается, если в блоке было исключение": value_of("log", "log = []\nclass M:\n    def __enter__(self): return self\n    def __exit__(self, *a): log.append('exit')\ntry:\n    with M():\n        1 / 0\nexcept ZeroDivisionError:\n    pass") == "[]",
                   "contextlib.suppress(KeyError) глушит любые исключения": is_ok("import contextlib\nwith contextlib.suppress(KeyError):\n    1 / 0"),
               }[text],
               topic="ctx_protocol", difficulty=3,
               hint="Проверьте, что делает __exit__ при исключении.",
               explanation="with гарантирует вызов __exit__ при любом выходе. as получает результат __enter__. suppress глушит только указанные исключения."),
]

# ------------------------------------------------------------------ typing
EXTRA_LEVELS["typing"] = [
    true_false("nx_typing_tf", "Аннотации при выполнении", "Верно ли утверждение?",
               [("Python не проверяет аннотации при вызове функции", True),
                ("def f(x: int) не даст передать строку", False, "Аннотации — подсказки: f('a') выполнится."),
                ("Ошибки типов находит статический анализатор (mypy, pyright)", True)],
               check=lambda text: {
                   "Python не проверяет аннотации при вызове функции": is_ok("def f(x: int) -> int:\n    return x\nf('a')"),
                   "def f(x: int) не даст передать строку": not is_ok("def f(x: int):\n    return x\nf('a')"),
                   "Ошибки типов находит статический анализатор (mypy, pyright)": True,
               }[text],
               topic="typing_basics", difficulty=2,
               hint="Аннотации — это проверяется при выполнении или нет?",
               explanation="Аннотации не влияют на выполнение. Их проверяют анализаторы до запуска."),
]

# --------------------------------------------------------------- algorithms
EXTRA_LEVELS["algorithms"] = [
    trace("nx_bsearch_trace", "Бинарный поиск по шагам", """\
          items = [2, 5, 8, 12, 16, 23]
          target = 16
          lo, hi = 0, len(items) - 1
          while lo <= hi:
              mid = (lo + hi) // 2
              if items[mid] < target:
                  lo = mid + 1
              elif items[mid] > target:
                  hi = mid - 1
              else:
                  break""", ["lo", "hi", "mid"], lines=[5],
          topic="algo_search_sort", difficulty=3,
          hint="mid — середина между lo и hi. Если середина меньше искомого, lo сдвигается за неё.",
          explanation="Сначала mid = 2 (8 < 16) — lo = 3. Затем mid = 4 — там 16, break. Две проверки вместо пяти."),
    categorize("nx_complexity_sort", "Сложность операции", "Разложите операции по сложности",
               ["O(1)", "O(n)", "O(n log n)"],
               [("x in set", 0), ("x in list", 1), ("sorted(list)", 2), ("dict[key]", 0), ("list.insert(0, x)", 1), ("sum(list)", 1)],
               code_items=True, topic="algo_complexity", difficulty=3,
               hint="Хеш-таблицы — O(1), просмотр всех элементов — O(n), сортировка — O(n log n).",
               explanation="Множество и словарь ищут по хешу. in по списку, сумма и вставка в начало проходят или сдвигают все элементы. Сортировка — O(n log n)."),
]

# ----------------------------------------------------------------- pythonic
EXTRA_LEVELS["pythonic"] = [
    fix_line("nx_walrus_fix", "Моржовый оператор", """\
             data = [3, 8, 1, 9]
             if n = len(data) > 3:
                 print("длина", n)""", 1, ["if (n := len(data)) > 3:"],
             expect_error="SyntaxError", topic="idiom_walrus", role="challenge", difficulty=3,
             hint="Присваивание внутри выражения пишут через :=, и нужны скобки, чтобы n получило длину.",
             explanation="= внутри if — синтаксическая ошибка. (n := len(data)) > 3 сохраняет длину в n и сравнивает её с 3."),
]

# ------------------------------------------------------------------ testing
EXTRA_LEVELS["testing"] = [
    true_false("nx_test_tf", "Про тесты", "Верно ли утверждение?",
               [("assert с ложным условием бросает AssertionError", True),
                ("assert (x > 0, 'сообщение') проверяет x > 0", False, "Это кортеж — он всегда истинен."),
                ("Mock запоминает, с какими аргументами его вызывали", True)],
               check=lambda text: {
                   "assert с ложным условием бросает AssertionError": run("assert 1 > 2").error == "AssertionError",
                   "assert (x > 0, 'сообщение') проверяет x > 0": not is_ok("x = -1\nassert (x > 0, 'msg')"),
                   "Mock запоминает, с какими аргументами его вызывали": value_of("m.call_args.args", "from unittest.mock import Mock\nm = Mock()\nm(1, 2)") == "(1, 2)",
               }[text],
               topic="test_assert", difficulty=2,
               hint="Что именно проверяет assert, если после него стоят скобки с запятой?",
               explanation="assert падает, если условие ложно. Скобки с запятой создают кортеж — непустой кортеж всегда истинен. Mock записывает каждый вызов."),
]

# -------------------------------------------------------------------- async
EXTRA_LEVELS["async"] = [
    categorize("nx_async_sort", "Блокирует или уступает", "Что делает эта строка внутри корутины?",
               ["Уступает ход другим задачам", "Блокирует весь цикл"],
               [("await asyncio.sleep(1)", 0), ("time.sleep(1)", 1), ("await queue.get()", 0),
                ("sum(range(10**8))", 1, "Долгое вычисление не отдаёт управление — остальные задачи ждут."),
                ("await asyncio.gather(a(), b())", 0)],
               code_items=True, topic="async_basics", difficulty=3,
               hint="Управление отдаётся только в точке await.",
               explanation="await с асинхронной операцией отдаёт ход циклу событий. Синхронный sleep и тяжёлые вычисления держат поток — все задачи стоят."),
]

# -------------------------------------------------------------- concurrency
EXTRA_LEVELS["concurrency"] = [
    categorize("nx_conc_sort", "Потоки или процессы", "Что лучше подходит для задачи в обычном CPython?",
               ["Потоки (threading)", "Процессы (multiprocessing)"],
               [("Скачать 100 страниц", 0), ("Посчитать хеши миллиона паролей на чистом Python", 1),
                ("Ждать ответы базы данных", 0), ("Обработать картинки циклами на Python на всех ядрах", 1)],
               topic="conc_processes", difficulty=2,
               hint="GIL не мешает ожиданию, но мешает вычислениям на чистом Python.",
               explanation="Ожидания (сеть, база) хорошо работают в потоках. Вычисления на чистом Python упираются в GIL — им нужны процессы."),
]

# ------------------------------------------------------------- performance
EXTRA_LEVELS["performance"] = [
    fix_line("nx_perf_fix", "Кэш и список", """\
             from functools import cache

             @cache
             def total(prices):
                 return sum(prices)

             print(total([10, 20, 30]))""", 6, ["print(total((10, 20, 30)))"],
             expect_error="TypeError", topic="perf_tricks", role="practice", difficulty=2,
             hint="Кэш хранит результаты в словаре по аргументам. Каким должен быть ключ словаря?",
             explanation="Список нехешируем — cache не может сделать его ключом: TypeError. Кортеж (10, 20, 30) хешируем."),
]

# ------------------------------------------------------------------ project
EXTRA_LEVELS["project"] = [
    fix_line("nx_main_fix", "Точка входа", """\
             def main():
                 print("программа работает")

             if __name__ == "main":
                 main()""", 3, ['if __name__ == "__main__":'],
             topic="proj_structure", role="practice", difficulty=1,
             hint="Какое значение у __name__ у запущенного файла?",
             explanation="У запущенного файла __name__ — \"__main__\" с подчёркиваниями. С \"main\" условие ложно, и программа молчит."),
]
