"""Модули 22–26: классы и объекты, наследование, магические методы,
свойства и методы класса, dataclasses и enum."""
from bclib import choice, fill, match, multi, order, predict, bug, typed, topic, task, run, pitfall


def runs(code):
    return run(code).ok


def result_of(code):
    result = run(code)
    return result.out.strip() if result.ok else result.error


MODULES = []

# ------------------------------------------------------------------ classes
MODULES.append(dict(
    id="classes", title="Классы и объекты", description="class, __init__, self", icon="🏗️",
    topics=[
        topic("oop_class", "Класс, объект, self",
              "Класс — шаблон, по которому создаются объекты: он описывает их данные и действия.",
              """
              Программа часто работает со множеством похожих вещей: игроки, заказы, товары. У каждой есть данные (имя, баланс) и действия (пополнить, списать). Класс собирает данные и действия в одно целое, и их не приходится носить по разным словарям и функциям.

              ## Как записать

              ```syntax
              class ИмяКласса:
                  def __init__(self, параметры):
                      self.атрибут = значение

                  def метод(self, параметры):
                      действия
              ```

              - Имя класса пишут с заглавной буквы: `Player`, `Order`.
              - `__init__` настраивает новый объект. Python вызывает его сам.
              - `self` — первый параметр каждого метода.

              ## Как создаётся объект

              Объект создают вызовом класса, как функции: `Player("Ада")`. Python при этом:

              1. создаёт пустой объект;
              2. вызывает `__init__`, передав объект в `self`, а `"Ада"` — в следующий параметр;
              3. возвращает готовый объект.

              Сам `__init__` ничего не возвращает: он только заполняет объект.

              ## Атрибуты и методы

              Атрибут — переменная внутри объекта. Присваивание `self.name = name` создаёт его. У каждого объекта свои значения атрибутов. Значения, общие для всех объектов, — это [[oop_class_attrs|атрибуты класса]].

              Метод — функция внутри класса. При вызове `p.heal(10)` Python сам передаёт `p` первым аргументом: это то же, что `Player.heal(p, 10)`.

              Внутри метода к атрибутам обращаются только через `self`. Просто `name` — это обычная переменная, а не атрибут объекта.

              По умолчанию `print(p)` покажет что-то вроде `<__main__.Player object at 0x…>`. Понятный текст задают методом [[dunder_str|`__str__`]].
              """,
              [("""\
                class Player:
                    def __init__(self, name):
                        self.name = name
                        self.hp = 100

                p = Player("Ада")
                print(p.name)
                print(p.hp)""",
                "Объект хранит свои атрибуты: имя из вызова и hp = 100"),
               ("""\
                class Player:
                    def __init__(self, name):
                        self.name = name
                        self.hp = 100

                    def hit(self, damage):
                        self.hp -= damage

                a = Player("Ада")
                b = Player("Боб")
                a.hit(30)
                print(a.hp)
                print(b.hp)""",
                "У каждого объекта свои данные: урон получил только a"),
               ("""\
                class Lamp:
                    def __init__(self):
                        self.on = False

                    def switch(self):
                        self.on = not self.on

                lamp = Lamp()
                lamp.switch()
                print(lamp.on)
                Lamp.switch(lamp)
                print(lamp.on)""",
                "lamp.switch() и Lamp.switch(lamp) — один и тот же вызов"),
               ("""\
                class Bell:
                    def ring():
                        return "дзинь"

                try:
                    Bell().ring()
                except TypeError as e:
                    print(e)""",
                "Метод без self: Python передал объект, а принять его некуда")],
              [pitfall("Метод без `self`: `TypeError: Bell.ring() takes 0 positional arguments but 1 was given`.",
                       bad='''
                           def ring():
                               return "дзинь"''',
                       good='''
                           def ring(self):
                               return "дзинь"'''),
               pitfall("Без `self.` Python ищет обычную переменную: будет `NameError` или чужое значение.",
                       bad='return name + ": гав"', good='return self.name + ": гав"'),
               pitfall("Класс без скобок не создаёт объект: в `p` окажется сам класс.",
                       bad="p = Player", good='p = Player("Ада")'),
               pitfall("`return self` в `__init__` даёт `TypeError: __init__() should return None`.",
                       bad='''
                           def __init__(self, name):
                               self.name = name
                               return self''',
                       good='''
                           def __init__(self, name):
                               self.name = name''')]),
        topic("oop_class_attrs", "Атрибуты класса и объекта",
              "Атрибут класса один на все объекты, а атрибут объекта (`self.x`) у каждого объекта свой.",
              """
              Некоторые значения должны быть общими для всех объектов: ставка налога, число созданных заказов, настройки по умолчанию. Такое значение объявляют прямо в теле класса — это атрибут класса.

              ## Как записать

              ```syntax
              class ИмяКласса:
                  атрибут_класса = значение

                  def __init__(self, параметр):
                      self.атрибут_объекта = параметр
              ```

              ## Как Python ищет атрибут

              Для записи `obj.x` Python:

              1. смотрит в атрибуты самого объекта;
              2. если там нет — в атрибуты класса;
              3. если нет и там — выбрасывает `AttributeError`.

              Поэтому объект видит атрибут класса, пока у него нет своего с тем же именем.

              ## Чтение и запись — разные вещи

              Чтение `obj.x` найдёт атрибут класса. Присваивание `obj.x = 3` всегда создаёт атрибут объекта: он закрывает атрибут класса только для этого объекта. Общее значение меняют через класс: `ИмяКласса.x = 3`.

              По той же причине `self.count += 1` не меняет счётчик класса. Справа читается атрибут класса, а результат записывается в новый атрибут объекта.

              ## Список в теле класса

              Список, объявленный в теле класса, — один на все объекты. `self.items.append(...)` ничего не присваивает, а меняет этот общий [[list_mutable|изменяемый]] список, и изменение видят все. Свой список каждому объекту создают в `__init__`: {`self.items = []`}.
              """,
              [("""\
                class Order:
                    tax = 20

                    def __init__(self, price):
                        self.price = price

                    def total(self):
                        k = 100 + self.tax
                        return self.price * k // 100

                a = Order(500)
                print(a.total())
                Order.tax = 10
                print(a.total())""",
                "Ставку поменяли через класс — новую ставку видит и объект a"),
               ("""\
                class Theme:
                    color = "светлая"

                a = Theme()
                b = Theme()
                a.color = "тёмная"
                print(a.color, b.color)
                print(Theme.color)""",
                "Присваивание через a закрыло атрибут класса только у a"),
               ("""\
                class Backpack:
                    def __init__(self):
                        self.things = []

                a = Backpack()
                b = Backpack()
                a.things.append("фонарь")
                print(a.things)
                print(b.things)""",
                "Список создан в __init__ — у каждого рюкзака свой")],
              [pitfall("Список в теле класса общий: `append` через один объект виден во всех.",
                       bad='''
                           class Team:
                               members = []''',
                       good='''
                           class Team:
                               def __init__(self):
                                   self.members = []'''),
               pitfall("`self.count += 1` создаёт атрибут объекта, а счётчик класса не меняется.",
                       bad="self.count += 1", good="Order.count += 1")]),
    ],
    tasks=[
        task("t_oop_rectangle", "Прямоугольник",
             "Создайте класс Rectangle с атрибутами w и h и методами area() и perimeter(). Прочитайте w и h из одной строки и выведите площадь и периметр через пробел.",
             solution="""\
                class Rectangle:
                    def __init__(self, w, h):
                        self.w = w
                        self.h = h

                    def area(self):
                        return self.w * self.h

                    def perimeter(self):
                        return 2 * (self.w + self.h)

                w, h = map(int, input().split())
                r = Rectangle(w, h)
                print(r.area(), r.perimeter())""",
             starter="""\
                class Rectangle:
                    def __init__(self, w, h):
                        pass

                w, h = map(int, input().split())
                r = Rectangle(w, h)
                print(r.area(), r.perimeter())""",
             tests=["2 3\n", "5 5\n", "1 10\n", "7 4\n"], hint="Сохраните w и h в self.", difficulty=1,
             requires=dict(classes=["Rectangle"], methods={"Rectangle": ["__init__", "area", "perimeter"]},
                           calls=["area", "perimeter"])),
    ],
    levels=[
        choice("py_cls_001", "Кто такой self", "Что такое self в методе класса?",
               ["Имя класса", "Объект, у которого вызван метод", "Глобальная переменная", "Ключевое слово для создания класса"], 1,
               topic="oop_class", hint="При вызове d.bark() Python сам передаёт d первым аргументом.",
               explanation="self — ссылка на конкретный объект, у которого вызвали метод. Через него метод читает и меняет атрибуты этого объекта.",
               feedback={"Имя класса": "self — это конкретный объект, а не класс.",
                         "Глобальная переменная": "self — обычный параметр метода, первый по счёту.",
                         "Ключевое слово для создания класса": "Класс создаёт class. self — даже не ключевое слово, а соглашение об имени."}),
        predict("py_cls_002", "Первый класс", """\
                class Cat:
                    def __init__(self, name, sound="Мяу"):
                        self.name = name
                        self.sound = sound

                    def say(self):
                        return f"{self.name}: {self.sound}"

                c = Cat("Мурка")
                print(c.say())""",
                ["Cat: Мяу", "name: sound", "TypeError"], position=0, topic="oop_class",
                hint="В self.name и self.sound сохранены значения, переданные при создании (или по умолчанию).",
                explanation="Cat(\"Мурка\") вызывает __init__: name = «Мурка», sound по умолчанию «Мяу». say подставляет оба атрибута в строку.",
                feedback={"Cat: Мяу": "self.name — имя объекта, а не класса.",
                          "name: sound": "f-строка подставляет значения атрибутов, а не их названия.",
                          "TypeError": "c.say() передаёт c как self автоматически, аргументы совпадают."}),
        fill("py_cls_003", "Первый параметр", "Допишите первый параметр __init__",
             """\
             class Counter:
                 def __init__({{0}}):
                     self.value = 0

                 def inc(self):
                     self.value += 1

             c = Counter()
             c.inc()
             c.inc()
             print(c.value)""", ["self", "this", "obj", "cls"], ["self"],
             topic="oop_class", hint="Внутри метода используется имя self.",
             explanation="Первый параметр получает создаваемый объект. Тело метода обращается к нему как self, значит параметр должен так называться.",
             expect="2\n"),
        typed("py_cls_004", "Два счёта", """\
              class Account:
                  def __init__(self, owner, balance=0):
                      self.owner = owner
                      self.balance = balance

                  def deposit(self, amount):
                      self.balance += amount

              a = Account("Ada")
              b = Account("Bob", 100)
              a.deposit(50)
              b.deposit(25)
              print(a.owner, a.balance)
              print(b.owner, b.balance)""",
              topic="oop_class", hint="У каждого объекта свой balance.",
              explanation="a начинает с 0 и получает 50; b начинает со 100 и получает 25."),
        bug("py_cls_005", "Потерянный self", """\
            class Circle:
                def __init__(self, r):
                    self.r = r

                def area(self):
                    return 3.14 * r * r

            print(Circle(2).area())""", {5: "        return 3.14 * self.r * self.r"},
            prompt="Найдите строку с ошибкой", topic="oop_class",
            hint="Как метод получает доступ к атрибутам объекта?",
            explanation="r — параметр __init__, он существует только внутри __init__. В area радиус доступен как self.r, иначе NameError.",
            expect_error="NameError"),
        match("py_cls_006", "Атрибуты", ["c.brand", "c.wheels", "Car.wheels", "isinstance(c, Car)", "type(c).__name__"],
              setup="""\
                class Car:
                    wheels = 4
                    def __init__(self, brand):
                        self.brand = brand
                c = Car("Lada")
                c.wheels = 3""",
              topic="oop_class_attrs", hint="c.wheels = 3 создаёт атрибут объекта, класс не меняется.",
              explanation="У объекта появился свой wheels = 3, а Car.wheels по-прежнему 4. type(c).__name__ — имя класса."),
        predict("py_cls_007", "Общий список", """\
                class Team:
                    members = []

                    def add(self, name):
                        self.members.append(name)

                a = Team()
                b = Team()
                a.add("Ада")
                print(b.members)""",
                ["[]", "AttributeError", "['Ада', 'Ада']"], position=3, topic="oop_class_attrs",
                hint="Чей это список — класса или объекта?",
                explanation="members объявлен в теле класса — это один список на все объекты. append через a меняет его, и b видит то же самое.",
                role="challenge", difficulty=3,
                feedback={"[]": "У b нет своего списка: он видит общий список класса, в который a добавил «Ада».",
                          "AttributeError": "Объект видит атрибуты класса.",
                          "['Ада', 'Ада']": "Добавление было одно."}),
        multi("py_cls_008", "Про __init__", "Какие утверждения верны?",
              ["__init__ вызывается автоматически при создании объекта",
               "__init__ должен возвращать созданный объект",
               "Атрибуты можно добавить объекту и вне __init__",
               "Без __init__ объект создать нельзя",
               "self — ссылка на текущий объект"], [0, 2, 4],
              check=lambda s: {
                  "__init__ вызывается автоматически при создании объекта":
                      runs("log = []\nclass A:\n    def __init__(self):\n        log.append(1)\nA()\nassert log == [1]"),
                  "__init__ должен возвращать созданный объект":
                      runs("class A:\n    def __init__(self):\n        return self\nA()"),
                  "Атрибуты можно добавить объекту и вне __init__":
                      runs("class A:\n    pass\na = A()\na.x = 5\nassert a.x == 5"),
                  "Без __init__ объект создать нельзя":
                      not runs("class A:\n    pass\nA()"),
                  "self — ссылка на текущий объект":
                      runs("class A:\n    def me(self):\n        return self\na = A()\nassert a.me() is a"),
              }[s],
              topic="oop_class", hint="Попробуйте мысленно создать пустой класс class A: pass.",
              explanation="__init__ только настраивает объект, который уже создан, и должен возвращать None. Класс без __init__ тоже можно создавать, а атрибуты можно добавлять в любой момент.",
              feedback={"__init__ должен возвращать созданный объект": "__init__ должен вернуть None, иначе TypeError.",
                        "Без __init__ объект создать нельзя": "class A: pass — и A() отлично работает."}),
        predict("py_cls_010", "Счётчик через self", """\
                class Ticket:
                    issued = 0
                    def __init__(self):
                        self.issued += 1

                a, b = Ticket(), Ticket()
                print(a.issued, b.issued, Ticket.issued)""",
                ["1 2 2", "2 2 2", "1 1 1"], position=3, topic="oop_class_attrs",
                hint="self.issued += 1 — это self.issued = self.issued + 1. Куда записывается результат?",
                explanation="Справа self.issued читает атрибут класса (0), а присваивание создаёт атрибут объекта со значением 1. У каждого объекта своя 1, а Ticket.issued остаётся 0.",
                role="challenge", difficulty=3,
                feedback={"1 2 2": "Атрибут класса не меняется: присваивание через self создаёт атрибут объекта.",
                          "2 2 2": "Каждый объект получает своё значение 1, класс остаётся с 0.",
                          "1 1 1": "Ticket.issued не изменился — по-прежнему 0."}),
        order("py_cls_009", "Босс: цепочка вызовов", "Соберите класс так, чтобы программа вывела 2",
              ["class Stack:", "    def __init__(self):", "        self.items = []", "    def push(self, x):",
               "        self.items.append(x)", "        return self", "print(len(Stack().push(1).push(2).items))"],
              topic="oop_class", hint="push возвращает сам объект — поэтому вызовы можно сцепить.",
              explanation="return self после append позволяет писать Stack().push(1).push(2): каждый push возвращает тот же стек.",
              role="boss", difficulty=3),
    ],
))

# -------------------------------------------------------------- inheritance
MODULES.append(dict(
    id="inheritance", title="Наследование", description="super, полиморфизм, ABC", icon="🌳",
    topics=[
        topic("inh_basics", "Наследование и super()",
              "Наследование создаёт новый класс на основе готового: подкласс получает методы родителя и меняет только отличия.",
              """
              Новый класс часто оказывается частным случаем уже готового: администратор — тоже пользователь, но с дополнительными правами. Наследование позволяет взять готовый класс и описать только то, чем новый от него отличается.

              ## Как записать

              ```syntax
              class Подкласс(Родитель):
                  def метод(self):
                      новое_поведение
              ```

              - Подкласс получает все методы и атрибуты родителя.
              - Метод с тем же именем в подклассе заменяет метод родителя. Это называют переопределением.
              - Новые методы просто добавляются к унаследованным.

              ## Как Python ищет метод

              Для `obj.m()` Python смотрит в класс объекта, затем в его родителя, затем в родителя родителя. Берётся первый найденный метод. Поэтому подкласс меняет поведение, не трогая код родителя.

              Так же наследуются [[oop_class_attrs|атрибуты класса]]. Порядок поиска при нескольких родителях описан в теме [[inh_mro|Множественное наследование и MRO]].

              ## super(): версия родителя

              `super().метод(...)` вызывает метод родителя для того же объекта. Так подкласс дополняет поведение родителя, а не переписывает его с нуля.

              Чаще всего это нужно в `__init__`. Если у подкласса свой `__init__`, родительский сам не вызывается. Без `super().__init__(...)` у объекта не будет атрибутов, которые создаёт родитель.

              ## Когда наследовать

              Наследование выражает отношение «является»: студент — человек. Если объект только пользуется другим («у машины есть двигатель»), храните его в атрибуте. Это называют композицией.

              Подкласс должен работать везде, где работает родитель. Если код, написанный для родителя, на подклассе ведёт себя неожиданно, наследование выбрано неверно.
              """,
              [("""\
                class User:
                    def who(self):
                        return "гость"

                    def badge(self):
                        return f"[{self.who()}]"

                class Admin(User):
                    def who(self):
                        return "админ"

                print(User().badge())
                print(Admin().badge())""",
                "badge унаследован, а who у Admin свой — значки разные"),
               ("""\
                class Item:
                    def __init__(self, title):
                        self.title = title

                class Food(Item):
                    def __init__(self, title, kcal):
                        super().__init__(title)
                        self.kcal = kcal

                apple = Food("яблоко", 52)
                print(apple.title)
                print(apple.kcal)""",
                "title создал __init__ родителя, kcal — подкласс"),
               ("""\
                class Report:
                    def title(self):
                        return "Итоги"

                class Daily(Report):
                    def title(self):
                        base = super().title()
                        return base + " за день"

                print(Daily().title())""",
                "super() взял текст родителя, подкласс дописал своё"),
               ("""\
                class Item:
                    def __init__(self, title):
                        self.title = title

                class Drink(Item):
                    def __init__(self, ml):
                        self.ml = ml

                try:
                    print(Drink(330).title)
                except AttributeError as e:
                    print(e)""",
                "Без super().__init__ атрибута title у объекта нет")],
              [pitfall("Свой `__init__` без `super().__init__()`: атрибутов родителя нет, будет `AttributeError`.",
                       bad='''
                           def __init__(self, name, kcal):
                               self.kcal = kcal''',
                       good='''
                           def __init__(self, name, kcal):
                               super().__init__(name)
                               self.kcal = kcal'''),
               pitfall("`super()` уже знает объект: лишний `self` даёт `TypeError: … takes 2 positional arguments but 3 were given`.",
                       bad="super().__init__(self, name)", good="super().__init__(name)"),
               pitfall("Наследовать ради пары методов, когда «является» не выполняется: храните объект в атрибуте.",
                       bad='''
                           class Car(Engine):
                               pass''',
                       good='''
                           class Car:
                               def __init__(self):
                                   self.engine = Engine()''')]),
        topic("inh_poly", "Полиморфизм и утиная типизация",
              "Полиморфизм — один и тот же вызов метода для объектов разных классов, каждый из которых выполняет его по-своему.",
              """
              Программа часто обрабатывает разные объекты одинаково: рисует все фигуры, рассылает уведомления по почте и в SMS. Полиморфизм позволяет написать такой код один раз, без цепочки `if` по типам.

              ## Один вызов — разное поведение

              Если у разных классов есть метод с одним именем, цикл `for s in shapes: s.area()` работает для всех. Каждый объект выполняет свою версию метода. Новый класс с методом `area` подойдёт без правок в цикле.

              ## Утиная типизация

              «Если крякает как утка — значит, утка». При вызове метода Python не проверяет класс объекта: важно только, что метод есть. Общий родитель не нужен. Если метода нет, будет `AttributeError` в момент вызова.

              ## Проверка класса

              - `isinstance(obj, Cls)` — объект этого класса или его подкласса;
              - `isinstance(obj, (A, B))` — объект одного из нескольких классов;
              - `issubclass(B, A)` — класс `B` наследует `A`.

              Все классы — наследники `object`. Сравнение `type(x) == A` подклассы не учитывает, поэтому для проверок берут `isinstance`.

              ## Что выбрать

              Утиная типизация — по умолчанию: код гибче. `isinstance` нужен, когда разные типы обрабатываются по-разному, например число и список на входе.

              Чтобы явно потребовать набор методов, используют [[inh_abc|абстрактный класс]] или [[typing_advanced|Protocol]].
              """,
              [("""\
                class Email:
                    def send(self, text):
                        return "письмо: " + text

                class Sms:
                    def send(self, text):
                        return "смс: " + text

                for ch in [Email(), Sms()]:
                    print(ch.send("код 42"))""",
                "Один и тот же вызов send — разный результат"),
               ("""\
                def load(src):
                    return src.read()

                class Socket:
                    def read(self):
                        return "пакет"

                print(load(Socket()))
                try:
                    load(42)
                except AttributeError as e:
                    print(e)""",
                "Подходит любой объект с методом read; у числа его нет"),
               ("""\
                class Animal:
                    pass

                class Cat(Animal):
                    pass

                c = Cat()
                print(isinstance(c, Animal))
                print(type(c) == Animal)
                print(issubclass(Cat, object))""",
                "isinstance учитывает наследование, сравнение type — нет"),
               ("""\
                def total(x):
                    if isinstance(x, (list, tuple)):
                        return sum(x)
                    return x

                print(total(5))
                print(total([1, 2, 3]))""",
                "isinstance с кортежем классов: список сложен, число — как есть")],
              [pitfall("`type(x) == A` не пропускает подклассы, а `isinstance` учитывает наследование.",
                       bad="ok = type(x) == Animal", good="ok = isinstance(x, Animal)"),
               pitfall("Цепочку `if` по типам правят при каждом новом классе, а метод у каждого класса — нет.",
                       bad='''
                           if isinstance(s, Square):
                               a = s.side ** 2
                           elif isinstance(s, Circle):
                               a = 3.14 * s.r ** 2''',
                       good="a = s.area()")]),
        topic("inh_mro", "Множественное наследование и MRO",
              "При нескольких родителях Python ищет методы в строгом порядке — MRO, и `super()` идёт по этому же порядку.",
              """
              Класс может наследовать сразу от нескольких родителей. Обычно так подмешивают небольшие готовые возможности: «умеет сохраняться», «умеет писать в лог». Чтобы не было путаницы, методы ищутся в строго определённом порядке.

              ## Как записать

              ```syntax
              class Класс(Родитель1, Родитель2):
                  тело
              ```

              ## Порядок поиска: MRO

              MRO (method resolution order) — список классов, в котором Python ищет метод или атрибут. Его показывают `Класс.__mro__` и `Класс.mro()`. Правила:

              - сначала сам класс, затем родители слева направо;
              - подкласс всегда стоит раньше своего родителя;
              - общий предок входит один раз — после всех своих наследников.

              Последним всегда идёт `object`.

              ## super() идёт по MRO

              `super()` вызывает не обязательно прямого родителя, а **следующий класс в MRO того объекта**, у которого вызван метод. Если каждый класс в цепочке вызывает `super()`, сработают все — каждый по одному разу.

              Явный вызов `Родитель.метод(self)` этот порядок ломает: общий предок может сработать дважды. Поэтому в таких иерархиях пишут `super()`.

              ## Когда это нужно

              Чаще всего множественное наследование встречается в виде примесей (mixin): маленький класс с одним-двумя методами и без своего `__init__`. Запутанные иерархии лучше заменять композицией: хранить объекты в атрибутах.

              Если порядок родителей противоречив, например родитель указан раньше своего подкласса, Python не построит MRO и выбросит `TypeError`.
              """,
              [("""\
                class Named:
                    def __init__(self, name):
                        self.name = name

                class Greeter:
                    def hello(self):
                        return "привет, " + self.name

                class Bot(Named, Greeter):
                    pass

                print(Bot("R2").hello())""",
                "Bot взял __init__ у Named, а hello — у Greeter"),
               ("""\
                class Base:
                    pass

                class Left(Base):
                    pass

                class Right(Base):
                    pass

                class Child(Left, Right):
                    pass

                for k in Child.__mro__:
                    print(k.__name__)""",
                "MRO: сам класс, Left, Right, затем общий Base и object"),
               ("""\
                class Log:
                    def parts(self):
                        return ["Log"] + super().parts()

                class Cache:
                    def parts(self):
                        return ["Cache"]

                class App(Log, Cache):
                    pass

                print(App().parts())""",
                "super() в Log вызвал не родителя, а соседа по MRO — Cache"),
               ("""\
                class A:
                    pass

                class B(A):
                    pass

                try:
                    class C(A, B):
                        pass
                except TypeError:
                    print("MRO построить нельзя")""",
                "Родитель A указан раньше своего подкласса B — ошибка")],
              [pitfall("Примесь без `super()` обрывает цепочку: `save` следующего класса в MRO не вызовется.",
                       bad='''
                           class LogMixin:
                               def save(self):
                                   print("лог")''',
                       good='''
                           class LogMixin:
                               def save(self):
                                   print("лог")
                                   super().save()'''),
               pitfall("Примесь, указанная после основного класса, не срабатывает: его `save` в MRO находится первым.",
                       bad='''
                           class Doc(Storage, LogMixin):
                               pass''',
                       good='''
                           class Doc(LogMixin, Storage):
                               pass'''),
               pitfall("Явный вызов родителя в «ромбе» запускает общего предка дважды, а `super()` — один раз.",
                       bad="Log.parts(self)", good="super().parts()"),
               pitfall("Родитель указан раньше своего подкласса: `TypeError: Cannot create a consistent method resolution order`.",
                       bad='''
                           class C(A, B):
                               pass''',
                       good='''
                           class C(B, A):
                               pass''')]),
        topic("inh_abc", "Абстрактные классы",
              "Абстрактный класс задаёт обязательные методы: объект создать нельзя, пока подкласс их не реализует.",
              """
              Иногда базовый класс нужен только как договор: «каждый способ оплаты обязан уметь `pay`». Сам он ничего не делает, и создавать его объекты бессмысленно. Абстрактный класс закрепляет такой договор, и Python проверяет его за вас.

              ## Как записать

              ```syntax
              from abc import ABC, abstractmethod

              class Базовый(ABC):
                  @abstractmethod
                  def метод(self):
                      ...
              ```

              - Родитель {`ABC`} включает проверку.
              - {`@abstractmethod`} помечает обязательный метод. Строка с `@` над `def` — это [[deco_basics|декоратор]].
              - `...` (многоточие) — тело-заглушка: «здесь ничего нет». Подойдёт и `pass`.

              ## Когда срабатывает проверка

              Объявить подкласс без нужного метода можно. Ошибка будет при создании объекта: `TypeError: Can't instantiate abstract class`. То же — при попытке создать сам базовый класс.

              Так незаконченный класс виден сразу, а не в момент, когда программа дойдёт до вызова метода.

              ## Обычные методы в ABC

              В абстрактном классе могут быть и обычные методы, они наследуются как всегда. Часто общий метод вызывает абстрактный: родитель задаёт порядок действий, а подклассы — детали.

              ## Что выбрать

              - Обычный родитель с `raise NotImplementedError` в методе — ошибка только при вызове метода.
              - {`ABC`} — ошибка уже при создании объекта; нужен общий родитель.
              - [[typing_advanced|Protocol]] — требование по форме, без наследования; проверяет анализатор типов.

              Без общего родителя объекты разных классов работают вместе благодаря [[inh_poly|утиной типизации]].
              """,
              [("""\
                from abc import ABC, abstractmethod

                class Payment(ABC):
                    @abstractmethod
                    def pay(self, amount):
                        ...

                class Card(Payment):
                    def pay(self, amount):
                        return f"карта: {amount}"

                print(Card().pay(500))""",
                "Подкласс реализовал pay — объект создаётся"),
               ("""\
                from abc import ABC, abstractmethod

                class Payment(ABC):
                    @abstractmethod
                    def pay(self, amount):
                        ...

                class Cash(Payment):
                    pass

                try:
                    Cash()
                except TypeError as e:
                    print(e)""",
                "Подкласс без pay: ошибка уже при создании объекта"),
               ("""\
                from abc import ABC, abstractmethod

                class Export(ABC):
                    @abstractmethod
                    def body(self):
                        ...
                    def render(self):
                        return "== " + self.body()

                class Sales(Export):
                    def body(self):
                        return "продажи: 12"

                print(Sales().render())""",
                "Общий render из базы вызывает body подкласса")],
              [pitfall("Без наследования от {`ABC`} пометка {`@abstractmethod`} не действует: объект создаётся.",
                       bad='''
                           class Payment:
                               @abstractmethod
                               def pay(self, amount): ...''',
                       good='''
                           class Payment(ABC):
                               @abstractmethod
                               def pay(self, amount): ...'''),
               pitfall("Опечатка в имени метода: абстрактный остался нереализованным, при создании объекта `TypeError`.",
                       bad='''
                           def pai(self, amount):
                               return amount''',
                       good='''
                           def pay(self, amount):
                               return amount''')]),
    ],
    tasks=[
        task("t_inh_shapes", "Фигуры",
             "Создайте базовый класс Shape с методом area() и подклассы Square(a) и Circle(r) (π = 3.14159). Прочитайте n и n строк вида «square 3» или «circle 2» и выведите площадь каждой фигуры ровно с двумя знаками после точки (например, 9.00).",
             solution="""\
                class Shape:
                    def area(self):
                        raise NotImplementedError

                class Square(Shape):
                    def __init__(self, a):
                        self.a = a
                    def area(self):
                        return self.a ** 2

                class Circle(Shape):
                    def __init__(self, r):
                        self.r = r
                    def area(self):
                        return 3.14159 * self.r ** 2

                kinds = {"square": Square, "circle": Circle}
                for _ in range(int(input())):
                    kind, size = input().split()
                    print(f"{kinds[kind](float(size)).area():.2f}")""",
             starter="""\
                class Shape:
                    def area(self):
                        return 0

                for _ in range(int(input())):
                    kind, size = input().split()
                    print(Shape().area())""",
             tests=["2\nsquare 3\ncircle 1\n", "1\ncircle 2\n", "3\nsquare 1.5\nsquare 2\ncircle 0.5\n",
                    "1\nsquare 10\n"],
             hint="Словарь «название → класс» избавит от цепочки if.", difficulty=2,
             requires=dict(classes=["Shape", "Square", "Circle"], inherits={"Square": "Shape", "Circle": "Shape"},
                           methods={"Square": ["area"], "Circle": ["area"]})),
    ],
    levels=[
        predict("py_inh_001", "Переопределение", """\
                class Animal:
                    def speak(self):
                        return "..."

                class Cat(Animal):
                    def speak(self):
                        return "Мяу"

                class Fish(Animal):
                    pass

                print(Cat().speak(), Fish().speak())""",
                ["Мяу Мяу", "Мяу", "... ..."], position=1, topic="inh_basics",
                hint="У Fish нет своего speak — какой будет использован?",
                explanation="Cat переопределяет speak. У Fish своего метода нет, и Python берёт метод родителя Animal.",
                feedback={"Мяу Мяу": "Fish наследует от Animal, а не от Cat.",
                          "Мяу": "Fish().speak() тоже работает: метод унаследован.",
                          "... ...": "Cat переопределяет speak и возвращает «Мяу»."}),
        fill("py_inh_002", "Вызов родителя", "Вызовите __init__ родителя",
             """\
             class Animal:
                 def __init__(self, name):
                     self.name = name

             class Dog(Animal):
                 def __init__(self, name, breed):
                     {{0}}.__init__(name)
                     self.breed = breed

             d = Dog("Рекс", "овчарка")
             print(d.name, d.breed)""", ["super()", "self", "Animal", "Dog"], ["super()"],
             topic="inh_basics", hint="Функция, которая даёт доступ к методам родителя с уже привязанным self.",
             explanation="super().__init__(name) вызывает Animal.__init__ для текущего объекта. Animal.__init__(name) не передаёт self, а self.__init__ снова вызвал бы Dog.__init__ и упал бы с TypeError: не хватает breed.",
             expect="Рекс овчарка\n"),
        typed("py_inh_003", "Полиморфизм", """\
              class Shape:
                  def area(self):
                      return 0

              class Square(Shape):
                  def __init__(self, a):
                      self.a = a
                  def area(self):
                      return self.a ** 2

              class Circle(Shape):
                  def __init__(self, r):
                      self.r = r
                  def area(self):
                      return round(3.14159 * self.r ** 2, 1)

              for s in [Square(3), Circle(1), Shape()]:
                  print(type(s).__name__, s.area())""",
              topic="inh_poly", hint="Каждый класс считает площадь по-своему, Shape возвращает 0.",
              explanation="Один и тот же вызов s.area() даёт разный результат: 3² = 9, π·1² ≈ 3.1, и 0 у базового класса."),
        multi("py_inh_004", "Родство", "Какие выражения истинны?",
              ["isinstance(B(), A)", "isinstance(A(), B)", "issubclass(B, A)", "issubclass(A, object)", "isinstance(C(), A)"],
              [0, 2, 3],
              code="""\
                class A:
                    pass

                class B(A):
                    pass

                class C:
                    pass""",
              check=lambda expr: eval(expr, {"A": (A := type("A", (), {})), "B": type("B", (A,), {}),
                                             "C": type("C", (), {})}),
              topic="inh_poly", hint="Объект подкласса — это и объект родителя, но не наоборот.",
              explanation="B — подкласс A, поэтому объект B — это и A. Объект A не является B. Все классы — наследники object. C с A не связан.",
              feedback={"isinstance(A(), B)": "Наследование работает в одну сторону: A не знает про B.",
                        "isinstance(C(), A)": "C не наследует A."}),
        bug("py_inh_005", "Забытый вызов", """\
            class Base:
                def __init__(self):
                    self.items = []

            class Log(Base):
                def __init__(self, title):
                    Base.__init__
                    self.title = title

                def add(self, x):
                    self.items.append(x)

            log = Log("день")
            log.add("старт")
            print(log.title, log.items)""", {6: "        super().__init__()"},
            prompt="Найдите строку с ошибкой", topic="inh_basics",
            hint="Base.__init__ без скобок — это вызов?",
            explanation="Base.__init__ без скобок только упоминает функцию, но не вызывает её. Атрибут items не создаётся, и add падает с AttributeError. Нужно super().__init__().",
            expect_error="AttributeError"),
        predict("py_inh_006", "Наследуемый атрибут", """\
                class Base:
                    color = "red"

                class Child(Base):
                    pass

                c = Child()
                print(c.color)
                Child.color = "blue"
                print(Base.color, c.color)""",
                ["red\nblue blue", "red\nred red", "blue\nred blue"], position=1, topic="inh_basics",
                hint="Child.color = ... создаёт атрибут у Child, Base не меняется.",
                explanation="Сначала c видит color из Base. Присваивание Child.color создаёт свой атрибут подкласса, и c видит его, а у Base остаётся «red».",
                role="practice", difficulty=2,
                feedback={"red\nblue blue": "Присваивание у Child не меняет атрибут Base.",
                          "red\nred red": "После Child.color = \"blue\" объект c видит атрибут своего класса.",
                          "blue\nred blue": "Первый print выполняется до изменения."}),
        choice("py_inh_007", "Абстрактный класс", "Что произойдёт при вызове Shape()?",
               ["Создастся объект Shape", "TypeError: абстрактный класс нельзя создать", "NameError", "Вернётся None"], 1,
               code="""\
                from abc import ABC, abstractmethod

                class Shape(ABC):
                    @abstractmethod
                    def area(self): ...

                s = Shape()""",
               check=lambda option: (result_of("from abc import ABC, abstractmethod\nclass Shape(ABC):\n    @abstractmethod\n    def area(self): ...\ns = Shape()") == "TypeError") == option.startswith("TypeError"),
               topic="inh_abc", hint="Зачем методу пометка @abstractmethod?",
               explanation="Класс с нереализованным абстрактным методом нельзя создать: TypeError. Его подклассы обязаны реализовать area.",
               role="practice", difficulty=2,
               feedback={"Создастся объект Shape": "У Shape есть абстрактный метод — создать объект нельзя.",
                         "NameError": "Все имена импортированы и определены.",
                         "Вернётся None": "Вызов класса либо создаёт объект, либо вызывает исключение."}),
        match("py_inh_008", "Утиная типизация", ["ring(Bell())", "ring(Phone())", "isinstance(Phone(), Bell)",
                                                  "hasattr(Phone(), 'ring')"],
              setup="""\
                class Bell:
                    def ring(self):
                        return "дзинь"
                class Phone:
                    def ring(self):
                        return "трр"
                def ring(x):
                    return x.ring()""",
              topic="inh_poly", hint="Функция ring не проверяет тип, только вызывает метод ring.",
              explanation="ring работает с любым объектом, у которого есть метод ring. Phone не наследует Bell, но метод у него есть."),
        predict("py_inh_010", "Квадрат — не прямоугольник", """\
                class Rect:
                    def __init__(self, w, h):
                        self.w, self.h = w, h
                    def set_w(self, w):
                        self.w = w
                    def area(self):
                        return self.w * self.h

                class Square(Rect):
                    def __init__(self, a):
                        super().__init__(a, a)
                    def set_w(self, w):
                        self.w = self.h = w

                def stretch(r):
                    r.set_w(10)
                    return r.area()

                print(stretch(Rect(2, 5)), stretch(Square(5)))""",
                ["50 50", "20 25", "50 10"], position=3, topic="inh_basics",
                hint="Square меняет обе стороны сразу. Что ждёт функция stretch от прямоугольника?",
                explanation="stretch рассчитывает, что меняется только ширина: 10 · 5 = 50. Square при set_w меняет и высоту: 10 · 10 = 100. Код, рассчитанный на Rect, ведёт себя неожиданно — это нарушение принципа подстановки Лисков.",
                role="challenge", difficulty=4,
                feedback={"50 50": "Square.set_w меняет и высоту: площадь 10 · 10.",
                          "20 25": "stretch сначала меняет ширину на 10, потом считает площадь.",
                          "50 10": "Площадь квадрата со стороной 10 — 100."}),
        predict("py_inh_009", "Босс: порядок MRO", """\
                class A:
                    def who(self):
                        return "A"

                class B(A):
                    def who(self):
                        return "B" + super().who()

                class C(A):
                    def who(self):
                        return "C" + super().who()

                class D(C, B):
                    def who(self):
                        return "D" + super().who()

                print(D().who())""",
                ["DBCA", "DCA", "DCBAA"], position=1, topic="inh_mro",
                hint="Порядок поиска для D(C, B): D, C, B, A. super() идёт по этому порядку.",
                explanation="MRO класса D — D, C, B, A (родители в порядке объявления). super() в C ведёт к B — следующему в MRO, — а не к A. A вызывается один раз.",
                role="boss", difficulty=4,
                feedback={"DBCA": "Родители перечислены как (C, B): C стоит первым.",
                          "DCA": "super() в C вызывает следующий класс в MRO объекта D — это B, а не A.",
                          "DCBAA": "A входит в MRO один раз."}),
    ],
))

# -------------------------------------------------------------------- dunder
MODULES.append(dict(
    id="dunder", title="Магические методы", description="__str__, __eq__, __add__, __len__", icon="✨",
    topics=[
        topic("dunder_str", "__str__ и __repr__",
              "`__str__` даёт понятный текст объекта для людей, а `__repr__` — точное описание для разработчика.",
              """
              По умолчанию объект печатается как `<__main__.Order object at 0x7f…>`: ни данных, ни пользы. Два специальных метода задают текст объекта — один для пользователей программы, другой для отладки.

              ## Как записать

              ```syntax
              class Класс:
                  def __str__(self):
                      return "текст для людей"

                  def __repr__(self):
                      return "Класс(аргументы)"
              ```

              Оба метода обязаны вернуть строку. Печатать внутри них не нужно.

              ## Кто какой метод вызывает

              | Где | Метод |
              |---|---|
              | {`print(obj)`}, {`str(obj)`} | {`__str__`} |
              | {`f"{obj}"`} | {`__str__`} |
              | {`repr(obj)`}, {`f"{obj!r}"`} | {`__repr__`} |
              | {`print([obj])`} | {`__repr__`} элементов |
              | консоль, отладчик | {`__repr__`} |

              Если `__str__` нет, везде используется `__repr__`. Поэтому если писать только один метод, то `__repr__`.

              ## Каким делать repr

              Хороший `__repr__` похож на код, который создаёт такой же объект: `Money(5)`. Строки внутри него показывают в кавычках — для этого в [[str_fstring|f-строке]] пишут `{self.name!r}`.
              """,
              [("""\
                class Money:
                    def __init__(self, rub):
                        self.rub = rub

                    def __str__(self):
                        return f"{self.rub} руб."

                m = Money(250)
                print(m)
                print("Итого: " + str(m))""",
                "print и str() берут текст из __str__"),
               ("""\
                class Money:
                    def __init__(self, rub):
                        self.rub = rub
                    def __str__(self):
                        return f"{self.rub} руб."
                    def __repr__(self):
                        return f"Money({self.rub})"

                wallet = [Money(5), Money(20)]
                print(wallet[0])
                print(wallet)""",
                "Сам объект — через __str__, внутри списка — через __repr__"),
               ("""\
                class Tag:
                    def __init__(self, label):
                        self.label = label
                    def __repr__(self):
                        return f"Tag({self.label!r})"

                t = Tag("python")
                print(t)
                print(f"{t}")""",
                "Без __str__ print берёт __repr__; !r добавил кавычки")],
              [pitfall("Список печатает элементы через `__repr__`: с одним `__str__` будет `<__main__.X object at 0x…>`.",
                       bad='''
                           def __str__(self):
                               return f"Money({self.rub})"''',
                       good='''
                           def __repr__(self):
                               return f"Money({self.rub})"'''),
               pitfall("Метод должен вернуть строку, иначе `TypeError: __str__ returned non-string (type int)`.",
                       bad="return self.rub", good="return str(self.rub)"),
               pitfall("`print` вместо `return`: `TypeError: __str__ returned non-string (type NoneType)`.",
                       bad='print(f"{self.rub} руб.")', good='return f"{self.rub} руб."')]),
        topic("dunder_ops", "Сравнение и операторы",
              "Операторы `==`, `<`, `+` для своих объектов работают через специальные методы `__eq__`, `__lt__`, `__add__`.",
              """
              Свои классы могут работать с операторами так же, как числа: сравнивать заказы по сумме, складывать векторы, сортировать карты. Для каждого оператора есть специальный метод, который Python вызывает вместо него.

              ## Оператор и метод

              | Запись | Метод |
              |---|---|
              | {`a == b`}, {`a != b`} | {`__eq__`} |
              | {`a < b`}, {`a > b`} | {`__lt__`}, {`__gt__`} |
              | {`a <= b`}, {`a >= b`} | {`__le__`}, {`__ge__`} |
              | {`a + b`} | {`__add__`} |
              | {`a * b`} | {`__mul__`} |
              | {`hash(a)`} | {`__hash__`} |

              `a == b` — это вызов `a.__eq__(b)`. Без своего `__eq__` объекты равны, только если это один и тот же объект. Результат `!=` Python выводит из `__eq__` сам. `__add__` возвращает новый объект и не меняет исходные.

              ## Сравнение и сортировка

              `sorted` и `min` сравнивают элементы через `<`, `max` — через `>`. Если `__gt__` нет, Python пробует обратное `b < a`, поэтому для всех троих хватает `__lt__`. Декоратор `functools.total_ordering` достраивает `<=`, `>`, `>=` по `__eq__` и `__lt__`.

              ## Чужой тип: NotImplemented

              Если операция с объектом другого типа не имеет смысла, метод возвращает `NotImplemented`. Тогда Python пробует метод второго объекта. Для `==` в итоге получится `False`, для `+` — `TypeError`. Не путайте с исключением `NotImplementedError`.

              ## Равные объекты — равные хеши

              Объявив `__eq__`, класс теряет `__hash__`: объект нельзя положить в [[set_basics|множество]] или сделать ключом словаря. Правило: если `a == b`, то и `hash(a) == hash(b)`. Хеш считают от тех же полей, что сравнивают: `hash((self.x, self.y))`.

              Всё это для классов с данными пишет [[dc_basics|`@dataclass`]].
              """,
              [("""\
                class Coin:
                    def __init__(self, value):
                        self.value = value

                    def __eq__(self, other):
                        return self.value == other.value

                a = Coin(5)
                b = Coin(5)
                print(a == b)
                print(a is b)""",
                "== сравнивает по value, а is проверяет, один ли это объект"),
               ("""\
                from functools import total_ordering

                @total_ordering
                class Rank:
                    def __init__(self, n):
                        self.n = n
                    def __eq__(self, other):
                        return self.n == other.n
                    def __lt__(self, other):
                        return self.n < other.n

                print(Rank(2) >= Rank(1))
                print(max(Rank(3), Rank(7)).n)""",
                "total_ordering достроил >=, max сравнил ранги через >"),
               ("""\
                class Score:
                    def __init__(self, pts):
                        self.pts = pts
                    def __add__(self, other):
                        if not isinstance(other, Score):
                            return NotImplemented
                        return Score(self.pts + other.pts)

                total = Score(10) + Score(5)
                print(total.pts)
                try:
                    Score(10) + 5
                except TypeError as e:
                    print(e)""",
                "Score + Score — новый объект; Score + число — TypeError"),
               ("""\
                class Color:
                    def __init__(self, code):
                        self.code = code
                    def __eq__(self, other):
                        return self.code == other.code

                print(Color.__hash__)
                try:
                    {Color("red")}
                except TypeError as e:
                    print(e)""",
                "С __eq__, но без __hash__ объект не кладётся в set")],
              [pitfall("`__eq__` без `__hash__`: в множестве или ключе словаря будет `TypeError: unhashable type`.",
                       bad='''
                           def __eq__(self, other):
                               return self.xy == other.xy''',
                       good='''
                           def __eq__(self, other):
                               return self.xy == other.xy
                           def __hash__(self):
                               return hash(self.xy)'''),
               pitfall("Хеш от `id(self)` при `__eq__` по полям: в множество попадут оба равных объекта.",
                       bad="return hash(id(self))", good="return hash((self.x, self.y))"),
               pitfall("Без проверки типа `v == 5` падает: `AttributeError: 'int' object has no attribute 'x'`.",
                       bad='''
                           def __eq__(self, other):
                               return self.x == other.x''',
                       good='''
                           def __eq__(self, other):
                               if not isinstance(other, Vec):
                                   return NotImplemented
                               return self.x == other.x''')]),
        topic("dunder_protocols", "Объект как коллекция и функция",
              "Специальные методы позволяют своему объекту работать с `len`, индексами, `in`, вызовом `()` и проверкой `if`.",
              """
              Встроенные функции и операторы работают не только со списками. `len(x)`, {`x[i]`}, `in`, вызов `x()` и проверка `if x` вызывают у объекта специальные методы. Добавив их, класс начинает вести себя как коллекция или функция.

              ## Запись и метод

              | Запись | Метод |
              |---|---|
              | {`len(obj)`} | {`__len__`} |
              | {`obj[key]`} | {`__getitem__`} |
              | {`x in obj`} | {`__contains__`} |
              | {`for x in obj`} | {`__iter__`}, {`__getitem__`} |
              | {`obj(аргументы)`} | {`__call__`} |
              | {`if obj:`}, {`bool(obj)`} | {`__bool__`}, {`__len__`} |

              ## Коллекция из двух методов

              Объекту с `__len__` и `__getitem__` по номеру сразу доступны индексы, `for`, `in` и `reversed`. Цикл `for` вызывает `__getitem__(0)`, `__getitem__(1)` и так далее, пока не получит `IndexError`.

              Если `__getitem__` передаёт индекс списку, работают и срезы. Свой способ перебора задают методом [[gen_iter|`__iter__`]].

              ## in без перебора

              Без `__contains__` оператор `in` перебирает элементы один за другим. Свой `__contains__` отвечает сразу — например, проверкой во внутреннем множестве.

              ## Объект-функция

              `__call__` делает объект вызываемым: `obj(5)` — то же, что `obj.__call__(5)`. В отличие от функции, такой объект хранит состояние в атрибутах: настройки, счётчик вызовов. Похожего добиваются [[scope_closure|замыканием]].

              ## Истинность

              `if obj:` сначала ищет `__bool__`. Если его нет — берёт `__len__`, и длина `0` означает ложь. Если нет и его, объект всегда истинен. Подробнее — в теме [[types_bool|Истинность значений]].
              """,
              [("""\
                class Week:
                    days = ["пн", "вт", "ср"]
                    def __len__(self):
                        return len(self.days)
                    def __getitem__(self, i):
                        return self.days[i]

                w = Week()
                print(len(w))
                print(w[-1])
                print(w[0:2])
                for d in w:
                    print(d)""",
                "Два метода дали len, индексы, срезы и цикл for"),
               ("""\
                class Blacklist:
                    def __init__(self, words):
                        self.words = set(words)
                    def __contains__(self, word):
                        return word.lower() in self.words

                bl = Blacklist(["спам", "реклама"])
                print("СПАМ" in bl)
                print("привет" in bl)""",
                "in вызвал __contains__: проверка без учёта регистра"),
               ("""\
                class Discount:
                    def __init__(self, percent):
                        self.percent = percent
                    def __call__(self, price):
                        k = 100 - self.percent
                        return price * k // 100

                sale = Discount(20)
                print(sale(1000))
                print(list(map(sale, [50, 300])))""",
                "Объект с __call__ вызывается как функция и помнит процент"),
               ("""\
                class Inbox:
                    def __init__(self):
                        self.letters = []
                    def __len__(self):
                        return len(self.letters)

                box = Inbox()
                print(bool(box))
                box.letters.append("счёт")
                print(bool(box))""",
                "Без __bool__ истинность берётся из __len__")],
              [pitfall("Ждать, что объект без `__bool__` и `__len__` будет ложным: он всегда истинен, нужен один из методов."),
               pitfall("`for` по `__getitem__` идёт до `IndexError`; без него цикл бесконечный.",
                       bad='''
                           def __getitem__(self, i):
                               return i * i''',
                       good='''
                           def __getitem__(self, i):
                               if i >= self.n:
                                   raise IndexError
                               return i * i'''),
               pitfall("`__bool__` возвращает только `bool`: иначе `TypeError: __bool__ should return bool, returned int`.",
                       bad="return len(self.letters)", good="return len(self.letters) > 0")]),
    ],
    tasks=[
        task("t_dunder_fraction", "Дроби",
             "Создайте класс Fraction(num, den) с методом __add__ и методом __str__, который печатает дробь в несократимом виде «a/b» (или просто «a», если знаменатель 1). Прочитайте строку «a/b c/d» и выведите сумму дробей.",
             solution="""\
                from math import gcd

                class Fraction:
                    def __init__(self, num, den):
                        g = gcd(num, den)
                        self.num, self.den = num // g, den // g
                    def __add__(self, other):
                        return Fraction(self.num * other.den + other.num * self.den, self.den * other.den)
                    def __str__(self):
                        return str(self.num) if self.den == 1 else f"{self.num}/{self.den}"

                a, b = (Fraction(*map(int, part.split("/"))) for part in input().split())
                print(a + b)""",
             starter="""\
                class Fraction:
                    def __init__(self, num, den):
                        self.num, self.den = num, den

                a, b = (Fraction(*map(int, part.split("/"))) for part in input().split())
                print(a.num + b.num)""",
             tests=["1/2 1/3\n", "1/4 3/4\n", "2/6 1/6\n", "5/3 2/7\n"],
             hint="Сокращайте в __init__ через math.gcd.", difficulty=3,
             requires=dict(classes=["Fraction"], methods={"Fraction": ["__init__", "__add__", "__str__"]},
                           no_imports=["fractions"])),
    ],
    levels=[
        predict("py_dun_001", "Красивый вывод", """\
                class Point:
                    def __init__(self, x, y):
                        self.x, self.y = x, y

                    def __str__(self):
                        return f"({self.x}, {self.y})"

                print(Point(1, 2))""",
                ["Point(1, 2)", "1 2", "<Point object>"], position=0, topic="dunder_str",
                hint="print использует __str__.",
                explanation="print(obj) вызывает obj.__str__(), который возвращает «(1, 2)».",
                feedback={"Point(1, 2)": "Такой текст вернул бы __repr__, а здесь определён __str__.",
                          "1 2": "__str__ возвращает строку со скобками и запятой.",
                          "<Point object>": "Стандартный вид был бы без __str__. Здесь он определён."}),
        predict("py_dun_002", "str или repr", """\
                class Point:
                    def __init__(self, x, y):
                        self.x, self.y = x, y
                    def __str__(self):
                        return f"({self.x}, {self.y})"
                    def __repr__(self):
                        return f"Point({self.x}, {self.y})"

                p = Point(1, 2)
                print(p, [p])""",
                ["(1, 2) [(1, 2)]", "Point(1, 2) [Point(1, 2)]", "Point(1, 2) [(1, 2)]"], position=1,
                topic="dunder_str", hint="Внутри списка Python показывает repr элементов.",
                explanation="Сам объект печатается через __str__, а список показывает элементы через __repr__.",
                feedback={"(1, 2) [(1, 2)]": "Список использует __repr__ своих элементов.",
                          "Point(1, 2) [Point(1, 2)]": "print(p) вызывает __str__, если он есть.",
                          "Point(1, 2) [(1, 2)]": "Наоборот: снаружи __str__, в списке __repr__."}),
        fill("py_dun_003", "Равенство по сумме", "Сделайте так, чтобы == сравнивал суммы",
             """\
             class Money:
                 def __init__(self, amount):
                     self.amount = amount

                 def {{0}}(self, other):
                     return self.amount == other.amount

             print(Money(5) == Money(5))""", ["__eq__", "__equals__", "__cmp__", "__is__"], ["__eq__"],
             topic="dunder_ops", hint="eq — от equal.",
             explanation="Оператор == вызывает __eq__. С другими именами метод не используется, и == сравнивает объекты по идентичности — получилось бы False.",
             expect="True\n"),
        typed("py_dun_004", "Векторы", """\
              class Vec:
                  def __init__(self, x, y):
                      self.x, self.y = x, y
                  def __add__(self, o):
                      return Vec(self.x + o.x, self.y + o.y)
                  def __mul__(self, k):
                      return Vec(self.x * k, self.y * k)
                  def __repr__(self):
                      return f"Vec({self.x}, {self.y})"

              v = Vec(1, 2) + Vec(3, 4)
              print(v)
              print(v * 2)""",
              topic="dunder_ops", hint="+ вызывает __add__, * — __mul__.",
              explanation="Vec(1, 2) + Vec(3, 4) = Vec(4, 6); умножение на 2 даёт Vec(8, 12). print использует __repr__, так как __str__ нет."),
        match("py_dun_005", "Колода", ["len(d)", "d[0]", "d[-1]", "'K' in d", "list(reversed(d))"],
              setup="""\
                class Deck:
                    def __init__(self):
                        self.cards = ["A", "K", "Q"]
                    def __len__(self):
                        return len(self.cards)
                    def __getitem__(self, i):
                        return self.cards[i]
                d = Deck()""",
              topic="dunder_protocols", hint="__len__ и __getitem__ превращают объект в последовательность.",
              explanation="len вызывает __len__, индексы — __getitem__. in и reversed тоже работают через __getitem__ и __len__."),
        bug("py_dun_006", "Двойники в множестве", """\
            class Tag:
                def __init__(self, name):
                    self.name = name
                def __eq__(self, other):
                    return self.name == other.name
                def __hash__(self):
                    return id(self)

            tags = {Tag("py"), Tag("py")}
            print(len(tags))""", {6: "        return hash(self.name)"},
            prompt="Одинаковые теги должны считаться одним — программа должна вывести 1. Найдите строку с ошибкой",
            topic="dunder_ops", hint="Что должно быть у равных объектов?",
            explanation="Равные объекты обязаны иметь одинаковый хеш. id у разных объектов разный, поэтому множество даже не сравнивает их через __eq__. Хеш нужно считать от name.",
            role="challenge", difficulty=3),
        multi("py_dun_007", "Ложный объект", "В каких классах if X(): посчитает объект ложным?",
              ["class X:\n    def __len__(self):\n        return 0",
               "class X:\n    def __bool__(self):\n        return False",
               "class X:\n    pass",
               "class X:\n    def __len__(self):\n        return 3",
               "class X:\n    def __bool__(self):\n        return True\n    def __len__(self):\n        return 0"], [0, 1],
              check=lambda code: runs(f"{code}\nassert not X()"),
              topic="dunder_protocols", hint="__bool__ главнее __len__, а без обоих объект истинен.",
              explanation="Сначала проверяется __bool__, если его нет — __len__ (0 — ложь). Объект без них всегда истинен.",
              feedback={"class X:\n    pass": "Без __bool__ и __len__ объект истинен.",
                        "class X:\n    def __len__(self):\n        return 3": "Длина 3 — истина.",
                        "class X:\n    def __bool__(self):\n        return True\n    def __len__(self):\n        return 0": "Если есть __bool__, __len__ для истинности не используется."}),
        predict("py_dun_008", "Сортировка карт", """\
                class Card:
                    order = "6789TJQKA"
                    def __init__(self, rank):
                        self.rank = rank
                    def __lt__(self, other):
                        return self.order.index(self.rank) < self.order.index(other.rank)
                    def __repr__(self):
                        return self.rank

                print(sorted([Card("K"), Card("7"), Card("A"), Card("T")]))""",
                ["[A, K, T, 7]", "[7, A, K, T]", "TypeError"], position=1, topic="dunder_ops",
                hint="sorted сравнивает элементы оператором <, то есть __lt__.",
                explanation="__lt__ сравнивает позиции ранга в строке order: 7 < T < K < A. Для sorted этого достаточно.",
                role="practice", difficulty=3,
                feedback={"[A, K, T, 7]": "sorted сортирует по возрастанию: от младшей карты к старшей.",
                          "[7, A, K, T]": "Сравнение идёт не по алфавиту, а по позиции в строке order.",
                          "TypeError": "Для сортировки достаточно __lt__."}),
        predict("py_dun_010", "Сравнение с чужими", """\
                class Vec:
                    def __init__(self, x, y):
                        self.x, self.y = x, y
                    def __eq__(self, other):
                        if not isinstance(other, Vec):
                            return NotImplemented
                        return (self.x, self.y) == (other.x, other.y)

                print(Vec(1, 2) == Vec(1, 2), Vec(1, 2) == (1, 2), Vec(0, 0) in [0, "a"])""",
                ["True True False", "True False True", "AttributeError"], position=1, topic="dunder_ops",
                hint="NotImplemented говорит Python: «я не умею сравнивать с этим типом».",
                explanation="С другим Vec сравнение работает по полям. С кортежем и элементами списка __eq__ возвращает NotImplemented, Python пробует сравнение второго объекта, и в итоге == даёт False.",
                role="practice", difficulty=3,
                feedback={"True True False": "Кортеж — не Vec: __eq__ возвращает NotImplemented, и результат False.",
                          "True False True": "in сравнивает Vec(0, 0) с 0 и \"a\" через ==, а с ними __eq__ возвращает NotImplemented — значит, False.",
                          "AttributeError": "Так было бы без проверки isinstance: у кортежа и числа нет атрибута x."}),
        predict("py_dun_009", "Босс: вызываемый объект", """\
                class Multiplier:
                    def __init__(self, k):
                        self.k = k
                        self.calls = 0

                    def __call__(self, x):
                        self.calls += 1
                        return x * self.k

                triple = Multiplier(3)
                print(triple(2), triple(5), triple.calls)
                print(list(map(triple, [1, 2])), triple.calls)""",
                ["6 15 0\n[3, 6] 2", "6 15 2\n[3, 6] 2", "TypeError"], position=2, topic="dunder_protocols",
                hint="Каждый вызов triple(...) увеличивает calls. map тоже вызывает его.",
                explanation="После двух вызовов calls = 2. map вызывает объект ещё дважды, и к моменту печати calls = 4.",
                role="boss", difficulty=3,
                feedback={"6 15 0\n[3, 6] 2": "Аргументы print вычисляются слева направо: к моменту triple.calls вызовов уже два.",
                          "6 15 2\n[3, 6] 2": "map вызывает triple для каждого элемента: ещё два вызова.",
                          "TypeError": "__call__ делает объект вызываемым."}),
    ],
))

# --------------------------------------------------------------- attributes
MODULES.append(dict(
    id="properties", title="Свойства и методы класса", description="@property, @classmethod, @staticmethod",
    icon="🔐",
    topics=[
        topic("prop_property", "@property",
              "`@property` превращает метод в атрибут: его читают без скобок, а запись можно проверить в сеттере.",
              """
              Атрибут удобно читать: `user.age`, без скобок. Но иногда значение нужно вычислять на лету или проверять при записи. `@property` прячет метод за обычным обращением к атрибуту, и код снаружи не меняется.

              ## Как записать

              ```syntax
              class Класс:
                  @property
                  def имя(self):
                      return self._имя

                  @имя.setter
                  def имя(self, value):
                      проверка
                      self._имя = value
              ```

              - Обе функции называются так же, как свойство.
              - Значение хранится в атрибуте с подчёркиванием: `self._имя`.
              - Строка с `@` над `def` — [[deco_basics|декоратор]]: он заменяет функцию объектом-свойством.

              ## Чтение и запись

              - `obj.имя` вызывает первую функцию — геттер.
              - `obj.имя = 5` вызывает сеттер. В нём проверяют значение и при ошибке выбрасывают [[exc_raise|`ValueError`]].
              - Без сеттера присваивание даёт `AttributeError`: свойство только для чтения.

              Если в `__init__` написать `self.имя = значение`, сеттер сработает уже при создании объекта, и проверка не обойдётся.

              ## Вычисляемое свойство

              Свойство без своего атрибута вычисляется при каждом обращении: площадь из сторон, полное имя из имени и фамилии. Значение всегда актуально.

              Если вычисление дорогое, есть `functools.cached_property`. Оно считает значение при первом обращении и запоминает в объекте. Подходит, когда исходные данные не меняются.
              """,
              [("""\
                class User:
                    def __init__(self, first, last):
                        self.first = first
                        self.last = last

                    @property
                    def full(self):
                        return self.first + " " + self.last

                u = User("Ада", "Лавлейс")
                print(u.full)
                u.last = "Байрон"
                print(u.full)""",
                "Свойство пересчитывается при каждом обращении, скобки не нужны"),
               ("""\
                class Account:
                    @property
                    def balance(self):
                        return self._balance

                    @balance.setter
                    def balance(self, value):
                        self._balance = max(value, 0)

                acc = Account()
                acc.balance = 100
                print(acc.balance)
                acc.balance = -5
                print(acc.balance)""",
                "Присваивание прошло через сеттер: минус заменён нулём"),
               ("""\
                class Circle:
                    def __init__(self, r):
                        self.r = r
                    @property
                    def d(self):
                        return self.r * 2

                c = Circle(3)
                print(c.d)
                try:
                    c.d = 10
                except AttributeError as e:
                    print(e)""",
                "Без сеттера свойство только для чтения"),
               ("""\
                from functools import cached_property

                class Report:
                    @cached_property
                    def data(self):
                        print("считаю…")
                        return 42

                r = Report()
                print(r.data)
                print(r.data)""",
                "cached_property посчитал один раз, второй раз — из памяти")],
              [pitfall("Свойство читает само себя: `self.balance` снова вызывает свойство — `RecursionError`.",
                       bad="return self.balance", good="return self._balance"),
               pitfall("Сеттер под другим именем создаёт отдельное свойство, а исходное остаётся только для чтения.",
                       bad='''
                           @balance.setter
                           def set_balance(self, value):
                               self._balance = value''',
                       good='''
                           @balance.setter
                           def balance(self, value):
                               self._balance = value'''),
               pitfall("Свойство читают без скобок: `c.d()` даёт `TypeError: 'int' object is not callable`.",
                       bad="c.d()", good="c.d")]),
        topic("prop_classmethod", "@classmethod и @staticmethod",
              "`@classmethod` получает класс и обычно создаёт объекты, а `@staticmethod` — функция внутри класса без `self`.",
              """
              Не всякий метод работает с конкретным объектом. Иногда нужен второй способ создать объект — из строки или словаря. Иногда — вспомогательная функция, которая по смыслу относится к классу.

              ## Как записать

              ```syntax
              class Класс:
                  @classmethod
                  def метод_класса(cls, параметры):
                      return cls(аргументы)

                  @staticmethod
                  def статический(параметры):
                      действия
              ```

              ## Три вида методов

              | Вид | Первый параметр |
              |---|---|
              | обычный | {`self`} — объект |
              | {`@classmethod`} | {`cls`} — класс |
              | {`@staticmethod`} | нет |

              Методы класса и статические вызывают и через класс, и через объект. Обычный метод через класс без объекта не вызвать: в `Класс.m(2)` двойка попадёт в `self`, а для остальных параметров ничего не останется.

              ## Альтернативный конструктор

              Метод класса чаще всего создаёт объект из других данных: `User.from_dict(d)`. Объект создают через `cls(...)`, а не по имени класса. Тогда в подклассе тот же метод создаст объект подкласса.

              ## Статический метод

              Это обычная функция, помещённая в класс по смыслу. Она не получает ни объект, ни класс и не видит их атрибутов. Если функции класс не нужен совсем, её можно вынести на уровень модуля.
              """,
              [("""\
                class Temp:
                    def __init__(self, c):
                        self.c = c

                    @classmethod
                    def from_f(cls, f):
                        return cls((f - 32) * 5 / 9)

                t = Temp.from_f(212)
                print(t.c)""",
                "Метод класса создал объект из градусов Фаренгейта"),
               ("""\
                class Shape:
                    @classmethod
                    def empty(cls):
                        return cls()

                class Square(Shape):
                    pass

                s = Square.empty()
                print(type(s).__name__)""",
                "Через cls подкласс получил объект своего типа"),
               ("""\
                class Password:
                    @staticmethod
                    def strong(text):
                        return len(text) >= 8

                print(Password.strong("qwerty"))
                p = Password()
                print(p.strong("correct-horse"))""",
                "Статический метод вызывается и через класс, и через объект")],
              [pitfall("Имя класса вместо `cls`: подкласс получит объект родителя.",
                       bad="return User(data[\"name\"])", good="return cls(data[\"name\"])"),
               pitfall("Без `@classmethod` класс не передаётся: `TypeError: … missing 1 required positional argument`.",
                       bad='''
                           def from_f(cls, f):
                               return cls((f - 32) * 5 / 9)''',
                       good='''
                           @classmethod
                           def from_f(cls, f):
                               return cls((f - 32) * 5 / 9)'''),
               pitfall("У статического метода нет `self`: обращение к `self.x` даёт `NameError`.",
                       bad='''
                           @staticmethod
                           def show():
                               return self.x''',
                       good='''
                           def show(self):
                               return self.x''')]),
        topic("prop_private", "Приватность и __slots__",
              "Подчёркивание в начале имени помечает атрибут как внутренний, а `__slots__` фиксирует набор атрибутов объекта.",
              """
              У класса есть атрибуты для внешнего кода и служебные — для внутренних расчётов. Python не запрещает доступ ни к тем, ни к другим. Но по имени видно, что трогать снаружи не стоит.

              ## Одно подчёркивание

              `self._cache` — соглашение: «внутреннее, снаружи не использовать». Python ничего не проверяет, но программисты и редакторы кода это правило соблюдают. `from модуль import *` не импортирует имена, начинающиеся с `_`.

              ## Два подчёркивания

              `self.__code` внутри класса `Safe` Python переименовывает в `_Safe__code`. Это называют искажением имени. Оно защищает от случайного совпадения имён в подклассах, а не от чтения: по полному имени атрибут доступен.

              Имена с подчёркиваниями и в конце, как `__init__`, не искажаются.

              ## __slots__

              `__slots__ = ("x", "y")` в теле класса фиксирует набор атрибутов объекта. Другой атрибут создать нельзя: `AttributeError`. У таких объектов нет словаря атрибутов, поэтому они занимают меньше памяти. Это заметно, когда объектов миллионы, — см. тему [[perf_tricks|Быстрые идиомы и память]].

              ## Что выбрать

              - `_имя` — по умолчанию для служебных атрибутов.
              - `__имя` — если класс рассчитан на наследование и имя может совпасть с именем в подклассе.
              - Проверку при записи делают через [[prop_property|`@property`]].
              """,
              [("""\
                class Counter:
                    def __init__(self):
                        self._n = 0
                    def tick(self):
                        self._n += 1
                        return self._n

                c = Counter()
                c.tick()
                print(c.tick())
                print(c._n)""",
                "_n доступен снаружи: подчёркивание — только договорённость"),
               ("""\
                class Base:
                    def __init__(self):
                        self.__id = "base"

                class Child(Base):
                    def __init__(self):
                        super().__init__()
                        self.__id = "child"

                c = Child()
                print(c._Base__id)
                print(c._Child__id)""",
                "Два __id не столкнулись: у каждого класса своё имя"),
               ("""\
                class Pixel:
                    __slots__ = ("x", "y")
                    def __init__(self, x, y):
                        self.x = x
                        self.y = y

                p = Pixel(1, 2)
                try:
                    p.color = "red"
                except AttributeError as e:
                    print(e)""",
                "Атрибута color нет в __slots__ — создать его нельзя")],
              [pitfall("Снаружи `safe.__code` не найдётся: имя искажено в `_Safe__code`, будет `AttributeError`. Дайте свойство для чтения.",
                       bad="print(safe.__code)",
                       good='''
                           class Safe:
                               @property
                               def code(self):
                                   return self.__code

                           print(safe.code)'''),
               pitfall("Атрибут, которого нет в `__slots__`, нельзя создать даже в `__init__`: `AttributeError`.",
                       bad='''
                           __slots__ = ("x",)
                           def __init__(self, x, y):
                               self.x, self.y = x, y''',
                       good='''
                           __slots__ = ("x", "y")
                           def __init__(self, x, y):
                               self.x, self.y = x, y''')]),
    ],
    tasks=[
        task("t_prop_temperature", "Термометр",
             "Создайте класс Thermometer со свойством celsius (с проверкой: не ниже -273.15, иначе ValueError) и свойством fahrenheit только для чтения. Прочитайте числа через пробел; для каждого выведите градусы Фаренгейта с одним знаком после запятой или «ошибка», если значение недопустимо.",
             solution="""\
                class Thermometer:
                    def __init__(self, celsius):
                        self.celsius = celsius

                    @property
                    def celsius(self):
                        return self._celsius

                    @celsius.setter
                    def celsius(self, value):
                        if value < -273.15:
                            raise ValueError("слишком холодно")
                        self._celsius = value

                    @property
                    def fahrenheit(self):
                        return self._celsius * 9 / 5 + 32

                for x in input().split():
                    try:
                        print(f"{Thermometer(float(x)).fahrenheit:.1f}")
                    except ValueError:
                        print("ошибка")""",
             starter="""\
                class Thermometer:
                    def __init__(self, celsius):
                        self.celsius = celsius

                for x in input().split():
                    print(Thermometer(float(x)).celsius)""",
             tests=["0 100 -40\n", "36.6\n", "-300 20\n", "-273.15 -273.16\n"],
             hint="Конструктор присваивает self.celsius — проверка в сеттере сработает и там.", difficulty=3,
             requires=dict(classes=["Thermometer"], uses=["property", "raise"])),
    ],
    levels=[
        predict("py_prop_001", "Вычисляемый атрибут", """\
                class Rect:
                    def __init__(self, w, h):
                        self.w, self.h = w, h

                    @property
                    def area(self):
                        return self.w * self.h

                r = Rect(2, 3)
                r.w = 5
                print(r.area)""",
                ["6", "<bound method>", "TypeError"], position=1, topic="prop_property",
                hint="Свойство вычисляется заново при каждом обращении.",
                explanation="r.area вызывает метод area без скобок. К этому моменту w = 5, поэтому площадь 5 · 3 = 15.",
                feedback={"6": "Свойство не запоминает значение: оно считает площадь в момент обращения, когда w уже 5.",
                          "<bound method>": "@property делает так, что r.area возвращает результат, а не сам метод.",
                          "TypeError": "Скобки не нужны: area — свойство."}),
        fill("py_prop_002", "Проверка при записи", "Добавьте сеттер для свойства c",
             """\
             class Temp:
                 def __init__(self):
                     self._c = 0

                 @property
                 def c(self):
                     return self._c

                 @c.{{0}}
                 def c(self, value):
                     if value < -273:
                         raise ValueError("ниже абсолютного нуля")
                     self._c = value

             t = Temp()
             t.c = 25
             print(t.c)""", ["setter", "getter", "deleter", "property"], ["setter"],
             topic="prop_property", hint="Метод для записи значения.",
             explanation="@c.setter регистрирует функцию, которая вызывается при t.c = 25. Без сеттера присваивание даёт AttributeError.",
             expect="25\n"),
        typed("py_prop_003", "Альтернативный конструктор", """\
              class Date:
                  def __init__(self, y, m, d):
                      self.y, self.m, self.d = y, m, d

                  @classmethod
                  def parse(cls, text):
                      d, m, y = map(int, text.split("."))
                      return cls(y, m, d)

                  def __str__(self):
                      return f"{self.y}-{self.m:02}-{self.d:02}"

              print(Date.parse("05.03.2024"))
              print(Date(2024, 12, 1))""",
              topic="prop_classmethod", hint=":02 дополняет число нулём до двух цифр.",
              explanation="parse разбирает «день.месяц.год» и создаёт Date через cls. __str__ печатает год-месяц-день с ведущими нулями."),
        match("py_prop_004", "Виды методов",
              ["def m(self)", "@classmethod def m(cls)", "@staticmethod def m()", "@property def m(self)"],
              rights=["Метод объекта: получает экземпляр", "Получает класс: альтернативные конструкторы",
                      "Не получает ни объект, ни класс", "Читается как атрибут, без скобок"],
              prompt="Сопоставьте объявление и его смысл", topic="prop_classmethod",
              hint="Смотрите на первый параметр.",
              explanation="Обычный метод получает self, метод класса — cls, статический — ничего, а свойство вызывается без скобок."),
        bug("py_prop_005", "Бесконечное свойство", """\
            class User:
                def __init__(self, name):
                    self._name = name
                @property
                def name(self):
                    return self.name.title()

            print(User("ada lovelace").name)""", {5: "        return self._name.title()"},
            prompt="Найдите строку с ошибкой", topic="prop_property",
            hint="Что происходит, когда свойство name читает self.name?",
            explanation="self.name снова вызывает свойство name, и так бесконечно — RecursionError. Значение хранится в self._name.",
            expect_error="RecursionError"),
        predict("py_prop_006", "Искажение имени", """\
                class Vault:
                    def __init__(self):
                        self.__pin = 1234

                v = Vault()
                print(hasattr(v, "__pin"), hasattr(v, "_Vault__pin"))""",
                ["True False", "True True", "False False"], position=0, topic="prop_private",
                hint="Два подчёркивания в начале имени внутри класса меняют его название.",
                explanation="self.__pin внутри класса Vault сохраняется под именем _Vault__pin. Атрибута __pin у объекта нет, а по искажённому имени он есть — значит, это не настоящая защита.",
                role="challenge", difficulty=3,
                feedback={"True False": "Наоборот: имя искажено в _Vault__pin.",
                          "True True": "Атрибута с именем «__pin» нет: имя искажено.",
                          "False False": "Под искажённым именем _Vault__pin атрибут существует."}),
        multi("py_prop_007", "Как вызвать", "Какие вызовы сработают?",
              ["M.st(2)", "M().st(2)", "M.cm(2)", "M.inst(2)", "M().inst(2)"], [0, 1, 2, 4],
              code="""\
                class M:
                    @staticmethod
                    def st(x):
                        return x

                    @classmethod
                    def cm(cls, x):
                        return x

                    def inst(self, x):
                        return x""",
              check=lambda call: runs("class M:\n    @staticmethod\n    def st(x):\n        return x\n"
                                      "    @classmethod\n    def cm(cls, x):\n        return x\n"
                                      f"    def inst(self, x):\n        return x\nassert {call} == 2"),
              topic="prop_classmethod", hint="Обычному методу нужен объект.",
              explanation="Статические методы и методы класса работают и через класс, и через объект. Обычный метод через класс без объекта не получит self: M.inst(2) — TypeError.",
              feedback={"M.inst(2)": "2 попадёт в self, а для x значения не останется: TypeError."}),
        predict("py_prop_010", "Сеттер не того имени", """\
                class Temp:
                    def __init__(self):
                        self._c = 0
                    @property
                    def c(self):
                        return self._c
                    @c.setter
                    def set_c(self, value):
                        self._c = value

                t = Temp()
                try:
                    t.c = 25
                except AttributeError:
                    print("нет сеттера")
                print(t.c)""",
                ["25", "нет сеттера\n25", "AttributeError"], position=3, topic="prop_property",
                hint="Сеттер привязан к свойству с тем именем, под которым объявлена функция.",
                explanation="@c.setter над def set_c создаёт новое свойство set_c, а у c сеттера так и нет. t.c = 25 даёт AttributeError, значение остаётся 0.",
                role="practice", difficulty=3,
                feedback={"25": "Сеттер объявлен под именем set_c, поэтому c остаётся только для чтения.",
                          "нет сеттера\n25": "Присваивание не выполнилось — значение осталось 0.",
                          "AttributeError": "Ошибка перехвачена except и программа продолжается."}),
        choice("py_prop_008", "__slots__", "Что произойдёт при p.z = 3?",
               ["Появится атрибут z", "AttributeError", "z запишется в __slots__", "Ничего, присваивание проигнорируется"], 1,
               code="""\
                class P:
                    __slots__ = ("x", "y")
                    def __init__(self, x, y):
                        self.x, self.y = x, y

                p = P(1, 2)
                p.z = 3""",
               check=lambda option: (option == "AttributeError") == (
                   result_of("class P:\n    __slots__ = ('x', 'y')\n    def __init__(self, x, y):\n"
                             "        self.x, self.y = x, y\np = P(1, 2)\np.z = 3") == "AttributeError"),
               topic="prop_private", hint="__slots__ фиксирует набор атрибутов.",
               explanation="Объекты с __slots__ не имеют __dict__ и могут хранить только перечисленные атрибуты. Новый атрибут вызывает AttributeError.",
               role="practice", difficulty=2,
               feedback={"Появится атрибут z": "Так было бы без __slots__.",
                         "z запишется в __slots__": "__slots__ задаётся при создании класса и не меняется.",
                         "Ничего, присваивание проигнорируется": "Python не игнорирует ошибки молча."}),
        order("py_prop_009", "Босс: счётчик билетов", "Соберите класс так, чтобы программа вывела 2 2",
              ["class Ticket:", "    issued = 0", "    def __init__(self):", "        Ticket.issued += 1",
               "        self.number = Ticket.issued", "a, b = Ticket(), Ticket()", "print(b.number, Ticket.issued)"],
              topic="oop_class_attrs", hint="Счётчик общий для класса, номер — у каждого билета свой.",
              explanation="issued — атрибут класса: каждый новый билет увеличивает его и запоминает текущее значение как свой number. Второй билет получает номер 2.",
              role="boss", difficulty=3),
    ],
))

# --------------------------------------------------------- dataclasses/enum
MODULES.append(dict(
    id="dataclasses", title="Dataclasses и Enum", description="Классы данных и перечисления", icon="🗃️",
    topics=[
        topic("dc_basics", "@dataclass",
              "`@dataclass` по списку полей сам пишет классу `__init__`, `__repr__` и `__eq__`.",
              """
              Многие классы просто хранят данные: товар, точка, строка таблицы. Для них приходится писать однотипные `__init__`, `__repr__` и `__eq__`. Декоратор `@dataclass` пишет их сам по списку полей.

              ## Как записать

              ```syntax
              from dataclasses import dataclass, field

              @dataclass
              class Имя:
                  поле: тип
                  поле_со_значением: тип = значение
                  список: list = field(default_factory=list)
              ```

              - Тип поля обязателен: по [[typing_basics|аннотациям]] декоратор находит поля. Сам тип Python не проверяет.
              - Поля без значения по умолчанию идут раньше полей со значением.

              Изменяемое значение по умолчанию ({`[]`}, `{}`) запрещено: будет `ValueError`. Вместо него пишут `field(default_factory=list)`, и каждый объект получает свой список.

              ## Что пишется само

              - `__init__` с параметрами в порядке полей;
              - `__repr__` вида `Item(name='чай', qty=2)`;
              - `__eq__`: объекты равны, если равны все поля.

              ## Параметры декоратора

              | Параметр | Что даёт |
              |---|---|
              | {`order=True`} | {`<`} и {`>`} по полям |
              | {`frozen=True`} | запрет изменений и хеш |
              | {`slots=True`} | {`__slots__`} |
              | {`kw_only=True`} | поля только по имени |

              Обычный `@dataclass` нехешируем: из-за `__eq__` у него `__hash__ = None`, и объект нельзя положить в `set`. С `frozen=True` можно.

              ## Проверки и копии

              - `__post_init__(self)` вызывается сразу после созданного `__init__` — место для проверок;
              - `replace(obj, поле=значение)` — копия с изменёнными полями;
              - `asdict(obj)` — словарь из полей, удобно для [[data_json|JSON]].
              """,
              [("""\
                from dataclasses import dataclass

                @dataclass
                class Item:
                    name: str
                    qty: int = 1

                a = Item("чай", 2)
                print(a)
                print(a == Item("чай", 2))
                print(Item("хлеб"))""",
                "repr, == и значение по умолчанию написал декоратор"),
               ("""\
                from dataclasses import dataclass

                @dataclass
                class Order:
                    total: int
                    def __post_init__(self):
                        if self.total < 0:
                            raise ValueError("сумма < 0")

                print(Order(100))
                try:
                    Order(-5)
                except ValueError as e:
                    print("ошибка:", e)""",
                "__post_init__ проверил сумму сразу после создания"),
               ("""\
                from dataclasses import dataclass
                from dataclasses import replace, asdict

                @dataclass(frozen=True, order=True)
                class Move:
                    turn: int
                    cell: str

                a = Move(1, "e4")
                print(a < Move(2, "d5"))
                print(replace(a, cell="e5"))
                print(asdict(a))""",
                "order сравнил по turn, replace сделал копию, asdict — словарь")],
              [pitfall("Список по умолчанию: `ValueError: mutable default <class 'list'> for field tags is not allowed`.",
                       bad="tags: list = []", good="tags: list = field(default_factory=list)"),
               pitfall("Поле без значения после поля со значением: `TypeError: non-default argument 'name' follows …`.",
                       bad='''
                           qty: int = 1
                           name: str''',
                       good='''
                           name: str
                           qty: int = 1'''),
               pitfall("Поля `frozen`-объекта не меняют: `FrozenInstanceError`. Создают копию через `replace`.",
                       bad="a.turn = 2", good="a = replace(a, turn=2)"),
               pitfall("Ждать проверки типов: `Item(\"чай\", \"много\")` создастся без ошибки. Проверяйте в `__post_init__`.")]),
        topic("dc_enum", "Enum",
              "`Enum` — набор именованных констант: вместо строк и чисел-«кодов» используются элементы с именем и значением.",
              """
              Статус заказа, уровень сложности, цвет фигуры — значения из короткого фиксированного списка. Строку вроде `"new"` легко написать с опечаткой, и ошибку никто не заметит. `Enum` превращает такой список в набор именованных констант.

              ## Как записать

              ```syntax
              from enum import Enum, auto

              class Имя(Enum):
                  ЭЛЕМЕНТ = значение
                  ДРУГОЙ = auto()
              ```

              - Имена элементов пишут заглавными буквами, как константы.
              - `auto()` подставляет значения сам: 1, 2, 3…

              ## Что умеет элемент

              - `Color.RED.name` — имя, строка `"RED"`;
              - `Color.RED.value` — значение;
              - `Color(1)` — элемент по значению;
              - {`Color["RED"]`} — элемент по имени;
              - `for c in Color`, `len(Color)` — перебор и количество.

              Каждый элемент существует в одном экземпляре, поэтому сравнивать можно и через `is`, и через `==`.

              ## Почему не строки

              Опечатка `Status.DONEE` сразу даёт `AttributeError`, а строка `"donee"` молча пройдёт все проверки. Редактор кода подсказывает возможные элементы. Элементы удобно разбирать в [[idiom_match|`match`]].

              ## Enum, IntEnum, StrEnum, Flag

              Элемент обычного `Enum` не равен своему значению и не сравнивается через `<`. `IntEnum` и `StrEnum` — подклассы `int` и `str`: их элементы ведут себя как числа и строки. `Flag` позволяет объединять элементы через `|`.
              """,
              [("""\
                from enum import Enum

                class Level(Enum):
                    EASY = 1
                    HARD = 2

                lv = Level.HARD
                print(lv)
                print(lv.name)
                print(lv.value)""",
                "Элемент печатается с именем класса; name и value — его части"),
               ("""\
                from enum import Enum, auto

                class Step(Enum):
                    CART = auto()
                    PAY = auto()
                    SHIP = auto()

                print(Step(2))
                print(Step["SHIP"].value)
                for s in Step:
                    print(s.name)""",
                "auto() пронумеровал с 1; поиск по значению и по имени"),
               ("""\
                from enum import Enum

                class Mode(Enum):
                    READ = "r"
                    WRITE = "w"

                print(Mode.READ == "r")
                print(Mode("r") is Mode.READ)
                try:
                    Mode.REED
                except AttributeError:
                    print("нет элемента REED")""",
                "Элемент не равен значению, а опечатка видна сразу")],
              [pitfall("Элемент `Enum` не равен своему значению: `Status.NEW == 1` даёт `False`.",
                       bad="is_new = status == 1", good="is_new = status is Status.NEW"),
               pitfall("Элементы обычного `Enum` не сравниваются через `<`: `TypeError: '<' not supported`.",
                       bad="Level.EASY < Level.HARD", good="Level.EASY.value < Level.HARD.value")]),
    ],
    tasks=[
        task("t_dc_inventory", "Склад",
             "Объявите dataclass Item(name: str, qty: int, price: float). Прочитайте n и n строк «название количество цена». Выведите общую стоимость склада (ровно с двумя знаками после точки) и название позиции с наибольшей стоимостью (qty * price); при равенстве — первую по порядку ввода.",
             solution="""\
                from dataclasses import dataclass

                @dataclass
                class Item:
                    name: str
                    qty: int
                    price: float

                    @property
                    def total(self):
                        return self.qty * self.price

                items = []
                for _ in range(int(input())):
                    name, qty, price = input().split()
                    items.append(Item(name, int(qty), float(price)))
                print(f"{sum(i.total for i in items):.2f}")
                print(max(items, key=lambda i: i.total).name)""",
             starter="""\
                from dataclasses import dataclass

                @dataclass
                class Item:
                    name: str
                    qty: int
                    price: float

                for _ in range(int(input())):
                    print(input())""",
             tests=["2\nчай 10 2.5\nкофе 3 12\n", "1\nхлеб 2 40\n", "3\na 1 1\nb 2 2\nc 1 3.5\n",
                    "2\nx 0 100\ny 1 0.5\n"],
             hint="Стоимость позиции удобно сделать свойством.", difficulty=2,
             requires=dict(classes=["Item"], uses=["dataclass"])),
    ],
    levels=[
        predict("py_dc_001", "Автоматический repr", """\
                from dataclasses import dataclass

                @dataclass
                class Point:
                    x: int
                    y: int = 0

                print(Point(3))""",
                ["Point(3)", "(3, 0)", "<Point object>"], position=3, topic="dc_basics",
                hint="dataclass сам пишет __repr__ с именами полей.",
                explanation="@dataclass создаёт __init__ (y по умолчанию 0) и __repr__ вида Point(x=3, y=0).",
                feedback={"Point(3)": "repr dataclass показывает все поля с именами.",
                          "(3, 0)": "Это не кортеж, а объект Point с понятным repr.",
                          "<Point object>": "dataclass автоматически создаёт __repr__."}),
        predict("py_dc_002", "Равенство полей", """\
                from dataclasses import dataclass

                @dataclass
                class Point:
                    x: int
                    y: int

                print(Point(1, 2) == Point(1, 2), Point(1, 2) is Point(1, 2))""",
                ["False False", "True True", "False True"], position=1, topic="dc_basics",
                hint="== сравнивает поля, is — один ли это объект.",
                explanation="dataclass создаёт __eq__, сравнивающий поля, поэтому == даёт True. Но это два разных объекта: is — False.",
                feedback={"False False": "dataclass добавляет __eq__ по полям.",
                          "True True": "Два вызова Point(...) создают два разных объекта.",
                          "False True": "Разные объекты не могут быть is-идентичны."}),
        fill("py_dc_003", "Свой список у каждого", "Сделайте так, чтобы у каждой корзины был свой список",
             """\
             from dataclasses import dataclass, field

             @dataclass
             class Cart:
                 items: list = field({{0}}=list)

             a, b = Cart(), Cart()
             a.items.append("чай")
             print(len(a.items), len(b.items))""", ["default_factory", "default", "factory", "init"],
             ["default_factory"], topic="dc_basics", hint="Нужна функция, которая создаёт новое значение для каждого объекта.",
             explanation="default_factory=list вызывает list() для каждого нового объекта. default=list сделал бы значением сам тип list.",
             expect="1 0\n"),
        bug("py_dc_004", "Запрещённое значение", """\
            from dataclasses import dataclass, field

            @dataclass
            class Team:
                name: str
                members: list = []

            print(Team("A").members)""", {5: "    members: list = field(default_factory=list)"},
            prompt="Найдите строку с ошибкой", topic="dc_basics",
            hint="Можно ли в dataclass указать изменяемое значение по умолчанию?",
            explanation="dataclass запрещает изменяемые значения по умолчанию (list, dict, set): ValueError при объявлении класса. Нужен field(default_factory=list).",
            expect_error="ValueError"),
        typed("py_dc_005", "Сортировка версий", """\
              from dataclasses import dataclass

              @dataclass(order=True)
              class Version:
                  major: int
                  minor: int

              vs = [Version(1, 10), Version(1, 2), Version(0, 9)]
              print(max(vs))
              print([f"{v.major}.{v.minor}" for v in sorted(vs)])""",
              topic="dc_basics", hint="order=True сравнивает поля по очереди: сначала major, потом minor — как числа.",
              explanation="Сравнение идёт как у кортежей (major, minor): (1, 10) > (1, 2) > (0, 9). Числа сравниваются численно, поэтому 1.10 больше 1.2."),
        predict("py_dc_006", "Перечисление", """\
                from enum import Enum

                class Color(Enum):
                    RED = 1
                    GREEN = 2

                print(Color.RED, Color.RED.name, Color.RED.value, Color(2))""",
                ["RED RED 1 GREEN", "1 RED 1 2", "Color.RED red 1 Color.GREEN"], position=0, topic="dc_enum",
                hint="print элемента Enum показывает Класс.ИМЯ.",
                explanation="str(Color.RED) — «Color.RED», name — «RED», value — 1, а Color(2) находит элемент по значению.",
                feedback={"RED RED 1 GREEN": "Элемент печатается вместе с именем класса: Color.RED.",
                          "1 RED 1 2": "print элемента показывает имя, а не значение.",
                          "Color.RED red 1 Color.GREEN": "name возвращает имя как в коде — заглавными."}),
        multi("py_dc_007", "Неизменяемый", "Какие операции с p вызовут ошибку?",
              ["p.x = 5", "P(1) == P(1)", "hash(P(1))", "del p.x", "replace(p, x=2)"], [0, 3],
              code="""\
                from dataclasses import dataclass, replace

                @dataclass(frozen=True)
                class P:
                    x: int

                p = P(1)""",
              check=lambda op: not runs("from dataclasses import dataclass, replace\n"
                                        "@dataclass(frozen=True)\nclass P:\n    x: int\np = P(1)\n" + op),
              topic="dc_basics", hint="frozen запрещает менять объект, но не создавать новые.",
              explanation="Присваивание и удаление атрибута у frozen-объекта дают FrozenInstanceError. Сравнение и хеш работают, а replace создаёт новый объект.",
              feedback={"P(1) == P(1)": "Сравнение ничего не меняет — работает.",
                        "hash(P(1))": "frozen dataclass как раз хешируемый.",
                        "replace(p, x=2)": "replace не меняет p, а создаёт новый объект."}),
        multi("py_dc_010", "В множество", "Объекты каких dataclass-классов можно положить в set?",
              ["@dataclass", "@dataclass(frozen=True)", "@dataclass(eq=False)", "@dataclass(order=True)"], [1, 2],
              check=lambda deco: runs(f"from dataclasses import dataclass\n{deco}\nclass P:\n    x: int\n{{P(1)}}"),
              topic="dc_basics", hint="Обычный dataclass определяет __eq__ — и поэтому убирает __hash__.",
              explanation="С eq=True (по умолчанию) dataclass ставит __hash__ = None. frozen=True делает объект неизменяемым и добавляет хеш по полям, eq=False оставляет хеш по идентичности.",
              feedback={"@dataclass": "Обычный dataclass нехешируем: TypeError unhashable type.",
                        "@dataclass(order=True)": "order добавляет сравнения, но хеша по-прежнему нет."}),
        match("py_dc_011", "Виды перечислений", ["Lang.PY + \"thon\"", "Level.LOW + 1", "Color.RED == 1",
                                                 "(Perm.R | Perm.W).value", "Perm.W in (Perm.R | Perm.W)"],
              setup="""\
                from enum import Enum, IntEnum, StrEnum, Flag

                class Lang(StrEnum):
                    PY = "py"
                class Level(IntEnum):
                    LOW = 1
                class Color(Enum):
                    RED = 1
                class Perm(Flag):
                    R = 1
                    W = 2""",
              rights=None, topic="dc_enum",
              hint="StrEnum и IntEnum ведут себя как строка и число, обычный Enum — нет. Flag можно объединять через |.",
              explanation="StrEnum и IntEnum — подклассы str и int: с ними работают операции строк и чисел. Элемент обычного Enum не равен своему значению. Flag объединяет флаги: R | W имеет значение 3, и W входит в эту комбинацию.",
              role="practice", difficulty=3),
        match("py_dc_008", "Enum изнутри", ["Status.NEW.value", "Status['DONE']", "len(Status)",
                                            "[s.name for s in Status]", "Status.NEW is Status(1)"],
              setup="""\
                from enum import Enum, auto
                class Status(Enum):
                    NEW = auto()
                    DONE = auto()""",
              topic="dc_enum", hint="auto() нумерует с 1.",
              explanation="auto даёт значения 1 и 2. Status['DONE'] ищет по имени, Status(1) — по значению; элементы Enum единственны, поэтому is даёт True."),
        order("py_dc_009", "Босс: задачи по приоритету", "Соберите программу, которая выведет «тесты, код»",
              ["from dataclasses import dataclass", "@dataclass(order=True)", "class Task:", "    priority: int",
               "    title: str", "tasks = sorted([Task(2, \"код\"), Task(1, \"тесты\")])",
               "print(\", \".join(t.title for t in tasks))"],
              topic="dc_basics", hint="Порядок полей определяет порядок сравнения.",
              explanation="order=True сравнивает сначала priority, затем title. Задача с приоритетом 1 идёт первой.",
              role="boss", difficulty=3),
    ],
))
