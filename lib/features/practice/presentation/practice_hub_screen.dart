import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/routes.dart';
import '../../learning_map/presentation/learning_map_providers.dart';
import '../../world/presentation/world_ui.dart';

class PracticeHubScreen extends ConsumerWidget {
  const PracticeHubScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) => WorldPage(
        title: 'Практика',
        subtitle: 'Пиши код и разбирай ошибки',
        child: ListView(padding: const EdgeInsets.all(16), children: [
          _option(
            title: 'Написать код',
            description: 'Пустой редактор Python, запуск программы и задачи с проверками.',
            button: 'Открыть редактор',
            icon: Icons.terminal_rounded,
            action: () => context.go(Routes.playground)),
          const SizedBox(height: 12),
          _option(
            title: 'Работа над ошибками',
            description: 'Ошибки по темам и 100 разных заданий для тренировки основ Python.',
            button: 'Разобрать ошибки',
            icon: Icons.biotech_rounded,
            action: () => context.go(Routes.journal)),
          const SizedBox(height: 12),
          _option(
            title: 'На время',
            description: 'Забег по модулю курса с общим таймером. Жизни не расходуются.',
            button: 'Выбрать модуль',
            icon: Icons.timer_outlined,
            action: () {
              ref.read(mapModeProvider.notifier).select(MapMode.timed);
              context.go(Routes.map);
            }),
        ]),
      );

  Widget _option({required String title,
    required String description, required String button, required IconData icon,
    required VoidCallback action}) => WorldPanel(child: Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(title, style: const TextStyle(color: WorldPalette.text,
          fontSize: 19, fontWeight: FontWeight.w800)),
        const SizedBox(height: 8),
        Text(description, style: const TextStyle(color: WorldPalette.muted)),
        const SizedBox(height: 12),
        WorldButton(label: button, icon: icon, onPressed: action),
      ],
    ));
}
