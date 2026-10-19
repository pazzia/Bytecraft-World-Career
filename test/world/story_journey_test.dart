import 'package:bytecraft/features/world/domain/story_journey.dart';
import 'package:bytecraft/features/world/domain/world_state.dart';
import 'package:bytecraft/features/world/presentation/story_guide.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('journey follows expedition, chest, actual code, boss and course', () {
    var s = WorldState.initial();
    expect(StoryJourney(s).destination, StoryDestination.expedition);
    s = s.copyWith(expeditionStep: 5);
    expect(StoryJourney(s).action, 'Забрать сундук экспедиции');
    s = s.copyWith(
      expeditionChestClaimed: true,
      projectSteps: {for (final id in WorldState.projectIds) id: true},
    );
    final migrated = StoryJourney(s, verifiedComponents: 1);
    expect(migrated.destination, StoryDestination.project);
    expect(migrated.projectCount, 1);
    expect(migrated.completedStages, 1);
    s = s.copyWith(hasVerifiedProject: true);
    expect(StoryJourney(s).destination, StoryDestination.boss);
    s = s.copyWith(bossCleared: true, bossTask: 4, bossHp: 0);
    expect(StoryJourney(s).destination, StoryDestination.course);
    expect(StoryJourney(s).completedStages, 3);
  });

  testWidgets(
    'next action, result and all stages fit a narrow phone with larger text',
    (tester) async {
      tester.view.physicalSize = const Size(320, 900);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.reset);
      await tester.pumpWidget(
        MaterialApp(
          home: MediaQuery(
            data: const MediaQueryData(textScaler: TextScaler.linear(1.5)),
            child: Scaffold(
              body: SingleChildScrollView(
                child: StoryGuide(journey: StoryJourney(WorldState.initial())),
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.text('Сейчас: Восстанови API'), findsOneWidget);
      expect(find.text('Экспедиция · 0/5 задач'), findsOneWidget);
      expect(find.text('Калькулятор · 0/4 проверено'), findsOneWidget);
      expect(find.textContaining('После 5 задач откроются'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );
}
