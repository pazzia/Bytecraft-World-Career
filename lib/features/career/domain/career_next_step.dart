import '../../courses/domain/course.dart';
import '../../playground/domain/practice_task.dart';
import '../../progress/domain/course_progress.dart';
import '../../progress/domain/unlock_policy.dart';
import '../../projects/domain/calculator_project.dart';
import '../../world/domain/repair_catalog.dart';
import '../../world/domain/skill_repair.dart';
import 'skill_evidence.dart';

enum CareerStepKind { course, practice, assessment, project, expedition }

class CareerNextStep {
  const CareerNextStep(this.kind, this.id, this.label, this.reason);
  final CareerStepKind kind;
  final String id, label, reason;

  static CareerNextStep? choose({
    required Course course,
    required CourseProgress progress,
    required Set<String> modules,
    required List<PracticeTask> tasks,
    required Set<String> solved,
    required Iterable<SkillRepair> repairs,
    required SkillEvidence evidence,
    required CalculatorProject project,
    required bool includesProject,
    required bool projectUnlocked,
    required int score,
    required int target,
    required UnlockMode mode,
    RepairCatalog? catalog,
  }) {
    for (final r in evidence.pending) {
      if (catalog?.next(r) != null) {
        return CareerNextStep(
          CareerStepKind.assessment,
          r.skillId,
          'Закрепить: ${catalog!.title(r)}',
          'Есть незавершённая самостоятельная проверка.',
        );
      }
    }
    final levels = course.playableLevels.where(
      (l) => modules.contains(l.moduleId),
    );
    final available = levels.where(
      (l) =>
          !progress.isCompleted(l.id) &&
          const UnlockPolicy().isUnlocked(course, progress, l.id, mode: mode),
    );
    final practice = tasks.where((t) => modules.contains(t.moduleId));
    final remaining = practice.where((t) => !solved.contains(t.id));
    final studiedModules = {
      for (final l in levels)
        if (progress.isCompleted(l.id)) l.moduleId,
    };
    final eligible = remaining.where(
      (t) => studiedModules.contains(t.moduleId),
    );
    if (eligible.isNotEmpty) {
      final task = eligible.first;
      return CareerNextStep(
        CareerStepKind.practice,
        task.id,
        'Отработать: ${task.title}',
        'Напиши программу и пройди проверки.',
      );
    }
    final completedTopics = {
      for (final l in levels)
        if (progress.isCompleted(l.id) && l.topicId != null)
          'topic:${course.id}:${l.topicId}',
      for (final t in practice)
        if (solved.contains(t.id)) 'practice:${course.id}:${t.id}',
    };
    final records = {for (final r in repairs) r.skillId: r};
    for (final id in completedTopics) {
      final definition = catalog?.skills[id];
      final previous = records[id];
      if (definition == null ||
          (previous != null &&
              (previous.pending || previous.proofs.isNotEmpty)))
        continue;
      return CareerNextStep(
        CareerStepKind.assessment,
        id,
        'Подтвердить: ${definition['title']}',
        'Реши новый пример без предварительного разбора.',
      );
    }
    if (includesProject && !project.complete && evidence.studied.isNotEmpty) {
      return CareerNextStep(
        projectUnlocked ? CareerStepKind.project : CareerStepKind.expedition,
        '',
        projectUnlocked
            ? 'Продолжить калькулятор'
            : 'Открыть проект через экспедицию',
        'Сохрани работающий проект на Python.',
      );
    }
    if (score < target && available.isNotEmpty) {
      final level = available.first;
      return CareerNextStep(
        CareerStepKind.course,
        level.id,
        'Изучить: ${level.title}',
        'Следующий доступный уровень навыка.',
      );
    }
    if (available.isNotEmpty) {
      return CareerNextStep(
        CareerStepKind.course,
        available.first.id,
        'Продолжить: ${available.first.title}',
        'Расширь изученную часть навыка.',
      );
    }
    final prerequisite = const UnlockPolicy().nextToPlay(
      course,
      progress,
      mode: mode,
    );
    if (levels.any((l) => !progress.isCompleted(l.id)) &&
        prerequisite != null) {
      return CareerNextStep(
        CareerStepKind.course,
        prerequisite.id,
        'Пройти основу: ${prerequisite.title}',
        'Этот уровень откроет дальнейший маршрут.',
      );
    }
    if (remaining.isNotEmpty) {
      return CareerNextStep(
        CareerStepKind.practice,
        remaining.first.id,
        'Отработать: ${remaining.first.title}',
        'Напиши программу и пройди проверки.',
      );
    }
    return null;
  }
}
