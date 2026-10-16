import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/routes.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../shared/widgets/app_progress_bar.dart';
import '../../../shared/widgets/async_value_view.dart';
import '../domain/learning_map_model.dart';
import 'learning_map_providers.dart';
import 'widgets/map_node.dart';

class LearningMapScreen extends ConsumerWidget {
  const LearningMapScreen({super.key});

  void _open(BuildContext context, LearningMapModel model, MapNode node) {
    if (!node.isPlayable) {
      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(
          const SnackBar(content: Text('Сначала пройдите предыдущие уровни 🔒')),
        );
      return;
    }
    context.push(Routes.level(model.course.id, node.level.id));
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final map = ref.watch(learningMapProvider);
    return Scaffold(
      body: AsyncValueView<LearningMapModel>(
        value: map,
        onRetry: () => ref.invalidate(learningMapProvider),
        data: (model) => CustomScrollView(
          slivers: [
            SliverAppBar(
              pinned: true,
              title: Text(model.course.title),
              bottom: PreferredSize(
                preferredSize: const Size.fromHeight(Spacing.xl),
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(
                    Spacing.page,
                    0,
                    Spacing.page,
                    Spacing.md,
                  ),
                  child: AppProgressBar(value: model.progress, height: 10),
                ),
              ),
            ),
            for (final section in model.sections) ...[
              SliverToBoxAdapter(child: _ModuleHeader(section: section)),
              SliverPadding(
                padding: const EdgeInsets.symmetric(horizontal: Spacing.lg),
                sliver: SliverList.builder(
                  itemCount: section.nodes.length,
                  itemBuilder: (context, index) {
                    final node = section.nodes[index];
                    return MapNodeTile(
                      key: ValueKey(node.level.id),
                      node: node,
                      isFirst: index == 0,
                      isLast: index == section.nodes.length - 1,
                      onTap: () => _open(context, model, node),
                    );
                  },
                ),
              ),
            ],
            const SliverToBoxAdapter(child: SizedBox(height: Spacing.xxxl)),
          ],
        ),
      ),
    );
  }
}

class _ModuleHeader extends StatelessWidget {
  const _ModuleHeader({required this.section});

  final MapSection section;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;
    final module = section.module;
    return Padding(
      padding: const EdgeInsets.fromLTRB(
        Spacing.page,
        Spacing.xl,
        Spacing.page,
        Spacing.sm,
      ),
      child: Container(
        padding: const EdgeInsets.all(Spacing.lg),
        decoration: BoxDecoration(
          color: scheme.primary,
          borderRadius: AppRadius.lgAll,
        ),
        child: Row(
          children: [
            Text(module.icon, style: const TextStyle(fontSize: 32)),
            const SizedBox(width: Spacing.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    module.title,
                    style: textTheme.titleLarge
                        ?.copyWith(color: scheme.onPrimary),
                  ),
                  if (module.description.isNotEmpty)
                    Text(
                      module.description,
                      style: TextStyle(
                        color: scheme.onPrimary.withValues(alpha: 0.85),
                      ),
                    ),
                ],
              ),
            ),
            Text(
              '${section.completed}/${section.total}',
              style:
                  textTheme.titleMedium?.copyWith(color: scheme.onPrimary),
            ),
          ],
        ),
      ),
    );
  }
}
