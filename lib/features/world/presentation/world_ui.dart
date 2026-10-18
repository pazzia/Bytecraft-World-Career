import 'dart:math' as math;

import 'package:flutter/material.dart';
import '../../../shared/widgets/code_copy.dart';

abstract final class WorldPalette {
  static const bg = Color(0xFF071021);
  static const bg2 = Color(0xFF0B1630);
  static const panel = Color(0xFF101C36);
  static const panel2 = Color(0xFF152441);
  static const border = Color(0xFF24385D);
  static const text = Color(0xFFF4F7FF);
  static const muted = Color(0xFF9AA8C7);
  static const purple = Color(0xFF8B5CF6);
  static const violet = Color(0xFFA855F7);
  static const blue = Color(0xFF4F7CFF);
  static const cyan = Color(0xFF22D3EE);
  static const green = Color(0xFF22C55E);
  static const orange = Color(0xFFF59E0B);
  static const red = Color(0xFFEF4444);
  static const gold = Color(0xFFFACB45);
}

class WorldPage extends StatelessWidget {
  const WorldPage({
    required this.title,
    required this.child,
    super.key,
    this.subtitle,
    this.actions,
    this.bottomBar,
  });

  final String title;
  final String? subtitle;
  final Widget child;
  final List<Widget>? actions;
  final Widget? bottomBar;

  @override
  Widget build(BuildContext context) => Scaffold(
        backgroundColor: WorldPalette.bg,
        bottomNavigationBar: bottomBar,
        appBar: AppBar(
          backgroundColor: WorldPalette.bg,
          foregroundColor: WorldPalette.text,
          surfaceTintColor: Colors.transparent,
          titleSpacing: 12,
          title: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  color: WorldPalette.text,
                  fontWeight: FontWeight.w900,
                  fontSize: 19,
                ),
              ),
              if (subtitle != null)
                Text(
                  subtitle!,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    color: WorldPalette.muted,
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                  ),
                ),
            ],
          ),
          actions: actions,
        ),
        body: DecoratedBox(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [WorldPalette.bg, Color(0xFF050914)],
            ),
          ),
          child: child,
        ),
      );
}

class WorldPanel extends StatelessWidget {
  const WorldPanel({
    required this.child,
    super.key,
    this.padding = const EdgeInsets.all(16),
    this.onTap,
    this.glow,
  });

  final Widget child;
  final EdgeInsets padding;
  final VoidCallback? onTap;
  final Color? glow;

  @override
  Widget build(BuildContext context) {
    final card = Container(
      padding: padding,
      decoration: BoxDecoration(
        color: WorldPalette.panel.withValues(alpha: .96),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: glow ?? WorldPalette.border),
        boxShadow: [
          if (glow != null)
            BoxShadow(
              color: glow!.withValues(alpha: .16),
              blurRadius: 24,
              spreadRadius: 1,
            ),
        ],
      ),
      child: child,
    );
    if (onTap == null) return card;
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(18),
      child: card,
    );
  }
}

class WorldButton extends StatelessWidget {
  const WorldButton({
    required this.label,
    required this.onPressed,
    super.key,
    this.icon,
    this.secondary = false,
  });

  final String label;
  final VoidCallback? onPressed;
  final IconData? icon;
  final bool secondary;

  @override
  Widget build(BuildContext context) => SizedBox(
        width: double.infinity,
        height: 48,
        child: FilledButton.icon(
          onPressed: onPressed,
          icon: icon == null ? const SizedBox.shrink() : Icon(icon, size: 19),
          label: Text(
            label,
            style: const TextStyle(fontWeight: FontWeight.w800),
          ),
          style: FilledButton.styleFrom(
            backgroundColor:
                secondary ? WorldPalette.panel2 : WorldPalette.purple,
            foregroundColor: WorldPalette.text,
            disabledBackgroundColor: WorldPalette.panel2,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: BorderSide(
                color: secondary ? WorldPalette.border : WorldPalette.violet,
              ),
            ),
          ),
        ),
      );
}

class StatPill extends StatelessWidget {
  const StatPill({
    required this.icon,
    required this.value,
    super.key,
    this.color = WorldPalette.gold,
  });

  final IconData icon;
  final String value;
  final Color color;

  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
        decoration: BoxDecoration(
          color: WorldPalette.panel2,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: WorldPalette.border),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 17, color: color),
            const SizedBox(width: 6),
            Text(
              value,
              style: const TextStyle(
                color: WorldPalette.text,
                fontSize: 13,
                fontWeight: FontWeight.w900,
              ),
            ),
          ],
        ),
      );
}

class WorldProgress extends StatelessWidget {
  const WorldProgress({
    required this.value,
    super.key,
    this.color = WorldPalette.purple,
    this.height = 8,
  });

  final double value;
  final Color color;
  final double height;

  @override
  Widget build(BuildContext context) => ClipRRect(
        borderRadius: BorderRadius.circular(99),
        child: LinearProgressIndicator(
          value: value.clamp(0.0, 1.0).toDouble(),
          minHeight: height,
          color: color,
          backgroundColor: WorldPalette.border.withValues(alpha: .55),
        ),
      );
}

class SectionTitle extends StatelessWidget {
  const SectionTitle(this.title, {super.key, this.trailing});

  final String title;
  final String? trailing;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 10),
        child: Row(
          children: [
            Expanded(
              child: Text(
                title,
                style: const TextStyle(
                  color: WorldPalette.text,
                  fontSize: 18,
                  fontWeight: FontWeight.w900,
                ),
              ),
            ),
            if (trailing != null)
              Text(
                trailing!,
                style: const TextStyle(
                  color: WorldPalette.muted,
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                ),
              ),
          ],
        ),
      );
}

class CodeBlock extends StatelessWidget {
  const CodeBlock(this.code, {super.key});

  final String code;

  @override
  Widget build(BuildContext context) => Container(
        width: double.infinity,
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: const Color(0xFF08111F),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: const Color(0xFF1F3352)),
        ),
        child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
          CodeCopyButton(code: code),
          Text(
          code,
          style: const TextStyle(
            color: Color(0xFFCFA7FF),
            fontFamily: 'JetBrainsMono',
            fontSize: 12,
            height: 1.55,
          ),
        ),
        ]),
      );
}

enum WorldScene { city, expedition, boss, kai }

/// One bundled texture; quadrant clipping happens at render time, offline.
class WorldArtwork extends StatelessWidget {
  const WorldArtwork(this.scene, {super.key});
  final WorldScene scene;

  @override
  Widget build(BuildContext context) => ExcludeSemantics(
        child: ClipRRect(
          borderRadius: BorderRadius.circular(18),
          child: SizedBox.expand(
            child: FittedBox(
              fit: BoxFit.cover,
              child: SizedBox(
                width: 512,
                height: 512,
                child: ClipRect(
                  child: OverflowBox(
                    alignment: switch (scene) {
                      WorldScene.city => Alignment.topLeft,
                      WorldScene.expedition => Alignment.topRight,
                      WorldScene.boss => Alignment.bottomLeft,
                      WorldScene.kai => Alignment.bottomRight,
                    },
                    minWidth: 1024,
                    maxWidth: 1024,
                    minHeight: 1024,
                    maxHeight: 1024,
                    child: Image.asset(
                      'assets/world/world-atlas.png',
                      width: 1024,
                      height: 1024,
                      fit: BoxFit.fill,
                      gaplessPlayback: true,
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      );
}

class WorldCityScene extends StatelessWidget {
  const WorldCityScene({required this.levels, super.key, this.onBuilding});
  final Map<String, int> levels;
  final ValueChanged<String>? onBuilding;

  @override
  Widget build(BuildContext context) => AspectRatio(
        aspectRatio: 1,
        child: LayoutBuilder(builder: (context, constraints) {
          const buildings = [
            ('office', 'Офис', .18, .40),
            ('python', 'Python Lab', .51, .27),
            ('rnd', 'R&D', .82, .47),
            ('team', 'Команда', .28, .68),
            ('servers', 'Серверная', .75, .72),
          ];
          return Stack(children: [
            const Positioned.fill(child: WorldArtwork(WorldScene.city)),
            for (final building in buildings)
              Positioned(
                left: (constraints.maxWidth * building.$3 - 50)
                    .clamp(0.0, constraints.maxWidth - 100).toDouble(),
                top: constraints.maxHeight * building.$4,
                width: 100,
                child: Semantics(
                  button: onBuilding != null,
                  label: '${building.$2}, уровень ${levels[building.$1] ?? 1}',
                  child: Material(
                    color: const Color(0xE6071021),
                    borderRadius: BorderRadius.circular(12),
                    child: InkWell(
                      borderRadius: BorderRadius.circular(12),
                      onTap: onBuilding == null ? null : () => onBuilding!(building.$1),
                      child: Padding(
                        padding: const EdgeInsets.symmetric(vertical: 9, horizontal: 4),
                        child: Text(
                          '${building.$2} · ${levels[building.$1] ?? 1}',
                          textAlign: TextAlign.center,
                          style: const TextStyle(color: WorldPalette.text,
                              fontWeight: FontWeight.w800, fontSize: 11),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
          ]);
        }),
      );
}

class DonutChart extends StatelessWidget {
  const DonutChart({required this.values, super.key});

  final Map<String, int> values;

  @override
  Widget build(BuildContext context) => CustomPaint(
        painter: _DonutPainter(values.values.toList()),
        child: SizedBox(
          width: 150,
          height: 150,
          child: Center(
            child: Text(
              '${values.values.isEmpty ? 0 : values.values.reduce(math.max)}%',
              style: const TextStyle(
                color: WorldPalette.text,
                fontWeight: FontWeight.w900,
                fontSize: 24,
              ),
            ),
          ),
        ),
      );
}

class _DonutPainter extends CustomPainter {
  _DonutPainter(this.values);

  final List<int> values;
  static const colors = [
    WorldPalette.red,
    WorldPalette.blue,
    WorldPalette.green,
    WorldPalette.cyan,
    WorldPalette.purple,
  ];

  @override
  void paint(Canvas canvas, Size size) {
    final total = values.fold<int>(0, (a, b) => a + b);
    final rect = Offset.zero & size;
    var start = -math.pi / 2;
    for (var i = 0; i < values.length; i++) {
      final sweep = total == 0 ? 0.0 : values[i] / total * math.pi * 2;
      final paint = Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = 22
        ..strokeCap = StrokeCap.butt
        ..color = colors[i % colors.length];
      canvas.drawArc(rect.deflate(18), start, sweep, false, paint);
      start += sweep;
    }
  }

  @override
  bool shouldRepaint(covariant _DonutPainter oldDelegate) => true;
}
