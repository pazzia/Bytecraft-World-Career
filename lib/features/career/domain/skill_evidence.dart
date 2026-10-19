import '../../courses/domain/course.dart';
import '../../playground/domain/practice_task.dart';
import '../../progress/domain/course_progress.dart';
import '../../projects/domain/calculator_project.dart';
import '../../world/domain/skill_repair.dart';

/// A read-only projection of saved work, never a second reward/save ledger.
class SkillEvidence {
  const SkillEvidence({
    this.studied = const [],
    this.practiced = const [],
    this.confirmed = const [],
    this.pending = const [],
  });
  final List<String> studied, practiced;
  final List<SkillRepair> confirmed, pending;
  String get status => confirmed.isNotEmpty
      ? 'Подтверждено подтем: ${confirmed.length}'
      : practiced.isNotEmpty
      ? 'Отработано задач: ${practiced.length}'
      : studied.isNotEmpty
      ? 'Изучено уровней: ${studied.length}'
      : 'Пока нет результатов';

  static SkillEvidence collect({
    required Course course,
    required CourseProgress progress,
    required Set<String> modules,
    required List<PracticeTask> tasks,
    required Set<String> solved,
    required Iterable<SkillRepair> repairs,
    required CalculatorProject project,
    required bool includesCore,
    required bool includesProject,
  }) {
    final topicIds = {
      for (final m in course.modules.where((m) => modules.contains(m.id)))
        for (final l in m.playableLevels)
          if (l.topicId != null) 'topic:${course.id}:${l.topicId}',
    };
    final taskIds = {
      for (final t in tasks.where((t) => modules.contains(t.moduleId)))
        'practice:${course.id}:${t.id}',
    };
    final relevant = repairs
        .where(
          (r) =>
              topicIds.contains(r.skillId) ||
              taskIds.contains(r.skillId) ||
              (includesCore && r.skillId.startsWith('dna:')),
        )
        .toList();
    return SkillEvidence(
      studied: [
        for (final m in course.modules.where((m) => modules.contains(m.id)))
          for (final l in m.playableLevels)
            if (progress.isCompleted(l.id)) l.title,
      ],
      practiced: [
        for (final t in tasks)
          if (modules.contains(t.moduleId) && solved.contains(t.id)) t.title,
        if (includesProject &&
            project.complete &&
            project.verifiedCode.trim().isNotEmpty)
          'Калькулятор: свой код прошёл 14 проверок',
      ],
      confirmed: relevant
          .where(
            (r) =>
                !r.pending &&
                r.proofs.any(
                  (p) =>
                      (p['exampleId'] ?? '').isNotEmpty &&
                      DateTime.tryParse(p['verifiedAt'] ?? '') != null,
                ),
          )
          .toList(),
      pending: relevant.where((r) => r.pending).toList(),
    );
  }
}
