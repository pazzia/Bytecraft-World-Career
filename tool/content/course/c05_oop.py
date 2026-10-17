"""Модули 22–26: классы и объекты, наследование, магические методы,
свойства и методы класса, dataclasses и enum."""
from bclib import choice, fill, match, multi, order, predict, bug, typed, topic, task, run


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
              "Класс — шаблон, объект — экземпляр. __init__ настраивает новый объект, self — ссылка на этот объект.",
              """
              class Dog: объявляет класс. Dog("Рекс") создаёт объект: Python вызывает __init__(self, "Рекс"), где self — только что созданный объект.

              Атрибуты объекта создаются присваиванием self.name = name. У каждого объекта свои значения атрибутов.

              Методы — функции внутри класса. Первый параметр — self: при вызове d.bark() Python сам передаёт d как self. Внутри метода к атрибутам обращаются только через self: просто name — это была бы обычная (несуществующая) переменная.
              """,
              [("""\
                class Dog:
                    def __init__(self, name):
                        self.name = name

                    def bark(self):
                        return f"{self.name}: Гав!"

                a = Dog("Рекс")
                b = Dog("Шарик")
                print(a.bark(), b.bark())""", "У каждого объекта своё имя.")],
              ["Забыть self в списке параметров метода: TypeError takes 0 positional arguments but 1 was given.",
               "Писать name вместо self.name внутри метода: NameError — или, что хуже, метод молча возьмёт глобальную переменную с тем же именем."]),
        topic("oop_class_attrs", "Атрибуты класса и объекта",
              "Атрибут класса общий для всех объектов, атрибут объекта (self.x) — у каждого свой.",
              """
              Переменная, объявленная прямо в теле класса (wheels = 4), принадлежит классу. Объект видит её, если у него нет своего атрибута с тем же именем.

              Присваивание obj.wheels = 3 создаёт атрибут объекта и «закрывает» атрибут класса только для этого объекта.

              Опасно хранить в атрибуте класса изменяемый список: append через любой объект меняет общий список для всех.
              """,
              [("""\
                class Car:
                    wheels = 4

                a, b = Car(), Car()
                b.wheels = 3
                print(a.wheels, b.wheels, Car.wheels)""", None)],
              ["members = [] в теле класса вместо self.members = [] в __init__: список общий для всех объектов.",
               "self.count += 1 для атрибута класса не меняет класс: это чтение атрибута класса и создание атрибута объекта. Счётчик класса меняют через ИмяКласса.count."]),
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
              "class B(A) наследует методы A. Метод с тем же именем в B переопределяет метод A; super() вызывает версию родителя.",
              """
              Подкласс получает все методы и атрибуты класса-родителя и может добавить свои или заменить существующие.

              Наследование выражает отношение «является» (студент — человек). Если объект просто использует другой («у машины есть двигатель»), лучше композиция: хранить объект в атрибуте. Подкласс должен работать везде, где работает родитель (принцип подстановки Лисков): квадрат, у которого нельзя отдельно менять ширину, — плохой подкласс прямоугольника.

              Если в подклассе есть свой __init__, родительский __init__ сам не вызывается. Его вызывают явно: super().__init__(...), иначе атрибуты, которые настраивает родитель, не появятся.

              Атрибуты класса тоже наследуются: если у подкласса нет своего, Python берёт атрибут родителя.
              """,
              [("""\
                class Person:
                    def __init__(self, name):
                        self.name = name

                class Student(Person):
                    def __init__(self, name, group):
                        super().__init__(name)
                        self.group = group

                s = Student("Ада", "П-1")
                print(s.name, s.group)""", None)],
              ["Забыть вызвать super().__init__(): у объекта не будет атрибутов родителя."]),
        topic("inh_poly", "Полиморфизм и утиная типизация",
              "Разные классы с одинаковым методом можно обрабатывать одним кодом. Python смотрит на наличие метода, а не на тип.",
              """
              Если у объектов есть метод area(), цикл for s in shapes: s.area() работает для любых фигур — каждая считает площадь по-своему.

              Утиная типизация: «если крякает как утка — это утка». Функции не важно, от какого класса объект, важно, что у него есть нужный метод.

              isinstance(obj, Cls) проверяет принадлежность классу с учётом наследования, issubclass(B, A) — родство классов. Все классы — наследники object.
              """,
              [("""\
                class Duck:
                    def sound(self):
                        return "кря"

                class Robot:
                    def sound(self):
                        return "бип"

                for x in [Duck(), Robot()]:
                    print(x.sound())""", None)],
              ["Проверять type(x) == A вместо isinstance(x, A): подклассы не пройдут проверку."]),
        topic("inh_mro", "Множественное наследование, MRO, ABC",
              "При нескольких родителях Python ищет методы в порядке MRO. Абстрактный класс (ABC) нельзя создать, пока не реализованы его абстрактные методы.",
              """
              class D(B, C): порядок поиска методов — D, B, C, затем общий предок. Посмотреть его можно в D.__mro__. super() вызывает следующий класс в MRO того объекта, для которого вызван метод, — а не обязательно прямого родителя.

              from abc import ABC, abstractmethod: метод, помеченный строкой @abstractmethod (это декоратор — пометка над функцией; подробно о них в отдельном модуле), обязан быть реализован в подклассе. Объявить подкласс без него можно, но создать объект такого класса нельзя: TypeError. Так задают интерфейс. Тело абстрактного метода часто пишут как ... (многоточие) — «здесь ничего нет».

              ABC требует явного наследования. Protocol из модуля typing описывает интерфейс «по форме» — без наследования (об этом — в модуле про аннотации типов).
              """,
              [("""\
                class A:
                    def who(self):
                        return "A"

                class B(A):
                    def who(self):
                        return "B" + super().who()

                class C(A):
                    def who(self):
                        return "C" + super().who()

                class D(B, C):
                    def who(self):
                        return "D" + super().who()

                print(D().who(), B().who(), [k.__name__ for k in D.__mro__])""", "Для объекта D super() в B вызывает C (следующий в D.__mro__); для объекта B — сразу A."),
               ("""\
                from abc import ABC, abstractmethod

                class Shape(ABC):
                    @abstractmethod
                    def area(self): ...

                class Square(Shape):
                    def __init__(self, a):
                        self.a = a
                    def area(self):
                        return self.a ** 2

                print(Square(3).area())
                try:
                    Shape()
                except TypeError:
                    print("абстрактный класс создать нельзя")""", None)],
              ["Думать, что super() всегда вызывает прямого родителя: он идёт по MRO."]),
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
               topic="inh_mro", hint="Зачем методу пометка @abstractmethod?",
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
              "__str__ — понятный текст для людей (print, str), __repr__ — точное представление для разработчиков (списки, отладка).",
              """
              print(obj) и str(obj) используют __str__. Если его нет — __repr__. Если нет и его, выводится что-то вроде <__main__.Point object at 0x…>.

              Внутри контейнеров (print([p])) и в интерактивной консоли всегда используется __repr__. Хорошая практика: __repr__ похож на код, создающий объект: Point(1, 2).

              f"{obj!r}" вставляет repr вместо str.
              """,
              [("""\
                class Money:
                    def __init__(self, amount):
                        self.amount = amount
                    def __str__(self):
                        return f"{self.amount} ₽"
                    def __repr__(self):
                        return f"Money({self.amount})"

                m = Money(5)
                print(m, [m], f"{m!r}")""", None)],
              ["Определить только __str__ и удивляться, что список объектов печатается непонятно."]),
        topic("dunder_ops", "Сравнение и операторы",
              "== вызывает __eq__, < — __lt__, + — __add__, * — __mul__. Равные объекты обязаны иметь равные хеши.",
              """
              Без __eq__ объекты равны, только если это один и тот же объект. Определив __eq__, вы задаёте равенство по содержимому.

              Если объявлен __eq__, Python убирает __hash__ — объект нельзя положить в множество или сделать ключом словаря, пока не определён __hash__. Правило: a == b ⇒ hash(a) == hash(b). Обычно hash считают от тех же полей, что сравниваются.

              sorted и min сравнивают через <, max — через >; если __gt__ нет, Python пробует отражённое сравнение other.__lt__(self), поэтому для всех троих хватает __lt__. functools.total_ordering достраивает остальные сравнения по __eq__ и __lt__.

              Если сравнение с объектом другого типа не имеет смысла, метод возвращает специальное значение NotImplemented — тогда Python попробует операцию другого объекта или вернёт False для ==. Иначе Vec(1, 2) == 5 упадёт на 5.x.

              __add__(self, other) возвращает новый объект и не меняет исходные.
              """,
              [("""\
                class Vec:
                    def __init__(self, x, y):
                        self.x, self.y = x, y
                    def __add__(self, other):
                        return Vec(self.x + other.x, self.y + other.y)
                    def __eq__(self, other):
                        if not isinstance(other, Vec):
                            return NotImplemented
                        return (self.x, self.y) == (other.x, other.y)
                    def __hash__(self):
                        return hash((self.x, self.y))
                    def __repr__(self):
                        return f"Vec({self.x}, {self.y})"

                print(Vec(1, 2) + Vec(3, 4), Vec(1, 1) == Vec(1, 1), len({Vec(1, 1), Vec(1, 1)}), Vec(1, 1) == 5)""", None)],
              ["__eq__ без __hash__: TypeError unhashable type при добавлении в set.",
               "__hash__ от id(self) при __eq__ по содержимому: равные объекты попадут в множество дважды."]),
        topic("dunder_protocols", "Протоколы: len, [], in, вызов, истинность",
              "__len__ — для len(), __getitem__ — для obj[i] и перебора, __contains__ — для in, __call__ — для obj(), __bool__ — для if obj.",
              """
              Объект с __len__ и __getitem__ ведёт себя как последовательность: работают len, индексы, срезы (если __getitem__ их поддерживает), for, in и reversed.

              __call__ делает объект вызываемым как функция — удобно для объектов с состоянием.

              Истинность: если есть __bool__, используется он; иначе __len__ (0 — ложь); иначе объект всегда истинен.
              """,
              [("""\
                class Playlist:
                    def __init__(self):
                        self.songs = ["intro", "verse", "outro"]
                    def __len__(self):
                        return len(self.songs)
                    def __getitem__(self, i):
                        return self.songs[i]

                p = Playlist()
                print(len(p), p[0], "verse" in p, p[1:], list(reversed(p)))""", "Срез тоже работает: __getitem__ передаёт его списку.")],
              ["Ждать, что пустой объект без __bool__ и __len__ будет ложным: он истинен."]),
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
              "@property превращает метод в атрибут только для чтения; @имя.setter добавляет проверку при записи.",
              """
              @property над методом area позволяет писать r.area без скобок: значение вычисляется при каждом обращении и всегда актуально.

              Сеттер (@c.setter) вызывается при присваивании t.c = 25 — в нём проверяют значение и сохраняют его во «внутренний» атрибут с подчёркиванием (self._c). Без сеттера присваивание даёт AttributeError. Функция-сеттер обязана называться так же, как свойство (def c), иначе получится отдельное свойство, а c останется только для чтения.

              functools.cached_property вычисляет значение один раз при первом обращении и запоминает его в объекте — для дорогих вычислений.

              Внутри свойства обращайтесь к _c, а не к c: иначе свойство вызовет само себя бесконечно (RecursionError).

              Строка с @ над функцией — декоратор. Как они устроены, разберём в отдельном модуле.
              """,
              [("""\
                class Temp:
                    def __init__(self, c):
                        self.c = c

                    @property
                    def c(self):
                        return self._c

                    @c.setter
                    def c(self, value):
                        if value < -273.15:
                            raise ValueError("ниже абсолютного нуля")
                        self._c = value

                    @property
                    def f(self):
                        return self.c * 9 / 5 + 32

                t = Temp(25)
                print(t.c, t.f)
                try:
                    t.c = -300
                except ValueError as e:
                    print(e)""", "Проверка работает и в __init__: там тоже присваивание self.c.")],
              ["return self.c внутри свойства c — RecursionError.",
               "Вызывать свойство со скобками: r.area() — TypeError, ведь r.area уже число."]),
        topic("prop_classmethod", "@classmethod и @staticmethod",
              "@classmethod получает класс (cls) — для альтернативных конструкторов. @staticmethod не получает ни класс, ни объект.",
              """
              Метод класса вызывается как Date.parse("05.03.2024") и создаёт объект через cls(...). Благодаря cls подклассы получат объект своего типа.

              Статический метод — обычная функция, помещённая в класс по смыслу: вызывается и через класс, и через объект, первый параметр не передаётся.

              Обычный метод через класс без объекта вызвать нельзя: в M.inst(2) двойка попадает в self, а для x значения не остаётся — TypeError. Через класс обычный метод вызывают, только передав объект явно: M.inst(m, 2).
              """,
              [("""\
                class Temperature:
                    def __init__(self, celsius):
                        self.celsius = celsius

                    @classmethod
                    def from_fahrenheit(cls, f):
                        return cls(round((f - 32) * 5 / 9, 1))

                    @staticmethod
                    def is_freezing(celsius):
                        return celsius <= 0

                t = Temperature.from_fahrenheit(212)
                print(t.celsius, Temperature.is_freezing(-5), t.is_freezing(t.celsius))""", None)],
              ["Создавать объект в методе класса через имя класса Date(...) вместо cls(...): подклассы получат не тот тип."]),
        topic("prop_private", "Соглашения о приватности и __slots__",
              "_name — «внутреннее, не трогать снаружи» (соглашение). __name — искажение имени. __slots__ запрещает новые атрибуты.",
              """
              В Python нет настоящих приватных атрибутов. Одно подчёркивание — договорённость для программистов.

              Два подчёркивания в начале (self.__code) включают искажение имени: снаружи атрибут называется _Класс__code. Это защита от случайных конфликтов имён в подклассах, а не от доступа.

              __slots__ = ("x", "y") задаёт фиксированный набор атрибутов: объекты занимают меньше памяти, а попытка создать другой атрибут даёт AttributeError.
              """,
              [("""\
                class Safe:
                    def __init__(self):
                        self.__code = 42

                s = Safe()
                print(hasattr(s, "__code"), s._Safe__code)""", None),
               ("""\
                class Pixel:
                    __slots__ = ("r", "g", "b")
                    def __init__(self, r, g, b):
                        self.r, self.g, self.b = r, g, b

                p = Pixel(255, 0, 0)
                try:
                    p.alpha = 1
                except AttributeError:
                    print("атрибута alpha нет в __slots__")""", None)],
              ["Считать __атрибут надёжно скрытым: к нему всё равно можно обратиться."]),
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
              "@dataclass по аннотациям полей сам пишет __init__, __repr__ и __eq__.",
              """
              Поля объявляются с типом: x: int, y: int = 0. Поля без значения по умолчанию должны идти раньше полей со значением.

              Изменяемые значения по умолчанию запрещены (items: list = [] — ValueError): используйте field(default_factory=list), тогда каждый объект получит свой список.

              @dataclass(order=True) добавляет сравнения <, > по полям в порядке объявления — объекты можно сортировать. frozen=True делает объекты неизменяемыми (присваивание — FrozenInstanceError) и хешируемыми. Обычный @dataclass нехешируем: с eq=True (по умолчанию) он ставит __hash__ = None, и объекты нельзя класть в set.

              __post_init__(self) вызывается после автоматического __init__ — место для проверок. dataclasses.replace(obj, поле=значение) создаёт копию с изменёнными полями, asdict(obj) — словарь. slots=True экономит память, kw_only=True требует передавать поля только по имени.
              """,
              [("""\
                from dataclasses import dataclass, field

                @dataclass
                class Team:
                    name: str
                    members: list = field(default_factory=list)

                a = Team("A")
                a.members.append("Ада")
                print(a, a == Team("A", ["Ада"]))""", None),
               ("""\
                from dataclasses import dataclass, replace

                @dataclass(order=True, frozen=True)
                class Score:
                    points: int
                    name: str

                best = max([Score(7, "Ада"), Score(9, "Боб")])
                print(best, replace(best, points=10), best in {best})""", None)],
              ["items: list = [] в dataclass — ValueError при объявлении класса.",
               "Ждать, что аннотация типа проверяется: x: int = \"текст\" сработает без ошибки."]),
        topic("dc_enum", "Enum",
              "Enum — набор именованных констант. У элемента есть name и value; элементы сравниваются через is и ==.",
              """
              class Color(Enum): RED = 1 — Color.RED. Color(1) находит элемент по значению, Color["RED"] — по имени.

              auto() сам подставляет значения 1, 2, 3…. По Enum можно пройти циклом, len(Color) — количество элементов.

              Enum лучше «магических строк»: опечатка Color.REDD сразу даст AttributeError, а не тихую ошибку.
              """,
              [("""\
                from enum import Enum, auto

                class Status(Enum):
                    NEW = auto()
                    DONE = auto()

                s = Status.NEW
                print(s, s.name, s.value, Status(2), [x.name for x in Status])""", None)],
              ["Сравнивать элемент со значением: Status.NEW == 1 — False."]),
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
