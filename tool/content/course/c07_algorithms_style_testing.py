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

              Цена операций Python: x in list — O(n) (просмотр всех элементов), x in set и d[key] — O(1) в среднем (хеш-таблица), list.append — O(1) амортизированно (изредка список расширяется с копированием), list.insert(0, x) и list.pop(0) — O(n) (сдвиг всех элементов), deque.appendleft/popleft — O(1), sorted — O(n log n).

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
                print("один проход с множеством:", ops)""", "Сравнение числа шагов: n² против n (плюс O(n) на построение множества).")],
              ["Проверять x in список внутри цикла по большому списку — это скрытый вложенный цикл O(n²).",
               "Оптимизировать «на глаз»: сначала измерьте, где программа тратит время."]),
        topic("algo_search_sort", "Поиск и сортировка",
              "Бинарный поиск находит элемент в отсортированном списке за O(log n). Модуль bisect делает это готово; sorted и sort — устойчивая сортировка O(n log n).",
              """
              Бинарный поиск каждый раз сравнивает с серединой и отбрасывает половину: для миллиона элементов хватает около 20 шагов (проверок середины). Работает только на отсортированных данных.

              bisect.bisect_left(a, x) — позиция, куда вставить x слева от равных, bisect_right — справа от равных, insort — вставка с сохранением порядка.

              Сортировка в Python устойчивая: элементы с равным ключом сохраняют исходный порядок. Поэтому сложную сортировку можно делать в несколько проходов или ключом-кортежем.
              """,
              [("""\
                import bisect

                scores = [10, 20, 30, 40]
                print(bisect.bisect_left(scores, 25), bisect.bisect_left(scores, 30), bisect.bisect_right(scores, 30))
                bisect.insort(scores, 25)
                print(scores)""", None)],
              ["Запускать бинарный поиск по неотсортированному списку — результат будет неверным, причём без всякой ошибки.",
               "Ошибка на единицу в границах: lo = mid вместо mid + 1 зацикливает поиск."]),
        topic("algo_patterns", "Приёмы: куча, очередь, окно, два указателя",
              "heapq — быстрый доступ к минимуму, deque — очередь для обхода в ширину (BFS), скользящее окно и два указателя — проход за O(n) вместо перебора пар.",
              """
              heapq хранит список как кучу: heappush/heappop за O(log n), минимум всегда в heap[0]. heapify(список) превращает готовый список в кучу за O(n). nlargest(k, data) — k наибольших. Кортежи в куче сравниваются поэлементно: при равных приоритетах сравнение дойдёт до второго элемента — если он несравним (словари), будет TypeError. Поэтому добавляют счётчик: (приоритет, номер, данные).

              Обход в ширину (BFS) на очереди deque находит кратчайшее число шагов в графе: соседи вершины обрабатываются раньше соседей соседей.

              Скользящее окно: сумму окна не пересчитывают заново, а прибавляют новый элемент и вычитают ушедший. Два указателя идут навстречу по отсортированному списку: если сумма мала — двигаем левый, велика — правый. Так пара с нужной суммой находится за один проход.
              """,
              [("""\
                import heapq

                tasks = [(3, "тесты"), (1, "баг в проде"), (2, "ревью")]
                heapq.heapify(tasks)
                while tasks:
                    priority, name = heapq.heappop(tasks)
                    print(priority, name)""", "Задача с наименьшим числом приоритета выходит первой."),
               ("""\
                nums = [4, 2, 7, 1, 8, 3]
                k = 2
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
             "В первой строке — отсортированные по возрастанию различные целые числа, во второй — числа для поиска. Для каждого искомого числа выведите его индекс или -1. Напишите функцию binary_search(items, target) сами — без bisect, index и оператора in. Последний тест большой: линейный перебор не успеет за 5 секунд.",
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
             tests=["1 3 5 7 9\n7 1 4\n", "2\n2 3\n", "-5 0 8 13 21 34\n34 -5 9 0\n", "10 20\n15\n",
                    " ".join(str(3 * i) for i in range(20000)) + "\n"
                    + " ".join(str(3 * i + i % 2) for i in range(0, 60000, 3)) + "\n"],
             hint="Держите границы lo и hi и сужайте их вокруг середины.", difficulty=3,
             requires=dict(defines=["binary_search"], uses=["while"], no_in_operator=["binary_search"],
                           no_calls=["index", "enumerate", "zip", "get"], no_imports=["bisect"])),
        task("t_algo_unique_fast", "Без повторов, но быстро",
             "В строке — целые числа через пробел, записанные без ведущих нулей (их может быть очень много). Выведите числа без повторов в порядке первого появления. Решение должно работать за один проход: на большом тесте вложенный перебор не успеет за 5 секунд.",
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
             tests=["3 1 3 2 1\n", "5\n", "1 1 1 1\n", " ".join(str(i % 60013) for i in range(120000)) + "\n"],
             hint="Множество проверяет «было ли уже» за O(1), список — за O(n).", difficulty=3),
    ],
    levels=[
        choice("py_algo_001", "Сколько шагов", "Сколько раз в худшем случае бинарный поиск проверит середину в отсортированном списке из 1 000 000 элементов?",
               ["около 20", "около 1 000", "около 500 000", "1 000 000"], 0,
               check=lambda option: (option == "около 20") == (math.ceil(math.log2(10 ** 6 + 1)) == 20),
               topic="algo_search_sort", hint="Каждая проверка отбрасывает половину оставшихся элементов.",
               explanation="Делений пополам хватит log₂(1 000 000) ≈ 20: 2²⁰ = 1 048 576. Поэтому бинарный поиск — O(log n).",
               feedback={"около 1 000": "Это √n. Бинарный поиск делит пополам: нужно около log₂ n проверок.",
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
            def best_window(nums, k):
                best = 0
                for i in range(len(nums) - k):
                    best = max(best, sum(nums[i:i + k]))
                return best

            print(best_window([2, 1, 5, 1, 3], 3), best_window([4, 4, 1, 1], 2))""",
            {2: "    for i in range(len(nums) - k + 1):"},
            alt_fixes={3: "        best = max(best, sum(nums[i + 1:i + k + 1]))"},
            prompt="Нужна наибольшая сумма k подряд идущих чисел: 9 и 8. Найдите строку с ошибкой", topic="algo_patterns",
            hint="Сколько окон длины k в списке из n элементов?",
            explanation="Окон длины k ровно n - k + 1. range(n - k) пропускает последнее окно [5, 1, 3] с суммой 9 — классическая ошибка на единицу.",
            difficulty=3),
        multi("py_algo_008", "O(1) в среднем", "Какие операции выполняются за O(1) (в среднем или амортизированно), независимо от размера коллекции?",
              list(O1_OPERATIONS), [i for i, ok in enumerate(O1_OPERATIONS.values()) if ok],
              check=lambda op: O1_OPERATIONS[op], topic="algo_complexity",
              hint="Хеш-таблицы и добавление в конец — быстро. Сдвиг всех элементов и просмотр всех — медленно.",
              explanation="Множество и словарь ищут по хешу, append пишет в конец, deque снимает элемент с начала без сдвигов. insert(0, x) сдвигает все элементы списка, x in список просматривает их по очереди — O(n).",
              feedback={"список.insert(0, x)": "Вставка в начало сдвигает все элементы — O(n). Для очереди — deque.",
                        "x in список": "Список просматривается по очереди — O(n)."}),
        bug("py_algo_010", "Ничья в куче", """\
            import heapq
            from itertools import count

            order = count()
            heap = []
            heapq.heappush(heap, (1, {"name": "отчёт"}))
            heapq.heappush(heap, (1, {"name": "ревью"}))
            print(heapq.heappop(heap)[-1]["name"])""",
            {5: "heapq.heappush(heap, (1, next(order), {\"name\": \"отчёт\"}))",
             6: "heapq.heappush(heap, (1, next(order), {\"name\": \"ревью\"}))"},
            expect_error="TypeError", prompt="Программа падает при равных приоритетах. Отметьте все строки с ошибкой",
            topic="algo_patterns",
            hint="Как сравниваются два кортежа с одинаковым первым элементом? А можно ли сравнить два словаря через <?",
            explanation="При равных приоритетах куча сравнивает вторые элементы кортежей — словари, а для них < не определён: TypeError. Номер из count() между приоритетом и данными делает каждый кортеж уникальным, и до словарей сравнение не доходит. Обе вставки должны иметь одинаковый вид.",
            difficulty=3),
        predict("py_algo_011", "Два указателя", """\
                def pair_sum(nums, target):
                    lo, hi = 0, len(nums) - 1
                    steps = 0
                    while lo < hi:
                        steps += 1
                        s = nums[lo] + nums[hi]
                        if s == target:
                            return nums[lo], nums[hi], steps
                        if s < target:
                            lo += 1
                        else:
                            hi -= 1
                    return None

                print(pair_sum([1, 3, 4, 6, 8, 11], 10))""",
                ["(4, 6, 3)", "(1, 8, 2)", "None"], position=3, topic="algo_patterns", role="practice", difficulty=3,
                hint="Пройдите вручную: 1 + 11, затем сдвиг правого указателя, и так далее. Считайте каждую проверку суммы.",
                explanation="1 + 11 = 12 — много, hi влево; 1 + 8 = 9 — мало, lo вправо; 3 + 8 = 11 — много; 3 + 6 = 9 — мало; 4 + 6 = 10 — нашли на пятом шаге. Каждый шаг сдвигает один указатель, поэтому проход — O(n).",
                feedback={"(4, 6, 3)": "Посчитайте шаги заново: пара находится на пятой проверке.",
                          "(1, 8, 2)": "1 + 8 = 9, а нужно 10.",
                          "None": "Пара 4 + 6 = 10 в списке есть."}),
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
                explanation="Из A за шаг достижимы B и C, за два — D и E, за три — F. Очередь гарантирует, что первая найденная дорога — кратчайшая по числу рёбер (в графе без весов); словарь хранит вершины в порядке открытия.",
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
              case 0: — литерал. case [x, y]: — список из двух элементов (x и y получают значения). case ["take", *items]: — первый элемент «take», остальные в items. case {"type": "click", "x": x}: — словарь с такими ключами (лишние ключи допускаются). case Point(x=0, y=y): — объект класса с полями (позиционно, case Point(0, y):, — если у класса есть __match_args__; у dataclass он создаётся сам). case str(): — проверка типа. case _: — всё остальное. Строка не подходит под шаблон последовательности [a, b], хотя её и можно перебирать.

              После шаблона можно добавить условие: case int() if x < 0:. Срабатывает первый подходящий case.

              Голое имя в case — это захват, а не сравнение: case RED: поймает что угодно и запишет в RED (Python не даст поставить такой case не последним — SyntaxError). Для сравнения с константой нужно имя с точкой: case Color.RED:.
              """,
              [("""\
                def command(text):
                    match text.split():
                        case ["move", x, y]:
                            return f"перемещение на ({x}, {y})"
                        case ["say", *words]:
                            return " ".join(words) or "(молчание)"
                        case ["quit"]:
                            return "выход"
                        case _:
                            return "неизвестная команда"

                print(command("move 3 4"), "|", command("say всем привет"), "|", command("quit"), "|", command("jump"))""", None)],
              ["Писать case RED: для сравнения с переменной: это захват любого значения.",
               "Ждать, что match работает как switch в других языках «с проваливанием»: срабатывает не больше одного case, а если ни один не подошёл — ничего не происходит, ошибки нет."]),
        topic("idiom_walrus", "Моржовый оператор и распаковка",
              ":= присваивает значение внутри выражения. Звёздочка при распаковке собирает «всё остальное»: first, *rest = items.",
              """
              if (n := len(data)) > 10: — вычисляет длину один раз, сохраняет в n и сразу сравнивает. Удобно в while: while (line := f.readline()):.

              head, *body, tail = "питон" — звёздочка собирает середину в список. a, b = b, a — обмен без временной переменной.

              f"{x + y = }" — f-строка с = печатает и выражение, и его значение: удобно для отладки.
              """,
              [("""\
                words = ["лес", "река", "гора"]
                while (word := words.pop()) != "лес":
                    print("обрабатываю", word)
                head, *rest = "питон"
                print(head, rest)
                a, b = 2, 5
                print(f"{a * b = }")""", None)],
              ["Писать if n = len(data): — в условии = недопустим, нужен :=.",
               "Забыть скобки: if n := len(data) > 3: присвоит n результат сравнения (True), а не длину."]),
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
                hint="Сколько элементов может собрать *items? А сколько слов нужно первому шаблону?",
                explanation="«go west» — два слова, direction = «west». «take x y z» — items из трёх. «take» — items пустой, это тоже подходит. «go» — одно слово, шаблон из двух не подходит.",
                role="practice", difficulty=2,
                feedback={"идём west берём 3 непонятно непонятно": "*items собирает и ноль элементов: «take» подходит под второй case.",
                          "идём west берём 3 берём 0 идём": "Шаблон [\"go\", direction] требует ровно два элемента, а в «go» один.",
                          "идём west берём 4 берём 1 непонятно": "Слово take не входит в items: в «take x y z» items — это x, y, z."}),
        fill("py_idiom_003", "Вычислить и сравнить", "Посчитайте слова и сразу используйте число в условии",
             """\
             text = "раз два три"
             if (k {{0}} len(text.split())) >= 3:
                 print(f"слов: {k}")""", [":=", "=", "==", "->"], [":="],
             topic="idiom_walrus", hint="Нужен оператор, который присваивает внутри выражения.",
             explanation=":= присваивает k и возвращает значение, которое тут же сравнивается с 3. Обычное = внутри выражения — SyntaxError, а == сравнило бы с несуществующим k.",
             expect="слов: 3\n"),
        predict("py_idiom_010", "Скобки у моржа", """\
                data = [3, 8, 1, 9]
                if n := len(data) > 3:
                    print(n)""",
                ["4", "3", "SyntaxError"], position=0, topic="idiom_walrus", role="practice", difficulty=3,
                hint=":= связывает слабее, чем сравнение >. Что вычислится первым?",
                explanation="Без скобок выражение читается как n := (len(data) > 3): n получает результат сравнения — True. Чтобы сохранить длину, пишут (n := len(data)) > 3.",
                feedback={"4": "Без скобок в n попадает результат сравнения len(data) > 3.",
                          "3": "n получает не число, а результат сравнения.",
                          "SyntaxError": "Это корректный код: := внутри if допустим и без скобок."}),
        predict("py_idiom_011", "Строка — не пара", """\
                def kind(x):
                    match x:
                        case [a, b]:
                            return f"пара {a}{b}"
                        case str():
                            return "строка"
                        case _:
                            return "другое"

                print(kind("ab"), kind(["a", "b"]), kind((1, 2)), kind({1, 2}))""",
                ["пара ab пара ab пара 12 другое", "строка пара ab другое другое", "строка пара ab пара 12 пара 12"],
                position=1, topic="idiom_match", role="practice", difficulty=3,
                hint="Шаблон последовательности принимает списки и кортежи. А строки и множества?",
                explanation="Строки, bytes и bytearray намеренно не подходят под шаблон последовательности, хотя их можно перебирать. Список и кортеж подходят. Множество не последовательность — case _.",
                feedback={"пара ab пара ab пара 12 другое": "Строка не подходит под [a, b] — она попадает в case str().",
                          "строка пара ab другое другое": "Кортеж — тоже последовательность: (1, 2) подходит под [a, b].",
                          "строка пара ab пара 12 пара 12": "Множество не упорядочено и не последовательность: case _."}),
        typed("py_idiom_004", "Звёздочка при распаковке", """\
              *init, tail = (10, 20, 30)
              print(init, tail)
              a, *b = "xy"
              print(a, b)
              x, *y, z = [1, 2]
              print(x, y, z)""",
              topic="idiom_walrus", hint="*имя собирает все «лишние» элементы в список — даже если их нет.",
              explanation="Звёздочка всегда даёт список: из кортежа — [10, 20], из строки — ['y']. Если «лишних» элементов нет, получается пустой список."),
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
        multi("py_idiom_007", "Безопасное чтение", "Какие выражения вернут d['age'], а если ключа нет — 0, не вызывая ошибки (изменять словарь допустимо)?",
              GET_OPTIONS, [0, 1, 3], check=safe_get, topic="idiom_eafp",
              hint="Проверьте каждое выражение для пустого словаря.",
              explanation="get с default, условное выражение и setdefault возвращают значение или 0 (setdefault заодно записывает 0 в словарь). d['age'] or 0 падает с KeyError, d.age — AttributeError, а d.get(age, 0) обращается к несуществующей переменной age.",
              feedback={"d['age'] or 0": "d['age'] вычисляется первым и падает с KeyError, до or дело не доходит.",
                        "d.age": "К ключам словаря не обращаются через точку: AttributeError.",
                        "d.get(age, 0)": "Без кавычек age — имя переменной, а её нет: NameError."}),
        predict("py_idiom_012", "Попросить прощения", """\
                def read_port(cfg):
                    try:
                        return int(cfg["port"])
                    except KeyError:
                        return 8000
                    except ValueError:
                        return -1

                print(read_port({}), read_port({"port": "80a"}), read_port({"port": "443"}))""",
                ["8000 8000 443", "-1 -1 443", "KeyError"], position=1, topic="idiom_eafp", role="practice", difficulty=2,
                hint="Какое исключение возникает, если ключа нет, а какое — если строку нельзя превратить в число?",
                explanation="EAFP: сразу пробуем прочитать и преобразовать, а неудачи разбираем по типу. Нет ключа — KeyError и порт по умолчанию 8000; «80a» не число — ValueError и -1.",
                feedback={"8000 8000 443": "«80a» есть в словаре: ошибка возникает в int() — это ValueError.",
                          "-1 -1 443": "Для пустого словаря возникает KeyError — его ветка возвращает 8000.",
                          "KeyError": "KeyError перехвачен в except и превращён в 8000."}),
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
              В стиле pytest тест — обычная функция test_...() с assert внутри; pytest находит их сам и показывает, где проверка не сошлась. pytest — сторонний пакет (pip install pytest), в стандартной библиотеке его нет; встроенные инструменты — unittest и doctest.

              doctest проверяет примеры прямо в docstring: строки >>> выполняются, и их вывод сравнивается с текстом ниже. Так документация не устаревает.

              Дробные числа сравнивают с допуском: math.isclose(a, b) или assertAlmostEqual, потому что 0.1 + 0.2 != 0.3.

              Хороший тест проверяет один сценарий, включая крайние случаи: пустой ввод, ноль, отрицательные числа, повторы.

              assert — не для проверки пользовательского ввода: с флагом python -O все assert отключаются. Для данных пользователя — if и raise ValueError.

              Ловушка: assert (условие, "сообщение") со скобками проверяет непустой кортеж — он всегда истинен, и тест никогда не падает (Python выдаёт SyntaxWarning).
              """,
              [("""\
                def clamp(x, lo, hi):
                    return max(lo, min(x, hi))

                def test_clamp():
                    assert clamp(5, 0, 10) == 5
                    assert clamp(-3, 0, 10) == 0, "ниже нижней границы"
                    assert clamp(99, 0, 10) == 10

                test_clamp()
                print("тесты прошли")""", None)],
              ["assert (x > 0, \"сообщение\") — кортеж всегда истинен, проверка не работает.",
               "Проверять assert-ом ввод пользователя: с python -O проверка исчезнет."]),
        topic("test_unittest", "unittest и mock",
              "unittest — встроенный фреймворк: класс-наследник TestCase, методы test_*, проверки assertEqual, assertRaises… unittest.mock подменяет зависимости.",
              """
              setUp() выполняется перед каждым тестом — там готовят данные. assertEqual(a, b), assertTrue(x), assertIn(item, container), with self.assertRaises(Error): ... — проверки с понятными сообщениями.

              Тесты запускают командой python -m unittest или pytest. Результат: число тестов, failures (проверка не сошлась) и errors (тест упал с исключением).

              result.wasSuccessful() — True, если нет ни failures, ни errors.

              Mock() — объект-заглушка: принимает любые вызовы и запоминает их. mock.method.call_count — сколько раз вызывали, call_args.args — кортеж позиционных аргументов последнего вызова. Так тестируют код, который отправляет письма или ходит в сеть, не делая этого на самом деле.

              with patch("модуль.имя", return_value=...): временно подменяет функцию там, где её ищут при вызове, и возвращает всё обратно после блока.
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
              "logging пишет сообщения с уровнем важности (DEBUG < INFO < WARNING < ERROR < CRITICAL); формат можно дополнить временем и источником (%(asctime)s, %(name)s), а уровень и формат настраиваются в одном месте.",
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
             "Напишите функцию median(nums) и функцию test_median() — в ней не меньше трёх assert, каждый вызывает median (нечётная и чётная длина, один элемент). Вызовите test_median(), затем прочитайте целые числа через пробел и выведите медиану: при нечётной длине — сам средний элемент (для 3 1 2 → 2), при чётной — среднее двух центральных как дробное число (для 1 3 → 2.0). Модуль statistics не используйте.",
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
             requires=dict(defines=["median", "test_median"], calls=["test_median"], no_imports=["statistics"],
                           calls_in={"test_median": ["median"]}, asserts_in={"test_median": 3})),
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
             explanation="assertEqual(a, b) проходит, если a == b. Остальные не проходят: assertNotEqual и assertIsNone дают failure, а assertIn(5, 5) — error (TypeError: в число нельзя искать вхождение).",
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
                hint="Чем failure отличается от error? Вспомните, как round округляет половинки.",
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
        predict("py_test_005", "Подмена через patch", """\
                from unittest.mock import patch
                import random

                def roll():
                    return random.randint(1, 6) * 10

                with patch("random.randint", return_value=4) as fake:
                    print(roll(), fake.call_args.args)
                print(roll() in range(10, 61, 10))""",
                ["40 (4,)\nTrue", "40 (1, 6)\nFalse", "4 (1, 6)\nTrue"], position=1, topic="test_unittest",
                role="practice", difficulty=3,
                hint="Внутри with randint всегда возвращает 4. Что в call_args — результат или аргументы вызова? И что происходит после блока?",
                explanation="patch подменяет random.randint заглушкой, которая возвращает 4: roll() даёт 40, а call_args.args — аргументы вызова (1, 6). После with настоящий randint возвращается, и roll() снова даёт одно из 10, 20, …, 60.",
                feedback={"40 (4,)\nTrue": "call_args хранит аргументы, с которыми вызвали заглушку, а не её результат.",
                          "40 (1, 6)\nFalse": "После блока with подмена снимается: roll() снова работает по-настоящему.",
                          "4 (1, 6)\nTrue": "roll умножает результат randint на 10."}),
        predict("py_test_010", "doctest", """\
                import doctest

                def mid(a, b):
                    \"\"\"Середина отрезка.

                    >>> mid(2, 4)
                    3.0
                    >>> mid(1, 2)
                    1
                    \"\"\"
                    return (a + b) / 2

                runner = doctest.DocTestRunner()
                for test in doctest.DocTestFinder().find(mid, globs=globals()):
                    print(runner.run(test, out=lambda text: None))""",
                ["TestResults(failed=0, attempted=2)", "TestResults(failed=2, attempted=2)",
                 "TestResults(failed=1, attempted=1)"], position=1, topic="test_assert", role="practice", difficulty=3,
                hint="doctest сравнивает вывод с текстом буквально. Что напечатает mid(1, 2)?",
                explanation="Примеров два. mid(2, 4) печатает 3.0 — совпадает. mid(1, 2) печатает 1.5, а в docstring написано 1 — пример не сошёлся. doctest не останавливается на первой ошибке: попыток 2, неудач 1.",
                feedback={"TestResults(failed=0, attempted=2)": "mid(1, 2) — это 1.5, а в docstring ожидается 1.",
                          "TestResults(failed=2, attempted=2)": "mid(2, 4) печатает 3.0 — первый пример сходится.",
                          "TestResults(failed=1, attempted=1)": "doctest выполняет все примеры, даже после неудачи."}),
        fill("py_test_011", "Дробные числа в тестах", "Сравните сумму с 0.3 так, чтобы тест прошёл",
             """\
             import io
             import unittest

             class TestMoney(unittest.TestCase):
                 def test_sum(self):
                     self.{{0}}(0.1 + 0.2, 0.3)

             suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestMoney)
             result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
             print(result.wasSuccessful(), 0.1 + 0.2 == 0.3)""",
             ["assertAlmostEqual", "assertEqual", "assertIs", "assertLess"], ["assertAlmostEqual"],
             topic="test_unittest", hint="0.1 + 0.2 в двоичной арифметике — не ровно 0.3.",
             explanation="0.1 + 0.2 = 0.30000000000000004, поэтому assertEqual и == дают «не равно». assertAlmostEqual сравнивает с точностью до 7 знаков после запятой (как и math.isclose — с допуском).",
             role="practice", difficulty=2, expect="True False\n"),
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
                hint="Что именно возвращает \"a b\".split()?",
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
