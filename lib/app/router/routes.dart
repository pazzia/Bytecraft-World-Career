import '../../features/level/domain/level_session.dart';

/// Route paths in one place — screens never hardcode URLs.
abstract final class Routes {
  static const String splash = '/splash';
  static const String onboarding = '/onboarding';
  static const String onboardingCourse = '/onboarding/course';
  static const String home = '/home';
  static const String map = '/map';
  static const String career = '/career';
  static const String profile = '/profile';
  static const String practice = '/practice';
  static const String journal = '/practice/dna';
  static const String playground = '/practice/code';
  static const String topicPattern = '/topic/:topicId';
  static const String topicIdParam = 'topicId';

  // Bytecraft World — the game layer built around learning.
  static const String worldCity = '/world/city';
  static const String worldExpedition = '/world/expedition';
  static const String worldBoss = '/world/boss';
  static const String worldGhost = '/world/ghost';
  static const String worldGuild = '/world/guild';
  static const String worldRival = '/world/rival';
  static const String worldMistakes = '/world/mistakes';
  static const String worldBuild = '/world/build';
  static const String worldSeason = '/world/season';
  static const String worldInfinite = '/world/infinite';

  static const String practiceTaskSegment = 'task/:taskId';
  static const String taskIdParam = 'taskId';

  static String practiceTask(String taskId) =>
      '$playground/task/${Uri.encodeComponent(taskId)}';

  static String topic(String topicId) => '/topic/${Uri.encodeComponent(topicId)}';
  static const String shop = '/shop';
  static const String premium = '/premium';

  static const String levelPattern = '/level/:courseId/:levelId';
  static const String courseIdParam = 'courseId';
  static const String levelIdParam = 'levelId';
  static const String modeQuery = 'mode';
  static const String experienceQuery = 'experience';

  static String level(
    String courseId,
    String levelId, {
    LevelMode mode = LevelMode.standard,
  }) =>
      Uri(
        path: '/level/$courseId/$levelId',
        queryParameters:
            mode == LevelMode.standard ? null : {modeQuery: mode.name},
      ).toString();

  static LevelMode modeFrom(String? value) => LevelMode.values.firstWhere(
        (mode) => mode.name == value,
        orElse: () => LevelMode.standard,
      );

  static String onboardingCourseFor(String experienceId) => Uri(
        path: onboardingCourse,
        queryParameters: {experienceQuery: experienceId},
      ).toString();
}
