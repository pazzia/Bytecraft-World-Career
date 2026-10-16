/// Route paths in one place — screens never hardcode URLs.
abstract final class Routes {
  static const String splash = '/splash';
  static const String onboarding = '/onboarding';
  static const String onboardingCourse = '/onboarding/course';
  static const String home = '/home';
  static const String map = '/map';
  static const String profile = '/profile';
  static const String shop = '/shop';
  static const String premium = '/premium';

  static const String levelPattern = '/level/:courseId/:levelId';
  static const String courseIdParam = 'courseId';
  static const String levelIdParam = 'levelId';
  static const String dailyQuery = 'daily';
  static const String experienceQuery = 'experience';

  static String level(String courseId, String levelId, {bool daily = false}) =>
      Uri(
        path: '/level/$courseId/$levelId',
        queryParameters: daily ? {dailyQuery: '1'} : null,
      ).toString();

  static String onboardingCourseFor(String experienceId) => Uri(
        path: onboardingCourse,
        queryParameters: {experienceQuery: experienceId},
      ).toString();
}
