import 'package:bytecraft/features/journal/presentation/widgets/topic_body.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('blocks: headings, lists, tables, syntax, paragraphs', () {
    const body = 'Первый абзац\nпродолжение.\n\n## Как это работает\n'
        '- один\n- два\n  перенос\n\n1. шаг\n2. шаг\n\n'
        '| a | b |\n|---|---|\n| 1 | 2 |\n\n```syntax\nfor имя in набор:\n    тело\n```';
    final blocks = TopicMarkup.parse(body);
    expect(blocks, hasLength(6));
    expect((blocks[0] as ParagraphBlock).text, 'Первый абзац продолжение.');
    expect((blocks[1] as HeadingBlock).text, 'Как это работает');
    final bullets = blocks[2] as ListBlock;
    expect(bullets.numbered, isFalse);
    expect(bullets.items, ['один', 'два перенос']);
    expect((blocks[3] as ListBlock).numbered, isTrue);
    final table = blocks[4] as TableBlock;
    expect(table.header, ['a', 'b']);
    expect(table.rows, [
      ['1', '2'],
    ]);
    expect((blocks[5] as SyntaxBlock).code, 'for имя in набор:\n    тело');
  });

  test('plain old text is paragraphs', () {
    final blocks = TopicMarkup.parse('Один.\n\nДва.');
    expect(blocks.map((b) => (b as ParagraphBlock).text), ['Один.', 'Два.']);
  });

  test('inline: code, bold, links with terms', () {
    final parts = InlineMarkup.parse(
      'См. [[py_dicts|`dict.get`|.get]] и **важно** `x = 1` [[g:len|длина]].',
    );
    final link = parts.whereType<LinkPart>().first;
    expect(link.target, 'py_dicts');
    expect(link.label, '`dict.get`');
    expect(link.term, '.get');
    expect(parts.whereType<CodePart>().single.code, 'x = 1');
    expect(parts.whereType<TextPart>().any((p) => p.bold && p.text == 'важно'), isTrue);
    final glossary = parts.whereType<LinkPart>().last;
    expect(glossary.target, 'g:len');
    expect(glossary.term, isNull);
  });
}
