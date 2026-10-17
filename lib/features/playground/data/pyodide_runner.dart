import 'dart:async';
import 'dart:convert';

import 'package:flutter/services.dart';
import 'package:webview_flutter/webview_flutter.dart';

import '../domain/python_runner.dart';
import 'asset_http_server.dart';

/// [PythonRunner] on top of Pyodide (CPython compiled to WebAssembly)
/// running in an invisible WebView. See assets/python_runner/.
class PyodideRunner implements PythonRunner {
  PyodideRunner({AssetBundle? bundle}) : _bundle = bundle ?? rootBundle;

  /// Loading Pyodide on a slow phone can take a while.
  static const Duration loadTimeout = Duration(seconds: 60);

  /// On top of the program's own limit: worker restart, messaging.
  static const Duration resultGrace = Duration(seconds: 6);

  final AssetBundle _bundle;
  final StreamController<PythonRunnerState> _states =
      StreamController<PythonRunnerState>.broadcast();
  final Map<int, Completer<RunResult>> _pending = {};

  AssetHttpServer? _server;
  WebViewController? _controller;
  Completer<void>? _ready;
  Timer? _loadTimer;
  int _nextId = 1;

  PythonRunnerState _state = PythonRunnerState.idle;
  String? _error;
  String? _version;

  /// The WebView to keep in the widget tree (see PythonHost).
  WebViewController? get controller => _controller;

  @override
  PythonRunnerState get state => _state;

  @override
  String? get error => _error;

  @override
  String? get version => _version;

  @override
  Stream<PythonRunnerState> get states => _states.stream;

  void _setState(PythonRunnerState state, {String? error}) {
    _state = state;
    _error = error;
    _states.add(state);
  }

  @override
  Future<void> start() {
    final ready = _ready;
    if (ready != null && _state != PythonRunnerState.failed) return ready.future;
    final completer = _ready = Completer<void>();
    _setState(PythonRunnerState.loading);
    unawaited(_boot(completer));
    return completer.future;
  }

  Future<void> _boot(Completer<void> completer) async {
    try {
      _server ??= await AssetHttpServer.start(_bundle);
      final origin = _server!.origin;
      final controller = WebViewController();
      await controller.setJavaScriptMode(JavaScriptMode.unrestricted);
      await controller.addJavaScriptChannel(
        'BytecraftChannel',
        onMessageReceived: (message) => _onMessage(message.message),
      );
      await controller.setNavigationDelegate(
        NavigationDelegate(
          onNavigationRequest: (request) =>
              Uri.tryParse(request.url)?.host == origin.host
                  ? NavigationDecision.navigate
                  : NavigationDecision.prevent,
          onWebResourceError: (error) {
            if (error.isForMainFrame != false) {
              _fail('Не удалось открыть интерпретатор: ${error.description}');
            }
          },
        ),
      );
      _controller = controller;
      _states.add(_state); // the host widget can now show the WebView
      _loadTimer = Timer(loadTimeout, () {
        if (_state == PythonRunnerState.loading) {
          _fail('Python загружался слишком долго');
        }
      });
      await controller.loadRequest(
        origin.replace(path: '/python_runner/index.html'),
      );
    } catch (error) {
      _fail('Не удалось запустить интерпретатор: $error');
    }
  }

  void _fail(String message) {
    _loadTimer?.cancel();
    _setState(PythonRunnerState.failed, error: message);
    final ready = _ready;
    if (ready != null && !ready.isCompleted) ready.completeError(message);
    for (final pending in _pending.values) {
      if (!pending.isCompleted) {
        pending.complete(RunResult(status: RunStatus.unavailable, stderr: message));
      }
    }
    _pending.clear();
  }

  void _onMessage(String text) {
    final Object? decoded;
    try {
      decoded = jsonDecode(text);
    } catch (_) {
      return;
    }
    if (decoded is! Map<String, dynamic>) return;
    switch (decoded['type']) {
      case 'status':
        switch (decoded['state']) {
          case 'ready':
            _loadTimer?.cancel();
            _version = decoded['version'] as String?;
            _setState(PythonRunnerState.ready);
            final ready = _ready;
            if (ready != null && !ready.isCompleted) ready.complete();
          case 'loading':
            // A restart after a hard stop: runs queue up in the page.
            if (_state != PythonRunnerState.ready) {
              _setState(PythonRunnerState.loading);
            }
          case 'failed':
            _fail('Python не запустился: ${decoded['message']}');
        }
      case 'result':
        final id = decoded['id'];
        final completer = id is int ? _pending.remove(id) : null;
        if (completer == null || completer.isCompleted) return;
        completer.complete(
          RunResult(
            status: switch (decoded['status']) {
              'ok' => RunStatus.ok,
              'timeout' || 'interrupted' => RunStatus.timeout,
              'limit' => RunStatus.limit,
              _ => RunStatus.error,
            },
            stdout: decoded['stdout'] as String? ?? '',
            stderr: decoded['stderr'] as String? ?? '',
            duration: Duration(
              milliseconds: (decoded['durationMs'] as num?)?.toInt() ?? 0,
            ),
          ),
        );
    }
  }

  @override
  Future<RunResult> run(
    String code, {
    String stdin = '',
    Duration timeout = const Duration(seconds: 5),
    bool echoInputPrompt = true,
  }) async {
    try {
      await start();
    } catch (_) {
      return RunResult(
        status: RunStatus.unavailable,
        stderr: _error ?? 'Интерпретатор недоступен',
      );
    }
    final controller = _controller;
    if (controller == null) {
      return const RunResult(status: RunStatus.unavailable);
    }
    final id = _nextId++;
    final completer = _pending[id] = Completer<RunResult>();
    final job = jsonEncode({
      'id': id,
      'code': code,
      'stdin': stdin,
      'quietInput': !echoInputPrompt,
      'timeoutMs': timeout.inMilliseconds,
    });
    try {
      await controller.runJavaScript('window.bytecraft.run($job);');
    } catch (error) {
      _pending.remove(id);
      return RunResult(status: RunStatus.unavailable, stderr: '$error');
    }
    return completer.future.timeout(
      timeout + resultGrace,
      onTimeout: () {
        _pending.remove(id);
        unawaited(
          controller.runJavaScript('window.bytecraft.restart();').catchError((_) {}),
        );
        return RunResult(status: RunStatus.timeout, duration: timeout);
      },
    );
  }

  Future<void> dispose() async {
    _loadTimer?.cancel();
    await _server?.close();
    await _states.close();
  }
}
