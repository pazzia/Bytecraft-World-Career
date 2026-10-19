import 'dart:convert';
import 'dart:io';

import '../../lib/core/storage/game_save_store.dart';
import '../../lib/core/storage/json_document_store.dart';
import '../../lib/core/storage/key_value_store.dart';
import '../../lib/core/time/clock.dart';
import '../../lib/features/career/domain/career_dashboard.dart';
import '../../lib/features/career/domain/career_next_step.dart';
import '../../lib/features/courses/data/content_parser.dart';
import '../../lib/features/courses/data/content_sources.dart';
import '../../lib/features/playground/data/practice_repository.dart';
import '../../lib/features/progress/domain/course_progress.dart';
import '../../lib/features/progress/domain/level_progress.dart';
import '../../lib/features/progress/domain/unlock_policy.dart';
import '../../lib/features/projects/domain/calculator_project.dart';
import '../../lib/features/world/data/world_repository.dart';
import '../../lib/features/world/domain/repair_service.dart';
import '../../lib/features/world/domain/world_rules.dart';
import '../../lib/features/world/domain/world_state.dart';

void check(bool value, String message) {
  if (!value) throw StateError(message);
}

Future<void> main() async {
  final raw = InMemoryKeyValueStore();
  final save = GameSaveStore(raw);
  final documents = JsonDocumentStore(save);
  final clock = FixedClock(DateTime(2026, 10, 19));
  final world = WorldRepository(documents, clock, save);
  Future<String> load(String p) => File(p).readAsString();
  final service = RepairService(save, world, load, clock);
  final catalog = await service.catalog();
  final course = ContentParser().parseCourse(
    await BundledContentSource(load).fetchCourse('python'),
  );
  final tasks = await PracticeRepository(load, documents).tasks('python');
  var progress = CourseProgress(courseId: course.id);
  const calc = CareerDashboardCalculator();
  CareerDashboard dashboard({
    Set<String> solved = const {},
    CalculatorProject project = const CalculatorProject(),
    CareerTargetId goal = CareerTargetId.pythonBackend,
    WorldState? state,
  }) => calc.build(
    course: course,
    progress: progress,
    tasks: tasks,
    solved: solved,
    project: project,
    target: goal,
    repairs: state?.repairs.values ?? const [],
    catalog: catalog,
  );
  CareerSkill core(CareerDashboard d) => d.skills.first;
  var vm = dashboard();
  check(
    vm.skills.every(
      (s) => s.evidence.confirmed.isEmpty && s.evidence.studied.isEmpty,
    ),
    'Invented starting evidence',
  );
  check(
    core(vm).nextStep?.id == course.playableLevels.first.id,
    'Missing first learning step',
  );
  for (final s in vm.skills) {
    final next = s.nextStep;
    if (next?.kind == CareerStepKind.course) {
      check(
        const UnlockPolicy().isUnlocked(course, progress, next!.id),
        'Locked career recommendation',
      );
    }
  }
  final first = course.playableLevels.first;
  progress = progress.withLevel(
    LevelProgress(levelId: first.id, completed: true, bestStars: 3),
  );
  vm = dashboard();
  check(core(vm).evidence.studied.length == 1, 'Course evidence missing');
  check(
    core(vm).evidence.practiced.isEmpty && core(vm).evidence.confirmed.isEmpty,
    'Course stars fabricated practice/proof',
  );
  final task = tasks.first;
  vm = dashboard(solved: {task.id});
  check(core(vm).evidence.practiced.length == 1, 'Solved program missing');
  check(
    core(vm).evidence.confirmed.isEmpty,
    'Practice fabricated independent proof',
  );
  vm = dashboard(project: const CalculatorProject(step: 4));
  check(
    core(vm).evidence.practiced.isEmpty,
    'Legacy project flags fabricated verified code',
  );
  vm = dashboard(
    project: const CalculatorProject(step: 4, verifiedCode: 'working code'),
  );
  check(core(vm).evidence.practiced.length == 1, 'Verified project missing');
  check(
    vm.skills
        .firstWhere((s) => s.id == CareerSkillId.testing)
        .evidence
        .practiced
        .isEmpty,
    'Passing project tests claimed test authorship',
  );

  final id = 'topic:python:${first.topicId}';
  final before = await world.load();
  await Future.wait([service.beginAssessment(id), service.beginAssessment(id)]);
  var state = await world.load();
  var record = state.repairs[id]!;
  check(
    record.pending && record.openErrors == 0 && record.generation == 1,
    'Voluntary check invented errors or duplicated',
  );
  check(
    state.coins == before.coins && state.worldXp == before.worldXp,
    'Starting check awarded currency',
  );
  final restart = RepairService(
    save,
    WorldRepository(documents, clock, save),
    load,
    clock,
  );
  var example = catalog.next(record)!;
  await restart.submit(id, record.generation, example.id, 'WRONG');
  state = await world.load();
  record = state.repairs[id]!;
  check(
    record.pending && record.proofs.isEmpty,
    'Wrong voluntary answer confirmed skill',
  );
  final second = catalog.next(record)!;
  check(second.id != example.id, 'Disclosed voluntary example reused');
  final result = await restart.submit(
    id,
    record.generation,
    second.id,
    second.answer,
  );
  check(result.passed, 'Fresh independent answer rejected');
  state = WorldState.fromJson((await world.load()).toJson());
  vm = dashboard(state: state);
  check(
    core(vm).evidence.confirmed.length == 1,
    'Persisted proof missing in Career',
  );
  check(
    vm.skills.skip(1).every((s) => s.evidence.confirmed.isEmpty),
    'Proof leaked into unrelated skills',
  );
  final coins = state.coins;
  await service.beginAssessment(id);
  await restart.submit(id, record.generation, second.id, second.answer);
  check((await world.load()).coins == coins, 'Repeated check farmed rewards');
  final alternate = dashboard(state: state, goal: CareerTargetId.strongMiddle);
  check(
    core(alternate).evidence.confirmed.length == 1 &&
        core(alternate).target != core(vm).target,
    'Goal changed proofs',
  );
  final reopened = WorldRules.recordError(
    state,
    skillId: id,
    title: record.title,
    category: record.category,
    sourceCode: 'new source',
  );
  vm = dashboard(state: reopened);
  check(
    core(vm).evidence.confirmed.isEmpty &&
        core(vm).evidence.pending.length == 1,
    'New error did not revoke current confirmation',
  );
  check(
    reopened.repairs[id]!.proofs.length == 1,
    'Historical proof was destroyed',
  );
  check(
    core(vm).nextStep?.kind == CareerStepKind.assessment,
    'Open gap was not prioritized',
  );

  // Every catalogue course topic and task maps by exact content identifiers.
  for (final t in tasks) {
    final skillIds = calc.modulesFor(
      CareerSkillId.values.firstWhere(
        (s) => calc.modulesFor(s).contains(t.moduleId),
      ),
    );
    check(
      skillIds.contains(t.moduleId),
      'Unmapped practice module ${t.moduleId}',
    );
  }
  print(
    'Career: real course/practice/project evidence, voluntary independent checks, wrong answers, restart, duplicate rewards, goal changes and reopened gaps passed',
  );
}
