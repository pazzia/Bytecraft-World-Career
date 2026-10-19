import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/routes.dart';
import '../domain/story_journey.dart';
import 'world_ui.dart';

class StoryGuide extends StatelessWidget {
  const StoryGuide({required this.journey, this.showAction = true, super.key});
  final StoryJourney journey;
  final bool showAction;
  static String route(StoryDestination destination) => switch (destination) {
    StoryDestination.expedition => Routes.worldExpedition,
    StoryDestination.project => Routes.worldBuild,
    StoryDestination.boss => Routes.worldBoss,
    StoryDestination.course => Routes.map,
  };
  @override
  Widget build(BuildContext context) => WorldPanel(
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          'Твой маршрут · ${journey.completedStages}/3 этапов',
          style: const TextStyle(
            color: WorldPalette.cyan,
            fontWeight: FontWeight.w800,
          ),
        ),
        const SizedBox(height: 10),
        for (final item in [
          (
            'Экспедиция',
            '${journey.world.expeditionProgress}/5 задач',
            journey.world.expeditionProgress == 5,
          ),
          (
            'Калькулятор',
            '${journey.projectCount}/4 проверено',
            journey.world.hasVerifiedProject,
          ),
          (
            'Босс',
            '${journey.world.bossTask.clamp(0, 4)}/4 уязвимостей',
            journey.world.bossCleared,
          ),
        ])
          Padding(
            padding: const EdgeInsets.only(bottom: 5),
            child: Row(
              children: [
                Icon(
                  item.$3 ? Icons.check_circle : Icons.radio_button_unchecked,
                  size: 18,
                  color: item.$3 ? WorldPalette.green : WorldPalette.muted,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    '${item.$1} · ${item.$2}',
                    style: const TextStyle(color: WorldPalette.text),
                  ),
                ),
              ],
            ),
          ),
        const Divider(color: WorldPalette.border),
        Text(
          'Сейчас: ${journey.title}',
          style: const TextStyle(
            color: WorldPalette.text,
            fontSize: 18,
            fontWeight: FontWeight.w800,
          ),
        ),
        const SizedBox(height: 6),
        Text(
          journey.instruction,
          style: const TextStyle(color: WorldPalette.text),
        ),
        const SizedBox(height: 6),
        Text(journey.result, style: const TextStyle(color: WorldPalette.muted)),
        if (showAction) ...[
          const SizedBox(height: 12),
          WorldButton(
            label: journey.action,
            icon: Icons.arrow_forward_rounded,
            onPressed: () => context.push(route(journey.destination)),
          ),
        ],
      ],
    ),
  );
}
