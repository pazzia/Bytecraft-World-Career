import 'package:bytecraft/shared/widgets/code_block.dart';
import 'package:bytecraft/shared/widgets/code_copy.dart';
import 'package:bytecraft/features/playground/presentation/code_editor.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('copy unlocks on third error and copies raw code without line numbers', (tester) async {
    const code = 'for n in [1, 2]:\n    print(n)';
    String? copied;
    tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(SystemChannels.platform, (call) async {
      if (call.method == 'Clipboard.setData') copied = (call.arguments as Map)['text'] as String;
      return null;
    });
    addTearDown(() => tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(SystemChannels.platform, null));
    for (final errors in [0, 1, 2, 3, 4, 0]) {
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: CodeCopyScope(
        wrongAnswers: errors, child: const CodeBlock(code: code)))));
      expect(find.byTooltip('Скопировать код'), errors >= 3 ? findsOneWidget : findsNothing);
      if (errors == 3) {
        await tester.tap(find.byTooltip('Скопировать код'));
        await tester.pump();
        expect(copied, code);
      }
    }
  });

  testWidgets('editor hint is not text and clear updates the draft', (tester) async {
    final controller = TextEditingController();
    addTearDown(controller.dispose);
    String? changed;
    await tester.pumpWidget(MaterialApp(home: Scaffold(body: SingleChildScrollView(child:
      CodeEditor(controller: controller, onChanged: (text) => changed = text)))));
    expect(controller.text, isEmpty);
    await tester.enterText(find.byKey(const ValueKey('code_editor')), 'print(42)');
    await tester.tap(find.byTooltip('Очистить код'));
    await tester.pump();
    expect(controller.text, isEmpty);
    expect(changed, '');
  });
}
