import 'package:flutter/material.dart';

/// Crown for boss levels (Material has no crown glyph).
class CrownIcon extends StatelessWidget {
  const CrownIcon({super.key, this.size = 24, this.color});

  final double size;
  final Color? color;

  @override
  Widget build(BuildContext context) => ExcludeSemantics(
        child: CustomPaint(
          size: Size.square(size),
          painter: _CrownPainter(color ?? IconTheme.of(context).color!),
        ),
      );
}

class _CrownPainter extends CustomPainter {
  const _CrownPainter(this.color);

  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final s = size.width / 24;
    final path = Path()
      ..moveTo(3 * s, 8 * s)
      ..lineTo(7.5 * s, 12 * s)
      ..lineTo(12 * s, 5 * s)
      ..lineTo(16.5 * s, 12 * s)
      ..lineTo(21 * s, 8 * s)
      ..lineTo(19 * s, 19 * s)
      ..lineTo(5 * s, 19 * s)
      ..close();
    canvas.drawPath(path, Paint()..color = color);
  }

  @override
  bool shouldRepaint(_CrownPainter oldDelegate) => oldDelegate.color != color;
}
