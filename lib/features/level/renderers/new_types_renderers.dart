import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';
import '../../../core/theme/game_colors.dart';
import '../../../shared/widgets/code_block.dart';
import '../../../shared/widgets/keycap.dart';
import '../../courses/domain/level_payload.dart';
import '../domain/answer.dart';
import 'question_renderer.dart';

AssignmentAnswer _assignment(QuestionContext question, int slots) => switch (question.answer) {
      final AssignmentAnswer answer => answer,
      _ => AssignmentAnswer.empty(slots),
    };

// ---------------------------------------------------------------- trace table

/// "Отследи переменные": the code stays pinned with the current step's
/// line highlighted; the player fills the table from a bank of values.
/// The cell to fill is always the first empty one, so there is no extra
/// selection state: tap a filled cell to empty it and refill it.
class TraceTableRenderer extends QuestionRenderer {
  const TraceTableRenderer();

  @override
  bool get showsLevelCode => false;

  @override
  Widget? buildStage(BuildContext context, QuestionContext question) {
    final payload = question.level.payload as TraceTablePayload;
    final answer = _assignment(question, payload.blanks.length);
    final slot = answer.firstEmpty;
    final row = slot == null ? null : payload.rows[payload.blanks[slot].row];
    return CodeBlock(
      code: question.level.code ?? '',
      selectedLines: row == null ? const <int>{} : {row.line - 1},
      expandable: true,
    );
  }

  @override
  Widget build(BuildContext context, QuestionContext question) =>
      TraceTableView(question: question);
}

class TraceTableView extends StatelessWidget {
  const TraceTableView({super.key, required this.question});

  final QuestionContext question;

  @override
  Widget build(BuildContext context) {
    final payload = question.level.payload as TraceTablePayload;
    final answer = _assignment(question, payload.blanks.length);
    final game = context.gameColors;
    final scheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    final active = answer.firstEmpty;
    final wrong = question.outcome?.wrongParts ?? const <int>{};
    final solved = question.outcome?.isCorrect ?? false;
    final headerStyle = AppTypography.code(color: game.textMuted, size: 14, weight: FontWeight.w700);

    Widget cell(int row, int column) {
      final slot = payload.slotOf(row, column);
      final given = slot == null;
      final value = given ? payload.rows[row].values[column] : answer.values[slot];
      final isActive = slot != null && slot == active && !question.isLocked;
      final isWrong = slot != null && wrong.contains(slot);
      final Color border = isWrong
          ? game.error
          : solved && !given
              ? game.success
              : isActive
                  ? scheme.primary
                  : given
                      ? Colors.transparent
                      : game.track;
      final content = Container(
        key: ValueKey('trace_cell_${row}_$column'),
        constraints: const BoxConstraints(minHeight: 44),
        alignment: Alignment.center,
        margin: const EdgeInsets.all(3),
        padding: const EdgeInsets.symmetric(horizontal: Spacing.xs),
        decoration: BoxDecoration(
          color: given ? Colors.transparent : (value == null ? game.track.withValues(alpha: 0.35) : scheme.primary.withValues(alpha: 0.12)),
          borderRadius: AppRadius.mdAll,
          border: Border.all(color: border, width: isActive || isWrong ? 2.5 : 1.5),
        ),
        child: Text(
          value ?? (isActive ? '?' : ''),
          textAlign: TextAlign.center,
          style: AppTypography.code(
            color: given ? game.textMuted : scheme.onSurface,
            size: 15,
            weight: given ? FontWeight.w500 : FontWeight.w700,
          ).copyWith(height: 1.2),
        ),
      );
      if (slot == null || value == null || question.isLocked) return content;
      return Semantics(
        button: true,
        label: 'Значение $value, нажмите, чтобы убрать',
        child: InkWell(
          borderRadius: AppRadius.mdAll,
          onTap: () => question.onChanged(answer.clear(slot)),
          child: content,
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          'Значения переменных после выполнения строки',
          style: textTheme.bodySmall?.copyWith(color: game.textMuted),
        ),
        const SizedBox(height: Spacing.sm),
        Table(
          columnWidths: const {0: IntrinsicColumnWidth()},
          defaultVerticalAlignment: TableCellVerticalAlignment.middle,
          children: [
            TableRow(
              children: [
                Padding(
                  padding: const EdgeInsets.only(right: Spacing.sm),
                  child: Text('стр.', style: headerStyle),
                ),
                for (final column in payload.columns)
                  Center(child: Text(column, style: headerStyle)),
              ],
            ),
            for (var r = 0; r < payload.rows.length; r++)
              TableRow(
                children: [
                  Padding(
                    padding: const EdgeInsets.only(right: Spacing.sm),
                    child: Text(
                      '${payload.rows[r].line}',
                      style: AppTypography.code(color: game.textMuted, size: 14),
                    ),
                  ),
                  for (var c = 0; c < payload.columns.length; c++) cell(r, c),
                ],
              ),
          ],
        ),
        const SizedBox(height: Spacing.xl),
        Wrap(
          spacing: Spacing.sm,
          runSpacing: Spacing.sm,
          children: [
            for (final value in payload.bank)
              Keycap(
                key: ValueKey('trace_value_$value'),
                face: game.keyFace,
                edge: game.keyEdge,
                border: game.keyBorder,
                radius: AppRadius.md,
                depth: 4,
                padding: const EdgeInsets.symmetric(horizontal: Spacing.lg, vertical: Spacing.md),
                semanticLabel: 'Значение $value',
                onTap: question.isLocked || active == null
                    ? null
                    : () => question.onChanged(answer.assign(active, value)),
                child: Text(
                  value,
                  style: AppTypography.code(color: scheme.onSurface, size: 17, weight: FontWeight.w700)
                      .copyWith(height: 1.1),
                ),
              ),
          ],
        ),
      ],
    );
  }
}

// ----------------------------------------------------------------- categorize

/// "Разложи по группам": one card at a time, a big key for each group.
/// Sorted cards gather under their group; tap one to take it back.
class CategorizeRenderer extends QuestionRenderer {
  const CategorizeRenderer();

  @override
  Widget build(BuildContext context, QuestionContext question) =>
      CategorizeView(question: question);
}

class CategorizeView extends StatelessWidget {
  const CategorizeView({super.key, required this.question});

  final QuestionContext question;

  @override
  Widget build(BuildContext context) {
    final payload = question.level.payload as CategorizePayload;
    final answer = _assignment(question, payload.items.length);
    final game = context.gameColors;
    final scheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    final current = answer.firstEmpty;
    final wrong = question.outcome?.wrongParts ?? const <int>{};
    final solved = question.outcome?.isCorrect ?? false;
    final placed = answer.values.length;

    TextStyle itemStyle(CategorizeItem item, {required double size, Color? color}) => item.isCode
        ? AppTypography.code(color: color, size: size, weight: FontWeight.w700).copyWith(height: 1.3)
        : (textTheme.titleMedium ?? const TextStyle()).copyWith(fontSize: size, color: color);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // The card to sort.
        AnimatedSwitcher(
          duration: const Duration(milliseconds: 180),
          child: Container(
            key: ValueKey('categorize_card_${current ?? 'done'}'),
            constraints: const BoxConstraints(minHeight: 96),
            alignment: Alignment.center,
            padding: const EdgeInsets.all(Spacing.lg),
            decoration: BoxDecoration(
              color: current == null ? game.track.withValues(alpha: 0.4) : game.board,
              borderRadius: AppRadius.lgAll,
            ),
            child: current == null
                ? Text(
                    solved ? 'Всё разложено верно' : 'Всё разложено — нажмите «Проверить»',
                    textAlign: TextAlign.center,
                    style: textTheme.titleMedium?.copyWith(color: game.textMuted),
                  )
                : Column(
                    children: [
                      Text(
                        '${placed + 1} из ${payload.items.length}',
                        style: textTheme.labelMedium?.copyWith(color: game.codeLineNumber),
                      ),
                      const SizedBox(height: Spacing.sm),
                      Text(
                        payload.items[current].text,
                        key: const ValueKey('categorize_current'),
                        textAlign: TextAlign.center,
                        style: itemStyle(payload.items[current], size: 19, color: game.codeText),
                      ),
                    ],
                  ),
          ),
        ),
        const SizedBox(height: Spacing.lg),
        // One key per group.
        for (var g = 0; g < payload.categories.length; g++)
          Padding(
            padding: const EdgeInsets.only(bottom: Spacing.md),
            child: Keycap(
              key: ValueKey('categorize_group_$g'),
              face: game.keyFace,
              edge: game.keyEdge,
              border: game.keyBorder,
              height: 60,
              semanticLabel: 'В группу «${payload.categories[g]}»',
              onTap: question.isLocked || current == null
                  ? null
                  : () => question.onChanged(answer.assign(current, '$g')),
              child: Text(
                payload.categories[g],
                style: textTheme.titleMedium?.copyWith(color: scheme.onSurface),
              ),
            ),
          ),
        if (placed > 0) ...[
          const SizedBox(height: Spacing.md),
          for (var g = 0; g < payload.categories.length; g++)
            if (answer.values.values.contains('$g')) ...[
              Text(payload.categories[g], style: textTheme.titleSmall?.copyWith(color: game.textMuted)),
              const SizedBox(height: Spacing.xs),
              Wrap(
                spacing: Spacing.sm,
                runSpacing: Spacing.sm,
                children: [
                  for (final entry in answer.values.entries)
                    if (entry.value == '$g')
                      _PlacedChip(
                        key: ValueKey('categorize_placed_${entry.key}'),
                        text: payload.items[entry.key].text,
                        style: itemStyle(payload.items[entry.key], size: 15),
                        color: wrong.contains(entry.key)
                            ? game.error
                            : solved
                                ? game.success
                                : game.track,
                        onTap: question.isLocked ? null : () => question.onChanged(answer.clear(entry.key)),
                      ),
                ],
              ),
              const SizedBox(height: Spacing.md),
            ],
        ],
      ],
    );
  }
}

class _PlacedChip extends StatelessWidget {
  const _PlacedChip({super.key, required this.text, required this.style, required this.color, this.onTap});

  final String text;
  final TextStyle style;
  final Color color;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) => Semantics(
        button: onTap != null,
        label: onTap == null ? text : '$text, нажмите, чтобы вернуть',
        excludeSemantics: true,
        child: InkWell(
          borderRadius: AppRadius.mdAll,
          onTap: onTap,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: Spacing.md, vertical: Spacing.sm),
            decoration: BoxDecoration(
              borderRadius: AppRadius.mdAll,
              border: Border.all(color: color, width: 2),
            ),
            child: Text(text, style: style),
          ),
        ),
      );
}

// ------------------------------------------------------------------- fix line

/// "Исправь строку": the broken line is marked in the pinned code; the
/// player edits it in a code field (it starts with the broken line).
class FixLineRenderer extends QuestionRenderer {
  const FixLineRenderer();

  @override
  bool get showsLevelCode => false;

  @override
  Widget? buildStage(BuildContext context, QuestionContext question) {
    final payload = question.level.payload as FixLinePayload;
    final outcome = question.outcome;
    return CodeBlock(
      code: question.level.code ?? '',
      errorLines: outcome?.isCorrect ?? false ? const <int>{} : {payload.line},
      successLines: outcome?.isCorrect ?? false ? {payload.line} : const <int>{},
      expandable: true,
    );
  }

  @override
  Widget build(BuildContext context, QuestionContext question) => FixLineView(
        key: ValueKey('fix_line_${question.level.id}'),
        question: question,
      );
}

class FixLineView extends StatefulWidget {
  const FixLineView({super.key, required this.question});

  final QuestionContext question;

  @override
  State<FixLineView> createState() => _FixLineViewState();
}

class _FixLineViewState extends State<FixLineView> {
  late final TextEditingController _controller;

  String get _answerText => switch (widget.question.answer) {
        TextAnswer(:final text) => text,
        _ => '',
      };

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: _answerText);
  }

  @override
  void didUpdateWidget(FixLineView oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (_controller.text != _answerText) {
      _controller.value = TextEditingValue(
        text: _answerText,
        selection: TextSelection.collapsed(offset: _answerText.length),
      );
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _insert(String text) {
    final value = _controller.value;
    final start = value.selection.isValid ? value.selection.start : value.text.length;
    final end = value.selection.isValid ? value.selection.end : value.text.length;
    final next = value.text.replaceRange(start, end, text);
    _controller.value = TextEditingValue(
      text: next,
      selection: TextSelection.collapsed(offset: start + text.length),
    );
    widget.question.onChanged(TextAnswer(next));
  }

  @override
  Widget build(BuildContext context) {
    final payload = widget.question.level.payload as FixLinePayload;
    final game = context.gameColors;
    final textTheme = Theme.of(context).textTheme;
    final outcome = widget.question.outcome;
    final border = outcome == null
        ? game.boardMuted
        : outcome.isCorrect
            ? game.success
            : game.error;
    const symbols = [':', '(', ')', '[', ']', '"', '=', '+', '-', '<', '>', '.', ','];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          'Исправленная строка ${payload.line + 1}',
          style: textTheme.labelLarge?.copyWith(color: game.textMuted),
        ),
        const SizedBox(height: Spacing.sm),
        Container(
          decoration: BoxDecoration(
            color: game.board,
            borderRadius: AppRadius.lgAll,
            border: Border.all(color: border, width: 2),
          ),
          padding: const EdgeInsets.symmetric(horizontal: Spacing.lg, vertical: Spacing.xs),
          child: TextField(
            key: const ValueKey('fix_line_field'),
            controller: _controller,
            readOnly: widget.question.isLocked,
            onChanged: (text) => widget.question.onChanged(TextAnswer(text)),
            maxLines: 3,
            minLines: 1,
            keyboardType: TextInputType.visiblePassword,
            textCapitalization: TextCapitalization.none,
            autocorrect: false,
            enableSuggestions: false,
            smartQuotesType: SmartQuotesType.disabled,
            smartDashesType: SmartDashesType.disabled,
            enableIMEPersonalizedLearning: false,
            cursorColor: game.codeText,
            style: AppTypography.code(color: game.codeText, size: 16),
            decoration: const InputDecoration(
              border: InputBorder.none,
              enabledBorder: InputBorder.none,
              focusedBorder: InputBorder.none,
              filled: false,
              isDense: true,
              contentPadding: EdgeInsets.symmetric(vertical: 12),
            ),
          ),
        ),
        const SizedBox(height: Spacing.sm),
        // Symbols that are awkward to reach on a phone keyboard.
        SizedBox(
          height: 44,
          child: ListView(
            scrollDirection: Axis.horizontal,
            children: [
              for (final symbol in symbols)
                Padding(
                  padding: const EdgeInsets.only(right: Spacing.xs),
                  child: OutlinedButton(
                    style: OutlinedButton.styleFrom(
                      minimumSize: const Size(44, 44),
                      padding: EdgeInsets.zero,
                    ),
                    onPressed: widget.question.isLocked ? null : () => _insert(symbol),
                    child: Text(symbol, style: AppTypography.code(size: 17, weight: FontWeight.w700)),
                  ),
                ),
            ],
          ),
        ),
        const SizedBox(height: Spacing.sm),
        Text(
          'Отступ можно не набирать. Пробелы и вид кавычек не важны.',
          style: textTheme.bodySmall?.copyWith(color: game.textMuted),
        ),
      ],
    );
  }
}
