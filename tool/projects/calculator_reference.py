history = []

def calculate(a, b, operation):
    if operation == "+":
        result = a + b
    elif operation == "-":
        result = a - b
    elif operation == "*":
        result = a * b
    elif operation == "/":
        result = a / b
    else:
        raise ValueError("Неизвестная операция")
    history.append(result)
    return result

def run_calculator(text):
    try:
        a, operation, b = text.split()
        return str(calculate(float(a), float(b), operation))
    except (ValueError, ZeroDivisionError):
        return "Ошибка: проверь выражение"

if __name__ == "__main__":
    print(run_calculator(input()))
