import 'career_dashboard.dart';

class VacancyRequirementMatch {
  const VacancyRequirementMatch({
    required this.label,
    required this.skill,
    required this.score,
  });

  final String label;
  final CareerSkillId skill;
  final int score;
}

class VacancyMatchReport {
  const VacancyMatchReport({
    required this.match,
    required this.requirements,
  });

  final int match;
  final List<VacancyRequirementMatch> requirements;

  bool get hasRequirements => requirements.isNotEmpty;

  List<VacancyRequirementMatch> get gaps {
    final result = requirements.where((item) => item.score < 70).toList();
    result.sort((a, b) => a.score.compareTo(b.score));
    return result;
  }
}

class VacancyMatcher {
  const VacancyMatcher();

  VacancyMatchReport analyze(String text, List<CareerSkill> skills) {
    final normalized = text.toLowerCase();
    if (normalized.trim().isEmpty) {
      return const VacancyMatchReport(match: 0, requirements: []);
    }

    final detected = <VacancyRequirementMatch>[];
    for (final definition in _definitions) {
      if (!definition.keywords.any(normalized.contains)) continue;
      final skill = skills.firstWhere((item) => item.id == definition.skill);
      detected.add(
        VacancyRequirementMatch(
          label: definition.label,
          skill: definition.skill,
          score: skill.score,
        ),
      );
    }
    if (detected.isEmpty) {
      return const VacancyMatchReport(match: 0, requirements: []);
    }

    final average = detected.fold<int>(0, (sum, item) => sum + item.score) /
        detected.length;
    return VacancyMatchReport(
      match: average.round().clamp(0, 100),
      requirements: List.unmodifiable(detected),
    );
  }

  static const _definitions = [
    _RequirementDefinition(
      'Python',
      CareerSkillId.pythonCore,
      {'python', 'python3'},
    ),
    _RequirementDefinition(
      'OOP / архитектура',
      CareerSkillId.oop,
      {
        'oop',
        'solid',
        'design pattern',
        'паттерн',
        'архитектур',
        'microservice',
        'микросервис',
      },
    ),
    _RequirementDefinition(
      'Алгоритмы',
      CareerSkillId.algorithms,
      {
        'algorithm',
        'алгоритм',
        'data structure',
        'структур данных',
        'complexity',
        'big o',
      },
    ),
    _RequirementDefinition(
      'Тестирование',
      CareerSkillId.testing,
      {'pytest', 'unit test', 'testing', 'тестирован', 'tdd'},
    ),
    _RequirementDefinition(
      'Async / concurrency',
      CareerSkillId.async,
      {
        'asyncio',
        'async',
        'асинхрон',
        'concurrency',
        'celery',
        'rabbitmq',
        'kafka',
      },
    ),
    _RequirementDefinition(
      'Production / backend',
      CareerSkillId.production,
      {
        'fastapi',
        'django',
        'flask',
        'docker',
        'kubernetes',
        'ci/cd',
        'postgres',
        'redis',
        'linux',
        'rest api',
      },
    ),
  ];
}

class _RequirementDefinition {
  const _RequirementDefinition(this.label, this.skill, this.keywords);

  final String label;
  final CareerSkillId skill;
  final Set<String> keywords;
}
