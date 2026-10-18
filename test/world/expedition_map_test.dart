import 'dart:io';
import 'dart:ui' as ui;

import 'package:bytecraft/features/world/domain/world_challenge.dart';
import 'package:bytecraft/features/world/domain/world_rules.dart';
import 'package:bytecraft/features/world/domain/world_state.dart';
import 'package:bytecraft/features/world/presentation/expedition_map.dart';
import 'package:bytecraft/features/world/presentation/world_ui.dart';
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  setUpAll(() async {
    final fonts = FontLoader('Onest')
      ..addFont(rootBundle.load('assets/fonts/Onest-Regular.ttf'));
    await fonts.load();
  });

  testWidgets('whole square map, all stages and explorer fit at every progress on phones', (tester) async {
    for (final width in [320.0, 390.0]) {
      tester.view.physicalSize = Size(width, 900);
      tester.view.devicePixelRatio = 1;
      for (var step = 0; step <= 5; step++) {
        final boundaryKey = GlobalKey();
        await tester.pumpWidget(MaterialApp(theme: ThemeData(fontFamily: 'Onest'),
          home: Scaffold(backgroundColor: WorldPalette.bg, body: SingleChildScrollView(
            child: Padding(padding: const EdgeInsets.all(16), child: RepaintBoundary(
              key: boundaryKey, child: ExpeditionMap(completed: step)))))));
        await tester.pumpAndSettle();
        expect(find.byKey(const ValueKey('expedition-progress')), findsOneWidget);
        expect(find.text('$step / 5'), findsOneWidget);
        for (var i = 0; i < 5; i++) {
          expect(find.byKey(ValueKey('expedition-node-$i')), findsOneWidget);
        }
        final map = tester.getSize(find.byType(AspectRatio));
        expect(map.width, map.height);
        final explorer = tester.getRect(find.byKey(const ValueKey('expedition-explorer')));
        final frame = tester.getRect(find.byType(AspectRatio));
        expect(frame.contains(explorer.topLeft), isTrue);
        expect(frame.contains(explorer.bottomRight - const Offset(.1, .1)), isTrue);
        expect(tester.takeException(), isNull);
        if (width == 390 && [0, 3, 5].contains(step)) {
          final boundary = boundaryKey.currentContext!.findRenderObject()! as RenderRepaintBoundary;
          await tester.runAsync(() async {
            final image = await boundary.toImage(pixelRatio: 2);
            final bytes = await image.toByteData(format: ui.ImageByteFormat.png);
            final file = File('build/expedition-preview-$step.png');
            await file.parent.create(recursive: true);
            await file.writeAsBytes(bytes!.buffer.asUint8List());
            image.dispose();
          });
        }
      }
    }
    tester.view.reset();
  });

  testWidgets('wrong answer keeps position, correct moves to next platform and stays after restore', (tester) async {
    var state = WorldState.initial();
    Future<Offset> show() async {
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: SingleChildScrollView(
        child: ExpeditionMap(completed: state.expeditionStep)))));
      await tester.pumpAndSettle();
      return tester.getTopLeft(find.byKey(const ValueKey('expedition-explorer')));
    }
    final before = await show();
    final q = WorldChallenges.at(state, WorldMode.expedition);
    state = WorldRules.submit(state, WorldMode.expedition, q.id, 'wrong', DateTime(2026)).state;
    expect(await show(), before);
    state = WorldRules.submit(state, WorldMode.expedition, q.id, q.answer, DateTime(2026)).state;
    final moved = await show();
    expect(moved, isNot(before));
    state = WorldState.fromJson(state.toJson());
    expect(await show(), moved);
  });
}
