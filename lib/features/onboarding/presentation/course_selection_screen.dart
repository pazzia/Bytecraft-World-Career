import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/di/providers.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';
import '../../../core/theme/game_colors.dart';
import '../../../shared/widgets/app_button.dart';
import '../../../shared/widgets/app_card.dart';
import '../../../shared/widgets/async_value_view.dart';
import '../../courses/domain/course_summary.dart';
import '../../settings/domain/app_settings.dart';
import '../../settings/presentation/settings_controller.dart';

final courseCatalogProvider = FutureProvider<List<CourseSummary>>(
  (ref) => ref.watch(contentRepositoryProvider).loadCatalog(),
);

/// Onboarding step 2: language selection. Completing it flips
/// `onboardingCompleted`, and the router redirect moves to Home.
class CourseSelectionScreen extends ConsumerStatefulWidget {
  const CourseSelectionScreen({super.key, required this.experienceId});

  final String? experienceId;

  @override
  ConsumerState<CourseSelectionScreen> createState() =>
      _CourseSelectionScreenState();
}

class _CourseSelectionScreenState extends ConsumerState<CourseSelectionScreen> {
  String? _selectedId;
  bool _saving = false;

  Future<void> _start(String courseId) async {
    setState(() => _saving = true);
    await ref.read(settingsControllerProvider.notifier).completeOnboarding(
          experience: ExperienceLevel.fromId(widget.experienceId) ??
              ExperienceLevel.beginner,
          courseId: courseId,
        );
    if (mounted) setState(() => _saving = false);
  }

  static const Map<String, String> _shortNames = {
    'python': 'Py',
    'javascript': 'JS',
    'sql': 'SQL',
    'java': 'Jv',
    'csharp': 'C#',
    'cpp': 'C++',
    'go': 'Go',
    'rust': 'Rs',
  };

  @override
  Widget build(BuildContext context) {
    final catalog = ref.watch(courseCatalogProvider);
    final textTheme = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;
    final game = context.gameColors;
    // With a single available course, choose it for the player.
    final available = catalog.value?.where((course) => course.isAvailable).toList();
    final selectedId = _selectedId ??
        (available != null && available.length == 1 ? available.first.id : null);
    return Scaffold(
      appBar: AppBar(),
      body: SafeArea(
        top: false,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: Spacing.page),
              child: Text('Что будем учить?', style: textTheme.headlineLarge),
            ),
            const SizedBox(height: Spacing.xl),
            Expanded(
              child: AsyncValueView<List<CourseSummary>>(
                value: catalog,
                onRetry: () => ref.invalidate(courseCatalogProvider),
                data: (courses) => ListView.separated(
                  padding: const EdgeInsets.symmetric(horizontal: Spacing.page),
                  itemCount: courses.length,
                  separatorBuilder: (context, index) =>
                      const SizedBox(height: Spacing.sm),
                  itemBuilder: (context, index) {
                    final course = courses[index];
                    final selected = course.id == selectedId;
                    final badge = Container(
                      width: 44,
                      height: 44,
                      alignment: Alignment.center,
                      decoration: BoxDecoration(
                        color: course.isAvailable ? game.board : game.locked,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        _shortNames[course.language] ?? course.title.substring(0, 2),
                        style: AppTypography.code(
                          color: course.isAvailable ? game.reward : game.lockedIcon,
                          size: 15,
                          weight: FontWeight.w700,
                        ).copyWith(height: 1.1),
                      ),
                    );
                    if (!course.isAvailable) {
                      return Semantics(
                        label: '${course.title}, скоро',
                        excludeSemantics: true,
                        child: Padding(
                          padding: const EdgeInsets.symmetric(
                            horizontal: Spacing.lg,
                            vertical: Spacing.sm,
                          ),
                          child: Row(
                            children: [
                              badge,
                              const SizedBox(width: Spacing.lg),
                              Expanded(
                                child: Text(
                                  course.title,
                                  style: textTheme.titleMedium
                                      ?.copyWith(color: game.textMuted),
                                ),
                              ),
                              Text(
                                'скоро',
                                style: textTheme.labelMedium
                                    ?.copyWith(color: game.textMuted),
                              ),
                            ],
                          ),
                        ),
                      );
                    }
                    return AppCard(
                      semanticLabel: course.title,
                      borderColor: selected ? scheme.primary : null,
                      color: selected ? game.primaryTint : null,
                      onTap: () => setState(() => _selectedId = course.id),
                      child: Row(
                        children: [
                          badge,
                          const SizedBox(width: Spacing.lg),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(course.title, style: textTheme.titleMedium),
                                if (course.description.isNotEmpty)
                                  Text(
                                    course.description,
                                    style: textTheme.bodySmall
                                        ?.copyWith(color: game.textMuted),
                                  ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(
                Spacing.page,
                Spacing.md,
                Spacing.page,
                Spacing.lg,
              ),
              child: AppButton(
                label: 'Начать',
                isLoading: _saving,
                onPressed: selectedId == null ? null : () => _start(selectedId),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
