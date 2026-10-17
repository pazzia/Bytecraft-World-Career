import '../../courses/domain/course.dart';
import '../../progress/domain/course_progress.dart';

enum CareerSkillId {
  pythonCore,
  oop,
  algorithms,
  testing,
  async,
  production,
}

enum CareerTargetId {
  junior('junior_python_backend', 'Junior Python Backend'),
  pythonBackend('python_backend', 'Python Backend Developer'),
  strongMiddle('strong_middle_python_backend', 'Strong Middle Python Backend');

  const CareerTargetId(this.id, this.title);

  final String id;
  final String title;

  static CareerTargetId fromId(String? id) => CareerTargetId.values.firstWhere(
        (value) => value.id == id,
        orElse: () => CareerTargetId.pythonBackend,
      );

  Map<CareerSkillId, int> get requirements => switch (this) {
        CareerTargetId.junior => const {
            CareerSkillId.pythonCore: 68,
            CareerSkillId.oop: 48,
            CareerSkillId.algorithms: 45,
            CareerSkillId.testing: 50,
            CareerSkillId.async: 35,
            CareerSkillId.production: 42,
          },
        CareerTargetId.pythonBackend => const {
            CareerSkillId.pythonCore: 85,
            CareerSkillId.oop: 70,
            CareerSkillId.algorithms: 65,
            CareerSkillId.testing: 75,
            CareerSkillId.async: 70,
            CareerSkillId.production: 70,
          },
        CareerTargetId.strongMiddle => const {
            CareerSkillId.pythonCore: 92,
            CareerSkillId.oop: 82,
            CareerSkillId.algorithms: 76,
            CareerSkillId.testing: 84,
            CareerSkillId.async: 82,
            CareerSkillId.production: 84,
          },
      };
}

class CareerSkill {
  const CareerSkill({
    required this.id,
    required this.title,
    required this.score,
    required this.target,
  });

  final CareerSkillId id;
  final String title;
  final int score;
  final int target;

  int get gap => (target - score).clamp(0, 100).toInt();
  bool get readyForAssessment => score >= target;
}

class CareerAction {
  const CareerAction({
    required this.skill,
    required this.title,
    required this.subtitle,
    required this.estimatedGain,
  });

  final CareerSkillId skill;
  final String title;
  final String subtitle;
  final int estimatedGain;
}

class RoleMatch {
  const RoleMatch({
    required this.id,
    required this.title,
    required this.match,
  });

  final CareerTargetId id;
  final String title;
  final int match;
}

class CareerDashboard {
  const CareerDashboard({
    required this.targetId,
    required this.targetTitle,
    required this.careerScore,
    required this.readiness,
    required this.cvScore,
    required this.skills,
    required this.actions,
    required this.roleMatches,
    required this.completedLevels,
    required this.totalLevels,
  });

  final CareerTargetId targetId;
  final String targetTitle;
  final int careerScore;
  final int readiness;
  final int cvScore;
  final List<CareerSkill> skills;
  final List<CareerAction> actions;
  final List<RoleMatch> roleMatches;
  final int completedLevels;
  final int totalLevels;

  int get assessmentReadyCount =>
      skills.where((skill) => skill.readyForAssessment).length;
}

class CareerDashboardCalculator {
  const CareerDashboardCalculator();

  CareerDashboard build({
    required Course course,
    required CourseProgress progress,
    CareerTargetId target = CareerTargetId.pythonBackend,
  }) {
    final requirements = target.requirements;
    final skills = <CareerSkill>[
      _skill(
        CareerSkillId.pythonCore,
        'Python Core',
        requirements[CareerSkillId.pythonCore]!,
        course,
        progress,
        _pythonCore,
      ),
      _skill(
        CareerSkillId.oop,
        'OOP и архитектура',
        requirements[CareerSkillId.oop]!,
        course,
        progress,
        _oop,
      ),
      _skill(
        CareerSkillId.algorithms,
        'Алгоритмы',
        requirements[CareerSkillId.algorithms]!,
        course,
        progress,
        _algorithms,
      ),
      _skill(
        CareerSkillId.testing,
        'Тестирование',
        requirements[CareerSkillId.testing]!,
        course,
        progress,
        _testing,
      ),
      _skill(
        CareerSkillId.async,
        'Async и concurrency',
        requirements[CareerSkillId.async]!,
        course,
        progress,
        _async,
      ),
      _skill(
        CareerSkillId.production,
        'Production skills',
        requirements[CareerSkillId.production]!,
        course,
        progress,
        _production,
      ),
    ];

    final careerScore = _weightedAverage(skills);
    final readiness = _roleMatch(skills, requirements);
    final courseTotal = course.playableLevels.length;
    final completion = courseTotal == 0
        ? 0
        : _percent(progress.completedCount / courseTotal * 100);
    final cvScore = _percent(readiness * 0.72 + completion * 0.28);

    final actions = _actions(skills, course, progress);
    final roleMatches = [
      for (final role in CareerTargetId.values)
        RoleMatch(
          id: role,
          title: role.title,
          match: _roleMatch(skills, role.requirements),
        ),
    ];

    return CareerDashboard(
      targetId: target,
      targetTitle: target.title,
      careerScore: careerScore,
      readiness: readiness,
      cvScore: cvScore,
      skills: List.unmodifiable(skills),
      actions: List.unmodifiable(actions),
      roleMatches: List.unmodifiable(roleMatches),
      completedLevels: progress.completedCount,
      totalLevels: courseTotal,
    );
  }

  static int readinessFor(List<CareerSkill> skills) {
    if (skills.isEmpty) return 0;
    var total = 0.0;
    for (final skill in skills) {
      if (skill.target <= 0) continue;
      total += (skill.score / skill.target).clamp(0.0, 1.0);
    }
    return _percent(total / skills.length * 100);
  }

  static int _percent(num value) => value.round().clamp(0, 100).toInt();

  CareerSkill _skill(
    CareerSkillId id,
    String title,
    int target,
    Course course,
    CourseProgress progress,
    Set<String> moduleIds,
  ) =>
      CareerSkill(
        id: id,
        title: title,
        score: _moduleScore(course, progress, moduleIds),
        target: target,
      );

  int _moduleScore(
    Course course,
    CourseProgress progress,
    Set<String> moduleIds,
  ) {
    var total = 0;
    var completed = 0;
    var stars = 0;
    for (final module in course.modules) {
      if (!moduleIds.contains(module.id)) continue;
      for (final level in module.playableLevels) {
        total++;
        final levelProgress = progress.levelOf(level.id);
        if (levelProgress.completed) completed++;
        stars += levelProgress.bestStars.clamp(0, 3).toInt();
      }
    }
    if (total == 0) return 0;
    final completionScore = completed / total * 70;
    final masteryScore = stars / (total * 3) * 30;
    return _percent(completionScore + masteryScore);
  }

  int _weightedAverage(List<CareerSkill> skills) {
    const weights = {
      CareerSkillId.pythonCore: 30,
      CareerSkillId.oop: 15,
      CareerSkillId.algorithms: 15,
      CareerSkillId.testing: 15,
      CareerSkillId.async: 10,
      CareerSkillId.production: 15,
    };
    var value = 0;
    var weight = 0;
    for (final skill in skills) {
      final currentWeight = weights[skill.id] ?? 1;
      value += skill.score * currentWeight;
      weight += currentWeight;
    }
    return weight == 0 ? 0 : _percent(value / weight);
  }

  int _roleMatch(
    List<CareerSkill> skills,
    Map<CareerSkillId, int> requirements,
  ) {
    var sum = 0.0;
    var count = 0;
    for (final entry in requirements.entries) {
      final skill = skills.firstWhere((item) => item.id == entry.key);
      sum += (skill.score / entry.value).clamp(0.0, 1.0);
      count++;
    }
    return count == 0 ? 0 : _percent(sum / count * 100);
  }

  List<CareerAction> _actions(
    List<CareerSkill> skills,
    Course course,
    CourseProgress progress,
  ) {
    final ordered = [...skills]..sort((a, b) => b.gap.compareTo(a.gap));
    final result = <CareerAction>[];
    for (final skill in ordered) {
      if (skill.gap == 0) continue;
      final definition = _definitionFor(skill.id);
      CourseModule? nextModule;
      for (final module in course.modules) {
        if (!definition.contains(module.id)) continue;
        if (module.playableLevels.any((level) => !progress.isCompleted(level.id))) {
          nextModule = module;
          break;
        }
      }
      result.add(
        CareerAction(
          skill: skill.id,
          title: 'Прокачать ${skill.title}',
          subtitle: nextModule == null
              ? 'Закрепить навык в практике и задачах на время'
              : 'Следующий модуль: ${nextModule.title}',
          estimatedGain: skill.gap.clamp(1, 5).toInt(),
        ),
      );
      if (result.length == 3) break;
    }
    return result;
  }

  Set<String> _definitionFor(CareerSkillId id) => switch (id) {
        CareerSkillId.pythonCore => _pythonCore,
        CareerSkillId.oop => _oop,
        CareerSkillId.algorithms => _algorithms,
        CareerSkillId.testing => _testing,
        CareerSkillId.async => _async,
        CareerSkillId.production => _production,
      };

  static const _pythonCore = {
    'variables',
    'types',
    'operators',
    'strings',
    'io',
    'conditions',
    'loops',
    'loops_control',
    'lists',
    'tuples_sets',
    'dicts',
    'comprehensions',
    'functions',
    'args',
    'scope',
    'functional',
    'exceptions',
    'files',
    'stdlib',
    'textdata',
    'pythonic',
  };

  static const _oop = {
    'classes',
    'inheritance',
    'dunder',
    'properties',
    'dataclasses',
    'typing',
    'decorators',
    'contexts',
    'generators',
  };

  static const _algorithms = {'recursion', 'algorithms', 'performance'};
  static const _testing = {'testing'};
  static const _async = {'async', 'concurrency'};
  static const _production = {
    'project',
    'files',
    'stdlib',
    'textdata',
    'testing',
    'typing',
    'performance',
    'async',
    'concurrency',
  };
}
