"""Glossary: language constructs and terms -> the topic that explains them.

Used at build time to turn `code` fragments of topic texts into links
(see topic_markup.autolink) and shipped as glossary.json: the app shows
`brief` and the example (with its real output) in a bottom sheet when a
link is tapped.

term(key, topic=..., brief=..., example=..., match=(...), basic=False, auto=True)
  key      what is matched: a name (`print`, `json.dumps`, `@property`) or an
           operator (`**`). Methods are written with a dot: `.get`.
  topic    id of the topic; None for glossary-only entries (opened as
           [[g:key|text]], the sheet has no "open topic" button).
  match    other spellings that mean the same (`dict.get`, `.get`).
  basic    part of the basic vocabulary (print, len, for...): not linked
           after the functions module.
  auto     False for ambiguous fragments (`in`, `.pop`, `with`): linked only
           by hand.
"""

TERMS = []


def term(key, topic=None, *, brief, example=None, match=(), basic=False, auto=True):
    TERMS.append(dict(key=key, topic=topic, brief=brief, example=example,
                      match=list(match), basic=basic, auto=auto))


# The full list is maintained below.
# Source: docs/TOPIC_STYLE.md, section 4.3. Order of groups follows the table.

# ------------------------------------------------------------ built-ins
term("print", "io_print", basic=True,
     brief="Выводит значения через пробел; `sep` и `end` меняют разделители.",
     example='print("a", "b", sep="-")\nprint("x", end="!\\n")')
term("input", "io_input", basic=True,
     brief="Читает строку с клавиатуры; результат всегда `str`.")
term("len", "str_basics", basic=True,
     brief="Длина строки, списка, словаря: число элементов.",
     example='print(len("кот"), len([1, 2]))')
term("type", "types_basic",
     brief="Тип значения: `int`, `str`, `list` и другие.",
     example='print(type(3.5))\nprint(type("hi"))')
term("int", "types_convert", basic=True,
     brief="Целое число; `int(\"42\")` превращает строку в число, `int(3.9)` отбрасывает дробь.",
     example='print(int("42") + 1)\nprint(int(3.9))')
term("float", "types_convert",
     brief="Дробное число; `float(\"2.5\")` превращает строку в число.",
     example='print(float("2.5") * 2)')
term("str", "types_convert", basic=True,
     brief="Строка; `str(7)` превращает любое значение в текст.",
     example='print(str(7) + "!")')
term("bool", "types_convert",
     brief="Логическое значение; `bool(x)` говорит, истинно ли `x`.",
     example='print(bool(0), bool("да"))')
term("round", "types_convert",
     brief="Округляет; половинки идут к чётному: `round(2.5)` даёт 2.",
     example='print(round(2.5), round(3.5))\nprint(round(3.14159, 2))')
term("abs", "ops_arith",
     brief="Модуль числа: расстояние до нуля без знака.",
     example='print(abs(-7), abs(2.5))')
term("divmod", "ops_arith",
     brief="Частное и остаток сразу: `divmod(a, b)` даёт `(a // b, a % b)`.",
     example='print(divmod(17, 5))')
term("pow", "ops_arith",
     brief="Степень: `pow(2, 10)` то же, что `2 ** 10`.",
     example='print(pow(2, 10))')
term("range", "loop_range", basic=True,
     brief="Последовательность целых чисел; `stop` не входит.",
     example='print(list(range(1, 5)))\nprint(list(range(0, 10, 3)))')
term("enumerate", "loopx_enumerate",
     brief="Пары (номер, элемент) при переборе.",
     example='for i, ch in enumerate("ab"):\n    print(i, ch)')
term("zip", "loopx_enumerate",
     brief="Идёт по нескольким последовательностям параллельно.",
     example='for a, b in zip("ab", [1, 2]):\n    print(a, b)')
term("list", "list_basics", basic=True,
     brief="Изменяемый упорядоченный список.",
     example='print(list("abc"))')
term("tuple", "tuple_basics",
     brief="Неизменяемая последовательность.",
     example='t = tuple([1, 2])\nprint(t, len(t))')
term("set", "set_basics",
     brief="Множество уникальных элементов без порядка.",
     example='print(set([1, 1, 2]))')
term("dict", "dict_basics",
     brief="Словарь: пары «ключ — значение».",
     example='d = dict(a=1, b=2)\nprint(d["b"])')
term("sorted", "list_methods",
     brief="Новый отсортированный список, исходный не меняется.",
     example='xs = [3, 1, 2]\nprint(sorted(xs), xs)')
term("min", "fn_builtins",
     brief="Наименьший элемент последовательности или из аргументов.",
     example='print(min([4, 2, 9]), min(5, 3))')
term("max", "fn_builtins",
     brief="Наибольший элемент последовательности или из аргументов.",
     example='print(max([4, 2, 9]))\nprint(max("кот"))')
term("sum", "fn_builtins",
     brief="Сумма чисел последовательности; строки не складывает.",
     example='print(sum([1, 2, 3]))')
term("key=", "fn_lambda_key", match=("key=len",),
     brief="Функция, по результату которой сравнивают элементы в `sorted`, `min`, `max`.",
     example='w = ["ccc", "a", "bb"]\nprint(sorted(w, key=len))')
term("map", "fn_builtins",
     brief="Применяет функцию к каждому элементу; результат ленивый.",
     example='print(list(map(abs, [-1, 2])))')
term("filter", "fn_builtins",
     brief="Оставляет элементы, для которых функция вернула истину.",
     example='f = lambda n: n % 2\nprint(list(filter(f, range(5))))')
term("any", "fn_builtins",
     brief="Есть ли хоть одно истинное значение.",
     example='print(any([0, "", 3]))')
term("all", "fn_builtins",
     brief="Все ли значения истинны.",
     example='print(all([1, "a", []]))')
term("isinstance", "inh_poly",
     brief="Принадлежит ли объект классу с учётом наследования.",
     example='print(isinstance(5, int))\nprint(isinstance(True, int))')
term("issubclass", "inh_poly",
     brief="Является ли класс потомком другого класса.",
     example='print(issubclass(bool, int))')
term("iter", "gen_iter",
     brief="Получает итератор из списка, строки и другого итерируемого.",
     example='it = iter([10, 20])\nprint(next(it), next(it))')
term("next", "gen_iter",
     brief="Берёт следующее значение из итератора.",
     example='it = iter("ab")\nprint(next(it))\nprint(next(it, "конец"))')
term("open", "files_open",
     brief="Открывает файл; закрывать удобнее через `with`.",
     example='with open("a.txt", "w") as f:\n    f.write("hi")\nprint(open("a.txt").read())')
term("bytes", "files_bytes",
     brief="Неизменяемая последовательность байтов, чисел от 0 до 255; литерал пишут с `b`: `b\"abc\"`.",
     example='data = b"Hi"\nprint(data[0], list(data))')
term(".encode", "files_bytes", match=("str.encode",),
     brief="Превращает строку в байты в заданной кодировке, обычно UTF-8.",
     example='print("да".encode("utf-8"))')
term(".decode", "files_bytes", match=("bytes.decode",),
     brief="Превращает байты обратно в строку; кодировка должна совпасть.",
     example='data = b"\\xd0\\xb4\\xd0\\xb0"\nprint(data.decode("utf-8"))')
term("breakpoint", "test_debug",
     brief="Останавливает программу на этой строке и открывает отладчик `pdb`.")
term("hash", "dunder_ops",
     brief="Число-«отпечаток» значения для set и ключей dict.",
     example='print(hash(5))\nt = (1, 2)\nprint(hash(t) == hash((1, 2)))')
term("repr", "dunder_str",
     brief="Точное представление объекта для разработчика.",
     example='print(repr("hi"), str("hi"))')
term("super", "inh_basics",
     brief="Вызывает метод класса-родителя.",
     example=('class A:\n    def hi(self): return "A"\n'
              'class B(A):\n    def hi(self):\n'
              '        s = super().hi()\n        return s + "B"\nprint(B().hi())'))
term("hasattr", "prop_private",
     brief="Есть ли у объекта атрибут с таким именем.",
     example='print(hasattr("abc", "upper"))\nprint(hasattr(5, "upper"))')
term("help", "func_def",
     brief="Показывает docstring функции или модуля.",
     example='def f():\n    "Ничего не делает."\nprint(f.__doc__)')
term("reversed", "dunder_protocols",
     brief="Перебор последовательности с конца.",
     example='print(list(reversed([1, 2, 3])))')
term("id", "list_mutable",
     brief="Номер объекта; одинаковый у одного и того же объекта.",
     example='a = [1]\nb = a\nprint(id(a) == id(b))')

# -------------------------------------------- keywords and constructions
term("=", "var_assign", basic=True,
     brief="Связывает имя со значением.",
     example='x = 5\nx = x + 1\nprint(x)')
term("+=", "var_assign",
     brief="`x += 1` то же, что `x = x + 1`.",
     example='x = 5\nx += 2\nprint(x)')
term("-=", "var_assign",
     brief="`x -= 1` то же, что `x = x - 1`.",
     example='x = 5\nx -= 2\nprint(x)')
term("a, b = b, a", "var_multi",
     brief="Присваивание нескольких имён сразу и обмен значениями.",
     example='a, b = 1, 2\na, b = b, a\nprint(a, b)')
term("if", "cond_if", basic=True,
     brief="Выполняет блок, только если условие истинно.",
     example='x = 5\nif x > 0:\n    print("плюс")')
term("elif", "cond_if", basic=True,
     brief="Следующее условие, если предыдущие оказались ложными.",
     example='x = 0\nif x > 0: print("плюс")\nelif x == 0: print("ноль")')
term("else", "cond_if", auto=False,
     brief="Блок, который выполняется, если ни одно условие не подошло.",
     example='x = -3\nif x > 0: print("плюс")\nelse: print("не плюс")')
term("x if c else y", "cond_ternary",
     brief="Выражение: одно из двух значений в зависимости от условия.",
     example='n = 7\nprint("да" if n > 5 else "нет")')
term("and", "ops_logic",
     brief="Логическое «и»; второе не вычисляется, если первое ложно.",
     example='print(3 > 1 and 2 > 5)')
term("or", "ops_logic",
     brief="Логическое «или»; второе не вычисляется, если первое истинно.",
     example='print(3 > 1 or 2 > 5)\nprint("" or "пусто")')
term("not", "ops_logic",
     brief="Логическое «не»: превращает истину в ложь и наоборот.",
     example='print(not True, not [])')
term("for", "loop_for", basic=True,
     brief="Перебирает элементы последовательности по одному.",
     example='for ch in "abc":\n    print(ch)')
term("while", "loop_while", basic=True,
     brief="Повторяет блок, пока условие истинно.",
     example='n = 3\nwhile n > 0:\n    print(n); n -= 1')
term("break", "loopx_break",
     brief="Немедленно выходит из цикла.",
     example='for n in range(10):\n    if n == 3: break\nprint(n)')
term("continue", "loopx_break",
     brief="Пропускает остаток шага и переходит к следующему.",
     example='for n in range(4):\n    if n == 1: continue\n    print(n)')
term("for-else", "loopx_else", auto=False,
     brief="`else` у цикла выполняется, если цикл завершился без `break`.",
     example='for n in [1, 3]:\n    if n == 2: break\nelse: print("нет двойки")')
term("def", "func_def", basic=True,
     brief="Объявляет функцию.",
     example='def hi(name):\n    print("Привет,", name)\nhi("Аня")')
term("return", "func_def", basic=True,
     brief="Завершает функцию и возвращает результат.",
     example='def sq(x):\n    return x * x\nprint(sq(4))')
term("lambda", "fn_lambda_key",
     brief="Короткая безымянная функция из одного выражения.",
     example='sq = lambda x: x * x\nprint(sq(5))')
term("*args", "args_star",
     brief="Собирает лишние позиционные аргументы в кортеж.",
     example='def f(*args):\n    print(args)\nf(1, 2, 3)')
term("**kwargs", "args_star",
     brief="Собирает лишние именованные аргументы в словарь.",
     example='def f(**kwargs):\n    print(kwargs)\nf(a=1, b=2)')
term("f(*xs)", "args_unpack",
     brief="Раскладывает список по позиционным аргументам.",
     example='xs = [1, 2, 3]\nprint(*xs)\nprint(max(*xs))')
term("f(**d)", "args_unpack",
     brief="Раскладывает словарь по именованным аргументам.",
     example='d = {"sep": "-"}\nprint("a", "b", **d)')
term("f(a, /)", "args_kwonly", auto=False,
     brief="Параметры до `/` передаются только по позиции.",
     example='def f(a, /):\n    return a\nprint(f(1))')
term("f(*, b)", "args_kwonly", auto=False,
     brief="Параметры после `*` передаются только по имени.",
     example='def f(*, b):\n    return b\nprint(f(b=2))')
term("global", "scope_global",
     brief="Разрешает функции присваивать переменной модуля.",
     example='n = 0\ndef inc():\n    global n\n    n += 1\ninc()\nprint(n)')
term("nonlocal", "scope_global",
     brief="Разрешает вложенной функции присваивать переменной внешней.",
     example=('def outer():\n    n = 0\n    def inc():\n'
              '        nonlocal n\n        n += 1\n'
              '    inc()\n    return n\nprint(outer())'))
term("try", "exc_try",
     brief="Блок, ошибки в котором можно перехватить в `except`.",
     example='try:\n    1 / 0\nexcept ZeroDivisionError:\n    print("на ноль нельзя")')
term("except", "exc_try",
     brief="Перехватывает ошибку указанного типа.",
     example='try:\n    int("x")\nexcept ValueError as e:\n    print("ошибка:", e)')
term("finally", "exc_try",
     brief="Блок, который выполняется в любом случае: с ошибкой и без.",
     example='try:\n    print("работа")\nfinally:\n    print("уборка")')
term("raise", "exc_raise",
     brief="Выбрасывает исключение.",
     example='try:\n    raise ValueError("плохо")\nexcept ValueError as e:\n    print(e)')
term("class", "oop_class",
     brief="Объявляет класс: шаблон объектов.",
     example='class Cat:\n    name = "Мурка"\nprint(Cat().name)')
term("self", "oop_class",
     brief="Объект, у которого вызван метод.",
     example=('class Cat:\n    def __init__(self, n):\n'
              '        self.name = n\nprint(Cat("Мурка").name)'))
term("cls", "prop_classmethod",
     brief="Класс, у которого вызван метод класса.",
     example=('class A:\n    @classmethod\n'
              '    def who(cls):\n        return cls.__name__\nprint(A.who())'))
term("with", "files_open", auto=False,
     brief="Открывает ресурс и гарантированно закрывает его после блока.",
     example='with open("a.txt", "w") as f:\n    f.write("hi")\nprint(f.closed)')
term("yield", "gen_yield",
     brief="Отдаёт значение из генератора и замирает до следующего `next`.",
     example='def gen():\n    yield 1\n    yield 2\nprint(list(gen()))')
term("yield from", "gen_yield",
     brief="Отдаёт по очереди все значения другого итерируемого.",
     example='def gen():\n    yield from "ab"\n    yield "c"\nprint(list(gen()))')
term("async", "async_basics",
     brief="`async def` объявляет корутину: функцию, которая умеет ждать.",
     example=('import asyncio\nasync def main():\n'
              '    print("корутина")\nasyncio.run(main())'))
term("await", "async_basics",
     brief="Ждёт результат корутины, не блокируя другие задачи.",
     example=('import asyncio\nasync def main():\n'
              '    await asyncio.sleep(0)\n    print("дождались")\nasyncio.run(main())'))
term("import", "std_import",
     brief="Подключает модуль.",
     example='import math\nprint(math.sqrt(16))')
term("from", "std_import",
     brief="`from модуль import имя` подключает только нужное имя.",
     example='from math import pi\nprint(round(pi, 2))')
term("as", "std_import", auto=False,
     brief="Даёт модулю или имени другое имя при импорте.",
     example='import math as m\nprint(m.floor(2.7))')
term("match", "idiom_match", match=("case",),
     brief="Сопоставление с шаблоном: форма данных и разбор на части.",
     example=('p = (0, 5)\nmatch p:\n    case (0, y):\n'
              '        print("на оси Y:", y)'))
term(":=", "idiom_walrus",
     brief="Присваивание внутри выражения.",
     example='if (n := len("hello")) > 3:\n    print(n)')
term("first, *rest = xs", "idiom_unpack", match=("first, *rest",),
     brief="Звёздочка собирает «всё остальное» в список.",
     example='first, *rest = [1, 2, 3]\nprint(first, rest)')
term("is", "list_mutable", match=("is not",),
     brief="Один ли это объект, а не равны ли значения.",
     example='a = [1]\nb = [1]\nprint(a == b, a is b)')
term("assert", "test_assert",
     brief="Проверка: если условие ложно, выбрасывается AssertionError.",
     example='x = 5\nassert x > 0\nprint("проверка прошла")')
term("@", "deco_basics",
     brief="Применяет декоратор: `@deco` над `def f` значит `f = deco(f)`.",
     example=('def loud(f):\n    return lambda: f().upper()\n'
              '@loud\ndef hi(): return "hi"\nprint(hi())'))
term("...", "inh_abc", auto=False,
     brief="«Здесь ничего нет»: заглушка тела функции или класса.",
     example='def todo():\n    ...\nprint(todo())')
term("in", "list_basics", auto=False,
     brief="Проверка вхождения: подстрока в строке, элемент в списке, ключ в словаре.",
     example='print("от" in "кот")\nprint(3 in [1, 2])\nprint("a" in {"a": 1})')

# ---------------------------------------------- operators and literals
term("+", "ops_arith", auto=False,
     brief="Сложение чисел; строки и списки склеивает.",
     example='print(2 + 3, "ab" + "c")')
term("-", "ops_arith", auto=False,
     brief="Вычитание; у множеств это разность.",
     example='print(10 - 4)')
term("*", "ops_arith", auto=False,
     brief="Умножение; строку или список повторяет.",
     example='print(3 * 4, "ab" * 2)')
term("/", "ops_arith", auto=False,
     brief="Деление; результат всегда `float`.",
     example='print(7 / 2, 6 / 3)')
term("//", "ops_arith",
     brief="Деление нацело с округлением вниз.",
     example='print(7 // 2, -7 // 2)')
term("%", "ops_arith",
     brief="Остаток от деления.",
     example='print(7 % 2, 10 % 3)')
term("**", "ops_arith",
     brief="Возведение в степень.",
     example='print(2 ** 10, 9 ** 0.5)')
term("==", "ops_compare",
     brief="Равны ли значения; результат `True` или `False`.",
     example='print(2 + 2 == 4, "a" == "A")')
term("!=", "ops_compare",
     brief="Не равны ли значения.",
     example='print(3 != 4)')
term("<", "ops_compare",
     brief="Меньше; строки сравниваются по алфавиту.",
     example='print(2 < 3, "кот" < "кит")')
term(">", "ops_compare",
     brief="Больше.",
     example='print(5 > 3)')
term("<=", "ops_compare",
     brief="Меньше или равно.",
     example='print(3 <= 3)')
term(">=", "ops_compare",
     brief="Больше или равно.",
     example='print(2 >= 5)')
term("приоритет операторов", "ops_precedence", auto=False,
     brief="Что вычисляется раньше: `**`, потом `*` и `/`, потом `+` и `-`.",
     example='print(2 + 3 * 4 ** 2)\nprint((2 + 3) * 4)')
term("s[i]", "str_index",
     brief="Элемент по индексу; отрицательный индекс считает с конца.",
     example='s = "Python"\nprint(s[0], s[-1])')
term("s[a:b:c]", "str_index", match=("s[a:b]",),
     brief="Срез: с `a` до `b` (не включая) с шагом `c`.",
     example='s = "Python"\nprint(s[1:4], s[::-1])')
term("|", "set_ops", auto=False,
     brief="Объединение множеств: элементы из обоих.",
     example='print({1, 2} | {2, 3})')
term("&", "set_ops", auto=False,
     brief="Пересечение множеств: общие элементы.",
     example='print({1, 2} & {2, 3})')
term("^", "set_ops", auto=False,
     brief="Симметричная разность: элементы ровно одного из множеств.",
     example='print({1, 2} ^ {2, 3})')
term('f"{x}"', "str_fstring",
     brief="f-строка: подставляет значения выражений в фигурных скобках.",
     example='name = "Аня"\nprint(f"Привет, {name}!")')
term("{x:.2f}", "io_format",
     brief="Число с заданным количеством знаков после точки.",
     example='x = 3.14159\nprint(f"{x:.2f}")')
term("{n:>5}", "io_format",
     brief="Выравнивание значения по ширине в f-строке.",
     example='n = 42\nprint(f"[{n:>5}]", f"[{n:<5}]")')
term('r"..."', "data_re",
     brief="Сырая строка: обратная косая черта не экранирует.",
     example='print(r"a\\nb")\nprint(len(r"\\d"))')
term("\\n", "str_basics",
     brief="Перевод строки внутри строкового литерала.",
     example='print("раз\\nдва")')
term("\\t", "str_basics",
     brief="Табуляция внутри строкового литерала.",
     example='print("a\\tb")')
term("[x for x in xs]", "comp_list",
     brief="Списковое включение: новый список одной строкой.",
     example='print([x * x for x in range(4)])')
term("[x for x in xs if c]", "comp_cond",
     brief="Включение с фильтром: берёт только подходящие элементы.",
     example='xs = range(10)\nprint([x for x in xs if x > 6])')
term("{k: v for k in xs}", "comp_dict_set",
     brief="Словарь или множество одной строкой.",
     example='ws = ["a", "bb"]\nprint({w: len(w) for w in ws})')
term("(x for x in xs)", "comp_dict_set",
     brief="Генераторное выражение: значения считаются лениво.",
     example='g = (x * x for x in range(4))\nprint(sum(g))')
term("-> int", "typing_basics",
     brief="Аннотация типа результата; Python её не проверяет.",
     example='def f(x: int) -> int:\n    return x * 2\nprint(f(3))')
term("x: int", "typing_basics",
     brief="Аннотация типа переменной или параметра; Python её не проверяет.",
     example='x: int = "не число"\nprint(x)')
term("True", "types_basic", basic=True,
     brief="Истина: одно из двух значений типа `bool`.",
     example='print(3 > 2, type(True))')
term("False", "types_basic", basic=True,
     brief="Ложь: одно из двух значений типа `bool`.",
     example='print(3 < 2, False == 0)')

# --------------------------------------------------------------- methods
term("str.upper", "str_methods", match=(".upper",),
     brief="Новая строка заглавными буквами; исходная не меняется.",
     example='s = "кот"\nprint(s.upper(), s)')
term("str.lower", "str_methods", match=(".lower",),
     brief="Новая строка строчными буквами.",
     example='print("ПрИвЕт".lower())')
term("str.strip", "str_methods", match=(".strip",),
     brief="Убирает пробелы и переводы строки по краям.",
     example='s = "  hi \\n".strip()\nprint("[" + s + "]")')
term("str.replace", "str_methods", match=(".replace",),
     brief="Новая строка, где одна подстрока заменена другой.",
     example='print("мама".replace("м", "п"))')
term("str.split", "str_methods", match=(".split",),
     brief="Разрезает строку в список по разделителю.",
     example='print("a b  c".split())\nprint("1,2".split(","))')
term("str.join", "str_methods",
     brief="Склеивает список строк, вставляя между ними разделитель.",
     example='print("-".join(["a", "b", "c"]))')
term("str.find", "str_methods", match=(".find",),
     brief="Позиция подстроки или -1, если её нет.",
     example='print("кошка".find("шк"))\nprint("кот".find("я"))')
term("str.startswith", "str_methods", match=(".startswith",),
     brief="Начинается ли строка с данной подстроки.",
     example='print("python".startswith("py"))')
term("str.isdigit", "str_methods", match=(".isdigit",),
     brief="Состоит ли строка только из цифр.",
     example='print("123".isdigit())\nprint("1.5".isdigit())')
term("list.append", "list_methods", match=(".append",),
     brief="Добавляет элемент в конец списка; возвращает `None`.",
     example='xs = [1]\nxs.append(2)\nprint(xs)')
term("list.extend", "list_methods", match=(".extend",),
     brief="Добавляет в конец все элементы другой последовательности.",
     example='xs = [1]\nxs.extend([2, 3])\nprint(xs)')
term("list.insert", "list_methods", match=(".insert",),
     brief="Вставляет элемент на позицию; остальные сдвигаются.",
     example='xs = [1, 3]\nxs.insert(1, 2)\nprint(xs)')
term("list.remove", "list_methods",
     brief="Удаляет первый элемент с таким значением.",
     example='xs = [1, 2, 1]\nxs.remove(1)\nprint(xs)')
term("list.sort", "list_methods", match=(".sort",),
     brief="Сортирует список на месте; возвращает `None`.",
     example='xs = [3, 1, 2]\nxs.sort()\nprint(xs)')
term("list.reverse", "list_methods", match=(".reverse",),
     brief="Разворачивает список на месте.",
     example='xs = [1, 2, 3]\nxs.reverse()\nprint(xs)')
term("list.index", "list_methods",
     brief="Позиция первого элемента с таким значением.",
     example='xs = ["a", "b", "c"]\nprint(xs.index("b"))')
term("list.copy", "list_mutable", auto=False,
     brief="Поверхностная копия списка.",
     example='a = [1, 2]\nb = a.copy()\nb.append(3)\nprint(a, b)')
term("a[:]", "list_mutable",
     brief="Срез без границ: поверхностная копия списка.",
     example='a = [1, 2]\nb = a[:]\nprint(a == b, a is b)')
term("dict.get", "dict_methods", match=(".get",),
     brief="Значение по ключу; если ключа нет, значение по умолчанию без KeyError.",
     example='d = {"чай": 3}\nprint(d.get("сок", 0))')
term("dict.items", "dict_methods", match=(".items",),
     brief="Пары (ключ, значение) для перебора словаря.",
     example='d = {"a": 1, "b": 2}\nfor k, v in d.items():\n    print(k, v)')
term("dict.keys", "dict_methods", match=(".keys",),
     brief="Ключи словаря.",
     example='d = {"a": 1, "b": 2}\nprint(list(d.keys()))')
term("dict.values", "dict_methods", match=(".values",),
     brief="Значения словаря.",
     example='d = {"a": 1, "b": 2}\nprint(sum(d.values()))')
term("dict.update", "dict_methods",
     brief="Дописывает в словарь пары из другого словаря.",
     example='d = {"a": 1}\nd.update({"b": 2})\nprint(d)')
term("dict.setdefault", "dict_methods", match=(".setdefault",),
     brief="Записывает значение, только если ключа ещё нет, и возвращает его.",
     example='d = {}\nd.setdefault("x", []).append(1)\nprint(d)')
term("list.pop", "list_methods",
     brief="Удаляет и возвращает элемент списка, по умолчанию последний.",
     example='xs = [1, 2, 3]\nprint(xs.pop(), xs)')
term("dict.pop", "dict_methods",
     brief="Удаляет ключ и возвращает его значение.",
     example='d = {"a": 1}\nprint(d.pop("a"), d)')
term("list.count", "list_methods",
     brief="Сколько раз значение встречается в списке.",
     example='print([1, 2, 1].count(1))')
term("str.count", "str_methods",
     brief="Сколько раз подстрока встречается в строке.",
     example='print("банан".count("а"))')
term("set.add", "set_basics", match=(".add",),
     brief="Добавляет элемент во множество; повтор не добавится.",
     example='s = {1}\ns.add(2)\ns.add(2)\nprint(s)')
term("set.discard", "set_basics", match=(".discard",),
     brief="Удаляет элемент, если он есть; без ошибки, если нет.",
     example='s = {1, 2}\ns.discard(5)\nprint(s)')
term("generator.send", "gen_yield", match=(".send",),
     brief="Передаёт значение внутрь генератора, в место `yield`.",
     example=('def g():\n    x = yield\n    yield x * 2\n'
              'it = g(); next(it)\nprint(it.send(5))'))
term("generator.close", "gen_yield", auto=False,
     brief="Останавливает генератор.",
     example='g = (x for x in range(3))\ng.close()\nprint(list(g))')
term("file.read", "files_read", match=(".read",),
     brief="Читает весь файл одной строкой.",
     example='with open("a.txt", "w") as f:\n    f.write("раз\\nдва")\nprint(open("a.txt").read())')
term("file.readline", "files_read", match=(".readline",),
     brief="Читает одну строку файла вместе с `\\n`.",
     example='with open("a.txt", "w") as f:\n    f.write("раз\\nдва")\nprint(open("a.txt").readline())')
term("file.readlines", "files_read", match=(".readlines",),
     brief="Читает файл в список строк.",
     example='with open("a.txt", "w") as f:\n    f.write("1\\n2")\nprint(open("a.txt").readlines())')
term("file.write", "files_read", match=(".write",),
     brief="Записывает строку в файл; перевод строки не добавляет.",
     example='with open("a.txt", "w") as f:\n    f.write("hi")\nprint(open("a.txt").read())')
term("__init__", "oop_class",
     brief="Настраивает только что созданный объект.",
     example=('class P:\n    def __init__(self, x):\n'
              '        self.x = x\nprint(P(3).x)'))
term("__init__.py", "proj_modules",
     brief="Файл, который делает папку пакетом; выполняется при импорте пакета.")
term("__debug__", "test_debug",
     brief="`True` при обычном запуске, `False` с флагом `python -O`: тогда `assert` пропускаются.",
     example='print(__debug__)')
term("__str__", "dunder_str",
     brief="Текст объекта для людей: его показывают `print` и `str`.",
     example=('class P:\n    def __str__(self):\n'
              '        return "точка"\nprint(P())'))
term("__repr__", "dunder_str",
     brief="Текст объекта для отладки: его показывают `repr` и списки.",
     example=('class P:\n    def __repr__(self):\n'
              '        return "P()"\nprint([P()])'))
term("__eq__", "dunder_ops",
     brief="Как объект сравнивается через `==`.",
     example=('class A:\n    def __eq__(self, o):\n'
              '        return True\nprint(A() == 5)'))
term("__lt__", "dunder_ops",
     brief="Как объект сравнивается через `<`; нужен для `sorted`.",
     example=('class A:\n    def __init__(s, v): s.v = v\n'
              '    def __lt__(s, o):\n        return s.v < o.v\n'
              'print(A(1) < A(2))'))
term("__add__", "dunder_ops",
     brief="Как объект складывается через `+`.",
     example=('class V:\n    def __add__(self, o):\n'
              '        return "сумма"\nprint(V() + V())'))
term("__hash__", "dunder_ops",
     brief="Отпечаток объекта для `set` и ключей `dict`.",
     example=('class A:\n    def __hash__(self):\n'
              '        return 7\nprint(hash(A()))'))
term("__len__", "dunder_protocols",
     brief="Что вернёт `len()` для объекта.",
     example=('class Box:\n    def __len__(self):\n'
              '        return 3\nprint(len(Box()))'))
term("__getitem__", "dunder_protocols",
     brief="Доступ по индексу или ключу: `obj[i]`.",
     example=('class Sq:\n    def __getitem__(self, i):\n'
              '        return i * i\nprint(Sq()[4])'))
term("__contains__", "dunder_protocols",
     brief="Что вернёт проверка `x in obj`.",
     example=('class Even:\n    def __contains__(s, n):\n'
              '        return n % 2 == 0\nprint(4 in Even())'))
term("__call__", "dunder_protocols",
     brief="Позволяет вызывать объект как функцию: `obj()`.",
     example=('class Hi:\n    def __call__(self):\n'
              '        return "привет"\nprint(Hi()())'))
term("__bool__", "dunder_protocols",
     brief="Истинность объекта в `if` и `bool()`.",
     example=('class Empty:\n    def __bool__(self):\n'
              '        return False\nprint(bool(Empty()))'))
term("__iter__", "gen_iter",
     brief="Возвращает итератор: так объект работает в `for`.",
     example=('class Two:\n    def __iter__(self):\n'
              '        return iter([1, 2])\nprint(list(Two()))'))
term("__next__", "gen_iter",
     brief="Следующее значение итератора или StopIteration.",
     example='it = iter("ab")\nprint(it.__next__())')
term("__enter__", "ctx_protocol",
     brief="Вход в блок `with`; результат попадает в имя после `as`.",
     example=('class C:\n    def __enter__(s): return 1\n'
              '    def __exit__(self, *a): pass\n'
              'with C() as x:\n    print(x)'))
term("__exit__", "ctx_protocol",
     brief="Выход из блока `with`, даже если случилась ошибка.",
     example=('class C:\n    def __enter__(self): pass\n'
              '    def __exit__(self, *a):\n        print("выход")\n'
              'with C():\n    print("внутри")'))
term("__slots__", "prop_private",
     brief="Фиксированный набор атрибутов: меньше памяти, лишние нельзя.",
     example=('class P:\n    __slots__ = ("x",)\np = P()\n'
              'try: p.y = 1\nexcept AttributeError:\n    print("нельзя")'))
term("__post_init__", "dc_basics",
     brief="Проверки после автоматического `__init__` у dataclass.",
     example=('from dataclasses import *\n@dataclass\n'
              'class P:\n    x: int\n    def __post_init__(s):\n'
              '        s.x = abs(s.x)\nprint(P(-3))'))
term("__mro__", "inh_mro", match=("MRO",),
     brief="Порядок поиска методов при наследовании.",
     example='print(bool.__mro__)')
term("__match_args__", "idiom_match",
     brief="Позиционные поля для шаблона `case Класс(a, b)`.",
     example=('class P:\n    __match_args__ = ("x",)\n'
              '    def __init__(s, x): s.x = x\n'
              'match P(5):\n    case P(n): print(n)'))
term('__name__ == "__main__"', "proj_modules", match=("__name__",),
     brief="Код, который выполняется только при запуске файла, а не при импорте.",
     example='if __name__ == "__main__":\n    print("запущен напрямую")')

# ------------------------------------------------------- standard library
term("json", "data_json",
     brief="Модуль для перевода данных Python в текст JSON и обратно.",
     example='import json\nprint(json.dumps([1, None]))')
term("json.dumps", "data_json",
     brief="Превращает данные Python в строку JSON.",
     example='import json\nprint(json.dumps({"a": True}))')
term("json.loads", "data_json",
     brief="Превращает строку JSON в данные Python.",
     example='import json\nprint(json.loads("[1, 2]"))')
term("json.dump", "data_json",
     brief="Записывает данные Python в файл как JSON.",
     example=('import json\nwith open("d.json", "w") as f:\n'
              '    json.dump([1, 2], f)\nprint(open("d.json").read())'))
term("json.load", "data_json",
     brief="Читает JSON из открытого файла.",
     example=('import json\nwith open("d.json", "w") as f:\n'
              '    f.write("[1, 2]")\nprint(json.load(open("d.json")))'))
term("JSONDecodeError", "data_json", match=("json.JSONDecodeError",),
     brief="Текст не является правильным JSON.",
     example=('import json\ntry: json.loads("{a}")\n'
              'except json.JSONDecodeError:\n    print("не JSON")'))
term("re", "data_re",
     brief="Модуль регулярных выражений: поиск и замена по шаблону.",
     example='import re\ns = "a1b22"\nprint(re.findall(r"\\d+", s))')
term("re.search", "data_re",
     brief="Первое совпадение с шаблоном в любом месте строки или None.",
     example='import re\nm = re.search(r"\\d+", "a12b")\nprint(m.group())')
term("re.findall", "data_re",
     brief="Список всех совпадений с шаблоном.",
     example='import re\ns = "a1b2"\nprint(re.findall(r"[a-z]", s))')
term("re.sub", "data_re",
     brief="Заменяет все совпадения с шаблоном.",
     example='import re\ns = "a   b"\nprint(re.sub(r"\\s+", " ", s))')
term("re.match", "data_re",
     brief="Совпадение с шаблоном только в начале строки.",
     example='import re\nprint(re.match(r"\\d", "a1"))')
term("re.fullmatch", "data_re",
     brief="Совпадает ли с шаблоном вся строка целиком.",
     example='import re\nm = re.fullmatch(r"\\d+", "123")\nprint(m is not None)')
term("re.compile", "data_re",
     brief="Готовит шаблон заранее, чтобы применять его много раз.",
     example='import re\np = re.compile(r"\\d")\nprint(p.findall("a1b2"))')
term("datetime", "data_datetime", match=("datetime.datetime",),
     brief="Дата и время вместе; модуль с тем же именем.",
     example=('from datetime import datetime\n'
              'd = datetime(2024, 5, 1, 9, 30)\nprint(d)'))
term("date", "data_datetime", match=("datetime.date",),
     brief="Дата без времени: год, месяц, день.",
     example='from datetime import date\nd = date(2024, 3, 8)\nprint(d, d.weekday())')
term("timedelta", "data_datetime", match=("datetime.timedelta",),
     brief="Промежуток времени; его прибавляют к дате.",
     example=('from datetime import *\n'
              'd = date(2024, 2, 28)\nprint(d + timedelta(days=1))'))
term("strftime", "data_datetime", match=(".strftime",),
     brief="Дата в строку по формату: `%d.%m.%Y`.",
     example=('from datetime import date\n'
              'd = date(2024, 3, 8)\nprint(d.strftime("%d.%m.%Y"))'))
term("strptime", "data_datetime", match=(".strptime",),
     brief="Строка в дату по формату.",
     example=('from datetime import datetime\n'
              's = "08.03.2024"\nf = "%d.%m.%Y"\n'
              'd = datetime.strptime(s, f)\nprint(d.month)'))
term("math", "std_import",
     brief="Математические функции и константы: `sqrt`, `pi`, `floor`.",
     example='import math\nprint(math.sqrt(2), math.pi)')
term("statistics", "std_import",
     brief="Среднее, медиана и другая статистика.",
     example='import statistics as st\nprint(st.mean([1, 2, 6]))')
term("Counter", "std_collections", match=("collections.Counter",),
     brief="Словарь-счётчик: сколько раз встретился каждый элемент.",
     example='from collections import Counter\nprint(Counter("абба"))')
term("defaultdict", "std_collections", match=("collections.defaultdict",),
     brief="Словарь, который сам создаёт значение для нового ключа.",
     example=('from collections import *\nd = defaultdict(list)\n'
              'd["a"].append(1)\nprint(dict(d))'))
term("deque", "std_deque", match=("collections.deque",),
     brief="Очередь с быстрым добавлением и удалением с обоих концов.",
     example=('from collections import deque\nq = deque([1, 2])\n'
              'q.appendleft(0)\nprint(list(q))'))
term("namedtuple", "std_deque", match=("collections.namedtuple",),
     brief="Кортеж с именованными полями.",
     example=('from collections import *\nP = namedtuple("P", "x y")\n'
              'print(P(1, 2).y)'))
term("OrderedDict", "std_collections", match=("collections.OrderedDict",),
     brief="Словарь с методами для управления порядком ключей.",
     example=('from collections import *\nd = OrderedDict(a=1, b=2)\n'
              'd.move_to_end("a")\nprint(list(d))'))
term("ChainMap", "std_collections", match=("collections.ChainMap",),
     brief="Несколько словарей как один: ищет ключ по очереди.",
     example=('from collections import *\n'
              'c = ChainMap({"a": 1}, {"a": 2})\nprint(c["a"])'))
term("itertools", "std_itertools",
     brief="Модуль для комбинаций и цепочек последовательностей.",
     example='import itertools as it\nprint(list(it.chain("ab", "c")))')
term("itertools.chain", "std_itertools", match=("chain",),
     brief="Перебирает несколько последовательностей одну за другой.",
     example='from itertools import chain\nprint(list(chain([1], [2, 3])))')
term("itertools.product", "std_itertools",
     brief="Все пары и наборы из нескольких последовательностей.",
     example='from itertools import product\nprint(list(product("ab", "12")))')
term("itertools.combinations", "std_itertools", match=("combinations",),
     brief="Все наборы по k элементов без учёта порядка.",
     example=('from itertools import *\n'
              'c = combinations("abc", 2)\nprint(list(c))'))
term("itertools.permutations", "std_itertools", match=("permutations",),
     brief="Все перестановки элементов.",
     example=('from itertools import *\n'
              'p = permutations("abc")\nprint(len(list(p)))'))
term("itertools.groupby", "std_itertools", match=("groupby",),
     brief="Группирует подряд идущие элементы с одинаковым ключом.",
     example=('from itertools import groupby\n'
              'for k, g in groupby("aabccc"):\n    print(k, len(list(g)))'))
term("itertools.accumulate", "std_itertools", match=("accumulate",),
     brief="Накопленные суммы или другие накопленные результаты.",
     example=('from itertools import *\n'
              'a = accumulate([1, 2, 3])\nprint(list(a))'))
term("itertools.islice", "gen_lazy", match=("islice",),
     brief="Берёт часть потока, даже бесконечного.",
     example=('from itertools import *\n'
              'print(list(islice(count(), 3)))'))
term("itertools.batched", "gen_lazy", match=("batched",),
     brief="Режет поток на пачки по n элементов.",
     example=('from itertools import batched\n'
              'print(list(batched("abcde", 2)))'))
term("functools.reduce", "fn_functools", match=("reduce",),
     brief="Сворачивает последовательность в одно значение.",
     example=('from functools import reduce\n'
              'f = lambda a, b: a * b\nprint(reduce(f, [1, 2, 3, 4]))'))
term("functools.partial", "fn_functools", match=("partial",),
     brief="Новая функция с частично зафиксированными аргументами.",
     example=('from functools import partial\n'
              'bin2 = partial(int, base=2)\nprint(bin2("101"))'))
term("@lru_cache", "rec_memo", match=("lru_cache", "functools.lru_cache"),
     brief="Запоминает результаты вызовов функции.",
     example=('from functools import lru_cache\n@lru_cache\n'
              'def fib(n):\n    return n if n < 2 else \\\n'
              '        fib(n - 1) + fib(n - 2)\nprint(fib(50))'))
term("@cache", "rec_memo", match=("functools.cache",),
     brief="Запоминает все результаты вызовов функции без ограничения.",
     example=('from functools import cache\n@cache\n'
              'def sq(n):\n    print("считаю")\n    return n * n\n'
              'print(sq(4), sq(4))'))
term("@wraps", "deco_basics", match=("wraps", "functools.wraps"),
     brief="Переносит имя и docstring функции на обёртку.",
     example=('from functools import wraps\ndef deco(f):\n'
              '    @wraps(f)\n    def w(): return f()\n    return w\n'
              '@deco\ndef hi(): pass\nprint(hi.__name__)'))
term("@total_ordering", "dunder_ops", match=("total_ordering",),
     brief="Достраивает все сравнения по `==` и `<`.",
     example=('from functools import *\n@total_ordering\n'
              'class A:\n    def __init__(s, v): s.v = v\n'
              '    def __eq__(s, o):\n        return s.v == o.v\n'
              '    def __lt__(s, o):\n        return s.v < o.v\n'
              'print(A(3) >= A(2))'))
term("@property", "prop_property", match=("property",),
     brief="Метод, который читается как атрибут.",
     example=('class C:\n    @property\n'
              '    def area(self): return 4\nprint(C().area)'))
term("@x.setter", "prop_property", match=(".setter",),
     brief="Метод, который срабатывает при присваивании свойству.",
     example=('class C:\n    @property\n    def x(s): return s._x\n'
              '    @x.setter\n    def x(s, v): s._x = abs(v)\n'
              'c = C(); c.x = -5\nprint(c.x)'))
term("@cached_property", "prop_property", match=("cached_property",),
     brief="Свойство, которое вычисляется один раз и запоминается.",
     example=('from functools import *\nclass C:\n'
              '    @cached_property\n    def v(self):\n'
              '        print("считаю")\n        return 1\n'
              'c = C()\nprint(c.v, c.v)'))
term("@classmethod", "prop_classmethod", match=("classmethod",),
     brief="Метод класса: получает класс `cls`, а не объект.",
     example=('class P:\n    def __init__(s, x): s.x = x\n'
              '    @classmethod\n    def zero(cls):\n'
              '        return cls(0)\nprint(P.zero().x)'))
term("@staticmethod", "prop_classmethod", match=("staticmethod",),
     brief="Обычная функция внутри класса, без `self` и `cls`.",
     example=('class M:\n    @staticmethod\n'
              '    def add(a, b): return a + b\nprint(M.add(2, 3))'))
term("pathlib", "files_pathlib",
     brief="Модуль, где путь к файлу является объектом.",
     example='import pathlib\np = pathlib.Path("a/b.txt")\nprint(p.name)')
term("Path", "files_pathlib", match=("pathlib.Path",),
     brief="Путь к файлу как объект: части пути, чтение, запись.",
     example=('from pathlib import Path\np = Path("dir/note.txt")\n'
              'print(p.suffix, p.parent)'))
term("csv", "files_csv",
     brief="Модуль для чтения и записи таблиц CSV.",
     example=('import csv\nlines = ["a,b", "1,2"]\n'
              'print(list(csv.reader(lines)))'))
term("csv.DictReader", "files_csv", match=("DictReader",),
     brief="Читает CSV в словари: ключи берутся из первой строки.",
     example=('import csv\nlines = ["a,b", "1,2"]\n'
              'r = csv.DictReader(lines)\nprint(next(r))'))
term("csv.writer", "files_csv",
     brief="Записывает строки таблицы в CSV-файл.",
     example=('import csv\nwith open("t.csv", "w") as f:\n'
              '    w = csv.writer(f)\n    w.writerow([1, 2])\n'
              'print(open("t.csv").read())'))
term("@dataclass", "dc_basics", match=("dataclass", "dataclasses"),
     brief="Класс данных: `__init__`, `__repr__`, `__eq__` пишутся сами.",
     example=('from dataclasses import *\n@dataclass\n'
              'class P:\n    x: int\n    y: int = 0\nprint(P(1))'))
term("dataclasses.field", "dc_basics",
     brief="Настройка поля dataclass, например `default_factory=list`.",
     example=('from dataclasses import *\n@dataclass\n'
              'class Bag:\n    xs: list = field(\n'
              '        default_factory=list)\nprint(Bag())'))
term("dataclasses.asdict", "dc_basics", match=("asdict",),
     brief="Превращает объект dataclass в словарь.",
     example=('from dataclasses import *\n@dataclass\n'
              'class P:\n    x: int\nprint(asdict(P(1)))'))
term("dataclasses.replace", "dc_basics",
     brief="Копия объекта dataclass с изменёнными полями.",
     example=('from dataclasses import *\n@dataclass\n'
              'class P:\n    x: int\n    y: int\n'
              'print(replace(P(1, 2), y=5))'))
term("Enum", "dc_enum", match=("enum.Enum", "enum"),
     brief="Набор именованных констант.",
     example=('from enum import Enum\nclass C(Enum):\n'
              '    RED = 1\nprint(C.RED, C.RED.value)'))
term("enum.auto", "dc_enum", match=("auto()",),
     brief="Номер для константы Enum выбирается автоматически.",
     example=('from enum import Enum, auto\nclass C(Enum):\n'
              '    A = auto()\n    B = auto()\nprint(C.B.value)'))
term("ABC", "inh_abc", match=("abc.ABC",),
     brief="Класс-интерфейс, который нельзя создать напрямую.",
     example=('from abc import *\nclass Shape(ABC):\n'
              '    @abstractmethod\n    def area(self): ...\n'
              'try: Shape()\nexcept TypeError:\n    print("нельзя")'))
term("@abstractmethod", "inh_abc", match=("abstractmethod",),
     brief="Метод, который обязан написать каждый потомок.",
     example=('from abc import *\nclass S(ABC):\n'
              '    @abstractmethod\n    def f(self): ...\n'
              'class T(S):\n    def f(self): return 1\nprint(T().f())'))
term("Protocol", "typing_advanced", match=("typing.Protocol",),
     brief="Интерфейс по форме: подходит любой класс с нужными методами.",
     example=('from typing import Protocol\n'
              'class Named(Protocol):\n    name: str\n'
              'print(Named.__name__)'))
term("TypedDict", "typing_typeddict", match=("typing.TypedDict",),
     brief="Словарь с известными ключами и типами значений.",
     example=('from typing import TypedDict\n'
              'class U(TypedDict):\n    name: str\n'
              'print(U(name="Аня"))'))
term("Literal", "typing_typeddict", match=("typing.Literal",),
     brief="Тип, допускающий только перечисленные значения.",
     example=('from typing import Literal\n'
              'Mode = Literal["r", "w"]\nprint(Mode)'))
term("@runtime_checkable", "typing_advanced", match=("runtime_checkable",),
     brief="Разрешает проверять Protocol через `isinstance`.",
     example=('from typing import *\n@runtime_checkable\n'
              'class Sized2(Protocol):\n'
              '    def __len__(self): ...\n'
              'print(isinstance("ab", Sized2))'))
term("Callable", "typing_basics", match=("typing.Callable",),
     brief="Тип функции: `Callable[[int], str]`.",
     example=('from typing import Callable\n'
              'def run(f: Callable[[], int]):\n'
              '    return f()\nprint(run(lambda: 7))'))
term("Optional", "typing_basics", match=("typing.Optional",),
     brief="`Optional[int]` значит «`int` или None».",
     example=('from typing import Optional\n'
              'def f(x: Optional[int] = None):\n'
              '    return x or 0\nprint(f())'))
term("int | None", "typing_basics",
     brief="Значение типа `int` или None; короткая запись `Optional[int]`.",
     example='def f(x: int | None = None):\n    return x is None\nprint(f())')
term("@contextmanager", "ctx_contextlib", match=("contextmanager", "contextlib.contextmanager"),
     brief="Контекстный менеджер из функции-генератора.",
     example=('from contextlib import *\n@contextmanager\n'
              'def tag():\n    print("<b>")\n    yield\n'
              '    print("</b>")\nwith tag():\n    print("текст")'))
term("suppress", "ctx_contextlib", match=("contextlib.suppress",),
     brief="Блок `with`, который молча пропускает указанные ошибки.",
     example=('from contextlib import suppress\n'
              'with suppress(ValueError):\n    int("x")\nprint("дальше")'))
term("redirect_stdout", "ctx_contextlib", match=("contextlib.redirect_stdout",),
     brief="Перенаправляет вывод `print` в другой поток, например в строку.",
     example=('import io, contextlib as c\nbuf = io.StringIO()\n'
              'with c.redirect_stdout(buf):\n    print("тихо")\n'
              'print(buf.getvalue().upper())'))
term("ExitStack", "ctx_contextlib", match=("contextlib.ExitStack",),
     brief="Объединяет любое число контекстных менеджеров в один `with`.",
     example=('from contextlib import ExitStack\n'
              'with ExitStack() as st:\n'
              '    st.callback(print, "выход")\n    print("внутри")'))
term("unittest", "test_unittest",
     brief="Встроенный модуль для тестов: классы `TestCase` и проверки.",
     example='import unittest as u\nprint(u.TestCase.__name__)')
term("TestCase", "test_unittest", match=("unittest.TestCase",),
     brief="Класс, методы `test_...` которого становятся тестами.",
     example=('import unittest\nclass T(unittest.TestCase):\n'
              '    def test_ok(self):\n        self.assertEqual(1, 1)\n'
              'r = T("test_ok").run()\nprint(r.wasSuccessful())'))
term("assertEqual", "test_unittest", match=(".assertEqual",),
     brief="Проверка в TestCase: два значения равны.",
     example=('import unittest\nt = unittest.TestCase()\n'
              't.assertEqual(2 + 2, 4)\nprint("равно")'))
term("Mock", "test_unittest", match=("unittest.mock.Mock", "MagicMock"),
     brief="Объект-заглушка: принимает любые вызовы и запоминает их.",
     example=('from unittest.mock import Mock\nm = Mock(return_value=5)\n'
              'print(m(1), m.call_count)'))
term("patch", "test_unittest", match=("unittest.mock.patch", "@patch"),
     brief="Временно подменяет объект заглушкой на время теста.",
     example=('from unittest.mock import patch\nimport math\n'
              'with patch("math.pi", 3):\n    print(math.pi)'))
term("pytest", "test_assert",
     brief="Популярная библиотека тестов: тест это функция с `assert`.")
term("doctest", "test_assert",
     brief="Проверяет примеры из docstring, сравнивая вывод.",
     example=('import doctest\ndef sq(x):\n    """\n    >>> sq(3)\n'
              '    9\n    """\n    return x * x\n'
              'doctest.run_docstring_examples(\n'
              '    sq, globals(), verbose=True)'))
term("logging", "test_logging",
     brief="Сообщения с уровнем важности вместо `print`.",
     example='import logging as lg\nprint(lg.WARNING, lg.INFO)')
term("logging.getLogger", "test_logging", match=("getLogger",),
     brief="Логгер с именем, обычно `__name__` модуля.",
     example='import logging\nlog = logging.getLogger("app")\nprint(log.name)')
term("logging.basicConfig", "test_logging", match=("basicConfig",),
     brief="Настраивает уровень и формат сообщений всего приложения.",
     example=('import logging, sys\nlogging.basicConfig(\n'
              '    stream=sys.stdout,\n'
              '    format="%(levelname)s: %(message)s",\n'
              '    force=True)\n'
              'logging.warning("осторожно")'))
term("argparse", "proj_cli_logging",
     brief="Модуль для разбора аргументов командной строки.",
     example=('import argparse\np = argparse.ArgumentParser()\n'
              'p.add_argument("n", type=int)\nprint(p.parse_args(["5"]).n)'))
term("ArgumentParser", "proj_cli_logging", match=("argparse.ArgumentParser",),
     brief="Описывает аргументы программы и разбирает их.",
     example=('from argparse import *\np = ArgumentParser()\n'
              'p.add_argument("--n", type=int)\n'
              'a = p.parse_args(["--n", "3"])\nprint(a)'))
term("sys.argv", "proj_structure",
     brief="Список аргументов запуска; первый элемент это имя файла.")
term("sys.exit", "proj_structure",
     brief="Завершает программу с кодом выхода; 0 значит успех.",
     example='import sys\nprint("пока")\nsys.exit(0)')
term("sys.path", "proj_modules",
     brief="Список папок, в которых `import` ищет модули; первой идёт папка запущенного файла.",
     example='import sys\nprint(type(sys.path).__name__)')
term("sys.modules", "proj_modules",
     brief="Словарь уже загруженных модулей: повторный `import` берёт модуль отсюда.",
     example='import sys, json\nprint("json" in sys.modules)')
term("pdb", "test_debug",
     brief="Встроенный отладчик: пошаговое выполнение и просмотр переменных.")
term("traceback", "exc_traceback",
     brief="Модуль для работы с трассировкой ошибки.")
term("traceback.print_exc", "test_debug", match=("print_exc", "traceback.format_exc", "format_exc"),
     brief="Печатает (или возвращает строкой) трассировку текущей ошибки, не останавливая программу.",
     example=('import sys, traceback\ntry:\n    1 / 0\nexcept ZeroDivisionError:\n'
              '    t = traceback.format_exc()\nprint(t.splitlines()[-1])'))
term("asyncio.run", "async_basics",
     brief="Запускает корутину и цикл событий.",
     example=('import asyncio\nasync def main():\n'
              '    return 42\nprint(asyncio.run(main()))'))
term("asyncio.sleep", "async_basics",
     brief="Пауза, во время которой выполняются другие задачи.",
     example=('import asyncio\nasync def main():\n'
              '    await asyncio.sleep(0.01)\n    print("проснулся")\n'
              'asyncio.run(main())'))
term("asyncio.gather", "async_tasks", match=("gather",),
     brief="Запускает несколько корутин одновременно и собирает результаты.",
     example=('import asyncio\nasync def sq(x): return x * x\n'
              'async def main():\n'
              '    return await asyncio.gather(\n        sq(2), sq(3))\n'
              'print(asyncio.run(main()))'))
term("asyncio.create_task", "async_tasks", match=("create_task", ".create_task"),
     brief="Запускает корутину в фоне как задачу.",
     example=('import asyncio\nasync def main():\n'
              '    t = asyncio.create_task(\n        asyncio.sleep(0, "ок"))\n'
              '    print(await t)\nasyncio.run(main())'))
term("asyncio.TaskGroup", "async_tasks", match=("TaskGroup",),
     brief="Группа задач: блок ждёт их все и отменяет при ошибке.",
     example=('import asyncio\nasync def main():\n'
              '    tg = asyncio.TaskGroup()\n    async with tg:\n'
              '        t = tg.create_task(\n            asyncio.sleep(0, 1))\n'
              '    print(t.result())\nasyncio.run(main())'))
term("asyncio.wait_for", "async_timeouts", match=("wait_for",),
     brief="Ждёт корутину не дольше заданного времени.",
     example=('import asyncio\nasync def main():\n    try:\n'
              '        c = asyncio.sleep(1)\n'
              '        await asyncio.wait_for(\n'
              '            c, timeout=0.01)\n'
              '    except TimeoutError:\n        print("не дождались")\n'
              'asyncio.run(main())'))
term("asyncio.timeout", "async_timeouts",
     brief="Блок `async with` с ограничением времени.",
     example=('import asyncio\nasync def main():\n    try:\n'
              '        t = asyncio.timeout(0.1)\n'
              '        async with t:\n'
              '          await asyncio.sleep(1)\n'
              '    except TimeoutError:\n        print("время вышло")\n'
              'asyncio.run(main())'))
term("threading", "conc_threads",
     brief="Модуль для запуска кода в нескольких потоках.",
     example='import threading as th\nt = th.current_thread()\nprint(t.name)')
term("Thread", "conc_threads", match=("threading.Thread",),
     brief="Поток: функция, которая выполняется параллельно с основной программой.",
     example=('from threading import Thread\n'
              'def work(): print("поток")\n'
              't = Thread(target=work)\nt.start(); t.join()'))
term("Lock", "conc_lock", match=("threading.Lock",),
     brief="Замок: только один поток за раз выполняет защищённый блок.",
     example=('from threading import Lock\nlock = Lock()\n'
              'with lock:\n    print(lock.locked())'))
term("GIL", "conc_threads",
     brief="Блокировка интерпретатора: байт-код выполняет один поток за раз.")
term("queue.Queue", "conc_queue", match=("Queue",),
     brief="Потокобезопасная очередь для передачи данных между потоками.",
     example='import queue\nq = queue.Queue()\nq.put(1)\nprint(q.get())')
term("ThreadPoolExecutor", "conc_pool", match=("concurrent.futures.ThreadPoolExecutor",),
     brief="Пул потоков: раздаёт задачи нескольким потокам.",
     example=('from concurrent.futures import *\n'
              'with ThreadPoolExecutor() as ex:\n'
              '    r = ex.map(abs, [-1, -2])\n    print(list(r))'))
term("ProcessPoolExecutor", "conc_processes", match=("concurrent.futures.ProcessPoolExecutor",),
     brief="Пул процессов: вычисления на нескольких ядрах процессора.")
term("multiprocessing", "conc_processes",
     brief="Модуль для запуска кода в отдельных процессах.",
     example='import multiprocessing as mp\nprint(mp.cpu_count() > 0)')
term("heapq", "algo_patterns",
     brief="Куча: быстрый доступ к наименьшему элементу.",
     example=('import heapq\nh = [5, 1, 3]\nheapq.heapify(h)\n'
              'print(heapq.heappop(h))'))
term("bisect", "algo_search_sort",
     brief="Бинарный поиск места в отсортированном списке.",
     example='import bisect\nxs = [1, 3, 5]\nprint(bisect.bisect(xs, 4))')
term("time.perf_counter", "perf_measure", match=("perf_counter",),
     brief="Точные часы для замера, сколько длится код.",
     example=('import time\nt = time.perf_counter()\nsum(range(1000))\n'
              'print(time.perf_counter() >= t)'))
term("timeit", "perf_measure",
     brief="Многократно запускает код и измеряет время.",
     example=('import timeit\n'
              't = timeit.timeit("1+1",\n    number=10)\nprint(t >= 0)'))
term("cProfile", "perf_measure",
     brief="Профилировщик: показывает, какие функции работают дольше всего.")
term("sys.getsizeof", "perf_tricks", match=("getsizeof",),
     brief="Размер объекта в байтах без вложенных объектов.",
     example=('import sys\na = sys.getsizeof([])\n'
              'print(sys.getsizeof([1, 2]) > a)'))

# ------------------------------------------------------------ exceptions
term("ValueError", "exc_types",
     brief="Неподходящее значение верного типа: `int(\"abc\")`.",
     example='try: int("abc")\nexcept ValueError as e:\n    print(e)')
term("TypeError", "exc_types",
     brief="Операция с неподходящим типом: `\"1\" + 1`.",
     example='try: "1" + 1\nexcept TypeError as e:\n    print(e)')
term("KeyError", "exc_types",
     brief="В словаре нет такого ключа.",
     example='try: {"a": 1}["b"]\nexcept KeyError as e:\n    print("нет ключа", e)')
term("IndexError", "exc_types",
     brief="Индекс за пределами списка или строки.",
     example='try: [1, 2][5]\nexcept IndexError as e:\n    print(e)')
term("NameError", "exc_types",
     brief="Имя не определено: опечатка или переменная ещё не создана.",
     example='try: print(nme)\nexcept NameError as e:\n    print(e)')
term("AttributeError", "exc_types",
     brief="У объекта нет такого атрибута или метода.",
     example='try: (5).upper()\nexcept AttributeError as e:\n    print(e)')
term("ZeroDivisionError", "exc_types",
     brief="Деление на ноль.",
     example='try: 1 / 0\nexcept ZeroDivisionError as e:\n    print(e)')
term("FileNotFoundError", "exc_types",
     brief="Файла с таким именем нет.",
     example='try: open("nope.txt")\nexcept FileNotFoundError:\n    print("нет файла")')
term("UnicodeDecodeError", "files_bytes",
     brief="Байты не читаются в указанной кодировке: файл записан в другой.",
     example=('try: b"\\xff".decode("utf-8")\n'
              'except UnicodeDecodeError as e:\n    print(e.reason)'))
term("Exception", "exc_types",
     brief="Общий предок почти всех ошибок; `except Exception` ловит их все.",
     example='try: 1 / 0\nexcept Exception as e:\n    print(type(e).__name__)')
term("ExceptionGroup", "exc_types",
     brief="Несколько ошибок сразу в одном исключении.",
     example=('g = ExceptionGroup("две",\n'
              '    [ValueError(1), KeyError()])\nprint(len(g.exceptions))'))
term("except*", "exc_types",
     brief="Обрабатывает ошибки из ExceptionGroup по типам.",
     example=('try:\n    raise ExceptionGroup("g",\n'
              '        [ValueError(1)])\nexcept* ValueError:\n'
              '    print("поймали ValueError")'))
term("StopIteration", "gen_iter",
     brief="Итератор закончился: значений больше нет.",
     example='it = iter([])\ntry: next(it)\nexcept StopIteration:\n    print("пусто")')
term("RecursionError", "rec_basics",
     brief="Слишком глубокая рекурсия, обычно нет базового случая.",
     example=('def f(n): return f(n + 1)\ntry: f(0)\n'
              'except RecursionError:\n    print("слишком глубоко")'))
term("UnboundLocalError", "scope_legb",
     brief="Локальную переменную прочитали до присваивания.",
     example=('n = 1\ndef f():\n    n += 1\n'
              'try: f()\nexcept UnboundLocalError:\n    print("ошибка")'))
term("KeyboardInterrupt", "exc_try",
     brief="Пользователь нажал Ctrl+C и прервал программу.")
term("AssertionError", "test_assert",
     brief="Не прошла проверка `assert`.",
     example='try: assert 1 > 2, "не так"\nexcept AssertionError as e:\n    print(e)')
term("CancelledError", "async_timeouts", match=("asyncio.CancelledError",),
     brief="Задачу отменили.",
     example=('import asyncio\nasync def main():\n'
              '    t = asyncio.create_task(\n        asyncio.sleep(1))\n'
              '    await asyncio.sleep(0)\n    t.cancel()\n'
              '    try: await t\n'
              '    except (asyncio\n'
              '            .CancelledError):\n'
              '        print("отменена")\nasyncio.run(main())'))
term("TimeoutError", "async_timeouts", match=("asyncio.TimeoutError",),
     brief="Результата не дождались за отведённое время.",
     example='try: raise TimeoutError\nexcept TimeoutError:\n    print("тайм-аут")')

# --------------------------------------------- concepts (manual links only)
term("переменная", "var_assign", auto=False,
     brief="Имя, которое ссылается на значение.",
     example='x = 10\nprint(x * 2)')
term("истинность", "types_bool", auto=False,
     brief="Как значение ведёт себя в `if`: `0`, `\"\"`, `[]`, None считаются ложью.",
     example='print(bool(0), bool([]))\nprint(bool(""), bool("0"))')
term("изменяемый", "list_mutable", auto=False,
     brief="Изменяемый объект можно поменять на месте, неизменяемый нельзя.",
     example='xs = [1]\nxs[0] = 9\nprint(xs)')
term("хешируемый", "tuple_basics", auto=False,
     brief="Значение, по которому Python может вычислить `hash`: число, строка, кортеж из таких же. Только такие бывают ключами `dict` и элементами `set`; список — нет.",
     example='print(hash("a") == hash("a"))\nprint({(1, 2): "ok"})')
term("None", "none_value",
     brief="«Значения нет». Его возвращает функция без `return`.",
     example='def f(): pass\nprint(f(), f() is None)')
term("pass", None,
     brief="Пустая инструкция там, где синтаксис требует тела.",
     example='for i in range(3):\n    pass\nprint("готово")')
term("del", None,
     brief="Удаляет имя, элемент списка или ключ словаря.",
     example='xs = [1, 2, 3]\ndel xs[0]\nprint(xs)')
term("поверхностная копия", "list_mutable", auto=False,
     brief="Поверхностная копия: новый контейнер с теми же вложенными объектами.",
     example='a = [[1]]\nb = a.copy()\nb[0].append(2)\nprint(a)')
term("параметр", "func_params", auto=False,
     brief="Параметр это имя в объявлении функции, аргумент это значение при вызове.",
     example='def f(x):\n    print(x)\nf(5)')
term("docstring", "func_def", auto=False,
     brief="Строка-описание первой строкой функции, класса или модуля.",
     example='def f():\n    """Описание."""\nprint(f.__doc__)')
term("замыкание", "scope_closure", auto=False,
     brief="Вложенная функция, которая помнит переменные внешней.",
     example=('def adder(n):\n    return lambda x: x + n\n'
              'add5 = adder(5)\nprint(add5(1))'))
term("итератор", "gen_iter", auto=False,
     brief="Итератор это одноразовый поток значений; итерируемое то, из чего его получают.",
     example='it = iter([1, 2])\nprint(list(it), list(it))')
term("генератор", "gen_yield", auto=False,
     brief="Функция с `yield`, выдающая значения по одному.",
     example='def g():\n    yield "a"; yield "b"\nprint(list(g()))')
term("ленивые вычисления", "gen_lazy", auto=False,
     brief="Значения считаются, только когда их просят.",
     example='big = range(10**9)\nsq = map(lambda x: x * x, big)\nprint(next(sq), next(sq))')
term("исключение", "exc_try", auto=False,
     brief="Объект ошибки, прерывающий выполнение.",
     example='try: [][0]\nexcept Exception as e:\n    print(type(e).__name__)')
term("модуль", "std_import", auto=False,
     brief="Модуль это файл `.py`, пакет это папка с модулями.",
     example='import math\nprint(math.__name__)')
term("пакет", "proj_modules", auto=False,
     brief="Папка с модулями и файлом `__init__.py`; имена из неё импортируют через точку.")
term("объект", "oop_class", auto=False,
     brief="Метод это функция внутри объекта, атрибут это переменная внутри объекта.",
     example='s = "кот"\nprint(s.upper())')
term("наследование", "inh_basics", auto=False,
     brief="Класс получает методы класса-родителя.",
     example=('class A:\n    def hi(self): return "hi"\n'
              'class B(A): pass\nprint(B().hi())'))
term("утиная типизация", "inh_poly", auto=False,
     brief="Важно, что умеет объект, а не его класс.",
     example='for x in ["ab", [1, 2, 3]]:\n    print(len(x))')
term("декоратор", "deco_basics", auto=False,
     brief="Функция, которая оборачивает другую функцию.",
     example=('def twice(f):\n    return lambda: f() * 2\n'
              '@twice\ndef one(): return 1\nprint(one())'))
term("контекстный менеджер", "ctx_protocol", auto=False,
     brief="Объект для `with`: вход и гарантированный выход.",
     example='with open("a.txt", "w") as f:\n    pass\nprint(f.closed)')
term("сериализация", "data_json", auto=False,
     brief="Превращение данных в текст или байты для хранения и передачи.",
     example='import json\nprint(json.dumps({"a": [1, 2]}))')
term("O-большое", "algo_complexity", auto=False,
     brief="Сложность алгоритма: как растёт время работы с ростом данных.")
term("EAFP", "idiom_eafp", auto=False,
     brief="Сначала попробовать, потом обработать ошибку.",
     example='d = {}\ntry: print(d["k"])\nexcept KeyError: print("нет")')
term("корутина", "async_basics", auto=False,
     brief="Функция, которая умеет ждать, не блокируя другие; ими управляет цикл событий.",
     example='async def f(): return 1\nc = f()\nprint(type(c).__name__)\nc.close()')
term("PEP 8", "proj_style", auto=False,
     brief="Стиль кода Python: отступы, имена, длина строк.")
