"""Checks that a solution of a coding exercise is written the way the task
asks (recursion, no loops, a class, nonlocal...), not only that it prints
the right thing.

One source of truth for two places:
* the content generator imports check() to verify reference solutions;
* the app runs this file's source in the bundled Python (Pyodide) with
  {"code": ..., "requires": ...} as JSON on stdin and reads a JSON list of
  problems from stdout (empty list = all good).

Requirement keys (all optional):
  defines:   names of functions/classes that must be defined
  recursive: functions that must call themselves
  uses:      constructs that must appear (see USES)
  forbids:   constructs that must not appear (see USES)
  no_calls:  built-in functions that must not be called
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
    "star_args": (_has_star_args, "*args"),
    "star_kwargs": (_has_star_kwargs, "**kwargs"),
    "decorator": (_has_decorator, "декоратор (@...)"),
    "async": (_any(ast.AsyncFunctionDef, ast.Await), "async/await"),
    "match": (_any(ast.Match), "match/case"),
    "import": (_any(ast.Import, ast.ImportFrom), "import"),
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
    return {n.func.id for n in ast.walk(tree)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


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
    called = _called_names(tree)
    for name in requires.get("no_calls", []):
        if name in called:
            problems.append(f"В этой задаче нельзя вызывать {name}().")
    return problems


def validate_spec(requires):
    """For the generator: unknown keys or constructs are content bugs."""
    allowed = {"defines", "recursive", "uses", "forbids", "no_calls"}
    assert set(requires) <= allowed, ("unknown requirement", set(requires) - allowed)
    for key in requires.get("uses", []) + requires.get("forbids", []):
        assert key in USES, ("unknown construct", key)


if __name__ == "__main__":
    request = json.loads(sys.stdin.read())
    print(json.dumps(check(request["code"], request.get("requires", {})), ensure_ascii=False))
