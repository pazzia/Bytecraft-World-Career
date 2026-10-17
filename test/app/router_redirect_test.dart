import 'package:bytecraft/app/router/app_router.dart';
import 'package:bytecraft/app/router/routes.dart';
import 'package:bytecraft/features/settings/domain/app_settings.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  final fresh = AppSettings.initial('python');

  test('stays on splash until startup is ready', () {
    expect(
      resolveRedirect(location: Routes.home, isReady: false, settings: null),
      Routes.splash,
    );
    expect(
      resolveRedirect(location: Routes.splash, isReady: false, settings: null),
      isNull,
    );
  });

  test('fresh World users launch directly into the game hub', () {
    expect(
      resolveRedirect(location: Routes.splash, isReady: true, settings: fresh),
      Routes.home,
    );
    expect(
      resolveRedirect(
        location: Routes.onboardingCourse,
        isReady: true,
        settings: fresh,
      ),
      Routes.home,
    );
  });

  test('ready users can open game and learning pages', () {
    expect(
      resolveRedirect(
        location: Routes.worldBoss,
        isReady: true,
        settings: fresh,
      ),
      isNull,
    );
    expect(
      resolveRedirect(
        location: Routes.level('python', 'py_var_001'),
        isReady: true,
        settings: fresh,
      ),
      isNull,
    );
  });
}
