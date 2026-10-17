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
              ["Голый except: перехватывает всё подряд — опечатки в коде, даже Ctrl+C (KeyboardInterrupt) и sys.exit() — и прячет ошибки.",
               "return внутри finally перекрывает return из try и даже глотает исключение — так не пишут.",
               "Слишком большой блок try: непонятно, какая строка на самом деле упала."]),
        topic("exc_types", "Иерархия исключений",
              "Исключения — классы. except ловит указанный класс и все его подклассы, поэтому важен порядок блоков except.",
              """
              Частые: ValueError (неподходящее значение: int("abc")), TypeError (неподходящий тип: "5" + 5), KeyError и IndexError (нет ключа или индекса), ZeroDivisionError, NameError, AttributeError, FileNotFoundError.

              KeyError и IndexError — подклассы LookupError, почти все — подклассы Exception. except Exception ловит практически всё (кроме KeyboardInterrupt и SystemExit), поэтому его ставят последним: Python проверяет блоки сверху вниз и выполняет первый подходящий.

              Несколько типов в одном блоке — кортежем: except (ValueError, TypeError) as e.

              С Python 3.11 несколько независимых ошибок можно передать сразу — ExceptionGroup, а обработать по типам — блоками except*. Так работают параллельные задачи asyncio.

              Подход EAFP («проще попросить прощения, чем разрешения»): попробовать действие и обработать исключение, вместо множества предварительных проверок.
              """,
              [("""\
                actions = [lambda: [1][5], lambda: {}["k"], lambda: 1 / 0]
                for act in actions:
                    try:
                        act()
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

              Если внутри except возникает новая ошибка, Python сам запоминает исходную в __context__ и покажет обе («During handling of the above exception…»). raise NewError(...) from e делает связь явной: e становится __cause__ («direct cause»). from None скрывает исходную ошибку. Голый raise внутри except пробрасывает текущее исключение дальше.
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
             "В первой строке — число n, далее n строк вида «a b». Для каждой строки выведите a / b ровно с двумя знаками после точки (например, 3.00), а при ошибке — «деление на ноль» или «не число».",
             solution="""\
                n = int(input())
                for _ in range(n):
                    a, b = input().split()
                    try:
                        print(f"{float(a) / float(b):.2f}")
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
        predict("py_exc_001", "Перехват ошибки", """\
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
              def share(x):
                  try:
                      part = 12 / x
                  except ZeroDivisionError:
                      print("ноль")
                  else:
                      print("частное", part)
                  finally:
                      print("готово")

              share(4)
              share(0)""",
              topic="exc_try", hint="else — только без ошибки, finally — всегда.",
              explanation="share(4): ошибки нет — else печатает «частное 3.0», потом finally. share(0): except печатает «ноль», потом finally."),
        bug("py_exc_005", "Не тот except", """\
            menu = ["чай", "кофе"]
            try:
                print(menu[5])
            except KeyError:
                print("нет такой позиции")""", {3: "except IndexError:"},
            prompt="Несуществующая позиция меню должна давать сообщение, а не падение. Найдите строку с ошибкой",
            topic="exc_types", hint="Какое исключение вызывает индекс за пределами списка?",
            explanation="Индекс за пределами списка — IndexError, а не KeyError (тот — для словарей). except KeyError его не ловит, и программа падает.",
            expect_error="IndexError", alt_fixes={2: "    print(menu[-1])"}),
        predict("py_exc_010", "Два типа в одном except", """\
                for raw in ["5", "x", None]:
                    try:
                        print(int(raw) * 2)
                    except (ValueError, TypeError) as e:
                        print("плохо:", type(e).__name__)""",
                ["10\nплохо: ValueError\nплохо: ValueError", "10\nплохо: ValueError", "TypeError"], position=3,
                topic="exc_types", hint="int(None) — это не ValueError. Ловит ли его кортеж исключений?",
                explanation="int(\"x\") — ValueError, int(None) — TypeError. Кортеж в except ловит оба типа, а as e даёт сам объект ошибки.",
                role="practice", difficulty=2,
                feedback={"10\nплохо: ValueError\nплохо: ValueError": "int(None) — TypeError: None вообще не строка и не число.",
                          "10\nплохо: ValueError": "Цикл продолжается: третий элемент None тоже обрабатывается.",
                          "TypeError": "TypeError перехвачен: он есть в кортеже исключений."}),
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
        predict("py_exc_011", "Группы исключений", """\
                try:
                    raise ExceptionGroup("пакет", [ValueError("a"), KeyError("b"), ValueError("c")])
                except* ValueError as group:
                    print("value:", len(group.exceptions))
                except* KeyError as group:
                    print("key:", len(group.exceptions))""",
                ["value: 1", "value: 2", "value: 2\nkey: 0"], position=3, topic="exc_types",
                hint="except* обрабатывает свою часть группы, а остальное передаёт следующим блокам except*.",
                explanation="ExceptionGroup несёт три ошибки. except* ValueError получает подгруппу из двух ValueError, except* KeyError — из одной KeyError. Сработали оба блока.",
                role="challenge", difficulty=4,
                feedback={"value: 1": "except* получает все ValueError группы сразу — их две.",
                          "value: 2": "В отличие от обычного except, блоки except* срабатывают все, у кого есть свои ошибки в группе.",
                          "value: 2\nkey: 0": "except* KeyError получает одну ошибку KeyError из группы."}),
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
                with open("data.txt", "w", encoding="utf-8") as f:
                    f.write("3\\n5\\n8\\n")
                with open("data.txt", encoding="utf-8") as f:
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

                p = Path("docs") / "2023" / "plan.draft.md"
                print(p.name, p.stem, p.suffix, p.parent, sep=" | ")""", None),
               ("""\
                from pathlib import Path

                p = Path("hello.txt")
                p.write_text("Привет!", encoding="utf-8")
                print(p.exists(), p.read_text(encoding="utf-8"))""", None)],
              ["Склеивать пути строками через \"+\" и \"/\": Path делает это правильно на любой системе."]),
        topic("files_csv", "CSV",
              "Модуль csv читает и пишет таблицы: writer.writerow(список), DictReader — строки как словари. Он сам разбирает кавычки и запятые внутри значений.",
              """
              CSV — текст, где значения разделены запятыми. Если значение само содержит запятую, его берут в кавычки: Ада,"Лондон, UK". Поэтому split(",") для CSV ненадёжен.

              csv.writer(f).writerow([...]) записывает строку, csv.reader(f) возвращает списки, csv.DictReader(f) — словари по заголовкам первой строки. Файл для csv открывают с newline="", чтобы не появлялись пустые строки.
              """,
              [("""\
                import csv

                with open("p.csv", "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["name", "city"])
                    writer.writerow(["Ада", "Лондон, UK"])

                with open("p.csv", newline="", encoding="utf-8") as f:
                    print(f.read().splitlines()[1])
                with open("p.csv", newline="", encoding="utf-8") as f:
                    for row in csv.DictReader(f):
                        print(row["city"])""", "Запятая внутри значения не ломает разбор.")],
              ["Разбирать CSV через split(\",\"): значение с запятой развалится на части."]),
    ],
    tasks=[
        task("t_files_reverse", "Обратный порядок",
             "Прочитайте число n и n строк. Запишите строки в файл lines.txt (каждую на своей строке), затем прочитайте файл и выведите его строки в обратном порядке. Решение должно работать через файл: открыть его и записать.",
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
             requires=dict(uses=["with"], calls=["open", "write"])),
    ],
    levels=[
        choice("py_files_001", "Режим «a»", "Что делает режим \"a\" в open(\"log.txt\", \"a\")?",
               ["Открывает только для чтения", "Стирает файл и пишет заново", "Дописывает в конец файла",
                "Создаёт новый файл; если файл уже есть — ошибка"], 2,
               topic="files_open", hint="a — от слова append.",
               explanation="\"a\" (append) дописывает данные в конец, сохраняя старое содержимое; если файла нет, он создаётся.",
               feedback={"Открывает только для чтения": "Это режим \"r\".",
                         "Стирает файл и пишет заново": "Это режим \"w\".",
                         "Создаёт новый файл; если файл уже есть — ошибка": "Это режим \"x\"."}),
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
             with open("log.txt", "w", encoding="utf-8") as f:
                 f.write("a\\n")
             with open("log.txt", "{{0}}", encoding="utf-8") as f:
                 f.write("b\\n")
             with open("log.txt", encoding="utf-8") as f:
                 print(f.read(), end="")""", ["a", "w", "r", "x"], ["a"],
             topic="files_open", hint="Нужен режим дописывания.",
             explanation="Режим \"a\" дописывает в конец. \"w\" стёр бы строку a, \"r\" не разрешает запись, \"x\" требует, чтобы файла не было.",
             expect="a\nb\n"),
        typed("py_files_004", "Сумма из файла", """\
              with open("data.txt", "w", encoding="utf-8") as f:
                  f.write("3\\n5\\n8\\n")
              total = 0
              count = 0
              with open("data.txt", encoding="utf-8") as f:
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
              explanation="read() и read_text() возвращают весь текст. join склеивает строки, по которым идёт цикл. readlines даёт список, readline — только первую строку. (В варианте с голым open файл не закрывается явно — в рабочем коде нужен with.)",
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
        predict("py_files_010", "Запятая внутри значения", """\
                import csv

                with open("t.csv", "w", newline="", encoding="utf-8") as f:
                    csv.writer(f).writerow(["Грейс", "Нью-Йорк, США", 85])

                with open("t.csv", newline="", encoding="utf-8") as f:
                    line = f.readline().strip()
                    print(len(line.split(",")))
                with open("t.csv", newline="", encoding="utf-8") as f:
                    print(len(next(csv.reader(f))))""",
                ["3\n3", "4\n4", "3\n4"], position=1, topic="files_csv",
                hint="csv.writer берёт значение с запятой в кавычки. Знает ли о кавычках split?",
                explanation="В файле строка Грейс,\"Нью-Йорк, США\",85. split(\",\") режет и внутри кавычек — 4 части. csv.reader понимает кавычки и возвращает 3 значения.",
                role="practice", difficulty=3,
                feedback={"3\n3": "split ничего не знает о кавычках и режет по каждой запятой.",
                          "4\n4": "csv.reader учитывает кавычки: значений три.",
                          "3\n4": "Наоборот: split даёт 4 части, csv.reader — 3 значения."}),
        predict("py_files_009", "Босс: после with", """\
                with open("t.txt", "w", encoding="utf-8") as f:
                    f.write("hi")
                print(f.closed)
                try:
                    f.write("again")
                except ValueError as e:
                    print("ошибка:", e)""",
                ["False", "True", "False\nошибка: I/O operation on closed file."], position=0,
                topic="files_open", hint="Что делает with с файлом при выходе из блока?",
                explanation="После блока with файл закрыт: f.closed — True, а запись в закрытый файл вызывает ValueError.",
                role="boss", difficulty=3,
                feedback={"False": "with закрывает файл при выходе из блока.",
                          "True": "Запись в закрытый файл не игнорируется молча: ValueError.",
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
              import math → math.sqrt(16). from math import sqrt → sqrt(16). import datetime as dt — короткий псевдоним.

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

              deque — двусторонняя очередь: append/appendleft и pop/popleft за O(1). deque(maxlen=3) хранит не больше 3 элементов: при append лишний выталкивается слева, при appendleft — справа.

              OrderedDict — словарь с дополнительными операциями над порядком: move_to_end(k) переносит ключ в конец. ChainMap(user, defaults) ищет ключ сначала в первом словаре, потом во втором — удобно для настроек.

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
                c = Counter("mississippi")
                print(c.most_common(2))""",
                ["[('s', 4), ('i', 4)]", "{'i': 4, 's': 4}", "['i', 's']"], position=1, topic="std_collections",
                hint="i и s встречаются по 4 раза. Кто встретился раньше?",
                explanation="i и s — по 4 раза, p — 2, m — 1. При равенстве most_common сохраняет порядок первого появления: i раньше s.",
                feedback={"[('s', 4), ('i', 4)]": "При равных счётчиках порядок — по первому появлению: i появляется раньше s.",
                          "{'i': 4, 's': 4}": "most_common возвращает список пар (элемент, количество).",
                          "['i', 's']": "Вместе с элементами возвращаются и количества."}),
        fill("py_std_003", "Группы по букве", "Сгруппируйте слова по первой букве",
             """\
             from collections import defaultdict
             groups = defaultdict({{0}})
             for word in ["kiwi", "kale", "plum"]:
                 groups[word[0]].append(word)
             print(dict(groups))""", ["list", "dict", "set", "int"], ["list"],
             topic="std_collections", hint="У значения по умолчанию должен быть метод append.",
             explanation="defaultdict(list) создаёт пустой список для нового ключа, и append сразу работает.",
             expect="{'k': ['kiwi', 'kale'], 'p': ['plum']}\n"),
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
        predict("py_std_007", "Разорванные группы", """\
                from itertools import groupby
                words = ["apple", "bob", "avocado", "banana"]
                for letter, group in groupby(words, key=lambda w: w[0]):
                    print(letter, len(list(group)), end="; ")""",
                ["a 2; b 2; ", "a 1; b 1; ", "a 3; b 1; "], position=3, topic="std_itertools",
                hint="groupby объединяет только соседние элементы с одинаковым ключом.",
                explanation="groupby начинает новую группу при каждой смене ключа: a, b, a, b — четыре группы по одному слову. Чтобы получить a 2; b 2, список сначала сортируют по тому же ключу.",
                role="challenge", difficulty=3,
                feedback={"a 2; b 2; ": "Так было бы после сортировки. groupby объединяет только соседей.",
                          "a 1; b 1; ": "Групп четыре: после b снова идёт a.",
                          "a 3; b 1; ": "Слова на a не стоят рядом — они попадают в разные группы."}),
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

              Ключи объектов JSON — всегда строки: число-ключ после dumps/loads станет строкой. Кортеж превращается в список.
              """,
              [("""\
                import json

                data = {"name": "Ада", "langs": ["Python"], "admin": False, "boss": None}
                text = json.dumps(data, ensure_ascii=False)
                print(text)
                print(json.loads(text)["langs"][0])""", None),
               ("""\
                import json

                with open("cfg.json", "w", encoding="utf-8") as f:
                    json.dump({"size": 3, "tags": ("a", "b")}, f)
                with open("cfg.json", encoding="utf-8") as f:
                    print(json.load(f))""", "dump/load работают с файлами; кортеж стал списком.")],
              ["Путать dumps/loads (строки) и dump/load (файлы).",
               "Ждать, что числовые ключи переживут JSON: {1: 'a'} вернётся как {'1': 'a'}.",
               "Одинарные кавычки внутри JSON-строки: это не JSON."]),
        topic("data_re", "Регулярные выражения",
              "Модуль re ищет текст по шаблону: search — первое совпадение, findall — все, sub — замена, fullmatch — вся строка целиком.",
              """
              Основы шаблонов: \\d — цифра, \\w — буква, цифра или _, \\s — пробельный символ, . — любой символ кроме перевода строки, + — один или больше, * — ноль или больше, ? — ноль или один, {3} — ровно три, [a-z] — символ из набора, ^ и $ — начало и конец строки.

              Скобки ( ) создают группу: m.group(1) — её текст. findall с группами возвращает только группы.

              + и * жадные: захватывают как можно больше. +? и *? — ленивые, захватывают как можно меньше.

              Шаблоны пишут в сырых строках r"..." — тогда \\d не нужно экранировать ещё раз; без r Python 3.12 предупреждает о неизвестной escape-последовательности (SyntaxWarning).

              \\w в Python 3 включает и кириллицу. re.compile(шаблон, флаги) заранее готовит шаблон; флаги: re.I — без учёта регистра, re.M — ^ и $ для каждой строки. (?P<имя>...) — именованная группа: m["имя"].
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

              strftime форматирует: d.strftime("%d.%m.%Y") → «01.03.2024». datetime.strptime("01.03.2024", "%d.%m.%Y") разбирает строку в datetime (.date() — только дата).

              Время с часовым поясом: datetime(..., tzinfo=timezone.utc); astimezone переводит в другой пояс. Сравнивать время с поясом и без — TypeError.

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
             "Прочитайте строку текста. Найдите в ней все целые числа (в том числе отрицательные, со знаком минус перед цифрами) и выведите их сумму. Минус, стоящий сразу перед цифрами, относится к числу: «5-3» — это 5 и -3; точка разделяет числа: «1.5» — это 1 и 5.",
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
              m = re.search(r"(\\w+)@(\\w+)\\.org", "кому: grace@hopper.org")
              print(m.group(1))
              print(m.group(2))""",
              topic="data_re", hint="Каждая пара скобок — отдельная группа, нумерация с 1.",
              explanation="Первая группа захватывает имя до @, вторая — домен до .org."),
        predict("py_data_005", "Обычный февраль", """\
                from datetime import date, timedelta
                d = date(2023, 2, 27) + timedelta(days=2)
                print(d)""",
                ["2023-02-29", "2023-03-02", "2023-02-28"], position=3, topic="data_datetime",
                hint="2023 — не високосный год.",
                explanation="После 27 февраля 2023 идёт 28-е, а 29 февраля в 2023 году нет — следующий день 1 марта.",
                feedback={"2023-02-29": "В 2023 году в феврале 28 дней: такой даты нет.",
                          "2023-03-02": "Это +3 дня, а прибавили 2.",
                          "2023-02-28": "Это +1 день, а прибавили 2."}),
        bug("py_data_006", "Строка или файл", """\
            import json
            raw = '{"name": "Ada"}'
            data = json.load(raw)
            print(data["name"])""", {2: "data = json.loads(raw)"},
            prompt="Найдите строку с ошибкой", topic="data_json",
            hint="Какая функция json разбирает строку, а какая — файл?",
            explanation="json.load ждёт файл и вызывает у аргумента .read() — у строки такого метода нет: AttributeError. Для строки нужен json.loads.",
            expect_error="AttributeError", alt_fixes={1: "raw = {'name': 'Ada'}"}),
        predict("py_data_010", "Ключи JSON", """\
                import json
                data = json.loads(json.dumps({1: "a", "pair": (1, 2)}))
                print(data, 1 in data)""",
                ["{1: 'a', 'pair': (1, 2)} True", "{'1': 'a', 'pair': [1, 2]} True", "{1: 'a', 'pair': [1, 2]} True"],
                position=3, topic="data_json",
                hint="В JSON ключи объектов — только строки, а кортежей нет вообще.",
                explanation="dumps превратил ключ 1 в строку «1», а кортеж — в массив. После loads ключ остался строкой, поэтому 1 in data — False.",
                role="practice", difficulty=3,
                feedback={"{1: 'a', 'pair': (1, 2)} True": "JSON не хранит числовые ключи и кортежи.",
                          "{'1': 'a', 'pair': [1, 2]} True": "Ключ стал строкой «1», а 1 — число: in даёт False.",
                          "{1: 'a', 'pair': [1, 2]} True": "Ключ после JSON — строка «1»."}),
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
