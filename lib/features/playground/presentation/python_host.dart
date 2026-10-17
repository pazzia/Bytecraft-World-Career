import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:webview_flutter/webview_flutter.dart';

import '../data/pyodide_runner.dart';
import 'playground_providers.dart';

/// Keeps the interpreter's WebView in the widget tree (1×1 px, invisible
/// to the player) once it has been started. Lives in the main shell so the
/// interpreter survives tab switches.
class PythonHost extends ConsumerWidget {
  const PythonHost({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    ref.watch(pythonRunnerStateProvider);
    final runner = ref.watch(pythonRunnerProvider);
    final controller = runner is PyodideRunner ? runner.controller : null;
    if (controller == null) {
      // Positioned even when empty: in the shell's expanding Stack a
      // non-positioned child would cover the whole screen.
      return const Positioned(left: 0, bottom: 0, width: 0, height: 0, child: SizedBox.shrink());
    }
    return Positioned(
      left: 0,
      bottom: 0,
      width: 1,
      height: 1,
      child: IgnorePointer(
        child: ExcludeSemantics(child: WebViewWidget(controller: controller)),
      ),
    );
  }
}
