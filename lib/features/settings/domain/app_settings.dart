/// Self-assessed experience chosen during onboarding.
enum ExperienceLevel {
  beginner('beginner'),
  someExperience('some'),
  developer('developer');

  const ExperienceLevel(this.id);

  final String id;

  static ExperienceLevel? fromId(String? id) {
    for (final level in ExperienceLevel.values) {
      if (level.id == id) return level;
    }
    return null;
  }
}

enum ThemePreference {
  system('system'),
  light('light'),
  dark('dark');

  const ThemePreference(this.id);

  final String id;

  static ThemePreference fromId(String? id) => ThemePreference.values
      .firstWhere((value) => value.id == id, orElse: () => system);
}

class AppSettings {
  const AppSettings({
    required this.onboardingCompleted,
    required this.activeCourseId,
    required this.theme,
    this.experience,
    this.careerGoalId = 'python_backend',
  });

  factory AppSettings.initial(String defaultCourseId) => AppSettings(
        onboardingCompleted: false,
        activeCourseId: defaultCourseId,
        theme: ThemePreference.system,
      );

  factory AppSettings.fromJson(
    Map<String, dynamic> json, {
    required String defaultCourseId,
  }) {
    final courseId = json['activeCourseId'];
    final careerGoal = json['careerGoalId'];
    return AppSettings(
      onboardingCompleted: json['onboardingCompleted'] == true,
      activeCourseId: courseId is String ? courseId : defaultCourseId,
      theme: ThemePreference.fromId(json['theme'] as String?),
      experience: ExperienceLevel.fromId(json['experience'] as String?),
      careerGoalId: careerGoal is String ? careerGoal : 'python_backend',
    );
  }

  final bool onboardingCompleted;
  final String activeCourseId;
  final ThemePreference theme;
  final ExperienceLevel? experience;
  final String careerGoalId;

  AppSettings copyWith({
    bool? onboardingCompleted,
    String? activeCourseId,
    ThemePreference? theme,
    ExperienceLevel? experience,
    String? careerGoalId,
  }) =>
      AppSettings(
        onboardingCompleted: onboardingCompleted ?? this.onboardingCompleted,
        activeCourseId: activeCourseId ?? this.activeCourseId,
        theme: theme ?? this.theme,
        experience: experience ?? this.experience,
        careerGoalId: careerGoalId ?? this.careerGoalId,
      );

  Map<String, dynamic> toJson() => {
        'onboardingCompleted': onboardingCompleted,
        'activeCourseId': activeCourseId,
        'theme': theme.id,
        if (experience != null) 'experience': experience!.id,
        'careerGoalId': careerGoalId,
      };
}
