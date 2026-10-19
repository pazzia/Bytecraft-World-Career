import 'dart:async';
import 'dart:convert';

import 'package:bytecraft/core/storage/game_save_store.dart';
import 'package:bytecraft/core/storage/json_document_store.dart';
import 'package:bytecraft/core/storage/key_value_store.dart';
import 'package:bytecraft/core/time/clock.dart';
import 'package:bytecraft/features/playground/domain/python_runner.dart';
import 'package:bytecraft/features/projects/domain/calculator_project.dart';
import 'package:bytecraft/features/projects/domain/project_service.dart';
import 'package:bytecraft/features/world/data/world_repository.dart';
import 'package:bytecraft/features/world/domain/world_state.dart';
import 'package:flutter_test/flutter_test.dart';

class Env {
  Env({KeyValueStore? source, WorldState? state}) {
    raw =
        source ??
        InMemoryKeyValueStore({
          WorldRepository.key: jsonEncode({
            ...((state ?? WorldState.initial().copyWith(expeditionStep: 5))
                .toJson()),
            'schemaVersion': 2,
          }),
        });
    save = GameSaveStore(raw);
    documents = JsonDocumentStore(save);
    world = WorldRepository(
      documents,
      FixedClock(DateTime(2026, 10, 19)),
      save,
    );
    service = ProjectService(
      documents,
      save,
      world,
      runner,
      (_) async => '# checker',
      FixedClock(DateTime(2026, 10, 19)),
    );
  }
  late final KeyValueStore raw;
  late final GameSaveStore save;
  late final JsonDocumentStore documents;
  late final WorldRepository world;
  late final ProjectService service;
  final runner = _Runner();
}

void main() {
  test('four code checks persist program, unlock boss and reward each component once', () async {
    final env = Env();
    for (var step = 0; step < 4; step++) {
      expect((await env.service.check('my program')).passed, isTrue);
      expect((await env.service.load()).step, step + 1);
    }
    final wallet = await env.world.load();
    expect(wallet.coins, 100);
    expect(wallet.worldXp, 180);
    expect(wallet.hasVerifiedProject, isTrue);
    expect(wallet.completedProjectSteps, 4);
    expect(wallet.solved['project'], 4);
    expect((await env.service.load()).verifiedCode, 'my program');
    await env.service.check('my program');
    expect((await env.world.load()).coins, 100);
    final restarted = Env(source: env.raw);
    expect((await restarted.service.load()).verifiedCode, 'my program');
    expect((await restarted.world.load()).hasVerifiedProject, isTrue);
  });

  test('failed tests retain draft but never advance or unlock; unavailable runner grants nothing', () async {
    final env = Env();
    env.runner.pass = false;
    expect((await env.service.check('incorrect program')).passed, isFalse);
    expect((await env.service.load()).step, 0);
    expect((await env.service.load()).wrongAnswers, 1);
    expect((await env.service.load()).draft, 'incorrect program');
    expect((await env.world.load()).coins, 0);
    env.runner.unavailable = true;
    await env.service.check('still saved');
    expect((await env.service.load()).wrongAnswers, 1);
    expect((await env.world.load()).hasVerifiedProject, isFalse);
  });

  test(
    'a stale result cannot verify changed code or overwrite its draft',
    () async {
      final env = Env();
      env.runner.gate = Completer<void>();
      final check = env.service.check('old program');
      await env.runner.started.future;
      await env.service.saveDraft('new program');
      env.runner.gate!.complete();
      expect((await check).passed, isFalse);
      expect((await env.service.load()).draft, 'new program');
      expect((await env.service.load()).step, 0);
      expect((await env.world.load()).coins, 0);
    },
  );

  test('duplicate concurrent checks cannot reward a component twice', () async {
    final env = Env();
    env.runner.gate = Completer<void>();
    final checks = List.generate(8, (_) => env.service.check('program'));
    await env.runner.started.future;
    // All check requests save/read their starting step before Python resumes.
    await env.save.transaction(() async {});
    env.runner.gate!.complete();
    await Future.wait(checks);
    expect((await env.service.load()).step, 1);
    expect((await env.world.load()).coins, 25);
  });

  test('a forged or incomplete checker report is not proof', () async {
    final env = Env();
    env.runner.forgedNonce = true;
    expect((await env.service.check('program')).passed, isFalse);
    env.runner.forgedNonce = false;
    env.runner.partial = true;
    expect((await env.service.check('program')).passed, isFalse);
    expect((await env.world.load()).hasVerifiedProject, isFalse);
    expect((await env.world.load()).coins, 0);
    expect((await env.service.load()).wrongAnswers, 0);
    env.runner.partial = false;
    await env.service.check('program');
    expect((await env.world.load()).worldXp, 45);
  });

  test('duplicated checks cannot substitute for missing operations or reduce rewards', () async {
    final env = Env();
    env.runner.duplicateNames = true;
    expect((await env.service.check('program')).passed, isFalse);
    expect((await env.service.load()).step, 0);
    expect((await env.service.load()).wrongAnswers, 0);
    expect((await env.world.load()).coins, 0);
  });

  test('syntax errors and timeouts count as failed attempts with clear diagnostics', () async {
    final env = Env();
    env.runner.loadError = true;
    final syntax = await env.service.check('def broken(');
    expect(syntax.passed, isFalse);
    expect(syntax.lines.single, contains('SyntaxError'));
    expect((await env.service.load()).wrongAnswers, 1);
    env.runner.loadError = false;
    env.runner.timedOut = true;
    final timeout = await env.service.check('while True: pass');
    expect(timeout.lines.single, contains('5 секунд'));
    expect((await env.service.load()).wrongAnswers, 2);
    env.runner.timedOut = false;
    await env.service.check('working program');
    expect((await env.world.load()).worldXp, 22);
  });

  test('a failed check without details never says it passed', () async {
    final env = Env();
    env.runner.pass = false;
    final report = await env.service.check('wrong program');
    expect(
      report.lines.every((line) => line.contains('проверка не пройдена')),
      isTrue,
    );
  });

  test('a disk failure cannot commit the project step or its reward', () async {
    final source = _Disk({
      WorldRepository.key: jsonEncode({
        ...WorldState.initial().copyWith(expeditionStep: 5).toJson(),
        'schemaVersion': 2,
      }),
    });
    final env = Env(source: source);
    env.runner.afterRun = () => source.fail = true;
    await expectLater(env.service.check('program'), throwsStateError);
    source.fail = false;
    env.runner.afterRun = null;
    expect((await env.service.load()).step, 0);
    expect((await env.service.load()).draft, 'program');
    expect((await env.world.load()).coins, 0);
    await env.service.check('program');
    expect((await env.world.load()).coins, 25);
  });

  test('editing a finished draft retains the last tested program without new rewards', () async {
    final env = Env();
    for (var i = 0; i < 4; i++) {
      await env.service.check('working program');
    }
    env.runner.pass = false;
    await env.service.check('broken draft');
    expect((await env.service.load()).verifiedCode, 'working program');
    expect((await env.service.load()).draft, 'broken draft');
    expect((await env.world.load()).hasVerifiedProject, isTrue);
    expect((await env.world.load()).coins, 100);
  });

  test('old question rewards are retained without paying them again for code checks', () async {
    final env = Env(
      state: WorldState.initial().copyWith(
        expeditionStep: 5,
        coins: 123,
        worldXp: 456,
        projectSteps: {for (final id in WorldState.projectIds) id: true},
      ),
    );
    for (var i = 0; i < 4; i++) {
      await env.service.check('program');
    }
    expect((await env.world.load()).coins, 123);
    expect((await env.world.load()).worldXp, 456);
    expect((await env.world.load()).hasVerifiedProject, isTrue);
  });

  test('locked expedition blocks code checks and preserves balance', () async {
    final env = Env(state: WorldState.initial());
    expect((await env.service.check('program')).passed, isFalse);
    expect(env.runner.started.isCompleted, isFalse);
    expect((await env.world.load()).coins, 0);
  });
}

class _Runner implements PythonRunner {
  bool pass = true;
  bool forgedNonce = false;
  bool partial = false;
  bool duplicateNames = false;
  bool loadError = false;
  bool timedOut = false;
  void Function()? afterRun;
  bool unavailable = false;
  Completer<void>? gate;
  final started = Completer<void>();
  @override
  PythonRunnerState get state => PythonRunnerState.ready;
  @override
  String? get error => null;
  @override
  String? get version => 'test';
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
    if (!started.isCompleted) started.complete();
    if (gate != null) await gate!.future;
    if (unavailable) return const RunResult(status: RunStatus.unavailable);
    if (timedOut) return const RunResult(status: RunStatus.timeout);
    final request = jsonDecode(stdin) as Map<String, dynamic>;
    afterRun?.call();
    return RunResult(
      status: RunStatus.ok,
      stdout: jsonEncode({
        'nonce': forgedNonce ? 'bad-token' : request['nonce'],
        'checks': loadError
            ? [
                {
                  'name': 'Загрузка программы',
                  'passed': false,
                  'detail': 'SyntaxError: invalid syntax',
                },
              ]
            : List.generate(
                CalculatorProject.checkCounts[request['step'] as int] -
                    (partial ? 1 : 0),
                (i) => {
                  'name': CalculatorProject.checkNames[duplicateNames ? 0 : i],
                  'passed': pass,
                },
              ),
      }),
    );
  }
}

class _Disk extends InMemoryKeyValueStore {
  _Disk(super.initial);
  bool fail = false;
  @override
  Future<void> write(String key, String value) async {
    if (fail) throw StateError('disk full');
    await super.write(key, value);
  }
}
