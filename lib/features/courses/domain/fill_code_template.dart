/// Parsed representation of a fill-in-the-blank code template.
///
/// Blanks are written as `{{0}}`, `{{1}}`, ... in content JSON.
sealed class TemplateSegment {
  const TemplateSegment();
}

final class TextSegment extends TemplateSegment {
  const TextSegment(this.text);

  final String text;
}

final class BlankSegment extends TemplateSegment {
  const BlankSegment(this.index);

  final int index;
}

abstract final class FillCodeTemplate {
  static final RegExp _blank = RegExp(r'\{\{(\d+)\}\}');

  static List<TemplateSegment> parse(String template) {
    final segments = <TemplateSegment>[];
    var cursor = 0;
    for (final match in _blank.allMatches(template)) {
      if (match.start > cursor) {
        segments.add(TextSegment(template.substring(cursor, match.start)));
      }
      segments.add(BlankSegment(int.parse(match.group(1)!)));
      cursor = match.end;
    }
    if (cursor < template.length) {
      segments.add(TextSegment(template.substring(cursor)));
    }
    return List.unmodifiable(segments);
  }

  /// Distinct blank indexes in the template, sorted.
  static List<int> blankIndexes(String template) {
    final indexes = _blank
        .allMatches(template)
        .map((match) => int.parse(match.group(1)!))
        .toSet()
        .toList()
      ..sort();
    return indexes;
  }

  /// Splits the template into lines, each a list of segments.
  /// Rendering line-by-line keeps indentation and allows horizontal scroll.
  static List<List<TemplateSegment>> lines(String template) =>
      template.split('\n').map(parse).toList(growable: false);
}
