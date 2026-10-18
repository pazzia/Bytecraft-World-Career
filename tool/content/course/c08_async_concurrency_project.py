"""Модули 34–37: asyncio, потоки и процессы, производительность, программа
как проект (argparse, logging, структура, PEP 8)."""
from bclib import (choice, fill, match, multi, order, predict, bug, typed, topic, pitfall, task, run,
                   categorize, fix_line)


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
              "Корутина — функция `async def`, которая умеет ждать, не останавливая остальные задачи программы.",
              """
              Программа, которая скачивает страницы или ждёт ответа базы данных, большую часть времени простаивает. Асинхронность позволяет в одном потоке вести много таких ожиданий сразу: пока одна задача ждёт, работают другие.

              ## Как записать

              ```syntax
              import asyncio

              async def main():
                  результат = await другая_корутина()

              asyncio.run(main())
              ```

              - `async def` объявляет корутинную функцию.
              - Её вызов ничего не выполняет, а только создаёт объект-корутину.
              - Выполняют корутину через `await` внутри другой корутины или через `asyncio.run` на верхнем уровне — обычно один раз, для `main()`.

              ## Что делает await

              `await` пишут только внутри `async def`. В этой точке корутина отдаёт управление циклу событий — диспетчеру, который запускает другие готовые задачи. Когда ожидание закончится, корутина продолжит с того же места.

              ## Блокировать нельзя

              `await asyncio.sleep(сек)` — пауза, во время которой работают другие корутины. `time.sleep` останавливает весь поток вместе с циклом событий. То же делает долгий расчёт внутри корутины: остальные задачи замирают.

              Асинхронность не ускоряет вычисления, она выигрывает только на ожиданиях: сеть, диск, база данных. Два `await` подряд выполняются по очереди. Как ждать несколько корутин одновременно — в теме [[async_tasks|задачи и gather]].
              """,
              [("""\
                import asyncio

                async def greet(name):
                    await asyncio.sleep(0.01)
                    return f"привет, {name}"

                async def main():
                    text = await greet("Ада")
                    print(text)

                asyncio.run(main())""",
                "await дождался результата, asyncio.run запустил main"),
               ("""\
                import asyncio

                async def save():
                    print("сохраняю")

                job = save()
                print("корутина создана")
                asyncio.run(job)""",
                "Тело выполнилось в asyncio.run, а не при вызове save()"),
               ("""\
                import asyncio

                async def step(name):
                    print("начал", name)
                    await asyncio.sleep(0.01)
                    print("закончил", name)

                async def main():
                    await step("A")
                    await step("B")

                asyncio.run(main())""",
                "Два await подряд идут по очереди: B ждёт конца A")],
              [pitfall("Без await корутина не выполняется: RuntimeWarning: coroutine 'save' was never awaited.",
                       bad="save()", good="await save()"),
               pitfall("time.sleep в корутине останавливает весь цикл событий и все задачи сразу.",
                       bad="time.sleep(1)", good="await asyncio.sleep(1)"),
               pitfall("await в обычной функции — SyntaxError: 'await' outside async function.",
                       bad='''
                           def main():
                               await asyncio.sleep(1)''',
                       good='''
                           async def main():
                               await asyncio.sleep(1)''', syntax_error=True),
               pitfall("asyncio.run внутри работающей корутины — RuntimeError. Внутри корутин ждут через await.",
                       bad="data = asyncio.run(fetch())", good="data = await fetch()")]),
        topic("async_tasks", "Задачи: gather и create_task",
              "`gather` и задачи запускают несколько корутин одновременно: общее время равно самому долгому ожиданию.",
              """
              Скачать десять страниц по очереди — это десять ожиданий подряд. Если запустить их одновременно, общее время сократится до самого долгого из них. Для этого корутины превращают в задачи.

              ## Три способа

              - `asyncio.gather(f(), g())` — ждать все и получить список результатов
              - `asyncio.create_task(f())` — запустить в фоне, результат забрать позже
              - `asyncio.TaskGroup()` — группа задач с общей обработкой ошибок (с Python 3.11)

              ## gather

              ```syntax
              результаты = await asyncio.gather(корутина_1, корутина_2)
              ```

              Результаты идут в порядке аргументов, а не в порядке завершения. Если одна корутина упала, исключение долетит до `await gather`, а остальные продолжат работать. С `return_exceptions=True` исключения встают в список на место результатов.

              ## create_task

              `task = asyncio.create_task(f())` ставит корутину в план. Работать она начнёт, когда текущая корутина отдаст управление на `await`. Результат забирают через `await task`.

              Ссылку на задачу храните в переменной: задачу, на которую никто не ссылается, может удалить сборщик мусора.

              ## TaskGroup

              ```syntax
              async with asyncio.TaskGroup() as tg:
                  задача = tg.create_task(корутина)
              ```

              Выход из блока ждёт все задачи. Если одна упала, остальные отменяются, а ошибки приходят вместе как `ExceptionGroup`; их ловят через {`except*`} ([[exc_types|группы исключений]]).

              ## Что выбрать

              - Набор корутин известен заранее, нужны результаты — `gather`.
              - Ошибка в одной задаче должна остановить остальные — `TaskGroup`.
              - Одна фоновая работа рядом с основной — `create_task`.

              Время ожидания ограничивают [[async_timeouts|таймауты]], а данные между задачами передают [[async_sync|очереди]].
              """,
              [("""\
                import asyncio

                async def load(name, delay):
                    await asyncio.sleep(delay)
                    print("готов", name)
                    return len(name)

                async def main():
                    sizes = await asyncio.gather(
                        load("фото", 0.03),
                        load("текст", 0.01),
                    )
                    print(sizes)

                asyncio.run(main())""",
                "Печать — по готовности, а результаты — в порядке аргументов"),
               ("""\
                import asyncio

                async def backup():
                    await asyncio.sleep(0.02)
                    return "копия готова"

                async def main():
                    task = asyncio.create_task(backup())
                    print("main работает дальше")
                    await asyncio.sleep(0.01)
                    print("main ждёт задачу")
                    print(await task)

                asyncio.run(main())""",
                "Задача шла в фоне, пока main делал своё"),
               ("""\
                import asyncio

                async def price(shop, value):
                    await asyncio.sleep(0.01)
                    return shop, value

                async def main():
                    async with asyncio.TaskGroup() as tg:
                        a = tg.create_task(price("A", 90))
                        b = tg.create_task(price("B", 75))
                    print(a.result())
                    print(b.result())

                asyncio.run(main())""",
                "После блока все задачи готовы, result() отдаёт значения"),
               ("""\
                import asyncio

                async def check(n):
                    if n < 0:
                        raise ValueError(n)
                    return n * 2

                async def main():
                    res = await asyncio.gather(
                        check(1), check(-1),
                        return_exceptions=True,
                    )
                    print(res)

                asyncio.run(main())""",
                "С return_exceptions ошибка стоит в списке на месте результата")],
              [pitfall("await в цикле ждёт корутины по одной: общее время — сумма всех пауз.",
                       bad='''
                           for url in urls:
                               pages.append(await fetch(url))''',
                       good="pages = await asyncio.gather(*(fetch(u) for u in urls))"),
               pitfall("gather ждёт корутины отдельными аргументами; список целиком даёт TypeError: unhashable type: 'list'.",
                       bad="await asyncio.gather(jobs)", good="await asyncio.gather(*jobs)"),
               pitfall("Задачу без сохранённой ссылки может удалить сборщик мусора до конца её работы.",
                       bad="asyncio.create_task(backup())", good="task = asyncio.create_task(backup())")]),
        topic("async_timeouts", "Таймауты и отмена",
              "Таймаут ограничивает ожидание, а отмена останавливает задачу исключением CancelledError внутри неё.",
              """
              Сервер может не ответить никогда. Программа не должна ждать вечно: через несколько секунд она сдаётся, убирает за собой и сообщает об ошибке. Для этого в asyncio есть таймауты и отмена задач.

              ## Как записать

              ```syntax
              результат = await asyncio.wait_for(корутина, timeout=секунды)

              async with asyncio.timeout(секунды):
                  await долгая_операция()
              ```

              - {`wait_for`} ограничивает одну корутину.
              - {`asyncio.timeout`} (с Python 3.11) ограничивает весь блок, сколько бы `await` в нём ни было.

              Если время вышло, наружу вылетает {`TimeoutError`}.

              ## Как работает отмена

              `task.cancel()` не убивает задачу сразу. Внутри задачи на текущем `await` возникает исключение {`asyncio.CancelledError`}. Благодаря этому срабатывают [[exc_try|finally]] и `with`: задача успевает закрыть файлы и соединения.

              Таймауты устроены так же: когда время вышло, они отменяют ожидание. После отмены `await task` выбрасывает {`CancelledError`}, а `task.cancelled()` возвращает `True`.

              ## Не глушите отмену

              {`CancelledError`} наследует `BaseException`, а не `Exception` ([[exc_types|иерархия исключений]]). Поэтому `except Exception` его не ловит, а голый `except:` поймает — и задача перестанет отменяться.

              Если отмену перехватили, чтобы убрать за собой, выбросьте её дальше через `raise`.
              """,
              [("""\
                import asyncio

                async def ask_server():
                    await asyncio.sleep(1)
                    return "ответ"

                async def main():
                    try:
                        r = await asyncio.wait_for(
                            ask_server(), timeout=0.02)
                        print(r)
                    except TimeoutError:
                        print("сервер молчит")

                asyncio.run(main())""",
                "Пауза длиннее таймаута — вместо ответа TimeoutError"),
               ("""\
                import asyncio

                async def download():
                    try:
                        await asyncio.sleep(1)
                    finally:
                        print("закрываю соединение")

                async def main():
                    try:
                        async with asyncio.timeout(0.02):
                            await download()
                    except TimeoutError:
                        print("время вышло")

                asyncio.run(main())""",
                "Сначала finally внутри задачи, потом TimeoutError снаружи"),
               ("""\
                import asyncio

                async def ticker():
                    try:
                        while True:
                            await asyncio.sleep(0.01)
                    except asyncio.CancelledError:
                        print("ticker: стоп")
                        raise

                async def main():
                    t = asyncio.create_task(ticker())
                    await asyncio.sleep(0.03)
                    t.cancel()
                    try:
                        await t
                    except asyncio.CancelledError:
                        print("отменена:", t.cancelled())

                asyncio.run(main())""",
                "cancel() бросил исключение внутрь задачи, raise довёл отмену")],
              [pitfall("Голый except ловит и CancelledError: задача перестаёт отменяться. Перехватили — выбросьте снова.",
                       bad='''
                           try:
                               await fetch()
                           except:
                               log("сбой")''',
                       good='''
                           try:
                               await fetch()
                           except asyncio.CancelledError:
                               cleanup()
                               raise'''),
               pitfall("asyncio.timeout — асинхронный менеджер: TypeError: 'Timeout' object does not support the context manager protocol.",
                       bad='''
                           with asyncio.timeout(1):
                               await fetch()''',
                       good='''
                           async with asyncio.timeout(1):
                               await fetch()'''),
               "Ждать, что cancel() остановит задачу мгновенно: исключение возникнет только на её ближайшем await."]),
        topic("async_sync", "Очереди и семафоры",
              "`asyncio.Queue`, `Semaphore` и `Lock` согласуют корутины: передают данные и ограничивают одновременную работу.",
              """
              Когда задач много, им нужно договариваться. Одни производят данные, другие их обрабатывают. К серверу можно делать не больше пяти запросов сразу. Общий счётчик нельзя менять двум задачам одновременно. Для этого в asyncio есть свои очередь, семафор и замок.

              ## Очередь

              `asyncio.Queue` передаёт данные от производителя к потребителю:

              - `await q.put(x)` — положить; если очередь с `maxsize` заполнена — ждать места
              - `await q.get()` — взять; если пусто — ждать элемента
              - `q.task_done()` и `await q.join()` — дождаться обработки всего положенного

              Конец работы обычно обозначают особым значением, например `None`.

              ## Семафор

              ```syntax
              sem = asyncio.Semaphore(n)

              async with sem:
                  действия
              ```

              Семафор пускает в блок не больше `n` корутин. Остальные ждут на входе, пока кто-то не выйдет. Так ограничивают число одновременных запросов к одному серверу.

              ## Замок

              `asyncio.Lock` — семафор на одного: `async with lock:` пускает в блок одну корутину. Он нужен, если между чтением и записью общих данных есть `await`: в этой точке может вклиниться другая корутина. Без `await` корутины и так не переключаются.

              ## async with и async for

              `async with` — [[ctx_protocol|контекстный менеджер]], вход и выход которого сами умеют ждать. `async for x in поток:` перебирает асинхронный итератор: между элементами можно ждать. Обе конструкции пишут только внутри `async def`.
              """,
              [("""\
                import asyncio

                async def cook(q):
                    for dish in ["суп", "плов"]:
                        await q.put(dish)
                    await q.put(None)

                async def waiter(q):
                    while (dish := await q.get()):
                        print("несу", dish)

                async def main():
                    q = asyncio.Queue()
                    await asyncio.gather(cook(q), waiter(q))

                asyncio.run(main())""",
                "None в очереди — сигнал, что блюд больше не будет"),
               ("""\
                import asyncio

                async def visit(sem, n):
                    async with sem:
                        print("вошёл", n)
                        await asyncio.sleep(0.01 * (n + 1))
                        print("вышел", n)

                async def main():
                    sem = asyncio.Semaphore(2)
                    await asyncio.gather(
                        *(visit(sem, n) for n in range(3)))

                asyncio.run(main())""",
                "Внутри не больше двух: третий вошёл, когда вышел первый"),
               ("""\
                import asyncio

                stock = 1

                async def buy(lock, who):
                    global stock
                    async with lock:
                        if stock > 0:
                            await asyncio.sleep(0.01)
                            stock -= 1
                            print(who, "купил")
                        else:
                            print(who, "опоздал")

                async def main():
                    lock = asyncio.Lock()
                    await asyncio.gather(buy(lock, "Ада"),
                                         buy(lock, "Боб"))
                    print("осталось:", stock)

                asyncio.run(main())""",
                "Замок не дал второму проверить остаток до списания")],
              [pitfall("Потребитель без сигнала конца ждёт get() вечно, и программа не завершается.",
                       bad='''
                           while True:
                               item = await q.get()
                               handle(item)''',
                       good='''
                           while (item := await q.get()) is not None:
                               handle(item)'''),
               pitfall("threading.Lock в корутине блокирует весь цикл событий: для корутин нужен asyncio.Lock.",
                       bad="lock = threading.Lock()", good="lock = asyncio.Lock()"),
               pitfall("Новый семафор в каждой корутине у каждой свой и ничего не ограничивает: создайте один общий.",
                       bad="async with asyncio.Semaphore(2):\n    await fetch()",
                       good="async with sem:\n    await fetch()")]),
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
                ["таймаут", "данные", "таймаут\nslow: уборка"], position=3, topic="async_timeouts",
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
                 "отмена: убираю за собой"], position=1, topic="async_timeouts", role="practice", difficulty=3,
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
                ["[0, 1, 2, 3, 4] 5", "[0, 1, 2, 3, 4] 1", "[0, 1] 2"], position=3, topic="async_sync",
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
                position=1, topic="async_sync", role="boss", difficulty=4,
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
        topic("conc_threads", "Потоки: Thread и join",
              "Поток — ещё одна линия выполнения внутри программы; потоки помогают, когда программа много ждёт.",
              """
              Пока программа ждёт ответа сервера или чтения файла, процессор простаивает. В отдельном потоке это ожидание идёт одновременно с остальной работой. В отличие от [[async_basics|asyncio]], потоки работают и с обычными, не асинхронными функциями.

              ## Как записать

              ```syntax
              import threading

              t = threading.Thread(target=функция, args=(аргумент,))
              t.start()
              t.join()
              ```

              - `target` — функция, которую выполнит поток. Её передают без скобок.
              - `args` — кортеж аргументов; для одного аргумента запятая обязательна.
              - `start()` запускает поток, и программа сразу идёт дальше.
              - `join()` ждёт, пока поток закончит. Без него результат можно прочитать раньше, чем поток его запишет.

              ## Состояние потоков

              - `t.is_alive()` — работает ли поток
              - `threading.active_count()` — сколько потоков живо, включая главный
              - `daemon=True` — фоновый поток: программа не ждёт его при выходе

              ## GIL

              В обычном CPython GIL (глобальная блокировка интерпретатора) разрешает выполнять байт-код только одному потоку за раз. Пока поток ждёт ввода-вывода, GIL отпускается. Поэтому потоки ускоряют ожидание — сеть, диск, — но не вычисления на чистом Python.

              С Python 3.13 есть экспериментальная сборка без GIL, с 3.14 она поддерживается официально. Но ставится она отдельно и по умолчанию не используется.

              ## Потоки в приложении

              Во встроенном Python приложения потоки эмулируются: выполняются по очереди, и ускорения нет. Логика и порядок — как в обычном Python, подробнее — в теме [[conc_processes|процессы]]. Как потокам безопасно делить данные — в теме [[conc_lock|гонка данных]].
              """,
              [("""\
                import threading
                import time

                def download(name):
                    time.sleep(0.02)
                    print("скачан", name)

                t = threading.Thread(target=download,
                                     args=("отчёт",))
                t.start()
                print("главный поток не ждёт")
                t.join()
                print("поток закончил")""",
                "start() не ждёт: главный поток печатает раньше потока"),
               ("""\
                import threading
                import time

                sizes = {}

                def measure(word):
                    time.sleep(0.01)
                    sizes[word] = len(word)

                threads = []
                for w in ["кот", "собака", "ёж"]:
                    t = threading.Thread(
                        target=measure, args=(w,))
                    t.start()
                    threads.append(t)
                for t in threads:
                    t.join()
                print(sizes["собака"])
                print(len(sizes))""",
                "Сначала запускают все потоки, потом ждут каждый"),
               ("""\
                import threading
                import time

                result = []

                def work():
                    time.sleep(0.02)
                    result.append("готово")

                t = threading.Thread(target=work)
                t.start()
                print(result)
                t.join()
                print(result)
                print(t.is_alive())""",
                "До join список пуст, после — заполнен, поток завершён")],
              [pitfall("args ждёт кортеж: (\"отчёт\") — просто строка, и поток упадёт с TypeError: takes 1 positional argument but 5 were given.",
                       bad='Thread(target=download, args=("отчёт"))',
                       good='Thread(target=download, args=("отчёт",))'),
               pitfall("target=work() вызывает функцию сразу в главном потоке, а потоку отдаёт её результат.",
                       bad="Thread(target=work())", good="Thread(target=work)"),
               pitfall("Без join главный поток читает результат раньше, чем поток его запишет.",
                       bad='''
                           t.start()
                           print(result)''',
                       good='''
                           t.start()
                           t.join()
                           print(result)'''),
               "Ждать от потоков ускорения вычислений в обычном CPython: из-за GIL байт-код выполняется по очереди."]),
        topic("conc_lock", "Гонка данных и Lock",
              "Гонка данных — потеря обновлений, когда потоки меняют общее значение; `Lock` пускает к нему один поток за раз.",
              """
              Два кассира одновременно списывают деньги с одного счёта: оба прочитали 100, оба записали своё, и одно списание пропало. С потоками бывает то же самое, причём ошибка проявляется не при каждом запуске.

              ## Откуда берётся гонка

              «Прочитать — изменить — записать» — несколько шагов. Если между ними поток переключится, другой поток прочитает старое значение, и одно из изменений затрётся. Даже `counter += 1` — несколько шагов байт-кода, а не одно действие.

              ## Как записать

              ```syntax
              lock = threading.Lock()

              def работа():
                  with lock:
                      чтение_и_запись_общих_данных
              ```

              `with lock:` пускает в блок один поток, остальные ждут у входа. При выходе из блока замок открывается, даже если внутри случилась ошибка.

              ## Правила

              - Замок создают один на всех, до запуска потоков. Новый {`Lock()`} внутри функции у каждого вызова свой и ничего не защищает.
              - Чтение и запись общего значения держат в одном блоке под замком.
              - Под замком — только работа с общими данными: долгие ожидания под ним выстраивают потоки в очередь.
              - Поток, который второй раз берёт свой же {`Lock`}, зависнет навсегда. Для повторного входа есть `threading.RLock`.

              Чтобы не делить данные вовсе, потоки передают их через [[conc_queue|очередь]].
              """,
              [("""\
                import threading
                import time

                seats = 10

                def book(n):
                    global seats
                    free = seats
                    time.sleep(0.01)
                    seats = free - n

                a = threading.Thread(target=book, args=(3,))
                b = threading.Thread(target=book, args=(2,))
                a.start()
                b.start()
                a.join()
                b.join()
                print(seats)""",
                "Ждали 5 свободных мест, но потоки затёрли изменения друг друга"),
               ("""\
                import threading
                import time

                seats = 10
                lock = threading.Lock()

                def book(n):
                    global seats
                    with lock:
                        free = seats
                        time.sleep(0.01)
                        seats = free - n

                a = threading.Thread(target=book, args=(3,))
                b = threading.Thread(target=book, args=(2,))
                a.start()
                b.start()
                a.join()
                b.join()
                print(seats)""",
                "Под замком второй поток ждал, пока первый закончит")],
              [pitfall("Новый замок при каждом вызове у каждого потока свой и ничего не защищает.",
                       bad='''
                           with threading.Lock():
                               seats -= n''',
                       good='''
                           with lock:
                               seats -= n'''),
               pitfall("Чтение вне замка: другой поток успеет изменить значение до записи.",
                       bad='''
                           free = seats
                           with lock:
                               seats = free - n''',
                       good='''
                           with lock:
                               free = seats
                               seats = free - n'''),
               pitfall("acquire без release при ошибке оставляет замок закрытым навсегда; with открывает его сам.",
                       bad='''
                           lock.acquire()
                           seats -= n
                           lock.release()''',
                       good='''
                           with lock:
                               seats -= n''')]),
        topic("conc_queue", "Очередь между потоками",
              "`queue.Queue` безопасно передаёт данные между потоками, и общий Lock для этого не нужен.",
              """
              Один поток получает задания, другой их выполняет. Делить общий список под замком неудобно, и легко ошибиться. Очередь решает это готово: её методы уже защищены.

              ## Как записать

              ```syntax
              import queue

              q = queue.Queue()
              q.put(элемент)
              элемент = q.get()
              ```

              - `put` кладёт в конец, `get` берёт из начала: первым пришёл — первым ушёл.
              - Если очередь пуста, `get` ждёт, пока кто-то положит элемент.
              - `queue.Queue(maxsize=n)` ограничивает размер: `put` ждёт, пока освободится место.

              ## Как остановить работника

              Работник — поток, который в цикле берёт задания из очереди. Чтобы он закончил, в очередь кладут особое значение, например `None`. Получив его, работник выходит из цикла, и [[conc_threads|`join()`]] потока возвращается. Каждому работнику нужен свой сигнал.

              ## Дождаться обработки

              - `q.task_done()` — работник сообщает, что закончил с элементом
              - `q.join()` — ждёт, пока для каждого `put` вызовут `task_done`

              Так главный поток узнаёт, что все задания обработаны, даже если работники ещё живы. Не путайте `q.join()` очереди и `t.join()` потока.
              """,
              [("""\
                import queue
                import threading

                q = queue.Queue()

                def printer():
                    while (doc := q.get()) is not None:
                        print("печатаю", doc)

                t = threading.Thread(target=printer)
                t.start()
                for doc in ["счёт", "договор"]:
                    q.put(doc)
                q.put(None)
                t.join()
                print("принтер свободен")""",
                "None — сигнал остановки: работник вышел из цикла"),
               ("""\
                import queue
                import threading

                q = queue.Queue()
                done = []

                def worker():
                    while (n := q.get()) is not None:
                        done.append(n * n)
                        q.task_done()

                ts = [threading.Thread(target=worker)
                      for _ in range(2)]
                for t in ts:
                    t.start()
                for n in range(5):
                    q.put(n)
                q.join()
                print(sorted(done))
                for t in ts:
                    q.put(None)""",
                "q.join() вернулся, когда все задания отмечены task_done")],
              [pitfall("Работник без сигнала остановки ждёт get() вечно, и программа не завершается.",
                       bad='''
                           while True:
                               job = q.get()
                               run(job)''',
                       good='''
                           while (job := q.get()) is not None:
                               run(job)'''),
               pitfall("Без task_done() вызов q.join() не вернётся никогда.",
                       bad='''
                           n = q.get()
                           done.append(n)''',
                       good='''
                           n = q.get()
                           done.append(n)
                           q.task_done()'''),
               pitfall("Один None остановит только одного работника: сигнал кладут каждому.",
                       bad="q.put(None)",
                       good='''
                           for _ in workers:
                               q.put(None)''')]),
        topic("conc_pool", "Пул потоков",
              "`ThreadPoolExecutor` раздаёт задания готовым потокам и собирает результаты без ручных start и join.",
              """
              Сто файлов не стоит качать в ста потоках: их создание тоже стоит времени и памяти. Пул держит несколько рабочих потоков и раздаёт им задания по очереди. Пул живёт в модуле `concurrent.futures`.

              ## Как записать

              ```syntax
              from concurrent.futures import ThreadPoolExecutor

              with ThreadPoolExecutor(max_workers=4) as pool:
                  результаты = list(pool.map(функция, данные))
              ```

              Выход из `with` ждёт все задания, как `join` у каждого потока.

              ## map, submit, as_completed

              - {`pool.map(f, данные)`} — результаты в порядке входных данных
              - `pool.submit(f, x)` — одно задание, возвращает `Future`
              - `future.result()` — дождаться результата задания
              - `as_completed(futures)` — выдавать задания по мере готовности

              `Future` — «обещание результата»: объект, в котором результат появится, когда задание закончится. Если в задании было исключение, `result()` выбросит его в главном потоке.

              ## Что выбрать

              - Нужны все результаты по порядку — {`map`}.
              - Готовое нужно обрабатывать сразу — `submit` и `as_completed`.

              Для вычислений есть такой же пул процессов — [[conc_processes|ProcessPoolExecutor]].
              """,
              [("""\
                from concurrent.futures import (
                    ThreadPoolExecutor)
                import time

                def fetch(page):
                    time.sleep(0.01 * (4 - page))
                    return f"стр.{page}"

                with ThreadPoolExecutor(3) as pool:
                    pages = pool.map(fetch, [1, 2, 3])
                    print(list(pages))""",
                "Быстрее всех готова стр.3, но map сохранил порядок"),
               ("""\
                from concurrent.futures import (
                    ThreadPoolExecutor, as_completed)
                import time

                def cook(dish, minutes):
                    time.sleep(minutes / 100)
                    return dish

                orders = [("плов", 3), ("чай", 1),
                          ("суп", 2)]
                with ThreadPoolExecutor() as pool:
                    futs = [pool.submit(cook, d, m)
                            for d, m in orders]
                    for f in as_completed(futs):
                        print(f.result())""",
                "as_completed отдаёт блюда по мере готовности"),
               ("""\
                from concurrent.futures import (
                    ThreadPoolExecutor)

                def parse(text):
                    return int(text)

                with ThreadPoolExecutor() as pool:
                    fut = pool.submit(parse, "12a")
                    try:
                        fut.result()
                    except ValueError as e:
                        print("ошибка:", e)""",
                "Исключение из потока пришло в главный через result()")],
              [pitfall("submit(parse(text)) вызывает функцию сразу, а в пул отдаёт результат; result() даст TypeError.",
                       bad='pool.submit(parse("12"))', good='pool.submit(parse, "12")'),
               pitfall("Исключение задания видно только через result(): без него ошибка пропадает молча.",
                       bad="pool.submit(parse, text)",
                       good='''
                           fut = pool.submit(parse, text)
                           fut.result()'''),
               "Ждать от map результатов по мере готовности: порядок всегда как у входных данных."]),
        topic("conc_processes", "Процессы",
              "Процессы — отдельные копии интерпретатора, которые считают на нескольких ядрах процессора одновременно.",
              """
              Расчёт на чистом Python занимает одно ядро, даже если их восемь: [[conc_threads|GIL]] не даёт потокам считать одновременно. Процессы обходят это ограничение — у каждого свой интерпретатор и свой GIL.

              ## Как записать

              ```syntax
              from concurrent.futures import ProcessPoolExecutor

              if __name__ == "__main__":
                  with ProcessPoolExecutor() as pool:
                      результаты = list(pool.map(функция, данные))
              ```

              Интерфейс тот же, что у [[conc_pool|пула потоков]]: {`map`}, `submit`, `as_completed`. Модуль `multiprocessing` даёт то же на более низком уровне.

              ## Цена процессов

              - Запуск процесса дороже, чем запуск потока.
              - Общей памяти у процессов нет: аргументы и результаты передаются через [[data_json|сериализацию]] модулем `pickle`.
              - Поэтому функцию объявляют на верхнем уровне модуля: `lambda` и вложенные функции не сериализуются.

              ## Зачем проверка __name__

              У запущенного файла `__name__` равен `"__main__"`, у импортированного — имени модуля ([[proj_structure|точка входа]]). Новые процессы на Windows и macOS, а с Python 3.14 и на Linux импортируют главный модуль заново.

              Без проверки каждый из них снова создавал бы пул — Python останавливает это ошибкой `RuntimeError`. Проверку пишут всегда, ради переносимости.

              ## Процессы в приложении

              Во встроенном Python приложения потоки и процессы эмулируются: они выполняются по очереди в одном настоящем потоке и переключаются там, где ждут (`sleep`, замок, очередь, `join`). Логика, порядок и синхронизация — как в обычном Python, но ускорения нет, а у «процессов» общая память.
              """,
              [("""\
                from concurrent.futures import (
                    ProcessPoolExecutor)

                if __name__ == "__main__":
                    with ProcessPoolExecutor(2) as pool:
                        res = pool.map(pow, [2, 3, 4],
                                       [10, 2, 3])
                        print(list(res))""",
                "Каждая пара чисел возведена в степень в процессах пула"),
               ("""\
                import math
                from concurrent.futures import (
                    ProcessPoolExecutor)

                if __name__ == "__main__":
                    with ProcessPoolExecutor() as pool:
                        fut = pool.submit(math.factorial, 20)
                        print(fut.result())""",
                "submit и result работают так же, как у пула потоков"),
               ("""\
                print(__name__)
                if __name__ == "__main__":
                    print("файл запущен, а не импортирован")""",
                "У запущенного файла __name__ равен \"__main__\"")],
              [pitfall("lambda нельзя сериализовать для другого процесса: PicklingError. Нужна функция верхнего уровня.",
                       bad="pool.map(lambda x: x * 2, data)", good="pool.map(double, data)"),
               pitfall("Пул процессов без проверки __name__ на Windows, macOS и Linux 3.14+ падает с RuntimeError.",
                       bad='''
                           with ProcessPoolExecutor() as pool:
                               run(pool)''',
                       good='''
                           if __name__ == "__main__":
                               with ProcessPoolExecutor() as pool:
                                   run(pool)'''),
               "Ждать, что процесс изменит глобальную переменную главной программы: память у процессов своя."]),
        topic("conc_choice", "Потоки, процессы или asyncio",
              "Для ожиданий подходят asyncio и потоки, для вычислений на чистом Python — процессы.",
              """
              Три инструмента решают похожую задачу — делать несколько дел сразу, — но выигрывают в разных случаях. Главный вопрос: программа больше ждёт или больше считает?

              ## Ждёт или считает

              - Ввод-вывод: сеть, диск, база данных. Процессор простаивает, и выигрыш дают и [[conc_threads|потоки]], и [[async_basics|asyncio]].
              - Вычисления на чистом Python: циклы, перебор, математика. Потокам мешает GIL, нужны [[conc_processes|процессы]].

              ## Что выбрать

              | Задача | Инструмент |
              |---|---|
              | тысячи соединений | {`asyncio`} |
              | ожидания в обычном коде | пул потоков |
              | счёт на чистом Python | процессы |
              | счёт в numpy | потоки или процессы |

              ## Почему numpy — исключение

              Библиотеки на C, например numpy, во время тяжёлых операций часто отпускают GIL. Тогда считать параллельно могут и потоки.

              ## Можно сочетать

              Блокирующую функцию из корутины выносят в поток: `await asyncio.to_thread(f, x)`. Цикл событий в это время продолжает работать с другими задачами.

              Во встроенном Python приложения ни один вариант не даёт ускорения: потоки и процессы там эмулируются. Но порядок и логика работы — как в обычном Python.
              """,
              [("""\
                import threading
                import time

                def wait():
                    time.sleep(0.03)

                start = time.perf_counter()
                ts = [threading.Thread(target=wait)
                      for _ in range(3)]
                for t in ts:
                    t.start()
                for t in ts:
                    t.join()
                spent = time.perf_counter() - start
                print(spent < 0.06)""",
                "Три паузы по 0.03 с в потоках заняли меньше 0.06 с"),
               ("""\
                import asyncio
                import time

                def read_disk(name):
                    time.sleep(0.02)
                    return name + ": прочитан"

                async def main():
                    a, b = await asyncio.gather(
                        asyncio.to_thread(read_disk, "a"),
                        asyncio.to_thread(read_disk, "b"))
                    print(a)
                    print(b)

                asyncio.run(main())""",
                "Обычная функция с паузой работает в потоке рядом с asyncio",
                {"native_only": True})],
              [pitfall("Потоки не ускоряют счёт на чистом Python: GIL выполняет байт-код по очереди.",
                       bad="ThreadPoolExecutor().map(count_primes, parts)",
                       good="ProcessPoolExecutor().map(count_primes, parts)"),
               pitfall("Блокирующий вызов в корутине останавливает весь asyncio: выносите его в поток.",
                       bad='data = read_disk("a")',
                       good='data = await asyncio.to_thread(read_disk, "a")'),
               "Отдавать процессам короткие задачи: запуск и передача данных обходятся дороже самой работы."]),
    ],
    tasks=[
        task("t_conc_queue", "Рабочий поток и очередь",
             "Первая строка — n, дальше n слов по одному в строке. Напишите функцию worker(q, out): она берёт слова из очереди queue.Queue, пока не получит None, и добавляет в список out строку «СЛОВО длина» (слово в верхнем регистре и число букв). Главный поток запускает worker в отдельном потоке threading.Thread, кладёт в очередь все слова, затем None, ждёт поток через join и печатает out — по элементу на строке.",
             solution="""\
                import queue
                import threading

                def worker(q, out):
                    while (word := q.get()) is not None:
                        out.append(f"{word.upper()} {len(word)}")

                q = queue.Queue()
                out = []
                t = threading.Thread(target=worker, args=(q, out))
                t.start()
                for _ in range(int(input())):
                    q.put(input())
                q.put(None)
                t.join()
                print("\\n".join(out))""",
             starter="""\
                import queue
                import threading

                def worker(q, out):
                    pass

                q = queue.Queue()
                out = []
                for _ in range(int(input())):
                    q.put(input())
                print("\\n".join(out))""",
             tests=["3\nкот\nпёс\nёжик\n", "1\npython\n", "2\na\nbb\n", "4\nочередь\nпоток\nзамок\nGIL\n"],
             hint="Цикл while (word := q.get()) is not None читает до сигнала остановки. Без join главный поток напечатает out раньше, чем worker его заполнит.",
             difficulty=3,
             requires=dict(defines=["worker"], calls_in={"worker": ["get"]},
                           calls=["Thread", "Queue", "put", "start", "join"])),
    ],
    levels=[
        predict("py_conc_001", "Запуск и ожидание", """\
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
                          "[0, 1, 4, 9] 4": "active_count считает и главный поток, а рабочие уже закончились."}),
        fill("py_conc_002", "Аргументы потока", "Передайте имя в функцию потока",
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
                    expect="привет, Ада\nпоток завершён: True\n"),
        bug("py_conc_003", "Замок, который не запирает", """\
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
            prompt="Два снятия должны оставить 50. Найдите строку с ошибкой", topic="conc_lock",
            hint="Сколько разных замков создаётся в этой программе?",
            explanation="threading.Lock() внутри функции создаёт новый замок при каждом вызове — потоки не мешают друг другу. Оба читают 100, и одно снятие теряется. Нужен один общий lock.",
            difficulty=3),
        predict("py_conc_004", "Порядок в pool.map", """\
                from concurrent.futures import ThreadPoolExecutor
                import time

                def slow_square(n):
                    time.sleep(0.05 * (3 - n))
                    return n * n

                with ThreadPoolExecutor(max_workers=3) as pool:
                    print(list(pool.map(slow_square, [0, 1, 2])))""",
                ["[4, 1, 0]", "[0, 1, 2]"], position=0, topic="conc_pool", role="practice", difficulty=2,
                hint="Быстрее всех закончится slow_square(2). Но в каком порядке map отдаёт результаты?",
                explanation="map возвращает результаты в порядке входных данных, даже если задачи закончились в другом порядке.",
                feedback={"[4, 1, 0]": "Это порядок завершения. map сохраняет порядок входных данных.",
                          "[0, 1, 2]": "map возвращает результаты функции — квадраты."}),
        predict("py_conc_005", "По мере готовности", """\
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
                topic="conc_pool", role="practice", difficulty=3,
                hint="as_completed отдаёт задачи по мере завершения. А список futures?",
                explanation="as_completed выдаёт Future в порядке готовности: b, c, a. Список futures остаётся в порядке создания.",
                feedback={"['a', 'b', 'c']\n['a', 'b', 'c']": "as_completed выдаёт задачи по мере готовности — первой b.",
                          "['b', 'c', 'a']\n['b', 'c', 'a']": "Список futures не пересортировывается: он в порядке submit."}),
        multi("py_conc_006", "Где помогут потоки", "В каких задачах потоки обычного CPython (с GIL) реально ускорят программу?",
              list(PURPOSES), [i for i, ok in enumerate(PURPOSES.values()) if ok],
              check=lambda option: PURPOSES[option], topic="conc_choice",
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
              prompt="Сопоставьте понятие и смысл", topic="conc_choice",
              hint="Где пул потоков, а где пул процессов — подскажут их имена.",
              explanation="GIL ограничивает потоки CPython, Lock защищает общие данные, Queue передаёт задачи, пулы потоков — для ожиданий, пулы процессов — для вычислений."),
        typed("py_conc_008", "Счёт под замком", """\
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
              topic="conc_lock", hint="Сколько раз выполнится counter += 1 и может ли увеличение потеряться?",
              explanation="С общим Lock каждое counter += 1 выполняется целиком: 3 × 5000 = 15000."),
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
        predict("py_conc_010", "Босс: очередь задач", """\
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
                ["[]\nFalse", "[0, 10, 20]\nTrue", "[20, 10, 0]\nFalse"], position=2, topic="conc_queue",
                role="boss", difficulty=4,
                hint="q.join() ждёт, пока для каждого put вызовут task_done. А что сделает None?",
                explanation="q.join() возвращается, когда все три элемента обработаны (task_done) — results уже полон, порядок FIFO. None выводит рабочего из цикла, t.join() дожидается его конца — поток больше не жив.",
                feedback={"[]\nFalse": "q.join() ждёт обработки всех элементов — к print они в results.",
                          "[0, 10, 20]\nTrue": "None завершает цикл рабочего, и t.join() ждёт его конца.",
                          "[20, 10, 0]\nFalse": "Queue — очередь FIFO: элементы выходят в порядке добавления."}),
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
        topic("perf_measure", "Замеры скорости",
              "Ускоряют только то, что измерили: время замеряют часами, `timeit` и профилировщиком.",
              """
              Интуиция о «медленных местах» часто ошибается: программа тратит время совсем не там, где кажется. Поэтому ускорение начинают с замеров.

              ## Порядок работы

              1. Убедиться, что программа работает правильно.
              2. Измерить и найти узкое место.
              3. Ускорить только его.
              4. Измерить снова и сравнить.

              ## Инструменты

              - `time.perf_counter()` — точные часы: засекают до и после, разница — в секундах
              - `timeit.timeit(код, number=N)` — запускает фрагмент N раз и возвращает общее время
              - `python -m timeit "выражение"` — то же из терминала
              - `python -m cProfile -s cumtime файл.py` — сколько раз вызвана каждая функция и сколько времени в ней прошло
              - `tracemalloc` — где программа выделяет память

              ## Почему много запусков

              Один замер искажают другие программы, кэши процессора, сборщик мусора. `timeit` повторяет фрагмент много раз и сглаживает этот шум. Варианты сравнивают одним способом и на одних данных.

              Главный выигрыш почти всегда даёт алгоритм — O(n) вместо O(n²), — а не мелкие приёмы. Как оценить алгоритм — в теме [[algo_complexity|сложность алгоритма]].
              """,
              [("""\
                import time

                start = time.perf_counter()
                total = sum(range(100_000))
                spent = time.perf_counter() - start
                print(total)
                print(type(spent).__name__)""",
                "Разница показаний часов — дробное число секунд"),
               ("""\
                import timeit

                data = list(range(10_000))
                items = set(data)
                t_list = timeit.timeit(
                    lambda: 9_999 in data, number=200)
                t_set = timeit.timeit(
                    lambda: 9_999 in items, number=200)
                print(t_set < t_list)""",
                "Замер подтверждает: множество ищет быстрее списка")],
              [pitfall("Один запуск ничего не доказывает: шум системы легко перекрывает разницу.",
                       bad="t = timeit.timeit(f, number=1)", good="t = timeit.timeit(f, number=1000)"),
               pitfall("time.time() для замеров грубее и может скакнуть при смене системного времени.",
                       bad="start = time.time()", good="start = time.perf_counter()"),
               "Ускорять код, который выполняется редко, вместо узкого места, найденного профилировщиком."]),
        topic("perf_tricks", "Быстрые идиомы и память",
              "Встроенные функции, множества, `join`, генераторы и кэш ускоряют код без смены алгоритма.",
              """
              Когда узкое место найдено, часто хватает простой замены: другой структуры данных или встроенной функции вместо ручного цикла. Эти приёмы дают выигрыш почти всегда.

              ## Скорость

              - Встроенные `sum`, `max`, `sorted`, `any` написаны на C и быстрее ручного цикла.
              - `x in множество` — O(1), а `x in список` — O(n).
              - `"".join(части)` собирает строку за один проход. `s += часть` в цикле может каждый раз копировать всю строку.
              - Неизменные вычисления выносят из тела цикла.
              - Готовые [[std_collections|`Counter`]] и [[std_deque|`deque`]] быстрее самодельных.

              ## Память

              - [[gen_lazy|Генератор]] не хранит элементы: `sum(x * x for x in data)` почти не занимает памяти. Но пройти его можно только один раз.
              - `sys.getsizeof(obj)` — сколько байт занимает сам объект, без вложенных.
              - `__slots__ = ("x", "y")` убирает у объектов словарь `__dict__`: на миллионах объектов это заметная экономия, но новые атрибуты добавить нельзя.

              Если у родительского класса слотов нет, `__dict__` вернётся от него, и экономии не будет.

              ## Кэш

              `@functools.cache` запоминает результат по аргументам: повторный вызов не считает заново ([[rec_memo|запоминание результатов]]). Аргументы должны быть [[g:хешируемый|хешируемыми]] — кортеж, а не список.

              `cache_info()` показывает попадания `hits` и промахи `misses`. `lru_cache(maxsize=N)` хранит только N последних результатов.
              """,
              [("""\
                from functools import cache

                @cache
                def tax(price):
                    print("считаю", price)
                    return price * 0.2

                print(tax(100))
                print(tax(100))
                print(tax.cache_info().hits)""",
                "Второй вызов не печатает «считаю»: ответ взят из кэша"),
               ("""\
                import sys

                nums = [n * n for n in range(10_000)]
                lazy = (n * n for n in range(10_000))
                print(sys.getsizeof(nums) > 10_000)
                print(sys.getsizeof(lazy) < 1_000)
                print(sum(lazy))""",
                "Список хранит все числа, генератор — только своё состояние"),
               ("""\
                class Point:
                    __slots__ = ("x", "y")

                    def __init__(self, x, y):
                        self.x, self.y = x, y

                p = Point(1, 2)
                print(hasattr(p, "__dict__"))
                try:
                    p.z = 3
                except AttributeError:
                    print("новый атрибут нельзя")""",
                "У объекта со слотами нет __dict__ и лишних атрибутов")],
              [pitfall("Функция с @cache не принимает список: TypeError: unhashable type: 'list'. Передайте кортеж.",
                       bad="total([10, 20])", good="total((10, 20))"),
               pitfall("Строка через += в большом цикле может копироваться каждый раз; соберите части через join.",
                       bad='''
                           s = ""
                           for w in words:
                               s += w + " "''',
                       good='s = " ".join(words)'),
               "Кэшировать функцию с побочным эффектом: при попадании в кэш print или запись в файл не выполнятся.",
               "Жертвовать читаемостью ради ускорений, которых не видно в замерах."]),
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
    id="project", title="Программа как проект", description="Модули и пакеты, __main__, argparse, logging, PEP 8",
    icon="🏗️",
    topics=[
        topic("proj_modules", "Свои модули и пакеты",
              "Свой файл `.py` подключают через `import` как модуль, а папка с модулями и `__init__.py` становится пакетом.",
              """
              Когда программа растёт, код раскладывают по файлам: расчёты отдельно, ввод и вывод отдельно. Свой файл подключают тем же `import`, что и [[std_import|модули стандартной библиотеки]].

              ## Как записать

              ```syntax
              # файл prices.py
              def tax(цена):
                  return цена * 1.2

              # файл main.py в той же папке
              import prices
              from prices import tax
              ```

              Имя модуля — имя файла без `.py`. Поэтому файл называют как переменную: `my_tools.py`, а не `my-tools.py`.

              ## Где Python ищет модули

              Папки поиска перечислены в списке `sys.path`. Первой идёт папка запущенного файла, затем стандартная библиотека и установленные пакеты. В примерах файлы создаются кодом, и папку добавляют в `sys.path` вручную.

              ## Импорт выполняет модуль

              При первом импорте код модуля выполняется сверху вниз, а сам модуль запоминается в `sys.modules`. Повторный `import` берёт готовый объект.

              У импортированного модуля `__name__` — его имя, у запущенного файла — `"__main__"`. Код под `if __name__ == "__main__":` при импорте не выполняется. Как на этом строят файл программы — в теме [[proj_structure|Структура программы]].

              ## Пакет и относительный импорт

              Пакет — папка с модулями и файлом `__init__.py`. Этот файл выполняется при импорте пакета. Внутри пакета соседей импортируют с точкой:

              - `from . import prices` — модуль этого же пакета
              - `from .prices import tax` — имя из соседнего модуля
              - `from ..utils import log` — из пакета уровнем выше

              Точка работает только в модуле пакета. Поэтому файл пакета запускают из папки проекта как модуль: `python -m shop.cart`.
              """,
              [("""\
                import sys
                from pathlib import Path

                Path("greet.py").write_text(
                    "def hello(name):\\n"
                    "    return 'Привет, ' + name\\n",
                    encoding="utf-8")
                sys.path.insert(0, str(Path.cwd()))

                import greet
                print(greet.hello("Ада"))""",
                "Файл greet.py стал модулем: import нашёл его через sys.path"),
               ("""\
                import sys
                from pathlib import Path

                Path("units.py").write_text(
                    'print("units:", __name__)\\n'
                    'if __name__ == "__main__":\\n'
                    '    print("демо units")\\n',
                    encoding="utf-8")
                sys.path.insert(0, str(Path.cwd()))

                import units
                print("main:", __name__)""",
                "При импорте __name__ — имя модуля, блок __main__ пропущен"),
               ("""\
                import sys
                from pathlib import Path

                pkg = Path("shop")
                pkg.mkdir()
                (pkg / "prices.py").write_text(
                    "def tax(p):\\n    return p * 1.2\\n")
                (pkg / "__init__.py").write_text(
                    "from .prices import tax\\n")
                sys.path.insert(0, str(Path.cwd()))

                from shop import tax
                print(tax(50))""",
                "__init__.py поднял tax из shop.prices на уровень пакета"),
               ("""\
                print(__name__)
                try:
                    from .prices import tax
                except ImportError as e:
                    print(e)""",
                "У запущенного файла нет пакета: импорт с точкой не работает")],
              [pitfall("Свой файл `random.py` рядом с программой заслоняет модуль стандартной библиотеки, и `random.randint` пропадает.",
                       bad='''
                           # файл random.py
                           import random
                           print(random.randint(1, 6))''',
                       good='''
                           # файл dice.py
                           import random
                           print(random.randint(1, 6))'''),
               pitfall("Дефис в имени файла не даёт его импортировать: `import my-tools` — SyntaxError.",
                       bad="import my-tools", good="import my_tools", syntax_error=True),
               pitfall("Запускать файл пакета как `python shop/cart.py`: импорт с точкой даст `ImportError`. Запускайте `python -m shop.cart` из папки проекта."),
               pitfall("Повторный `import` не перечитывает изменённый файл: модуль уже лежит в `sys.modules`. Перезапустите программу.")]),
        topic("proj_structure", "Структура программы",
              "Программа — набор функций с одной точкой входа `main()`, которая срабатывает только при запуске файла.",
              """
              Скрипт из двадцати строк можно писать сверху вниз. Когда строк сотни, код раскладывают по функциям, а запуск собирают в одном месте. Так программу проще читать, тестировать и подключать к другим.

              ## Шаблон файла

              ```syntax
              \"\"\"Что делает программа.\"\"\"
              import sys

              КОНСТАНТА = значение

              def функция():
                  действия

              def main(argv):
                  действия
                  return 0

              if __name__ == "__main__":
                  sys.exit(main(sys.argv[1:]))
              ```

              Порядок сверху вниз: описание модуля, импорты, константы, функции и классы, точка входа.

              ## Что значит __name__

              Каждый файл `.py` — [[std_import|модуль]]. У запущенного файла `__name__` равен `"__main__"`, а при импорте — имени модуля. Поэтому код под проверкой выполняется при запуске и не выполняется при импорте: функции модуля можно подключать и тестировать.

              ## Код выхода

              `main` возвращает число, а `sys.exit` передаёт его системе: `0` — успех, другое — ошибка. По коду выхода скрипты и сборочные системы понимают, удалась ли программа.

              `sys.argv` — список аргументов запуска, `sys.argv[0]` — имя самого файла. Разбирать аргументы удобнее модулем [[proj_cli_logging|argparse]].

              ## Пакеты и окружение

              - Папка с модулями и файлом `__init__.py` — [[proj_modules|пакет]]: `from shop.cart import Cart`.
              - Зависимости проекта перечисляют в `pyproject.toml`.
              - Ставят их в виртуальное окружение: `python -m venv .venv`, у каждого проекта своё.

              Как оформлять сам код — в теме [[proj_style|PEP 8 и docstring]].
              """,
              [("""\
                def area(w, h):
                    return w * h

                if __name__ == "__main__":
                    print("запуск как программы")
                    print(area(3, 4))""",
                "Файл запущен напрямую, поэтому блок под проверкой выполнился"),
               ("""\
                \"\"\"Считает слова в тексте.\"\"\"

                def count_words(text):
                    return len(text.split())

                def main(argv):
                    if not argv:
                        print("нужен текст")
                        return 1
                    print(count_words(" ".join(argv)))
                    return 0

                if __name__ == "__main__":
                    print("код:", main(["раз", "два три"]))
                    print("код:", main([]))""",
                "main возвращает 0 при успехе и 1, когда текста нет")],
              [pitfall("С \"main\" вместо \"__main__\" условие всегда ложно, и программа молча ничего не делает.",
                       bad='if __name__ == "main":\n    main()',
                       good='if __name__ == "__main__":\n    main()'),
               pitfall("Код на верхнем уровне модуля выполняется при каждом импорте, и его трудно протестировать.",
                       bad='''
                           data = load()
                           report(data)''',
                       good='''
                           def main():
                               report(load())

                           if __name__ == "__main__":
                               main()'''),
               "Называть свой файл как модуль стандартной библиотеки (random.py, json.py): import подхватит ваш файл вместо настоящего."]),
        topic("proj_style", "PEP 8 и docstring",
              "PEP 8 — общий стиль кода Python, а docstring — строка-описание, которую показывает `help()`.",
              """
              Код читают чаще, чем пишут: коллеги, проверяющие, вы сами через полгода. Единый стиль убирает споры о мелочах, и чужой код читается так же легко, как свой.

              ## Имена

              | Что | Как писать |
              |---|---|
              | переменная, функция | {`total_price`} |
              | класс | {`UserAccount`} |
              | константа | {`MAX_RETRIES`} |
              | внутреннее имя | {`_cache`} |

              Функции и переменные пишут строчными через подчёркивание, классы — с заглавной буквы каждого слова. Стиль `getUserName` из Java и JavaScript в Python не используют.

              ## Оформление

              - Отступ — 4 пробела, без табуляции.
              - Пробелы вокруг `=` и операторов, но не у `=` именованного аргумента: `f(x=1)`.
              - Строка — до 79 символов; многие проекты разрешают 99.
              - Две пустые строки между функциями верхнего уровня.
              - Импорты наверху, группами: стандартная библиотека, сторонние, свои.

              Следить за этим вручную не нужно: форматировщики (black, `ruff format`) и линтеры (ruff, flake8) проверяют и правят код сами.

              ## Docstring

              [[func_def|Docstring]] — строка в тройных кавычках первой строкой тела функции, класса или модуля. Первая строка — кратко, что делает код, дальше через пустую строку подробности.

              Docstring хранится в атрибуте `__doc__`, его показывает `help(функция)`. Docstring говорит, что делает функция, а комментарий `#` — почему код написан именно так.
              """,
              [("""\
                def bmi(weight, height):
                    \"\"\"Индекс массы тела: вес в кг, рост в м.\"\"\"
                    return weight / height ** 2

                print(bmi.__doc__)
                print(round(bmi(70, 1.75), 1))""",
                "Docstring хранится в __doc__ — его же покажет help(bmi)"),
               ("""\
                def CalcTotal(Prices,Tax=0.2):
                    return sum(Prices)*(1+Tax)

                def calc_total(prices, tax=0.2):
                    return sum(prices) * (1 + tax)

                print(CalcTotal([10, 20]))
                print(calc_total([10, 20]))""",
                "Результат одинаковый, но второй вариант читается легче")],
              [pitfall("camelCase для функций — стиль Java; в Python имена функций пишут через подчёркивание.",
                       bad="def getUserName(): ...", good="def get_user_name(): ..."),
               pitfall("Комментарий не попадает в __doc__ и help(): описание функции пишут docstring-ом.",
                       bad='''
                           def area(w, h):
                               # Площадь прямоугольника.
                               return w * h''',
                       good='''
                           def area(w, h):
                               """Площадь прямоугольника."""
                               return w * h'''),
               pitfall("По PEP 8 у = именованного аргумента пробелов нет.",
                       bad="connect(timeout = 5)", good="connect(timeout=5)")]),
        topic("proj_cli_logging", "Аргументы командной строки",
              "`argparse` разбирает аргументы командной строки, проверяет их и сам пишет справку `--help`.",
              """
              Программу запускают с настройками: `resize cat.png --width 320`. Разбирать `sys.argv` вручную долго: нужно проверять типы и обязательность, писать справку. Модуль `argparse` делает это по описанию аргументов.

              ## Как записать

              ```syntax
              import argparse

              parser = argparse.ArgumentParser(description="что делает")
              parser.add_argument("имя")
              parser.add_argument("--опция", type=int, default=значение)
              args = parser.parse_args()
              ```

              `parse_args()` читает [[proj_structure|`sys.argv`]]. В тестах ему передают список: `parse_args(["a.txt", "--limit", "5"])`. Значения доступны как атрибуты: `args.limit`.

              ## Параметры add_argument

              - `"file"` — позиционный аргумент, обязательный
              - `"--limit"` — опция, необязательная; `required=True` делает её обязательной
              - `"-v", "--verbose"` — короткое и длинное имя одной опции
              - {`type=int`} — превратить строку в число
              - `default=10` — значение, если опцию не указали
              - `action="store_true"` — флаг без значения: есть — `True`, нет — `False`
              - `nargs="+"` — одно или больше значений списком
              - `choices=[1, 2, 3]` — только перечисленные значения

              ## Ошибки и справка

              Без {`type`} все значения — строки. При неверных аргументах argparse печатает подсказку в stderr и завершает программу через `SystemExit` с кодом 2. Справка `--help` создаётся сама.

              ## Подкоманды

              Как у git: `sub = parser.add_subparsers(dest="command")`, затем `sub.add_parser("add")` — у каждой подкоманды свои аргументы. Имя выбранной подкоманды попадает в `args.command`.

              Диагностику работы программы пишут не `print`, а [[proj_logging|logging]].
              """,
              [("""\
                import argparse

                parser = argparse.ArgumentParser()
                parser.add_argument("image")
                parser.add_argument("--width", type=int,
                                    default=800)
                args = parser.parse_args(["cat.png"])
                print(args.image)
                print(args.width)""",
                "Опцию не передали — сработал default"),
               ("""\
                import argparse

                p = argparse.ArgumentParser()
                p.add_argument("files", nargs="+")
                p.add_argument("-q", "--quiet",
                               action="store_true")
                args = p.parse_args(["a.txt", "b.txt", "-q"])
                print(args.files)
                print(args.quiet)""",
                "nargs собрал имена в список, флаг -q дал True"),
               ("""\
                import argparse

                p = argparse.ArgumentParser(prog="todo")
                sub = p.add_subparsers(dest="command")
                add = sub.add_parser("add")
                add.add_argument("title")
                sub.add_parser("list")

                args = p.parse_args(["add", "купить хлеб"])
                print(args.command)
                print(args.title)""",
                "Подкоманда add со своим аргументом title")],
              [pitfall("Без type=int значение — строка: \"3\" * 2 даст \"33\".",
                       bad='p.add_argument("--times")', good='p.add_argument("--times", type=int)'),
               pitfall("Имя без -- — позиционный аргумент: он обязателен, даже если указан default.",
                       bad='p.add_argument("limit", default=10)', good='p.add_argument("--limit", default=10)'),
               pitfall("Дефис в имени опции становится подчёркиванием: --dry-run читают как args.dry_run.",
                       bad="if args.dry-run:\n    return", good="if args.dry_run:\n    return")]),
        topic("proj_logging", "logging в проекте",
              "В программе из нескольких модулей logging настраивают один раз, а каждый модуль пишет в свой логгер.",
              """
              Основы — уровни, `basicConfig`, формат — в теме [[test_logging|logging вместо print]]. Когда модулей много, нужен порядок: кто настраивает вывод, кто пишет сообщения и как заглушить один шумный модуль.

              ## Как записать

              ```syntax
              # в каждом модуле
              log = logging.getLogger(__name__)

              # один раз в точке входа
              def main():
                  logging.basicConfig(level=logging.INFO)
              ```

              `getLogger` с одним и тем же именем всегда возвращает один и тот же объект. Имя `__name__` совпадает с именем модуля, поэтому по сообщению видно, откуда оно пришло.

              ## Дерево логгеров

              Логгеры образуют дерево по точкам в имени: `shop.db` — потомок `shop`, а все вместе — потомки корневого логгера. Сообщение потомка доходит до вывода, который настроил `basicConfig` у корня.

              Уровень можно задать отдельной ветке: `logging.getLogger("shop.db").setLevel(logging.WARNING)` заглушит только её.

              ## Аргументы — отдельно

              `log.info("файл %s", name)` подставляет аргументы, только если сообщение действительно пишется. f-строку Python собирает всегда, даже когда уровень выключен.

              ## print или logging

              `print` — для результата программы: его читает пользователь или следующая программа. `logging` — для диагностики: что происходило и где сломалось.
              """,
              [("""\
                import logging
                import sys

                logging.basicConfig(
                    stream=sys.stdout,
                    level=logging.INFO,
                    format="%(name)s: %(message)s",
                    force=True)
                db = logging.getLogger("shop.db")
                api = logging.getLogger("shop.api")
                db.info("подключение")
                api.info("GET /cart")""",
                "Имя логгера в каждой строке показывает, откуда сообщение"),
               ("""\
                import logging
                import sys

                logging.basicConfig(
                    stream=sys.stdout,
                    level=logging.INFO,
                    format="%(name)s: %(message)s",
                    force=True)
                logging.getLogger("shop.db").setLevel(
                    logging.WARNING)
                db = logging.getLogger("shop.db")
                db.info("запрос за 1 мс")
                db.warning("запрос за 3 с")
                logging.getLogger("shop.api").info("GET /")""",
                "Ветку shop.db заглушили до WARNING, shop.api пишет INFO"),
               ("""\
                import logging
                import sys

                logging.basicConfig(stream=sys.stdout,
                                    level=logging.INFO,
                                    force=True)
                log = logging.getLogger("calc")

                class Report:
                    def __str__(self):
                        print("(собираю отчёт)")
                        return "отчёт"

                log.debug("данные: %s", Report())
                log.info("данные: %s", Report())""",
                "Для выключенного DEBUG строка не собиралась: __str__ не вызван")],
              [pitfall("f-строка собирается всегда; с %s строка форматируется, только если сообщение пишется.",
                       bad='log.debug(f"данные: {data}")', good='log.debug("данные: %s", data)'),
               pitfall("basicConfig срабатывает один раз: вызовы в модулях конфликтуют. Настраивайте в точке входа.",
                       bad="logging.basicConfig(level=logging.DEBUG)",
                       good="log = logging.getLogger(__name__)"),
               pitfall("Общее имя вроде \"log\" во всех модулях лишает дерева: ни источник, ни уровень по модулю не задать.",
                       bad='log = logging.getLogger("log")', good="log = logging.getLogger(__name__)")]),
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
                position=3, topic="proj_logging", role="practice", difficulty=3,
                hint="У логгера app.db свой порог. А что возвращает getLogger при повторном вызове с тем же именем?",
                explanation="Для app.db порог поднят до WARNING — его info отсекается. app.api наследует порог INFO от корня. getLogger с тем же именем возвращает тот же объект — поэтому в каждом модуле пишут getLogger(__name__) и настраивают уровни по именам.",
                feedback={"app.db|INFO|подключение\napp.db|WARNING|медленный запрос\napp.api|INFO|GET /users\nTrue": "db.setLevel(WARNING) отсекает info этого логгера.",
                          "app.db|WARNING|медленный запрос\nTrue": "Порог WARNING задан только для app.db, app.api пишет INFO.",
                          "app.db|WARNING|медленный запрос\napp.api|INFO|GET /users\nFalse": "getLogger с одним именем всегда возвращает один и тот же логгер."}),
        multi("py_proj_006", "Имена по PEP 8", "Какие имена записаны по PEP 8?",
              list(PEP8_NAMES), [i for i, ok in enumerate(PEP8_NAMES.values()) if ok],
              check=lambda option: PEP8_NAMES[option], topic="proj_style",
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
                position=1, topic="proj_style", role="practice",
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
        predict("py_proj_012", "Модуль загружается один раз", """\
                import sys
                from pathlib import Path

                Path("helper.py").write_text(
                    'print("helper загружен")\\n'
                    'def run():\\n'
                    '    print("helper.run")\\n'
                    'if __name__ == "__main__":\\n'
                    '    run()\\n',
                    encoding="utf-8")
                sys.path.insert(0, str(Path.cwd()))

                print("старт")
                import helper
                import helper
                helper.run()""",
                ["старт\nhelper загружен\nhelper загружен\nhelper.run",
                 "старт\nhelper загружен\nhelper.run\nhelper.run",
                 "helper загружен\nстарт\nhelper.run"],
                position=3, topic="proj_modules", difficulty=2,
                hint="Сколько раз выполняется код модуля при двух import? Чему равен __name__ у импортированного модуля?",
                explanation="Код модуля выполняется при первом import — после «старт». Второй import берёт модуль из sys.modules и ничего не печатает. Внутри helper __name__ равно \"helper\", поэтому run() под проверкой не вызывается — его вызывает только main.",
                feedback={"старт\nhelper загружен\nhelper загружен\nhelper.run": "Повторный import не выполняет модуль заново: он уже в sys.modules.",
                          "старт\nhelper загружен\nhelper.run\nhelper.run": "При импорте __name__ — \"helper\", блок под __main__ не выполняется.",
                          "helper загружен\nстарт\nhelper.run": "import выполняется там, где стоит, — после print(\"старт\")."}),
        fix_line("py_proj_013", "Импорт с точкой", """\
                 import sys
                 from pathlib import Path

                 pkg = Path("store")
                 pkg.mkdir()
                 (pkg / "__init__.py").write_text("")
                 (pkg / "prices.py").write_text(
                     "def tax(p):\\n    return p * 1.2\\n")
                 sys.path.insert(0, str(Path.cwd()))

                 from .prices import tax
                 print(tax(100))""", 10,
                 ["from store.prices import tax"],
                 expect_error="ImportError", topic="proj_modules", role="practice", difficulty=2,
                 hint="Запущенный файл — модуль __main__, он не лежит ни в каком пакете. Куда тогда указывает точка?",
                 explanation="Импорт с точкой ищет соседа в пакете текущего модуля, а у запущенного файла пакета нет: ImportError: attempted relative import with no known parent package. Из главного файла пишут полный путь: from store.prices import tax."),
        categorize("py_proj_014", "Что выполнится при импорте", "Файл tools.py импортируют командой import tools. Что из него выполнится?",
                   ["Выполнится при импорте", "Не выполнится"],
                   [('print("загрузка") на верхнем уровне', 0),
                    ("RATE = 0.2 на верхнем уровне", 0),
                    ("import json в начале файла", 0),
                    ("тело функции def report()", 1, "def только создаёт функцию, тело выполнится при вызове."),
                    ('код под if __name__ == "__main__":', 1, "При импорте __name__ равно \"tools\", условие ложно."),
                    ("тело класса class Cart:", 0, "Тело класса выполняется сразу, когда Python доходит до class: так создаются его атрибуты и методы.")],
                   topic="proj_modules", difficulty=3,
                   hint="Импорт выполняет модуль сверху вниз, как при запуске. Что из этого откладывает выполнение?",
                   explanation="При импорте выполняется весь верхний уровень модуля: присваивания, import, print, создание функций и классов вместе с телом класса. Тело функции ждёт вызова, а блок под проверкой __name__ ждёт запуска файла напрямую."),
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
