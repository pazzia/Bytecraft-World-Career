import 'package:flutter/material.dart';
import '../models/progress.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key, required this.progress});
  final AppProgress progress;

  @override
  Widget build(BuildContext context) {
    final accountLevel = 1 + progress.totalXp ~/ 100;
    return Scaffold(
      appBar: AppBar(title: const Text('Профиль')),
      body: ListView(padding: const EdgeInsets.all(20), children: [
        const CircleAvatar(radius: 40, child: Icon(Icons.person, size: 42)),
        const SizedBox(height: 14),
        Text('Coder #1', textAlign: TextAlign.center, style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800)),
        Text('Уровень $accountLevel', textAlign: TextAlign.center),
        const SizedBox(height: 24),
        Card(child: Column(children: [
          ListTile(leading: const Icon(Icons.bolt), title: const Text('Всего XP'), trailing: Text('${progress.totalXp}')),
          ListTile(leading: const Icon(Icons.check_circle_outline), title: const Text('Пройдено уровней'), trailing: Text('${progress.completedLevelIds.length}')),
          ListTile(leading: const Icon(Icons.local_fire_department), title: const Text('Текущая серия'), trailing: Text('${progress.streak} дн.')),
        ])),
      ]),
    );
  }
}
