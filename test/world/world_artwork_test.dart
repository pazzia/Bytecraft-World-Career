import 'package:bytecraft/features/world/presentation/world_ui.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('City labels fit a narrow phone and open the selected building',
      (tester) async {
    tester.view.physicalSize = const Size(320, 800);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    String? selected;
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: WorldCityScene(
          levels: const {'office': 3, 'python': 2},
          onBuilding: (id) => selected = id,
        ),
      ),
    ));
    await tester.pumpAndSettle();
    expect(tester.takeException(), isNull);
    expect(find.text('Офис · 3'), findsOneWidget);
    await tester.tap(find.text('Офис · 3'));
    expect(selected, 'office');
    await tester.tap(find.text('Python Lab · 2'));
    expect(selected, 'python');
  });

  testWidgets('All atlas scenes render without layout or asset errors',
      (tester) async {
    for (final scene in WorldScene.values) {
      await tester.pumpWidget(MaterialApp(
        home: Center(child: SizedBox(
          width: 288, height: 250, child: WorldArtwork(scene),
        )),
      ));
      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull, reason: scene.name);
    }
  });
}
