import 'dart:async';

import 'package:flutter/material.dart';

import '../models/level.dart';
import '../state/app_controller.dart';

class LearningMapScreen extends StatefulWidget {
  const LearningMapScreen({
    super.key,
    required this.levels,
    required this.controller,
    required this.onLevel,
  });

  final List<Level> levels;
  final AppController controller;
  final void Function(Level level) onLevel;

  @override
  State<LearningMapScreen> createState() => _LearningMapScreenState();
}

class _LearningMapScreenState extends State<LearningMapScreen> {
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    widget.controller.refreshHardcoreExpirations(widget.levels);
    if (widget.controller.progress.hardcoreMode) {
      _timer = Timer.periodic(const Duration(seconds: 1), (_) async {
        await widget.controller.refreshHardcoreExpirations(widget.levels);
        if (mounted) setState(() {});
      });
    }
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final progress = widget.controller.progress;
    final hardcore = progress.hardcoreMode;
    return Scaffold(
      appBar: AppBar(
        title: Text(hardcore ? 'Python Hardcore' : 'Python Path'),
        actions: [
          if (hardcore)
            const Padding(
              padding: EdgeInsets.only(right: 16),
              child: Center(child: Text('×2 XP', style: TextStyle(fontWeight: FontWeight.w800))),
            ),
        ],
      ),
      body: ListView.builder(
        padding: const EdgeInsets.fromLTRB(20, 10, 20, 32),
        itemCount: widget.levels.length,
        itemBuilder: (context, index) {
          final level = widget.levels[index];
          final showHeader = index == 0 || widget.levels[index - 1].module != level.module;
          final done = widget.controller.isCompleted(level);
          final unlocked = widget.controller.isUnlocked(widget.levels, index);
          final remaining = hardcore ? widget.controller.hardcoreRemainingFor(level.module) : null;
          return Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
            if (showHeader)
              Padding(
                padding: const EdgeInsets.only(top: 18, bottom: 10),
                child: Row(children: [
                  Expanded(
                    child: Text(
                      level.module,
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800),
                    ),
                  ),
                  if (hardcore && remaining != null)
                    _TimerBadge(remaining: remaining)
                  else if (hardcore)
                    Text('${widget.controller.hardcoreDurationFor(level.module).inMinutes} мин', style: const TextStyle(fontWeight: FontWeight.w700)),
                ]),
              ),
            Card(
              child: ListTile(
                enabled: unlocked,
                onTap: unlocked ? () => widget.onLevel(level) : null,
                leading: CircleAvatar(
                  child: Icon(done ? Icons.check : (unlocked ? (hardcore ? Icons.timer_outlined : Icons.code) : Icons.lock_outline)),
                ),
                title: Text(level.title, style: const TextStyle(fontWeight: FontWeight.w700)),
                subtitle: Text('${hardcore ? level.xp * 2 : level.xp} XP • ${_typeName(level.type)}'),
                trailing: done ? const Text('★★★') : const Icon(Icons.chevron_right),
              ),
            ),
            const SizedBox(height: 10),
          ]);
        },
      ),
    );
  }

  String _typeName(LevelType type) => switch (type) {
    LevelType.multipleChoice => 'Выбор ответа',
    LevelType.fillMissing => 'Пропуск в коде',
    LevelType.codeOrdering => 'Порядок строк',
  };
}

class _TimerBadge extends StatelessWidget {
  const _TimerBadge({required this.remaining});
  final Duration remaining;

  @override
  Widget build(BuildContext context) {
    final minutes = remaining.inMinutes.remainder(60).toString().padLeft(2, '0');
    final seconds = remaining.inSeconds.remainder(60).toString().padLeft(2, '0');
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.errorContainer,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(mainAxisSize: MainAxisSize.min, children: [
        const Icon(Icons.timer, size: 18),
        const SizedBox(width: 5),
        Text('$minutes:$seconds', style: const TextStyle(fontWeight: FontWeight.w800)),
      ]),
    );
  }
}
