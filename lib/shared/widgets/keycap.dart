import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../core/theme/app_spacing.dart';

/// The signature element of the design: a physical key with a solid bottom
/// edge. Pressing it sinks the face onto the edge, so every tap is felt.
///
/// Used for buttons, answer options, code tokens and map nodes.
class Keycap extends StatefulWidget {
  const Keycap({
    super.key,
    required this.child,
    required this.face,
    required this.edge,
    this.onTap,
    this.border,
    this.radius = AppRadius.lg,
    this.depth = AppShadows.keyDepth,
    this.padding = EdgeInsets.zero,
    this.height,
    this.width,
    this.semanticLabel,
    this.selected,
    this.haptic = true,
    this.alignment = Alignment.center,
  });

  final Widget child;
  final Color face;
  final Color edge;
  final Color? border;
  final VoidCallback? onTap;
  final double radius;
  final double depth;
  final EdgeInsetsGeometry padding;
  final double? height;
  final double? width;
  final String? semanticLabel;

  /// For toggle-like keys (answer options), exposed to screen readers.
  final bool? selected;
  final bool haptic;
  final AlignmentGeometry alignment;

  @override
  State<Keycap> createState() => _KeycapState();
}

class _KeycapState extends State<Keycap> {
  bool _pressed = false;

  bool get _enabled => widget.onTap != null;

  void _setPressed(bool value) {
    if (_pressed != value && mounted) setState(() => _pressed = value);
  }

  void _handleTap() {
    if (widget.haptic) HapticFeedback.selectionClick();
    widget.onTap?.call();
  }

  @override
  Widget build(BuildContext context) {
    final reduceMotion = MediaQuery.maybeDisableAnimationsOf(context) ?? false;
    final sunk = _pressed && _enabled ? widget.depth : 0.0;
    final radius = BorderRadius.circular(widget.radius);
    final face = AnimatedContainer(
      duration: reduceMotion ? Duration.zero : AppDurations.press,
      curve: Curves.easeOut,
      height: widget.height == null ? null : widget.height! - widget.depth,
      width: widget.width,
      padding: widget.padding,
      alignment: widget.alignment,
      transform: Matrix4.translationValues(0, sunk, 0),
      decoration: BoxDecoration(
        color: widget.face,
        borderRadius: radius,
        border: widget.border == null
            ? null
            : Border.all(color: widget.border!, width: 2),
        boxShadow: widget.depth == 0
            ? null
            : AppShadows.edge(widget.edge, depth: widget.depth - sunk),
      ),
      child: widget.child,
    );
    return Semantics(
      button: _enabled,
      enabled: _enabled,
      selected: widget.selected,
      label: widget.semanticLabel,
      child: Padding(
        // Reserve room for the edge so pressing never shifts the layout.
        padding: EdgeInsets.only(bottom: widget.depth),
        child: GestureDetector(
          behavior: HitTestBehavior.opaque,
          onTapDown: _enabled ? (_) => _setPressed(true) : null,
          onTapCancel: _enabled ? () => _setPressed(false) : null,
          onTapUp: _enabled ? (_) => _setPressed(false) : null,
          onTap: _enabled ? _handleTap : null,
          child: FocusableActionDetector(
            enabled: _enabled,
            mouseCursor:
                _enabled ? SystemMouseCursors.click : MouseCursor.defer,
            actions: {
              ActivateIntent: CallbackAction<ActivateIntent>(
                onInvoke: (_) {
                  _handleTap();
                  return null;
                },
              ),
            },
            child: face,
          ),
        ),
      ),
    );
  }
}
