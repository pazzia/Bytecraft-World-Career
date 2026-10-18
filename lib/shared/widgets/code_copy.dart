import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Copying is an earned aid for the current exercise, never a global unlock.
class CodeCopyScope extends InheritedWidget {
  const CodeCopyScope({super.key, required this.wrongAnswers, required super.child});
  final int wrongAnswers;
  static bool enabled(BuildContext context) =>
      (context.dependOnInheritedWidgetOfExactType<CodeCopyScope>()?.wrongAnswers ?? 0) >= 3;
  @override
  bool updateShouldNotify(CodeCopyScope oldWidget) => wrongAnswers != oldWidget.wrongAnswers;
}

class CodeCopyButton extends StatelessWidget {
  const CodeCopyButton({super.key, required this.code});
  final String code;
  @override
  Widget build(BuildContext context) {
    if (!CodeCopyScope.enabled(context) || code.trim().isEmpty) return const SizedBox.shrink();
    return Align(
      alignment: Alignment.centerRight,
      child: IconButton(
        tooltip: 'Скопировать код',
        icon: const Icon(Icons.copy_rounded, color: Color(0xFFCFA7FF)),
        onPressed: () async {
          await Clipboard.setData(ClipboardData(text: code));
          if (context.mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Код скопирован')),
            );
          }
        },
      ),
    );
  }
}
