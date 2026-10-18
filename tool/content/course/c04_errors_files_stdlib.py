"""Модули 18–21: исключения, файлы, стандартная библиотека, текст и данные."""
import re as _re
from bclib import (choice, fill, match, multi, order, predict, bug, typed, topic, task, run, pitfall,
                   categorize, fix_line)


def runs(code):
    return run(code).ok


def error_of(code):
    return run(code).error


def output_of(code):
    return run(code).out


MODULES = []

# -------------------------------------------------------------- exceptions
ERROR_SNIPPETS = ["int('abc')", "[1, 2][5]", "{'a': 1}['b']", "1 / 0", "'5' + 5", "undefined_name"]

MODULES.append(dict(
    id="exceptions", title="Исключения", description="try, except, raise", icon="🛟",
    topics=[
        topic("exc_traceback", "Как читать трассировку",
              "Трассировка — отчёт Python об ошибке: что пошло не так, на какой строке и через какие вызовы.",
              """
              Когда программа падает, Python печатает трассировку (traceback). Это не приговор, а подробная подсказка, где искать ошибку.

              ## Из чего она состоит

              ```syntax
              Traceback (most recent call last):
                File "файл.py", line номер, in функция
                  строка_кода
              ТипОшибки: сообщение
              ```

              Читают снизу вверх:

              1. Последняя строка — тип ошибки и сообщение. С неё начинают.
              2. Над ней — строка кода, на которой программа упала, и её номер.
              3. Выше — цепочка вызовов, которая привела к этой строке. Первый вызов — сверху.

              С Python 3.11 под строкой кода стоят значки `^`: они указывают на выражение с ошибкой.

              В приложении программа запускается из памяти, а не из файла на диске. Поэтому строк кода и значков `^` в трассировке нет, остаются номера строк и имена функций.

              ## Частые типы

              | Тип | Что случилось |
              |---|---|
              | {`NameError`} | имя не объявлено |
              | {`TypeError`} | неподходящий тип |
              | {`ValueError`} | неподходящее значение |
              | {`IndexError`} | нет такого индекса |
              | {`KeyError`} | нет такого ключа |
              | {`ZeroDivisionError`} | деление на ноль |
              | {`AttributeError`} | нет такого атрибута |
              | {`SyntaxError`} | код не по правилам |

              Как эти типы связаны между собой — в теме [[exc_types|Иерархия исключений]].

              ## Где искать причину

              Трассировка показывает строку, где ошибка проявилась. Причина бывает выше: `None` вернула функция без `return`, а упало сложение. Если строка выглядит правильной, проверьте, откуда взялись её значения.

              `SyntaxError` появляется до запуска: Python не может прочитать файл, и не выполняется ни одна строка. Перехватить ошибку и продолжить работу позволяет [[exc_try|try / except]].
              """,
              [("""\
                try:
                    int("12a")
                except ValueError as e:
                    print(type(e).__name__)
                    print(e)""",
                "Тип и сообщение — то же, что в последней строке трассировки"),
               ("""\
                import traceback

                def average(marks):
                    return sum(marks) / len(marks)

                def report(marks):
                    return average(marks)

                try:
                    report([])
                except ZeroDivisionError:
                    print(traceback.format_exc(), end="")""",
                "Снизу: ошибка в average, её вызвала report, её — сам модуль"),
               ("""\
                def find_user(name):
                    if name == "ada":
                        return {"age": 36}

                user = find_user("bob")
                try:
                    print(user["age"])
                except TypeError as e:
                    print(e)""",
                "Упало чтение user, а причина выше: функция вернула None")],
              [pitfall("Читать трассировку сверху: первая строка — лишь начало цепочки вызовов. Начинайте с последней строки."),
               pitfall("Исправлять строку из трассировки, не проверив значения: `NoneType` в сообщении значит, что `None` пришло раньше.",
                       bad='''
                           user = find_user("bob")
                           print(user["age"])''',
                       good='''
                           user = find_user("bob")
                           if user is not None:
                               print(user["age"])''')]),
        topic("exc_try", "try / except / else / finally",
              "`try` выполняет код, который может упасть, а `except` перехватывает ошибку, и программа продолжает работу.",
              """
              Некоторые ошибки нельзя исключить заранее: пользователь ввёл буквы вместо числа, файла нет, сеть недоступна. `try` позволяет обработать такую ошибку, а не падать с [[exc_traceback|трассировкой]].

              ## Как записать

              ```syntax
              try:
                  код_который_может_упасть
              except ТипОшибки as e:
                  действия_при_ошибке
              else:
                  действия_если_ошибки_не_было
              finally:
                  действия_в_любом_случае
              ```

              `else` и `finally` необязательны, блоков `except` может быть несколько.

              ## Как это выполняется

              1. Python выполняет блок `try`.
              2. При ошибке остаток `try` пропускается, Python ищет подходящий `except`.
              3. Если ошибки не было, выполняется `else`.
              4. `finally` выполняется в любом случае — даже после `return` внутри `try`.

              Если подходящего `except` нет, ошибка идёт дальше, как будто `try` не было.

              ## Объект ошибки

              `except ValueError as e` кладёт в `e` объект ошибки. `print(e)` выводит сообщение, `type(e).__name__` — название типа.

              ## Что выбрать

              - В `try` — только опасную строку, код после успеха — в `else`.
              - В `finally` — то, что нужно при любом исходе. Для файлов удобнее [[files_open|with]].
              - Ловите конкретный тип, а не всё подряд: какие бывают типы — в теме [[exc_types|Иерархия исключений]].
              """,
              [("""\
                text = "12a"
                try:
                    n = int(text)
                    print("число", n)
                except ValueError:
                    print("не число:", text)
                print("работаем дальше")""",
                "После ошибки остаток try пропущен, но программа не упала"),
               ("""\
                try:
                    int("12a")
                except ValueError as e:
                    print(type(e).__name__)
                    print(e)""",
                "В e — объект ошибки: у него есть тип и сообщение"),
               ("""\
                for raw in ["пять", "0", "4"]:
                    try:
                        share = 20 / int(raw)
                    except ValueError:
                        print(raw, "— не число")
                    except ZeroDivisionError:
                        print("на ноль делить нельзя")
                    else:
                        print("по", share)""",
                "Каждая ошибка попала в свой except, else — только при успехе")],
              [pitfall("Голый `except` ловит всё, даже опечатки в именах и Ctrl+C, и прячет настоящие ошибки.",
                       bad='''
                           try:
                               n = int(text)
                           except:
                               n = 0''',
                       good='''
                           try:
                               n = int(text)
                           except ValueError:
                               n = 0'''),
               pitfall("Большой блок `try` прячет, какая строка упала, и может перехватить чужую ошибку.",
                       bad='''
                           try:
                               n = int(text)
                               total = price * n
                           except ValueError:
                               total = 0''',
                       good='''
                           try:
                               n = int(text)
                           except ValueError:
                               n = 0
                           total = price * n'''),
               pitfall("Если `int` упал, `n` так и не создана: следующая строка даст NameError.",
                       bad='''
                           try:
                               n = int(text)
                           except ValueError:
                               print("не число")
                           print(n * 2)''',
                       good='''
                           try:
                               n = int(text)
                           except ValueError:
                               n = 0
                           print(n * 2)''')]),
        topic("exc_types", "Иерархия исключений",
              "Исключения — классы, связанные наследованием: `except` ловит указанный тип и все его подтипы.",
              """
              Ошибки в Python — не просто список названий. Они образуют дерево: `KeyError` и `IndexError` — разновидности общей ошибки поиска `LookupError`. Поэтому можно перехватить сразу целое семейство.

              ## Как устроено дерево

              - `BaseException` — корень, от него идут `KeyboardInterrupt` и `SystemExit`;
              - `Exception` — почти все обычные ошибки;
              - `LookupError` — `KeyError` и `IndexError`;
              - `ArithmeticError` — `ZeroDivisionError` и другие ошибки вычислений;
              - `OSError` — ошибки системы, например `FileNotFoundError`.

              Связь «тип — подтип» — это [[inh_basics|наследование]] классов. Как объявить свой тип — в теме [[exc_raise|raise и свои исключения]].

              ## Как Python выбирает except

              1. Проверяет блоки `except` сверху вниз.
              2. Блок подходит, если ошибка — указанного типа или его подтипа.
              3. Выполняется первый подходящий блок, остальные пропускаются.

              Поэтому общий тип ставят последним: `except Exception` перед `except ValueError` перехватит всё сам.

              ## Несколько типов в одном блоке

              Кортеж типов: `except (ValueError, TypeError) as e`. Подходит, когда реакция на обе ошибки одинаковая.

              ## Группы ошибок

              С Python 3.11 несколько ошибок можно выбросить разом — `ExceptionGroup`. Их обрабатывают блоками `except*`: каждый получает свою часть группы. Так работают параллельные задачи в [[async_tasks|asyncio]].
              """,
              [("""\
                for cls in KeyError.__mro__:
                    print(cls.__name__)""",
                "Цепочка типов от KeyError до самого корня"),
               ("""\
                def find(data, key):
                    try:
                        return data[key]
                    except LookupError:
                        return "нет"

                print(find([10, 20], 5))
                print(find({"a": 1}, "b"))""",
                "Один except LookupError поймал и IndexError, и KeyError"),
               ("""\
                try:
                    int("x")
                except Exception:
                    print("что-то пошло не так")
                except ValueError:
                    print("не число")""",
                "Первым подошёл общий Exception, до ValueError дело не дошло"),
               ("""\
                for x in [10, "5", 0]:
                    try:
                        print(100 // x)
                    except (TypeError, ZeroDivisionError) as e:
                        print("пропуск:", type(e).__name__)""",
                "Кортеж в except ловит оба типа")],
              [pitfall("Общий `except Exception` выше `ValueError` перехватит всё сам: второй блок не сработает никогда.",
                       bad='''
                           try:
                               n = int(s)
                           except Exception:
                               n = -1
                           except ValueError:
                               n = 0''',
                       good='''
                           try:
                               n = int(s)
                           except ValueError:
                               n = 0
                           except Exception:
                               n = -1'''),
               pitfall("Типы через запятую без скобок — SyntaxError: multiple exception types must be parenthesized.",
                       bad='''
                           try:
                               n = int(s)
                           except ValueError, TypeError:
                               n = 0''',
                       good='''
                           try:
                               n = int(s)
                           except (ValueError, TypeError):
                               n = 0''', syntax_error=True),
               "Ждать, что `except Exception` поймает Ctrl+C: `KeyboardInterrupt` — подтип `BaseException`, а не `Exception`."]),
        topic("exc_raise", "raise и свои исключения",
              "`raise` сообщает об ошибке из своего кода, а собственный класс исключения позволяет ловить её отдельно.",
              """
              Функция не всегда может выполнить работу: продать больше, чем есть на складе, или записать возраст -5. Вернуть «особое» значение вроде -1 ненадёжно — его легко не заметить. Правильнее выбросить исключение.

              ## Как записать

              ```syntax
              raise ТипОшибки("сообщение")
              ```

              `raise` сразу прерывает функцию. Ошибка поднимается к вызывающему коду, пока её не перехватит [[exc_try|try / except]]. Если её никто не перехватил, программа падает.

              Для неверных данных подходит готовый `ValueError`, для неверного типа — `TypeError`.

              ## Своё исключение

              ```syntax
              class ИмяОшибки(Exception):
                  pass
              ```

              Такой класс наследует `Exception` и ведёт себя как любая ошибка. Зато его можно перехватить отдельно от остальных: `except OutOfStock`. Как устроены классы и наследование — в теме [[inh_basics|Наследование и super()]].

              ## Ошибка внутри except

              Голый `raise` внутри `except` пробрасывает текущую ошибку дальше — например, после записи в лог.

              `raise НоваяОшибка(...) from e` заменяет ошибку более понятной и сохраняет исходную как причину. В трассировке будут обе. {`from None`} скрывает исходную.
              """,
              [("""\
                def set_age(age):
                    if age < 0:
                        raise ValueError("возраст < 0")
                    return age

                print(set_age(30))
                try:
                    set_age(-5)
                except ValueError as e:
                    print("Ошибка:", e)""",
                "raise прервал функцию, ошибку перехватил вызывающий код"),
               ("""\
                class OutOfStock(Exception):
                    pass

                def buy(stock, qty):
                    if qty > stock:
                        raise OutOfStock(f"осталось {stock}")
                    return stock - qty

                try:
                    buy(3, 5)
                except OutOfStock as e:
                    print("Нельзя:", e)""",
                "Своё исключение перехвачено по имени класса"),
               ("""\
                def parse_age(text):
                    try:
                        return int(text)
                    except ValueError as e:
                        msg = f"плохой возраст: {text}"
                        raise ValueError(msg) from e

                try:
                    parse_age("abc")
                except ValueError as e:
                    print(e)
                    print(repr(e.__cause__))""",
                "Новая ошибка понятнее, а исходная сохранена в __cause__"),
               ("""\
                def risky():
                    try:
                        return 1 / 0
                    except ZeroDivisionError:
                        print("пишем в лог")
                        raise

                try:
                    risky()
                except ZeroDivisionError:
                    print("поймали снаружи")""",
                "Голый raise передал ту же ошибку дальше")],
              [pitfall("`raise` без аргумента вне `except` — RuntimeError: No active exception to reraise.",
                       bad="raise", good='raise ValueError("нет данных")'),
               pitfall("Код ошибки вроде `-1` легко пропустить: его сложат с другими числами без всякого сообщения.",
                       bad='''
                           if qty > stock:
                               return -1''',
                       good='''
                           if qty > stock:
                               raise OutOfStock("мало товара")'''),
               pitfall("Своё исключение от `BaseException` не поймает `except Exception`. Наследуйте `Exception`.",
                       bad='''
                           class AppError(BaseException):
                               pass''',
                       good='''
                           class AppError(Exception):
                               pass''')]),
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
              topic="exc_traceback", hint="Неверное значение — ValueError, неверный тип — TypeError.",
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
    id="files", title="Файлы", description="open, with, pathlib, bytes", icon="📄",
    topics=[
        topic("files_open", "open и with",
              "`open` открывает файл для чтения или записи, а `with` гарантированно закрывает его после работы.",
              """
              Переменные исчезают, когда программа завершается. Чтобы сохранить результат — список дел, рекорд, отчёт, — его записывают в файл, а при следующем запуске читают обратно.

              ## Как записать

              ```syntax
              with open(путь, режим, encoding="utf-8") as f:
                  работа_с_файлом
              ```

              - `путь` — имя файла: `"todo.txt"` ищется в текущей папке.
              - `f` — объект файла. Методы чтения — в теме [[files_read|Чтение построчно]].
              - `f.write(текст)` пишет строку как есть, перевод строки `\\n` добавляют сами.

              ## Режимы

              | Режим | Что делает |
              |---|---|
              | {`"r"`} | чтение, по умолчанию |
              | {`"w"`} | запись, файл очищается |
              | {`"a"`} | дописывание в конец |
              | {`"x"`} | только новый файл |
              | {`"b"`} | добавка: двоичный режим |

              Если файла нет, `"r"` даёт [[exc_types|FileNotFoundError]], а `"w"` и `"a"` создают его. `"x"` даёт FileExistsError, если файл уже есть.

              ## Кодировка

              Для текста указывайте `encoding="utf-8"`. Без него Python берёт кодировку системы, и русский текст на другом компьютере может прочитаться неверно.

              ## Зачем with

              После блока `with` файл закрыт, даже если внутри случилась ошибка. Без `with` нужен `f.close()`, и при ошибке до него файл останется открытым, а часть записанного не попадёт на диск. Как это устроено — в теме [[ctx_protocol|Протокол with]].
              """,
              [("""\
                path = "todo.txt"
                with open(path, "w", encoding="utf-8") as f:
                    f.write("купить хлеб\\n")
                    f.write("позвонить маме\\n")

                with open(path, encoding="utf-8") as f:
                    print(f.read(), end="")""",
                "Перевод строки \\n write не добавляет, его пишут в тексте"),
               ("""\
                path = "game.log"
                enc = "utf-8"
                with open(path, "w", encoding=enc) as f:
                    f.write("старт\\n")
                with open(path, "a", encoding=enc) as f:
                    f.write("уровень 2\\n")
                with open(path, encoding=enc) as f:
                    print(f.read(), end="")
                with open(path, "w", encoding=enc) as f:
                    f.write("заново\\n")
                with open(path, encoding=enc) as f:
                    print(f.read(), end="")""",
                "«a» дописал строку, а «w» стёр всё и начал заново"),
               ("""\
                try:
                    with open("no.txt", encoding="utf-8") as f:
                        print(f.read())
                except FileNotFoundError as e:
                    print("нет файла:", e.filename)""",
                "Режим «r» не создаёт файл: FileNotFoundError")],
              [pitfall("Режим `\"w\"` стирает файл в момент открытия, даже если ничего не записать.",
                       bad='open(path, "w", encoding="utf-8")', good='open(path, "a", encoding="utf-8")'),
               pitfall("`write` принимает только строку: TypeError: write() argument must be str, not int.",
                       bad="f.write(42)", good="f.write(str(42))"),
               pitfall("Без `encoding` берётся кодировка системы: на другом компьютере текст прочитается с искажениями.",
                       bad="open(path)", good='open(path, encoding="utf-8")')]),
        topic("files_read", "Чтение построчно",
              "Файл читают целиком через `read`, списком строк через `readlines` или по одной строке в цикле `for`.",
              """
              Данные в текстовых файлах обычно идут по строкам: одна строка — одна запись, число или имя. Поэтому файл чаще читают построчно.

              ## Способы чтения

              - `f.read()` — весь текст одной строкой;
              - `f.readline()` — следующая строка;
              - `f.readlines()` — список всех строк;
              - `for line in f:` — строки по одной в цикле.

              Файл читается с текущего места. После `read()` всё уже прочитано, и повторный `read()` вернёт пустую строку.

              ## Перевод строки в конце

              Каждая прочитанная строка заканчивается символом `\\n`, кроме, возможно, последней. Перед сравнением его убирают: `line.strip()` или `line.rstrip("\\n")`.

              `int(" 42\\n")` работает и без этого: `int` пропускает пробелы и переводы строк по краям.

              ## Что выбрать

              - Файл небольшой и нужен целиком — `read()`.
              - Нужен список строк без `\\n` — `f.read().splitlines()`.
              - Файл большой — цикл `for line in f`.

              Цикл держит в памяти одну строку за раз — это пример [[gen_lazy|ленивых вычислений]].
              """,
              [("""\
                path = "pets.txt"
                with open(path, "w", encoding="utf-8") as f:
                    f.write("кот\\nпёс\\nёж\\n")

                with open(path, encoding="utf-8") as f:
                    lines = f.readlines()
                print(lines)""",
                "Каждая строка из readlines заканчивается на \\n"),
               ("""\
                path = "answers.txt"
                with open(path, "w", encoding="utf-8") as f:
                    f.write("да\\nнет\\nда\\n")

                yes = 0
                with open(path, encoding="utf-8") as f:
                    for line in f:
                        if line.strip() == "да":
                            yes += 1
                print(yes)""",
                "strip убрал \\n, и сравнение с «да» сработало"),
               ("""\
                path = "team.txt"
                with open(path, "w", encoding="utf-8") as f:
                    f.write("Ада\\nЛинус")

                with open(path, encoding="utf-8") as f:
                    text = f.read()
                    again = f.read()
                print(text.splitlines())
                print(repr(again))""",
                "splitlines убрал переводы строк; второй read вернул пустую строку")],
              [pitfall("Строка из файла содержит `\\n`, поэтому `\"да\\n\" == \"да\"` — `False`.",
                       bad='''
                           if line == "да":
                               yes += 1''',
                       good='''
                           if line.strip() == "да":
                               yes += 1'''),
               pitfall("Второй проход по тому же файлу пуст: файл уже прочитан до конца.",
                       bad='''
                           total = sum(int(x) for x in f)
                           count = len(f.readlines())''',
                       good='''
                           lines = f.readlines()
                           total = sum(int(x) for x in lines)
                           count = len(lines)''')]),
        topic("files_pathlib", "pathlib.Path",
              "`Path` — путь к файлу в виде объекта: его склеивают через `/`, разбирают на части и читают файл одной строкой.",
              """
              Пути на разных системах пишутся по-разному: `docs/a.txt` в Linux и macOS, `docs\\a.txt` в Windows. Склеивать их строками ненадёжно. `Path` из модуля `pathlib` делает это правильно на любой системе.

              ## Как записать

              ```syntax
              from pathlib import Path

              путь = Path("папка") / "подпапка" / "файл.txt"
              ```

              Оператор `/` склеивает части пути. Слева должен стоять `Path`, справа можно строку.

              ## Части пути

              | Атрибут | Для {`a/b/plan.md`} |
              |---|---|
              | {`name`} | {`plan.md`} |
              | {`stem`} | {`plan`} |
              | {`suffix`} | {`.md`} |
              | {`parent`} | {`a/b`} |

              ## Файлы без open

              - `p.read_text(encoding="utf-8")` — прочитать весь текст;
              - `p.write_text(текст, encoding="utf-8")` — записать текст;
              - `p.exists()` — есть ли такой путь;
              - `p.mkdir(parents=True, exist_ok=True)` — создать папку;
              - `p.glob("*.txt")` — найти файлы по шаблону.

              Эти методы сами открывают и закрывают файл. `write_text` перезаписывает файл целиком. `Path` можно передать и в [[files_open|open]].
              """,
              [("""\
                from pathlib import Path

                p = Path("game") / "saves" / "slot1.json"
                print(p)
                print(p.name)
                print(p.suffix)
                print(p.parent)""",
                "/ склеил путь, а атрибуты разобрали его на части"),
               ("""\
                from pathlib import Path

                p = Path("hello.txt")
                print(p.exists())
                p.write_text("Привет", encoding="utf-8")
                print(p.exists())
                print(p.read_text(encoding="utf-8"))""",
                "write_text создал файл, read_text прочитал его без open"),
               ("""\
                from pathlib import Path

                folder = Path("notes")
                folder.mkdir(exist_ok=True)
                for name in ["b.txt", "a.txt", "c.md"]:
                    (folder / name).write_text("")

                for p in sorted(folder.glob("*.txt")):
                    print(p.name)""",
                "mkdir создал папку, glob нашёл только файлы .txt")],
              [pitfall("Склейка строками зависит от системы и легко теряет разделитель между частями.",
                       bad='path = folder + "/" + name', good="path = Path(folder) / name"),
               pitfall("`/` между двумя строками — TypeError: unsupported operand type(s) for /: 'str' and 'str'.",
                       bad='"docs" / "a.txt"', good='Path("docs") / "a.txt"'),
               pitfall("`mkdir` для существующей папки — FileExistsError. `exist_ok=True` это разрешает.",
                       bad="folder.mkdir()", good="folder.mkdir(exist_ok=True)")]),
        topic("files_csv", "CSV",
              "Модуль `csv` читает и записывает таблицы и сам разбирает кавычки и запятые внутри значений.",
              """
              CSV — простой формат таблиц: одна строка текста — одна строка таблицы, значения разделены запятыми. В CSV выгружают данные из Excel, банков, интернет-магазинов.

              ## Почему не split

              Если значение само содержит запятую, его берут в кавычки: `Ада,"Лондон, UK"`. `split(",")` об этом не знает и разрежет значение пополам. Модуль `csv` кавычки понимает.

              ## Как записать

              ```syntax
              import csv

              with open(путь, "w", newline="", encoding="utf-8") as f:
                  csv.writer(f).writerow(список_значений)

              with open(путь, newline="", encoding="utf-8") as f:
                  for строка in csv.reader(f):
                      действия
              ```

              `newline=""` нужен для `csv`: без него в Windows между строками появятся пустые.

              ## Чтение и запись

              - `csv.reader(f)` — каждая строка как список;
              - `csv.DictReader(f)` — как словарь с ключами из первой строки;
              - `csv.writer(f)` — `writerow` пишет одну строку, `writerows` — много.

              Все значения читаются строками. Числа переводят сами: `int(row["age"])`.
              """,
              [("""\
                import csv

                opts = dict(newline="", encoding="utf-8")
                with open("team.csv", "w", **opts) as f:
                    w = csv.writer(f)
                    w.writerow(["name", "city"])
                    w.writerow(["Ада", "Лондон, UK"])

                with open("team.csv", encoding="utf-8") as f:
                    print(f.read(), end="")""",
                "Значение с запятой writer сам взял в кавычки"),
               ("""\
                import csv

                line = 'Ада,"Лондон, UK",36'
                print(line.split(","))
                print(next(csv.reader([line])))""",
                "split разрезал город пополам, csv.reader — нет"),
               ("""\
                import csv

                opts = dict(newline="", encoding="utf-8")
                with open("scores.csv", "w", **opts) as f:
                    f.write("name,score\\nАда,90\\nЛинус,75\\n")

                total = 0
                with open("scores.csv", **opts) as f:
                    for row in csv.DictReader(f):
                        total += int(row["score"])
                print(total)""",
                "DictReader дал словари по заголовку, числа переведены через int")],
              [pitfall("`split(\",\")` режет и внутри кавычек: `\"Лондон, UK\"` развалится на два значения.",
                       bad='row = line.split(",")',
                       good="row = next(csv.reader([line]))"),
               pitfall("Без `newline=\"\"` в Windows между строками CSV появятся пустые строки.",
                       bad='open(path, "w", encoding="utf-8")',
                       good='open(path, "w", newline="", encoding="utf-8")'),
               pitfall("Значения из CSV — строки: TypeError: unsupported operand type(s) for +=: 'int' and 'str'.",
                       bad='total += row["score"]', good='total += int(row["score"])')]),
        topic("files_bytes", "Байты и кодировки",
              "`bytes` — последовательность чисел от 0 до 255; кодировка задаёт, как текст `str` превращается в байты и обратно.",
              """
              Диск и сеть хранят не буквы, а байты. Текст перед записью кодируют в байты, а при чтении декодируют обратно. Картинки, архивы и звук — только байты, текста в них нет.

              ## Как записать

              ```syntax
              данные = строка.encode("utf-8")
              строка = данные.decode("utf-8")

              with open(путь, "rb") as f:
                  данные = f.read()
              ```

              Литерал байтов пишут с буквой `b`: `b"PNG"`. Внутри — только латиница и коды вида `\\xd0`. Элемент `bytes` по индексу — число: `b"A"[0]` даёт `65`.

              ## UTF-8: разная длина

              UTF-8 — самая распространённая кодировка. Символ занимает в ней от 1 до 4 байт:

              | Символ | Байт в UTF-8 |
              |---|---|
              | {`a`}, {`7`}, пробел | 1 |
              | {`я`}, {`ё`} | 2 |
              | {`€`} | 3 |

              Поэтому `len(строки)` считает символы, а длину в байтах даёт `len(строка.encode())`. Лимиты сообщений и полей в базе часто заданы в байтах.

              ## Не та кодировка

              Байты, записанные в одной кодировке, нельзя читать в другой. Текст в `cp1251` (старая кодировка Windows) при `decode("utf-8")` даёт `UnicodeDecodeError`. Параметр `errors="replace"` заменяет испорченные байты значком вместо ошибки.

              ## Двоичный режим файла

              Буква `b` в режиме [[files_open|open]] — `"rb"`, `"wb"` — включает двоичный режим. `read` возвращает `bytes`, а `write` принимает только `bytes`. Параметр `encoding` в этом режиме запрещён: перевода в текст нет.
              """,
              [("""\
                word = "кот"
                data = word.encode("utf-8")
                print(data)
                print(len(word), len(data))
                print(data.decode("utf-8"))""",
                "3 символа стали 6 байтами; decode вернул строку"),
               ("""\
                path = "note.txt"
                with open(path, "w", encoding="utf-8") as f:
                    f.write("да\\n")

                with open(path, "rb") as f:
                    raw = f.read()
                print(raw)
                print(len(raw))""",
                "Режим rb показал файл как есть: 4 байта букв и \\n"),
               ("""\
                data = "привет".encode("cp1251")
                try:
                    data.decode("utf-8")
                except UnicodeDecodeError as e:
                    print("ошибка:", e.reason)
                print(data.decode("cp1251"))""",
                "Чужая кодировка — UnicodeDecodeError, своя — исходный текст"),
               ("""\
                head = bytes([137, 80, 78, 71])
                with open("pic.png", "wb") as f:
                    f.write(head)

                with open("pic.png", "rb") as f:
                    sign = f.read(4)
                print(sign)
                print(sign[0], sign[1:] == b"PNG")""",
                "Байт 137 не символ ASCII, поэтому он показан кодом \\x89")],
              [pitfall("Строку и байты не сложить: TypeError: can only concatenate str (not \"bytes\") to str.",
                       bad='text = "ID: " + data',
                       good='text = "ID: " + data.decode("utf-8")'),
               pitfall("В режиме `\"wb\"` `write` ждёт байты: TypeError: a bytes-like object is required, not 'str'.",
                       bad='f.write("готово")',
                       good='f.write("готово".encode("utf-8"))'),
               pitfall("Двоичный режим не принимает `encoding`: ValueError: binary mode doesn't take an encoding argument.",
                       bad='open(path, "rb", encoding="utf-8")',
                       good='open(path, "rb")'),
               pitfall("Лимит в байтах по `len(строки)` не проверить: кириллица занимает по 2 байта.",
                       bad='''
                           if len(text) <= 70:
                               send(text)''',
                       good='''
                           if len(text.encode("utf-8")) <= 70:
                               send(text)''')]),
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
        predict("py_files_011", "Длина в байтах", """\
                msg = "Привет!"
                data = msg.encode("utf-8")
                print(len(msg), len(data))""",
                ["7 7", "7 14", "13 7"], position=2, topic="files_bytes",
                hint="Сколько байт в UTF-8 занимает русская буква, а сколько — восклицательный знак?",
                explanation="В строке 7 символов. В UTF-8 шесть русских букв занимают по 2 байта, «!» — 1 байт: 6 · 2 + 1 = 13.",
                feedback={"7 7": "В UTF-8 кириллица занимает 2 байта на букву.",
                          "7 14": "«!» — символ ASCII, он занимает 1 байт.",
                          "13 7": "len строки считает символы, а длину в байтах даёт len байтов."}),
        categorize("py_files_012", "str, bytes или int", "Разложите выражения по типу результата",
                   ["str", "bytes", "int"],
                   [('"кот".encode("utf-8")', 1), ('b"abc"', 1), ('b"abc".decode("ascii")', 0),
                    ('bytes([72, 105])', 1), ('b"abc"[0]', 2, "Элемент bytes по индексу — число, код байта: 97."),
                    ('b"abc"[:1]', 1, "Срез bytes — снова bytes: b'a'."),
                    ('str(b"hi")', 0, "str от байтов не декодирует, а даёт строку \"b'hi'\" — тип всё равно str."),
                    ('len("€".encode())', 2)],
                   check=lambda expr: ["str", "bytes", "int"].index(
                       output_of(f"print(type({expr}).__name__)").strip()),
                   code_items=True, topic="files_bytes", difficulty=2,
                   hint="encode даёт bytes, decode — str. Индекс у bytes возвращает число, срез — bytes.",
                   explanation="encode, литерал b\"…\", bytes([...]) и срез дают bytes. decode и str() дают строку. Индекс у bytes — число от 0 до 255, len — тоже число."),
        fix_line("py_files_013", "Запись в двоичный файл", """\
                 with open("status.bin", "wb") as f:
                     f.write("OK")

                 with open("status.bin", "rb") as f:
                     print(f.read())""", 1,
                 ['f.write(b"OK")', 'f.write("OK".encode())', 'f.write("OK".encode("utf-8"))',
                  'f.write("OK".encode("ascii"))'],
                 expect_error="TypeError", topic="files_bytes", role="practice", difficulty=2,
                 hint="Что принимает write в режиме \"wb\" — строку или байты?",
                 explanation="Файл открыт в двоичном режиме, write ждёт bytes: TypeError: a bytes-like object is required, not 'str'. Подойдёт литерал b\"OK\" или \"OK\".encode()."),
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
              "`import` подключает модуль — файл с готовыми функциями, чтобы не писать их заново.",
              """
              Вместе с Python поставляется стандартная библиотека — сотни модулей: математика, случайные числа, даты, работа с файлами. Чтобы пользоваться модулем, его импортируют.

              ## Как записать

              ```syntax
              import модуль
              import модуль as псевдоним
              from модуль import имя
              ```

              - `import math` — имена берут через точку: `math.sqrt(16)`.
              - `import random as rnd` — короткий псевдоним: `rnd.randint(1, 6)`.
              - `from math import sqrt` — имя доступно напрямую: `sqrt(16)`.

              ## Что выбрать

              С точкой сразу видно, откуда взялось имя, поэтому `import модуль` — выбор по умолчанию. `from` удобен для одного-двух частых имён. `from модуль import *` не используют: он заполняет программу неизвестными именами.

              ## Полезные модули

              - `math` — `sqrt`, `pi`, `ceil`, `floor`;
              - `random` — `randint`, `choice`, `shuffle`;
              - `statistics` — `mean`, `median`;
              - `datetime` — даты, см. [[data_datetime|Даты и время]].

              ## Как Python ищет модуль

              Модуль выполняется один раз — при первом импорте. Сначала Python ищет его в папке запускаемой программы, потом в стандартной библиотеке. Поэтому файл `random.py` рядом с программой перекроет настоящий `random`.
              """,
              [("""\
                import math

                print(math.sqrt(81))
                print(math.ceil(4.1))
                print(round(math.pi, 2))""",
                "Имена из math берутся через точку"),
               ("""\
                from statistics import mean, median

                marks = [5, 4, 4, 3, 5]
                print(mean(marks))
                print(median(marks))""",
                "После from имена доступны без префикса"),
               ("""\
                import random as rnd

                rnd.seed(1)
                print(rnd.randint(1, 6))
                print(rnd.choice(["камень", "ножницы"]))""",
                "seed делает «случайные» значения одинаковыми при каждом запуске")],
              [pitfall("После `import math` имена доступны только через точку: `ceil` без `math.` — NameError.",
                       bad='''
                           import math
                           print(ceil(4.1))''',
                       good='''
                           import math
                           print(math.ceil(4.1))'''),
               pitfall("`import *` прячет, откуда взялись имена, и может молча перекрыть ваши переменные.",
                       bad="from math import *", good="import math"),
               "Называть свой файл как стандартный модуль (`random.py`, `json.py`): `import` найдёт ваш файл, а не библиотеку."]),
        topic("std_collections", "collections: словари-помощники",
              "`Counter` считает элементы, а `defaultdict` сам создаёт значение для нового ключа — без проверок `if key in d`.",
              """
              Подсчёт и группировка — две самые частые задачи со словарями. Модуль `collections` даёт для них готовые словари, и код становится короче на несколько строк.

              ## Counter

              `Counter(последовательность)` считает, сколько раз встретился каждый элемент. Это словарь «элемент — количество»:

              - `c["чай"]` — количество; для отсутствующего элемента `0`, а не KeyError;
              - `c.most_common(n)` — `n` самых частых в виде пар;
              - `c.update(ещё)` — досчитать новые элементы.

              При равных количествах `most_common` сохраняет порядок первого появления.

              ## defaultdict

              `defaultdict(list)` при обращении к новому ключу сам создаёт для него пустой список. Поэтому `groups[k].append(x)` работает без проверки ключа. Вместо `list` можно передать `int` (начальное `0`) или `set`.

              Как то же делают обычным словарём — в теме [[dict_counting|Подсчёт с помощью словаря]].

              ## Ещё два словаря

              - `OrderedDict` — словарь с `move_to_end(k)`: перенести ключ в конец;
              - `ChainMap(a, b)` — ищет ключ сначала в `a`, потом в `b`.

              Очередь `deque` и кортеж с именами полей `namedtuple` — в теме [[std_deque|deque и namedtuple]].
              """,
              [("""\
                from collections import Counter

                votes = ["чай", "кофе", "чай", "сок"]
                c = Counter(votes)
                print(c["чай"])
                print(c["вода"])
                print(c.most_common(1))""",
                "Отсутствующий элемент даёт 0, а не KeyError"),
               ("""\
                from collections import defaultdict

                by_len = defaultdict(list)
                for w in ["кот", "слон", "ёж", "пёс"]:
                    by_len[len(w)].append(w)
                print(dict(by_len))""",
                "Список для нового ключа создан автоматически"),
               ("""\
                from collections import OrderedDict

                recent = OrderedDict(a=1, b=2, c=3)
                recent.move_to_end("a")
                print(list(recent))
                recent.popitem(last=False)
                print(list(recent))""",
                "move_to_end перенёс ключ, popitem(last=False) убрал первый"),
               ("""\
                from collections import ChainMap

                defaults = {"theme": "light", "sound": True}
                user = {"theme": "dark"}
                cfg = ChainMap(user, defaults)
                print(cfg["theme"])
                print(cfg["sound"])""",
                "Ключ ищется сначала в user, потом в defaults")],
              [pitfall("В `defaultdict` передают саму функцию, без скобок: TypeError: first argument must be callable or None.",
                       bad="groups = defaultdict(list())", good="groups = defaultdict(list)"),
               pitfall("Чтение `groups[\"x\"]` в `defaultdict` добавляет ключ `x`. Наличие проверяйте через `in`.",
                       bad='''
                           if groups["x"]:
                               print("есть")''',
                       good='''
                           if "x" in groups:
                               print("есть")'''),
               pitfall("`most_common` возвращает список пар, а не словарь: TypeError при обращении по ключу.",
                       bad='top = c.most_common(1)["чай"]', good="word, n = c.most_common(1)[0]")]),
        topic("std_deque", "deque и namedtuple",
              "`deque` — очередь, быстрая с обоих концов, а `namedtuple` — кортеж, к полям которого обращаются по имени.",
              """
              Список хорош почти для всего, но не для очереди: `pop(0)` сдвигает все остальные элементы. А кортеж из пяти полей трудно читать: что лежит в `p[3]`? Для этих случаев в `collections` есть {`deque`} и {`namedtuple`}.

              ## deque

              {`deque`} — двусторонняя очередь. Добавить и забрать элемент можно с любого конца, и это быстро при любой длине:

              - `append(x)` и `pop()` — справа;
              - `appendleft(x)` и `popleft()` — слева.

              {`deque(maxlen=n)`} хранит не больше `n` элементов. Новый элемент выталкивает старый с противоположного конца — так хранят «последние n событий».

              ## namedtuple

              ```syntax
              Имя = namedtuple("Имя", "поле1 поле2")
              ```

              Получается новый тип: `Item("чай", 120)` создаёт значение, `item.price` читает поле. Это по-прежнему [[tuple_basics|кортеж]]: его можно распаковать и нельзя изменить.

              Для изменяемых записей с полями есть [[dc_basics|@dataclass]].

              ## Что выбрать

              - Очередь «пришёл первым — обслужен первым» — {`deque`} с `append` и `popleft`.
              - Неизменяемая запись из нескольких полей — {`namedtuple`}.
              """,
              [("""\
                from collections import deque

                queue = deque(["Ада", "Боб"])
                queue.append("Ева")
                print(queue.popleft())
                print(list(queue))""",
                "Первым обслужен тот, кто пришёл первым"),
               ("""\
                from collections import deque

                last = deque(maxlen=3)
                for move in ["e4", "e5", "Кf3", "Кc6"]:
                    last.append(move)
                print(list(last))""",
                "Четвёртый ход вытолкнул самый старый"),
               ("""\
                from collections import namedtuple

                Item = namedtuple("Item", "name price")
                tea = Item("чай", 120)
                print(tea)
                print(tea.price * 2)
                name, price = tea
                print(name)""",
                "Поля читаются по имени, а распаковка работает как у кортежа")],
              [pitfall("`list.pop(0)` сдвигает все элементы и на длинной очереди медленный, `deque.popleft()` — нет.",
                       bad="first = items.pop(0)", good="first = queue.popleft()"),
               pitfall("Поле `namedtuple` нельзя изменить: AttributeError: can't set attribute. `_replace` создаёт копию.",
                       bad="tea.price = 100", good="tea = tea._replace(price=100)")]),
        topic("std_itertools", "itertools",
              "Модуль `itertools` строит комбинации, цепочки и накопления из последовательностей без вложенных циклов.",
              """
              Перебрать все пары игроков, все коды из трёх цифр, склеить несколько списков — обычно для этого пишут вложенные циклы. В `itertools` для таких задач есть готовые функции.

              ## Комбинаторика

              | Функция | Порядок | Повторы |
              |---|---|---|
              | {`product`} | важен | можно |
              | {`permutations`} | важен | нельзя |
              | {`combinations`} | не важен | нельзя |

              `product(a, b)` перебирает пары из двух последовательностей, как два вложенных цикла. `product(s, repeat=3)` — тройки из одной. Второй аргумент `permutations` и `combinations` — сколько элементов брать.

              ## Цепочки и накопления

              - `chain(a, b)` — сначала элементы `a`, потом `b`;
              - `accumulate(xs)` — накопленные суммы: `[1, 3, 6]` для `[1, 2, 3]`;
              - `groupby(xs, key)` — группы подряд идущих элементов с одним ключом.

              `groupby` объединяет только соседей, поэтому данные сначала сортируют по тому же ключу.

              ## Ленивость

              Все функции `itertools` возвращают [[gen_iter|итераторы]]: значения создаются по одному, когда их просят. Чтобы увидеть результат целиком, нужен `list()`. Взять первые `n` значений помогает `islice` — о нём в теме [[gen_lazy|Ленивые вычисления и конвейеры]].
              """,
              [("""\
                from itertools import combinations

                team = ["Ада", "Боб", "Ева"]
                for a, b in combinations(team, 2):
                    print(a, b)""",
                "Каждая пара игроков один раз, порядок не важен"),
               ("""\
                from itertools import product, permutations

                codes = list(product("01", repeat=3))
                print(len(codes))
                print(codes[:3])
                print(list(permutations("ab")))""",
                "Двоичные коды из трёх цифр и перестановки двух букв"),
               ("""\
                from itertools import accumulate, chain

                week1 = [100, 50]
                week2 = [70]
                days = list(chain(week1, week2))
                print(days)
                print(list(accumulate(days)))""",
                "chain склеил недели, accumulate дал накопленный итог"),
               ("""\
                from itertools import groupby

                marks = sorted([5, 3, 5, 4, 5, 3])
                for mark, group in groupby(marks):
                    print(mark, len(list(group)))""",
                "После сортировки одинаковые оценки стоят рядом")],
              [pitfall("`groupby` объединяет только соседей: без сортировки одна группа распадётся на несколько.",
                       bad="groupby(words, key=len)",
                       good="groupby(sorted(words, key=len), key=len)"),
               pitfall("Функции `itertools` возвращают итераторы: `print` покажет объект, а не значения.",
                       bad="print(combinations(team, 2))", good="print(list(combinations(team, 2)))"),
               pitfall("Группа из `groupby` пустеет на следующем шаге: сохраняйте её через `list(group)` сразу.",
                       bad='''
                           groups = [g for _, g in groupby(marks)]
                           print(list(groups[0]))''',
                       good='''
                           groups = [list(g) for _, g in groupby(marks)]
                           print(groups[0])''')]),
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
              topic="std_deque", hint="При переполнении deque выталкивает элемент с противоположного конца.",
              explanation="append(4) выталкивает 1 слева: [2, 3, 4]. appendleft(0) выталкивает 4 справа: [0, 2, 3]."),
        predict("py_std_006", "Именованный кортеж", """\
                from collections import namedtuple
                Point = namedtuple("Point", "x y")
                p = Point(3, 4)
                print(p.x + p.y, p)""",
                ["7 (3, 4)", "34 Point(x=3, y=4)", "AttributeError"], position=1, topic="std_deque",
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
              "JSON — текстовый формат обмена данными; модуль `json` переводит словари и списки в такой текст и обратно.",
              """
              JSON — самый частый формат, в котором программы передают данные: ответы веб-сервисов, файлы настроек, сохранения в играх. Это обычный текст, который понимает почти любой язык программирования.

              ## Четыре функции

              Две работают со строками, две — с файлами. Буква `s` в конце значит string — строка.

              - `json.dumps(данные)` — данные Python в строку JSON
              - `json.loads(строка)` — строка JSON в данные Python
              - `json.dump(данные, файл)` — записать в открытый файл
              - `json.load(файл)` — прочитать из открытого файла

              Файл открывают через [[files_open|open и with]] с `encoding="utf-8"`.

              ## Как типы переводятся

              | Python | JSON |
              |---|---|
              | {`dict`} | объект {`{}`} |
              | {`list`}, {`tuple`} | массив {`[]`} |
              | {`str`} | строка {`"…"`} |
              | {`int`}, {`float`} | число |
              | {`True`}, {`False`} | {`true`}, {`false`} |
              | {`None`} | {`null`} |

              Обратно переводится не всё один к одному:

              - кортеж возвращается списком;
              - ключи словаря возвращаются строками: `{1: "a"}` станет `{"1": "a"}`.

              Множество, дату или свой объект `dumps` не переводит: будет `TypeError`. Их заранее превращают в список, строку или словарь.

              ## Строгий синтаксис

              JSON строже Python. Строки и ключи — только в двойных кавычках, `true` и `null` — со строчной буквы, запятая после последнего элемента запрещена. Текст `{'a': 1}` уже не JSON: `loads` выбросит `json.JSONDecodeError`.

              Неправильный JSON обычно приходит извне — от пользователя или из сети. Поэтому разбор оборачивают в [[exc_try|try / except]].

              ## Читаемый вывод

              По умолчанию `dumps` пишет всё в одну строку и заменяет русские буквы кодами вида `\\u0447`. Два параметра это меняют:

              - `ensure_ascii=False` — оставить русский текст как есть;
              - `indent=2` — разбить по строкам с отступом в 2 пробела.
              """,
              [("""\
                import json

                user = {
                    "name": "Ада",
                    "admin": False,
                    "boss": None,
                }
                text = json.dumps(user, ensure_ascii=False)
                print(text)
                print(type(text).__name__)

                back = json.loads(text)
                print(back["name"])""",
                "В строке JSON — false и null; loads вернул обычный словарь"),
               ("""\
                import json

                order = {"id": 7, "items": ["чай"]}
                print(json.dumps(order))

                pretty = json.dumps(
                    order, ensure_ascii=False, indent=2
                )
                print(pretty)""",
                "Без параметров — коды букв в одну строку, с ними — читаемо"),
               ("""\
                import json

                data = {1: "один", "pair": (2, 3)}
                back = json.loads(json.dumps(data))
                print(back)
                print(back["1"], back["pair"])""",
                "Ключ 1 вернулся строкой \"1\", кортеж — списком"),
               ("""\
                import json

                path = "save.json"
                with open(path, "w", encoding="utf-8") as f:
                    json.dump({"level": 3, "hp": 80}, f)

                with open(path, encoding="utf-8") as f:
                    save = json.load(f)
                print(save["level"], save["hp"])""",
                "Сохранение в файл и чтение обратно"),
               ("""\
                import json

                raw = "{'level': 3}"
                try:
                    json.loads(raw)
                except json.JSONDecodeError as e:
                    print("Не JSON:", e.msg)""",
                "Одинарные кавычки — ошибка разбора, её перехватывают")],
              [pitfall("В JSON строки и ключи — только в двойных кавычках, иначе json.JSONDecodeError.",
                       bad="""json.loads("{'a': 1}")""",
                       good="""json.loads('{"a": 1}')"""),
               pitfall("loads ждёт строку, а f — файл: TypeError. С файлами работают dump и load.",
                       bad="data = json.loads(f)",
                       good="data = json.load(f)"),
               pitfall("После JSON ключи-числа становятся строками: back[1] даст KeyError.",
                       bad="back[1]",
                       good='back["1"]'),
               pitfall("Множество не переводится в JSON: TypeError: Object of type set is not JSON serializable.",
                       bad='json.dumps({"tags": {"a", "b"}})',
                       good='json.dumps({"tags": sorted(tags)})')],
        ),
        topic("data_re", "Регулярные выражения",
              "Регулярное выражение — шаблон текста; модуль `re` ищет по нему совпадения, проверяет строки и делает замены.",
              """
              Найти в тексте все телефоны, проверить, что код состоит из шести цифр, заменить даты — методы строк здесь не справляются. Регулярное выражение описывает не конкретный текст, а его форму: «три цифры, дефис, две цифры».

              ## Как записать

              ```syntax
              import re

              re.search(r"шаблон", текст)
              ```

              Шаблон пишут в сырой строке `r"…"`: тогда обратная косая черта в `\\d` остаётся как есть. Без `r` Python 3.12 выдаёт SyntaxWarning.

              ## Основные символы

              | Шаблон | Что значит |
              |---|---|
              | {`\\d`} | цифра |
              | {`\\w`} | буква, цифра или {`_`} |
              | {`\\s`} | пробел, табуляция, {`\\n`} |
              | {`.`} | любой символ, кроме {`\\n`} |
              | {`[а-я]`} | один символ из набора |
              | {`^`}, {`$`} | начало и конец строки |

              `\\w` включает и русские буквы. Повторы ставят после символа: {`+`} — один раз и больше, `*` — ноль и больше, `?` — ноль или один, `{3}` — ровно три.

              ## Функции re

              - `re.search` — первое совпадение где угодно или `None`;
              - `re.match` — совпадение только в начале строки;
              - `re.fullmatch` — вся строка целиком;
              - `re.findall` — список всех совпадений;
              - `re.sub` — замена всех совпадений.

              ## Группы и жадность

              Скобки выделяют часть совпадения: `m.group(1)` — текст первой группы. `(?P<имя>…)` — именованная группа, её читают как `m["имя"]`.

              {`+`} и `*` жадные: захватывают как можно больше. `+?` и `*?` — ленивые, захватывают как можно меньше.
              """,
              [("""\
                import re

                msg = "Звоните: 8-900-123, офис 45"
                print(re.findall(r"\\d+", msg))
                print(re.sub(r"\\d", "*", msg))""",
                "findall нашёл все числа, sub заменил каждую цифру"),
               ("""\
                import re

                code = "AB-123"
                pat = r"[A-Z]{2}-\\d{3}"
                print(re.match(r"\\d+", code))
                print(re.search(r"\\d+", code).group())
                print(bool(re.fullmatch(pat, code)))""",
                "match смотрит только в начало, search — везде, fullmatch — всю строку"),
               ("""\
                import re

                line = "2024-05-17 оплата 350"
                pat = r"(?P<date>[\\d-]+) \\w+ (?P<sum>\\d+)"
                m = re.search(pat, line)
                print(m["date"])
                print(int(m["sum"]) + 50)""",
                "Именованные группы читаются по имени"),
               ("""\
                import re

                s = 'цвет "red", фон "blue"'
                print(re.findall(r'".+"', s))
                print(re.findall(r'".+?"', s))""",
                "Жадный + дошёл до последней кавычки, ленивый +? — до ближайшей")],
              [pitfall("`re.match` ищет только в начале строки: для `\"код 42\"` вернёт `None`.",
                       bad='re.match(r"\\d+", "код 42")', good='re.search(r"\\d+", "код 42")'),
               pitfall("Если совпадения нет, `search` вернёт `None`, и `.group()` упадёт с AttributeError.",
                       bad='''
                           m = re.search(pat, s)
                           print(m.group())''',
                       good='''
                           m = re.search(pat, s)
                           if m:
                               print(m.group())'''),
               pitfall("Без `r` строка `\"\\b\"` — символ backspace, а не граница слова: шаблон ничего не найдёт.",
                       bad='re.findall("\\bкот\\b", s)', good='re.findall(r"\\bкот\\b", s)')]),
        topic("data_datetime", "Даты и время",
              "Модуль `datetime` хранит даты и время, считает промежутки между ними и переводит даты в текст и обратно.",
              """
              Сколько дней до дедлайна, какое число будет через две недели, во сколько закончится матч — считать даты вручную трудно из-за разной длины месяцев и високосных лет. Модуль `datetime` делает это сам.

              ## Основные типы

              - `date(2024, 3, 1)` — дата: год, месяц, день;
              - `datetime(2024, 3, 1, 18, 30)` — дата и время;
              - `timedelta(days=2, hours=3)` — промежуток;
              - `date.today()` и `datetime.now()` — текущие дата и время.

              ## Арифметика дат

              Дата плюс `timedelta` — новая дата с учётом длины месяцев: `date(2024, 2, 28) + timedelta(days=2)` даёт 1 марта. Разность двух дат — `timedelta`, а её `.days` — число дней.

              Даты сравнивают обычными `<` и `>`: более ранняя дата меньше.

              ## Дата и текст

              - `d.strftime("%d.%m.%Y")` — дата в строку по формату;
              - `datetime.strptime(s, "%d.%m.%Y")` — строка в дату;
              - `print(d)` выводит дату в формате `2024-03-01`.

              Коды формата: `%d` — день, `%m` — месяц, `%Y` — год, `%H:%M` — часы и минуты.

              ## Часовые пояса

              `datetime.now()` без аргументов возвращает «наивное» время — без пояса. Пояс задают параметром `tzinfo`, а `astimezone(пояс)` переводит время в другой пояс. Вычитать и сравнивать через `<` наивное время и время с поясом нельзя: TypeError.
              """,
              [("""\
                from datetime import date, timedelta

                start = date(2024, 12, 25)
                end = start + timedelta(days=10)
                print(end)
                print((end - start).days)""",
                "timedelta перешёл через границу года"),
               ("""\
                from datetime import datetime

                s = "07.03.2025 18:30"
                dt = datetime.strptime(s, "%d.%m.%Y %H:%M")
                print(dt)
                print(dt.strftime("%H:%M, %d/%m"))""",
                "strptime разобрал строку, strftime собрал свой формат"),
               ("""\
                from datetime import datetime

                now = datetime.now()
                print(now > datetime(2000, 1, 1))
                print(now.tzinfo)""",
                "now() — текущее время без пояса: tzinfo равен None"),
               ("""\
                from datetime import datetime, timezone
                from datetime import timedelta

                msk = timezone(timedelta(hours=3))
                start = datetime(2025, 1, 1, 9, 0,
                                 tzinfo=timezone.utc)
                print(start)
                print(start.astimezone(msk))""",
                "Один и тот же момент по UTC и по Москве")],
              [pitfall("Даты в виде «дд.мм.гггг» сравниваются как текст: 2 января окажется позже 1 декабря.",
                       bad='"02.01.2024" > "01.12.2024"',
                       good="date(2024, 1, 2) > date(2024, 12, 1)"),
               pitfall("Несуществующая дата сразу даёт ValueError: day is out of range for month.",
                       bad="date(2023, 2, 29)", good="date(2024, 2, 29)"),
               pitfall("`timedelta` не знает месяцев и лет — их длина разная: `months=` даёт TypeError.",
                       bad="timedelta(months=1)", good="timedelta(days=30)")]),
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
