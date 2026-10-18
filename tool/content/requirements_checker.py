"""Checks that a solution of a coding exercise is written the way the task
asks (recursion, no loops, a class, nonlocal...), not only that it prints
the right thing.

One source of truth for two places:
* the content generator imports check() to verify reference solutions;
* the app runs this file's source in the bundled Python (Pyodide) with
  {"code": ..., "requires": ...} as JSON on stdin and reads a JSON list of
  problems from stdout (empty list = all good).

Requirement keys (all optional):
  defines:    names of functions/classes that must be defined
  classes:    names that must be classes (not functions)
  methods:    {class: [method, ...]} — methods defined in the class body
  inherits:   {class: base} — the class must list base among its bases
  recursive:  functions that must call themselves
  uses:       constructs that must appear (see USES)
  forbids:    constructs that must not appear (see USES)
  calls:      functions/methods that must be called (open, sorted, ...)
  no_calls:   functions/methods that must not be called
  no_imports: modules that must not be imported (fractions, ...)
  yields:     functions that must be generators (yield in their own body)
  annotated:  functions whose parameters (except self/cls) and result are annotated
  decorated:  {function: decorator} — the function must carry that decorator
  returns_function: functions that must define a nested function and return it
  no_in_operator: functions that must not use `in` / `not in` comparisons
  calls_in:   {function: [names]} — names that must be called inside that function
  asserts_in: {function: n} — the function must contain at least n assert statements
"""
import ast
import json
import sys

LOOPS = (ast.For, ast.While, ast.AsyncFor)
COMPREHENSIONS = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)


def _has_star_args(tree):
    return any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.args.vararg
               for n in ast.walk(tree))


def _has_star_kwargs(tree):
    return any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.args.kwarg
               for n in ast.walk(tree))


def _has_decorator(tree):
    return any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.decorator_list
               for n in ast.walk(tree))


def _has_annotations(tree):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = node.args.posonlyargs + node.args.args + node.args.kwonlyargs
            if node.returns is not None or any(a.annotation is not None for a in args):
                return True
        if isinstance(node, ast.AnnAssign):
            return True
    return False


def _decorator_names(tree):
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for deco in node.decorator_list:
                target = deco.func if isinstance(deco, ast.Call) else deco
                if isinstance(target, ast.Name):
                    names.add(target.id)
                elif isinstance(target, ast.Attribute):
                    names.add(target.attr)
    return names


def _any(*types):
    return lambda tree: any(isinstance(n, types) for n in ast.walk(tree))


# construct -> (test(tree), how it is called in messages)
USES = {
    "for": (_any(ast.For, ast.AsyncFor), "цикл for"),
    "while": (_any(ast.While), "цикл while"),
    "loop": (_any(*LOOPS), "циклы"),
    "comprehension": (_any(*COMPREHENSIONS), "включения (comprehensions)"),
    "lambda": (_any(ast.Lambda), "lambda"),
    "def": (_any(ast.FunctionDef, ast.AsyncFunctionDef), "def (свою функцию)"),
    "class": (_any(ast.ClassDef), "class (свой класс)"),
    "nonlocal": (_any(ast.Nonlocal), "nonlocal"),
    "global": (_any(ast.Global), "global"),
    "yield": (_any(ast.Yield, ast.YieldFrom), "yield (генератор)"),
    "with": (_any(ast.With, ast.AsyncWith), "with"),
    "try": (_any(ast.Try, ast.TryStar), "try/except"),
    "raise": (_any(ast.Raise), "raise"),
    "assert": (_any(ast.Assert), "assert"),
    "star_args": (_has_star_args, "*args"),
    "star_kwargs": (_has_star_kwargs, "**kwargs"),
    "decorator": (_has_decorator, "декоратор (@...)"),
    "async": (_any(ast.AsyncFunctionDef, ast.Await), "async/await"),
    "match": (_any(ast.Match), "match/case"),
    "import": (_any(ast.Import, ast.ImportFrom), "import"),
    "annotations": (_has_annotations, "аннотации типов"),
    "property": (lambda tree: "property" in _decorator_names(tree), "@property"),
    "dataclass": (lambda tree: "dataclass" in _decorator_names(tree), "@dataclass"),
    "contextmanager": (lambda tree: "contextmanager" in _decorator_names(tree), "@contextmanager"),
}


def _defined(tree):
    return {n.name for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}


def _calls_itself(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            for inner in ast.walk(node):
                if (isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name)
                        and inner.func.id == name):
                    return True
    return False


def _called_names(tree):
    """Names of called functions and methods: f(...) and obj.f(...)."""
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                names.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                names.add(node.func.attr)
    return names


def _classes(tree):
    return {n.name: n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}


def _base_names(cls):
    names = set()
    for base in cls.bases:
        if isinstance(base, ast.Name):
            names.add(base.id)
        elif isinstance(base, ast.Attribute):
            names.add(base.attr)
    return names


def _imported_modules(tree):
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module.split(".")[0])
    return modules


def _functions(tree):
    return {n.name: n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def _own_nodes(func):
    """Nodes of a function body without nested functions and classes."""
    stack = list(func.body)
    while stack:
        node = stack.pop()
        yield node
        for child in ast.iter_child_nodes(node):
            if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
                stack.append(child)


def _is_generator(func):
    return any(isinstance(n, (ast.Yield, ast.YieldFrom)) for n in _own_nodes(func))


def _is_annotated(func):
    args = func.args.posonlyargs + func.args.args + func.args.kwonlyargs
    params = [a for a in args if a.arg not in ("self", "cls")]
    return func.returns is not None and all(a.annotation is not None for a in params)


def _decorators_of(func):
    names = set()
    for deco in func.decorator_list:
        target = deco.func if isinstance(deco, ast.Call) else deco
        if isinstance(target, ast.Name):
            names.add(target.id)
        elif isinstance(target, ast.Attribute):
            names.add(target.attr)
    return names


def _returns_nested_function(func):
    nested = {n.name for n in func.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    for node in _own_nodes(func):
        if isinstance(node, ast.Return) and node.value is not None:
            if isinstance(node.value, ast.Name) and node.value.id in nested:
                return True
            if isinstance(node.value, ast.Lambda):
                return True
    return False


def check(code, requires):
    """Returns a list of problems (in Russian), empty when all is fine."""
    try:
        tree = ast.parse(code)
    except SyntaxError as error:
        return [f"Синтаксическая ошибка в строке {error.lineno}: {error.msg}"]
    problems = []
    defined = _defined(tree)
    for name in requires.get("defines", []):
        if name not in defined:
            problems.append(f"Объявите {name} — задача требует именно это имя.")
    classes = _classes(tree)
    for name in requires.get("classes", []):
        if name not in classes:
            problems.append(f"{name} должен быть классом: объявите class {name}.")
    for cls_name, methods in requires.get("methods", {}).items():
        cls = classes.get(cls_name)
        if cls is None:
            continue
        own = {n.name for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        for method in methods:
            if method not in own:
                problems.append(f"В классе {cls_name} нужен метод {method}.")
    for cls_name, base in requires.get("inherits", {}).items():
        cls = classes.get(cls_name)
        if cls is not None and base not in _base_names(cls):
            problems.append(f"Класс {cls_name} должен наследовать {base}.")
    for name in requires.get("recursive", []):
        if name in defined and not _calls_itself(tree, name):
            problems.append(f"Функция {name} должна быть рекурсивной: вызывать саму себя.")
    for key in requires.get("uses", []):
        test, title = USES[key]
        if not test(tree):
            problems.append(f"В решении нужно использовать: {title}.")
    for key in requires.get("forbids", []):
        test, title = USES[key]
        if test(tree):
            problems.append(f"В этой задаче нельзя использовать: {title}.")
    functions = _functions(tree)
    for name in requires.get("yields", []):
        if name in functions and not _is_generator(functions[name]):
            problems.append(f"{name} должна быть генератором: внутри нужен yield.")
    for name in requires.get("annotated", []):
        if name in functions and not _is_annotated(functions[name]):
            problems.append(f"Укажите аннотации типов у всех параметров {name} и у результата (-> ...).")
    for name, deco in requires.get("decorated", {}).items():
        if name in functions and deco not in _decorators_of(functions[name]):
            problems.append(f"Функция {name} должна быть объявлена с декоратором @{deco}.")
    for name in requires.get("returns_function", []):
        if name in functions and not _returns_nested_function(functions[name]):
            problems.append(f"{name} должна объявлять внутри функцию-обёртку и возвращать её.")
    for name in requires.get("no_in_operator", []):
        if name in functions and any(
                isinstance(node, ast.Compare) and any(isinstance(op, (ast.In, ast.NotIn)) for op in node.ops)
                for node in ast.walk(functions[name])):
            problems.append(f"В {name} нельзя использовать оператор in: найдите элемент сами.")
    for name, needed in requires.get("calls_in", {}).items():
        if name in functions:
            inside = _called_names(functions[name])
            for callee in needed:
                if callee not in inside:
                    problems.append(f"Внутри {name} нужно вызвать {callee}().")
    for name, count in requires.get("asserts_in", {}).items():
        if name in functions:
            found = sum(isinstance(node, ast.Assert) for node in ast.walk(functions[name]))
            if found < count:
                problems.append(f"В {name} нужно не меньше {count} проверок assert (сейчас {found}).")
    called = _called_names(tree) | _decorator_names(tree)
    for name in requires.get("calls", []):
        if name not in called:
            problems.append(f"В решении нужно вызвать {name}().")
    for name in requires.get("no_calls", []):
        if name in called:
            problems.append(f"В этой задаче нельзя вызывать {name}().")
    imported = _imported_modules(tree)
    for name in requires.get("no_imports", []):
        if name in imported:
            problems.append(f"В этой задаче нельзя импортировать {name}: напишите решение сами.")
    return problems


def validate_spec(requires):
    """For the generator: unknown keys or constructs are content bugs."""
    allowed = {"defines", "classes", "methods", "inherits", "recursive", "uses", "forbids",
               "calls", "no_calls", "no_imports", "yields", "annotated", "decorated", "returns_function",
               "no_in_operator", "calls_in", "asserts_in"}
    assert set(requires) <= allowed, ("unknown requirement", set(requires) - allowed)
    for key in requires.get("uses", []) + requires.get("forbids", []):
        assert key in USES, ("unknown construct", key)


if __name__ == "__main__":
    request = json.loads(sys.stdin.read())
    print(json.dumps(check(request["code"], request.get("requires", {})), ensure_ascii=False))
