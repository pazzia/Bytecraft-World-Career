class CalculatorProject {
  const CalculatorProject({this.draft = '', this.step = 0,
    this.verifiedCode = '', this.failures = const {}});
  static const revision = 1;
  static const titles = ['Базовые операции', 'История результатов', 'Обработка ошибок', 'Текстовый интерфейс'];
  static const instructions = [
    'Напиши calculate(a, b, operation). Функция возвращает число для операций +, − (в коде -), * и /. Поддержи отрицательные и дробные числа.',
    'Объяви список history. Каждый успешный вызов calculate добавляет в него число-результат. Сохрани работу базовых операций.',
    'При делении на ноль calculate должна вызывать ZeroDivisionError, при неизвестной операции — ValueError. Ошибочные вычисления не добавляются в history.',
    'Добавь run_calculator(text). Для строки «2 + 3» она возвращает строку с результатом. Разбери числа и операцию через пробелы. Для неверного ввода и деления на ноль верни строку, начинающуюся с «Ошибка».',
  ];
  static const checkCounts = [5, 6, 9, 14];

  factory CalculatorProject.fromJson(Map<String, dynamic>? json) => CalculatorProject(
    draft: json?['draft'] as String? ?? '',
    step: (json?['step'] as num?)?.toInt().clamp(0, 4) ?? 0,
    verifiedCode: json?['verifiedCode'] as String? ?? '',
    failures: Map<String, int>.from(json?['failures'] as Map? ?? {}),
  );
  final String draft;
  final int step;
  final String verifiedCode;
  final Map<String, int> failures;
  bool get complete => step == 4;
  int get wrongAnswers => failures['${step.clamp(0, 3)}'] ?? 0;
  Map<String, dynamic> toJson() => {
    'draft': draft, 'step': step, 'verifiedCode': verifiedCode,
    'failures': failures, 'checkerRevision': revision,
  };
}

class ProjectCheck {
  const ProjectCheck(this.message, {this.passed = false, this.lines = const []});
  final String message;
  final bool passed;
  final List<String> lines;
}
