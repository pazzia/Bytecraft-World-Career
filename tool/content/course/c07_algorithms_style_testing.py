"""Модули 31–33: алгоритмы и сложность, идиомы Python, тестирование и
отладка."""
import math

from bclib import (choice, fill, match, multi, order, predict, bug, typed, topic, pitfall, task, run,
                   categorize, true_false)


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
              "O-большое показывает, во сколько раз дольше станет работа программы, когда данных станет больше.",
              """
              На десяти элементах любой код работает мгновенно. Разница видна на миллионе: один алгоритм справится за долю секунды, другой — за часы. Оценка сложности позволяет заметить это до запуска.

              ## Что значит O(n)

              O-большое описывает не точное число операций, а порядок роста. Константы и мелкие слагаемые отбрасывают: `2 * n + 5` шагов — это O(n).

              | Запись | Рост | Пример |
              |---|---|---|
              | O(1) | не зависит от n | {`d[key]`} |
              | O(log n) | логарифмический | бинарный поиск |
              | O(n) | линейный | один проход {`for`} |
              | O(n log n) | чуть хуже линейного | {`sorted`} |
              | O(n²) | квадратичный | два вложенных цикла |

              Для n = 1 000 000 разница между O(n) и O(n²) — миллион операций против триллиона.

              ## Цена операций Python

              - `x in список` — O(n): элементы просматриваются по очереди
              - `x in множество`, `d[key]` — O(1) в среднем: поиск по хешу
              - `список.append(x)` — O(1) в среднем
              - `список.insert(0, x)`, `список.pop(0)` — O(n): сдвигают все элементы
              - [[std_deque|`deque.popleft()`]] — O(1)
              - `sorted(данные)` — O(n log n)

              «В среднем» у `append` значит: изредка список расширяется и копируется целиком, но на одно добавление это всё равно O(1).

              ## Как ускорить

              Частый приём — заменить поиск в списке на [[set_basics|множество]] или словарь. Проверка `x in список` внутри цикла — скрытый вложенный цикл O(n²), а с множеством остаётся один проход O(n).

              Прежде чем ускорять, найдите, где программа на самом деле тратит время: [[perf_measure|замеры скорости]].
              """,
              [("""\
                n = 100
                steps = 0
                for a in range(n):
                    for b in range(n):
                        steps += 1
                print(steps)""",
                "Два вложенных цикла по 100 — уже 10 000 шагов"),
               ("""\
                def find(items, x):
                    steps = 0
                    for item in items:
                        steps += 1
                        if item == x:
                            break
                    return steps

                data = list(range(1000))
                print(find(data, 999))
                print(999 in set(data))""",
                "Поиск последнего элемента списка — тысяча сравнений"),
               ("""\
                import math

                for n in (1_000, 1_000_000):
                    print(n, math.ceil(math.log2(n)))""",
                "Бинарному поиску хватает 10 и 20 шагов там, где проходу нужно n")],
              [pitfall("x in список внутри цикла — скрытый вложенный цикл O(n²). Множество проверяет за O(1).",
                       bad='''
                           for order in orders:
                               if order in banned_list:
                                   skip(order)''',
                       good='''
                           banned = set(banned_list)
                           for order in orders:
                               if order in banned:
                                   skip(order)'''),
               pitfall("pop(0) сдвигает все элементы — O(n) на каждом шаге. У deque есть popleft за O(1).",
                       bad="job = queue.pop(0)",
                       good="job = queue.popleft()"),
               "Считать O(1) «мгновенным»: это значит лишь, что время не растёт вместе с данными."]),
        topic("algo_search_sort", "Поиск и сортировка",
              "Бинарный поиск находит элемент в отсортированном списке за O(log n), а сортировка в Python устойчивая.",
              """
              Найти слово в словаре, место для нового рекорда в таблице, нужную версию среди релизов — всё это поиск. Если данные отсортированы, искать можно не по одному элементу, а делением пополам.

              ## Как работает бинарный поиск

              1. Берут середину диапазона.
              2. Если искомое равно середине — элемент найден.
              3. Если искомое больше — дальше ищут правее середины, если меньше — левее.
              4. Если диапазон опустел — элемента нет.

              Каждый шаг отбрасывает половину: для миллиона элементов хватает около 20 сравнений. **Работает только на отсортированных данных.** На неотсортированных ответ будет неверным, но без ошибки.

              Середина уже проверена, поэтому границы сдвигают за неё: `lo = mid + 1` или `hi = mid - 1`. Без `+ 1` диапазон может перестать сужаться, и цикл не закончится.

              ## Модуль bisect

              - `bisect.bisect_left(a, x)` — позиция для `x` левее равных ему
              - `bisect.bisect_right(a, x)` — позиция правее равных
              - `bisect.insort(a, x)` — вставить `x`, сохранив порядок

              Функции возвращают позицию, а не ответ «есть или нет». Чтобы найти элемент, проверяют `i < len(a) and a[i] == x`.

              ## Устойчивая сортировка

              `sorted` и `list.sort` работают за O(n log n) и устойчивы: элементы с равным ключом сохраняют исходный порядок. Поэтому сортировку по двум признакам делают [[fn_lambda_key|ключом]]-кортежем или в два прохода, начиная со второстепенного признака.
              """,
              [("""\
                def search(items, x):
                    lo, hi = 0, len(items) - 1
                    steps = 0
                    while lo <= hi:
                        steps += 1
                        mid = (lo + hi) // 2
                        if items[mid] == x:
                            return mid, steps
                        if items[mid] < x:
                            lo = mid + 1
                        else:
                            hi = mid - 1
                    return -1, steps

                nums = list(range(0, 2000, 2))
                print(search(nums, 1500))
                print(search(nums, 7))""",
                "Тысяча чисел, а сравнений около десяти — и для найденного, и нет"),
               ("""\
                import bisect

                ranks = [100, 250, 400]
                pos = bisect.bisect_left(ranks, 300)
                print(pos)
                bisect.insort(ranks, 300)
                print(ranks)""",
                "Позиция для 300 — между 250 и 400; insort вставил туда же"),
               ("""\
                players = [("Ада", 3), ("Боб", 5),
                           ("Ева", 3), ("Лев", 5)]
                by_score = sorted(players,
                                  key=lambda p: p[1])
                print(by_score)""",
                "При равных очках порядок исходный: Ада раньше Евы")],
              [pitfall("На неотсортированном списке бинарный поиск молча даёт неверный ответ.",
                       bad="i = bisect.bisect_left(nums, x)",
                       good='''
                           nums.sort()
                           i = bisect.bisect_left(nums, x)'''),
               pitfall("С lo = mid диапазон перестаёт сужаться, и цикл while не заканчивается.",
                       bad="lo = mid", good="lo = mid + 1"),
               pitfall("bisect_left возвращает позицию, а не «найдено»: 0 — тоже позиция. Проверьте элемент на ней.",
                       bad="found = bool(bisect.bisect_left(a, x))",
                       good='''
                           i = bisect.bisect_left(a, x)
                           found = i < len(a) and a[i] == x''')]),
        topic("algo_patterns", "Куча: heapq",
              "Куча — список, в котором наименьший элемент всегда первый; `heapq` достаёт его за O(log n).",
              """
              Очередь задач по приоритету, ближайшее событие в календаре, k лучших результатов — везде нужен быстрый доступ к минимуму. Сортировать список после каждого добавления долго, куча делает это дешевле.

              ## Как записать

              ```syntax
              import heapq

              heapq.heappush(куча, элемент)
              наименьший = heapq.heappop(куча)
              ```

              Куча — обычный список, который меняют только функциями `heapq`. Наименьший элемент всегда в `куча[0]`.

              ## Функции heapq

              - `heappush(h, x)` — добавить, O(log n)
              - `heappop(h)` — снять наименьший, O(log n)
              - `heapify(список)` — превратить готовый список в кучу, O(n)
              - `nlargest(k, данные)`, `nsmallest(k, данные)` — k наибольших или наименьших

              Куча не отсортирована целиком: упорядочено только то, что нужно для быстрого минимума. Поэтому `print(h)` покажет «странный» порядок.

              ## Приоритет и данные

              Задачи кладут [[tuple_basics|кортежем]] `(приоритет, данные)`: кортежи сравниваются поэлементно. При равных приоритетах сравнение дойдёт до данных, и если это словари — `TypeError`.

              Поэтому между приоритетом и данными ставят уникальный номер: `(приоритет, номер, данные)`. Номера удобно брать из `itertools.count()` ([[std_itertools|itertools]]).

              ## Что выбрать

              - Элементы постоянно добавляются, а нужен только минимум — куча.
              - Нужен весь порядок один раз — `sorted`.
              - Очередь «первым пришёл — первым ушёл» — [[std_deque|`deque`]].
              """,
              [("""\
                import heapq

                h = []
                for x in [5, 1, 8, 3]:
                    heapq.heappush(h, x)
                print(h[0])
                print(heapq.heappop(h))
                print(heapq.heappop(h))""",
                "Первым всегда выходит наименьший элемент"),
               ("""\
                import heapq

                queue = [(3, "письмо"),
                         (1, "сервер упал"),
                         (2, "ревью")]
                heapq.heapify(queue)
                while queue:
                    prio, task = heapq.heappop(queue)
                    print(prio, task)""",
                "Задачи выходят по возрастанию числа приоритета"),
               ("""\
                import heapq

                h = [9, 4, 7, 1, 8]
                heapq.heapify(h)
                print(h)
                print(heapq.nsmallest(2, h))""",
                "Куча не отсортирована целиком — первым стоит только минимум")],
              [pitfall("При равных приоритетах сравниваются данные: TypeError: '<' not supported between instances of 'dict' and 'dict'.",
                       bad="heapq.heappush(h, (1, task))",
                       good="heapq.heappush(h, (1, next(order), task))"),
               pitfall("heappop на списке, который не стал кучей, не обязан вернуть минимум: сначала heapify.",
                       bad='''
                           h = [5, 1, 3]
                           heapq.heappop(h)''',
                       good='''
                           h = [5, 1, 3]
                           heapq.heapify(h)
                           heapq.heappop(h)'''),
               "Ждать от print(h) отсортированный список: в куче упорядочен только путь к минимуму."]),
        topic("algo_bfs", "Обход в ширину",
              "Обход в ширину перебирает граф слоями и находит путь с наименьшим числом шагов.",
              """
              Сколько пересадок до нужной станции, через скольких знакомых вы связаны с человеком, за сколько ходов фигура дойдёт до клетки — всё это кратчайший путь в графе. Для графа без весов его находит обход в ширину (BFS).

              ## Граф в Python

              Граф — вершины и связи между ними. Его хранят словарём: ключ — вершина, значение — список соседей. Например, `{"A": ["B", "C"], "B": [], "C": []}`.

              ## Как записать

              ```syntax
              from collections import deque

              dist = {старт: 0}
              queue = deque([старт])
              while queue:
                  v = queue.popleft()
                  for сосед in граф[v]:
                      if сосед not in dist:
                          dist[сосед] = dist[v] + 1
                          queue.append(сосед)
              ```

              ## Почему путь кратчайший

              Очередь выдаёт вершины в порядке открытия: сначала все на расстоянии 1, потом все на расстоянии 2 и так далее. Поэтому первая найденная дорога к вершине — самая короткая по числу рёбер.

              Словарь `dist` заодно помнит посещённые вершины. Без проверки {`not in dist`} обход ходил бы по кругу.

              ## Почему deque

              `list.pop(0)` сдвигает все элементы — O(n) на каждом шаге. [[std_deque|`deque`]] снимает первый элемент за O(1). Весь обход — O(V + E), где V — число вершин, E — число связей.

              Если снимать вершины с конца, как из стека, получится обход в глубину. Он тоже посетит всё, но кратчайший путь не гарантирует.
              """,
              [("""\
                from collections import deque

                metro = {
                    "Центр": ["Парк", "Рынок"],
                    "Парк": ["Вокзал"],
                    "Рынок": ["Вокзал"],
                    "Вокзал": [],
                }
                dist = {"Центр": 0}
                queue = deque(["Центр"])
                while queue:
                    st = queue.popleft()
                    for nxt in metro[st]:
                        if nxt not in dist:
                            dist[nxt] = dist[st] + 1
                            queue.append(nxt)
                print(dist)""",
                "До Вокзала две дороги, но расстояние одно — 2 шага"),
               ("""\
                from collections import deque

                def route(graph, start, goal):
                    prev = {start: None}
                    queue = deque([start])
                    while queue:
                        v = queue.popleft()
                        for nxt in graph[v]:
                            if nxt not in prev:
                                prev[nxt] = v
                                queue.append(nxt)
                    path = []
                    while goal is not None:
                        path.append(goal)
                        goal = prev[goal]
                    return path[::-1]

                g = {1: [2, 3], 2: [4], 3: [4],
                     4: [5], 5: []}
                print(route(g, 1, 5))""",
                "Словарь prev помнит, откуда пришли, — по нему путь собирают назад")],
              [pitfall("Без проверки «уже посещена» обход в графе с циклом ходит по кругу и не заканчивается.",
                       bad="queue.append(nxt)",
                       good='''
                           if nxt not in dist:
                               dist[nxt] = dist[v] + 1
                               queue.append(nxt)'''),
               pitfall("pop(0) у списка — O(n) на каждом шаге обхода; у deque popleft — O(1).",
                       bad="v = queue.pop(0)", good="v = queue.popleft()"),
               pitfall("Снимать вершины с конца — это уже обход в глубину: кратчайший путь не гарантирован.",
                       bad="v = queue.pop()", good="v = queue.popleft()")]),
        topic("algo_window", "Окно и два указателя",
              "Скользящее окно и два указателя решают задачи о подряд идущих элементах и парах за один проход.",
              """
              Лучшая выручка за три дня подряд, пара товаров на заданную сумму — наивное решение перебирает все отрезки или все пары. Это O(n·k) или O(n²). Два приёма сводят такие задачи к одному проходу O(n).

              ## Скользящее окно

              Окно — k подряд идущих элементов. При сдвиге на один шаг сумму не пересчитывают заново:

              ```syntax
              окно += данные[i] - данные[i - k]
              ```

              Новый элемент входит справа, старый уходит слева, и каждая следующая сумма считается за O(1). Первое окно считают целиком: {`sum(данные[:k])`}.

              ## Два указателя

              Указатели стоят на краях **отсортированного** списка и идут навстречу:

              1. Если сумма пары меньше нужной — левый сдвигают вправо: сумма вырастет.
              2. Если больше — правый сдвигают влево: сумма уменьшится.
              3. Если равна — пара найдена.

              Каждый шаг сдвигает один указатель, поэтому они встретятся не больше чем за n шагов. Тот же приём проверяет строку на палиндром: края сравнивают и сдвигают к середине.

              ## Что выбрать

              - Подряд идущие элементы фиксированной длины — окно.
              - Пара в отсортированном списке — два указателя.
              - Пара в несортированном — один проход с [[set_basics|множеством]] увиденных чисел: тоже O(n), но нужна память.
              """,
              [("""\
                temps = [12, 15, 11, 18, 20, 9]
                k = 3
                window = sum(temps[:k])
                best = window
                for i in range(k, len(temps)):
                    window += temps[i] - temps[i - k]
                    best = max(best, window)
                print(best)""",
                "Самые тёплые три дня подряд — сумма за один проход"),
               ("""\
                def is_pal(s):
                    lo, hi = 0, len(s) - 1
                    while lo < hi:
                        if s[lo] != s[hi]:
                            return False
                        lo += 1
                        hi -= 1
                    return True

                print(is_pal("шалаш"))
                print(is_pal("шалун"))""",
                "Указатели идут навстречу и сравнивают края строки"),
               ("""\
                prices = [2, 5, 7, 11, 15]
                budget = 18
                lo, hi = 0, len(prices) - 1
                while lo < hi:
                    s = prices[lo] + prices[hi]
                    if s == budget:
                        print(prices[lo], prices[hi])
                        break
                    if s < budget:
                        lo += 1
                    else:
                        hi -= 1""",
                "Пара на сумму 18 найдена без перебора всех пар")],
              [pitfall("Сумма окна срезом на каждом шаге — снова O(n·k): срез и sum проходят всё окно.",
                       bad="best = max(best, sum(a[i:i + k]))",
                       good='''
                           window += a[i] - a[i - k]
                           best = max(best, window)'''),
               pitfall("На неотсортированном списке два указателя пропускают пары: сначала отсортируйте.",
                       bad="lo, hi = 0, len(a) - 1",
                       good='''
                           a = sorted(a)
                           lo, hi = 0, len(a) - 1'''),
               "Ошибиться на единицу в границах и потерять последнее окно: проверьте код на списке из 3–4 чисел вручную."]),
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
            prompt="Нужна наибольшая сумма k подряд идущих чисел: 9 и 8. Найдите строку с ошибкой", topic="algo_window",
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
                ["(4, 6, 3)", "(1, 8, 2)", "None"], position=3, topic="algo_window", role="practice", difficulty=3,
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
                 "{'A': 0, 'B': 1, 'C': 1, 'D': 2, 'E': 2, 'F': 4}"], position=0, topic="algo_bfs",
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
              "`match` сравнивает значение с шаблонами по очереди и сразу достаёт из подходящего нужные части.",
              """
              Команды игрока, ответы сервера, события интерфейса — данные разной формы: надо понять, что это за случай, и вытащить поля. Цепочка `if` с `len()` и [[inh_poly|`isinstance`]] здесь громоздкая. `match` делает то же короче (с Python 3.10).

              ## Как записать

              ```syntax
              match значение:
                  case шаблон:
                      действия
                  case другой_шаблон if условие:
                      другие_действия
                  case _:
                      действия_иначе
              ```

              Шаблоны проверяются сверху вниз, срабатывает первый подходящий — не больше одного. Если не подошёл ни один, ничего не происходит, ошибки нет. `case _` ловит всё остальное.

              ## Виды шаблонов

              - `case 0:`, `case "stop":` — литерал, сравнение на равенство
              - `case 200 | 204:` — любой из вариантов
              - `case [x, y]:` — последовательность ровно из двух элементов
              - `case ["go", *rest]:` — первый элемент `"go"`, остальные в `rest`
              - `case {"type": "click", "x": x}:` — словарь с такими ключами
              - `case Point(x=0, y=y):` — объект класса с такими атрибутами
              - `case str():` — проверка типа

              Имена внутри шаблона (`x`, `rest`, `y`) получают значения из данных.

              ## Словари, строки, классы

              Словарный шаблон не мешает лишним ключам. Строка не подходит под шаблон последовательности `[a, b]`, хотя её можно перебирать. Позиционный шаблон `case Point(0, y)` работает, если у класса есть `__match_args__`; у [[dc_basics|dataclass]] он создаётся сам.

              ## Захват или сравнение

              Голое имя в `case` — это захват: `case RED:` поймает любое значение и запишет его в `RED`. Python не даст поставить такой `case` не последним — `SyntaxError`. Для сравнения с константой нужно имя с точкой: `case Color.RED:`, например из [[dc_enum|Enum]].
              """,
              [("""\
                def http(code):
                    match code:
                        case 200:
                            return "OK"
                        case 404:
                            return "не найдено"
                        case 500 | 502 | 503:
                            return "ошибка сервера"
                        case _:
                            return "другое"

                print(http(404))
                print(http(502))
                print(http(301))""",
                "Литералы, варианты через | и case _ для всего прочего"),
               ("""\
                def run(cmd):
                    match cmd.split():
                        case ["move", x, y]:
                            return f"идём в {x},{y}"
                        case ["say", *words]:
                            return " ".join(words)
                        case ["quit"]:
                            return "выход"
                        case _:
                            return "не понял"

                print(run("move 3 4"))
                print(run("say всем привет"))
                print(run("jump"))""",
                "Шаблон проверяет число слов и раскладывает их по именам"),
               ("""\
                def handle(ev):
                    match ev:
                        case {"kind": "tap", "x": x} if x < 0:
                            return "тап за экраном"
                        case {"kind": "tap", "x": x}:
                            return f"тап в {x}"
                        case {"kind": k}:
                            return f"событие {k}"

                print(handle({"kind": "tap", "x": 5}))
                print(handle({"kind": "tap", "x": -1}))
                print(handle({"kind": "key", "k": "q"}))""",
                "Условие if уточняет шаблон, лишний ключ k не мешает")],
              [pitfall("case RED: не сравнивает с переменной RED, а захватывает любое значение; case после него — SyntaxError.",
                       bad='''
                           match color:
                               case RED:
                                   stop()''',
                       good='''
                           match color:
                               case Color.RED:
                                   stop()'''),
               "Ждать «проваливания» в следующий case, как в switch других языков: срабатывает только первый подходящий.",
               pitfall("Строка не подходит под шаблон последовательности: для разбора по символам сделайте список.",
                       bad='''
                           match word:
                               case [first, second]:
                                   print(first)''',
                       good='''
                           match list(word):
                               case [first, second]:
                                   print(first)''')]),
        topic("idiom_walrus", "Моржовый оператор :=",
              "Оператор `:=` присваивает значение прямо внутри выражения, чтобы не вычислять его дважды.",
              """
              Часто значение нужно и проверить, и использовать: длину списка, строку из ввода, результат поиска. Без `:=` его либо вычисляют дважды, либо заводят переменную строкой выше. Оператор появился в Python 3.8, а «моржовым» его прозвали за вид.

              ## Как записать

              ```syntax
              if (имя := выражение) > граница:
                  действия_с_именем
              ```

              `:=` вычисляет выражение, связывает результат с именем и возвращает его. Дальше это значение участвует в сравнении, а имя доступно и после.

              ## Где пригодится

              - `while (line := input()) != "end":` — читать, пока не встретится стоп-слово
              - `if (m := re.search(шаблон, текст)):` — найти и сразу использовать ([[data_re|регулярные выражения]])
              - `[y for x in data if (y := f(x)) > 0]` — не вызывать `f` дважды ([[comp_cond|включение с условием]])

              ## Скобки решают

              `:=` связывает слабее сравнения. `if n := len(data) > 3:` присвоит `n` результат сравнения, то есть `True`, а не длину. Поэтому присваивание берут в скобки: `(n := len(data)) > 3`.

              Обычное `=` внутри выражения — `SyntaxError`. И наоборот, `:=` не заменяет обычное присваивание: строка `x := 5` без скобок — тоже `SyntaxError`.

              ## Подпись значения в f-строке

              Похожий по виду, но другой приём: `=` в конце выражения [[str_fstring|f-строки]] печатает и само выражение, и его значение. `f"{hp=}"` даст `hp=50`. Текст выражения выводится как написан, вместе с пробелами. Удобно для отладочной печати.
              """,
              [("""\
                data = [4, 8, 15, 16, 23]
                if (n := len(data)) > 3:
                    print("элементов:", n)""",
                "Длина вычислена один раз и использована дважды"),
               ("""\
                stock = ["молоко", "хлеб", "стоп"]
                while (item := stock.pop(0)) != "стоп":
                    print("беру", item)
                print("осталось:", stock)""",
                "Цикл берёт элемент и сразу проверяет его на стоп-слово"),
               ("""\
                prices = [120, 80, 300]
                taxed = [t for p in prices
                         if (t := p * 1.2) > 100]
                print(taxed)""",
                "p * 1.2 посчитано один раз — и для условия, и для списка"),
               ("""\
                hp, dmg = 50, 12
                print(f"{hp - dmg = }")
                print(f"{dmg=}")""",
                "Знак = в f-строке печатает и выражение, и значение")],
              [pitfall("Внутри условия = недопустим: SyntaxError: invalid syntax. Maybe you meant '==' or ':=' instead of '='?",
                       bad="if n = len(data):\n    print(n)",
                       good="if (n := len(data)):\n    print(n)", syntax_error=True),
               pitfall("Без скобок в n попадает результат сравнения True, а не длина.",
                       bad="if n := len(data) > 3:\n    print(n)",
                       good="if (n := len(data)) > 3:\n    print(n)"),
               pitfall("Отдельной строкой := без скобок не пишут: SyntaxError. Для обычного присваивания есть =.",
                       bad="x := 5", good="x = 5", syntax_error=True)]),
        topic("idiom_unpack", "Распаковка со звёздочкой",
              "Звёздочка при распаковке собирает «все остальные» элементы в список: `first, *rest = items`.",
              """
              Из строки таблицы нужен первый столбец и все прочие, из пути — папки и имя файла, из рейтинга — победитель и остальные. Индексы и срезы это умеют, но распаковка короче и сразу даёт понятные имена.

              ## Как записать

              ```syntax
              первый, *остальные = последовательность
              *начало, последний = последовательность
              первый, *середина, последний = последовательность
              ```

              Обычная распаковка `a, b = пара` требует точного числа элементов — это [[var_multi|присваивание нескольких имён]]. Звёздочка снимает это ограничение.

              ## Как это работает

              - Имя со звёздочкой всегда получает **список**, даже если справа кортеж или строка.
              - Если «лишних» элементов нет, получается пустой список.
              - Звёздочка в распаковке может быть только одна.
              - Имён без звёздочки должно хватить: `a, *b, c = [1]` — `ValueError`.

              ## В цикле и в функциях

              Распаковка работает и в заголовке `for`: `for name, *marks in rows:`. Звёздочка в параметрах функции — другой механизм, он собирает аргументы: [[args_star|`*args`]]. А `f(*items)` при вызове, наоборот, раскладывает список по аргументам — [[args_unpack|распаковка аргументов]].
              """,
              [("""\
                winner, *others = ["Ада", "Боб", "Ева"]
                print(winner)
                print(others)""",
                "Первый — в winner, все остальные — списком в others"),
               ("""\
                path = "home/ada/notes.txt"
                *folders, file = path.split("/")
                print(folders)
                print(file)""",
                "Звёздочка в начале: последний элемент отдельно"),
               ("""\
                rows = [("Ада", 5, 4, 5),
                        ("Боб", 3, 4)]
                for name, *marks in rows:
                    avg = sum(marks) / len(marks)
                    print(name, round(avg, 1))""",
                "Имя отдельно, оценки любой длины — списком"),
               ("""\
                first, *mid, last = "ок"
                print(first, last)
                print(mid)""",
                "Лишних элементов нет — mid получает пустой список")],
              [pitfall("Две звёздочки в одной распаковке: SyntaxError: multiple starred expressions in assignment.",
                       bad="*head, *tail = items", good="head, *tail = items", syntax_error=True),
               pitfall("Обычных имён больше, чем элементов: ValueError: not enough values to unpack.",
                       bad="a, *b, c = [1]", good="a, *b = [1]"),
               "Ждать кортеж от *rest, если справа кортеж: имя со звёздочкой всегда получает список."]),
        topic("idiom_eafp", "EAFP и питоничный код",
              "EAFP — стиль «сначала сделать, потом обработать ошибку» вместо проверки всех условий заранее.",
              """
              Прочитать ключ, которого может не быть, превратить в число строку от пользователя, открыть файл, который могли удалить. Такие действия либо проверяют заранее, либо пробуют и обрабатывают неудачу. В Python чаще выбирают второй путь.

              ## Два стиля

              - LBYL (look before you leap, «смотри, прежде чем прыгать») — проверить всё через `if`, потом действовать.
              - EAFP (easier to ask forgiveness than permission, «проще попросить прощения, чем разрешения») — сразу действовать и перехватить ошибку через [[exc_try|try / except]].

              ## Почему EAFP

              Проверка и действие — два шага, и между ними мир может измениться: файл удалят сразу после проверки. Кроме того, проверка часто повторяет работу самого действия: чтобы узнать, число ли в строке, её всё равно надо разобрать.

              Перехватывайте только ожидаемое исключение — `KeyError`, `ValueError`, — а не все подряд. Иначе спрячутся и настоящие ошибки в коде.

              ## Готовые инструменты

              - `d.get(k, 0)` — значение или запасное, без `KeyError`
              - `d.setdefault(k, [])` — значение, а если ключа нет — сначала записать
              - `enumerate(items)` вместо `range(len(items))`
              - `any(...)`, `all(...)` вместо флага `found`
              - `sum`, `max(key=...)`, [[std_collections|`Counter`]] вместо ручного подсчёта

              Идеи стиля собраны в «Дзене Python» — его печатает `import this`: «Явное лучше неявного», «Простое лучше сложного».
              """,
              [("""\
                stock = {"чай": 3}

                if "кофе" in stock:
                    print(stock["кофе"])
                else:
                    print("нет")

                try:
                    print(stock["кофе"])
                except KeyError:
                    print("нет")""",
                "Один результат двумя стилями: проверка заранее и перехват"),
               ("""\
                def to_int(text):
                    try:
                        return int(text)
                    except ValueError:
                        return None

                print(to_int("42"))
                print(to_int("4.2"))
                print(to_int("-7"))""",
                "Проверить строку заранее сложно — проще попробовать int"),
               ("""\
                scores = {"Ада": 90, "Боб": 72}
                print(scores.get("Ева", 0))

                groups = {}
                groups.setdefault("A", []).append("Ада")
                print(groups)

                print(any(s > 85 for s in scores.values()))""",
                "get, setdefault и any заменяют проверки и флаги"),
               ("""\
                songs = ["Intro", "Hit", "Outro"]
                for i, song in enumerate(songs, 1):
                    print(i, song)""",
                "Номер и элемент сразу — без range(len(...))")],
              [pitfall("Голый except прячет все ошибки, даже опечатки в имени. Ловите конкретное исключение.",
                       bad='''
                           try:
                               port = int(cfg["port"])
                           except:
                               port = 8000''',
                       good='''
                           try:
                               port = int(cfg["port"])
                           except (KeyError, ValueError):
                               port = 8000'''),
               pitfall("Индекс через range(len(...)) там, где нужны номер и элемент: это делает enumerate.",
                       bad='''
                           for i in range(len(items)):
                               print(i, items[i])''',
                       good='''
                           for i, item in enumerate(items):
                               print(i, item)'''),
               pitfall("Между проверкой и чтением файл могут удалить, и чтение всё равно упадёт с FileNotFoundError.",
                       bad='''
                           if path.exists():
                               text = path.read_text()''',
                       good='''
                           try:
                               text = path.read_text()
                           except FileNotFoundError:
                               text = ""''')]),
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
              topic="idiom_unpack", hint="*имя собирает все «лишние» элементы в список — даже если их нет.",
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
    id="testing", title="Тестирование и отладка", description="assert, unittest, mock, logging, pdb", icon="🧪",
    topics=[
        topic("test_assert", "assert и тесты-функции",
              "`assert` проверяет условие и падает с AssertionError, если оно ложно; на этом строят простые тесты.",
              """
              Тест — маленькая программа, которая вызывает ваш код и сравнивает результат с ожидаемым. Тесты запускают после каждой правки, и сломанное место находится сразу, а не у пользователя.

              ## Как записать

              ```syntax
              assert условие, "сообщение"
              ```

              Если условие истинно, ничего не происходит. Если ложно — выбрасывается [[exc_try|исключение]] `AssertionError` с этим сообщением. Сообщение необязательно.

              ## Тест — функция с assert

              - Тест — функция с именем `test_…`: внутри вызов кода и `assert`.
              - Один тест — один сценарий.
              - Проверяют и крайние случаи: пустой ввод, ноль, отрицательные числа, повторы.

              pytest — сторонний пакет (`pip install pytest`) — сам находит такие функции и показывает, где проверка не сошлась. Встроенные в Python инструменты — [[test_unittest|unittest]] и doctest.

              ## doctest: примеры в docstring

              doctest находит в [[func_def|docstring]] строки с `>>>`, выполняет их и сравнивает вывод с текстом под ними буквально. Так примеры в документации не устаревают. Запуск: `python -m doctest файл.py`.

              ## Дробные числа

              `0.1 + 0.2 == 0.3` даёт `False` из-за двоичной записи дробей. Поэтому дроби сравнивают с допуском: `math.isclose(a, b)`.

              ## Где assert не нужен

              С флагом `python -O` все `assert` отключаются. Поэтому ввод пользователя проверяют через `if` и [[exc_raise|`raise ValueError`]], а `assert` оставляют для тестов и внутренних проверок.
              """,
              [("""\
                def clamp(x, lo, hi):
                    return max(lo, min(x, hi))

                def test_clamp():
                    assert clamp(5, 0, 10) == 5
                    assert clamp(-3, 0, 10) == 0
                    assert clamp(99, 0, 10) == 10

                test_clamp()
                print("тесты прошли")""",
                "Все условия истинны — assert молчит"),
               ("""\
                def discount(price):
                    return price * 0.9

                try:
                    assert discount(100) == 80, "ждали 80"
                except AssertionError as e:
                    print("упал:", e)""",
                "Ложное условие — AssertionError с вашим сообщением"),
               ("""\
                import doctest

                def double(n):
                    \"\"\"Удваивает число.

                    >>> double(4)
                    8
                    >>> double(-1)
                    -2
                    \"\"\"
                    return n * 2

                doctest.run_docstring_examples(
                    double, globals())
                print("примеры сошлись")""",
                "doctest молчит, когда вывод совпал с текстом под >>>"),
               ("""\
                import math

                total = 0.1 + 0.2
                print(total == 0.3)
                print(math.isclose(total, 0.3))""",
                "Дроби сравнивают с допуском, а не через ==")],
              [pitfall("Скобки превращают проверку в кортеж, а он всегда истинен: SyntaxWarning: assertion is always true.",
                       bad='assert (x > 0, "x должен быть > 0")',
                       good='assert x > 0, "x должен быть > 0"'),
               pitfall("С python -O assert отключается, и неверный ввод пройдёт дальше.",
                       bad="assert age >= 0",
                       good='''
                           if age < 0:
                               raise ValueError("возраст < 0")'''),
               pitfall("Тест без assert «проходит» всегда, даже если код сломан.",
                       bad='''
                           def test_total():
                               total([1, 2])''',
                       good='''
                           def test_total():
                               assert total([1, 2]) == 3'''),
               pitfall("Дроби через ==: 0.1 * 3 == 0.3 даёт False, и тест падает на верном коде.",
                       bad="assert price * 3 == 0.3",
                       good="assert math.isclose(price * 3, 0.3)")]),
        topic("test_unittest", "unittest и mock",
              "`unittest` — встроенный фреймворк тестов на классах, а `unittest.mock` подменяет то, что в тесте вызывать нельзя.",
              """
              Когда тестов десятки, нужны общая подготовка данных, понятный отчёт и запуск одной командой. Всё это есть в стандартной библиотеке — модуль `unittest`, устанавливать ничего не нужно.

              ## Как записать

              ```syntax
              import unittest

              class TestЧто(unittest.TestCase):
                  def setUp(self):
                      подготовка_данных
                  def test_случай(self):
                      self.assertEqual(результат, ожидание)
              ```

              - Класс наследует `TestCase` — это [[inh_basics|наследование]].
              - Каждый метод `test_…` — отдельный тест.
              - `setUp` выполняется перед каждым тестом, поэтому тесты не мешают друг другу.
              - Запуск: `python -m unittest` в папке проекта. pytest тоже умеет запускать такие тесты.

              ## Проверки

              | Метод | Проверяет |
              |---|---|
              | {`assertEqual(a, b)`} | {`a == b`} |
              | {`assertTrue(x)`} | {`x`} истинно |
              | {`assertIn(x, c)`} | {`x in c`} |
              | {`assertAlmostEqual(a, b)`} | равенство дробей |
              | {`assertRaises(Ошибка)`} | код бросает ошибку |

              `assertRaises` пишут блоком: `with self.assertRaises(ValueError):` — ошибка должна случиться внутри. В отчёте failure — проверка не сошлась, error — тест упал с неожиданным исключением.

              ## Заглушки: Mock и patch

              Код, который отправляет письма или ходит в сеть, в тесте по-настоящему запускать нельзя. `Mock()` — объект-заглушка: принимает любые вызовы и запоминает их.

              - `m.send.call_count` — сколько раз вызывали `send`
              - `m.send.call_args.args` — аргументы последнего вызова
              - `Mock(return_value=5)` — что вернёт вызов заглушки

              `with patch("модуль.имя", return_value=...):` временно подменяет функцию там, где её ищут при вызове, и возвращает настоящую после блока.
              """,
              [("""\
                import unittest

                class TestCart(unittest.TestCase):
                    def setUp(self):
                        self.cart = ["чай", "сыр"]

                    def test_size(self):
                        self.assertEqual(len(self.cart), 2)

                    def test_tea(self):
                        self.assertIn("чай", self.cart)

                loader = unittest.defaultTestLoader
                suite = loader.loadTestsFromTestCase(TestCart)
                result = unittest.TestResult()
                suite.run(result)
                print(result.testsRun)
                print(result.wasSuccessful())""",
                "Оба теста прошли; в проекте их запускает python -m unittest"),
               ("""\
                import unittest

                class T(unittest.TestCase):
                    def test_fail(self):
                        self.assertEqual(2 + 2, 5)

                    def test_error(self):
                        {}["нет"]

                    def test_raises(self):
                        with self.assertRaises(KeyError):
                            {}["нет"]

                loader = unittest.defaultTestLoader
                result = unittest.TestResult()
                loader.loadTestsFromTestCase(T).run(result)
                print(len(result.failures))
                print(len(result.errors))""",
                "Не сошлась проверка — failure, неожиданное исключение — error"),
               ("""\
                from unittest.mock import Mock

                def checkout(cart, mailer):
                    mailer.send("ada@x.ru", len(cart))
                    return "оплачено"

                mailer = Mock()
                print(checkout(["чай"], mailer))
                print(mailer.send.call_count)
                print(mailer.send.call_args.args)""",
                "Письмо не ушло: Mock только записал вызов и аргументы"),
               ("""\
                import time
                from unittest.mock import patch

                def stamp():
                    return int(time.time()) % 100

                with patch("time.time", return_value=1234.5):
                    print(stamp())""",
                "Внутри with time.time возвращает заданное число")],
              [pitfall("Метод без префикса test_ не запускается: тест молча пропущен.",
                       bad="def check_total(self): ...", good="def test_total(self): ..."),
               pitfall("Общий список на уровне класса копит изменения всех тестов. Готовьте данные в setUp.",
                       bad='''
                           class TestCart(unittest.TestCase):
                               cart = []''',
                       good='''
                           class TestCart(unittest.TestCase):
                               def setUp(self):
                                   self.cart = []'''),
               pitfall("Модуль shop сделал from random import randint — подменять надо имя в shop, а не в random.",
                       bad='patch("random.randint", return_value=6)',
                       good='patch("shop.randint", return_value=6)')]),
        topic("test_logging", "logging вместо print",
              "`logging` пишет сообщения с уровнем важности, и лишние уровни выключаются одной настройкой, без правки кода.",
              """
              Отладочные `print` приходится то добавлять, то удалять, и они смешиваются с выводом программы. Модуль `logging` разделяет результат и диагностику: сообщения остаются в коде, а показывать ли их, решает одна настройка.

              ## Уровни важности

              1. `DEBUG` — подробности для отладки
              2. `INFO` — обычные события: старт, сохранение
              3. `WARNING` — что-то странное, но работа идёт
              4. `ERROR` — операция не удалась
              5. `CRITICAL` — программа не может продолжать

              Показываются сообщения от заданного уровня и выше. По умолчанию это `WARNING`, а пишутся сообщения в stderr — отдельно от обычного вывода.

              ## Как записать

              ```syntax
              import logging

              logging.basicConfig(level=logging.INFO)
              log = logging.getLogger("имя")
              log.info("текст")
              ```

              `basicConfig` вызывают один раз в начале программы. `getLogger` даёт именованный логгер — его имя видно в сообщении.

              ## Формат и трассировка

              Параметр `format` задаёт вид строки:

              - `%(levelname)s` — уровень
              - `%(name)s` — имя логгера
              - `%(message)s` — текст
              - `%(asctime)s` — дата и время

              `log.exception("текст")` внутри `except` пишет сообщение уровня `ERROR` вместе с трассировкой ошибки.

              В примерах `stream=sys.stdout` направляет сообщения в обычный вывод, а `force=True` позволяет настроить logging заново.
              """,
              [("""\
                import logging
                import sys

                logging.basicConfig(
                    stream=sys.stdout,
                    level=logging.INFO,
                    force=True,
                )
                log = logging.getLogger("app")
                log.debug("не видно")
                log.info("старт")
                log.warning("мало места")""",
                "DEBUG ниже порога INFO; формат по умолчанию — УРОВЕНЬ:имя:текст"),
               ("""\
                import logging
                import sys

                logging.basicConfig(
                    stream=sys.stdout,
                    format="[%(levelname)s] %(message)s",
                    force=True,
                )
                logging.warning("диск заполнен")
                logging.error("файл не сохранён")""",
                "Свой формат: уровень в скобках и текст"),
               ("""\
                import logging
                import sys

                logging.basicConfig(stream=sys.stdout,
                                    force=True)
                try:
                    int("12a")
                except ValueError as e:
                    logging.error("ввод: %s", e)""",
                "Аргумент подставлен на место %s при записи сообщения")],
              [pitfall("Отладочный print попадает в вывод программы; logging.debug выключается уровнем.",
                       bad='print("отладка:", data)',
                       good='log.debug("данные: %s", data)'),
               pitfall("Без настройки INFO и DEBUG не видны: порог по умолчанию — WARNING.",
                       bad='logging.info("старт")',
                       good='''
                           logging.basicConfig(level=logging.INFO)
                           logging.info("старт")'''),
               pitfall("logging.info до basicConfig сам настраивает logging, и следующая basicConfig уже ничего не меняет.",
                       bad='''
                           logging.info("старт")
                           logging.basicConfig(level=logging.INFO)''',
                       good='''
                           logging.basicConfig(level=logging.INFO)
                           logging.info("старт")''')]),
        topic("test_debug", "Отладка: breakpoint() и pdb",
              "Отладка — поиск места, где значения расходятся с ожиданием: программу останавливают или печатают данные по пути.",
              """
              Программа не падает, но результат не тот. Тест показывает, что ошибка есть, а отладка — где именно. Для этого смотрят значения переменных в нужный момент.

              ## Как записать

              ```syntax
              def функция():
                  действия
                  breakpoint()
                  другие_действия
              ```

              `breakpoint()` останавливает программу на этой строке и открывает отладчик `pdb`. Дальше команды вводят с клавиатуры. В приложении ввода во время работы нет, поэтому отладчик здесь не запустится: пользуйтесь им на компьютере.

              ## Команды pdb

              | Команда | Что делает |
              |---|---|
              | {`n`} | следующая строка |
              | {`s`} | войти в вызов функции |
              | {`c`} | продолжить до остановки |
              | {`p выражение`} | показать значение |
              | {`l`} | код вокруг строки |
              | {`w`} | цепочка вызовов |
              | {`q`} | выйти |

              Всю программу под отладчиком запускают так: `python -m pdb файл.py`. Переменная окружения `PYTHONBREAKPOINT=0` отключает все `breakpoint()` разом.

              ## Без отладчика

              - `print(f"{x=}")` — имя и точное значение одной строкой
              - `assert условие` — падает там, где предположение нарушено
              - `traceback.print_exc()` в `except` — [[exc_traceback|трассировка]] без остановки
              - [[test_logging|`logging.debug`]] — сообщения, которые выключаются уровнем

              ## __debug__ и флаг -O

              При обычном запуске `__debug__` равно `True`. С флагом `python -O` оно становится `False`, а все `assert` и блоки `if __debug__:` пропускаются. Поэтому внутри `assert` не пишут действия, которые должны выполниться.
              """,
              [("""\
                def average(marks):
                    total = sum(marks)
                    print(f"{total=} {len(marks)=}")
                    return total // len(marks)

                print(average([4, 5, 5]))""",
                "Отладочный print показал данные: виновато // вместо /"),
               ("""\
                def discount(price, pct):
                    assert 0 <= pct <= 100, f"{pct=}"
                    return price * (100 - pct) / 100

                print(__debug__)
                print(discount(200, 15))
                try:
                    discount(200, 150)
                except AssertionError as e:
                    print("неверно:", e)""",
                "assert поймал неверный процент там, где он появился"),
               ("""\
                import sys
                import traceback

                def parse(line):
                    return int(line.split(";")[1])

                for line in ["чай;2", "сыр;x", "хлеб;1"]:
                    try:
                        print(parse(line))
                    except ValueError:
                        traceback.print_exc(file=sys.stdout)""",
                "Трассировка напечатана, а цикл дошёл до третьей строки"),
               ("""\
                import sys

                def show(*args, **kwargs):
                    caller = sys._getframe(1)
                    print("стоп, строка", caller.f_lineno)
                    print(caller.f_locals)

                sys.breakpointhook = show

                def total(prices):
                    s = sum(prices)
                    breakpoint()
                    return s

                print(total([3, 4]))""",
                "breakpoint() вызвал свою функцию вместо pdb: строка и переменные")],
              [pitfall("Забытый `breakpoint()` останавливает программу и ждёт команд: на сервере она просто зависнет.",
                       bad='''
                           breakpoint()
                           save(order)''',
                       good="save(order)"),
               pitfall("С `python -O` выражение в `assert` не вычисляется вовсе, и `pop` не случится.",
                       bad="assert items.pop() == last",
                       good='''
                           item = items.pop()
                           assert item == last'''),
               pitfall("Пустой `except` прячет ошибку, и отлаживать нечего. Напечатайте трассировку.",
                       bad='''
                           try:
                               qty = int(raw)
                           except ValueError:
                               pass''',
                       good='''
                           try:
                               qty = int(raw)
                           except ValueError:
                               traceback.print_exc()'''),
               pitfall("`print` не показывает пробелы по краям и кавычки: `\"5 \"` и `5` выглядят одинаково.",
                       bad="print(value)", good='print(f"{value=}")')]),
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
        predict("py_test_012", "Отладочная печать", """\
                raw = ["3", " 4", "5 "]
                nums = [x.strip() for x in raw]
                print(f"{raw[1]=}")
                print(f"{nums=}")
                print(sum(map(int, nums)))""",
                ["raw[1]=4\nnums=['3', '4', '5']\n12", "raw[1]=' 4'\nnums=[3, 4, 5]\n12",
                 "' 4'\n['3', '4', '5']\n12"], position=1, topic="test_debug",
                hint="Знак = в конце поля f-строки печатает само выражение и repr его значения.",
                explanation="f\"{выражение=}\" выводит текст выражения, знак = и значение через repr: строка — в кавычках, пробел виден. strip убрал пробелы, но элементы остались строками, а сумму считает int.",
                feedback={"raw[1]=4\nnums=['3', '4', '5']\n12": "Значение показывается через repr: строка в кавычках, и пробел перед 4 виден.",
                          "raw[1]=' 4'\nnums=[3, 4, 5]\n12": "strip возвращает строки, числами они становятся только внутри sum(map(int, ...)).",
                          "' 4'\n['3', '4', '5']\n12": "С = в конце поля печатается и само выражение: raw[1]=."}),
        categorize("py_test_013", "Команды pdb", "Разложите команды отладчика pdb по назначению",
                   ["Продвинуть выполнение", "Показать состояние", "Точки остановки"],
                   [("n", 0, "next — выполнить строку целиком и встать на следующей."),
                    ("s", 0, "step — войти внутрь вызываемой функции."),
                    ("c", 0, "continue — работать до следующей остановки."),
                    ("p total", 1), ("l", 1, "list — показать код вокруг текущей строки."),
                    ("w", 1, "where — цепочка вызовов, как в трассировке."),
                    ("b 12", 2, "break — поставить точку остановки на строку 12."),
                    ("cl", 2, "clear — убрать точки остановки.")],
                   code_items=True, topic="test_debug", difficulty=2,
                   hint="Команды pdb — первые буквы английских слов: next, step, continue, print, list, where, break, clear.",
                   explanation="n, s и c двигают программу дальше по-разному: строка, вход в функцию, до остановки. p, l и w ничего не выполняют, а показывают значение, код и цепочку вызовов. b ставит точку остановки, cl убирает."),
        true_false("py_test_014", "Отладка без отладчика", "Верно ли утверждение?",
                   [("traceback.format_exc() в except возвращает трассировку строкой", True),
                    ("traceback.print_exc() останавливает программу", False,
                     "Она только печатает трассировку: программа идёт дальше."),
                    ("При обычном запуске __debug__ равно True", True),
                    ("breakpoint() можно вызвать только внутри функции", False,
                     "Его вызывают в любом месте, и на уровне модуля тоже."),
                    ("f\"{x=}\" печатает имя и значение: x=5", True)],
                   check=lambda text: {
                       "traceback.format_exc() в except возвращает трассировку строкой": output_of(
                           "import traceback\ntry:\n    1 / 0\nexcept ZeroDivisionError:\n"
                           "    t = traceback.format_exc()\nprint(type(t).__name__, t.startswith('Traceback'))") == "str True\n",
                       "traceback.print_exc() останавливает программу": not output_of(
                           "import sys, traceback\ntry:\n    1 / 0\nexcept ZeroDivisionError:\n"
                           "    traceback.print_exc(file=sys.stdout)\nprint('дальше')").endswith("дальше\n"),
                       "При обычном запуске __debug__ равно True": output_of("print(__debug__)") == "True\n",
                       "breakpoint() можно вызвать только внутри функции": not runs(
                           "import sys\nsys.breakpointhook = lambda *a, **k: None\nbreakpoint()"),
                       "f\"{x=}\" печатает имя и значение: x=5": output_of("x = 5\nprint(f'{x=}')") == "x=5\n",
                   }[text],
                   topic="test_debug", difficulty=2,
                   hint="print_exc только печатает. Что делает флаг -O с __debug__, и что без него?",
                   explanation="format_exc возвращает трассировку строкой, print_exc печатает её и не прерывает программу. __debug__ равно True, пока не указан флаг -O. breakpoint() работает где угодно. {x=} печатает имя и значение."),
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
