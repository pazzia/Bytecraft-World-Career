/// Lightweight tokenizer for syntax highlighting of short Python snippets.
/// Pure Dart (no Flutter) so it is unit-testable; widgets map token kinds
/// to colors.
enum CodeTokenKind { plain, keyword, builtin, string, number, comment }

class CodeToken {
  const CodeToken(this.text, this.kind);

  final String text;
  final CodeTokenKind kind;

  @override
  String toString() => '${kind.name}:"$text"';
}

abstract final class PythonHighlighter {
  static const Set<String> keywords = {
    'False', 'None', 'True', 'and', 'as', 'assert', 'break', 'class',
    'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for',
    'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal',
    'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield',
  };

  static const Set<String> builtins = {
    'print', 'range', 'len', 'int', 'str', 'float', 'bool', 'type', 'input',
    'list', 'dict', 'set', 'tuple', 'abs', 'min', 'max', 'sum', 'round',
  };

  static final RegExp _token = RegExp(
    r'''(#.*$)|("[^"\n]*"?|'[^'\n]*'?)|(\b\d+(?:\.\d+)?\b)|([A-Za-z_][A-Za-z0-9_]*)''',
    multiLine: true,
  );

  static List<CodeToken> tokenize(String line) {
    final tokens = <CodeToken>[];
    var cursor = 0;
    for (final match in _token.allMatches(line)) {
      if (match.start > cursor) {
        tokens.add(CodeToken(line.substring(cursor, match.start), CodeTokenKind.plain));
      }
      final text = match.group(0)!;
      final CodeTokenKind kind;
      if (match.group(1) != null) {
        kind = CodeTokenKind.comment;
      } else if (match.group(2) != null) {
        kind = CodeTokenKind.string;
      } else if (match.group(3) != null) {
        kind = CodeTokenKind.number;
      } else if (keywords.contains(text)) {
        kind = CodeTokenKind.keyword;
      } else if (builtins.contains(text)) {
        kind = CodeTokenKind.builtin;
      } else {
        kind = CodeTokenKind.plain;
      }
      tokens.add(CodeToken(text, kind));
      cursor = match.end;
    }
    if (cursor < line.length) {
      tokens.add(CodeToken(line.substring(cursor), CodeTokenKind.plain));
    }
    return tokens;
  }
}
