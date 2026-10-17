"""Модули 34–37: asyncio, потоки и процессы, производительность, программа
как проект (argparse, logging, структура, PEP 8)."""
from bclib import choice, fill, match, multi, order, predict, bug, typed, topic, task, native, run


def compiles(code):
    try:
        compile(code, "main.py", "exec")
    except SyntaxError:
        return False
    return True


MODULES = []

# -------------------------------------------------------------------- async
MODULES.append(dict(
    id="async", title="Асинхронность: asyncio", description="async/await, задачи, gather, таймауты, очереди",
    icon="⏳",
    topics=[
        topic("async_basics", "Корутины и цикл событий",
              "async def создаёт корутину. Она выполняется, только когда её ждут через await или запускают asyncio.run(main()). Пока корутина ждёт (await asyncio.sleep, сеть), цикл событий выполняет другие.",
              """
              Асинхронность — способ делать много ожиданий одновременно в одном потоке: скачивать страницы, ждать базу данных, обслуживать тысячи соединений. Пока одна задача ждёт ответа, работают другие.

              async def f(): ... — объявление корутинной функции. Вызов f() ничего не выполняет: он возвращает объект-корутину. Выполнить её можно двумя способами: await f() внутри другой корутины или asyncio.run(f()) на верхнем уровне программы (обычно один раз — для main()).

              await можно писать только внутри async def. В точке await корутина отдаёт управление циклу событий, и тот запускает другие готовые задачи.

              asyncio.sleep(секунды) — неблокирующая пауза: ждёт только эта корутина. time.sleep останавливает весь поток вместе с циклом событий — в асинхронном коде его не используют. То же с любой долгой синхронной работой: тяжёлые вычисления в корутине «замораживают» все остальные.

              Асинхронность не ускоряет вычисления: она выигрывает только на ожиданиях (ввод-вывод).
              """,
              [("""\
                import asyncio

                async def greet(name):
                    await asyncio.sleep(0.01)
                    return f"привет, {name}"

                async def main():
                    text = await greet("Ада")
                    print(text)

                asyncio.run(main())""", "await ждёт результат корутины; asyncio.run запускает главную.")],
              ["Забыть await: f() без await не выполняется, Python лишь предупредит «coroutine was never awaited».",
               "Вызывать time.sleep или долгий цикл внутри корутины — это блокирует все задачи сразу.",
               "Вызывать asyncio.run изнутри уже работающей корутины — RuntimeError: внутри используют await."]),
        topic("async_tasks", "Задачи: gather, create_task, таймауты",
              "asyncio.gather запускает корутины одновременно и возвращает результаты в порядке аргументов. create_task ставит корутину в работу сразу, а await задачи ждёт её результат. wait_for и asyncio.timeout ограничивают время.",
              """
              await f(); await g() — последовательно: g начнётся только после f. Чтобы ждать одновременно, корутины превращают в задачи.

              asyncio.gather(f(), g(), h()) — ждёт все и возвращает список результатов в порядке аргументов, а не в порядке завершения. Если одна упала, исключение долетает до await gather, а остальные корутины не отменяются и продолжают работать. С return_exceptions=True исключения попадают в список результатов.

              asyncio.create_task(f()) — задача начнёт выполняться, когда текущая задача отдаст управление циклу (на await того, что реально ждёт; await корутины, которая не приостанавливается, хода не отдаёт). Результат забирают через await task, отменяют — task.cancel(). Ссылку на задачу нужно хранить, иначе её может собрать сборщик мусора.

              async with asyncio.TaskGroup() as tg: tg.create_task(...) (Python 3.11+) — современная замена gather: выход из блока ждёт все задачи, а при ошибке в одной остальные отменяются; ошибки приходят как ExceptionGroup и ловятся через except*.

              await asyncio.wait_for(f(), timeout=1) отменяет ожидаемую корутину, async with asyncio.timeout(1): (3.11+) — текущую задачу внутри блока. Внутри летит CancelledError (срабатывают finally), а наружу выходит TimeoutError.

              async with lock: — asyncio.Lock, замок для корутин. async for x in поток: — перебор асинхронного итератора. asyncio.Semaphore(n) ограничивает, сколько корутин одновременно входят в блок.

              asyncio.Queue — очередь между корутинами: await queue.put(x) и await queue.get(). С maxsize производитель ждёт, пока потребитель освободит место.
              """,
              [("""\
                import asyncio

                async def download(name, delay):
                    await asyncio.sleep(delay)
                    return name

                async def main():
                    async with asyncio.TaskGroup() as tg:
                        slow = tg.create_task(download("медленный", 0.03))
                        fast = tg.create_task(download("быстрый", 0.01))
                    print(slow.result(), fast.result())
                    try:
                        async with asyncio.timeout(0.01):
                            await download("вечный", 1)
                    except TimeoutError:
                        print("не дождались")

                asyncio.run(main())""", None)],
              ["Ждать задачи по одной в цикле for вместо gather/TaskGroup, если их можно ждать одновременно.",
               "Глотать CancelledError: с 3.8 это BaseException, и except Exception его не ловит, но except BaseException или голый except: поймают. Поймали — уберите за собой и снова raise, иначе отмена и таймауты сломаются."]),
    ],
    tasks=[
        task("t_async_gather", "Параллельная загрузка",
             "Первая строка — n, дальше n строк «имя задержка_мс». Напишите корутину fetch(name, ms): она ждёт ms миллисекунд через asyncio.sleep, печатает «готов имя» и возвращает длину имени. В main запустите все загрузки одновременно через asyncio.gather и выведите «итого: сумма_результатов». Задержки разные, поэтому «готов …» печатаются в порядке возрастания задержки.",
             solution="""\
                import asyncio

                async def fetch(name, ms):
                    await asyncio.sleep(ms / 1000)
                    print("готов", name)
                    return len(name)

                async def main():
                    n = int(input())
                    jobs = []
                    for _ in range(n):
                        name, ms = input().split()
                        jobs.append(fetch(name, int(ms)))
                    results = await asyncio.gather(*jobs)
                    print("итого:", sum(results))

                asyncio.run(main())""",
             starter="""\
                import asyncio

                async def fetch(name, ms):
                    print("готов", name)
                    return len(name)

                async def main():
                    n = int(input())
                    for _ in range(n):
                        name, ms = input().split()
                        await fetch(name, int(ms))

                asyncio.run(main())""",
             tests=["3\nкошка 30\nпёс 10\nёж 50\n", "2\nalpha 40\nbeta 20\n", "1\nсоло 10\n",
                    "4\nd 70\nc 50\nb 30\na 10\n"],
             hint="Не ждите fetch сразу: сначала соберите корутины, потом дождитесь их одним вызовом.",
             difficulty=3,
             requires=dict(defines=["fetch", "main"], uses=["async"],
                           calls_in={"main": ["gather"], "fetch": ["sleep"]})),
    ],
    levels=[
        predict("py_async_001", "Корутина ещё не работает", """\
                import asyncio

                async def hello():
                    print("привет")
                    return 5

                coro = hello()
                print(type(coro).__name__)
                print(asyncio.run(coro))""",
                ["привет\ncoroutine\n5", "function\nпривет\n5", "coroutine\n5"], position=1, topic="async_basics",
                hint="Что возвращает вызов async-функции — результат или что-то другое?",
                explanation="hello() не выполняет тело, а создаёт объект coroutine. Тело (print) работает внутри asyncio.run, который возвращает результат корутины — 5.",
                feedback={"привет\ncoroutine\n5": "Вызов hello() только создаёт корутину: «привет» напечатается в asyncio.run.",
                          "function\nпривет\n5": "Вызов async-функции возвращает объект coroutine.",
                          "coroutine\n5": "print внутри корутины выполняется — во время asyncio.run."}),
        fill("py_async_002", "Первая корутина", "Объявите корутину и дождитесь паузы",
             """\
             import asyncio

             {{0}} def main():
                 {{1}} asyncio.sleep(0.01)
                 print("готово")

             asyncio.run(main())""", ["async", "await", "return", "def"], ["async", "await"],
             topic="async_basics", hint="Вспомните, как объявляют корутину и как ждут асинхронную паузу.",
             explanation="async def объявляет корутину, await ждёт асинхронную паузу. Без async слово await — синтаксическая ошибка; return вернул бы корутину sleep, так и не дождавшись её, — «готово» не напечатается.",
             expect="готово\n"),
        predict("py_async_003", "Порядок в gather", """\
                import asyncio

                async def job(name, delay):
                    await asyncio.sleep(delay)
                    print("готов", name)
                    return name.upper()

                async def main():
                    results = await asyncio.gather(job("a", 0.03), job("b", 0.01), job("c", 0.02))
                    print(results)

                asyncio.run(main())""",
                ["готов a\nготов b\nготов c\n['A', 'B', 'C']", "готов b\nготов c\nготов a\n['B', 'C', 'A']"],
                position=1, topic="async_tasks", role="practice", difficulty=2,
                hint="Печать идёт по мере готовности. А в каком порядке gather возвращает результаты?",
                explanation="Задачи ждут одновременно, поэтому первой готова b (10 мс), затем c и a. Но gather возвращает результаты в порядке аргументов, а не завершения.",
                feedback={"готов a\nготов b\nготов c\n['A', 'B', 'C']": "Корутины ждут одновременно: первой просыпается та, у которой пауза короче.",
                          "готов b\nготов c\nготов a\n['B', 'C', 'A']": "gather сохраняет порядок аргументов, а не порядок завершения."}),
        predict("py_async_004", "Последовательно или вместе", """\
                import asyncio

                running = peak = 0

                async def fetch(n):
                    global running, peak
                    running += 1
                    peak = max(peak, running)
                    await asyncio.sleep(0.01)
                    running -= 1
                    return n

                async def one_by_one():
                    return [await fetch(1), await fetch(2), await fetch(3)]

                async def together():
                    return await asyncio.gather(fetch(1), fetch(2), fetch(3))

                for strategy in (one_by_one, together):
                    peak = 0
                    result = asyncio.run(strategy())
                    print(strategy.__name__, result, "одновременно:", peak)""",
                ["one_by_one [1, 2, 3] одновременно: 3\ntogether [1, 2, 3] одновременно: 3",
                 "one_by_one [1, 2, 3] одновременно: 1\ntogether [3, 2, 1] одновременно: 3",
                 "one_by_one [1, 2, 3] одновременно: 1\ntogether [1, 2, 3] одновременно: 1"],
                position=1, topic="async_tasks", role="practice", difficulty=2,
                hint="peak — сколько fetch ждали одновременно. Начинается ли следующий await в списке до конца предыдущего?",
                explanation="В one_by_one каждый await дожидается конца fetch, прежде чем начать следующий, — одновременно ждёт только один. gather запускает все три сразу: пик — 3. Результаты одинаковые: gather сохраняет порядок аргументов.",
                feedback={"one_by_one [1, 2, 3] одновременно: 3\ntogether [1, 2, 3] одновременно: 3": "await внутри списка выполняются по очереди: следующий fetch начинается после конца предыдущего.",
                          "one_by_one [1, 2, 3] одновременно: 1\ntogether [3, 2, 1] одновременно: 3": "gather возвращает результаты в порядке аргументов.",
                          "one_by_one [1, 2, 3] одновременно: 1\ntogether [1, 2, 3] одновременно: 1": "gather запускает корутины одновременно — все три ждут вместе."}),
        bug("py_async_005", "Заблокированный цикл", """\
            import asyncio
            import time

            async def tick(name):
                for i in range(2):
                    time.sleep(0.01)
                    print(name, i)

            async def main():
                await asyncio.gather(tick("A"), tick("B"))

            asyncio.run(main())""", {5: "        await asyncio.sleep(0.01)"},
            prompt="Задачи A и B должны чередоваться: A 0, B 0, A 1, B 1. Найдите строку с ошибкой", topic="async_basics",
            hint="Какая пауза отдаёт управление циклу событий, а какая останавливает весь поток?",
            explanation="time.sleep блокирует поток: пока A спит, цикл событий не может переключиться на B, и A выполняется целиком. await asyncio.sleep отдаёт управление — задачи чередуются.",
            difficulty=3),
        predict("py_async_006", "Когда стартует задача", """\
                import asyncio

                async def worker():
                    print("worker старт")
                    await asyncio.sleep(0)
                    print("worker конец")

                async def main():
                    task = asyncio.create_task(worker())
                    print("main: задача создана")
                    await asyncio.sleep(0)
                    print("main: после sleep(0)")
                    await task
                    print("main: конец")

                asyncio.run(main())""",
                ["worker старт\nmain: задача создана\nmain: после sleep(0)\nworker конец\nmain: конец",
                 "main: задача создана\nmain: после sleep(0)\nworker старт\nworker конец\nmain: конец",
                 "main: задача создана\nworker старт\nworker конец\nmain: после sleep(0)\nmain: конец"],
                position=3, topic="async_tasks", role="challenge", difficulty=4,
                hint="create_task не запускает корутину сразу: она стартует, когда main отдаст управление. И каждый await sleep(0) — это одна передача хода.",
                explanation="Задача ждёт первой паузы main. На sleep(0) main уступает: worker печатает «старт» и тоже уступает. main продолжает и на await task ждёт; worker заканчивает, и main завершается.",
                feedback={"worker старт\nmain: задача создана\nmain: после sleep(0)\nworker конец\nmain: конец": "create_task только планирует задачу: она начнётся, когда main отдаст управление.",
                          "main: задача создана\nmain: после sleep(0)\nworker старт\nworker конец\nmain: конец": "await asyncio.sleep(0) — это пауза: в ней успевает начаться worker.",
                          "main: задача создана\nworker старт\nworker конец\nmain: после sleep(0)\nmain: конец": "worker тоже уступает на sleep(0) — ход возвращается к main."}),
        predict("py_async_007", "Таймаут и уборка", """\
                import asyncio

                async def slow():
                    try:
                        await asyncio.sleep(1)
                        return "данные"
                    finally:
                        print("slow: уборка")

                async def main():
                    try:
                        print(await asyncio.wait_for(slow(), timeout=0.05))
                    except TimeoutError:
                        print("таймаут")

                asyncio.run(main())""",
                ["таймаут", "данные", "таймаут\nslow: уборка"], position=3, topic="async_tasks",
                role="practice", difficulty=3,
                hint="Что происходит с корутиной, которая не успела? Срабатывает ли её finally?",
                explanation="По таймауту wait_for отменяет slow: внутри неё await бросает CancelledError, finally печатает «уборка». Затем wait_for выбрасывает TimeoutError (в 3.11+ asyncio.TimeoutError — это он же).",
                feedback={"таймаут": "Отменённая корутина выполняет свой finally.",
                          "данные": "Пауза 1 с больше таймаута 0.05 с — результата не будет.",
                          "таймаут\nslow: уборка": "Уборка происходит при отмене — раньше, чем TimeoutError дойдёт до main."}),
        multi("py_async_008", "Только внутри async def", "Что можно написать только внутри async def?",
              ["await asyncio.sleep(1)", "async with lock:\n    pass", "async for item in stream:\n    pass",
               "asyncio.run(main())", "time.sleep(1)", "print(\"привет\")"], [0, 1, 2],
              check=lambda code: not compiles(code), topic="async_basics",
              hint="Ищите конструкции с ключевыми словами await и async.",
              explanation="await, async with и async for — синтаксис корутин: на верхнем уровне обычного файла .py или в обычной функции это SyntaxError (в REPL python -m asyncio и в Jupyter await на верхнем уровне разрешён). asyncio.run, наоборот, вызывают из обычного кода.",
              feedback={"asyncio.run(main())": "asyncio.run вызывают как раз из обычного кода — это вход в асинхронный мир.",
                        "time.sleep(1)": "Это обычная функция; внутри корутин её как раз избегают.",
                        "print(\"привет\")": "print работает везде."}),
        match("py_async_009", "Инструменты asyncio",
              ["asyncio.gather", "asyncio.create_task", "asyncio.wait_for", "asyncio.TaskGroup", "asyncio.Queue"],
              rights=["Ждёт несколько корутин, результаты — в порядке аргументов",
                      "Планирует корутину, не дожидаясь её",
                      "Ждёт результат не дольше заданного времени",
                      "Блок задач: при ошибке в одной остальные отменяются",
                      "Передаёт данные между корутинами"],
              prompt="Сопоставьте инструмент и его назначение", topic="async_tasks",
              hint="Начните с самого очевидного: где «очередь», где «таймаут».",
              explanation="gather собирает результаты, create_task запускает фоновую задачу, wait_for ограничивает время, TaskGroup управляет группой задач, Queue передаёт данные."),
        order("py_async_011", "Собери программу", "Расставьте строки так, чтобы программа напечатала «результат: 42»",
              ["import asyncio",
               "async def answer():",
               "    await asyncio.sleep(0.01)",
               "    return 42",
               "async def main():",
               "    print(\"результат:\", await answer())",
               "asyncio.run(main())"],
              topic="async_basics", hint="Сначала импорт и объявления, вызов asyncio.run — последним.",
              explanation="Функции объявляют до вызова asyncio.run. Порядок двух async def между собой не важен: answer нужна только при выполнении main."),
        predict("py_async_012", "Ошибки в группе задач", """\
                import asyncio

                async def job(n):
                    await asyncio.sleep(0.01 * n)
                    if n == 2:
                        raise ValueError(n)
                    return n

                async def main():
                    print(await asyncio.gather(job(1), job(2), job(3), return_exceptions=True))
                    try:
                        async with asyncio.TaskGroup() as tg:
                            for n in (1, 2, 3):
                                tg.create_task(job(n))
                    except* ValueError as group:
                        print("ошибки:", group.exceptions)

                asyncio.run(main())""",
                ["[1, 3]\nошибки: (ValueError(2),)", "ValueError: 2",
                 "[1, ValueError(2), 3]\nошибки: ValueError(2)"], position=2, topic="async_tasks",
                role="challenge", difficulty=4,
                hint="return_exceptions=True кладёт исключение в список результатов. В каком виде TaskGroup отдаёт ошибки?",
                explanation="gather с return_exceptions=True не бросает исключение, а ставит его на место результата. TaskGroup собирает ошибки задач в ExceptionGroup; except* ValueError ловит их, а group.exceptions — кортеж исключений.",
                feedback={"[1, 3]\nошибки: (ValueError(2),)": "Исключение не выбрасывается из списка — оно стоит на своём месте.",
                          "ValueError: 2": "return_exceptions=True не даёт исключению вылететь из gather, а except* ловит ошибки TaskGroup.",
                          "[1, ValueError(2), 3]\nошибки: ValueError(2)": "group.exceptions — кортеж, даже если ошибка одна."}),
        predict("py_async_013", "Явная отмена", """\
                import asyncio

                async def worker():
                    try:
                        await asyncio.sleep(1)
                    except asyncio.CancelledError:
                        print("отмена: убираю за собой")
                        raise

                async def main():
                    task = asyncio.create_task(worker())
                    await asyncio.sleep(0.01)
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        print("задача отменена:", task.cancelled())

                asyncio.run(main())""",
                ["задача отменена: True", "отмена: убираю за собой\nзадача отменена: False",
                 "отмена: убираю за собой"], position=1, topic="async_tasks", role="practice", difficulty=3,
                hint="cancel() бросает CancelledError внутрь задачи на её текущем await. Что сделает raise в except?",
                explanation="task.cancel() бросает CancelledError внутрь worker на await asyncio.sleep. worker убирает за собой и пробрасывает отмену дальше, поэтому задача считается отменённой, а await task в main выбрасывает CancelledError.",
                feedback={"задача отменена: True": "except внутри worker выполняется — он печатает про уборку.",
                          "отмена: убираю за собой\nзадача отменена: False": "raise пробросил отмену: задача отменена, cancelled() — True.",
                          "отмена: убираю за собой": "await task выбрасывает CancelledError, и main его ловит."}),
        predict("py_async_014", "Не больше двух сразу", """\
                import asyncio

                active = peak = 0

                async def fetch(sem, n):
                    global active, peak
                    async with sem:
                        active += 1
                        peak = max(peak, active)
                        await asyncio.sleep(0.01)
                        active -= 1
                    return n

                async def main():
                    sem = asyncio.Semaphore(2)
                    print(await asyncio.gather(*(fetch(sem, n) for n in range(5))), peak)

                asyncio.run(main())""",
                ["[0, 1, 2, 3, 4] 5", "[0, 1, 2, 3, 4] 1", "[0, 1] 2"], position=3, topic="async_tasks",
                role="practice", difficulty=3,
                hint="Semaphore(2) пускает в блок не больше двух корутин. Остальные ждут, но не пропадают.",
                explanation="Все пять корутин стартуют, но в async with sem одновременно находятся не больше двух — так ограничивают число параллельных запросов к серверу. Результаты — все пять, в порядке аргументов.",
                feedback={"[0, 1, 2, 3, 4] 5": "Semaphore(2) не пускает в блок больше двух корутин сразу.",
                          "[0, 1, 2, 3, 4] 1": "Две корутины ждут внутри блока одновременно.",
                          "[0, 1] 2": "Остальные корутины не отбрасываются, а ждут своей очереди."}),
        predict("py_async_010", "Босс: производитель и потребитель", """\
                import asyncio

                async def producer(queue):
                    for item in ["a", "b", "c"]:
                        await queue.put(item)
                        print("положил", item)
                    await queue.put(None)

                async def consumer(queue):
                    while (item := await queue.get()) is not None:
                        print("взял", item)

                async def main():
                    queue = asyncio.Queue(maxsize=1)
                    async with asyncio.TaskGroup() as tg:
                        tg.create_task(producer(queue))
                        tg.create_task(consumer(queue))
                    print("всё")

                asyncio.run(main())""",
                ["положил a\nположил b\nположил c\nвзял a\nвзял b\nвзял c\nвсё",
                 "положил a\nвзял a\nвзял b\nположил b\nположил c\nвзял c\nвсё",
                 "всё\nположил a\nвзял a\nположил b\nвзял b\nположил c\nвзял c"],
                position=1, topic="async_tasks", role="boss", difficulty=4,
                hint="В очереди помещается один элемент: put ждёт, пока потребитель заберёт предыдущий. И когда выполняется код после async with?",
                explanation="Очередь на один элемент: producer кладёт a, а на b ждёт. consumer забирает a, место освобождается — producer кладёт b и снова ждёт. Так они чередуются. Блок TaskGroup ждёт обе задачи, поэтому «всё» — последнее.",
                feedback={"положил a\nположил b\nположил c\nвзял a\nвзял b\nвзял c\nвсё": "maxsize=1: второй put ждёт, пока потребитель заберёт первый элемент.",
                          "положил a\nвзял a\nвзял b\nположил b\nположил c\nвзял c\nвсё": "producer печатает «положил» сразу после put — раньше, чем consumer успеет взять элемент.",
                          "всё\nположил a\nвзял a\nположил b\nвзял b\nположил c\nвзял c": "Выход из async with TaskGroup ждёт завершения всех задач."}),
    ],
))

# -------------------------------------------------------------- concurrency
PURPOSES = {
    "Скачать 50 страниц из сети": True,
    "Ждать ответы от базы данных": True,
    "Посчитать простые числа до 10 миллионов циклом на чистом Python": False,
    "Читать много файлов с медленного диска": True,
    "Перемножить большие матрицы вложенными циклами на чистом Python": False,
}

MODULES.append(dict(
    id="concurrency", title="Потоки и процессы", description="threading, Lock, очереди, пулы, GIL",
    icon="🧵",
    topics=[
        topic("conc_threads", "Потоки и GIL",
              "Поток — ещё одна линия выполнения в той же программе. Thread(target=f).start() запускает f одновременно с остальным кодом (конкурентно: с GIL байт-код потоков выполняется по очереди), join() ждёт её конца. Общие данные защищают Lock. Из-за GIL потоки ускоряют ожидание (сеть, диск), но не вычисления на чистом Python.",
              """
              threading.Thread(target=функция, args=(аргументы,)) создаёт поток, start() запускает его, join() ждёт завершения. Без join главный поток не ждёт результатов. t.is_alive() — работает ли поток, threading.active_count() — сколько потоков живо, включая главный. daemon=True — фоновый поток, который не мешает программе завершиться.

              GIL (глобальная блокировка интерпретатора) в обычном CPython позволяет выполнять байт-код только одному потоку за раз. Пока поток ждёт ввода-вывода, GIL отпускается — поэтому потоки хороши для сетевых запросов и файлов, но не ускоряют вычисления на чистом Python. (В 3.13 появилась экспериментальная сборка без GIL — free-threading; с 3.14 она официально поддерживается, но ставится отдельно, например python3.14t, и не используется по умолчанию.)

              Гонка данных: два потока читают и меняют одно значение, и обновления теряются. Решение — threading.Lock: with lock: ... пускает в блок только один поток. Lock должен быть общим для всех потоков, а не создаваться заново при каждом вызове.

              queue.Queue — потокобезопасная очередь: put/get уже защищены. task_done() и join() позволяют дождаться обработки всех элементов.

              concurrent.futures.ThreadPoolExecutor — пул потоков: pool.map(f, данные) возвращает результаты в исходном порядке, pool.submit(f, x) — объект Future, а as_completed(futures) выдаёт их по мере готовности.
              """,
              [("""\
                import threading

                counter = 0
                lock = threading.Lock()

                def add(times):
                    global counter
                    for _ in range(times):
                        with lock:
                            counter += 1

                threads = [threading.Thread(target=add, args=(10_000,)) for _ in range(4)]
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()
                print(counter)""", "С общим Lock ни одно увеличение не теряется.", {"native_only": True})],
              ["Забыть join: главный поток напечатает результат раньше, чем потоки его посчитают.",
               "Создавать Lock внутри функции потока: у каждого вызова свой замок, и он ничего не защищает.",
               "Ждать ускорения вычислений от потоков в обычном CPython: GIL выполняет байт-код по очереди."]),
        topic("conc_processes", "Процессы и выбор инструмента",
              "Для вычислений на всех ядрах — процессы: ProcessPoolExecutor или multiprocessing. Для ожиданий — потоки или asyncio. Код запуска пулов процессов держат под if __name__ == \"__main__\".",
              """
              Процесс — отдельная копия интерпретатора со своей памятью и своим GIL. Поэтому процессы ускоряют вычисления на нескольких ядрах. Цена — данные передаются между процессами через сериализацию (pickle), а запуск процесса дороже потока.

              ProcessPoolExecutor имеет тот же интерфейс, что ThreadPoolExecutor: map, submit, as_completed. Функция и аргументы должны сериализоваться: lambda и функции, объявленные внутри других функций, не подойдут.

              У запущенного файла имя модуля __name__ равно "__main__", а при импорте — имени файла (подробнее — в модуле «Программа как проект»). Новые процессы на Windows и macOS (способ spawn), а с Python 3.14 и на Linux (forkserver) импортируют главный модуль заново. Без if __name__ == "__main__": дочерний процесс попытался бы снова создать пул — multiprocessing это замечает и падает с RuntimeError. Fork (Linux до 3.13) копирует процесс и модуль не импортирует, но проверку пишут всегда — ради переносимости.

              Как выбрать: много ожиданий в сети — asyncio (тысячи соединений) или потоки (проще с синхронными библиотеками); тяжёлые вычисления на чистом Python — процессы; вычисления в numpy и других C-библиотеках часто отпускают GIL и работают и в потоках.

              Во встроенном интерпретаторе приложения нет потоков и процессов — эти примеры работают в обычном Python на компьютере.
              """,
              [("""\
                from concurrent.futures import ProcessPoolExecutor

                if __name__ == "__main__":
                    with ProcessPoolExecutor(max_workers=2) as pool:
                        print(list(pool.map(pow, [2, 3, 4], [10, 2, 3])))""",
                "pow — встроенная функция, она сериализуется и выполняется в процессах пула.", {"native_only": True})],
              ["Передавать в ProcessPoolExecutor lambda — её нельзя сериализовать (PicklingError).",
               "Запускать пул процессов без if __name__ == \"__main__\" — на Windows, macOS и Linux 3.14+ дочерние процессы падают с RuntimeError."]),
    ],
    levels=[
        native(predict("py_conc_001", "Запуск и ожидание", """\
                import threading

                results = []

                def work(n):
                    results.append(n * n)

                threads = [threading.Thread(target=work, args=(n,)) for n in range(4)]
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()
                print(sorted(results), threading.active_count())""",
                ["[] 1", "[0, 1, 4, 9] 5", "[0, 1, 4, 9] 4"], position=1, topic="conc_threads",
                hint="join дожидается конца каждого потока. А сколько потоков живо после этого?",
                explanation="После join все четыре потока закончили работу: в results четыре квадрата. Живым остаётся только главный поток — active_count() равен 1.",
                feedback={"[] 1": "join ждёт завершения потоков — к print все результаты уже добавлены.",
                          "[0, 1, 4, 9] 5": "Завершённые потоки не считаются: живым остался только главный.",
                          "[0, 1, 4, 9] 4": "active_count считает и главный поток, а рабочие уже закончились."})),
        native(fill("py_conc_002", "Аргументы потока", "Передайте имя в функцию потока",
                    """\
                    import threading

                    def greet(name):
                        print("привет,", name)

                    t = threading.Thread(target=greet, {{0}}=("Ада",))
                    t.start()
                    t.join()
                    print("поток завершён:", not t.is_alive())""", ["args", "kwargs", "name", "daemon"], ["args"],
                    topic="conc_threads", hint="Позиционные аргументы для target передают кортежем.",
                    explanation="args — кортеж позиционных аргументов для target. kwargs ждёт словарь (кортеж даст TypeError ещё до вызова greet); name и daemon — настройки самого потока, а greet вызовется без аргумента и упадёт.",
                    expect="привет, Ада\nпоток завершён: True\n")),
        native(bug("py_conc_003", "Замок, который не запирает", """\
            import threading
            import time

            balance = 100
            lock = threading.Lock()

            def withdraw(amount):
                global balance
                with threading.Lock():
                    current = balance
                    time.sleep(0.1)
                    balance = current - amount

            threads = [threading.Thread(target=withdraw, args=(a,)) for a in (30, 20)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            print(balance)""", {8: "    with lock:"},
            prompt="Два снятия должны оставить 50. Найдите строку с ошибкой", topic="conc_threads",
            hint="Сколько разных замков создаётся в этой программе?",
            explanation="threading.Lock() внутри функции создаёт новый замок при каждом вызове — потоки не мешают друг другу. Оба читают 100, и одно снятие теряется. Нужен один общий lock.",
            difficulty=3)),
        native(predict("py_conc_004", "Порядок в pool.map", """\
                from concurrent.futures import ThreadPoolExecutor
                import time

                def slow_square(n):
                    time.sleep(0.05 * (3 - n))
                    return n * n

                with ThreadPoolExecutor(max_workers=3) as pool:
                    print(list(pool.map(slow_square, [0, 1, 2])))""",
                ["[4, 1, 0]", "[0, 1, 2]"], position=0, topic="conc_threads", role="practice", difficulty=2,
                hint="Быстрее всех закончится slow_square(2). Но в каком порядке map отдаёт результаты?",
                explanation="map возвращает результаты в порядке входных данных, даже если задачи закончились в другом порядке.",
                feedback={"[4, 1, 0]": "Это порядок завершения. map сохраняет порядок входных данных.",
                          "[0, 1, 2]": "map возвращает результаты функции — квадраты."})),
        native(predict("py_conc_005", "По мере готовности", """\
                from concurrent.futures import ThreadPoolExecutor, as_completed
                import time

                def job(name, delay):
                    time.sleep(delay)
                    return name

                with ThreadPoolExecutor() as pool:
                    futures = [pool.submit(job, n, d) for n, d in [("a", 0.3), ("b", 0.1), ("c", 0.2)]]
                    print([f.result() for f in as_completed(futures)])
                    print([f.result() for f in futures])""",
                ["['a', 'b', 'c']\n['a', 'b', 'c']", "['b', 'c', 'a']\n['b', 'c', 'a']"], position=1,
                topic="conc_threads", role="practice", difficulty=3,
                hint="as_completed отдаёт задачи по мере завершения. А список futures?",
                explanation="as_completed выдаёт Future в порядке готовности: b, c, a. Список futures остаётся в порядке создания.",
                feedback={"['a', 'b', 'c']\n['a', 'b', 'c']": "as_completed выдаёт задачи по мере готовности — первой b.",
                          "['b', 'c', 'a']\n['b', 'c', 'a']": "Список futures не пересортировывается: он в порядке submit."})),
        multi("py_conc_006", "Где помогут потоки", "В каких задачах потоки обычного CPython (с GIL) реально ускорят программу?",
              list(PURPOSES), [i for i, ok in enumerate(PURPOSES.values()) if ok],
              check=lambda option: PURPOSES[option], topic="conc_processes",
              hint="GIL отпускается, пока поток ждёт ввода-вывода.",
              explanation="Сеть, база данных и диск — ожидания: пока один поток ждёт, другие работают. Вычисления на чистом Python упираются в GIL — для них нужны процессы (или numpy).",
              feedback={"Посчитать простые числа до 10 миллионов циклом на чистом Python": "Это чистые вычисления: GIL выполняет байт-код по очереди. Нужны процессы.",
                        "Перемножить большие матрицы вложенными циклами на чистом Python": "Вычисления на чистом Python — нужны процессы или numpy."}),
        match("py_conc_007", "Словарь параллельности",
              ["GIL", "threading.Lock", "queue.Queue", "ThreadPoolExecutor", "ProcessPoolExecutor"],
              rights=["Блокировка внутри интерпретатора: из-за неё потоки не ускоряют вычисления на чистом Python",
                      "Ваш замок для общих данных: with lock: …",
                      "Потокобезопасная очередь задач",
                      "Пул потоков для ожиданий: сеть, файлы",
                      "Пул процессов для вычислений на всех ядрах"],
              prompt="Сопоставьте понятие и смысл", topic="conc_processes",
              hint="Где пул потоков, а где пул процессов — подскажут их имена.",
              explanation="GIL ограничивает потоки CPython, Lock защищает общие данные, Queue передаёт задачи, пулы потоков — для ожиданий, пулы процессов — для вычислений."),
        native(typed("py_conc_008", "Счёт под замком", """\
              import threading

              counter = 0
              lock = threading.Lock()

              def add():
                  global counter
                  for _ in range(5000):
                      with lock:
                          counter += 1

              threads = [threading.Thread(target=add) for _ in range(3)]
              for t in threads:
                  t.start()
              for t in threads:
                  t.join()
              print(counter, len(threads))""",
              topic="conc_threads", hint="Сколько раз выполнится counter += 1 и может ли увеличение потеряться?",
              explanation="С общим Lock каждое counter += 1 выполняется целиком: 3 × 5000 = 15000.")),
        choice("py_conc_009", "Пул процессов", "Почему запуск ProcessPoolExecutor прячут под if __name__ == \"__main__\"?",
               ["Новые процессы импортируют главный модуль, и без проверки каждый попытался бы снова запустить пул",
                "Без этой проверки процессы делят один GIL",
                "Так быстрее: проверка включает оптимизацию байт-кода",
                "ProcessPoolExecutor работает только внутри функций"], 0,
               topic="conc_processes", role="practice", difficulty=3,
               hint="Что делает новый процесс при запуске spawn (Windows, macOS, Linux 3.14+)?",
               explanation="При запуске «с нуля» (spawn, forkserver) процесс импортирует главный модуль. Код под if __name__ == \"__main__\" при импорте не выполняется; без проверки дочерний процесс снова создал бы пул, и Python остановил бы это ошибкой RuntimeError.",
               feedback={"Без этой проверки процессы делят один GIL": "У каждого процесса свой GIL — проверка здесь ни при чём.",
                         "Так быстрее: проверка включает оптимизацию байт-кода": "Проверка не влияет на скорость — она защищает от повторного запуска.",
                         "ProcessPoolExecutor работает только внутри функций": "Работает и на верхнем уровне; проверка нужна из-за повторного импорта модуля."}),
        native(predict("py_conc_010", "Босс: очередь задач", """\
                import queue
                import threading

                q = queue.Queue()
                results = []

                def worker():
                    while True:
                        item = q.get()
                        if item is None:
                            break
                        results.append(item * 10)
                        q.task_done()

                t = threading.Thread(target=worker)
                t.start()
                for i in range(3):
                    q.put(i)
                q.join()
                print(results)
                q.put(None)
                t.join()
                print(t.is_alive())""",
                ["[]\nFalse", "[0, 10, 20]\nTrue", "[20, 10, 0]\nFalse"], position=2, topic="conc_threads",
                role="boss", difficulty=4,
                hint="q.join() ждёт, пока для каждого put вызовут task_done. А что сделает None?",
                explanation="q.join() возвращается, когда все три элемента обработаны (task_done) — results уже полон, порядок FIFO. None выводит рабочего из цикла, t.join() дожидается его конца — поток больше не жив.",
                feedback={"[]\nFalse": "q.join() ждёт обработки всех элементов — к print они в results.",
                          "[0, 10, 20]\nTrue": "None завершает цикл рабочего, и t.join() ждёт его конца.",
                          "[20, 10, 0]\nFalse": "Queue — очередь FIFO: элементы выходят в порядке добавления."})),
    ],
))

# -------------------------------------------------------------- performance
SPEEDUPS = {
    "Заменить x in список на x in множество, если проверок много": True,
    "Собирать строку через \"\".join(части) вместо += в цикле": True,
    "Вынести неизменное вычисление из тела цикла": True,
    "Заменить цикл for на while": False,
    "Переписать sum(nums) ручным циклом for": False,
}

MODULES.append(dict(
    id="performance", title="Производительность", description="Замеры, кэш, память, быстрые идиомы",
    icon="🚀",
    topics=[
        topic("perf_measure", "Сначала измерь",
              "Оптимизируют то, что измерили. time.perf_counter — для разового замера, timeit — для маленьких фрагментов, cProfile — чтобы найти, какие функции тратят время.",
              """
              Интуиция о «медленных местах» часто ошибается. Порядок работы: убедиться, что программа правильная, измерить, найти узкое место, ускорить его, измерить снова.

              time.perf_counter() — самые точные часы для замеров: засекают до и после, разница — секунды.

              timeit.timeit(функция, number=N) запускает фрагмент N раз и возвращает общее время — так сглаживаются случайные колебания. В терминале: python -m timeit "выражение".

              cProfile показывает, сколько раз вызвана каждая функция и сколько времени в ней проведено: python -m cProfile -s cumtime программа.py. tracemalloc отслеживает выделения памяти.

              Главный выигрыш почти всегда даёт алгоритм (O(n) вместо O(n²)), а не мелкие приёмы.
              """,
              [("""\
                import time
                import timeit

                start = time.perf_counter()
                total = sum(range(100_000))
                elapsed = time.perf_counter() - start
                print(total, type(elapsed).__name__)

                print(timeit.timeit("sum(range(100))", number=1000) < 60)""", "Время — дробное число секунд; сами значения от запуска к запуску разные.")],
              ["Сравнивать скорость по одному запуску — шум ОС и кэшей легко перекрывает разницу.",
               "Оптимизировать код, который выполняется редко, вместо найденного профилировщиком узкого места."]),
        topic("perf_tricks", "Быстрые идиомы и память",
              "Множества и словари вместо поиска в списке, join вместо += для строк, встроенные функции вместо ручных циклов, генераторы вместо огромных списков, functools.cache для повторных вычислений, __slots__ для миллионов объектов.",
              """
              Встроенные функции (sum, max, sorted, map, any) и методы написаны на C и обычно быстрее ручного цикла на Python.

              Строки неизменяемы: s += часть в цикле может каждый раз копировать всю строку. "".join(список_частей) собирает результат за один проход.

              Генератор вместо списка не хранит все элементы сразу: sum(x * x for x in данные) работает с памятью O(1). Но генератор одноразовый.

              functools.cache и lru_cache(maxsize=N) запоминают результаты по аргументам — аргументы должны быть хешируемыми (кортеж, а не список). cache_info() показывает попадания (hits) и промахи (misses).

              __slots__ = ("x", "y") в классе убирает словарь __dict__ у каждого объекта: меньше памяти, но новые атрибуты добавлять нельзя.

              collections.Counter, deque, defaultdict, bisect, heapq — готовые быстрые структуры; не изобретайте их заново.

              sys.getsizeof(объект) — сколько байт занимает сам объект (без вложенных).
              """,
              [("""\
                from functools import cache

                @cache
                def slow_square(n):
                    print("считаю", n)
                    return n * n

                print(slow_square(4), slow_square(4), slow_square(5))
                print(slow_square.cache_info())

                parts = [str(n) for n in range(5)]
                print("-".join(parts))""", "Второй вызов с 4 не печатает «считаю»: ответ взят из кэша.")],
              ["Передавать список в функцию с @cache — TypeError: unhashable type: 'list'.",
               "Кэшировать функции с побочными эффектами (print, запись в файл): при попадании в кэш они не выполнятся.",
               "Ждать, что __slots__ уберёт __dict__, если у родителя слотов нет: словарь вернётся от родителя.",
               "Жертвовать читаемостью ради микроускорений, которых не видно в замерах."]),
    ],
    tasks=[
        task("t_perf_stairs", "Лестница с кэшем",
             "Сколькими способами можно подняться на n ступенек, шагая на 1, 2 или 3 ступеньки за раз? Для 0 ступенек способ один (стоять на месте). Напишите рекурсивную функцию ways(n) именно с декоратором @cache из functools (@functools.cache или from functools import cache). Прочитайте n (до 300) и выведите ответ.",
             solution="""\
                from functools import cache

                @cache
                def ways(n):
                    if n < 0:
                        return 0
                    if n == 0:
                        return 1
                    return ways(n - 1) + ways(n - 2) + ways(n - 3)

                print(ways(int(input())))""",
             starter="""\
                def ways(n):
                    if n < 0:
                        return 0
                    if n == 0:
                        return 1
                    return ways(n - 1) + ways(n - 2) + ways(n - 3)

                print(ways(int(input())))""",
             tests=["3\n", "4\n", "10\n", "300\n", "1\n"],
             hint="Без кэша ways(300) считается дольше жизни Вселенной. С @cache каждое n считается один раз.",
             difficulty=3,
             requires=dict(defines=["ways"], recursive=["ways"], decorated={"ways": "cache"}, forbids=["loop"])),
        task("t_perf_join", "Быстрая сборка строки",
             "Первая строка — n, дальше n слов по одному в строке. Выведите слова через «-» в обратном порядке, а на второй строке — длину получившейся строки. Соберите строку через str.join; циклы for/while не используйте — слова прочитайте включением.",
             solution="""\
                n = int(input())
                words = [input() for _ in range(n)]
                line = "-".join(reversed(words))
                print(line)
                print(len(line))""",
             starter="""\
                n = int(input())
                line = ""
                for _ in range(n):
                    line += input() + "-"
                print(line)
                print(len(line))""",
             tests=["3\nраз\nдва\nтри\n", "1\nодин\n", "4\na\nbb\nccc\ndddd\n", "2\nпривет\nмир\n"],
             hint="Соберите слова в список, разверните его, а соединитель передайте строке, у которой вызываете join.",
             difficulty=2, requires=dict(calls=["join"], forbids=["loop"])),
    ],
    levels=[
        predict("py_perf_001", "Кэш в цифрах", """\
                from functools import lru_cache

                @lru_cache(maxsize=None)
                def fib(n):
                    return n if n < 2 else fib(n - 1) + fib(n - 2)

                print(fib(30))
                info = fib.cache_info()
                print(info.misses, info.hits)""",
                ["832040\n2692537 0", "832040\n30 30", "832040\n31 30"], position=3, topic="perf_tricks",
                role="practice", difficulty=3,
                hint="Промах (miss) — первый расчёт для нового n, попадание (hit) — ответ из кэша. Какие вызовы повторяются?",
                explanation="Каждое n от 0 до 30 считается один раз — 31 промах. fib(n) сначала вызывает fib(n - 1), и тот по пути вычисляет fib(n - 2). Поэтому второй вызов, fib(n - 2), при n от 3 до 30 берётся из кэша — 28 попаданий. Экспоненциальный счёт стал линейным.",
                feedback={"832040\n2692537 0": "Это число вызовов без кэша (2·fib(31) − 1). С кэшем каждое n считается один раз.",
                          "832040\n30 30": "Значений n от 0 до 30 — 31, каждое даёт один промах.",
                          "832040\n31 30": "Попаданий меньше: проверьте, какие вызовы реально повторяются."}),
        predict("py_perf_002", "Генератор экономит память", """\
                import sys

                nums = [n for n in range(100_000)]
                lazy = (n for n in range(100_000))
                print(sys.getsizeof(lazy) < sys.getsizeof(nums))
                print(max(lazy), max(lazy, default="пусто"))""",
                ["False\n99999 99999", "True\n99999 99999", "True\n99999 None"], position=3, topic="perf_tricks",
                role="practice", difficulty=2,
                hint="Генератор хранит только состояние, а не элементы. Но сколько раз его можно пройти?",
                explanation="Генератор занимает сотню-другую байт при любом n, список — сотни килобайт. Первый max проходит генератор до конца, второй получает пустую последовательность и возвращает default.",
                feedback={"False\n99999 99999": "Генератор не хранит элементы — он меньше списка.",
                          "True\n99999 99999": "Генератор одноразовый: второй max получает пустоту.",
                          "True\n99999 None": "Для пустой последовательности max возвращает значение default."}),
        choice("py_perf_003", "Быстрая проверка", "Нужно много раз проверять x in banned. Какую структуру выбрать для banned?",
               ["set", "list", "tuple", "str со словами через пробел"], 0,
               topic="perf_tricks", hint="Какая структура находит элемент по хешу?",
               explanation="Множество (как и словарь) ищет по хешу за O(1) в среднем. list и tuple просматривают все элементы — O(n). В строке in ищет подстроку: «ad» найдётся внутри «ads» — это ещё и ошибка.",
               feedback={"list": "x in list просматривает элементы по одному — O(n).",
                         "tuple": "Кортеж ищет так же, как список, — O(n).",
                         "str со словами через пробел": "in по строке ищет подстроку: найдёт «ad» внутри «ads»."}),
        bug("py_perf_004", "Кэш и список", """\
            from functools import lru_cache

            @lru_cache
            def total(prices):
                return sum(prices)

            print(total([10, 20, 30]))
            print(total.cache_info().misses)""", {6: "print(total((10, 20, 30)))"},
            expect_error="TypeError", topic="perf_tricks",
            hint="Кэш — это словарь, где ключ — аргументы. Каким должен быть ключ словаря?",
            explanation="lru_cache хранит результаты в словаре по аргументам, а список нехешируем: TypeError: unhashable type: 'list'. Передайте кортеж.",
            difficulty=2),
        predict("py_perf_005", "__slots__ и наследование", """\
                class Point:
                    __slots__ = ("x", "y")

                class Base:
                    pass

                class Tagged(Base):
                    __slots__ = ("tag",)

                p, t = Point(), Tagged()
                t.extra = 1
                print(hasattr(p, "__dict__"), hasattr(t, "__dict__"), t.extra)""",
                ["False False 1", "True True 1", "AttributeError"], position=1, topic="perf_tricks",
                role="practice", difficulty=3,
                hint="__slots__ убирает __dict__ только если слоты объявлены во всей цепочке наследования.",
                explanation="У Point есть только слоты x и y — словаря атрибутов нет. Tagged объявил слоты, но его родитель Base — нет, и __dict__ приходит от Base: новый атрибут extra добавляется, а экономия памяти пропадает.",
                feedback={"False False 1": "Base без __slots__ даёт объектам Tagged словарь __dict__.",
                          "True True 1": "У Point слоты во всей цепочке — __dict__ нет.",
                          "AttributeError": "Благодаря __dict__ от Base атрибут extra добавляется без ошибки."}),
        multi("py_perf_006", "Что ускорит программу", "Какие изменения обычно ускоряют программу на CPython, не меняя результат?",
              list(SPEEDUPS), [i for i, ok in enumerate(SPEEDUPS.values()) if ok],
              check=lambda option: SPEEDUPS[option], topic="perf_tricks",
              hint="Ищите изменения, которые убирают лишнюю работу или переносят её в C.",
              explanation="Множество ищет за O(1), join собирает строку за один проход, вынос из цикла убирает повторные вычисления. CPython иногда ускоряет += для строк на месте, но это не гарантировано (PEP 8 советует join). while не быстрее for, а встроенная sum (на C) быстрее ручного цикла.",
              feedback={"Заменить цикл for на while": "while обычно медленнее: счётчик приходится менять вручную на Python.",
                        "Переписать sum(nums) ручным циклом for": "sum написана на C — ручной цикл медленнее."}),
        match("py_perf_007", "Инструменты замера",
              ["time.perf_counter", "timeit", "cProfile", "tracemalloc", "functools.lru_cache"],
              rights=["Точные часы для разового замера", "Многократный запуск маленького фрагмента",
                      "Время и число вызовов каждой функции", "Отслеживает выделение памяти",
                      "Запоминает результаты вызовов"],
              prompt="Сопоставьте инструмент и назначение", topic="perf_measure",
              hint="cProfile — профилировщик, tracemalloc — память (malloc).",
              explanation="perf_counter — часы, timeit — повторные замеры, cProfile — профиль по функциям, tracemalloc — память, lru_cache — не замер, а ускорение повторных вызовов."),
        predict("py_perf_008", "timeit считает запуски", """\
                import timeit

                calls = []
                seconds = timeit.timeit(lambda: calls.append(len(calls)), number=500)
                print(len(calls), calls[-1], type(seconds).__name__)""",
                ["1 0 float", "500 500 float", "500 499 int"], position=1, topic="perf_measure",
                hint="number — сколько раз вызвать функцию. Что добавляется на последнем вызове?",
                explanation="timeit вызвал функцию 500 раз и вернул общее время в секундах — дробное число. На последнем вызове длина была 499.",
                feedback={"1 0 float": "number=500 — функция вызвана 500 раз.",
                          "500 500 float": "Последний вызов добавил len(calls) до добавления — 499.",
                          "500 499 int": "timeit возвращает время в секундах — float."}),
        typed("py_perf_009", "Скрытый вложенный цикл", """\
              banned_list = list(range(0, 3000, 3))
              banned_set = set(banned_list)
              checks_list = checks_set = 0

              for x in range(3000):
                  for item in banned_list:
                      checks_list += 1
                      if item == x:
                          break
                  checks_set += 1

              print(len(banned_list), checks_list, checks_set)""",
              topic="perf_measure", role="practice", difficulty=3,
              hint="Цикл по banned_list — это то, что делает x in список. Множество отвечает за одну проверку.",
              explanation="Для 2000 чисел, которых нет в списке, просматриваются все 1000 элементов — 2 000 000 сравнений; для найденных — в среднем половина, ещё 500 500. Всего около 2,5 миллиона против 3000 проверок множества. Вот почему x in список внутри цикла опасен."),
        predict("py_perf_010", "Босс: найти дубликат", """\
                def has_dup_slow(items):
                    steps = 0
                    for i in range(len(items)):
                        for j in range(i + 1, len(items)):
                            steps += 1
                            if items[i] == items[j]:
                                return True, steps
                    return False, steps

                def has_dup_fast(items):
                    seen = set()
                    for steps, x in enumerate(items, 1):
                        if x in seen:
                            return True, steps
                        seen.add(x)
                    return False, len(items)

                data = list(range(1000)) + [999]
                print(has_dup_slow(data))
                print(has_dup_fast(data))""",
                ["(True, 1001)\n(True, 1001)", "(True, 1000000)\n(True, 1001)", "(True, 500500)\n(True, 1000)"],
                position=2, topic="perf_measure", role="boss", difficulty=4,
                hint="Сколько пар (i, j) проверит двойной цикл, если дубликат — последний элемент?",
                explanation="Дубликат — последний элемент, поэтому медленная версия перебирает почти все пары: 1000 + 999 + … + 1 = 500 500 шагов (O(n²)). Быстрая проходит список один раз и находит повтор на 1001-м элементе (O(n)).",
                feedback={"(True, 1001)\n(True, 1001)": "Вложенные циклы проверяют пары — шагов гораздо больше.",
                          "(True, 1000000)\n(True, 1001)": "Пары без повторов: j начинается с i + 1, это сумма 1000 + 999 + … + 1.",
                          "(True, 500500)\n(True, 1000)": "enumerate(items, 1) нумерует с единицы: повтор — 1001-й элемент."}),
    ],
))

# ------------------------------------------------------------------ project
PEP8_NAMES = {
    "total_price — переменная": True,
    "MAX_RETRIES — константа модуля": True,
    "UserAccount — класс": True,
    "getUserName — функция": False,
    "Calculate_Total — функция": False,
    "_cache — внутренний атрибут": True,
}

MODULES.append(dict(
    id="project", title="Программа как проект", description="__main__, argparse, logging, PEP 8, docstring",
    icon="🏗️",
    topics=[
        topic("proj_structure", "Структура программы",
              "Код программы держат в функциях, точка входа — main(), а запуск — под if __name__ == \"__main__\":. Имена — по PEP 8, у функций — docstring.",
              """
              Каждый файл .py — модуль. При запуске файла его __name__ равен "__main__", а при импорте — имени модуля. Поэтому if __name__ == "__main__": main() выполняет программу при запуске, но не при импорте: функции модуля можно переиспользовать и тестировать.

              Типичная структура: импорты сверху (стандартная библиотека, сторонние, свои — группами), константы, функции и классы, main(argv) возвращает код выхода, внизу — sys.exit(main(sys.argv[1:])). Код выхода 0 — успех, не 0 — ошибка: так программу встраивают в скрипты.

              PEP 8 — стиль кода Python: отступ 4 пробела, имена_функций_и_переменных, ИменаКлассов, КОНСТАНТЫ, _внутренние_имена, пробелы вокруг операторов, строки до 79–99 символов. Форматировщики (black, ruff format) и линтеры (ruff, flake8) проверяют это автоматически.

              Docstring — строка сразу после def/class: первая строка — кратко что делает, дальше подробности. Её видно в help(функция) и в атрибуте __doc__.

              Папка с модулями и файлом __init__.py — пакет: from shop.cart import Cart. Зависимости проекта описывают в pyproject.toml, а ставят в виртуальное окружение (python -m venv .venv).
              """,
              [("""\
                \"\"\"Мини-утилита: приветствует пользователя.\"\"\"
                import sys

                GREETING = "Привет"


                def greet(name: str) -> str:
                    \"\"\"Возвращает приветствие для name.\"\"\"
                    return f"{GREETING}, {name}!"


                def main(argv: list[str]) -> int:
                    print(greet(argv[0] if argv else "мир"))
                    return 0


                if __name__ == "__main__":
                    code = main(["Ада"])
                    print("код выхода:", code)""", "При запуске __name__ == \"__main__\", при импорте — нет.")],
              ["Писать логику на верхнем уровне модуля: при импорте она выполнится, а протестировать её трудно.",
               "Опечатка в проверке: __name__ == \"main\" — условие всегда ложно, программа молча ничего не делает."]),
        topic("proj_cli_logging", "argparse и logging",
              "argparse разбирает аргументы командной строки и сам пишет справку и ошибки. logging пишет сообщения с уровнями важности, которые можно включать и выключать без правки кода.",
              """
              parser = argparse.ArgumentParser(description=...) — парсер. add_argument("file") — обязательный позиционный аргумент, add_argument("--limit", type=int, default=10) — необязательный с преобразованием типа, add_argument("-v", "--verbose", action="store_true") — флаг True/False, nargs="+" — один или больше значений, choices=[...] — допустимые значения. args = parser.parse_args() читает sys.argv; в тестах передают список: parse_args(["a.txt", "--limit", "5"]).

              При ошибке (нет обязательного аргумента, не то значение) argparse печатает подсказку в stderr и завершает программу с кодом 2 (SystemExit). --help генерируется сам. required=True делает опцию с -- обязательной. Подкоманды, как у git: sub = parser.add_subparsers(dest="command", required=True); sub.add_parser("add") — у каждой свои аргументы.

              logging в проекте (основы — в модуле «Тестирование и отладка»): basicConfig вызывают один раз в точке входа (force=True — перенастроить заново), а в каждом модуле берут log = logging.getLogger(__name__). Логгеры образуют дерево по точкам в имени: app.db — потомок app. Уровень можно задать отдельному логгеру — log.setLevel(logging.WARNING), — и шумный модуль замолчит, не трогая остальные.

              Аргументы передают отдельно: log.info("файл %s", name) — строка форматируется, только если сообщение реально пишется.

              print — для результата программы, logging — для диагностики.
              """,
              [("""\
                import argparse
                import logging
                import sys

                parser = argparse.ArgumentParser(prog="resize")
                parser.add_argument("image")
                parser.add_argument("--width", type=int, default=800)
                parser.add_argument("-q", "--quiet", action="store_true")
                args = parser.parse_args(["cat.png", "--width", "320"])

                logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(levelname)s %(message)s", force=True)
                log = logging.getLogger("resize")
                log.debug("не видно: уровень ниже INFO")
                log.info("сжимаю %s до %d px", args.image, args.width)
                print(args.quiet)""", "stream=sys.stdout — чтобы сообщения шли в обычный вывод (по умолчанию — stderr).")],
              ["Строить строку для лога заранее: log.debug(f\"...{дорогой_расчёт()}\") считает, даже когда DEBUG выключен.",
               "Забыть type=int: argparse возвращает строки, и \"3\" * 2 даст \"33\".",
               "Вызывать basicConfig в каждом модуле: настраивают один раз в точке входа."]),
    ],
    tasks=[
        task("t_proj_cli", "Своя командная строка",
             "Прочитайте одну строку — это аргументы командной строки, разделённые пробелами. Разберите их через argparse: позиционный аргумент word, необязательный --times (целое, по умолчанию 1) и --sep (строка, по умолчанию пробел). Выведите word, повторённое times раз через sep. Код держите в функции main(argv). Учтите, что argparse понимает и --times=2, и сокращения вроде --ti 3.",
             solution="""\
                import argparse


                def main(argv):
                    parser = argparse.ArgumentParser(prog="repeat")
                    parser.add_argument("word")
                    parser.add_argument("--times", type=int, default=1)
                    parser.add_argument("--sep", default=" ")
                    args = parser.parse_args(argv)
                    print(args.sep.join([args.word] * args.times))


                if __name__ == "__main__":
                    main(input().split())""",
             starter="""\
                def main(argv):
                    print(argv[0])

                main(input().split())""",
             tests=["привет --times 3 --sep -\n", "эхо\n", "ха --times 4\n", "--sep + да --times 2\n",
                    "ой --times=2 --sep=,\n", "ха --ti 3\n"],
             hint="parse_args принимает список строк. Для повтора: sep.join([word] * times).",
             difficulty=3,
             requires=dict(defines=["main"], calls_in={"main": ["ArgumentParser", "add_argument", "parse_args"]})),
    ],
    levels=[
        predict("py_proj_001", "Кто такой __main__", """\
                def main():
                    print("запуск main")

                print("имя модуля:", __name__)
                if __name__ == "__main__":
                    main()""",
                ["запуск main\nимя модуля: __main__", "имя модуля: main", "имя модуля: main.py\nзапуск main"],
                position=1, topic="proj_structure",
                hint="Какое имя получает файл, который запустили напрямую?",
                explanation="Запущенный файл всегда называется \"__main__\", поэтому условие истинно и main() вызывается — после печати имени.",
                feedback={"запуск main\nимя модуля: __main__": "Код выполняется сверху вниз: сначала печать имени, потом проверка.",
                          "имя модуля: main": "Имя запущенного модуля — \"__main__\" с подчёркиваниями.",
                          "имя модуля: main.py\nзапуск main": "__name__ — не имя файла, а \"__main__\"."}),
        bug("py_proj_002", "Тихая программа", """\
            def main():
                print("программа работает")

            if __name__ == "main":
                main()""", {3: "if __name__ == \"__main__\":"},
            prompt="Программа ничего не печатает. Найдите строку с ошибкой", topic="proj_structure",
            hint="Сравните строку в условии с настоящим значением __name__ запущенного файла.",
            explanation="У запущенного файла __name__ равен \"__main__\" — с двумя подчёркиваниями с каждой стороны. С \"main\" условие ложно, и программа молча ничего не делает.",
            difficulty=1, role="practice"),
        fill("py_proj_003", "Аргументы с типом", "Сделайте так, чтобы программа напечатала «ойойой»",
             """\
             import argparse

             parser = argparse.ArgumentParser()
             parser.add_argument("count", type={{0}})
             parser.add_argument("--word", default={{1}})
             args = parser.parse_args(["3"])
             print(args.word * args.count)""", ["int", "str", "\"ой\"", "None"], ["int", "\"ой\""],
             topic="proj_cli_logging", hint="argparse по умолчанию возвращает строки. Что получится из «ой» * \"3\"?",
             explanation="type=int превращает \"3\" в число 3, а default задаёт значение --word, если флаг не передан. Со строкой \"3\" умножение строки на строку — TypeError.",
             role="lesson", expect="ойойой\n"),
        predict("py_proj_004", "Разбор аргументов", """\
                import argparse

                parser = argparse.ArgumentParser(prog="tool")
                parser.add_argument("files", nargs="+")
                parser.add_argument("-v", "--verbose", action="store_true")
                parser.add_argument("--limit", type=int, default=10)
                args = parser.parse_args(["a.txt", "b.txt", "--limit", "5"])
                print(args.files, args.verbose, args.limit)""",
                ["a.txt False 5", "['a.txt', 'b.txt'] None '5'", "['a.txt', 'b.txt'] True 5"], position=1,
                topic="proj_cli_logging", role="practice", difficulty=2,
                hint="nargs=\"+\" собирает список. Что даёт store_true, если флага нет? И что делает type=int?",
                explanation="files — список из двух имён, флага -v нет — store_true даёт False, --limit превращён в число 5.",
                feedback={"a.txt False 5": "nargs=\"+\" собирает все позиционные значения в список.",
                          "['a.txt', 'b.txt'] None '5'": "store_true по умолчанию даёт False, а type=int — число.",
                          "['a.txt', 'b.txt'] True 5": "Флага -v в списке нет — verbose равен False."}),
        predict("py_proj_005", "Логгеры модулей", """\
                import logging
                import sys

                logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                                    format="%(name)s|%(levelname)s|%(message)s", force=True)
                db = logging.getLogger("app.db")
                db.setLevel(logging.WARNING)
                api = logging.getLogger("app.api")
                db.info("подключение")
                db.warning("медленный запрос")
                api.info("GET /users")
                print(logging.getLogger("app.db") is db)""",
                ["app.db|INFO|подключение\napp.db|WARNING|медленный запрос\napp.api|INFO|GET /users\nTrue",
                 "app.db|WARNING|медленный запрос\nTrue",
                 "app.db|WARNING|медленный запрос\napp.api|INFO|GET /users\nFalse"],
                position=3, topic="proj_cli_logging", role="practice", difficulty=3,
                hint="У логгера app.db свой порог. А что возвращает getLogger при повторном вызове с тем же именем?",
                explanation="Для app.db порог поднят до WARNING — его info отсекается. app.api наследует порог INFO от корня. getLogger с тем же именем возвращает тот же объект — поэтому в каждом модуле пишут getLogger(__name__) и настраивают уровни по именам.",
                feedback={"app.db|INFO|подключение\napp.db|WARNING|медленный запрос\napp.api|INFO|GET /users\nTrue": "db.setLevel(WARNING) отсекает info этого логгера.",
                          "app.db|WARNING|медленный запрос\nTrue": "Порог WARNING задан только для app.db, app.api пишет INFO.",
                          "app.db|WARNING|медленный запрос\napp.api|INFO|GET /users\nFalse": "getLogger с одним именем всегда возвращает один и тот же логгер."}),
        multi("py_proj_006", "Имена по PEP 8", "Какие имена записаны по PEP 8?",
              list(PEP8_NAMES), [i for i, ok in enumerate(PEP8_NAMES.values()) if ok],
              check=lambda option: PEP8_NAMES[option], topic="proj_structure",
              hint="Функции и переменные — snake_case, классы — CamelCase, константы — ВЕРХНИЙ_РЕГИСТР.",
              explanation="snake_case для переменных и функций, CapWords для классов, UPPER_CASE для констант, ведущее подчёркивание — для внутренних имён. getUserName и Calculate_Total нарушают стиль функций.",
              feedback={"getUserName — функция": "camelCase — стиль Java/JS. В Python: get_user_name.",
                        "Calculate_Total — функция": "Функции пишут строчными: calculate_total."}),
        predict("py_proj_007", "Docstring", """\
                def area(width, height):
                    \"\"\"Возвращает площадь прямоугольника.

                    width и height — длины сторон.
                    \"\"\"
                    return width * height

                print(area.__doc__.splitlines()[0])
                print(area(3, 4))""",
                ["None\n12", "width и height — длины сторон.\n12", "\"\"\"Возвращает площадь прямоугольника.\n12"],
                position=1, topic="proj_structure", role="practice",
                hint="Строка сразу после def попадает в __doc__.",
                explanation="Первая строка в теле функции — docstring: она хранится в __doc__ (без кавычек). Её первая строка — краткое описание.",
                feedback={"None\n12": "Строка сразу после def — это docstring, она сохраняется в __doc__.",
                          "width и height — длины сторон.\n12": "splitlines()[0] — первая строка, краткое описание.",
                          "\"\"\"Возвращает площадь прямоугольника.\n12": "Кавычки — синтаксис, в __doc__ хранится только текст."}),
        order("py_proj_008", "Точка входа", "Расставьте строки: программа должна напечатать «Привет, Ада!»",
              ["import sys",
               "def main(argv):",
               "    name = argv[0] if argv else \"мир\"",
               "    print(f\"Привет, {name}!\")",
               "    return 0",
               "if __name__ == \"__main__\":",
               "    sys.exit(main([\"Ада\"]))"],
              topic="proj_structure", hint="Тело функции — после def, запуск — в самом конце, под проверкой __name__.",
              explanation="Импорт, затем функция main с телом, и последней — точка входа: sys.exit(main(...)) завершает программу с кодом, который вернула main (0 — успех)."),
        match("py_proj_009", "Параметры add_argument",
              ["nargs=\"+\"", "action=\"store_true\"", "type=int", "choices=[1, 2, 3]", "required=True"],
              rights=["Один или больше значений — в список", "Флаг без значения: есть — True, нет — False",
                      "Превращает строку из командной строки в число", "Разрешает только перечисленные значения",
                      "Делает опцию с -- обязательной"],
              prompt="Сопоставьте параметр и что он делает", topic="proj_cli_logging",
              hint="Все значения из командной строки — строки. Какой параметр это меняет?",
              explanation="nargs управляет количеством значений, store_true делает флаг, type преобразует строку, choices ограничивает значения, required делает опцию обязательной (по умолчанию опции с -- необязательны)."),
        predict("py_proj_011", "Ошибка в аргументах", """\
                import argparse

                parser = argparse.ArgumentParser(prog="tool")
                parser.add_argument("--limit", type=int)
                try:
                    parser.parse_args(["--limit", "много"])
                except SystemExit as error:
                    print("код выхода:", error.code)""",
                ["ValueError", "код выхода: 1", "код выхода: 0"], position=3, topic="proj_cli_logging",
                role="practice", difficulty=3,
                hint="argparse сам сообщает об ошибке и завершает программу. Каким кодом?",
                explanation="«много» не превращается в int: argparse печатает подсказку в stderr и вызывает sys.exit(2). Код 2 — стандарт для неверных аргументов командной строки. В тестах ловят SystemExit или создают парсер с exit_on_error=False.",
                feedback={"ValueError": "argparse перехватывает ошибку преобразования и завершает программу через SystemExit.",
                          "код выхода: 1": "Для неверных аргументов argparse использует код 2.",
                          "код выхода: 0": "Код 0 означает успех — здесь ошибка."}),
        predict("py_proj_010", "Босс: мини-CLI", """\
                import argparse
                import logging
                import sys

                def build_parser():
                    parser = argparse.ArgumentParser(prog="todo")
                    sub = parser.add_subparsers(dest="command", required=True)
                    add = sub.add_parser("add")
                    add.add_argument("title")
                    add.add_argument("--priority", type=int, choices=[1, 2, 3], default=2)
                    sub.add_parser("list")
                    return parser

                def main(commands):
                    logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                                        format="%(levelname)s %(message)s", force=True)
                    tasks = []
                    for line in commands:
                        args = build_parser().parse_args(line.split())
                        if args.command == "add":
                            tasks.append((args.priority, args.title))
                            logging.debug("добавлено: %s", args.title)
                        else:
                            for priority, title in sorted(tasks):
                                print(priority, title)

                main(["add молоко --priority 3", "add хлеб --priority 1", "add сыр", "list"])""",
                ["DEBUG добавлено: молоко\nDEBUG добавлено: хлеб\nDEBUG добавлено: сыр\n1 хлеб\n2 сыр\n3 молоко",
                 "3 молоко\n1 хлеб\n2 сыр",
                 "1 хлеб\n3 молоко\n2 сыр"],
                position=1, topic="proj_cli_logging", role="boss", difficulty=4,
                hint="Видны ли DEBUG-сообщения при уровне INFO? Какой приоритет у «сыр» и как сортируются кортежи?",
                explanation="Подкоманда add кладёт (приоритет, название); у «сыр» --priority не указан — default 2. DEBUG ниже INFO и не печатается. list сортирует кортежи по первому элементу — приоритету.",
                feedback={"DEBUG добавлено: молоко\nDEBUG добавлено: хлеб\nDEBUG добавлено: сыр\n1 хлеб\n2 сыр\n3 молоко": "Уровень INFO отсекает DEBUG-сообщения.",
                          "3 молоко\n1 хлеб\n2 сыр": "list печатает sorted(tasks) — по приоритету.",
                          "1 хлеб\n3 молоко\n2 сыр": "У «сыр» приоритет по умолчанию 2 — он между 1 и 3."}),
    ],
))
