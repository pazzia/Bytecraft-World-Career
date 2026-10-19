// Offline integration check: actual ProjectService + CPython checker + saves.
// No Flutter bootstrap, network access or mocked successful Python reports.
// Run from the repository root: dart tool/projects/check_service.dart
import 'dart:convert';
import 'dart:io';

import '../../lib/core/storage/game_save_store.dart';
import '../../lib/core/storage/json_document_store.dart';
import '../../lib/core/storage/key_value_store.dart';
import '../../lib/core/time/clock.dart';
import '../../lib/features/playground/domain/python_runner.dart';
import '../../lib/features/projects/domain/project_service.dart';
import '../../lib/features/world/data/world_repository.dart';
import '../../lib/features/world/domain/world_state.dart';

void require(bool condition, String message) {
  if (!condition) throw StateError(message);
}

class Environment {
  Environment({PythonRunner? runner}) {
    service = ProjectService(
      documents,
      save,
      world,
      runner ?? ProcessRunner(),
      (path) => File(path).readAsString(),
      clock,
    );
  }
  final raw = InMemoryKeyValueStore();
  late final save = GameSaveStore(raw);
  late final documents = JsonDocumentStore(save);
  final clock = FixedClock(DateTime(2026, 10, 19));
  late final world = WorldRepository(documents, clock, save);
  late final ProjectService service;
  Future<void> unlock() =>
      world.write(WorldState.initial().copyWith(expeditionStep: 5));
}

class ProcessRunner implements PythonRunner {
  bool damagedReport = false;
  @override
  PythonRunnerState get state => PythonRunnerState.ready;
  @override
  String? get error => null;
  @override
  String? get version => null;
  @override
  Stream<PythonRunnerState> get states => const Stream.empty();
  @override
  Future<void> start() async {}
  @override
  Future<RunResult> run(
    String code, {
    String stdin = '',
    Duration timeout = const Duration(seconds: 5),
    bool echoInputPrompt = true,
  }) async {
    if (damagedReport)
      return const RunResult(status: RunStatus.ok, stdout: '{broken');
    final process = await Process.start('python3', ['-c', code]);
    final out = process.stdout.transform(utf8.decoder).join();
    final err = process.stderr.transform(utf8.decoder).join();
    process.stdin.write(stdin);
    await process.stdin.close();
    final exit = await process.exitCode.timeout(
      timeout,
      onTimeout: () {
        process.kill(ProcessSignal.sigkill);
        return -1;
      },
    );
    return RunResult(
      status: exit == -1
          ? RunStatus.timeout
          : exit == 0
          ? RunStatus.ok
          : RunStatus.error,
      stdout: await out,
      stderr: await err,
    );
  }
}

Future<void> main() async {
  final reference = await File('tool/projects/calculator_reference.py')
      .readAsString();
  final runner = ProcessRunner();
  final env = Environment(runner: runner);
  await env.unlock();
  runner.damagedReport = true;
  require(
    !(await env.service.check(reference)).passed,
    'Damaged report accepted',
  );
  require(
    (await env.service.load()).wrongAnswers == 0,
    'Damaged report penalized learner',
  );
  runner.damagedReport = false;
  for (var stage = 0; stage < 4; stage++) {
    final result = await env.service.check(reference);
    require(
      result.passed,
      'Real checker rejected stage $stage: ${result.lines}',
    );
    require((await env.service.load()).step == stage + 1, 'Step not saved');
  }
  require((await env.world.load()).worldXp == 180, 'Incorrect project XP');
  require((await env.world.load()).hasVerifiedProject, 'Boss not unlocked');
  await env.service.check(reference);
  require((await env.world.load()).coins == 100, 'Duplicate rewards');
  final syntax = await env.service.check('def broken(');
  require(
    !syntax.passed && syntax.lines.single.contains('SyntaxError'),
    'Syntax failure lost',
  );
  require(
    (await env.service.load()).verifiedCode == reference,
    'Working code overwritten',
  );

  final broken = Environment();
  await broken.unlock();
  require(
    (await broken.service.check(reference)).passed,
    'Stage zero rejected',
  );
  final missingHistory = reference.replaceAll(
    '    history.append(result)',
    '    if operation != "*":\n        history.append(result)',
  );
  require(
    !(await broken.service.check(missingHistory)).passed,
    'Incomplete history accepted',
  );
  require(
    (await broken.service.load()).step == 1,
    'Failed history advanced project',
  );
  require(
    (await broken.service.load()).wrongAnswers == 1,
    'Code error not recorded',
  );
  require(
    (await broken.service.check(reference)).passed,
    'Corrected program rejected',
  );
  require(
    (await broken.world.load()).worldXp == 67,
    'Retry reward is incorrect',
  );
  print(
    'ProjectService + CPython: stages, reports, syntax, history, rewards and saved code passed',
  );
}
