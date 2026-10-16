import 'package:flutter/material.dart';

abstract final class Spacing {
  static const double xxs = 2;
  static const double xs = 4;
  static const double sm = 8;
  static const double md = 12;
  static const double lg = 16;
  static const double xl = 20;
  static const double xxl = 24;
  static const double xxxl = 32;
  static const double huge = 48;

  /// Horizontal page padding on phones.
  static const double page = 20;

  /// Minimum comfortable touch target.
  static const double touchTarget = 48;

  /// Height of primary buttons and answer keys.
  static const double keyHeight = 56;
}

abstract final class AppRadius {
  static const double sm = 10;
  static const double md = 14;
  static const double lg = 16;
  static const double xl = 20;
  static const double board = 22;
  static const double sheet = 28;
  static const double pill = 999;

  static const BorderRadius smAll = BorderRadius.all(Radius.circular(sm));
  static const BorderRadius mdAll = BorderRadius.all(Radius.circular(md));
  static const BorderRadius lgAll = BorderRadius.all(Radius.circular(lg));
  static const BorderRadius xlAll = BorderRadius.all(Radius.circular(xl));
  static const BorderRadius boardAll = BorderRadius.all(Radius.circular(board));
  static const BorderRadius pillAll = BorderRadius.all(Radius.circular(pill));
}

abstract final class AppShadows {
  /// Depth of a keycap's solid bottom edge, px.
  static const double keyDepth = 4;

  static const List<BoxShadow> lifted = [
    BoxShadow(color: Color(0x73000000), blurRadius: 28, offset: Offset(0, 14)),
  ];

  /// Solid "keycap" bottom edge.
  static List<BoxShadow> edge(Color color, {double depth = keyDepth}) => [
        BoxShadow(color: color, offset: Offset(0, depth)),
      ];
}

abstract final class AppDurations {
  static const Duration press = Duration(milliseconds: 90);
  static const Duration fast = Duration(milliseconds: 150);
  static const Duration medium = Duration(milliseconds: 300);
  static const Duration slow = Duration(milliseconds: 600);
}
