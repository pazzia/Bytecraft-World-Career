import 'dart:math' as math;

import 'package:flutter/material.dart';

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
  });

  final String title;
  final String? subtitle;
  final Widget child;
  final List<Widget>? actions;

  @override
  Widget build(BuildContext context) => Scaffold(
        backgroundColor: WorldPalette.bg,
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
                style: const TextStyle(
                  color: WorldPalette.text,
                  fontWeight: FontWeight.w900,
                  fontSize: 19,
                ),
              ),
              if (subtitle != null)
                Text(
                  subtitle!,
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
          value: value.clamp(0, 1),
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
        child: Text(
          code,
          style: const TextStyle(
            color: Color(0xFFCFA7FF),
            fontFamily: 'JetBrainsMono',
            fontSize: 12,
            height: 1.55,
          ),
        ),
      );
}

class CityPainter extends CustomPainter {
  CityPainter({required this.levels});

  final Map<String, int> levels;

  @override
  void paint(Canvas canvas, Size size) {
    final road = Paint()..color = const Color(0xFF182640);
    final grass = Paint()..color = const Color(0xFF142741);
    final grid = Paint()
      ..color = const Color(0xFF244A65).withValues(alpha: .24)
      ..strokeWidth = 1;
    final glow = Paint()
      ..color = WorldPalette.purple.withValues(alpha: .18)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 18);

    canvas.drawRRect(
      RRect.fromRectAndRadius(Offset.zero & size, const Radius.circular(22)),
      grass,
    );
    for (var x = -size.height; x < size.width; x += 36) {
      canvas.drawLine(Offset(x, 0), Offset(x + size.height, size.height), grid);
    }
    canvas.drawRect(
      Rect.fromLTWH(0, size.height * .65, size.width, size.height * .13),
      road,
    );
    canvas.drawRect(
      Rect.fromLTWH(size.width * .43, 0, size.width * .13, size.height),
      road,
    );

    final specs = [
      (const Offset(.12, .16), 'office', WorldPalette.blue, 54.0),
      (const Offset(.58, .17), 'python', WorldPalette.purple, 68.0),
      (const Offset(.12, .53), 'rnd', WorldPalette.cyan, 46.0),
      (const Offset(.61, .55), 'servers', WorldPalette.orange, 50.0),
      (const Offset(.36, .36), 'team', WorldPalette.green, 40.0),
    ];
    for (final spec in specs) {
      final pos = Offset(size.width * spec.$1.dx, size.height * spec.$1.dy);
      final level = levels[spec.$2] ?? 1;
      final h = spec.$4 + (level - 1) * 8;
      final w = h * .72;
      final body = Rect.fromLTWH(pos.dx, pos.dy + 72 - h, w, h);
      canvas.drawRRect(
        RRect.fromRectAndRadius(body.inflate(7), const Radius.circular(12)),
        glow,
      );
      final paint = Paint()
        ..shader = LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [spec.$3, spec.$3.withValues(alpha: .38)],
        ).createShader(body);
      canvas.drawRRect(
        RRect.fromRectAndRadius(body, const Radius.circular(8)),
        paint,
      );
      final window = Paint()..color = const Color(0xFFDFF9FF).withValues(alpha: .9);
      for (var row = 0; row < math.max(2, level); row++) {
        final y = body.top + 10 + row * 12;
        if (y > body.bottom - 8) break;
        canvas.drawRect(
          Rect.fromLTWH(body.left + 8, y, 7, 5),
          window,
        );
        canvas.drawRect(
          Rect.fromLTWH(body.left + 22, y, 7, 5),
          window,
        );
      }
    }
  }

  @override
  bool shouldRepaint(covariant CityPainter oldDelegate) =>
      oldDelegate.levels != levels;
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
