"""Source of truth for the bundled Python course.

Generates assets/content/python/modules/*.json and VERIFIES every level by
executing the snippets with real Python: expected outputs, that each
ordering puzzle lists every valid order, and that bug-finder levels fail as
described and pass once the marked line is fixed.

Usage: python3 tool/content/generate_python_course.py assets/content/python/modules
"""
import contextlib
import io
import itertools
import json
import os
import sys

OUT = sys.argv[1]


def run(code):
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(code, "<level>", "exec"), {})
    except Exception as e:  # noqa
        return buf.getvalue(), type(e).__name__
    return buf.getvalue(), None


def mc(id, title, prompt, code, options, correct, hint, explanation, role="lesson", difficulty=1, expect_stdout=None):
    if expect_stdout is not None:
        out, err = run(code)
        assert err is None, (id, err)
        assert out == expect_stdout, (id, out, expect_stdout)
        # Options that are literal output must match it exactly once.
        printed = out.strip()
        if printed in options:
            assert options.index(printed) == correct, (id, "wrong correctIndex")
    return dict(id=id, type="multiple_choice", role=role, title=title, prompt=prompt, code=code,
                difficulty=difficulty, hint=hint, explanation=explanation,
                payload=dict(options=options, correctIndex=correct))


def fill(id, title, prompt, template, options, answers, hint, explanation, role="lesson", difficulty=1, expect_stdout=None):
    def filled(tokens):
        code = template
        for i, token in enumerate(tokens):
            code = code.replace("{{%d}}" % i, token)
        return code

    out, err = run(filled(answers))
    assert err is None, (id, err)
    if expect_stdout is not None:
        assert out == expect_stdout, (id, out)
    # No other combination of options may produce the same output:
    # otherwise a player with working code would be marked wrong.
    for combo in itertools.product(options, repeat=len(answers)):
        if list(combo) == list(answers):
            continue
        other, other_err = run(filled(combo))
        assert other_err is not None or other != out, (id, "ambiguous", combo)
    return dict(id=id, type="fill_code", role=role, title=title, prompt=prompt, difficulty=difficulty,
                hint=hint, explanation=explanation,
                payload=dict(template=template, options=options, answers=answers))


def order(id, title, prompt, lines, expect_stdout, hint, explanation, alternatives=(), role="practice", difficulty=2):
    for o in [list(range(len(lines)))] + [list(a) for a in alternatives]:
        out, err = run("\n".join(lines[i] for i in o))
        assert err is None and out == expect_stdout, (id, o, out, err)
    # sanity: count all permutations producing expected output == accepted set
    import itertools
    accepted = {tuple(range(len(lines)))} | {tuple(a) for a in alternatives}
    for perm in itertools.permutations(range(len(lines))):
        out, err = run("\n".join(lines[i] for i in perm))
        if err is None and out == expect_stdout:
            assert perm in accepted, (id, "missing alternative", perm)
    payload = dict(lines=lines)
    if alternatives:
        payload["alternativeOrders"] = [list(a) for a in alternatives]
    return dict(id=id, type="code_ordering", role=role, title=title, prompt=prompt, difficulty=difficulty,
                hint=hint, explanation=explanation, payload=payload)


def bug(id, title, prompt, code, buggy, hint, explanation, fixed_line, expect_fixed_stdout, role="challenge", difficulty=2, expect_error=None, expect_buggy_stdout=None):
    out, err = run(code)
    if expect_error:
        assert err == expect_error, (id, err)
    else:
        assert err is None and out == expect_buggy_stdout, (id, out, err)
    lines = code.split("\n")
    lines[buggy[0]] = fixed_line
    out, err = run("\n".join(lines))
    assert err is None and out == expect_fixed_stdout, (id, out, err)
    return dict(id=id, type="bug_finder", role=role, title=title, prompt=prompt, code=code, difficulty=difficulty,
                hint=hint, explanation=explanation, payload=dict(buggyLines=buggy))


modules = {}

modules["variables"] = [
    mc("py_var_001", "Первая переменная", "Какое значение будет у x?", "x = 5",
       ["3", "5", "x", "Ошибка"], 1,
       "После оператора = переменная получает значение справа.",
       "Оператор = записывает значение 5 в переменную x."),
    mc("py_var_002", "Изменение значения", "Что выведет код?", "x = 5\nx += 2\nprint(x)",
       ["5", "7", "2", "Ошибка"], 1,
       "x += 2 — это короткая запись x = x + 2.",
       "Сначала x = 5, затем x увеличивается на 2 и становится 7.", expect_stdout="7\n"),
    fill("py_var_003", "Присвоение значения", "Создайте переменную name со значением \"Ada\"",
         "name {{0}} \"Ada\"\nprint(name)", ["=", "==", ":", "->"], ["="],
         "Для присваивания используется один знак равенства.",
         "Один знак = присваивает значение, а == сравнивает два значения.", expect_stdout="Ada\n"),
    order("py_var_004", "Собери программу", "Расставьте строки так, чтобы программа вывела 15",
          ["x = 10", "y = 5", "result = x + y", "print(result)"], "15\n",
          "Переменную нельзя использовать до того, как ей присвоено значение.",
          "Сначала создаём x и y, затем считаем result и только потом выводим его.",
          alternatives=[[1, 0, 2, 3]]),
    bug("py_var_005", "Босс: опечатка", "Найдите строку с ошибкой",
        "score = 10\nbonus = 5\ntotal = score + bonsu\nprint(total)", [2],
        "Сравните имена переменных посимвольно.",
        "В строке 3 опечатка: bonsu вместо bonus. Python не знает такую переменную и выдаёт NameError.",
        "total = score + bonus", "15\n", role="boss", difficulty=3, expect_error="NameError"),
]

modules["types"] = [
    mc("py_types_001", "Дробные числа", "Какой тип у переменной x?", "x = 3.14",
       ["int", "float", "str", "bool"], 1,
       "Числа с точкой называются числами с плавающей точкой.",
       "3.14 — дробное число, его тип float."),
    mc("py_types_002", "Строка или число?", "Что выведет код?", "print(type(\"42\"))",
       ["<class 'int'>", "<class 'str'>", "<class 'float'>", "42"], 1,
       "Обратите внимание на кавычки.",
       "Всё, что в кавычках, — строка (str), даже если внутри цифры.", expect_stdout="<class 'str'>\n"),
    fill("py_types_003", "Преобразование типов", "Превратите строку \"25\" в целое число, чтобы программа вывела 26",
         "age = {{0}}(\"25\")\nprint(age + 1)", ["int", "str", "len", "bool"], ["int"],
         "Функция с именем целочисленного типа превращает строку в число.",
         "int(\"25\") возвращает число 25, поэтому age + 1 равно 26.", expect_stdout="26\n"),
    mc("py_types_004", "Правда или ложь", "Что выведет код?", "print(bool(0), bool(\"0\"))",
       ["False False", "False True", "True True", "True False"], 1,
       "Пустые значения и ноль — ложь. А непустая строка?",
       "bool(0) — False, а \"0\" — непустая строка, поэтому True.", difficulty=2,
       expect_stdout="False True\n"),
    order("py_types_005", "Босс: возраст", "Соберите программу, которая выведет «Возраст: 26»",
          ["age_text = \"25\"", "age = int(age_text) + 1", "message = \"Возраст: \" + str(age)", "print(message)"],
          "Возраст: 26\n",
          "Строки и числа нельзя складывать напрямую — нужен str().",
          "Сначала читаем строку, превращаем её в число, прибавляем 1 и собираем сообщение через str().",
          role="boss", difficulty=3),
]

modules["operators"] = [
    mc("py_ops_001", "Целочисленное деление", "Что выведет код?", "print(7 // 2)",
       ["3.5", "3", "4", "1"], 1,
       "// отбрасывает дробную часть.",
       "Оператор // делит нацело: 7 // 2 = 3.", expect_stdout="3\n"),
    mc("py_ops_002", "Остаток от деления", "Что выведет код?", "print(7 % 3)",
       ["1", "2", "0", "2.33"], 0,
       "% возвращает остаток от деления.",
       "7 = 3 * 2 + 1, поэтому остаток равен 1.", expect_stdout="1\n"),
    fill("py_ops_003", "Степень", "Возведите 2 в степень 10",
         "result = 2 {{0}} 10\nprint(result)", ["**", "^", "*", "//"], ["**"],
         "В Python для степени используются две звёздочки.",
         "2 ** 10 = 1024. Знак ^ в Python — это побитовое XOR, а не степень.", expect_stdout="1024\n"),
    bug("py_ops_004", "Сложение строки и числа", "Найдите строку, которая вызовет ошибку",
        "a = 10\nb = 0\nif b != 0:\n    print(a / b)\nprint(a + \"5\")", [4],
        "Можно ли сложить число и строку?",
        "Строка 5 складывает число и строку — это TypeError. Деление на ноль защищено проверкой b != 0.",
        "print(a + 5)", "15\n", role="challenge", expect_error="TypeError"),
    order("py_ops_005", "Босс: среднее", "Соберите программу, которая выведет среднее трёх чисел",
          ["a = 4", "b = 8", "c = 6", "average = (a + b + c) / 3", "print(average)"], "6.0\n",
          "Все три числа должны появиться до вычисления среднего.",
          "Порядок a, b, c не важен, но они должны быть до формулы, а print — в самом конце.",
          alternatives=[[0, 2, 1, 3, 4], [1, 0, 2, 3, 4], [1, 2, 0, 3, 4], [2, 0, 1, 3, 4], [2, 1, 0, 3, 4]],
          role="boss", difficulty=3),
]

modules["conditions"] = [
    mc("py_cond_001", "Первое условие", "Что выведет код?",
       "x = 7\nif x > 5:\n    print(\"big\")\nelse:\n    print(\"small\")",
       ["big", "small", "big small", "Ничего"], 0,
       "7 больше 5?",
       "Условие x > 5 истинно, поэтому выполняется ветка if.", expect_stdout="big\n"),
    fill("py_cond_002", "Больше или равно", "Разрешите доступ всем, кому 18 лет и больше",
         "age = 20\nif age {{0}} 18:\n    print(\"Доступ разрешён\")", [">=", "=", "=>", "=="], [">="],
         "Нужен оператор «больше или равно».",
         "В Python «больше или равно» пишется как >=. Вариант => — синтаксическая ошибка.",
         expect_stdout="Доступ разрешён\n"),
    fill("py_cond_003", "Цепочка условий", "Заполните пропуски, чтобы при t = 30 программа вывела только «жарко»",
         "t = 30\n{{0}} t > 25:\n    print(\"жарко\")\n{{1}} t > 10:\n    print(\"тепло\")\nelse:\n    print(\"холодно\")",
         ["if", "elif", "else", "when"], ["if", "elif"],
         "Нужна одна цепочка: после первой сработавшей проверки остальные пропускаются.",
         "if начинает цепочку, elif проверяется, только если предыдущие условия ложны. Два отдельных if вывели бы и «жарко», и «тепло».",
         role="practice", difficulty=2, expect_stdout="жарко\n"),
    bug("py_cond_004", "Пропавшее двоеточие", "Найдите строку с ошибкой",
        "n = 4\nif n % 2 == 0\n    print(\"чётное\")\nelse:\n    print(\"нечётное\")", [1],
        "Посмотрите на конец строк с if и else.",
        "После условия if обязательно ставится двоеточие. Без него — SyntaxError.",
        "if n % 2 == 0:", "чётное\n", role="challenge", expect_error="SyntaxError"),
    order("py_cond_005", "Босс: оценка", "Соберите программу, которая выведет «Отлично» для оценки 5",
          ["grade = 5", "if grade == 5:", "    print(\"Отлично\")", "else:", "    print(\"Можно лучше\")"],
          "Отлично\n",
          "Каждая ветка начинается со строки с двоеточием, а её тело идёт с отступом.",
          "Переменная, затем if с телом, затем else со своим телом.",
          role="boss", difficulty=3),
]

modules["loops"] = [
    fill("py_loop_001", "Цикл for", "Допишите цикл, который выведет числа от 0 до 4",
         "for i {{0}} range(5):\n    print(i)", ["in", "of", "from", "inside"], ["in"],
         "for <переменная> ___ <последовательность>",
         "Цикл for перебирает элементы последовательности с помощью ключевого слова in.",
         expect_stdout="0\n1\n2\n3\n4\n"),
    mc("py_loop_002", "range", "Какое последнее число выведет программа?",
       "for i in range(3):\n    print(i)", ["2", "3", "4", "Ничего"], 0,
       "range(3) начинается с 0 и не включает 3.",
       "range(3) даёт 0, 1, 2 — последнее число 2.", expect_stdout="0\n1\n2\n"),
    mc("py_loop_003", "Сумма в цикле", "Что выведет код?",
       "total = 0\nfor n in range(1, 4):\n    total += n\nprint(total)", ["6", "10", "3", "4"], 0,
       "range(1, 4) — это 1, 2, 3.",
       "1 + 2 + 3 = 6.", role="practice", difficulty=2, expect_stdout="6\n"),
    order("py_loop_004", "Обратный отсчёт", "Соберите программу: 3, 2, 1, затем «Старт!»",
          ["count = 3", "while count > 0:", "    print(count)", "    count -= 1", "print(\"Старт!\")"],
          "3\n2\n1\nСтарт!\n",
          "Сначала выводим число, потом уменьшаем.",
          "while повторяет тело, пока count > 0. «Старт!» стоит без отступа — после цикла.",
          role="challenge", difficulty=3),
    bug("py_loop_005", "Босс: сумма не считается", "Программа должна вывести 15, но выводит 0. Найдите ошибку",
        "total = 0\nfor i in range(1, 6):\n    total == total + i\nprint(total)", [2],
        "Чем отличаются = и ==?",
        "== только сравнивает и ничего не меняет. Нужно присваивание: total = total + i.",
        "    total = total + i", "15\n", role="boss", difficulty=3, expect_buggy_stdout="0\n"),
]

total = 0
for name, levels in modules.items():
    with open(os.path.join(OUT, f"{name}.json"), "w", encoding="utf-8") as f:
        json.dump({"schemaVersion": 1, "levels": levels}, f, ensure_ascii=False, indent=2)
        f.write("\n")
    total += len(levels)
print("levels:", total)
