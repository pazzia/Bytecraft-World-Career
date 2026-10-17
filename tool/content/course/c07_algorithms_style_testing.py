"""Модули 31–33: алгоритмы и сложность, идиомы Python, тестирование и
отладка."""
import math

from bclib import choice, fill, match, multi, order, predict, bug, typed, topic, task, run


def runs(code):
    return run(code).ok


def output_of(code):
    return run(code).out


MODULES = []

# --------------------------------------------------------------- algorithms
O1_OPERATIONS = {
    "x in множество": True,
    "список.append(x)": True,
    "список.insert(0, x)": False,
    "словарь[ключ]": True,
    "x in список": False,
    "deque.popleft()": True,
}

MODULES.append(dict(
    id="algorithms", title="Алгоритмы и сложность", description="O-большое, поиск, сортировка, графы",
    icon="🧮",
    topics=[
        topic("algo_complexity", "Сложность алгоритма",
              "O-большое показывает, как растёт время работы с ростом данных: O(1) — не зависит от n, O(log n) — бинарный поиск, O(n) — один проход, O(n log n) — сортировка, O(n²) — вложенные циклы.",
              """
              Важен не точный счёт операций, а порядок роста. Для n = 1 000 000 разница между O(n) и O(n²) — это миллион операций против триллиона.

              Цена операций Python: x in list — O(n) (просмотр всех элементов), x in set и d[key] — O(1) в среднем (хеш-таблица), list.append — O(1), list.insert(0, x) и list.pop(0) — O(n) (сдвиг всех элементов), deque.appendleft/popleft — O(1), sorted — O(n log n).

              Частый приём ускорения — заменить поиск в списке на множество или словарь: вложенный цикл O(n²) превращается в один проход O(n).
              """,
              [("""\
                ops = 0
                for a in range(100):
                    for b in range(100):
                        ops += 1
                print("вложенные циклы:", ops)

                seen = set(range(100))
                ops = 0
                for a in range(100):
                    ops += 1
                    found = (99 - a) in seen
                print("один проход с множеством:", ops)""", "Одна и та же задача: 10 000 шагов против 100.")],
              ["Проверять x in список внутри цикла по большому списку — это скрытый вложенный цикл O(n²).",
               "Оптимизировать «на глаз»: сначала измерьте, где программа тратит время."]),
        topic("algo_search_sort", "Поиск и сортировка",
              "Бинарный поиск находит элемент в отсортированном списке за O(log n). Модуль bisect делает это готово; sorted и sort — устойчивая сортировка O(n log n).",
              """
              Бинарный поиск каждый раз сравнивает с серединой и отбрасывает половину: для миллиона элементов хватает около 20 сравнений. Работает только на отсортированных данных.

              bisect.bisect_left(a, x) — позиция, куда вставить x слева от равных, bisect_right — справа от равных, insort — вставка с сохранением порядка.

              Сортировка в Python устойчивая: элементы с равным ключом сохраняют исходный порядок. Поэтому сложную сортировку можно делать в несколько проходов или ключом-кортежем.
              """,
              [("""\
                import bisect

                scores = [10, 20, 30, 40]
                print(bisect.bisect_left(scores, 25), bisect.bisect_left(scores, 30), bisect.bisect_right(scores, 30))
                bisect.insort(scores, 25)
                print(scores)""", None)],
              ["Запускать бинарный поиск по неотсортированному списку — результат будет случайным.",
               "Ошибка на единицу в границах: lo = mid вместо mid + 1 зацикливает поиск."]),
        topic("algo_patterns", "Приёмы: куча, очередь, окно, два указателя",
              "heapq — быстрый доступ к минимуму, deque — очередь для обхода в ширину (BFS), скользящее окно и два указателя — проход за O(n) вместо перебора пар.",
              """
              heapq хранит список как кучу: heappush/heappop за O(log n), минимум всегда в heap[0]. nlargest(k, data) — k наибольших.

              Обход в ширину (BFS) на очереди deque находит кратчайшее число шагов в графе: соседи вершины обрабатываются раньше соседей соседей.

              Скользящее окно: сумму окна не пересчитывают заново, а прибавляют новый элемент и вычитают ушедший. Два указателя идут навстречу по отсортированному списку.
              """,
              [("""\
                import heapq

                tasks = [(3, "тесты"), (1, "баг в проде"), (2, "ревью")]
                heapq.heapify(tasks)
                while tasks:
                    priority, name = heapq.heappop(tasks)
                    print(priority, name)""", "Самый важный (наименьший приоритет) выходит первым."),
               ("""\
                nums = [2, 1, 5, 1, 3, 2]
                k = 3
                window = sum(nums[:k])
                best = window
                for i in range(k, len(nums)):
                    window += nums[i] - nums[i - k]
                    best = max(best, window)
                print(best)""", "Скользящее окно: каждая сумма за O(1).")],
              ["Использовать list.pop(0) как очередь в BFS: каждый pop(0) — O(n)."]),
    ],
    tasks=[
        task("t_algo_binary_search", "Бинарный поиск",
             "В первой строке — отсортированные по возрастанию различные целые числа, во второй — числа для поиска. Для каждого искомого числа выведите его индекс или -1. Напишите функцию binary_search(items, target) сами — без bisect, index и оператора in.",
             solution="""\
                def binary_search(items, target):
                    lo, hi = 0, len(items) - 1
                    while lo <= hi:
                        mid = (lo + hi) // 2
                        if items[mid] == target:
                            return mid
                        if items[mid] < target:
                            lo = mid + 1
                        else:
                            hi = mid - 1
                    return -1

                items = list(map(int, input().split()))
                print(" ".join(str(binary_search(items, int(x))) for x in input().split()))""",
             starter="""\
                def binary_search(items, target):
                    return -1

                items = list(map(int, input().split()))
                print(" ".join(str(binary_search(items, int(x))) for x in input().split()))""",
             tests=["1 3 5 7 9\n7 1 4\n", "2\n2 3\n", "-5 0 8 13 21 34\n34 -5 9 0\n", "10 20\n15\n"],
             hint="Держите границы lo и hi и сужайте их вокруг середины.", difficulty=3,
             requires=dict(defines=["binary_search"], uses=["while"], no_calls=["index"], no_imports=["bisect"])),
        task("t_algo_unique_fast", "Без повторов, но быстро",
             "В строке — целые числа через пробел (их может быть очень много). Выведите числа без повторов в порядке первого появления. Решение должно работать за один проход: на большом тесте вложенный перебор не успеет за 5 секунд.",
             solution="""\
                seen = set()
                result = []
                for x in input().split():
                    if x not in seen:
                        seen.add(x)
                        result.append(x)
                print(" ".join(result))""",
             starter="""\
                result = []
                for x in input().split():
                    if x not in result:
                        result.append(x)
                print(" ".join(result))""",
             tests=["3 1 3 2 1\n", "5\n", "1 1 1 1\n", " ".join(str(i % 30011) for i in range(60000)) + "\n"],
             hint="Множество проверяет «было ли уже» за O(1), список — за O(n).", difficulty=3),
    ],
    levels=[
        choice("py_algo_001", "Сколько шагов", "Сколько сравнений в худшем случае сделает бинарный поиск в отсортированном списке из 1 000 000 элементов?",
               ["около 20", "около 1 000", "около 500 000", "1 000 000"], 0,
               check=lambda option: (option == "около 20") == (math.ceil(math.log2(10 ** 6 + 1)) == 20),
               topic="algo_search_sort", hint="Каждое сравнение отбрасывает половину оставшихся элементов.",
               explanation="Половин хватит log₂(1 000 000) ≈ 20: 2²⁰ = 1 048 576. Поэтому бинарный поиск — O(log n).",
               feedback={"около 1 000": "Это √n. Бинарный поиск делит пополам: нужно около log₂ n сравнений.",
                         "около 500 000": "Столько в среднем делает линейный поиск, а бинарный отбрасывает половину за шаг.",
                         "1 000 000": "Это худший случай линейного поиска."}),
        match("py_algo_002", "Цена операций",
              ["x in список", "x in множество", "sorted(данные)", "два вложенных цикла по n", "бинарный поиск"],
              rights=["O(n)", "O(1) в среднем", "O(n log n)", "O(n²)", "O(log n)"],
              prompt="Сопоставьте операцию и её сложность", topic="algo_complexity",
              hint="Множество — хеш-таблица, бинарный поиск каждый раз делит пополам.",
              explanation="Список просматривается целиком, множество находит элемент по хешу, сортировка — n log n, вложенные циклы — n · n, бинарный поиск — log n."),
        predict("py_algo_003", "bisect", """\
                import bisect

                ages = [18, 25, 25, 40]
                print(bisect.bisect_left(ages, 25), bisect.bisect_right(ages, 25), bisect.bisect_left(ages, 30))
                bisect.insort(ages, 30)
                print(ages)""",
                ["1 2 3\n[18, 25, 25, 40, 30]", "2 3 3\n[18, 25, 25, 30, 40]", "1 3 3\n[30, 18, 25, 25, 40]"],
                position=3, topic="algo_search_sort",
                hint="bisect_left — левее равных, bisect_right — правее. insort сохраняет порядок.",
                explanation="25 стоит на позициях 1 и 2: bisect_left даёт 1, bisect_right — 3. 30 встанет между 25 и 40 — позиция 3. insort вставляет 30 туда же.",
                feedback={"1 2 3\n[18, 25, 25, 40, 30]": "bisect_right — позиция после всех равных: 3. И insort не добавляет в конец.",
                          "2 3 3\n[18, 25, 25, 30, 40]": "bisect_left — позиция перед первым равным: 1.",
                          "1 3 3\n[30, 18, 25, 25, 40]": "insort вставляет на место по порядку, а не в начало."}),
        fill("py_algo_004", "Бинарный поиск", "Допишите сужение границ поиска",
             """\
             def search(items, target):
                 lo, hi = 0, len(items) - 1
                 while lo <= hi:
                     mid = (lo + hi) // 2
                     if items[mid] == target:
                         return mid
                     if items[mid] < target:
                         lo = {{0}}
                     else:
                         hi = {{1}}
                 return -1

             nums = [1, 3, 5, 7, 9, 11]
             print(search(nums, 9), search(nums, 4))""", ["mid + 1", "mid - 1", "mid", "hi + 1"],
             ["mid + 1", "mid - 1"], topic="algo_search_sort",
             hint="Середина уже проверена — её можно исключить из диапазона.",
             explanation="Если середина меньше искомого, ответ правее: lo = mid + 1. Если больше — левее: hi = mid - 1. Без ±1 диапазон может перестать сужаться, и цикл зациклится.",
             role="practice", difficulty=3, expect="4 -1\n"),
        typed("py_algo_005", "Куча", """\
              import heapq

              nums = [7, 2, 9, 4, 1]
              print(heapq.nlargest(2, nums))
              heap = []
              for n in nums:
                  heapq.heappush(heap, n)
              print(heapq.heappop(heap), heapq.heappop(heap))""",
              topic="algo_patterns", hint="heappop всегда достаёт наименьший элемент.",
              explanation="nlargest(2) — два наибольших: [9, 7]. Куча выдаёт элементы от меньшего к большему: сначала 1, потом 2.",
              role="practice", difficulty=2),
        predict("py_algo_006", "Пара с суммой", """\
                def has_pair(nums, target):
                    seen = set()
                    for x in nums:
                        if target - x in seen:
                            return (target - x, x)
                        seen.add(x)
                    return None

                print(has_pair([3, 8, 1, 5], 9), has_pair([1, 2], 7))""",
                ["(3, 5) None", "(1, 8) None", "True False"], position=0, topic="algo_complexity",
                hint="Пара находится в момент, когда встречается второе число пары. Какое первое?",
                explanation="Проход за O(n): для 3 и 8 пары ещё нет, на 1 оказывается, что 9 - 1 = 8 уже встречалось. Возвращается (8, 1). Для [1, 2] пары с суммой 7 нет.",
                role="practice", difficulty=3,
                feedback={"(3, 5) None": "3 + 5 = 8, а нужна сумма 9.",
                          "(1, 8) None": "Первым в кортеже стоит target - x — число, найденное раньше: 8.",
                          "True False": "Функция возвращает саму пару, а не True."}),
        bug("py_algo_007", "Потерянное окно", """\
            nums = [2, 1, 5, 1, 3]
            k = 3
            best = 0
            for i in range(len(nums) - k):
                best = max(best, sum(nums[i:i + k]))
            print(best)""", {3: "for i in range(len(nums) - k + 1):"},
            prompt="Нужна наибольшая сумма трёх подряд идущих чисел (9). Найдите строку с ошибкой", topic="algo_patterns",
            hint="Сколько окон длины k в списке из n элементов?",
            explanation="Окон длины k ровно n - k + 1. range(n - k) пропускает последнее окно [5, 1, 3] с суммой 9 — классическая ошибка на единицу.",
            difficulty=3),
        multi("py_algo_008", "O(1) в среднем", "Какие операции выполняются за O(1) (в среднем), независимо от размера коллекции?",
              list(O1_OPERATIONS), [i for i, ok in enumerate(O1_OPERATIONS.values()) if ok],
              check=lambda op: O1_OPERATIONS[op], topic="algo_complexity",
              hint="Хеш-таблицы и добавление в конец — быстро. Сдвиг всех элементов и просмотр всех — медленно.",
              explanation="Множество и словарь ищут по хешу, append пишет в конец, deque снимает элемент с начала без сдвигов. insert(0, x) сдвигает все элементы списка, x in список просматривает их по очереди — O(n).",
              feedback={"список.insert(0, x)": "Вставка в начало сдвигает все элементы — O(n). Для очереди — deque.",
                        "x in список": "Список просматривается по очереди — O(n)."}),
        predict("py_algo_009", "Босс: обход в ширину", """\
                from collections import deque

                graph = {"A": ["B", "C"], "B": ["D"], "C": ["D", "E"], "D": ["F"], "E": ["F"], "F": []}

                def bfs(start):
                    dist = {start: 0}
                    queue = deque([start])
                    while queue:
                        node = queue.popleft()
                        for nxt in graph[node]:
                            if nxt not in dist:
                                dist[nxt] = dist[node] + 1
                                queue.append(nxt)
                    return dist

                print(bfs("A"))""",
                ["{'A': 0, 'B': 1, 'C': 1, 'D': 2, 'E': 3, 'F': 4}", "{'A': 0, 'B': 1, 'D': 2, 'F': 3, 'C': 1, 'E': 2}",
                 "{'A': 0, 'B': 1, 'C': 1, 'D': 2, 'E': 2, 'F': 4}"], position=0, topic="algo_patterns",
                hint="BFS обрабатывает вершины слоями: сначала все на расстоянии 1, потом 2…",
                explanation="Из A за шаг достижимы B и C, за два — D и E, за три — F. Очередь гарантирует, что первая найденная дорога — кратчайшая; словарь хранит вершины в порядке открытия.",
                role="boss", difficulty=4,
                feedback={"{'A': 0, 'B': 1, 'C': 1, 'D': 2, 'E': 3, 'F': 4}": "E достижима из C за один шаг: расстояние 2.",
                          "{'A': 0, 'B': 1, 'D': 2, 'F': 3, 'C': 1, 'E': 2}": "Так обходил бы поиск в глубину. Очередь сначала обрабатывает весь слой: B и C раньше D.",
                          "{'A': 0, 'B': 1, 'C': 1, 'D': 2, 'E': 2, 'F': 4}": "F открывается из D на расстоянии 2 — значит, 3."}),
    ],
))

# --------------------------------------------------------------- pythonic
GET_OPTIONS = ["d.get('age', 0)", "d['age'] if 'age' in d else 0", "d['age'] or 0", "d.setdefault('age', 0)",
               "d.age", "d.get(age, 0)"]


def safe_get(expr):
    for data, want in [({}, 0), ({"age": 5}, 5), ({"age": 0}, 0)]:
        result = run(f"d = {data!r}\nprint(repr({expr}))")
        if not result.ok or result.out.strip() != repr(want):
            return False
    return True


MODULES.append(dict(
    id="pythonic", title="Идиомы Python", description="match/case, :=, распаковка, EAFP", icon="🐍",
    topics=[
        topic("idiom_match", "match / case",
              "Структурное сопоставление: match значение: case шаблон: — проверяет форму данных (литералы, последовательности, словари, классы) и сразу достаёт из них части.",
              """
              case 0: — литерал. case [x, y]: — список из двух элементов (x и y получают значения). case ["take", *items]: — первый элемент «take», остальные в items. case {"type": "click", "x": x}: — словарь с такими ключами (лишние ключи допускаются). case Point(x=0, y=y): — объект класса с полями. case _: — всё остальное.

              После шаблона можно добавить условие: case int() if x < 0:. Срабатывает первый подходящий case.

              Голое имя в case — это захват, а не сравнение: case RED: поймает что угодно и запишет в RED (Python не даст поставить такой case не последним — SyntaxError). Для сравнения с константой нужно имя с точкой: case Color.RED:.
              """,
              [("""\
                def parse(cmd):
                    match cmd.split():
                        case ["go", direction]:
                            return f"идём {direction}"
                        case ["take", *items]:
                            return f"берём {len(items)}"
                        case []:
                            return "пусто"
                        case _:
                            return "непонятно"

                print(parse("go north"), "|", parse("take a b"), "|", parse(""), "|", parse("go"))""", None)],
              ["Писать case RED: для сравнения с переменной: это захват любого значения.",
               "Ждать, что match работает как switch в других языках «с проваливанием»: срабатывает ровно один case."]),
        topic("idiom_walrus", "Моржовый оператор и распаковка",
              ":= присваивает значение внутри выражения. Звёздочка при распаковке собирает «всё остальное»: first, *rest = items.",
              """
              if (n := len(data)) > 10: — вычисляет длину один раз, сохраняет в n и сразу сравнивает. Удобно в while: while (line := f.readline()):.

              first, *middle, last = [1, 2, 3, 4, 5] — звёздочка собирает середину в список. a, b = b, a — обмен без временной переменной.

              f"{x + y = }" — f-строка с = печатает и выражение, и его значение: удобно для отладки.
              """,
              [("""\
                data = [3, 8, 1, 9]
                if (n := len(data)) > 3:
                    print(f"длинный список: {n}")
                first, *rest = data
                print(first, rest)
                x, y = 3, 4
                print(f"{x + y = }")""", None)],
              ["Писать if n = len(data): — в условии = недопустим, нужен :=."]),
        topic("idiom_eafp", "EAFP и питоничный код",
              "EAFP — «проще попросить прощения»: пробуем действие и обрабатываем исключение. Питоничный код использует встроенные инструменты вместо ручных циклов.",
              """
              Вместо цепочки проверок if key in d: ... — d.get(key, default) или try/except KeyError. Вместо for i in range(len(items)) — enumerate. Вместо флага found — any() или for/else. Вместо ручного подсчёта — Counter, sum, max(key=...).

              d.setdefault(k, v) возвращает d[k], а если ключа нет — записывает v и возвращает его (меняет словарь). any(...) и all(...) с генераторным выражением останавливаются на первом ответе.

              «Явное лучше неявного», «простое лучше сложного» — из import this, дзена Python.
              """,
              [("""\
                prices = {"чай": 3}
                print(prices.get("кофе", 0), prices.setdefault("сок", 5), prices)
                nums = [3, 7, 10]
                print(any(n > 9 for n in nums), all(n > 2 for n in nums))
                for i, n in enumerate(nums, 1):
                    print(i, n)""", None)],
              ["for i in range(len(items)): items[i] — там, где нужен enumerate."]),
    ],
    tasks=[
        task("t_idiom_commands", "Мини-стек команд",
             "Обработайте команды, по одной на строке, до строки «end»: «push X» кладёт X в стек, «pop» снимает верхний элемент (если стек пуст — печатает «пусто»), «peek» печатает верхний элемент (или «пусто»), «size» печатает размер. Используйте match/case.",
             solution="""\
                stack = []
                while (line := input()) != "end":
                    match line.split():
                        case ["push", value]:
                            stack.append(value)
                        case ["pop"]:
                            if stack:
                                stack.pop()
                            else:
                                print("пусто")
                        case ["peek"]:
                            print(stack[-1] if stack else "пусто")
                        case ["size"]:
                            print(len(stack))""",
             starter="""\
                stack = []
                while (line := input()) != "end":
                    print(line)""",
             tests=["push 1\npush 2\npeek\npop\npeek\nsize\nend\n", "pop\npeek\nsize\nend\n",
                    "push a\npush b\npush c\nsize\npop\npop\npeek\nend\n", "size\nend\n"],
             hint="case [\"push\", value]: — шаблон из двух слов, второе попадёт в value.", difficulty=3,
             requires=dict(uses=["match"])),
    ],
    levels=[
        predict("py_idiom_001", "Шаблоны с условием", """\
                def describe(x):
                    match x:
                        case 0:
                            return "ноль"
                        case int() if x < 0:
                            return "отрицательное"
                        case int():
                            return "положительное"
                        case _:
                            return "не число"

                print(describe(-5), describe(0), describe("5"))""",
                ["отрицательное ноль положительное", "отрицательное положительное не число", "ноль ноль не число"],
                position=3, topic="idiom_match",
                hint="Срабатывает первый подходящий case. \"5\" — строка, а не int.",
                explanation="-5 — целое и меньше нуля. 0 совпадает с первым case. Строка «5» не подходит ни под 0, ни под int(), поэтому попадает в case _.",
                feedback={"отрицательное ноль положительное": "\"5\" — строка: шаблон int() её не принимает.",
                          "отрицательное положительное не число": "Для 0 первым подходит case 0.",
                          "ноль ноль не число": "Для -5 первый case не подходит, а второй — да."}),
        predict("py_idiom_002", "Шаблоны последовательностей", """\
                def parse(cmd):
                    match cmd.split():
                        case ["go", direction]:
                            return f"идём {direction}"
                        case ["take", *items]:
                            return f"берём {len(items)}"
                        case []:
                            return "пусто"
                        case _:
                            return "непонятно"

                print(parse("go west"), parse("take x y z"), parse("take"), parse("go"))""",
                ["идём west берём 3 непонятно непонятно", "идём west берём 3 берём 0 идём", "идём west берём 4 берём 1 непонятно"],
                position=1, topic="idiom_match",
                hint="*items может собрать и ноль элементов. [\"go\", direction] требует ровно два слова.",
                explanation="«go west» — два слова, direction = «west». «take x y z» — items из трёх. «take» — items пустой, это тоже подходит. «go» — одно слово, шаблон из двух не подходит.",
                role="practice", difficulty=2,
                feedback={"идём west берём 3 непонятно непонятно": "*items собирает и ноль элементов: «take» подходит под второй case.",
                          "идём west берём 3 берём 0 идём": "Шаблон [\"go\", direction] требует ровно два элемента, а в «go» один.",
                          "идём west берём 4 берём 1 непонятно": "Слово take не входит в items: в «take x y z» items — это x, y, z."}),
        fill("py_idiom_003", "Моржовый оператор", "Вычислите длину и сразу используйте её в условии",
             """\
             data = [3, 8, 1, 9]
             if (n {{0}} len(data)) > 3:
                 print(f"длинный список: {n}")""", [":=", "=", "==", "->"], [":="],
             topic="idiom_walrus", hint="Оператор присваивания внутри выражения похож на моржа.",
             explanation=":= присваивает n и возвращает значение, которое тут же сравнивается с 3. Обычное = внутри выражения — SyntaxError.",
             expect="длинный список: 4\n"),
        typed("py_idiom_004", "Звёздочка при распаковке", """\
              first, *middle, last = [1, 2, 3, 4, 5]
              print(first, middle, last)
              head, *tail = "abc"
              print(head, tail)""",
              topic="idiom_walrus", hint="*имя собирает все «лишние» элементы в список.",
              explanation="first и last берут крайние элементы, middle — список середины. Строка тоже распаковывается: head — «a», tail — список остальных символов."),
        match("py_idiom_005", "Шаблоны словарей",
              ["kind({'type': 'click', 'x': 5, 'y': 1})", "kind({'type': 'key', 'key': 'q'})",
               "kind({'type': 'scroll'})", "kind([1, 2])"],
              setup="""\
                def kind(event):
                    match event:
                        case {"type": "click", "x": x}:
                            return f"клик {x}"
                        case {"type": "key", "key": k}:
                            return f"клавиша {k}"
                        case {"type": t}:
                            return f"другое {t}"
                        case _:
                            return "?\"""",
              topic="idiom_match", hint="Шаблон словаря проверяет только перечисленные ключи, лишние не мешают.",
              explanation="Клик с лишним ключом y подходит под первый case. «key» — под второй. «scroll» — под общий {\"type\": t}. Список не словарь — case _."),
        bug("py_idiom_006", "Имя вместо константы", """\
            RED = "red"

            def check(color):
                match color:
                    case RED:
                        return "стоп"
                    case _:
                        return "можно"

            print(check("green"))""", {4: "        case \"red\":"},
            prompt="Для зелёного должно выводиться «можно». Найдите строку с ошибкой", topic="idiom_match",
            hint="Голое имя в case — это сравнение или захват?",
            explanation="case RED: не сравнивает с переменной RED, а захватывает любое значение в имя RED. Такой шаблон ловит всё, и Python запрещает ставить после него другие case: SyntaxError. Нужен литерал \"red\" или имя с точкой (Color.RED).",
            expect_error="SyntaxError", difficulty=3),
        multi("py_idiom_007", "Безопасное чтение", "Какие выражения вернут d['age'], а если ключа нет — 0, не вызывая ошибки?",
              GET_OPTIONS, [0, 1, 3], check=safe_get, topic="idiom_eafp",
              hint="Проверьте каждое выражение для пустого словаря.",
              explanation="get с default, условное выражение и setdefault возвращают значение или 0 (setdefault заодно записывает 0 в словарь). d['age'] or 0 падает с KeyError, d.age — AttributeError, а d.get(age, 0) обращается к несуществующей переменной age.",
              feedback={"d['age'] or 0": "d['age'] вычисляется первым и падает с KeyError, до or дело не доходит.",
                        "d.age": "К ключам словаря не обращаются через точку: AttributeError.",
                        "d.get(age, 0)": "Без кавычек age — имя переменной, а её нет: NameError."}),
        predict("py_idiom_008", "Отладочная f-строка", """\
                x, y = 3, 4
                print(f"{x + y = }")
                print(f"{x=}, {y=}")""",
                ["7\n3, 4", "x + y = 7\nx = 3, y = 4", "{x + y = }\n{x=}, {y=}"], position=1, topic="idiom_walrus",
                hint="= в конце выражения f-строки печатает само выражение и его значение. Пробелы вокруг = сохраняются как написаны.",
                explanation="f\"{x + y = }\" печатает текст выражения с пробелами, как в коде, и значение: «x + y = 7». В {x=} пробелов нет — получится «x=3».",
                role="practice", difficulty=2,
                feedback={"7\n3, 4": "Знак = в f-строке выводит и само выражение.",
                          "x + y = 7\nx = 3, y = 4": "Пробелы вокруг = берутся из кода: в {x=} их нет.",
                          "{x + y = }\n{x=}, {y=}": "Это f-строка: выражения в скобках вычисляются."}),
        predict("py_idiom_009", "Босс: шаблоны классов", """\
                from dataclasses import dataclass

                @dataclass
                class Point:
                    x: int
                    y: int

                def where(p):
                    match p:
                        case Point(x=0, y=0):
                            return "центр"
                        case Point(x=0, y=y):
                            return f"ось Y: {y}"
                        case Point(x=x, y=0):
                            return f"ось X: {x}"
                        case Point(x=x, y=y) if x == y:
                            return "диагональ"
                        case _:
                            return "где-то"

                print(", ".join(where(p) for p in [Point(0, 0), Point(0, 5), Point(3, 3), Point(2, 7)]))""",
                ["центр, ось Y: 5, где-то, где-то", "центр, ось Y: 5, диагональ, ось X: 2", "ось Y: 0, ось Y: 5, диагональ, где-то"],
                position=3, topic="idiom_match",
                hint="Шаблоны проверяются сверху вниз; у четвёртого есть условие x == y.",
                explanation="(0, 0) — центр, (0, 5) — ось Y, (3, 3) проходит условие диагонали, (2, 7) не подходит ни под что, кроме case _.",
                role="boss", difficulty=4,
                feedback={"центр, ось Y: 5, где-то, где-то": "Для (3, 3) срабатывает case с условием x == y.",
                          "центр, ось Y: 5, диагональ, ось X: 2": "Для (2, 7) шаблон Point(x=x, y=0) не подходит: y не 0.",
                          "ось Y: 0, ось Y: 5, диагональ, где-то": "(0, 0) первым ловит case Point(x=0, y=0)."}),
    ],
))

# ------------------------------------------------------------------ testing
LOGGING_FACTS = {
    "По умолчанию показываются сообщения уровня WARNING и выше":
        output_of("import logging, sys\nlogging.basicConfig(stream=sys.stdout, force=True)\n"
                  "logging.info('i')\nlogging.warning('w')").strip() == "WARNING:root:w",
    "logging.exception() внутри except записывает и трассировку":
        "Traceback" in output_of("import logging, sys\nlogging.basicConfig(stream=sys.stdout, force=True)\n"
                                 "try:\n    1 / 0\nexcept ZeroDivisionError:\n    logging.exception('сбой')"),
    "logging.debug() видно всегда, без настройки":
        output_of("import logging, sys\nlogging.basicConfig(stream=sys.stdout, force=True)\n"
                  "logging.debug('d')").strip() == "DEBUG:root:d",
    "Уровень меняют через basicConfig(level=...)":
        output_of("import logging, sys\nlogging.basicConfig(stream=sys.stdout, level=logging.DEBUG, force=True)\n"
                  "logging.debug('d')").strip() == "DEBUG:root:d",
    "По умолчанию logging пишет в stdout, как print":
        output_of("import logging\nlogging.basicConfig(force=True)\nlogging.warning('w')").strip() == "WARNING:root:w",
}

MODULES.append(dict(
    id="testing", title="Тестирование и отладка", description="assert, unittest, mock, logging", icon="🧪",
    topics=[
        topic("test_assert", "assert и тесты-функции",
              "assert условие, \"сообщение\" — проверка, которая падает с AssertionError, если условие ложно. Тест — функция, которая вызывает код и проверяет результат через assert.",
              """
              В стиле pytest тест — обычная функция test_...() с assert внутри; pytest находит их сам и показывает, где проверка не сошлась.

              Хороший тест проверяет один сценарий, включая крайние случаи: пустой ввод, ноль, отрицательные числа, повторы.

              assert — не для проверки пользовательского ввода: с флагом python -O все assert отключаются. Для данных пользователя — if и raise ValueError.

              Ловушка: assert (условие, "сообщение") с скобками проверяет непустой кортеж — он всегда истинен, и тест никогда не падает (Python 3.12 даже выдаёт SyntaxWarning).
              """,
              [("""\
                def median(nums):
                    s = sorted(nums)
                    mid = len(s) // 2
                    return s[mid] if len(s) % 2 else (s[mid - 1] + s[mid]) / 2

                def test_median():
                    assert median([3, 1, 2]) == 2
                    assert median([4, 1, 3, 2]) == 2.5
                    assert median([5]) == 5

                test_median()
                print("тесты прошли")""", None)],
              ["assert (x > 0, \"сообщение\") — кортеж всегда истинен, проверка не работает.",
               "Проверять assert-ом ввод пользователя: с python -O проверка исчезнет."]),
        topic("test_unittest", "unittest и mock",
              "unittest — встроенный фреймворк: класс-наследник TestCase, методы test_*, проверки assertEqual, assertRaises… unittest.mock подменяет зависимости.",
              """
              setUp() выполняется перед каждым тестом — там готовят данные. assertEqual(a, b), assertTrue(x), assertIn(item, container), with self.assertRaises(Error): ... — проверки с понятными сообщениями.

              Тесты запускают командой python -m unittest или pytest. Результат: число тестов, failures (проверка не сошлась) и errors (тест упал с исключением).

              Mock() — объект-заглушка: принимает любые вызовы и запоминает их. mock.method.call_count, call_args — чем и сколько раз его вызывали. Так тестируют код, который отправляет письма или ходит в сеть, не делая этого на самом деле.
              """,
              [("""\
                import io
                import unittest

                class TestDivide(unittest.TestCase):
                    def test_half(self):
                        self.assertEqual(10 / 4, 2.5)

                    def test_zero(self):
                        with self.assertRaises(ZeroDivisionError):
                            1 / 0

                suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestDivide)
                result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
                print(result.testsRun, len(result.failures), len(result.errors))""", "Отчёт перенаправлен в буфер, печатаем только итоги.")],
              ["Тест без проверок: он «проходит», даже если код сломан.",
               "Тест зависит от другого теста или от порядка запуска."]),
        topic("test_logging", "logging вместо print",
              "logging пишет сообщения с уровнем важности (DEBUG < INFO < WARNING < ERROR < CRITICAL), временем и источником; уровень и формат настраиваются в одном месте.",
              """
              logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s") — настройка один раз в начале программы. logging.getLogger(__name__) — свой логгер для модуля.

              По умолчанию видно WARNING и выше, а вывод идёт в stderr. В отличие от print, отладочные сообщения не нужно удалять: достаточно поднять уровень.

              logging.exception("текст") внутри except пишет сообщение уровня ERROR вместе с трассировкой.
              """,
              [("""\
                import logging
                import sys

                logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                                    format="%(levelname)s:%(name)s:%(message)s", force=True)
                log = logging.getLogger("app")
                log.debug("детали не видны")
                log.info("старт")
                log.warning("мало места")""", "stream=sys.stdout только для примера; force=True перенастраивает logging заново.")],
              ["Оставлять отладочные print в коде вместо logging.debug."]),
    ],
    tasks=[
        task("t_test_median", "Медиана с проверками",
             "Напишите функцию median(nums) и функцию test_median() с проверками assert (нечётная и чётная длина, один элемент). Вызовите test_median(), затем прочитайте числа через пробел и выведите медиану.",
             solution="""\
                def median(nums):
                    s = sorted(nums)
                    mid = len(s) // 2
                    return s[mid] if len(s) % 2 else (s[mid - 1] + s[mid]) / 2

                def test_median():
                    assert median([3, 1, 2]) == 2
                    assert median([4, 1, 3, 2]) == 2.5
                    assert median([7]) == 7

                test_median()
                print(median(list(map(int, input().split()))))""",
             starter="""\
                def median(nums):
                    return sorted(nums)[len(nums) // 2]

                print(median(list(map(int, input().split()))))""",
             tests=["3 1 2\n", "4 1 3 2\n", "10\n", "5 5 1 9 7 3\n"],
             hint="При чётной длине медиана — среднее двух центральных элементов.", difficulty=2,
             requires=dict(defines=["median", "test_median"], uses=["assert"], calls=["test_median"])),
    ],
    levels=[
        predict("py_test_001", "Сработавший assert", """\
                def average(xs):
                    assert xs, "пустой список"
                    return sum(xs) / len(xs)

                print(average([2, 4]))
                try:
                    average([])
                except AssertionError as e:
                    print("ошибка:", e)""",
                ["3.0\nZeroDivisionError", "3\nошибка: пустой список", "3.0\nошибка: AssertionError"], position=1,
                topic="test_assert", hint="Пустой список — ложь, assert падает раньше деления.",
                explanation="Для [2, 4] проверка проходит: 6 / 2 = 3.0. Для [] assert падает с AssertionError и своим сообщением — до деления на ноль дело не доходит.",
                feedback={"3.0\nZeroDivisionError": "assert срабатывает раньше деления и останавливает функцию.",
                          "3\nошибка: пустой список": "/ всегда даёт float: 3.0.",
                          "3.0\nошибка: AssertionError": "str(e) — это сообщение из assert, а не имя исключения."}),
        fill("py_test_002", "Проверка в unittest", "Проверьте, что add(2, 3) равно 5",
             """\
             import io
             import unittest

             def add(a, b):
                 return a + b

             class TestAdd(unittest.TestCase):
                 def test_sum(self):
                     self.{{0}}(add(2, 3), 5)

             suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAdd)
             result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
             print(result.wasSuccessful(), result.testsRun)""",
             ["assertEqual", "assertNotEqual", "assertIsNone", "assertIn"], ["assertEqual"],
             topic="test_unittest", hint="Нужно сравнить два значения на равенство.",
             explanation="assertEqual(a, b) проходит, если a == b. Остальные проверки здесь не сходятся, и тест не проходит.",
             expect="True 1\n"),
        predict("py_test_003", "Итоги прогона", """\
                import io
                import unittest

                class T(unittest.TestCase):
                    def test_ok(self):
                        self.assertEqual(2 * 2, 4)
                    def test_round(self):
                        self.assertEqual(round(2.5), 3)
                    def test_error(self):
                        with self.assertRaises(ZeroDivisionError):
                            1 / 0

                suite = unittest.defaultTestLoader.loadTestsFromTestCase(T)
                result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
                print(result.testsRun, len(result.failures), len(result.errors))""",
                ["3 0 0", "3 0 1", "3 1 1"], position=1, topic="test_unittest",
                hint="round(2.5) в Python — 2 (округление к чётному). assertRaises ожидает ошибку.",
                explanation="Тестов три. round(2.5) == 2, поэтому test_round — failure (проверка не сошлась). Деление на ноль ожидалось в assertRaises — это успех, а не error.",
                role="practice", difficulty=3,
                feedback={"3 0 0": "round(2.5) — это 2: test_round не проходит.",
                          "3 0 1": "Не сошедшаяся проверка — failure, а не error. А ошибка внутри assertRaises ожидалась.",
                          "3 1 1": "Деление на ноль поймано assertRaises — тест успешен."}),
        choice("py_test_004", "Тест, который не падает", "Почему этот тест никогда не падает, хотя функция сломана?",
               ["assert с кортежем всегда истинен", "is_even вызывается неправильно",
                "Тесты в Python не запускаются без pytest", "4 — чётное, поэтому проверка верна"], 0,
               code="""\
                def is_even(n):
                    return n % 2 == 1

                def test_is_even():
                    assert (is_even(4), "4 — чётное")

                test_is_even()
                print("тест пройден")""",
               check=lambda option: (option == "assert с кортежем всегда истинен") == run(
                   "def is_even(n):\n    return n % 2 == 1\n"
                   "def test_is_even():\n    assert (is_even(4), '4 — чётное')\n"
                   "test_is_even()\nprint('ok')").ok,
               topic="test_assert", hint="Что стоит после assert — условие или что-то другое?",
               explanation="assert (условие, \"сообщение\") проверяет кортеж из двух элементов. Непустой кортеж всегда истинен, поэтому тест проходит при любой функции. Нужно assert is_even(4), \"4 — чётное\" — без скобок.",
               role="practice", difficulty=3,
               feedback={"is_even вызывается неправильно": "Вызов корректен: проблема в том, что результат вообще не проверяется.",
                         "Тесты в Python не запускаются без pytest": "Функцию test_is_even вызывают вручную — она выполняется.",
                         "4 — чётное, поэтому проверка верна": "is_even(4) возвращает False, но assert проверяет не его, а кортеж."}),
        match("py_test_005", "Уровни логирования",
              ["logging.DEBUG", "logging.INFO", "logging.WARNING", "logging.ERROR", "logging.CRITICAL"],
              setup="import logging", topic="test_logging", hint="Уровни — числа с шагом 10.",
              explanation="Уровни — это числа: DEBUG 10, INFO 20, WARNING 30, ERROR 40, CRITICAL 50. Логгер показывает сообщения с уровнем не ниже настроенного."),
        multi("py_test_006", "Про logging", "Какие утверждения о модуле logging верны?",
              list(LOGGING_FACTS), [i for i, ok in enumerate(LOGGING_FACTS.values()) if ok],
              check=lambda statement: LOGGING_FACTS[statement], topic="test_logging",
              hint="Какой уровень у logging по умолчанию и куда он пишет?",
              explanation="По умолчанию logging показывает WARNING и выше и пишет в stderr. logging.exception добавляет трассировку. Уровень меняется в basicConfig(level=...).",
              feedback={"logging.debug() видно всегда, без настройки": "DEBUG ниже порога WARNING — без настройки не виден.",
                        "По умолчанию logging пишет в stdout, как print": "По умолчанию — в stderr, отдельно от обычного вывода."}),
        predict("py_test_007", "Тесты без фреймворка", """\
                def test_upper():
                    assert "ab".upper() == "AB"

                def test_split():
                    assert "a b".split() == ["a", "b", ""]

                passed = failed = 0
                for test in [test_upper, test_split]:
                    try:
                        test()
                        passed += 1
                    except AssertionError:
                        failed += 1
                print(passed, failed)""",
                ["2 0", "0 2", "1 0"], position=1, topic="test_assert",
                hint="split() без аргумента не оставляет пустых строк.",
                explanation="Первый тест проходит. split() без аргумента возвращает ['a', 'b'], без пустой строки, поэтому второй падает с AssertionError.",
                role="practice", difficulty=2,
                feedback={"2 0": "split() без аргумента не даёт пустую строку в конце: второй тест падает.",
                          "0 2": "\"ab\".upper() — это \"AB\": первый тест проходит.",
                          "1 0": "Упавший тест тоже считается — failed = 1."}),
        predict("py_test_008", "Записать вместо печати", """\
                import logging
                import sys

                logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                                    format="%(levelname)s:%(name)s:%(message)s", force=True)
                log = logging.getLogger("shop")
                log.debug("корзина: 3 товара")
                log.info("оплата принята")
                log.error("склад недоступен")""",
                ["DEBUG:shop:корзина: 3 товара\nINFO:shop:оплата принята\nERROR:shop:склад недоступен",
                 "оплата принята\nсклад недоступен", "ERROR:shop:склад недоступен"], position=1, topic="test_logging",
                hint="level=logging.INFO отсекает всё, что ниже INFO.",
                explanation="DEBUG ниже порога INFO и не выводится. Остальные сообщения форматируются по шаблону «уровень:имя логгера:сообщение».",
                role="practice", difficulty=2,
                feedback={"DEBUG:shop:корзина: 3 товара\nINFO:shop:оплата принята\nERROR:shop:склад недоступен": "Порог — INFO: DEBUG не проходит.",
                          "оплата принята\nсклад недоступен": "format добавляет уровень и имя логгера.",
                          "ERROR:shop:склад недоступен": "INFO не ниже порога INFO — сообщение выводится."}),
        predict("py_test_009", "Босс: заглушка вместо почты", """\
                from unittest.mock import Mock

                def notify(sender, users):
                    for user in users:
                        if user["active"]:
                            sender.send(user["email"], "Привет!")

                sender = Mock()
                notify(sender, [{"email": "a@x", "active": True}, {"email": "b@x", "active": False}])
                print(sender.send.call_count, sender.send.call_args.args)""",
                ["2 ('b@x', 'Привет!')", "1 ('b@x', 'Привет!')", "0 None"], position=3, topic="test_unittest",
                hint="Mock запоминает каждый вызов своих методов. call_args — аргументы последнего вызова.",
                explanation="Письмо уходит только активному пользователю: send вызван один раз с ('a@x', 'Привет!'). Mock ничего не отправляет, а только записывает вызовы — так тестируют код с внешними зависимостями.",
                role="boss", difficulty=4,
                feedback={"2 ('b@x', 'Привет!')": "Второй пользователь не активен: ему send не вызывается.",
                          "1 ('b@x', 'Привет!')": "b@x не активен — ему письмо не отправляется; единственный вызов был с a@x.",
                          "0 None": "Mock принимает любые вызовы и запоминает их — send был вызван."}),
    ],
))
