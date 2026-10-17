import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../features/career/presentation/career_screen.dart';
import '../../features/home/presentation/home_screen.dart';
import '../../features/journal/presentation/journal_screen.dart';
import '../../features/journal/presentation/topic_screen.dart';
import '../../features/playground/presentation/playground_screen.dart';
import '../../features/playground/presentation/practice_task_screen.dart';
import '../../features/learning_map/presentation/learning_map_screen.dart';
import '../../features/level/presentation/level_screen.dart';
import '../../features/onboarding/presentation/course_selection_screen.dart';
import '../../features/onboarding/presentation/experience_screen.dart';
import '../../features/premium/presentation/premium_screen.dart';
import '../../features/profile/presentation/profile_screen.dart';
import '../../features/settings/domain/app_settings.dart';
import '../../features/settings/presentation/settings_controller.dart';
import '../../features/shop/presentation/shop_screen.dart';
import '../../features/splash/presentation/splash_screen.dart';
import '../shell/main_shell.dart';
import '../startup/app_startup.dart';
import 'routes.dart';

/// Re-evaluates redirects when startup or settings change.
class _RouterRefresh extends ChangeNotifier {
  _RouterRefresh(Ref ref) {
    ref.listen(appStartupProvider, (previous, next) => notifyListeners());
    ref.listen(settingsControllerProvider, (previous, next) => notifyListeners());
  }
}

/// Pure redirect rule, extracted for readability and testing.
String? resolveRedirect({
  required String location,
  required bool isReady,
  required AppSettings? settings,
}) {
  final atSplash = location == Routes.splash;
  if (!isReady || settings == null) return atSplash ? null : Routes.splash;
  final inOnboarding = location.startsWith(Routes.onboarding);
  if (!settings.onboardingCompleted) {
    return inOnboarding ? null : Routes.onboarding;
  }
  if (atSplash || inOnboarding) return Routes.home;
  return null;
}

final _rootKey = GlobalKey<NavigatorState>(debugLabel: 'root');

final routerProvider = Provider<GoRouter>((ref) {
  final refresh = _RouterRefresh(ref);
  final router = GoRouter(
    navigatorKey: _rootKey,
    initialLocation: Routes.splash,
    refreshListenable: refresh,
    redirect: (context, state) {
      final startup = ref.read(appStartupProvider);
      final settings = ref.read(settingsControllerProvider);
      return resolveRedirect(
        location: state.matchedLocation,
        isReady: startup.hasValue && !startup.hasError,
        settings: settings.value,
      );
    },
    routes: [
      GoRoute(
        path: Routes.splash,
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: Routes.onboarding,
        builder: (context, state) => const ExperienceScreen(),
        routes: [
          GoRoute(
            path: 'course',
            builder: (context, state) => CourseSelectionScreen(
              experienceId:
                  state.uri.queryParameters[Routes.experienceQuery],
            ),
          ),
        ],
      ),
      StatefulShellRoute.indexedStack(
        builder: (context, state, shell) => MainShell(shell: shell),
        branches: [
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: Routes.home,
                builder: (context, state) => const HomeScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: Routes.map,
                builder: (context, state) => const LearningMapScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: Routes.journal,
                builder: (context, state) => const JournalScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: Routes.playground,
                builder: (context, state) => const PlaygroundScreen(),
                routes: [
                  GoRoute(
                    path: Routes.practiceTaskSegment,
                    builder: (context, state) => PracticeTaskScreen(
                      taskId: state.pathParameters[Routes.taskIdParam]!,
                    ),
                  ),
                ],
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: Routes.profile,
                builder: (context, state) => const ProfileScreen(),
              ),
            ],
          ),
        ],
      ),
      GoRoute(
        path: Routes.levelPattern,
        parentNavigatorKey: _rootKey,
        builder: (context, state) => LevelScreen(
          args: (
            courseId: state.pathParameters[Routes.courseIdParam]!,
            levelId: state.pathParameters[Routes.levelIdParam]!,
            mode: Routes.modeFrom(state.uri.queryParameters[Routes.modeQuery]),
          ),
        ),
      ),
      GoRoute(
        path: Routes.topicPattern,
        parentNavigatorKey: _rootKey,
        builder: (context, state) => TopicScreen(
          topicId: state.pathParameters[Routes.topicIdParam]!,
        ),
      ),
      GoRoute(
        path: Routes.shop,
        parentNavigatorKey: _rootKey,
        builder: (context, state) => const ShopScreen(),
      ),
      GoRoute(
        path: Routes.premium,
        parentNavigatorKey: _rootKey,
        builder: (context, state) => const PremiumScreen(),
      ),
      GoRoute(
        path: Routes.career,
        parentNavigatorKey: _rootKey,
        builder: (context, state) => const CareerScreen(),
      ),
    ],
  );
  ref.onDispose(() {
    router.dispose();
    refresh.dispose();
  });
  return router;
});
