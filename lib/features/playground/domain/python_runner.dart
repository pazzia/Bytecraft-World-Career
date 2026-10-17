import 'dart:async';

/// State of the on-device Python interpreter.
enum PythonRunnerState {
  /// Not started yet (the interpreter loads on first use).
  idle,
  loading,
  ready,

  /// Could not start (old WebView, missing assets...). [PythonRunner.error]
  /// says why.
  failed,
}

enum RunStatus {
  ok,

  /// The program raised an exception (traceback in stderr).
  error,

  /// Stopped by the time limit.
  timeout,

  /// Printed more than the output limit.
  limit,

  /// The interpreter is not available.
  unavailable,
}

class RunResult {
  const RunResult({
    required this.status,
    this.stdout = '',
    this.stderr = '',
    this.duration = Duration.zero,
  });

  final RunStatus status;
  final String stdout;
  final String stderr;
  final Duration duration;

  bool get isOk => status == RunStatus.ok;
}

/// Runs Python programs on the device.
abstract interface class PythonRunner {
  PythonRunnerState get state;

  /// Why the interpreter failed to start (for [PythonRunnerState.failed]).
  String? get error;

  /// Python version string once ready, e.g. "3.12.7".
  String? get version;

  Stream<PythonRunnerState> get states;

  /// Starts loading the interpreter if it isn't loaded yet.
  Future<void> start();

  Future<RunResult> run(
    String code, {
    String stdin = '',
    Duration timeout = const Duration(seconds: 5),
  });
}
