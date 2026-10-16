import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/di/providers.dart';
import '../../../core/theme/app_spacing.dart';
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

  Future<void> _start() async {
    final courseId = _selectedId;
    if (courseId == null) return;
    setState(() => _saving = true);
    await ref.read(settingsControllerProvider.notifier).completeOnboarding(
          experience: ExperienceLevel.fromId(widget.experienceId) ??
              ExperienceLevel.beginner,
          courseId: courseId,
        );
    if (mounted) setState(() => _saving = false);
  }

  @override
  Widget build(BuildContext context) {
    final catalog = ref.watch(courseCatalogProvider);
    final textTheme = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;
    return Scaffold(
      appBar: const AppBar(),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: Spacing.page),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text('Что будем учить?', style: textTheme.headlineMedium),
              const SizedBox(height: Spacing.lg),
              Expanded(
                child: AsyncValueView<List<CourseSummary>>(
                  value: catalog,
                  onRetry: () => ref.invalidate(courseCatalogProvider),
                  data: (courses) => ListView.separated(
                    itemCount: courses.length,
                    separatorBuilder: (context, index) =>
                        const SizedBox(height: Spacing.md),
                    itemBuilder: (context, index) {
                      final course = courses[index];
                      final selected = course.id == _selectedId;
                      return Opacity(
                        opacity: course.isAvailable ? 1 : 0.5,
                        child: AppCard(
                          borderColor: selected ? scheme.primary : null,
                          onTap: course.isAvailable
                              ? () => setState(() => _selectedId = course.id)
                              : null,
                          child: Row(
                            children: [
                              Text(
                                course.icon,
                                style: const TextStyle(fontSize: 30),
                              ),
                              const SizedBox(width: Spacing.lg),
                              Expanded(
                                child: Text(
                                  course.title,
                                  style: textTheme.titleMedium,
                                ),
                              ),
                              if (!course.isAvailable)
                                Text('Скоро', style: textTheme.labelMedium),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ),
              const SizedBox(height: Spacing.md),
              AppButton(
                label: 'Начать',
                isLoading: _saving,
                onPressed: _selectedId == null ? null : _start,
              ),
              const SizedBox(height: Spacing.lg),
            ],
          ),
        ),
      ),
    );
  }
}
