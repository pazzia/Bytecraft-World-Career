import 'package:flutter/material.dart';

import '../core/level_engine.dart';
import '../models/level.dart';
import '../widgets/code_card.dart';

class LevelScreen extends StatefulWidget {
  const LevelScreen({super.key, required this.level, required this.onSubmit});
  final Level level;
  final Future<LevelResult> Function(String answer, int mistakes) onSubmit;

  @override
  State<LevelScreen> createState() => _LevelScreenState();
}

class _LevelScreenState extends State<LevelScreen> {
  String? selected;
  late List<String> ordered;
  int mistakes = 0;
  bool busy = false;

  @override
  void initState() {
    super.initState();
    ordered = List<String>.of(widget.level.options);
  }

  String get answer {
    if (widget.level.type == LevelType.codeOrdering) return ordered.join('\n');
    return selected ?? '';
  }

  Future<void> _check() async {
    if (answer.isEmpty || busy) return;
    setState(() => busy = true);
    final result = await widget.onSubmit(answer, mistakes);
    if (!mounted) return;
    setState(() => busy = false);

    if (result.isCorrect) {
      await showModalBottomSheet<void>(
        context: context,
        isDismissible: false,
        enableDrag: false,
        builder: (context) => SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.stretch, children: [
              const Icon(Icons.check_circle, size: 64),
              const SizedBox(height: 12),
              Text('Верно!', textAlign: TextAlign.center, style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.w800)),
              const SizedBox(height: 6),
              Text('+${result.xpAwarded} XP', textAlign: TextAlign.center),
              Text(List<String>.filled(result.stars, '★').join(), textAlign: TextAlign.center, style: const TextStyle(fontSize: 28)),
              const SizedBox(height: 14),
              Text(widget.level.explanation, textAlign: TextAlign.center),
              const SizedBox(height: 20),
              FilledButton(onPressed: () { Navigator.pop(context); Navigator.pop(context); }, child: const Text('Продолжить')),
            ]),
          ),
        ),
      );
    } else {
      setState(() => mistakes++);
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Пока неверно. Попробуй ещё раз — потеряна 1 жизнь.')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.level.module)),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
            Text(widget.level.title, style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800)),
            const SizedBox(height: 6),
            Text(widget.level.description, style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 18),
            CodeCard(code: widget.level.code),
            const SizedBox(height: 18),
            Expanded(child: _body()),
            FilledButton(
              onPressed: (answer.isEmpty || busy) ? null : _check,
              style: FilledButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16)),
              child: Text(busy ? 'Проверяю…' : 'Проверить'),
            ),
          ]),
        ),
      ),
    );
  }

  Widget _body() {
    if (widget.level.type == LevelType.codeOrdering) {
      return ReorderableListView.builder(
        itemCount: ordered.length,
        onReorder: (oldIndex, newIndex) {
          setState(() {
            if (newIndex > oldIndex) newIndex--;
            final item = ordered.removeAt(oldIndex);
            ordered.insert(newIndex, item);
          });
        },
        itemBuilder: (context, index) => Card(
          key: ValueKey('${ordered[index]}-$index'),
          child: ListTile(
            leading: const Icon(Icons.drag_handle),
            title: Text(ordered[index], style: const TextStyle(fontFamily: 'monospace')),
          ),
        ),
      );
    }

    return ListView.separated(
      itemCount: widget.level.options.length,
      separatorBuilder: (_, __) => const SizedBox(height: 10),
      itemBuilder: (context, index) {
        final option = widget.level.options[index];
        return ChoiceChip(
          label: SizedBox(width: double.infinity, child: Text(option, textAlign: TextAlign.center, style: const TextStyle(fontFamily: 'monospace', fontSize: 16))),
          selected: selected == option,
          onSelected: (_) => setState(() => selected = option),
          padding: const EdgeInsets.symmetric(vertical: 14),
        );
      },
    );
  }
}
