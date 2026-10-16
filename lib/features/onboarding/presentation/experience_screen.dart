import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/routes.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../shared/widgets/app_button.dart';
import '../../../shared/widgets/app_card.dart';
import '../../settings/domain/app_settings.dart';

/// Onboarding step 1: self-assessed experience.
class ExperienceScreen extends StatefulWidget {
  const ExperienceScreen({super.key});

  @override
  State<ExperienceScreen> createState() => _ExperienceScreenState();
}

class _ExperienceScreenState extends State<ExperienceScreen> {
  ExperienceLevel? _selected;

  static const Map<ExperienceLevel, (String, String, String)> _options = {
    ExperienceLevel.beginner: (
      '🌱',
      'Я никогда не программировал',
      'Начнём с самых основ',
    ),
    ExperienceLevel.someExperience: (
      '🛠️',
      'Я немного знаю программирование',
      'Освежим базу и пойдём дальше',
    ),
    ExperienceLevel.developer: (
      '🚀',
      'Я уже программист',
      'Все модули открыты — выбирайте сами',
    ),
  };

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(Spacing.page),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: Spacing.xl),
              Text('Привет! 👋', style: textTheme.headlineMedium),
              const SizedBox(height: Spacing.sm),
              Text(
                'Какой у вас опыт в программировании?',
                style: textTheme.bodyLarge,
              ),
              const SizedBox(height: Spacing.xl),
              Expanded(
                child: ListView(
                  children: [
                    for (final entry in _options.entries)
                      Padding(
                        padding: const EdgeInsets.only(bottom: Spacing.md),
                        child: AppCard(
                          onTap: () => setState(() => _selected = entry.key),
                          borderColor:
                              _selected == entry.key ? scheme.primary : null,
                          child: Row(
                            children: [
                              Text(
                                entry.value.$1,
                                style: const TextStyle(fontSize: 32),
                              ),
                              const SizedBox(width: Spacing.lg),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      entry.value.$2,
                                      style: textTheme.titleMedium,
                                    ),
                                    const SizedBox(height: Spacing.xs),
                                    Text(entry.value.$3),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                  ],
                ),
              ),
              AppButton(
                label: 'Дальше',
                onPressed: _selected == null
                    ? null
                    : () => context.push(
                          Routes.onboardingCourseFor(_selected!.id),
                        ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
