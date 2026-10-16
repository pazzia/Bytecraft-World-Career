import 'package:flutter/material.dart';

import '../models/progress.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({
    super.key,
    required this.progress,
    required this.onContinue,
    required this.onProfile,
    required this.onHardcoreChanged,
  });
  final AppProgress progress;
  final VoidCallback onContinue;
  final VoidCallback onProfile;
  final ValueChanged<bool> onHardcoreChanged;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('CodeQuest', style: TextStyle(fontWeight: FontWeight.w800)),
        actions: [IconButton(onPressed: onProfile, icon: const Icon(Icons.person_outline))],
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Row(children: [
            Expanded(child: _Stat(icon: Icons.local_fire_department, value: '${progress.streak}', label: 'серия')),
            const SizedBox(width: 10),
            Expanded(child: _Stat(icon: Icons.bolt, value: '${progress.totalXp}', label: 'XP')),
            const SizedBox(width: 10),
            Expanded(child: _Stat(icon: Icons.favorite, value: '${progress.lives}', label: 'жизни')),
          ]),
          const SizedBox(height: 18),
          Card(
            child: SwitchListTile(
              value: progress.hardcoreMode,
              onChanged: onHardcoreChanged,
              secondary: const Icon(Icons.local_fire_department_outlined),
              title: const Text('Hardcore Mode', style: TextStyle(fontWeight: FontWeight.w800)),
              subtitle: const Text('Пройди всю рубрику до истечения таймера. Ошибка по времени сбрасывает хардкор-прогресс рубрики. ×2 XP.'),
            ),
          ),
          const SizedBox(height: 18),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(progress.hardcoreMode ? 'PYTHON HARDCORE' : 'PYTHON PATH', style: const TextStyle(fontWeight: FontWeight.w700)),
                const SizedBox(height: 8),
                Text(progress.hardcoreMode ? 'Испытание на время' : 'Основы Python', style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800)),
                const SizedBox(height: 8),
                Text(progress.hardcoreMode
                    ? '${progress.hardcoreCompletedLevelIds.length} из 20 хардкор-уровней завершено'
                    : '${progress.completedLevelIds.length} из 20 уровней завершено'),
                const SizedBox(height: 14),
                LinearProgressIndicator(value: (progress.hardcoreMode ? progress.hardcoreCompletedLevelIds.length : progress.completedLevelIds.length) / 20),
                const SizedBox(height: 18),
                SizedBox(width: double.infinity, child: FilledButton.icon(onPressed: onContinue, icon: Icon(progress.hardcoreMode ? Icons.timer : Icons.play_arrow), label: Text(progress.hardcoreMode ? 'Начать Hardcore' : 'Продолжить обучение'))),
              ]),
            ),
          ),
          const SizedBox(height: 18),
          const Card(
            child: ListTile(
              leading: CircleAvatar(child: Icon(Icons.calendar_today)),
              title: Text('Daily Challenge'),
              subtitle: Text('Скоро: ежедневная задача и бонус XP'),
              trailing: Icon(Icons.lock_outline),
            ),
          ),
        ],
      ),
    );
  }
}

class _Stat extends StatelessWidget {
  const _Stat({required this.icon, required this.value, required this.label});
  final IconData icon;
  final String value;
  final String label;
  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.symmetric(vertical: 14),
      child: Column(children: [Icon(icon), const SizedBox(height: 5), Text(value, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800)), Text(label, style: Theme.of(context).textTheme.bodySmall)]),
    ),
  );
}
