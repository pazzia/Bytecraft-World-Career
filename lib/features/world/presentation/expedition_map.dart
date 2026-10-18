import 'package:flutter/material.dart';

import '../domain/world_challenge.dart';
import '../domain/world_state.dart';
import 'world_ui.dart';

/// Coordinates match the five stone platforms in the complete square artwork.
/// Only validated expeditionStep moves the explorer; taps never change progress.
class ExpeditionMap extends StatefulWidget {
  const ExpeditionMap({super.key, required this.completed});
  final int completed;

  static const platforms = [
    Offset(.67, .80),
    Offset(.42, .67),
    Offset(.71, .54),
    Offset(.60, .40),
    Offset(.72, .26),
    Offset(.87, .16), // chest, reached only after the fifth correct answer
  ];

  @override
  State<ExpeditionMap> createState() => _ExpeditionMapState();
}

class _ExpeditionMapState extends State<ExpeditionMap>
    with AutomaticKeepAliveClientMixin {
  @override
  bool get wantKeepAlive => true;

  @override
  Widget build(BuildContext context) {
    super.build(context);
    final step = widget.completed.clamp(0, 5);
    final current = step == 5 ? null : WorldChallenges.at(
      WorldState.initial().copyWith(expeditionStep: step), WorldMode.expedition);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(children: [
          const Expanded(child: Text('Маршрут экспедиции', style: TextStyle(
            color: WorldPalette.text, fontWeight: FontWeight.w800, fontSize: 17))),
          Text('$step / 5', key: const ValueKey('expedition-progress'),
            style: const TextStyle(color: WorldPalette.cyan, fontWeight: FontWeight.w900)),
        ]),
        const SizedBox(height: 10),
        ClipRRect(
          borderRadius: BorderRadius.circular(18),
          child: AspectRatio(
            aspectRatio: 1,
            child: LayoutBuilder(builder: (context, constraints) {
              final side = constraints.maxWidth;
              final point = ExpeditionMap.platforms[step];
              final height = (side * .26).clamp(72.0, 112.0);
              final width = height * 2 / 3;
              return Stack(children: [
                const Positioned.fill(child: WorldArtwork(WorldScene.expedition)),
                Positioned.fill(child: IgnorePointer(child: CustomPaint(
                  painter: _RoutePainter(completed: step)))),
                // A small caption sits in the open landscape, not over a task.
                Positioned(left: 10, top: 10, child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
                  decoration: BoxDecoration(color: const Color(0xE6071021),
                    borderRadius: BorderRadius.circular(12)),
                  child: Text(step == 5 ? 'API восстановлен ✓' : 'Ты на этапе ${step + 1}',
                    style: const TextStyle(color: WorldPalette.text, fontSize: 12,
                      fontWeight: FontWeight.w800)),
                )),
                for (var i = 0; i < 5; i++)
                  Positioned(
                    left: ExpeditionMap.platforms[i].dx * side - 17,
                    top: ExpeditionMap.platforms[i].dy * side + 7,
                    width: 34, height: 30,
                    child: Semantics(
                      label: 'Этап ${i + 1}: ${i < step ? "пройден" : i == step ? "текущий" : "закрыт"}',
                      child: Tooltip(
                        message: i < step ? 'Этап ${i + 1} пройден' : i == step
                            ? 'Текущее задание' : 'Откроется после предыдущего этапа',
                        child: DecoratedBox(
                          key: ValueKey('expedition-node-$i'),
                          decoration: BoxDecoration(
                            color: i < step ? WorldPalette.green : i == step
                              ? WorldPalette.purple : const Color(0xED152441),
                            borderRadius: BorderRadius.circular(10),
                            border: Border.all(color: i == step ? WorldPalette.cyan
                              : i < step ? Colors.white : WorldPalette.muted, width: 2),
                          ),
                          child: Center(child: i < step
                            ? const Icon(Icons.check_rounded, size: 21, color: Colors.white)
                            : Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                                if (i > step) const Icon(Icons.lock_rounded, size: 10,
                                  color: WorldPalette.muted),
                                Text('${i + 1}', style: const TextStyle(color: Colors.white,
                                  fontWeight: FontWeight.w900, fontSize: 13)),
                              ])),
                        ),
                      ),
                    ),
                  ),
                AnimatedPositioned(
                  key: const ValueKey('expedition-explorer-position'),
                  duration: const Duration(milliseconds: 850),
                  curve: Curves.easeInOutCubic,
                  left: (point.dx * side - width / 2).clamp(0.0, side - width),
                  top: (point.dy * side - height + 10).clamp(3.0, side - height),
                  width: width, height: height,
                  child: IgnorePointer(child: Image.asset(
                    'assets/world/programmer-explorer.png',
                    key: const ValueKey('expedition-explorer'),
                    fit: BoxFit.contain,
                    semanticLabel: step == 5 ? 'Программист достиг сундука' : 'Программист на этапе ${step + 1}',
                  )),
                ),
              ]);
            }),
          ),
        ),
        const SizedBox(height: 12),
        Semantics(liveRegion: true, child: Text(
          step == 5 ? '5 из 5 · маршрут завершён. Забери сундук ниже.'
            : 'Сейчас ${step + 1}/5 · ${current!.title}',
          key: const ValueKey('expedition-current-stage'),
          style: const TextStyle(color: WorldPalette.text, fontWeight: FontWeight.w800),
        )),
        const SizedBox(height: 8),
        ClipRRect(borderRadius: BorderRadius.circular(6), child: LinearProgressIndicator(
          value: step / 5, minHeight: 7, color: WorldPalette.green,
          backgroundColor: WorldPalette.border,
          semanticsLabel: 'Пройдено этапов', semanticsValue: '$step из 5',
        )),
        const SizedBox(height: 10),
        const Wrap(spacing: 14, runSpacing: 5, children: [
          _Legend(color: WorldPalette.green, text: 'Пройдено', icon: Icons.check_rounded),
          _Legend(color: WorldPalette.purple, text: 'Сейчас', icon: Icons.person_rounded),
          _Legend(color: WorldPalette.muted, text: 'Закрыто', icon: Icons.lock_rounded),
        ]),
        const SizedBox(height: 10),
        const Text('Верный ответ перемещает героя дальше. Ошибка оставляет его на месте.',
          style: TextStyle(color: WorldPalette.muted, fontSize: 12)),
        const SizedBox(height: 16),
      ],
    );
  }
}

class _Legend extends StatelessWidget {
  const _Legend({required this.color, required this.text, required this.icon});
  final Color color;
  final String text;
  final IconData icon;
  @override
  Widget build(BuildContext context) => Row(mainAxisSize: MainAxisSize.min, children: [
    Icon(icon, color: color, size: 14),
    const SizedBox(width: 4),
    Text(text, style: const TextStyle(color: WorldPalette.text, fontSize: 11)),
  ]);
}

class _RoutePainter extends CustomPainter {
  const _RoutePainter({required this.completed});
  final int completed;
  @override
  void paint(Canvas canvas, Size size) {
    final points = ExpeditionMap.platforms.map((p) => Offset(p.dx * size.width, p.dy * size.height)).toList();
    for (var i = 0; i < points.length - 1; i++) {
      final paint = Paint()..strokeWidth = 4..strokeCap = StrokeCap.round
        ..color = i < completed ? WorldPalette.green : const Color(0xAAFFFFFF);
      if (i < completed) {
        canvas.drawLine(points[i], points[i + 1], paint);
      } else {
        final distance = (points[i + 1] - points[i]).distance;
        for (double d = 0; d < distance; d += 10) {
          canvas.drawCircle(Offset.lerp(points[i], points[i + 1], d / distance)!, 2, paint);
        }
      }
    }
  }
  @override
  bool shouldRepaint(_RoutePainter oldDelegate) => completed != oldDelegate.completed;
}
