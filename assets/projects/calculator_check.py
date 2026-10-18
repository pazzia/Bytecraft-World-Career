"""Local functional checks for the player's calculator; no network or services."""
import contextlib
import json
import math

request = json.loads(input())
namespace = {"__name__": "bytecraft_project"}
checks = []

def record(name, action):
    try:
        action()
        checks.append({"name": name, "passed": True})
    except BaseException as error:
        checks.append({"name": name, "passed": False,
                       "detail": type(error).__name__ + ": " + str(error)[:160]})

def equal_number(actual, expected):
    assert isinstance(actual, (int, float)) and not isinstance(actual, bool), "Верни число"
    assert math.isfinite(actual) and math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-9), "Неверный результат"

def raises(kind, action):
    try:
        action()
    except kind:
        return
    raise AssertionError("Ожидалась ошибка " + kind.__name__)

class QuietOutput:
    # User logging must not allocate an unbounded StringIO buffer during checks.
    def write(self, text):
        return len(text)
    def flush(self):
        pass

with contextlib.redirect_stdout(QuietOutput()):
    try:
        exec(compile(request["code"], "calculator.py", "exec"), namespace)
    except BaseException as error:
        checks.append({"name": "Загрузка программы", "passed": False,
                       "detail": type(error).__name__ + ": " + str(error)[:160]})
    else:
        calculate = namespace.get("calculate")
        for name, a, b, operation, expected in [
            ("Сложение", 8, 3, "+", 11),
            ("Вычитание", -4, 7, "-", -11),
            ("Умножение", 2.5, 4, "*", 10),
            ("Деление", 7, 2, "/", 3.5),
            ("Дробные числа", 0.1, 0.2, "+", 0.3),
        ]:
            record(name, lambda a=a, b=b, operation=operation, expected=expected:
                   equal_number(calculate(a, b, operation), expected))
        if request["step"] >= 1:
            def history_check():
                history = namespace.get("history")
                assert isinstance(history, list), "Объяви список history"
                before = len(history)
                calculate(1, 2, "+")
                calculate(4, 2, "/")
                assert len(history) == before + 2, "Сохраняй каждый успешный результат"
                assert history[-2:] == [3, 2], "В history должны быть числа-результаты"
            record("История вычислений", history_check)
        if request["step"] >= 2:
            record("Защита от нуля", lambda: raises(ZeroDivisionError, lambda: calculate(1, 0, "/")))
            record("Неизвестная операция", lambda: raises(ValueError, lambda: calculate(1, 2, "^")))
            def no_error_history():
                before = list(namespace["history"])
                for b, operation in [(0, "/"), (2, "^")]:
                    try:
                        calculate(1, b, operation)
                    except (ZeroDivisionError, ValueError):
                        pass
                assert namespace["history"] == before, "Ошибки не попадают в историю"
            record("Чистая история", no_error_history)
        if request["step"] >= 3:
            run = namespace.get("run_calculator")
            for expression, expected in [("2 + 3", 5), ("1.5 * 2", 3), ("-4 + 1", -3)]:
                def text_check(expression=expression, expected=expected):
                    result = run(expression)
                    assert isinstance(result, str), "Верни строку"
                    equal_number(float(result), expected)
                record("Строка: " + expression, text_check)
            for expression in ["abc", "7 / 0"]:
                def friendly_error(expression=expression):
                    result = run(expression)
                    assert isinstance(result, str) and result.startswith("Ошибка"), "Верни строку, начинающуюся с Ошибка"
                record("Сообщение: " + expression, friendly_error)

print(json.dumps({"nonce": request["nonce"], "checks": checks}, ensure_ascii=False))
