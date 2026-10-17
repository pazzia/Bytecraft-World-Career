"""Модули 18–21: исключения, файлы, стандартная библиотека, текст и данные."""
import re as _re
from bclib import choice, fill, match, multi, order, predict, bug, typed, topic, task, run


def runs(code):
    return run(code).ok


def error_of(code):
    return run(code).error


MODULES = []

# -------------------------------------------------------------- exceptions
ERROR_SNIPPETS = ["int('abc')", "[1, 2][5]", "{'a': 1}['b']", "1 / 0", "'5' + 5", "undefined_name"]

MODULES.append(dict(
    id="exceptions", title="Исключения", description="try, except, raise", icon="🛟",
    topics=[
        topic("exc_try", "try / except / else / finally",
              "try выполняет код, except перехватывает ошибку, else — если ошибки не было, finally — всегда.",
              """
              Код, который может упасть, помещают в try. Если внутри возникло исключение, Python ищет первый подходящий except и выполняет его. Остаток try после ошибки не выполняется.

              else выполняется, только если в try не было исключения: туда кладут код, который зависит от успеха, но сам не должен перехватываться.

              finally выполняется всегда: и после успеха, и после ошибки, и даже если в try был return. Там закрывают ресурсы.

              except ValueError as e — в e попадает объект исключения; str(e) — сообщение.
              """,
              [("""\
                def check(x):
                    try:
                        r = 10 / x
                    except ZeroDivisionError:
                        print("ошибка")
                    else:
                        print("ok", r)
                    finally:
                        print("конец")

                check(2)
                check(0)""", None),
               ("""\
                try:
                    int("12a")
                except ValueError as e:
                    print("Сообщение:", e)""", None)],
              ["Голый except: перехватывает всё подряд, включая опечатки в коде, и прячет ошибки.",
               "Слишком большой блок try: непонятно, какая строка на самом деле упала."]),
        topic("exc_types", "Иерархия исключений",
              "Исключения — классы. except ловит указанный класс и все его подклассы, поэтому важен порядок блоков except.",
              """
              Частые: ValueError (неподходящее значение: int("abc")), TypeError (неподходящий тип: "5" + 5), KeyError и IndexError (нет ключа или индекса), ZeroDivisionError, NameError, AttributeError, FileNotFoundError.

              KeyError и IndexError — подклассы LookupError, почти все — подклассы Exception. except Exception ловит практически всё, поэтому его ставят последним: Python проверяет блоки сверху вниз и выполняет первый подходящий.

              Подход EAFP («проще попросить прощения, чем разрешения»): попробовать действие и обработать исключение, вместо множества предварительных проверок.
              """,
              [("""\
                for code in ["[1][5]", "{}['k']", "1/0"]:
                    try:
                        eval(code)
                    except LookupError as e:
                        print("поиск:", type(e).__name__)
                    except Exception as e:
                        print("другое:", type(e).__name__)""", "LookupError ловит и IndexError, и KeyError.")],
              ["except Exception перед except ValueError: второй блок никогда не сработает."]),
        topic("exc_raise", "raise и свои исключения",
              "raise создаёт исключение. Своё исключение — класс-наследник Exception. raise ... from e сохраняет причину.",
              """
              raise ValueError("сообщение") прерывает функцию и передаёт ошибку вызывающему коду. Так функция сообщает, что не может выполнить работу с такими данными.

              Своё исключение объявляют как class InsufficientFunds(Exception): pass — его можно ловить отдельно от остальных. Подробно о классах — в модуле про ООП.

              raise NewError(...) from e связывает новую ошибку с исходной (e становится __cause__) — в трассировке видны обе. Голый raise внутри except пробрасывает текущее исключение дальше.
              """,
              [("""\
                class InsufficientFunds(Exception):
                    pass

                def withdraw(balance, amount):
                    if amount > balance:
                        raise InsufficientFunds(f"не хватает {amount - balance}")
                    return balance - amount

                try:
                    withdraw(50, 80)
                except InsufficientFunds as e:
                    print("Ошибка:", e)""", None)],
              ["raise без аргумента вне except: RuntimeError No active exception to reraise.",
               "Возвращать «магические» значения вроде -1 вместо исключения: вызывающий код их легко пропустит."]),
    ],
    tasks=[
        task("t_exc_safe_div", "Безопасное деление",
             "В первой строке — число n, далее n строк вида «a b». Для каждой строки выведите a / b, округлив до 2 знаков, а при ошибке — «деление на ноль» или «не число».",
             solution="""\
                n = int(input())
                for _ in range(n):
                    a, b = input().split()
                    try:
                        print(round(float(a) / float(b), 2))
                    except ZeroDivisionError:
                        print("деление на ноль")
                    except ValueError:
                        print("не число")""",
             starter="""\
                n = int(input())
                for _ in range(n):
                    a, b = input().split()
                    print(round(float(a) / float(b), 2))""",
             tests=["2\n1 4\n10 3\n", "3\n5 0\nx 2\n9 3\n", "1\n7 abc\n", "2\n-9 2\n0 0\n"],
             hint="Два блока except: для ZeroDivisionError и для ValueError.", difficulty=2,
             requires=dict(uses=["try"])),
    ],
    levels=[
        predict("py_exc_001", "Перехват", """\
                try:
                    print(10 / 0)
                except ZeroDivisionError:
                    print("деление на ноль")""",
                ["ZeroDivisionError", "0", "inf"], position=0, topic="exc_try",
                hint="Ошибка внутри try передаёт управление в подходящий except.",
                explanation="10 / 0 вызывает ZeroDivisionError, print внутри try не успевает выполниться, и срабатывает except.",
                feedback={"ZeroDivisionError": "Исключение перехвачено, программа не падает и выполняет except.",
                          "0": "Деление на ноль в Python — ошибка, а не 0.",
                          "inf": "Для чисел Python не возвращает бесконечность при делении на 0, он вызывает ошибку."}),
        match("py_exc_002", "Какая ошибка", ERROR_SNIPPETS,
              rights=[error_of(s) for s in ERROR_SNIPPETS], prompt="Сопоставьте код и исключение, которое он вызовет",
              topic="exc_types", hint="Неверное значение — ValueError, неверный тип — TypeError.",
              explanation="int('abc') — ValueError, индекс за пределами — IndexError, нет ключа — KeyError, деление на 0 — ZeroDivisionError, строка + число — TypeError, неизвестное имя — NameError."),
        fill("py_exc_003", "Нужный except", "Перехватите ошибку преобразования",
             """\
             try:
                 n = int("x")
             except {{0}}:
                 print("не число")""", ["ValueError", "TypeError", "KeyError", "IndexError"], ["ValueError"],
             topic="exc_types", hint="int() получил строку подходящего типа, но неподходящего содержания.",
             explanation="int(\"x\") вызывает ValueError: тип (строка) подходит, а значение — нет.",
             expect="не число\n"),
        typed("py_exc_004", "else и finally", """\
              def check(x):
                  try:
                      r = 10 / x
                  except ZeroDivisionError:
                      print("ошибка")
                  else:
                      print("ok", r)
                  finally:
                      print("конец")

              check(2)
              check(0)""",
              topic="exc_try", hint="else — только без ошибки, finally — всегда.",
              explanation="check(2): ошибки нет — else печатает ok 5.0, потом finally. check(0): except печатает «ошибка», потом finally."),
        bug("py_exc_005", "Не тот except", """\
            prices = {"apple": 3}
            try:
                print(prices["pear"])
            except IndexError:
                print("нет такого товара")""", {3: "except KeyError:"},
            prompt="Отсутствующий товар должен давать сообщение, а не падение. Найдите строку с ошибкой",
            topic="exc_types", hint="Какое исключение вызывает обращение к отсутствующему ключу словаря?",
            explanation="Нет ключа в словаре — KeyError, а не IndexError. except IndexError его не ловит, и программа падает.",
            expect_error="KeyError"),
        multi("py_exc_006", "Семейство LookupError", "Какие исключения перехватит except LookupError?",
              ["KeyError", "IndexError", "ValueError", "ZeroDivisionError", "TypeError"], [0, 1],
              check=lambda name: issubclass(eval(name), LookupError), topic="exc_types",
              hint="LookupError — ошибки поиска по ключу или индексу.",
              explanation="KeyError и IndexError — подклассы LookupError, поэтому except LookupError ловит обе. Остальные к этому семейству не относятся.",
              feedback={"ValueError": "ValueError — ошибка значения, не поиска.",
                        "ZeroDivisionError": "Это арифметическая ошибка (ArithmeticError).",
                        "TypeError": "TypeError — ошибка типа, не поиска."}),
        order("py_exc_007", "Своя проверка", "Соберите программу, которая выведет «Ошибка: мало средств»",
              ["def withdraw(balance, amount):", "    if amount > balance:",
               "        raise ValueError(\"мало средств\")", "try:", "    withdraw(50, 80)",
               "except ValueError as e:", "    print(\"Ошибка:\", e)"],
              topic="exc_raise", hint="raise внутри функции, try/except — в вызывающем коде.",
              explanation="Функция сообщает о проблеме через raise, а код, который её вызвал, решает, что делать: перехватывает ValueError и печатает сообщение."),
        predict("py_exc_008", "Цепочка причин", """\
                try:
                    try:
                        int("x")
                    except ValueError as e:
                        raise RuntimeError("плохой ввод") from e
                except RuntimeError as e:
                    print(type(e).__name__, e, type(e.__cause__).__name__)""",
                ["ValueError плохой ввод RuntimeError", "RuntimeError плохой ввод NoneType",
                 "RuntimeError invalid literal ValueError"], position=3, topic="exc_raise",
                hint="from e записывает исходную ошибку в __cause__ новой.",
                explanation="Внешний except ловит RuntimeError с сообщением «плохой ввод», а его __cause__ — исходная ValueError.",
                role="challenge", difficulty=3,
                feedback={"ValueError плохой ввод RuntimeError": "Перехвачена новая ошибка RuntimeError, а ValueError — её причина.",
                          "RuntimeError плохой ввод NoneType": "from e заполняет __cause__: там ValueError.",
                          "RuntimeError invalid literal ValueError": "Сообщение новой ошибки — то, что передано в RuntimeError(...)."}),
        predict("py_exc_009", "Босс: return и finally", """\
                def f():
                    try:
                        return "try"
                    finally:
                        print("finally")

                print(f())""",
                ["try", "finally", "try\nfinally"], position=3, topic="exc_try",
                hint="finally выполняется даже тогда, когда try завершается через return.",
                explanation="return \"try\" запоминает значение, затем выполняется finally (печатает «finally»), и только потом функция возвращает «try», которое печатает внешний print.",
                role="boss", difficulty=3,
                feedback={"try": "finally выполняется всегда, даже после return.",
                          "finally": "Значение из return не теряется: оно возвращается после finally.",
                          "try\nfinally": "finally выполняется до того, как вызывающий код получит результат."}),
    ],
))

# ------------------------------------------------------------------- files
MODULES.append(dict(
    id="files", title="Файлы", description="open, with, pathlib", icon="📄",
    topics=[
        topic("files_open", "open и with",
              "open(путь, режим, encoding=...) открывает файл; with закрывает его автоматически.",
              """
              Режимы: "r" — чтение (по умолчанию), "w" — запись с очисткой файла, "a" — дописывание в конец, "x" — создать новый (ошибка, если файл уже есть). Добавка "b" — двоичный режим.

              with open(...) as f: закрывает файл при выходе из блока, даже если внутри случилась ошибка. Закрытый файл больше нельзя читать или писать: ValueError.

              Для текста указывайте кодировку: encoding="utf-8". Иначе используется кодировка системы, и русский текст может прочитаться неверно.
              """,
              [("""\
                with open("notes.txt", "w", encoding="utf-8") as f:
                    f.write("первая\\n")
                with open("notes.txt", "a", encoding="utf-8") as f:
                    f.write("вторая\\n")
                with open("notes.txt", encoding="utf-8") as f:
                    print(f.read(), end="")""", "\"a\" дописывает, не стирая.")],
              ["Открыть существующий файл в режиме \"w\": его содержимое сразу стирается.",
               "write не добавляет перевод строки сам: нужен \"\\n\"."]),
        topic("files_read", "Чтение построчно",
              "read() — весь текст, readline() — одна строка, readlines() — список строк, for line in f — строки по одной.",
              """
              Каждая прочитанная строка заканчивается символом \\n (кроме, возможно, последней). Для обработки его обычно убирают: line.rstrip("\\n") или line.strip().

              for line in f читает файл лениво, по строке за раз — так обрабатывают даже очень большие файлы.

              int(" 42\\n") работает: int игнорирует пробелы и переводы строк по краям.
              """,
              [("""\
                with open("data.txt", "w") as f:
                    f.write("3\\n5\\n8\\n")
                with open("data.txt") as f:
                    lines = f.readlines()
                print(lines)
                print([int(line) for line in lines])""", None)],
              ["Сравнивать прочитанную строку с текстом без strip: \"да\\n\" != \"да\"."]),
        topic("files_pathlib", "pathlib.Path",
              "Path — объект пути: части пути, проверка существования, чтение и запись в одну строку.",
              """
              Path("reports") / "2024" / "summary.csv" склеивает путь оператором /. У пути есть name (имя файла), stem (без расширения), suffix (расширение), parent (папка).

              path.write_text(text, encoding="utf-8") и path.read_text(encoding="utf-8") открывают и закрывают файл сами. path.exists() — существует ли путь, path.mkdir(parents=True, exist_ok=True) — создать папки, Path(".").glob("*.txt") — найти файлы по шаблону.
              """,
              [("""\
                from pathlib import Path

                p = Path("reports") / "2024" / "summary.final.csv"
                print(p.name, p.stem, p.suffix, p.parent, sep=" | ")""", None),
               ("""\
                from pathlib import Path

                p = Path("hello.txt")
                p.write_text("Привет!", encoding="utf-8")
                print(p.exists(), p.read_text(encoding="utf-8"))""", None)],
              ["Склеивать пути строками через \"+\" и \"/\": Path делает это правильно на любой системе."]),
    ],
    tasks=[
        task("t_files_reverse", "Обратный порядок",
             "Прочитайте число n и n строк. Запишите строки в файл lines.txt (каждую на своей строке), затем прочитайте файл и выведите строки в обратном порядке.",
             solution="""\
                n = int(input())
                with open("lines.txt", "w", encoding="utf-8") as f:
                    for _ in range(n):
                        f.write(input() + "\\n")
                with open("lines.txt", encoding="utf-8") as f:
                    lines = [line.rstrip("\\n") for line in f]
                for line in reversed(lines):
                    print(line)""",
             starter="""\
                n = int(input())
                with open("lines.txt", "w", encoding="utf-8") as f:
                    for _ in range(n):
                        f.write(input() + "\\n")
                with open("lines.txt", encoding="utf-8") as f:
                    print(f.read())""",
             tests=["3\nраз\nдва\nтри\n", "1\nодин\n", "2\nab\ncd\n", "4\n1\n2\n3\n4\n"],
             hint="Прочитанные строки содержат \\n в конце — уберите его через rstrip.", difficulty=2,
             requires=dict(uses=["with"])),
    ],
    levels=[
        choice("py_files_001", "Режим «a»", "Что делает режим \"a\" в open(\"log.txt\", \"a\")?",
               ["Открывает только для чтения", "Стирает файл и пишет заново", "Дописывает в конец файла",
                "Создаёт файл, только если его нет"], 2,
               topic="files_open", hint="a — от слова append.",
               explanation="\"a\" (append) дописывает данные в конец, сохраняя старое содержимое; если файла нет, он создаётся.",
               feedback={"Открывает только для чтения": "Это режим \"r\".",
                         "Стирает файл и пишет заново": "Это режим \"w\".",
                         "Создаёт файл, только если его нет": "Это режим \"x\"."}),
        predict("py_files_002", "Сколько строк", """\
                with open("notes.txt", "w", encoding="utf-8") as f:
                    f.write("первая\\n")
                    f.write("вторая\\n")
                with open("notes.txt", encoding="utf-8") as f:
                    print(len(f.readlines()))""",
                ["1", "14", "0"], position=1, topic="files_read",
                hint="readlines возвращает список строк файла.",
                explanation="В файл записаны две строки, каждая с \\n в конце. readlines() возвращает список из двух элементов.",
                feedback={"1": "Каждый write с \\n добавляет отдельную строку.",
                          "14": "len считает элементы списка (строки), а не символы.",
                          "0": "with закрыл файл после записи, данные сохранены."}),
        fill("py_files_003", "Не стереть", "Допишите вторую строку, сохранив первую",
             """\
             with open("log.txt", "w") as f:
                 f.write("a\\n")
             with open("log.txt", "{{0}}") as f:
                 f.write("b\\n")
             with open("log.txt") as f:
                 print(f.read(), end="")""", ["a", "w", "r", "x"], ["a"],
             topic="files_open", hint="Нужен режим дописывания.",
             explanation="Режим \"a\" дописывает в конец. \"w\" стёр бы строку a, \"r\" не разрешает запись, \"x\" требует, чтобы файла не было.",
             expect="a\nb\n"),
        typed("py_files_004", "Сумма из файла", """\
              with open("data.txt", "w") as f:
                  f.write("3\\n5\\n8\\n")
              total = 0
              count = 0
              with open("data.txt") as f:
                  for line in f:
                      total += int(line)
                      count += 1
              print(total, count)""",
              topic="files_read", hint="int() не мешает перевод строки в конце.",
              explanation="Цикл идёт по трём строкам: 3 + 5 + 8 = 16, строк 3."),
        bug("py_files_005", "Склеенные имена", """\
            names = ["Ада", "Линус"]
            with open("names.txt", "w", encoding="utf-8") as f:
                for name in names:
                    f.write(name)
            with open("names.txt", encoding="utf-8") as f:
                print(len(f.readlines()))""", {3: "        f.write(name + \"\\n\")"},
            prompt="Каждое имя должно оказаться на своей строке, программа должна вывести 2. Найдите строку с ошибкой",
            topic="files_open", hint="Добавляет ли write перевод строки сам?",
            explanation="write пишет ровно то, что передано: получилась одна строка «АдаЛинус». Нужно добавлять \"\\n\"."),
        match("py_files_006", "Части пути", ["p.name", "p.stem", "p.suffix", "p.parent", "p.parts[0]"],
              setup="""\
                from pathlib import Path
                p = Path("reports/2024/summary.final.csv")""",
              topic="files_pathlib", hint="suffix — только последнее расширение.",
              explanation="name — имя с расширением, stem — без последнего расширения, suffix — «.csv», parent — папка, parts[0] — первая часть пути."),
        multi("py_files_007", "Весь текст", "В файле data.txt две строки. Какие выражения вернут всё его содержимое одной строкой?",
              ["open(\"data.txt\").read()", "Path(\"data.txt\").read_text()", "open(\"data.txt\").readlines()",
               "\"\".join(open(\"data.txt\"))", "open(\"data.txt\").readline()"], [0, 1, 3],
              check=lambda expr: run(
                  "from pathlib import Path\n"
                  "with open('data.txt', 'w') as f:\n    f.write('a\\nb\\n')\n"
                  f"assert ({expr}) == 'a\\nb\\n'").ok,
              topic="files_read", hint="readlines возвращает список, readline — одну строку.",
              explanation="read() и read_text() возвращают весь текст. join склеивает строки, по которым идёт цикл. readlines даёт список, readline — только первую строку.",
              feedback={"open(\"data.txt\").readlines()": "readlines возвращает список строк, а не одну строку.",
                        "open(\"data.txt\").readline()": "readline читает только одну строку."}),
        order("py_files_008", "Простой CSV", "Соберите программу, которая выведет 77",
              ["rows = [(\"Ада\", 36), (\"Алан\", 41)]",
               "with open(\"people.csv\", \"w\", encoding=\"utf-8\") as f:",
               "    for name, age in rows:",
               "        f.write(f\"{name};{age}\\n\")",
               "with open(\"people.csv\", encoding=\"utf-8\") as f:",
               "    ages = [int(line.split(\";\")[1]) for line in f]",
               "print(sum(ages))"],
              topic="files_read", hint="Сначала записать файл, потом прочитать.",
              explanation="Каждая строка файла — «имя;возраст». split(\";\")[1] берёт возраст, int убирает \\n: 36 + 41 = 77.",
              role="challenge", difficulty=3),
        predict("py_files_009", "Босс: после with", """\
                with open("t.txt", "w") as f:
                    f.write("hi")
                print(f.closed)
                try:
                    f.write("again")
                except ValueError as e:
                    print("ошибка:", e)""",
                ["False", "True\nagain", "False\nошибка: I/O operation on closed file."], position=0,
                topic="files_open", hint="Что делает with с файлом при выходе из блока?",
                explanation="После блока with файл закрыт: f.closed — True, а запись в закрытый файл вызывает ValueError.",
                role="boss", difficulty=3,
                feedback={"False": "with закрывает файл при выходе из блока.",
                          "True\nagain": "В закрытый файл писать нельзя: будет ValueError.",
                          "False\nошибка: I/O operation on closed file.": "Ошибка верная, но f.closed уже True."}),
    ],
))

# ------------------------------------------------------------------ stdlib
DICT_LIKE = ["Counter", "defaultdict", "OrderedDict", "deque", "namedtuple"]

MODULES.append(dict(
    id="stdlib", title="Стандартная библиотека", description="import, collections, itertools", icon="🧰",
    topics=[
        topic("std_import", "Импорт модулей",
              "import модуль — доступ через модуль.имя; from модуль import имя — имя напрямую; as — псевдоним.",
              """
              import math → math.sqrt(16). from math import sqrt → sqrt(16). import numpy as np — короткий псевдоним.

              from модуль import * захламляет пространство имён и прячет, откуда взялось имя, — в рабочем коде так не делают.

              Модуль выполняется один раз при первом импорте. Свой файл можно импортировать так же, как стандартный модуль, поэтому не называйте файлы как стандартные модули (random.py, json.py): import подхватит ваш файл.
              """,
              [("""\
                import math
                from statistics import mean as average

                print(math.sqrt(16), math.pi > 3, average([1, 2, 3, 4]))""", None)],
              ["Файл random.py в папке проекта перекрывает стандартный модуль random."]),
        topic("std_collections", "collections",
              "Counter — подсчёт, defaultdict — значение по умолчанию, deque — быстрая очередь с двух концов, namedtuple — кортеж с именами полей.",
              """
              Counter("abracadabra") считает элементы; most_common(n) — n самых частых (при равенстве — в порядке первого появления).

              defaultdict(list) создаёт пустой список для нового ключа при первом обращении: groups[key].append(x) без проверок.

              deque — двусторонняя очередь: append/appendleft и pop/popleft за O(1). deque(maxlen=3) хранит только последние 3 элемента.

              namedtuple("Point", "x y") создаёт неизменяемый тип с полями p.x и p.y и понятным выводом.
              """,
              [("""\
                from collections import Counter, defaultdict, deque

                print(Counter("abracadabra").most_common(2))
                groups = defaultdict(list)
                for word in ["apple", "avocado", "banana"]:
                    groups[word[0]].append(word)
                print(dict(groups))
                last = deque(maxlen=2)
                for x in [1, 2, 3]:
                    last.append(x)
                print(list(last))""", None)],
              ["list.pop(0) в цикле — медленно для больших списков: для очереди есть deque.popleft()."]),
        topic("std_itertools", "itertools",
              "Инструменты для перебора: chain, product, permutations, combinations, accumulate, groupby, islice.",
              """
              chain(a, b) — последовательно a, затем b. product("ab", repeat=2) — все пары с повторениями (декартово произведение). permutations — перестановки, combinations — сочетания без учёта порядка. accumulate — накопленные суммы.

              groupby группирует только соседние одинаковые элементы — поэтому данные сначала сортируют по тому же ключу.

              Все они ленивые: возвращают итераторы, для печати нужен list().
              """,
              [("""\
                from itertools import combinations, groupby

                print(list(combinations("abc", 2)))
                words = sorted(["bob", "apple", "banana", "avocado"])
                for letter, group in groupby(words, key=lambda w: w[0]):
                    print(letter, list(group))""", None)],
              ["groupby без сортировки разбивает одну группу на несколько."]),
    ],
    tasks=[
        task("t_std_anagrams", "Анаграммы",
             "Прочитайте слова через пробел. Сгруппируйте анаграммы (слова из одних и тех же букв) и выведите каждую группу в отдельной строке: слова группы через пробел в алфавитном порядке, группы — по алфавиту первого слова.",
             solution="""\
                from collections import defaultdict

                groups = defaultdict(list)
                for word in input().split():
                    groups["".join(sorted(word))].append(word)
                for group in sorted(sorted(g) for g in groups.values()):
                    print(" ".join(group))""",
             starter="""\
                words = input().split()
                print(" ".join(words))""",
             tests=["кот ток окт сон нос\n", "a b a\n", "listen silent enlist google\n", "abc cab bca xyz zyx q\n"],
             hint="Ключ группы — буквы слова, отсортированные по алфавиту.", difficulty=3),
    ],
    levels=[
        choice("py_std_001", "Без префикса", "Какой импорт позволит писать sqrt(16) без math. впереди?",
               ["import math", "from math import sqrt", "import sqrt from math", "include math"], 1,
               check=lambda option: runs(f"{option}\nprint(sqrt(16))"), topic="std_import",
               hint="Нужно импортировать само имя из модуля.",
               explanation="from math import sqrt добавляет имя sqrt в программу. После import math нужно писать math.sqrt.",
               feedback={"import math": "После import math функция доступна как math.sqrt(16).",
                         "import sqrt from math": "Такой синтаксис есть в JavaScript, в Python — from math import sqrt.",
                         "include math": "В Python нет include, есть import."}),
        predict("py_std_002", "Самые частые", """\
                from collections import Counter
                c = Counter("abracadabra")
                print(c.most_common(2))""",
                ["[('a', 5), ('r', 2)]", "{'a': 5, 'b': 2}", "['a', 'b']"], position=1, topic="std_collections",
                hint="b и r встречаются по 2 раза. Кто встретился раньше?",
                explanation="a — 5 раз, b и r — по 2. При равенстве most_common сохраняет порядок первого появления: b раньше r.",
                feedback={"[('a', 5), ('r', 2)]": "При равных счётчиках порядок — по первому появлению: b появляется раньше r.",
                          "{'a': 5, 'b': 2}": "most_common возвращает список пар (элемент, количество).",
                          "['a', 'b']": "Вместе с элементами возвращаются и количества."}),
        fill("py_std_003", "Группы по букве", "Сгруппируйте слова по первой букве",
             """\
             from collections import defaultdict
             groups = defaultdict({{0}})
             for word in ["apple", "avocado", "banana"]:
                 groups[word[0]].append(word)
             print(dict(groups))""", ["list", "dict", "set", "int"], ["list"],
             topic="std_collections", hint="У значения по умолчанию должен быть метод append.",
             explanation="defaultdict(list) создаёт пустой список для нового ключа, и append сразу работает.",
             expect="{'a': ['apple', 'avocado'], 'b': ['banana']}\n"),
        match("py_std_004", "itertools", ["list(chain([1, 2], [3]))", "len(list(product('ab', repeat=2)))",
                                          "len(list(permutations('abc', 2)))", "len(list(combinations('abc', 2)))",
                                          "list(accumulate([1, 2, 3, 4]))"],
              setup="from itertools import chain, product, permutations, combinations, accumulate",
              topic="std_itertools", hint="В перестановках порядок важен, в сочетаниях — нет.",
              explanation="chain склеивает, product даёт 2·2 = 4 пары, перестановок по 2 из 3 — 6, сочетаний — 3, accumulate — накопленные суммы."),
        typed("py_std_005", "Очередь с лимитом", """\
              from collections import deque
              q = deque([1, 2, 3], maxlen=3)
              q.append(4)
              q.appendleft(0)
              print(list(q))""",
              topic="std_collections", hint="При переполнении deque выталкивает элемент с противоположного конца.",
              explanation="append(4) выталкивает 1 слева: [2, 3, 4]. appendleft(0) выталкивает 4 справа: [0, 2, 3]."),
        predict("py_std_006", "Именованный кортеж", """\
                from collections import namedtuple
                Point = namedtuple("Point", "x y")
                p = Point(3, 4)
                print(p.x + p.y, p)""",
                ["7 (3, 4)", "34 Point(x=3, y=4)", "AttributeError"], position=1, topic="std_collections",
                hint="namedtuple создаёт тип с полями x и y и понятным выводом.",
                explanation="p.x + p.y = 7, а print показывает Point(x=3, y=4).",
                role="practice", difficulty=2,
                feedback={"7 (3, 4)": "namedtuple печатается с именами типа и полей.",
                          "34 Point(x=3, y=4)": "x и y — числа, + складывает их.",
                          "AttributeError": "Поля x и y объявлены строкой \"x y\"."}),
        bug("py_std_007", "Разорванные группы", """\
            from itertools import groupby
            words = ["apple", "bob", "avocado", "banana"]
            for letter, group in groupby(words, key=lambda w: w[0]):
                print(letter, len(list(group)))""",
            {1: "words = sorted([\"apple\", \"bob\", \"avocado\", \"banana\"])"},
            prompt="Нужно вывести a 2 и b 2. Найдите строку с ошибкой", topic="std_itertools",
            hint="groupby объединяет только соседние элементы.",
            explanation="groupby идёт по списку и начинает новую группу при каждой смене ключа. Без сортировки получается a, b, a, b по одному. После sorted одинаковые буквы стоят рядом."),
        multi("py_std_008", "Похожи на словарь", "Какие типы из collections — подклассы dict?", DICT_LIKE, [0, 1, 2],
              check=lambda name: run(f"from collections import {name}\nassert isinstance({name}, type) and issubclass({name}, dict)").ok,
              topic="std_collections", hint="Какие из них хранят пары ключ → значение?",
              explanation="Counter, defaultdict и OrderedDict наследуют dict. deque — очередь, namedtuple — фабрика кортежей.",
              feedback={"deque": "deque — двусторонняя очередь, похожа на список.",
                        "namedtuple": "namedtuple — функция, создающая подкласс кортежа."}),
        order("py_std_009", "Босс: частые слова", "Соберите программу, которая выведет to=2, be=2",
              ["from collections import Counter", "text = \"to be or not to be\"",
               "counts = Counter(text.split())", "top = counts.most_common(2)",
               "print(\", \".join(f\"{w}={n}\" for w, n in top))"],
              topic="std_collections", hint="Импорт → данные → подсчёт → топ → вывод.",
              explanation="split разбивает текст на слова, Counter считает их, most_common(2) берёт два самых частых (to встречается раньше be).",
              role="boss", difficulty=3),
    ],
))

# --------------------------------------------------------------- text data
MODULES.append(dict(
    id="textdata", title="Текст и данные", description="json, регулярные выражения, даты", icon="🗂️",
    topics=[
        topic("data_json", "JSON",
              "json.dumps превращает данные Python в строку JSON, json.loads — обратно. dump/load работают с файлами.",
              """
              Соответствие: dict ↔ объект {}, list ↔ массив [], str ↔ строка в двойных кавычках, True/False ↔ true/false, None ↔ null.

              В JSON строки только в двойных кавычках: '{"a": 1}' — правильно, "{'a': 1}" — json.JSONDecodeError.

              По умолчанию dumps экранирует не-ASCII символы (\\u0410…). ensure_ascii=False оставляет русский текст как есть, indent=2 делает вывод многострочным и читаемым.
              """,
              [("""\
                import json

                data = {"name": "Ада", "langs": ["Python"], "admin": False, "boss": None}
                text = json.dumps(data, ensure_ascii=False)
                print(text)
                print(json.loads(text)["langs"][0])""", None)],
              ["Путать dumps/loads (строки) и dump/load (файлы).",
               "Одинарные кавычки внутри JSON-строки: это не JSON."]),
        topic("data_re", "Регулярные выражения",
              "Модуль re ищет текст по шаблону: search — первое совпадение, findall — все, sub — замена, fullmatch — вся строка целиком.",
              """
              Основы шаблонов: \\d — цифра, \\w — буква, цифра или _, \\s — пробельный символ, . — любой символ кроме перевода строки, + — один или больше, * — ноль или больше, ? — ноль или один, {3} — ровно три, [a-z] — символ из набора, ^ и $ — начало и конец строки.

              Скобки ( ) создают группу: m.group(1) — её текст. findall с группами возвращает только группы.

              + и * жадные: захватывают как можно больше. +? и *? — ленивые, захватывают как можно меньше.

              Шаблоны пишут в сырых строках r"..." — тогда \\d не нужно экранировать ещё раз.
              """,
              [("""\
                import re

                text = "Order 15: 3 apples, 12 pears"
                print(re.findall(r"\\d+", text))
                print(re.sub(r"\\d+", "#", text))
                m = re.search(r"(\\w+)@(\\w+)\\.com", "mail: ada@lovelace.com")
                print(m.group(1), m.group(2))""", None)],
              ["re.match проверяет только начало строки, re.search ищет везде.",
               "Жадный .+ между тегами захватывает лишнее: <.+> на \"<a><b>\" найдёт всю строку."]),
        topic("data_datetime", "Даты и время",
              "datetime.date и datetime.datetime хранят даты, timedelta — промежутки. Вычитание дат даёт timedelta.",
              """
              date(2024, 2, 28) + timedelta(days=2) учитывает длину месяцев и високосные годы: получится 2024-03-01.

              strftime форматирует: d.strftime("%d.%m.%Y") → «01.03.2024». datetime.strptime("01.03.2024", "%d.%m.%Y") разбирает строку в дату.

              (date2 - date1).days — количество дней между датами.
              """,
              [("""\
                from datetime import date, timedelta

                d = date(2024, 2, 28) + timedelta(days=2)
                print(d, d.strftime("%d.%m.%Y"))
                print((date(2025, 1, 1) - date(2024, 1, 1)).days)""", "2024 — високосный год: 366 дней.")],
              ["Сравнивать даты как строки в формате «дд.мм.гггг»: «02.01.2024» > «01.12.2024» по тексту, хотя раньше по времени."]),
    ],
    tasks=[
        task("t_data_sum_numbers", "Сумма чисел в тексте",
             "Прочитайте строку текста. Найдите в ней все целые числа (в том числе отрицательные, со знаком минус перед цифрами) и выведите их сумму.",
             solution="""\
                import re

                print(sum(int(x) for x in re.findall(r"-?\\d+", input())))""",
             starter="""\
                text = input()
                print(0)""",
             tests=["было 10 яблок, съели 3, осталось 7\n", "температура -5, завтра -2\n", "без чисел\n",
                    "a1b22c333\n"],
             hint="Шаблон r\"-?\\d+\": необязательный минус и одна или больше цифр.", difficulty=2,
             requires=dict(uses=["import"])),
    ],
    levels=[
        predict("py_data_001", "Python → JSON", """\
                import json
                print(json.dumps({"name": "Ada", "ok": True, "tags": None}))""",
                ["{'name': 'Ada', 'ok': True, 'tags': None}", "{\"name\": \"Ada\", \"ok\": True, \"tags\": None}",
                 "{name: Ada, ok: true, tags: null}"], position=2, topic="data_json",
                hint="В JSON строки — в двойных кавычках, True — true, None — null.",
                explanation="dumps переводит в формат JSON: двойные кавычки, true вместо True, null вместо None.",
                feedback={"{'name': 'Ada', 'ok': True, 'tags': None}": "Так печатается словарь Python, а dumps даёт строку JSON.",
                          "{\"name\": \"Ada\", \"ok\": True, \"tags\": None}": "В JSON логические значения и None пишутся по-другому: true, null.",
                          "{name: Ada, ok: true, tags: null}": "Ключи и строки в JSON всегда в двойных кавычках."}),
        fill("py_data_002", "Прочитать JSON", "Превратите строку JSON в словарь",
             """\
             import json
             data = json.{{0}}('{"a": 1}')
             print(data["a"])""", ["loads", "load", "dumps", "dump"], ["loads"],
             topic="data_json", hint="s на конце — от слова string.",
             explanation="loads разбирает строку. load читает из файла, dumps и dump, наоборот, создают JSON.",
             expect="1\n"),
        match("py_data_003", "Регулярные выражения",
              ["re.findall(r'\\d+', text)", "re.search(r'\\d+', text).group()", "re.sub(r'\\d+', '#', text)",
               "len(re.findall(r'[A-Za-z]+', text))", "bool(re.match(r'\\d', text))"],
              setup="""\
                import re
                text = 'Order 15: 3 apples, 12 pears'""",
              topic="data_re", hint="search — первое совпадение, match — только в начале строки.",
              explanation="findall находит все числа, search — первое, sub заменяет каждое число, слов из латинских букв три, а строка начинается с буквы, поэтому match с цифрой не совпадает."),
        typed("py_data_004", "Группы", """\
              import re
              m = re.search(r"(\\w+)@(\\w+)\\.com", "mail: ada@lovelace.com")
              print(m.group(1))
              print(m.group(2))""",
              topic="data_re", hint="Каждая пара скобок — отдельная группа, нумерация с 1.",
              explanation="Первая группа захватывает имя до @, вторая — домен до .com."),
        predict("py_data_005", "Високосный февраль", """\
                from datetime import date, timedelta
                d = date(2024, 2, 28) + timedelta(days=2)
                print(d)""",
                ["2024-02-30", "2024-03-02", "2024-02-29"], position=3, topic="data_datetime",
                hint="2024 — високосный год.",
                explanation="После 28 февраля 2024 идёт 29-е (високосный год), затем 1 марта.",
                feedback={"2024-02-30": "30 февраля не бывает: date учитывает длину месяца.",
                          "2024-03-02": "В 2024 году в феврале 29 дней.",
                          "2024-02-29": "Это +1 день, а прибавили 2."}),
        bug("py_data_006", "Не JSON", """\
            import json
            raw = "{'name': 'Ada'}"
            data = json.loads(raw)
            print(data["name"])""", {1: "raw = '{\"name\": \"Ada\"}'"},
            prompt="Найдите строку с ошибкой", topic="data_json",
            hint="Какие кавычки допустимы в JSON?",
            explanation="В JSON строки и ключи только в двойных кавычках. С одинарными json.loads выбрасывает JSONDecodeError.",
            expect_error="JSONDecodeError"),
        multi("py_data_007", "Формат кода", "Какие строки полностью соответствуют шаблону r\"\\d{3}-\\d{2}\" (проверка re.fullmatch)?",
              ["123-45", "12-345", "123-456", "abc-12", "000-00"], [0, 4],
              check=lambda s: _re.fullmatch(r"\d{3}-\d{2}", s) is not None, topic="data_re",
              hint="Ровно три цифры, дефис, ровно две цифры.",
              explanation="Подходят только 123-45 и 000-00. fullmatch требует, чтобы шаблону соответствовала вся строка.",
              feedback={"12-345": "До дефиса нужно ровно три цифры.",
                        "123-456": "После дефиса ровно две цифры: fullmatch не допускает лишнего.",
                        "abc-12": "\\d — только цифры."}),
        predict("py_data_008", "Жадность", """\
                import re
                print(re.findall(r"<.+?>", "<a><b>"))""",
                ["['<a><b>']", "['a', 'b']", "[]"], position=1, topic="data_re",
                hint="+? — ленивый квантификатор.",
                explanation="+? захватывает как можно меньше, поэтому каждое совпадение заканчивается на ближайшей >.",
                role="challenge", difficulty=3,
                feedback={"['<a><b>']": "Так сработал бы жадный <.+>. Знак ? делает его ленивым.",
                          "['a', 'b']": "Скобки < > входят в шаблон и в результат: групп нет.",
                          "[]": "Совпадения есть: <a> и <b>."}),
        order("py_data_009", "Босс: отчёт по логу", "Соберите программу, которая выведет {\"count\": 2, \"last\": \"timeout\"}",
              ["import json, re",
               "log = \"2024-05-01 ERROR disk full\\n2024-05-01 INFO ok\\n2024-05-02 ERROR timeout\"",
               "errors = re.findall(r\"(\\S+) ERROR (.+)\", log)",
               "report = {\"count\": len(errors), \"last\": errors[-1][1]}",
               "print(json.dumps(report))"],
              topic="data_re", hint="Импорт → данные → поиск → отчёт → JSON.",
              explanation="findall с двумя группами возвращает пары (дата, текст ошибки). . не захватывает перевод строки, поэтому каждая ошибка заканчивается в конце своей строки.",
              role="boss", difficulty=3),
    ],
))
