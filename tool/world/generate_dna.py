"""Author a finite DNA curriculum and compute/verify its outputs in CPython.
Each topic contains twenty different concepts, not numeric variants of a template.
"""
from pathlib import Path
import ast
import contextlib
import io
import json

lessons = {}
def add(topic, concept, code, explanation, options=(), correct=None):
    executable = code.replace('___', correct) if correct else code
    def run(source):
        out=io.StringIO()
        with contextlib.redirect_stdout(out): exec(compile(source,'<dna>','exec'), {})
        return out.getvalue().rstrip('\n')
    output=run(executable)
    assert output and output.strip()==output,concept
    if correct:
        assert correct in options
        for option in options:
            if option==correct:continue
            try: wrong=run(code.replace('___',option))
            except Exception: continue
            assert wrong!=output,(concept,option)
    lessons.setdefault(topic,[]).append(dict(concept=concept,code=code,answer=correct or output,
        explanation=explanation,options=list(options),verificationOutput=output if correct else None))

T='Условия'
add(T,'Сравнение чисел','temperature = 7\nif temperature < 0:\n    print("freeze")\nelse:\n    print("warm")','Ветка if выполняется только при отрицательной температуре.')
add(T,'Порядок веток elif','score = 75\nif score >= 90:\n    print("A")\nelif score >= 60:\n    print("B")\nelse:\n    print("C")','После первой истинной ветки остальные ветки не выполняются.')
add(T,'Обе границы диапазона','age = 18\nprint(___)','Для включения обеих границ нужны сравнения >= и <=, соединённые and.',('age > 18 and age < 65','age >= 18 and age <= 65','age < 18 or age > 65'),'age >= 18 and age <= 65')
add(T,'Хотя бы одно условие','is_admin = False\nis_owner = True\nprint(is_admin or is_owner)','or истинен, когда истинно хотя бы одно из условий.')
add(T,'Отрицание условия','active = False\nif not active:\n    print("start")','not меняет логическое значение на противоположное.')
add(T,'Принадлежность коллекции','role = "editor"\nallowed = {"admin", "editor"}\nprint(role ___ allowed)','in проверяет наличие элемента в коллекции.',('in','not in','=='),'in')
add(T,'Отсутствие элемента','blocked = ["root", "guest"]\nprint("anna" not in blocked)','not in истинен, если элемента нет в коллекции.')
add(T,'Истинность пустого списка','items = []\nprint("empty" if not items else "filled")','Пустой список имеет ложное логическое значение.')
add(T,'Короткое замыкание and','denominator = 0\nprint(denominator != 0 and 10 / denominator > 1)','При ложной левой части and правая часть не вычисляется, деления на ноль нет.')
add(T,'Значение по умолчанию через or','name = ""\nprint(name or "anonymous")','or возвращает первый истинный операнд или последний, если истинных нет.')
add(T,'Условное выражение','balance = -3\nstatus = "debt" if balance < 0 else "ok"\nprint(status)','Условное выражение выбирает одно из двух значений.')
add(T,'Цепочка сравнений','x = 5\nprint(2 < x <= 5)','Цепочка проверяет сразу обе границы, включая правую.')
add(T,'Вложенное условие','logged_in = True\ncredits = 0\nif logged_in:\n    if credits > 0:\n        print("buy")\n    else:\n        print("refill")','Внутренний else относится к проверке credits, а не к logged_in.')
add(T,'Два независимых if','x = 4\nif x > 0:\n    print("positive")\nif x % 2 == 0:\n    print("even")','Независимые if могут выполниться оба. Запиши вывод на двух строках.')
add(T,'Приоритет and и or','print(False or True and False)','and вычисляется раньше or.')
add(T,'Скобки в логике','print((False or True) and not False)','Скобки задают порядок вычисления, затем применяется not.')
add(T,'Проверка None','value = 0\nprint(value is None)','Ноль и None — разные значения; is None проверяет именно отсутствие значения.')
add(T,'Безопасное условие','items = []\nif ___:\n    print(items[0])\nelse:\n    print("empty")','Сначала проверяется непустота списка, затем читается первый элемент.',('items[0]','items','not items'),'items')
add(T,'Чётность и остаток','n = 9\nif n % 2 == 0:\n    print("even")\nelse:\n    print("odd")','Остаток от деления нечётного числа на два равен единице.')
add(T,'Структурное сопоставление','command = "stop"\nmatch command:\n    case "start":\n        print("running")\n    case "stop":\n        print("paused")\n    case _:\n        print("unknown")','match выбирает подходящий образец; _ используется как запасной вариант.')

T='Циклы'
add(T,'Правая граница range','print(list(range(1, 5)))','Правая граница range не включается.')
add(T,'Шаг диапазона','print(list(range(0, 8, 3)))','Третий аргумент задаёт шаг, а не число элементов.')
add(T,'Обратный обход','print(list(range(5, 0, -2)))','Отрицательный шаг уменьшает значение; правая граница также исключена.')
add(T,'Накопление суммы','total = 0\nfor n in [2, 4, 6]:\n    ___\nprint(total)','+= накапливает сумму; обычное присваивание заменяет её.',('total = n','total += n','total -= n'),'total += n')
add(T,'Накопление произведения','product = 1\nfor n in [2, 3, 4]:\n    product *= n\nprint(product)','Для произведения начальное значение равно единице.')
add(T,'Условие while','n = 3\nwhile n > 0:\n    print(n)\n    n -= 1','while проверяет условие перед каждой итерацией. Запиши вывод построчно.')
add(T,'Обновление счётчика','n = 1\nsteps = 0\nwhile n < 8:\n    n *= 2\n    steps += 1\nprint(steps)','Счётчик n удваивается: 1, 2, 4, 8; тело выполнится три раза.')
add(T,'Досрочный выход break','found = None\nfor n in [3, 8, 10]:\n    if n % 2 == 0:\n        found = n\n        ___\nprint(found)','break завершает цикл на первом найденном элементе.',('continue','break','pass'),'break')
add(T,'Пропуск continue','result = []\nfor n in [1, 2, 3, 4]:\n    if n % 2 == 0:\n        continue\n    result.append(n)\nprint(result)','continue пропускает остаток текущей итерации.')
add(T,'Цикл с else','for n in [1, 3, 5]:\n    if n % 2 == 0:\n        break\nelse:\n    print("not found")','else цикла выполняется, если цикл завершился без break.')
add(T,'enumerate и начальный номер','result = []\nfor i, word in enumerate(["a", "b"], start=1):\n    result.append(f"{i}:{word}")\nprint(",".join(result))','enumerate выдаёт номер и значение; start задаёт первый номер.')
add(T,'Совместный обход zip','print(list(zip([1, 2, 3], ["a", "b"])))','zip без strict заканчивается вместе с самой короткой последовательностью.')
add(T,'Вложенные циклы','pairs = []\nfor a in [1, 2]:\n    for b in [3, 4]:\n        pairs.append(a * b)\nprint(pairs)','Для каждого a внутренний цикл полностью перебирает значения b.')
add(T,'Обход словаря','scores = {"a": 2, "b": 3}\nresult = []\nfor key, value in scores.items():\n    result.append(key * value)\nprint(result)','items возвращает пары ключ–значение; строки умножаются на целое число.')
add(T,'Включение с фильтром','nums = [1, 2, 3, 4]\nprint([n * n for n in nums if n > 2])','Фильтр проверяется до добавления выражения в новый список.')
add(T,'Счётчик подходящих элементов','count = 0\nfor word in ["a", "bee", "cat", "d"]:\n    if len(word) == 3:\n        count += 1\nprint(count)','Счётчик увеличивается только для слов заданной длины.')
add(T,'Обход строки','vowels = "aeiou"\nprint(sum(1 for letter in "hello" if letter in vowels))','Строка перебирается по символам, генератор выдаёт по единице за гласную.')
add(T,'Индекс первого совпадения','values = [8, 3, 8]\nfor i in range(len(values)):\n    if values[i] == 3:\n        print(i)\n        break','Печатается индекс первого совпадения, а не само значение.')
add(T,'Пустой диапазон','visits = 0\nfor n in range(5, 2):\n    visits += 1\nprint(visits)','При положительном шаге начало больше конца: тело не выполняется.')
add(T,'Проверка всех элементов','values = [2, 3, 6]\nprint(___(n % 2 == 0 for n in values))','all проверяет, что условие верно для каждого элемента.',('any','all','sum'),'all')

T='Индексы'
add(T,'Нумерация с нуля','items = [10, 20, 30]\nprint(items[1])','Индекс 1 указывает на второй элемент.')
add(T,'Отрицательный индекс','items = [10, 20, 30]\nprint(items[-2])','Отрицательные индексы считают элементы с конца.')
add(T,'Срез без правой границы','items = [0, 1, 2, 3, 4]\nprint(items[1:4])','Срез включает левую границу и исключает правую.')
add(T,'Шаг среза','items = [0, 1, 2, 3, 4, 5]\nprint(items[::2])','Шаг 2 выбирает каждый второй элемент, начиная с индекса 0.')
add(T,'Разворот срезом','text = "python"\nprint(text[___])','Отрицательный шаг среза меняет направление обхода.',('::1','::-1','1:3'),'::-1')
add(T,'Выход среза за границы','items = [1, 2, 3]\nprint(items[:20])','Срез обрезается по длине последовательности и не вызывает IndexError.')
add(T,'Вложенный список','grid = [[1, 2], [3, 4]]\nprint(grid[1][0])','Сначала выбирается строка, затем элемент внутри неё.')
add(T,'Словарь с ключом','user = {"name": "Ada", "age": 30}\nprint(user["name"])','Словарь читается по ключу, а не по порядковому номеру.')
add(T,'get со значением по умолчанию','settings = {"theme": "dark"}\nresult = settings.___("language", "ru")\nprint(result, sorted(settings))','get позволяет прочитать отсутствующий ключ с запасным значением.',('__getitem__','get','setdefault'),'get')
add(T,'Индекс в строке','text = "code"\nprint(text[0] + text[-1])','Индексы строк возвращают односимвольные строки.')
add(T,'Замена элемента','values = [1, 2, 3]\nvalues[1] = 9\nprint(values)','Присваивание по индексу заменяет один элемент изменяемого списка.')
add(T,'Замена среза','values = [1, 2, 3, 4]\nvalues[1:3] = [8]\nprint(values)','При замене среза длина списка может измениться.')
add(T,'Удаление по индексу','values = [5, 6, 7]\nprint(values.pop(1))\nprint(values)','pop возвращает удалённый элемент; затем список становится короче.')
add(T,'Копия и общий объект','a = [1, 2]\nb = a[:]\nb[0] = 9\nprint(a)','Полный срез создаёт отдельный список верхнего уровня.')
add(T,'Вложенная поверхностная копия','a = [[1], [2]]\nb = a[:]\nb[0].append(3)\nprint(a)','Вложенные списки остаются общими при поверхностном копировании.')
add(T,'Поиск позиции index','values = [4, 7, 4]\nprint(values.index(4))','index возвращает позицию первого совпадения.')
add(T,'Вложенные словарь и список','data = {"users": [{"name": "Ada"}, {"name": "Lin"}]}\nprint(data["users"][1]["name"])','Доступ выполняется последовательно: ключ, индекс, ключ.')
add(T,'Распаковка последовательности','first, *middle, last = [1, 2, 3, 4]\nprint(middle)','Звёздочка при распаковке собирает промежуточные элементы в список.')
add(T,'Безопасный последний элемент','values = []\nprint(values[-1] if values else "empty")','Проверка непустоты защищает обращение по индексу.')
add(T,'Правильная граница индекса','items = [10, 20, 30]\nindex = 2\nprint(0 <= index ___ len(items))','Допустимый индекс строго меньше длины списка.',('==','<','>'),'<')

T='Типы данных'
add(T,'Строка и целое число','value = "12"\nprint(int(value) + 3)','int преобразует числовую строку перед сложением.')
add(T,'Сложение или склейка','print("12" + "3")','Плюс для строк выполняет конкатенацию.')
add(T,'Тип результата деления','print(type(8 / 2).__name__)','Обычное деление / возвращает float даже при целом результате.')
add(T,'Целочисленное деление','print(7 // 2)','// округляет результат вниз до целого значения.')
add(T,'Остаток от деления','print(17 % 5)','Остаток — часть числа после целочисленного деления.')
add(T,'Логическое значение строки','print(bool("False"))','Любая непустая строка истинна; текст False не меняет это правило.')
add(T,'Пустые значения','print(bool(0), bool([]), bool(""))','Ноль и пустые коллекции имеют ложное логическое значение.')
add(T,'Преобразование дробного числа','print(int(-3.9))','int отбрасывает дробную часть по направлению к нулю.')
add(T,'Число с плавающей точкой из строки','price = "2.5"\nprint(___(price) * 2)','float читает десятичную дробь из строки.',('int','float','str'),'float')
add(T,'Формат двух знаков','value = 3.5\nprint(f"{value:.2f}")','Формат .2f сохраняет два знака после точки.')
add(T,'Список из строки','print(list("abc"))','list создаёт список символов при обходе строки.')
add(T,'Неизменяемый кортеж','point = (3, 4)\nprint(type(point).__name__, len(point))','Кортеж хранит упорядоченные значения и не меняет элементы на месте.')
add(T,'Уникальные значения множества','items = [1, 1, 2, 3, 3]\nprint(len(set(items)))','Множество удаляет дубликаты; считаем уникальные значения.')
add(T,'Конструктор словаря','pairs = [("a", 1), ("b", 2)]\nprint(dict(pairs)["b"])','dict создаёт соответствие из пар ключ–значение.')
add(T,'Изменяемость списка','a = [1]\nb = a\nb.append(2)\nprint(a)','Присваивание ссылки не создаёт новый список.')
add(T,'None как отдельный тип','print(type(None).__name__)','None является единственным значением типа NoneType.')
add(T,'bool участвует в арифметике','print(True + True + False)','Логические значения ведут себя как 1 и 0 в арифметике.')
add(T,'Проверка типа isinstance','value = 5\nprint(___(value, int))','isinstance проверяет принадлежность значения указанному типу.',('type','isinstance','issubclass'),'isinstance')
add(T,'Преобразование в строку','value = 42\nprint("id=" + str(value))','Число нужно преобразовать в строку для конкатенации.')
add(T,'Разница равенства и типа','print(1 == 1.0, type(1) == type(1.0))','Равные числовые значения могут принадлежать разным типам.')

T='Функции'
add(T,'Аргумент и return','def double(x):\n    return x * 2\nprint(double(6))','Аргумент подставляется вместо параметра, return возвращает результат.')
add(T,'Отсутствие return','def square(x):\n    x * x\nprint(square(4))','Вычисление без return не передаёт результат; функция возвращает None.')
add(T,'Значение аргумента по умолчанию','def greet(name="guest"):\n    return "Hi " + name\nprint(greet())','Если аргумент не передан, используется значение по умолчанию.')
add(T,'Именованные аргументы','def subtract(a, b):\n    return a - b\nprint(subtract(b=3, a=10))','Именованные аргументы связываются с параметрами по имени, а не позиции.')
add(T,'Несколько возвращаемых значений','def bounds():\n    return 2, 8\nlow, high = bounds()\nprint(high - low)','Несколько значений возвращаются кортежем и могут быть распакованы.')
add(T,'Ранний выход','def label(n):\n    if n < 0:\n        return "negative"\n    return "other"\nprint(label(-1))','После return дальнейшие строки функции не выполняются.')
add(T,'Локальная область видимости','x = 10\ndef update():\n    x = 3\n    return x\nprint(update(), x)','Локальный x не заменяет внешнюю переменную.')
add(T,'Параметры args','def total(*numbers):\n    return sum(numbers)\nprint(total(1, 2, 3))','*args собирает позиционные аргументы в кортеж.')
add(T,'Параметры kwargs','def get_mode(**options):\n    return options.get("mode", "safe")\nprint(get_mode(mode="fast"))','**kwargs собирает именованные аргументы в словарь.')
add(T,'Аргумент только по имени','def scale(x, *, factor=2):\n    return x * factor\nprint(scale(3, factor=4))','После * параметр передаётся только по имени.')
add(T,'Композиция вызовов','def inc(x):\n    return x + 1\nprint(inc(inc(3)))','Сначала вычисляется внутренний вызов, затем внешний.')
add(T,'Короткая lambda','triple = lambda x: x * 3\nprint(triple(4))','lambda возвращает результат своего единственного выражения.')
add(T,'Функция как аргумент','def apply(fn, value):\n    return fn(value)\nprint(apply(abs, -7))','Функции являются значениями и могут передаваться другим функциям.')
add(T,'Замыкание','def make_adder(n):\n    def add(x):\n        return x + n\n    return add\nprint(make_adder(5)(2))','Внутренняя функция сохраняет доступ к n внешнего вызова.')
add(T,'Базовый случай рекурсии','def factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n - 1)\nprint(factorial(4))','Базовый случай останавливает рекурсию, результаты возвращаются по цепочке.')
add(T,'Изменяемый аргумент по умолчанию','def collect(x, items=[]):\n    items.append(x)\n    return items\ncollect(1)\nprint(collect(2))','Значение по умолчанию создаётся один раз и сохраняется между вызовами.')
add(T,'Правильный возврат результата','def add(a, b):\n    ___\nprint(add(2, 3))','return возвращает сумму; print только печатает её и сам возвращает None.',('print(a + b)','return a - b','return a + b'),'return a + b')
add(T,'Распаковка аргументов','def multiply(a, b):\n    return a * b\nvalues = [3, 5]\nprint(multiply(*values))','* перед списком распределяет его элементы по параметрам вызова.')
add(T,'Генератор вместо обычного return','def values():\n    yield 2\n    yield 4\nprint(list(values()))','yield выдаёт значения по одному, сохраняя состояние генератора.')
add(T,'Условие внутри функции','def is_even(n):\n    return ___\nprint(is_even(7))','Остаток равен нулю только для чётного числа.',('n % 2 != 0','n % 2 == 0','n > 0'),'n % 2 == 0')

# Assert the curriculum is authored once and contains no exact duplicate programs.
assert set(lessons)=={'Условия','Циклы','Индексы','Типы данных','Функции'}
assert all(len(v)==20 for v in lessons.values())
for topic, items in lessons.items():
    assert len({x['concept'] for x in items})==20,topic
    assert len({x['code'] for x in items})==20,topic

def dart(value):
    return json.dumps(value,ensure_ascii=False).replace('$','\\$')
lines=["part of 'world_challenge.dart';",'', '// Generated by tool/world/generate_dna.py; outputs verified with CPython.',
    'abstract final class DnaCurriculum {', '  static const revision = 2;',
    '  static int count(String category) => _lessons[category]?.length ?? 0;',
    '  static WorldChallenge at(String category, int index, String id) {',
    "    final lessons = _lessons[category];", "    if (lessons == null || index < 0 || index >= lessons.length) {",
    "      throw RangeError('DNA curriculum exhausted or unknown topic');",'    }',
    '    final lesson = lessons[index];', '    return WorldChallenge(id: id, title: lesson.title, code: lesson.code,',
    '      prompt: lesson.prompt, answer: lesson.answer, explanation: lesson.explanation,',
    '      category: category, options: lesson.options, verificationOutput: lesson.verificationOutput);',
    '  }', '  static const _lessons = <String, List<WorldChallenge>>{']
for topic,items in lessons.items():
    lines.append(f'    {dart(topic)}: [')
    for item in items:
        prompt=('Выбери фрагмент для пропуска, чтобы программа вывела:\n' + item['verificationOutput'] if item['options'] else
            ('Запиши вывод программы на отдельных строках, без кавычек вокруг строк.' if '\n' in item['answer'] else
             'Что напечатает программа? Введи точный вывод без внешних кавычек.'))
        lines.append('      WorldChallenge(')
        fields=dict(id='',title=item['concept'],code=item['code'],prompt=prompt,answer=item['answer'],
            explanation=item['explanation'],category=topic,options=item['options'],verificationOutput=item['verificationOutput'])
        for key,value in fields.items():
            if value is None:continue
            lines.append(f'        {key}: {dart(value)},')
        lines.append('      ),')
    lines.append('    ],')
lines.extend(['  };','}'])
out=Path(__file__).resolve().parents[2]/'lib/features/world/domain/dna_curriculum.dart'
content='\n'.join(lines)+'\n'
import sys
if '--check' in sys.argv:
    assert out.read_text()==content, 'Regenerate DNA curriculum'
else:
    out.write_text(content)
print('Authored and CPython-verified 100 DNA lessons across 5 topics')
