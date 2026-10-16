/// Resource limits every runner MUST enforce. User code is untrusted:
/// it is never executed directly on application servers.
class ExecutionLimits {
  const ExecutionLimits({
    this.timeout = const Duration(seconds: 3),
    this.memoryMb = 64,
    this.cpuTimeMs = 2000,
    this.networkAccess = false,
    this.maxOutputBytes = 64 * 1024,
  });

  final Duration timeout;
  final int memoryMb;
  final int cpuTimeMs;
  final bool networkAccess;
  final int maxOutputBytes;
}

enum ExecutionStatus { success, runtimeError, timeout, limitExceeded, unavailable }

class ExecutionResult {
  const ExecutionResult({
    required this.status,
    this.stdout = '',
    this.stderr = '',
    this.duration = Duration.zero,
  });

  final ExecutionStatus status;
  final String stdout;
  final String stderr;
  final Duration duration;
}

/// Port for real code execution.
///
/// Planned adapters:
///  * RemoteSandboxCodeRunner — isolated container/microVM per run
///    (gVisor/Firecracker), no network, cgroup CPU/memory limits, timeout.
///  * LocalCodeRunner — on-device interpreter (e.g. Pyodide in a WebView)
///    for offline levels.
abstract interface class CodeExecutionService {
  Future<ExecutionResult> execute(
    String language,
    String code, {
    ExecutionLimits limits = const ExecutionLimits(),
  });
}

/// MVP adapter: levels use predefined validation, nothing is executed.
class UnavailableCodeExecutionService implements CodeExecutionService {
  const UnavailableCodeExecutionService();

  @override
  Future<ExecutionResult> execute(
    String language,
    String code, {
    ExecutionLimits limits = const ExecutionLimits(),
  }) async =>
      const ExecutionResult(status: ExecutionStatus.unavailable);
}
