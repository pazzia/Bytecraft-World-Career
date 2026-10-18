import 'package:bytecraft/features/playground/domain/python_runner.dart';

/// Answers runs from a table: (code, stdin) -> result. Records every call.
class FakePythonRunner implements PythonRunner {
  FakePythonRunner(this.respond);

  final RunResult Function(String code, String stdin) respond;
  final List<({String code, String stdin, bool echo})> calls = [];

  @override
  PythonRunnerState get state => PythonRunnerState.ready;

  @override
  String? get error => null;

  @override
  String? get version => '3.12.7';

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
    calls.add((code: code, stdin: stdin, echo: echoInputPrompt));
    return respond(code, stdin);
  }
}
