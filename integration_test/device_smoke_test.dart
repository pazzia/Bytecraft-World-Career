@Timeout(Duration(minutes: 6))
library;

// Runs on a real platform (iOS Simulator in CI): the app starts, and the
// in-app Python (Pyodide in a WebView served from 127.0.0.1) runs programs.
import 'package:bytecraft/app/bootstrap.dart';
import 'package:bytecraft/features/playground/data/pyodide_runner.dart';
import 'package:bytecraft/features/playground/domain/python_runner.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:webview_flutter/webview_flutter.dart';

Future<void> pumpUntil(WidgetTester tester, Finder finder, {Duration timeout = const Duration(seconds: 40)}) async {
  final end = DateTime.now().add(timeout);
  while (DateTime.now().isBefore(end)) {
    await tester.pump(const Duration(milliseconds: 250));
    if (finder.evaluate().isNotEmpty) return;
  }
  throw TestFailure('not found in $timeout: $finder');
}

// ignore: avoid_print
void step(String message) => print('[smoke] $message');

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('app starts past the splash', (tester) async {
    step('bootstrap');
    await bootstrap();
    await pumpUntil(tester, find.text('Код за пару минут в день'));
    // Splash -> onboarding (fresh install) or home.
    await pumpUntil(
      tester,
      find.byWidgetPredicate((w) => w is Text && (w.data == 'Немного знаю' || w.data == 'Обучение')),
    );
  });

  testWidgets('Python runs in the WebView', (tester) async {
    step('python: start');
    final runner = PyodideRunner();
    final started = runner.start();
    final end = DateTime.now().add(const Duration(seconds: 90));
    while (runner.controller == null && runner.state != PythonRunnerState.failed && DateTime.now().isBefore(end)) {
      await tester.runAsync(() => Future<void>.delayed(const Duration(milliseconds: 100)));
    }
    final controller = runner.controller;
    expect(controller, isNotNull, reason: runner.error);
    await tester.pumpWidget(
      MaterialApp(
        home: Stack(
          children: [
            const Center(child: Text('python')),
            Positioned(left: 0, bottom: 0, width: 1, height: 1, child: WebViewWidget(controller: controller!)),
          ],
        ),
      ),
    );
    while (runner.state == PythonRunnerState.loading && DateTime.now().isBefore(end)) {
      await tester.runAsync(() => Future<void>.delayed(const Duration(milliseconds: 500)));
      await tester.pump();
    }
    step('python: ${runner.state}');
    expect(runner.state, PythonRunnerState.ready, reason: runner.error);
    await tester.runAsync(() => started);
    // ignore: avoid_print
    print('Python: ${runner.version}');

    Future<RunResult> run(String code, {String stdin = '', Duration timeout = const Duration(seconds: 5)}) async =>
        (await tester.runAsync(() => runner.run(code, stdin: stdin, timeout: timeout)))!;

    step('simple');
    final simple = await run('print(sum(range(10)), "привет")');
    expect(simple.status, RunStatus.ok, reason: simple.stderr);
    expect(simple.stdout, '45 привет\n');

    step('input');
    final input = await run('name = input()\nprint("Hi,", name)', stdin: 'Ann\n');
    expect(input.stdout.trim().endsWith('Hi, Ann'), isTrue, reason: input.stdout);

    step('threads');
    final threads = await run(
      'import threading\n'
      'out = []\n'
      'def work(n):\n'
      '    out.append(n * n)\n'
      'ts = [threading.Thread(target=work, args=(i,)) for i in range(4)]\n'
      'for t in ts: t.start()\n'
      'for t in ts: t.join()\n'
      'print(sorted(out))',
    );
    expect(threads.stdout, '[0, 1, 4, 9]\n', reason: threads.stderr);

    step('aio');
    final aio = await run(
      'import asyncio\n'
      'async def f(x):\n'
      '    await asyncio.sleep(0.01)\n'
      '    return x * 2\n'
      'async def main():\n'
      '    print(await asyncio.gather(f(1), f(2)))\n'
      'asyncio.run(main())',
    );
    expect(aio.stdout, '[2, 4]\n', reason: aio.stderr);

    step('error');
    final error = await run('1 / 0');
    expect(error.status, RunStatus.error);
    expect(error.stderr, contains('ZeroDivisionError'));

    step('loop');
    final loop = await run('while True:\n    pass');
    expect(loop.status, RunStatus.timeout);

    // After a hard stop the worker restarts and reloads Python.
    step('after');
    final after = await run('print("still alive")', timeout: const Duration(seconds: 60));
    expect(after.stdout, 'still alive\n', reason: after.stderr);
  });
}
