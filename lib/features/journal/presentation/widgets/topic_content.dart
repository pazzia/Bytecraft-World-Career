import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/router/routes.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../core/theme/app_typography.dart';
import '../../../../core/theme/game_colors.dart';
import '../../../../shared/widgets/app_button.dart';
import '../../domain/topic.dart';
import '../journal_providers.dart';
import 'topic_body.dart';

/// The reference card of a topic: summary, explanation with links, worked
/// examples with their real output, «так нельзя / так можно», related topics.
class TopicContent extends ConsumerWidget {
  const TopicContent({
    super.key,
    required this.topic,
    this.showTitle = true,
    this.showRelated = true,
  });

  final Topic topic;
  final bool showTitle;
  final bool showRelated;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    final catalog = ref.watch(topicCatalogProvider).value;
    void onLink(String target, String? term) =>
        showTermSheet(context, target: target, term: term, fromTopicId: topic.id);
    final related = [
      if (showRelated && catalog != null)
        for (final id in topic.linkedTopicIds)
          if (catalog.byId(id) case final linked?) linked,
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (showTitle) ...[
          Text(topic.title, style: textTheme.headlineSmall),
          const SizedBox(height: Spacing.sm),
        ],
        Container(
          padding: const EdgeInsets.fromLTRB(Spacing.md, Spacing.xs, 0, Spacing.xs),
          decoration: BoxDecoration(
            border: Border(left: BorderSide(color: Theme.of(context).colorScheme.primary, width: 3)),
          ),
          child: MarkupText(
            topic.summary,
            style: textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.w600, height: 1.45),
          ),
        ),
        TopicBody(body: topic.body, onLink: onLink),
        if (topic.examples.isNotEmpty) ...[
          _SectionLabel(topic.examples.length == 1 ? 'Пример' : 'Примеры'),
          for (final example in topic.examples) ...[
            if (example.note != null) ...[
              MarkupText(
                example.note!,
                style: textTheme.titleSmall?.copyWith(height: 1.35),
                onLink: onLink,
              ),
              const SizedBox(height: Spacing.sm),
            ],
            ExampleBoard(code: example.code, output: example.output),
            const SizedBox(height: Spacing.xl),
          ],
        ],
        if (topic.pitfalls.isNotEmpty) ...[
          _SectionLabel('Частые ошибки', top: topic.examples.isEmpty ? 28 : Spacing.sm),
          for (final pitfall in topic.pitfalls) PitfallView(pitfall: pitfall, onLink: onLink),
        ],
        if (related.isNotEmpty) ...[
          const _SectionLabel('Связанные темы'),
          Wrap(
            spacing: Spacing.sm,
            runSpacing: Spacing.sm,
            children: [
              for (final linked in related)
                ActionChip(
                  key: ValueKey('related_${linked.id}'),
                  label: Text(linked.title),
                  avatar: Icon(Icons.north_east_rounded, size: 16, color: game.textMuted),
                  onPressed: () => openLinkedTopic(context, linked.id, fromTopicId: topic.id),
                ),
            ],
          ),
        ],
      ],
    );
  }
}

class _SectionLabel extends StatelessWidget {
  const _SectionLabel(this.text, {this.top = 28});

  final String text;
  final double top;

  @override
  Widget build(BuildContext context) => Padding(
        padding: EdgeInsets.only(top: top, bottom: Spacing.md),
        child: Text(text, style: Theme.of(context).textTheme.titleMedium),
      );
}

/// Goes to [topicId] from [fromTopicId]: back if that is where the reader
/// came from, otherwise a new page with a way back.
void openLinkedTopic(BuildContext context, String topicId, {String? fromTopicId}) {
  String? cameFrom;
  try {
    cameFrom = GoRouterState.of(context).uri.queryParameters[Routes.fromQuery];
  } on Object {
    cameFrom = null;
  }
  if (cameFrom == topicId && context.canPop()) {
    context.pop();
    return;
  }
  context.push(Routes.topic(topicId, from: fromTopicId));
}

/// A short explanation of a linked term with a way into its topic.
Future<void> showTermSheet(
  BuildContext context, {
  required String target,
  String? term,
  String? fromTopicId,
}) {
  return showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    showDragHandle: true,
    useSafeArea: true,
    builder: (sheetContext) => _TermSheet(
      target: target,
      term: term,
      onOpenTopic: (topicId) {
        Navigator.of(sheetContext).pop();
        openLinkedTopic(context, topicId, fromTopicId: fromTopicId);
      },
    ),
  );
}

class _TermSheet extends ConsumerWidget {
  const _TermSheet({required this.target, required this.term, required this.onOpenTopic});

  final String target;
  final String? term;
  final ValueChanged<String> onOpenTopic;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final textTheme = Theme.of(context).textTheme;
    final game = context.gameColors;
    final glossary = ref.watch(glossaryProvider).value ?? Glossary.empty;
    final catalog = ref.watch(topicCatalogProvider).value;
    final isGlossaryOnly = target.startsWith('g:');
    final key = term ?? (isGlossaryOnly ? target.substring(2) : null);
    final entry = glossary[key];
    final topicId = isGlossaryOnly ? entry?.topicId : target;
    final topic = topicId == null ? null : catalog?.byId(topicId);
    final example = entry?.example ?? topic?.examples.firstOrNull?.code;
    final output = entry?.example != null ? entry?.output : topic?.examples.firstOrNull?.output;

    return Padding(
      padding: const EdgeInsets.fromLTRB(Spacing.page, 0, Spacing.page, Spacing.xxl),
      child: SingleChildScrollView(
        child: Column(
          key: const ValueKey('term_sheet'),
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (key != null)
              Text(
                entry?.key ?? key,
                style: AppTypography.code(color: Theme.of(context).colorScheme.onSurface, size: 20, weight: FontWeight.w700),
              )
            else if (topic != null)
              Text(topic.title, style: textTheme.titleLarge),
            if (topic != null && key != null) ...[
              const SizedBox(height: Spacing.xxs),
              Text('Тема «${topic.title}»', style: textTheme.bodySmall?.copyWith(color: game.textMuted)),
            ],
            const SizedBox(height: Spacing.md),
            MarkupText(
              entry?.brief ?? topic?.summary ?? 'Объяснение пока не готово.',
              style: textTheme.bodyLarge?.copyWith(height: 1.45),
            ),
            if (example != null) ...[
              const SizedBox(height: Spacing.lg),
              ExampleBoard(code: example, output: output ?? ''),
            ],
            if (topic != null) ...[
              const SizedBox(height: Spacing.xl),
              AppButton(
                key: const ValueKey('term_open_topic'),
                label: 'Открыть тему',
                icon: Icons.menu_book_rounded,
                onPressed: () => onOpenTopic(topic.id),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
